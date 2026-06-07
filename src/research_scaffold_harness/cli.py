"""Command-line entry point for the Research Scaffold Harness."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import get_args

import click

from research_scaffold_harness.models.common import WorkflowCondition

_CONDITIONS = get_args(WorkflowCondition)


@click.group()
@click.version_option(package_name="research-scaffold-harness")
def cli() -> None:
    """Research Scaffold Harness CLI."""


@cli.command("write-fixture-run")
@click.option(
    "--task",
    "task_dir",
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Path to fixture source packet directory containing task.yaml.",
)
@click.option(
    "--condition",
    required=True,
    type=click.Choice(_CONDITIONS),
    help="Workflow condition for claim generation.",
)
@click.option(
    "--out",
    "out_dir",
    required=True,
    type=click.Path(file_okay=False, path_type=Path),
    help="Parent directory for the scaffold-run output.",
)
def write_fixture_run(task_dir: Path, condition: str, out_dir: Path) -> None:
    """Generate a synthetic scaffold-run artifact from a fixture source packet."""
    from research_scaffold_harness.contracts.writer import write_scaffold_run
    from research_scaffold_harness.fixture import FixtureError, build_fixture_write_input

    try:
        write_input = build_fixture_write_input(task_dir, condition)  # type: ignore[arg-type]
        run_dir = write_scaffold_run(write_input, out_dir)
    except (FixtureError, Exception) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from exc

    click.echo(f"run_id:    {write_input.manifest.run_id}")
    click.echo(f"condition: {condition}")
    click.echo(f"sources:   {len(write_input.sources)}")
    click.echo(f"output:    {run_dir}")


@cli.command("run-task")
@click.option(
    "--task",
    "task_dir",
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Path to source packet directory containing task.yaml.",
)
@click.option(
    "--condition",
    required=True,
    type=click.Choice(_CONDITIONS),
    help="Workflow condition used to select the frozen prompt template.",
)
@click.option(
    "--adapter",
    "adapter_name",
    default="stub",
    show_default=True,
    type=click.Choice(("stub", "mlx")),
    help="Model adapter to use. 'stub' is deterministic offline; 'mlx' loads a live MLX model.",
)
@click.option(
    "--model",
    "model_id",
    default=None,
    help="HuggingFace repo path for the MLX adapter. Required when --adapter=mlx.",
)
@click.option(
    "--temperature",
    default=0.7,
    show_default=True,
    type=float,
    help="Generation temperature passed to the adapter.",
)
@click.option(
    "--max-tokens",
    default=2048,
    show_default=True,
    type=int,
    help="Maximum generated tokens passed to the adapter.",
)
@click.option(
    "--show-prompt",
    is_flag=True,
    help="Print the rendered frozen prompt before the model output.",
)
@click.option(
    "--extract",
    "extract_claims",
    is_flag=True,
    help="Run the uniform extractor after raw generation.",
)
@click.option(
    "--extractor",
    "extractor_name",
    default="stub",
    show_default=True,
    type=click.Choice(("stub", "nemo", "small3", "all")),
    help=(
        "Extractor set to run when --extract is set. 'all' runs the stub, Nemo, "
        "and Small 3 and persists all three as sidecars."
    ),
)
@click.option(
    "--official-extractor",
    "official_extractor",
    default=None,
    type=click.Choice(("stub", "nemo", "small3")),
    help=(
        "Which extraction is written to claims.yaml (and the run disposition). "
        "Defaults to Nemo when --extractor=all (calibration of record: Nemo F1 "
        "0.8916, strong tier), else the single extractor that ran."
    ),
)
@click.option(
    "--write",
    "write_artifact",
    is_flag=True,
    help="Write a C-A scaffold-run-{run_id}/ directory via the writer bridge. Requires --extract.",
)
@click.option(
    "--output-dir",
    "output_dir",
    default=None,
    type=click.Path(file_okay=False, path_type=Path),
    help="Parent directory for the produced scaffold-run artifact. Required when --write is set.",
)
def run_task(
    task_dir: Path,
    condition: str,
    adapter_name: str,
    model_id: str | None,
    temperature: float,
    max_tokens: int,
    show_prompt: bool,
    extract_claims: bool,
    extractor_name: str,
    official_extractor: str | None,
    write_artifact: bool,
    output_dir: Path | None,
) -> None:
    """Run a source packet through a frozen prompt and a model adapter."""
    from research_scaffold_harness.runner import (
        MLXAdapterError,
        MLXModelAdapter,
        RunnerError,
        RunnerSettings,
        SourcePacketError,
        StubModelAdapter,
        load_source_packet,
        run_source_packet,
    )

    if write_artifact and not extract_claims:
        click.echo("Error: --write requires --extract", err=True)
        raise SystemExit(2)
    if write_artifact and output_dir is None:
        click.echo("Error: --write requires --output-dir", err=True)
        raise SystemExit(2)
    if adapter_name == "mlx" and not model_id:
        click.echo("Error: --adapter=mlx requires --model", err=True)
        raise SystemExit(2)
    if (
        official_extractor is not None
        and extractor_name != "all"
        and official_extractor != extractor_name
    ):
        click.echo(
            f"Error: --official-extractor={official_extractor} requires "
            f"--extractor={official_extractor} or --extractor=all",
            err=True,
        )
        raise SystemExit(2)

    try:
        packet = load_source_packet(task_dir)
        if adapter_name == "stub":
            adapter = StubModelAdapter()
        else:
            adapter = MLXModelAdapter(model_id=model_id)  # type: ignore[arg-type]
        settings = RunnerSettings(temperature=temperature, max_tokens=max_tokens)
        result = run_source_packet(packet, condition, adapter, settings)  # type: ignore[arg-type]
    except (RunnerError, SourcePacketError, MLXAdapterError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from exc

    click.echo(f"task_id:   {result.task_id}")
    click.echo(f"condition: {condition}")
    click.echo(f"adapter:   {result.response.model_id}")
    click.echo(f"template:  {result.prompt_template_id}")
    click.echo(f"hash:      {result.prompt_template_hash}")
    if result.response.model_revision:
        click.echo(f"revision:  {result.response.model_revision}")
    if result.response.quantization:
        click.echo(f"quant:     {result.response.quantization}")
    if show_prompt:
        click.echo("")
        click.echo("rendered_prompt:")
        click.echo(result.prompt)
    click.echo("")
    click.echo("raw_output:")
    click.echo(result.output_text, nl=False)

    if extract_claims:
        from research_scaffold_harness.extractor import (
            MlxNemoExtractor,
            MlxSmallExtractor,
            StubUniformExtractor,
            extract_claims_from_runner_result,
            extract_think_claims_from_runner_result,
        )
        from research_scaffold_harness.extractor.live import LiveExtractorError
        from research_scaffold_harness.runner.writer_bridge import (
            WriterBridgeError,
            mint_run_id,
            resolve_official_extractor,
            select_official_extraction,
            write_scaffold_run_from_extraction,
        )

        run_id = mint_run_id() if write_artifact else (
            f"stub-extract-{result.task_id}-{condition}"
        )
        exploratory_think = None
        try:
            extractors = []
            if extractor_name in {"stub", "all"}:
                extractors.append(StubUniformExtractor())
            if extractor_name in {"nemo", "all"}:
                extractors.append(MlxNemoExtractor())
            if extractor_name in {"small3", "all"}:
                extractors.append(MlxSmallExtractor())
            extractions = [
                extract_claims_from_runner_result(
                    result=result,
                    run_id=run_id,
                    adapter=extractor,
                )
                for extractor in extractors
            ]
            if extractor_name == "all":
                exploratory_think = extract_think_claims_from_runner_result(
                    result=result,
                    run_id=run_id,
                    adapter=extractors[1],
                )
        except (LiveExtractorError, MLXAdapterError) as exc:
            click.echo(f"Error: {exc}", err=True)
            raise SystemExit(1) from exc

        official_slug = resolve_official_extractor(extractor_name, official_extractor)
        try:
            extraction = select_official_extraction(extractions, official_slug)
        except WriterBridgeError as exc:
            click.echo(f"Error: {exc}", err=True)
            raise SystemExit(2) from exc
        click.echo("")
        click.echo("extraction:")
        click.echo(f"official_extractor: {extraction.extractor_id} ({official_slug})")
        for item in extractions:
            click.echo(f"extractor: {item.extractor_id}")
            click.echo(f"extractor_version: {item.extractor_version}")
            click.echo(f"is_stub: {str(item.is_stub).lower()}")
            click.echo(f"claim_count: {len(item.claims.claims)}")
            for diagnostic in item.diagnostics:
                click.echo(f"diagnostic: {diagnostic}")
            for claim in item.claims.claims:
                click.echo(f"- {claim.claim_id}: {claim.claim_text}")

        if write_artifact:
            assert output_dir is not None
            output_dir.mkdir(parents=True, exist_ok=True)
            bridge_result = write_scaffold_run_from_extraction(
                runner_result=result,
                extraction=extraction,
                source_packet=packet,
                output_dir=output_dir,
                extractor_sidecars=extractions if extractor_name == "all" else [],
                exploratory_think_extraction=exploratory_think,
            )
            click.echo("")
            click.echo("artifact:")
            click.echo(f"run_id:    {bridge_result.run_id}")
            click.echo(f"directory: {bridge_result.scaffold_run_dir}")
            click.echo(f"extractor: {bridge_result.extractor_id}")
            click.echo(f"is_stub:   {str(bridge_result.is_stub).lower()}")


@cli.command("verify-run")
@click.argument(
    "scaffold_run_dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
def verify_run(scaffold_run_dir: Path) -> None:
    """Verify integrity of a scaffold-run artifact directory."""
    from research_scaffold_harness.contracts.hashing import (
        compute_corpus_hash,
        verify_sha256sums,
    )
    from research_scaffold_harness.contracts.yaml_io import load_yaml

    errors: list[str] = []

    manifest_path = scaffold_run_dir / "scaffold_run.yaml"
    claims_path = scaffold_run_dir / "claims.yaml"
    contract_path = scaffold_run_dir / "CONTRACT_VERSION"
    corpus_dir = scaffold_run_dir / "corpus"

    for required in (manifest_path, claims_path, contract_path):
        if not required.exists():
            errors.append(f"Missing required file: {required.name}")

    if errors:
        _report_and_exit(errors)

    try:
        manifest = load_yaml(manifest_path)
    except Exception as exc:
        errors.append(f"scaffold_run.yaml failed to parse: {exc}")
        _report_and_exit(errors)

    try:
        load_yaml(claims_path)
    except Exception as exc:
        errors.append(f"claims.yaml failed to parse: {exc}")

    if corpus_dir.is_dir():
        expected_hash = manifest.get("corpus", {}).get("corpus_hash", "")
        actual_hash = compute_corpus_hash(corpus_dir)
        if expected_hash and actual_hash != expected_hash:
            errors.append(
                f"corpus_hash mismatch: manifest={expected_hash}, computed={actual_hash}"
            )

        for source_dir in sorted(corpus_dir.iterdir()):
            if not source_dir.is_dir():
                continue
            meta_path = source_dir / "metadata.yaml"
            if meta_path.exists():
                try:
                    load_yaml(meta_path)
                except Exception as exc:
                    errors.append(f"{source_dir.name}/metadata.yaml: {exc}")
            passages_path = source_dir / "passages.yaml"
            if passages_path.exists():
                try:
                    load_yaml(passages_path)
                except Exception as exc:
                    errors.append(f"{source_dir.name}/passages.yaml: {exc}")

    sha_errors = verify_sha256sums(scaffold_run_dir)
    errors.extend(sha_errors)

    if errors:
        _report_and_exit(errors)

    click.echo("PASS")


def _report_and_exit(errors: list[str]) -> None:
    click.echo("FAIL", err=True)
    for err in errors:
        click.echo(f"  - {err}", err=True)
    sys.exit(1)


if __name__ == "__main__":
    cli()
