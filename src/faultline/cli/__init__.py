"""Command-line interface for faultline."""

import typer
from rich.console import Console

app = typer.Typer(
    name="faultline",
    help="tracellm-faultline — evaluate LLM agent reliability under corrupted tool outputs.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def inspect() -> None:
    """List available tasks, providers, and strategies."""
    console.print("[bold]faultline inspect[/bold] — not yet implemented")


@app.command()
def run(
    config: str = typer.Argument(..., help="Path to experiment config YAML"),
    resume: bool = typer.Option(False, "--resume", help="Resume an interrupted experiment"),
) -> None:
    """Run an experiment from a configuration file."""
    console.print(f"[bold]faultline run[/bold] {config} (resume={resume}) — not yet implemented")


@app.command()
def analyze(experiment_id: str = typer.Argument(..., help="Experiment ID to analyze")) -> None:
    """Analyze results for a completed experiment."""
    console.print(f"[bold]faultline analyze[/bold] {experiment_id} — not yet implemented")


@app.command()
def export(
    experiment_id: str = typer.Argument(..., help="Experiment ID to export"),
    format: str = typer.Option("jsonl", "--format", help="Export format: jsonl, csv, json"),
) -> None:
    """Export traces for an experiment."""
    console.print(
        f"[bold]faultline export[/bold] {experiment_id} (format={format}) — not yet implemented"
    )


@app.command()
def replay(run_id: str = typer.Argument(..., help="Run ID to replay")) -> None:
    """Replay a stored trajectory using recorded outputs."""
    console.print(f"[bold]faultline replay[/bold] {run_id} — not yet implemented")


@app.command()
def rerun(run_id: str = typer.Argument(..., help="Run ID to rerun")) -> None:
    """Perform a fresh rerun with live model calls."""
    console.print(f"[bold]faultline rerun[/bold] {run_id} — not yet implemented")
