"""
smartpull - Modelfile Generator
Layer 4: Takes the smart pull recommendation and generates an Ollama Modelfile using Jinja2.
"""

from jinja2 import Template
from pathlib import Path

MODELFILE_TEMPLATE = """FROM {{ model }}
PARAMETER num_ctx {{ ctx }}
PARAMETER num_gpu 99
PARAMETER num_thread 8
PARAMETER f16_kv true
PARAMETER use_mmap true
SYSTEM "You are a coding assistant optimized for {{ gpu }}. Context window: {{ ctx }} tokens. Quantization: {{ quant }}."
"""

def generate_modelfile(result: dict, output_path: str = "./Modelfile") -> str:
    """
    Takes a smart pull result dict and writes a Modelfile to disk.
    Returns the path of the generated file.
    """
    template = Template(MODELFILE_TEMPLATE)
    rendered = template.render(
        model=result["model"],
        ctx=result["ctx"],
        gpu=result["gpu"],
        quant=result["quant"],
    )

    path = Path(output_path)
    path.write_text(rendered)

    return str(path.resolve())


def print_ollama_commands(result: dict, modelfile_path: str):
    """Prints the exact commands the user needs to run."""
    tag = result["model"].replace(":", "-")

    print("\n" + "=" * 50)
    print("  smartpull — Run These Commands")
    print("=" * 50)
    print(f"\n  # 1. Pull the model")
    print(f"  ollama pull {result['model']}\n")
    print(f"  # 2. Create optimized build")
    print(f"  ollama create smartpull-{tag} -f {modelfile_path}\n")
    print(f"  # 3. Run it")
    print(f"  ollama run smartpull-{tag}\n")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    # Simulate a result for testing without needing GPU
    mock_result = {
        "gpu":   "NVIDIA GeForce RTX 3050 Ti Laptop GPU",
        "model": "gemma4:e2b",
        "quant": "IQ4_XS",
        "ctx":   4608,
    }

    path = generate_modelfile(mock_result)
    print(f"✅ Modelfile written to: {path}")
    print("\nContents:")
    print(open(path).read())
    print_ollama_commands(mock_result, path)