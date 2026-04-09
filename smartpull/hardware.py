"""
smartpull - Hardware Detection Module
Layer 1: Queries nvidia-smi and returns a clean hardware profile dict.
"""

import subprocess
import json
import platform


def get_gpu_info() -> dict:
    """
    Queries nvidia-smi for real-time GPU and VRAM stats.
    Returns a clean dict with GPU name, total VRAM, free VRAM, and driver version.
    """
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.free,memory.used,driver_version",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode != 0:
            return _fallback_profile(error="nvidia-smi returned non-zero exit code")

        # Parse CSV output
        line = result.stdout.strip().split("\n")[0]  # Take first GPU
        parts = [p.strip() for p in line.split(",")]

        gpu_name = parts[0]
        total_vram_mb = int(parts[1])
        free_vram_mb = int(parts[2])
        used_vram_mb = int(parts[3])
        driver_version = parts[4]

        # Apply 15% safety buffer to free VRAM
        buffer_mb = int(free_vram_mb * 0.15)
        usable_vram_mb = free_vram_mb - buffer_mb

        return {
            "status": "ok",
            "gpu": gpu_name,
            "driver": driver_version,
            "os": platform.system(),
            "total_vram_mb": total_vram_mb,
            "used_vram_mb": used_vram_mb,
            "free_vram_mb": free_vram_mb,
            "buffer_mb": buffer_mb,
            "usable_vram_mb": usable_vram_mb,
        }

    except FileNotFoundError:
        return _fallback_profile(error="nvidia-smi not found. Is an NVIDIA GPU present?")
    except subprocess.TimeoutExpired:
        return _fallback_profile(error="nvidia-smi timed out")
    except Exception as e:
        return _fallback_profile(error=str(e))


def _fallback_profile(error: str) -> dict:
    """Returns a safe fallback profile when GPU detection fails."""
    return {
        "status": "error",
        "error": error,
        "gpu": "Unknown",
        "driver": "Unknown",
        "os": platform.system(),
        "total_vram_mb": 0,
        "used_vram_mb": 0,
        "free_vram_mb": 0,
        "buffer_mb": 0,
        "usable_vram_mb": 0,
    }


def print_hardware_profile(profile: dict):
    """Pretty prints the hardware profile to terminal."""
    print("\n" + "=" * 45)
    print("  smartpull — Hardware Profile")
    print("=" * 45)

    if profile["status"] == "error":
        print(f"  ❌ Error: {profile['error']}")
        print("=" * 45)
        return

    total_gb = profile["total_vram_mb"] / 1024
    free_gb = profile["free_vram_mb"] / 1024
    usable_gb = profile["usable_vram_mb"] / 1024
    used_gb = profile["used_vram_mb"] / 1024

    print(f"  GPU     : {profile['gpu']}")
    print(f"  Driver  : {profile['driver']}")
    print(f"  OS      : {profile['os']}")
    print(f"  VRAM    : {total_gb:.1f} GB total")
    print(f"  Used    : {used_gb:.1f} GB (OS + apps)")
    print(f"  Free    : {free_gb:.1f} GB")
    print(f"  Buffer  : {profile['buffer_mb']} MB (15% safety)")
    print(f"  Usable  : {usable_gb:.1f} GB ✅")
    print("=" * 45 + "\n")


# Quick test — run this file directly to verify on your machine
if __name__ == "__main__":
    profile = get_gpu_info()
    print_hardware_profile(profile)
    print("Raw dict:")
    print(json.dumps(profile, indent=2))
