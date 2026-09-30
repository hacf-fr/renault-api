"""Nox sessions."""

import os
import shutil
from pathlib import Path
from textwrap import dedent

import nox
from nox import Session
from nox import session

package = "renault_api"
python_versions = ["3.14", "3.13", "3.12", "3.11", "3.10"]
nox.needs_version = ">= 2024.3.2"
nox.options.default_venv_backend = "uv"
nox.options.sessions = [
    "pre-commit",
    "safety",
    "ty",
    "tests",
    "docs-build",
]


def uv_sync(session: Session, *groups: str, install_project: bool = True) -> None:
    """Install the locked dependencies into the session's virtualenv.

    Args:
        session: The Session object.
        groups: The dependency groups to install.
        install_project: Whether to install the project with its extras.
    """
    args = ["uv", "sync", "--locked", "--no-default-groups"]
    args += [f"--group={group}" for group in groups]
    args += ["--all-extras"] if install_project else ["--no-install-project"]
    session.run_install(
        *args,
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )


def activate_virtualenv_in_precommit_hooks(session: Session) -> None:
    """Activate virtualenv in hooks installed by pre-commit.

    This function patches git hooks installed by pre-commit to activate the
    session's virtual environment. This allows pre-commit to locate hooks in
    that environment when invoked from git.

    Args:
        session: The Session object.
    """
    virtualenv = session.env.get("VIRTUAL_ENV")
    if virtualenv is None:
        return

    hookdir = Path(".git") / "hooks"
    if not hookdir.is_dir():
        return

    for hook in hookdir.iterdir():
        if hook.name.endswith(".sample") or not hook.is_file():
            continue

        text = hook.read_text()
        bindir = repr(session.bin)[1:-1]  # strip quotes
        if not (
            Path("A") == Path("a") and bindir.lower() in text.lower() or bindir in text
        ):
            continue

        lines = text.splitlines()
        if not (lines[0].startswith("#!") and "python" in lines[0].lower()):
            continue

        header = dedent(
            f"""\
            import os
            os.environ["VIRTUAL_ENV"] = {virtualenv!r}
            os.environ["PATH"] = os.pathsep.join((
                {session.bin!r},
                os.environ.get("PATH", ""),
            ))
            """
        )

        lines.insert(1, header)
        hook.write_text("\n".join(lines))


@session(name="pre-commit", python=python_versions[0])
def precommit(session: Session) -> None:
    """Lint using pre-commit."""
    args = session.posargs or ["run", "--all-files", "--show-diff-on-failure"]
    uv_sync(session, "dev", install_project=False)
    session.run("pre-commit", *args)
    if args and args[0] == "install":
        activate_virtualenv_in_precommit_hooks(session)


@session(python=python_versions[0])
def safety(session: Session) -> None:
    """Scan dependencies for insecure packages."""
    requirements = Path(session.create_tmp(), "requirements.txt")
    session.run_install(
        "uv",
        "export",
        "--locked",
        "--all-extras",
        "--all-groups",
        "--no-hashes",
        "--no-emit-project",
        f"--output-file={requirements}",
        silent=True,
    )
    uv_sync(session, "dev", install_project=False)
    session.run(
        "safety",
        "check",
        "--full-report",
        f"--file={requirements}",
    )


@session(python=python_versions[0])
def ty(session: Session) -> None:
    """Type-check using ty."""
    args = session.posargs or ["src", "tests", "docs/conf.py"]
    uv_sync(session, "dev")
    session.run("ty", "check", *args)


@session(python=python_versions)
def tests(session: Session) -> None:
    """Run the test suite."""
    uv_sync(session, "dev")
    try:
        session.run("coverage", "run", "--parallel", "-m", "pytest", *session.posargs)
    finally:
        if session.interactive:
            session.notify("coverage", posargs=[])


@session(python=python_versions[0])
def coverage(session: Session) -> None:
    """Produce the coverage report."""
    args = session.posargs or ["report"]

    uv_sync(session, "dev", install_project=False)

    if not session.posargs and any(Path().glob(".coverage.*")):
        session.run("coverage", "combine")

    session.run("coverage", *args)


@session(name="docs-build", python=python_versions[0])
def docs_build(session: Session) -> None:
    """Build the documentation."""
    args = session.posargs or ["docs", "docs/_build"]
    if not session.posargs and "FORCE_COLOR" in os.environ:
        args.insert(0, "--color")

    uv_sync(session, "docs")

    build_dir = Path("docs", "_build")
    if build_dir.exists():
        shutil.rmtree(build_dir)

    session.run("sphinx-build", *args)


@session(python=python_versions[0])
def docs(session: Session) -> None:
    """Build and serve the documentation with live reloading on file changes."""
    args = session.posargs or ["--open-browser", "docs", "docs/_build"]
    uv_sync(session, "docs")

    build_dir = Path("docs", "_build")
    if build_dir.exists():
        shutil.rmtree(build_dir)

    session.run("sphinx-autobuild", *args)
