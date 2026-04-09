"""
smartpull - CLI Interface
Layer 5: Click-based CLI that wires all layers into clean terminal commands.

Commands:
  smartpull scan        → Show hardware profile
  smartpull recommend   → Show best model recommendation
  smartpull build       → Generate Modelfile + print ollama commands
  smartpull matrix      → Print full model matrix table
"""

import click
from smartpull.hardware import get_gpu_info, print_hardware_profile
from smartpull.matrix import get_recommendation, print_recommendation, print_full_matrix
from smartpull.core import run_smart_pull, print_smart_pull_result
from smartpull.modelfile_gen import generate_modelfile, print_ollama_commands


@click.group()
@click.version_option(version="0.1.0", prog_name="smartpull")
def cli():
    """
    smartpull — Hardware-aware LLM orchestration for local models.

    Automatically profiles your GPU and recommends the best
    Ollama model + quantization for zero-swap inference.
    """
    pass


@cli.command()
def scan():
    """Scan your GPU and show real-time VRAM profile."""
    click.echo("\n🔍 Scanning hardware...")
    profile = get_gpu_info()
    print_hardware_profile(profile)

    if profile["status"] == "error":
        raise SystemExit(1)


@cli.command()
def recommend():
    """Recommend the best model for your current VRAM."""
    click.echo("\n🧠 Analysing your hardware...")
    result = run_smart_pull()
    print_smart_pull_result(result)

    if result["status"] == "error":
        raise SystemExit(1)


@cli.command()
@click.option(
    "--output", "-o",
    default="./Modelfile",
    help="Path to write the generated Modelfile (default: ./Modelfile)",
)
def build(output):
    """Generate an optimized Modelfile and print ollama commands."""
    click.echo("\n⚙️  Running SmartPull analysis...")
    result = run_smart_pull()

    if result["status"] == "error":
        click.echo(f"❌ Error: {result['error']}")
        raise SystemExit(1)

    print_smart_pull_result(result)

    click.echo("📝 Generating Modelfile...")
    path = generate_modelfile(result, output_path=output)
    click.echo(f"✅ Modelfile written to: {path}")

    print_ollama_commands(result, path)


@cli.command()
def matrix():
    """Show the full model matrix reference table."""
    print_full_matrix()


# Entry point
if __name__ == "__main__":
    cli()