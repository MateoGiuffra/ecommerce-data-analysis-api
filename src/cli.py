from __future__ import annotations
import os
import sys
import subprocess
import time
from typing import Optional

import typer


app = typer.Typer(name="ecommerce-cli", help="CLI for ecommerce-data-analysis-api")


def _ensure_settings_importable() -> None:
    """Ensure application settings can be imported early and raise a clear error if not."""
    try:
        # Import settings to surface misconfiguration early (env vars missing, etc.)
        from src.core.config import settings  # noqa: F401
    except Exception as exc:  # pragma: no cover - operational check
        raise typer.Exit(code=2)


@app.command("runserver")
def runserver(port: int = 8000, pre_kill: bool = True, kill_celery: bool = False):
    """Run the full development stack: optionally kill ports/celery, then start honcho.

    This replaces the old `dev:all` poe task. It will run `python scripts/kill_port.py <port>`
    if `--pre-kill` is set (default), optionally run `scripts/kill_celery.py` with
    `--kill-celery`, and finally run `honcho start` which brings up Redis, FastAPI, etc.
    """
    _run_dev_all_flow(port=port, pre_kill=pre_kill, kill_celery=kill_celery)


@app.command("runfastapi")
def runfastapi(host: str = "127.0.0.1", port: int = 8000, reload: bool = True, pre_kill: bool = True):
    """Run the FastAPI app using uvicorn.

    Example: `ecommerce-cli runfastapi --host 0.0.0.0 --port 8000 --reload`
    """
    _ensure_settings_importable()
    # Optionally run the kill script to free the port before starting uvicorn
    if pre_kill:
        kill_script = os.path.join(os.getcwd(), "public", "scripts", "kill_port.py")
        if os.path.exists(kill_script):
            try:
                subprocess.check_call([sys.executable, kill_script, str(port)])
            except subprocess.CalledProcessError:
                typer.echo(f"Warning: kill script {kill_script} failed or found no process on port {port}")

    try:
        import uvicorn

        from src.main import app as fastapi_app

        uvicorn.run(fastapi_app, host=host, port=port, reload=reload)
    except Exception as exc:  # pragma: no cover - runtime launcher
        typer.echo(f"Error running server: {exc}")
        raise typer.Exit(code=1)


@app.command()
def migrate(message: str = "auto migration"):
    """Create an alembic revision (autogenerate) and upgrade head.

    Example: `ecommerce-cli migrate --message "add table"`
    """
    _ensure_settings_importable()
    try:
        # Create revision
        subprocess.check_call([sys.executable, "-m", "alembic", "revision", "--autogenerate", "-m", message])
        # Upgrade head
        subprocess.check_call([sys.executable, "-m", "alembic", "upgrade", "head"])
    except subprocess.CalledProcessError as exc:  # pragma: no cover - integration
        typer.echo(f"Alembic command failed: {exc}")
        raise typer.Exit(code=1)


@app.command()
def alembic(cmd: str = typer.Argument(..., help="Alembic command string, e.g. 'upgrade head'")):
    """Pass-through to alembic. Example: `ecommerce-cli alembic 'current'`"""
    _ensure_settings_importable()
    parts = cmd.split()
    try:
        subprocess.check_call([sys.executable, "-m", "alembic"] + parts)
    except subprocess.CalledProcessError as exc:  # pragma: no cover - integration
        typer.echo(f"Alembic command failed: {exc}")
        raise typer.Exit(code=1)


@app.command()
def celeryworker(concurrency: int = 1, loglevel: str = "info"):
    """Start a celery worker. Ensure CELERY_APP env var or default path is set.

    Example: `ecommerce-cli celeryworker --concurrency 4`
    """
    _ensure_settings_importable()
    celery_app_path = os.environ.get("CELERY_APP", "src.tasks.worker:celery_app")
    cmd = ["celery", "-A", celery_app_path, "worker", "-l", loglevel, "-c", str(concurrency)]
    try:
        subprocess.check_call(cmd)
    except FileNotFoundError:
        typer.echo("`celery` executable not found. Is Celery installed in this environment?")
        raise typer.Exit(code=3)
    except subprocess.CalledProcessError as exc:  # pragma: no cover - integration
        typer.echo(f"Celery worker failed: {exc}")
        raise typer.Exit(code=1)


def _run_dev_all_flow(port: int = 8000, pre_kill: bool = True, kill_celery: bool = False) -> None:
    """Internal helper: optionally run kill scripts and start honcho.

    pre_kill controls whether `scripts/kill_port.py <port>` is executed.
    kill_celery controls whether `scripts/kill_celery.py` is executed.
    """
    _ensure_settings_importable()

    # Respect pre_kill/kill_celery first (these are the same semantics as the
    # poe tasks). We run local scripts if present.
    if pre_kill:
        kill_script = os.path.join(os.getcwd(), "public", "scripts", "kill_port.py")
        if os.path.exists(kill_script):
            try:
                typer.echo(f"Running kill script to free port {port}...")
                subprocess.check_call([sys.executable, kill_script, str(port)])
            except subprocess.CalledProcessError as exc:
                typer.echo(f"Kill script failed: {exc}")
            else:
                # Give OS a short moment to release the socket/port
                time.sleep(0.3)

    if kill_celery:
        kill_celery_script = os.path.join(os.getcwd(), "public", "scripts", "kill_celery.py")
        if os.path.exists(kill_celery_script):
            try:
                typer.echo("Running kill_celery script...")
                subprocess.check_call([sys.executable, kill_celery_script])
            except subprocess.CalledProcessError as exc:
                typer.echo(f"kill_celery script failed: {exc}")

    # First try: run the original poe task which performs the `kill` + `honcho`
    # flow. This mirrors the previous developer workflow exactly and avoids
    # duplicating behavior here. Running `poetry run poe dev:all` will usually
    # start the same processes your Poe config did.
    try:
        typer.echo("Attempting to run: poetry run poe dev (web) and poetry run poe dev:all (workers)...")
        # Start the web server via `poe dev` in the background so honcho (workers)
        # and the web process run concurrently. Ensure we terminate the web
        # process if the honcho/dev:all process exits.
        web_proc = subprocess.Popen(["poetry", "run", "poe", "dev"], stdout=sys.stdout, stderr=sys.stderr)
        try:
            subprocess.check_call(["poetry", "run", "poe", "dev:all"])  # blocks (honcho)
            return
        finally:
            # When dev:all returns, ensure the web background process is terminated.
            if web_proc.poll() is None:
                try:
                    web_proc.terminate()
                except Exception:
                    pass
    except FileNotFoundError:
        typer.echo("`poetry` not found in PATH; falling back to honcho/procfile logic.")
    except subprocess.CalledProcessError as exc:
        typer.echo(f"`poe dev:all` failed: {exc}; falling back to honcho/procfile logic.")

    # If poe wasn't available or failed, fall back to honoring a Procfile or
    # starting FastAPI directly as before.
    procfile_paths = [os.path.join(os.getcwd(), p) for p in ("Procfile", "Procfile.dev")]
    found_procfile = any(os.path.exists(p) for p in procfile_paths)

    if not found_procfile:
        typer.echo("No Procfile found — starting FastAPI directly (honcho skipped).")
        try:
            # Call the runfastapi function directly in-process so logs are
            # visible immediately and we don't spawn nested Python processes.
            runfastapi(host="0.0.0.0", port=port, reload=True, pre_kill=False)
        except Exception as exc:  # pragma: no cover - runtime
            typer.echo(f"Fallback to runfastapi failed: {exc}")
            raise typer.Exit(code=3)
        return

    try:
        typer.echo("Starting honcho (Procfile)...")
        subprocess.check_call(["honcho", "start"])
    except FileNotFoundError:
        typer.echo("`honcho` executable not found. Falling back to starting FastAPI directly.")
        try:
            runfastapi(host="0.0.0.0", port=port, reload=True, pre_kill=False)
        except Exception as exc:  # pragma: no cover - runtime
            typer.echo(f"Fallback to runfastapi failed: {exc}")
            raise typer.Exit(code=3)
    except subprocess.CalledProcessError as exc:
        typer.echo(f"Honcho failed: {exc}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
