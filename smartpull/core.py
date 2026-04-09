"""
smartpull - Smart Pull Logic Module
Layer 3: Wires hardware detection + model matrix together.
The brain of the tool — takes raw GPU data, applies all calculations,
and returns a final actionable recommendation object.
"""

from smartpull.hardware import get_gpu_info
from smartpull.matrix import get_recommendation

# ============================================================
# MoE (Mixture of Experts) Active Parameter Lookup
# Some models only activate a fraction of their weights
# during inference — we use active VRAM, not total weights.
# ============================================================

MOE_MODELS = {
    "gemma4:e2b": {"total_params_b": 4.0, "active_params_b": 1.6},
    "gemma4:27b": {"total_params_b": 27.0, "active_params_b": 3.8},
    "mixtral:8x7b": {"total_params_b": 46.7, "active_params_b": 12.9},
    "qwen2.5:72b": {"total_params_b": 72.0, "active_params_b": 20.0},
}


def is_moe_model(model_name: str) -> bool:
    """Check if a model uses Mixture of Experts architecture."""
    return model_name in MOE_MODELS


def get_moe_info(model_name: str) -> dict | None:
    """Returns MoE active parameter info if applicable."""
    return MOE_MODELS.get(model_name, None)


def calculate_ctx_from_headroom(headroom_mb: int, base_ctx: int) -> int:
    """
    Dynamically scales context window based on leftover VRAM headroom.
    More headroom = larger context window possible.

    KV Cache memory approx:
      - Each 1024 tokens of context needs ~100MB VRAM (rule of thumb)
      - We stay conservative and use 80% of headroom for ctx expansion
    """
    if headroom_mb <= 0:
        return base_ctx

    # How many extra 1024-token blocks can we fit in 80% of headroom?
    usable_headroom = int(headroom_mb * 0.80)
    extra_ctx_blocks = usable_headroom // 100  # ~100MB per 1024 tokens
    extra_ctx = extra_ctx_blocks * 1024

    expanded_ctx = base_ctx + extra_ctx

    # Cap at 32768 — beyond this, quality degrades for most local models
    return min(expanded_ctx, 32768)


def run_smart_pull() -> dict:
    """
    Main orchestration function.
    1. Gets hardware profile
    2. Gets model recommendation
    3. Applies MoE awareness
    4. Dynamically scales context window
    5. Returns a complete recommendation object
    """

    # Step 1 — Hardware Detection
    hw = get_gpu_info()

    if hw["status"] == "error":
        return {
            "status": "error",
            "stage": "hardware_detection",
            "error": hw["error"],
        }

    # Step 2 — Model Matrix Lookup
    rec = get_recommendation(hw["usable_vram_mb"])

    if rec["status"] == "error":
        return {
            "status": "error",
            "stage": "model_matrix",
            "error": rec["error"],
        }

    # Step 3 — MoE Awareness Check
    moe_info = get_moe_info(rec["model"])
    moe_note = None

    if moe_info:
        moe_note = (
            f"MoE model detected — only {moe_info['active_params_b']}B of "
            f"{moe_info['total_params_b']}B params active during inference."
        )

    # Step 4 — Dynamic Context Window Scaling
    optimized_ctx = calculate_ctx_from_headroom(
        headroom_mb=rec["headroom_mb"],
        base_ctx=rec["ctx"],
    )

    # Step 5 — Build Final Recommendation Object
    final = {
        "status": "ok",
        # Hardware summary
        "gpu": hw["gpu"],
        "driver": hw["driver"],
        "os": hw["os"],
        "total_vram_mb": hw["total_vram_mb"],
        "free_vram_mb": hw["free_vram_mb"],
        "usable_vram_mb": hw["usable_vram_mb"],
        "buffer_mb": hw["buffer_mb"],
        # Model recommendation
        "model": rec["model"],
        "quant": rec["quant"],
        "vram_needed_mb": rec["vram_needed_mb"],
        "headroom_mb": rec["headroom_mb"],
        "elo": rec["elo"],
        "notes": rec["notes"],
        # Optimized settings
        "ctx": optimized_ctx,
        "base_ctx": rec["ctx"],
        "ctx_expanded": optimized_ctx > rec["ctx"],
        # MoE info
        "is_moe": moe_info is not None,
        "moe_note": moe_note,
        # Swap safety
        "swap_risk": (
            "LOW" if rec["headroom_mb"] > 500 else "MEDIUM" if rec["headroom_mb"] > 200 else "HIGH"
        ),
    }

    return final


def print_smart_pull_result(result: dict):
    """Pretty prints the full smart pull result."""
    print("\n" + "=" * 50)
    print("  smartpull — Final Recommendation")
    print("=" * 50)

    if result["status"] == "error":
        print(f"  ❌ Failed at stage : {result['stage']}")
        print(f"  Error             : {result['error']}")
        print("=" * 50)
        return

    usable_gb = result["usable_vram_mb"] / 1024
    needed_gb = result["vram_needed_mb"] / 1024
    total_gb = result["total_vram_mb"] / 1024

    print(f"  GPU              : {result['gpu']}")
    print(f"  Total VRAM       : {total_gb:.1f} GB")
    print(f"  Usable VRAM      : {usable_gb:.2f} GB (after 15% buffer)")
    print()
    print(f"  ✅ Model          : {result['model']}")
    print(f"  ✅ Quantization   : {result['quant']}")
    print(f"  ✅ VRAM needed    : {needed_gb:.2f} GB")
    print(f"  ✅ Context window : {result['ctx']:,} tokens", end="")

    if result["ctx_expanded"]:
        print(f"  (expanded from {result['base_ctx']:,})")
    else:
        print()

    print(f"  ✅ Headroom       : {result['headroom_mb']} MB")
    print(f"  ✅ Swap risk      : {result['swap_risk']}")
    print(f"  ✅ ELO (approx)   : {result['elo']}")

    if result["is_moe"]:
        print(f"\n  ⚡ MoE Note       : {result['moe_note']}")

    print(f"\n  Note: {result['notes']}")
    print("=" * 50 + "\n")


# Quick test
if __name__ == "__main__":
    result = run_smart_pull()
    print_smart_pull_result(result)
