"""
smartpull - Model Matrix Module
Layer 2: Lookup table mapping usable VRAM to the best model, quantization, and context window.
"""

# ============================================================
# MODEL MATRIX
# Each entry defines:
#   - model       : Ollama model tag
#   - quant       : Quantization type (GGUF format)
#   - vram_mb     : Approximate VRAM needed at this quant
#   - ctx         : Safe context window for this VRAM budget
#   - elo         : Approximate coding ELO score (reference)
#   - notes       : Why this model at this quant
# ============================================================

MODEL_MATRIX = [
    {
        "min_vram_mb": 0,
        "max_vram_mb": 1800,
        "model": "gemma2:2b",
        "quant": "IQ4_XS",
        "vram_mb": 1400,
        "ctx": 2048,
        "elo": 1180,
        "notes": "Bare minimum. Good for quick completions only.",
    },
    {
        "min_vram_mb": 1800,
        "max_vram_mb": 2800,
        "model": "gemma4:e2b",
        "quant": "IQ4_XS",
        "vram_mb": 1600,
        "ctx": 4096,
        "elo": 1240,
        "notes": "Best sub-3GB option. MoE architecture, active params ~1.6GB.",
    },
    {
        "min_vram_mb": 2800,
        "max_vram_mb": 4500,
        "model": "qwen2.5-coder:3b",
        "quant": "Q4_K_S",
        "vram_mb": 2600,
        "ctx": 8192,
        "elo": 1290,
        "notes": "Strong coding model. Best quality in the 3-4.5GB window.",
    },
    {
        "min_vram_mb": 4500,
        "max_vram_mb": 6000,
        "model": "qwen2.5-coder:7b",
        "quant": "Q4_K_S",
        "vram_mb": 4700,
        "ctx": 16384,
        "elo": 1340,
        "notes": "Top choice for 6GB cards. High context, excellent code quality.",
    },
    {
        "min_vram_mb": 6000,
        "max_vram_mb": 9000,
        "model": "llama3.1:8b",
        "quant": "Q5_K_M",
        "vram_mb": 6000,
        "ctx": 32768,
        "elo": 1360,
        "notes": "Balanced general + coding. Good for 8GB cards.",
    },
    {
        "min_vram_mb": 9000,
        "max_vram_mb": 999999,
        "model": "qwen2.5-coder:14b",
        "quant": "Q5_K_M",
        "vram_mb": 9000,
        "ctx": 32768,
        "elo": 1420,
        "notes": "High-end option. Near GPT-4o level coding for local models.",
    },
]


def get_recommendation(usable_vram_mb: int) -> dict:
    """
    Takes usable VRAM (after buffer) in MB.
    Returns the best model recommendation from the matrix.
    """
    for entry in MODEL_MATRIX:
        if entry["min_vram_mb"] <= usable_vram_mb < entry["max_vram_mb"]:
            return {
                "status": "ok",
                "usable_vram_mb": usable_vram_mb,
                "model": entry["model"],
                "quant": entry["quant"],
                "vram_needed_mb": entry["vram_mb"],
                "ctx": entry["ctx"],
                "elo": entry["elo"],
                "headroom_mb": usable_vram_mb - entry["vram_mb"],
                "notes": entry["notes"],
            }

    # Fallback — should never hit this
    return {
        "status": "error",
        "error": f"No model found for {usable_vram_mb} MB usable VRAM",
        "usable_vram_mb": usable_vram_mb,
    }


def print_recommendation(rec: dict):
    """Pretty prints the recommendation to terminal."""
    print("\n" + "=" * 45)
    print("  smartpull — Model Recommendation")
    print("=" * 45)

    if rec["status"] == "error":
        print(f"  ❌ Error: {rec['error']}")
        print("=" * 45)
        return

    usable_gb = rec["usable_vram_mb"] / 1024
    needed_gb = rec["vram_needed_mb"] / 1024
    headroom_mb = rec["headroom_mb"]

    print(f"  Usable VRAM  : {usable_gb:.2f} GB")
    print(f"  Model        : {rec['model']}")
    print(f"  Quantization : {rec['quant']}")
    print(f"  VRAM needed  : {needed_gb:.2f} GB")
    print(f"  Context      : {rec['ctx']:,} tokens")
    print(f"  ELO (approx) : {rec['elo']}")
    print(f"  Headroom     : {headroom_mb} MB ✅")
    print(f"  Note         : {rec['notes']}")
    print("=" * 45 + "\n")


def print_full_matrix():
    """Prints the entire model matrix as a reference table."""
    print("\n" + "=" * 75)
    print("  smartpull — Full Model Matrix")
    print("=" * 75)
    print(f"  {'VRAM Range':<18} {'Model':<25} {'Quant':<10} {'CTX':<8} {'ELO'}")
    print("-" * 75)
    for entry in MODEL_MATRIX:
        vram_range = f"{entry['min_vram_mb']/1024:.1f}-{entry['max_vram_mb']/1024:.0f}GB"
        if entry["max_vram_mb"] == 999999:
            vram_range = f"{entry['min_vram_mb']/1024:.1f}GB+"
        print(
            f"  {vram_range:<18} {entry['model']:<25} {entry['quant']:<10} "
            f"{entry['ctx']:<8} {entry['elo']}"
        )
    print("=" * 75 + "\n")


# Quick test
if __name__ == "__main__":
    print_full_matrix()

    # Simulate your 3050 Ti (2380 MB usable after buffer)
    test_vram = 2380
    print(f"Testing with {test_vram} MB usable VRAM (RTX 3050 Ti simulation):\n")
    rec = get_recommendation(test_vram)
    print_recommendation(rec)
