"""
smartpull - Unit Tests
Layer 6: pytest tests for core logic. Mocks nvidia-smi so tests run without a GPU.
"""

import pytest
from unittest.mock import patch, MagicMock
from smartpull.hardware import get_gpu_info
from smartpull.matrix import get_recommendation
from smartpull.core import calculate_ctx_from_headroom, is_moe_model, run_smart_pull
from smartpull.modelfile_gen import generate_modelfile
import tempfile
import os


# ============================================================
# Layer 1 — Hardware Detection Tests
# ============================================================

MOCK_NVIDIA_SMI_OUTPUT = "NVIDIA GeForce RTX 3050 Ti Laptop GPU, 4096, 2800, 1296, 551.23"

@patch("smartpull.hardware.subprocess.run")
def test_get_gpu_info_success(mock_run):
    """nvidia-smi returns valid output → profile parsed correctly."""
    mock_run.return_value = MagicMock(returncode=0, stdout=MOCK_NVIDIA_SMI_OUTPUT)
    profile = get_gpu_info()

    assert profile["status"] == "ok"
    assert profile["gpu"] == "NVIDIA GeForce RTX 3050 Ti Laptop GPU"
    assert profile["total_vram_mb"] == 4096
    assert profile["free_vram_mb"] == 2800
    assert profile["used_vram_mb"] == 1296
    assert profile["driver"] == "551.23"


@patch("smartpull.hardware.subprocess.run")
def test_get_gpu_info_applies_buffer(mock_run):
    """Usable VRAM should be free VRAM minus 15% buffer."""
    mock_run.return_value = MagicMock(returncode=0, stdout=MOCK_NVIDIA_SMI_OUTPUT)
    profile = get_gpu_info()

    expected_buffer = int(2800 * 0.15)
    expected_usable = 2800 - expected_buffer

    assert profile["buffer_mb"] == expected_buffer
    assert profile["usable_vram_mb"] == expected_usable


@patch("smartpull.hardware.subprocess.run")
def test_get_gpu_info_nvidia_smi_not_found(mock_run):
    """Missing nvidia-smi → fallback profile with error status."""
    mock_run.side_effect = FileNotFoundError
    profile = get_gpu_info()

    assert profile["status"] == "error"
    assert "nvidia-smi" in profile["error"]
    assert profile["usable_vram_mb"] == 0


@patch("smartpull.hardware.subprocess.run")
def test_get_gpu_info_nonzero_exit(mock_run):
    """nvidia-smi non-zero exit → fallback profile."""
    mock_run.return_value = MagicMock(returncode=1, stdout="")
    profile = get_gpu_info()

    assert profile["status"] == "error"


# ============================================================
# Layer 2 — Model Matrix Tests
# ============================================================

def test_recommendation_under_1800mb():
    """Under 1800MB → gemma2:2b recommended."""
    rec = get_recommendation(1500)
    assert rec["status"] == "ok"
    assert rec["model"] == "gemma2:2b"


def test_recommendation_3050ti_range():
    """2380MB (3050 Ti typical) → gemma4:e2b recommended."""
    rec = get_recommendation(2380)
    assert rec["status"] == "ok"
    assert rec["model"] == "gemma4:e2b"
    assert rec["quant"] == "IQ4_XS"


def test_recommendation_4500mb():
    """4500MB → qwen2.5-coder:7b recommended."""
    rec = get_recommendation(4500)
    assert rec["status"] == "ok"
    assert rec["model"] == "qwen2.5-coder:7b"


def test_recommendation_has_headroom():
    """Headroom should be usable_vram minus vram_needed."""
    rec = get_recommendation(2380)
    expected_headroom = 2380 - rec["vram_needed_mb"]
    assert rec["headroom_mb"] == expected_headroom


def test_recommendation_returns_positive_headroom():
    """Recommended model should always fit within usable VRAM."""
    for vram in [1500, 2380, 3500, 5000, 7000, 10000]:
        rec = get_recommendation(vram)
        assert rec["headroom_mb"] >= 0, f"Negative headroom at {vram}MB"


# ============================================================
# Layer 3 — Smart Pull Logic Tests
# ============================================================

def test_ctx_expansion_with_headroom():
    """Large headroom should expand context window."""
    expanded = calculate_ctx_from_headroom(headroom_mb=1000, base_ctx=4096)
    assert expanded > 4096


def test_ctx_no_expansion_zero_headroom():
    """Zero headroom → context stays at base."""
    result = calculate_ctx_from_headroom(headroom_mb=0, base_ctx=4096)
    assert result == 4096


def test_ctx_capped_at_32768():
    """Context window should never exceed 32768."""
    result = calculate_ctx_from_headroom(headroom_mb=999999, base_ctx=4096)
    assert result <= 32768


def test_is_moe_model_true():
    """gemma4:e2b is a MoE model."""
    assert is_moe_model("gemma4:e2b") is True


def test_is_moe_model_false():
    """llama3.1:8b is not a MoE model."""
    assert is_moe_model("llama3.1:8b") is False


@patch("smartpull.core.get_gpu_info")
def test_run_smart_pull_hardware_error(mock_hw):
    """Hardware error → smart pull returns error status."""
    mock_hw.return_value = {"status": "error", "error": "no gpu", "usable_vram_mb": 0}
    result = run_smart_pull()
    assert result["status"] == "error"
    assert result["stage"] == "hardware_detection"


@patch("smartpull.core.get_gpu_info")
def test_run_smart_pull_success(mock_hw):
    """Valid hardware → smart pull returns ok status with all fields."""
    mock_hw.return_value = {
        "status": "ok",
        "gpu": "RTX 3050 Ti",
        "driver": "551.23",
        "os": "Windows",
        "total_vram_mb": 4096,
        "free_vram_mb": 2800,
        "used_vram_mb": 1296,
        "buffer_mb": 420,
        "usable_vram_mb": 2380,
    }
    result = run_smart_pull()

    assert result["status"] == "ok"
    assert "model" in result
    assert "ctx" in result
    assert "swap_risk" in result
    assert result["swap_risk"] in ["LOW", "MEDIUM", "HIGH"]


# ============================================================
# Layer 4 — Modelfile Generator Tests
# ============================================================

def test_generate_modelfile_creates_file():
    """Modelfile should be written to disk."""
    mock_result = {
        "gpu": "RTX 3050 Ti",
        "model": "gemma4:e2b",
        "quant": "IQ4_XS",
        "ctx": 4608,
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix="Modelfile") as tmp:
        path = tmp.name

    try:
        generate_modelfile(mock_result, output_path=path)
        assert os.path.exists(path)
        content = open(path).read()
        assert "gemma4:e2b" in content
        assert "4608" in content
        assert "num_gpu 99" in content
    finally:
        os.unlink(path)


def test_generate_modelfile_contains_system_prompt():
    """Modelfile SYSTEM prompt should mention the GPU."""
    mock_result = {
        "gpu": "RTX 3050 Ti",
        "model": "gemma4:e2b",
        "quant": "IQ4_XS",
        "ctx": 4608,
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix="Modelfile") as tmp:
        path = tmp.name

    try:
        generate_modelfile(mock_result, output_path=path)
        content = open(path).read()
        assert "RTX 3050 Ti" in content
    finally:
        os.unlink(path)