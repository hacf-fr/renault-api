# renault-api

Async Python client for the Renault / Dacia APIs (Gigya for authentication,
Kamereon for vehicle data and actions), with an optional `renault-api` CLI.
Its main consumer is the Home Assistant `renault` integration.

## Commands

```console
uv sync --all-extras                       # install (dev + docs groups by default)
uv run pytest                              # tests
uv run pytest --snapshot-update            # refresh syrupy snapshots (tests/__snapshots__)
uv run ty check src tests docs/conf.py     # type checking
uv run pre-commit run --all-files          # ruff, prettier, whitespace, ...
uv run sphinx-build docs docs/_build       # docs (Python 3.14+ only)
```

CI runs the same commands with `--locked`; keep `uv.lock` in sync with
`pyproject.toml`.

## Layout

- `src/renault_api/gigya/`: Gigya login, account info and JWT.
- `src/renault_api/kamereon/`: Kamereon models and schemas. `models.py` holds
  `_VEHICLE_ENDPOINTS`, the per-model-code (e.g. `XCB1VE`) map of supported
  endpoints, and `VEHICLE_SPECIFICATIONS` / `GATEWAY_SPECIFICATIONS`.
- `src/renault_api/renault_{client,account,vehicle,session}.py`: public API.
- `src/renault_api/cli/`: click CLI.
- `tests/fixtures/kamereon/<endpoint group>/`: recorded JSON responses;
  `vehicles/*.json` drive the parametrized per-vehicle tests, and
  `expected_specs.json` holds the expected specs per fixture file.
- `docs/`: Sphinx, reStructuredText. `docs/endpoints/` documents endpoints per
  vehicle; `docs/myr-gateway.rst` documents the app's `apis.renault.com` gateway.

## Conventions

- Python 3.10+ (`target-version = "py310"`); don't use newer syntax.
- Ruff with `force-single-line` imports and Google-style docstrings.
- 100% test coverage is required; add tests with every change.
- Dependency floors (`aiohttp`, `PyJWT`, ...) follow what Home Assistant core
  pins. Don't raise them without checking HA.
- Fixtures must be anonymised: VINs start with `VF1AAAA`, registration numbers
  with `REG-`, `radioCode` is `1234`, and no real account or person ids.
- New vehicle model: add its model code to `_VEHICLE_ENDPOINTS`, add the
  fixtures, then update `expected_specs.json` and the snapshots.

## Reviewing contributor PRs

Contributor PRs are checked out locally as `pr/<user>/<number>`, tracking a
remote named after the contributor. Push follow-ups as new commits on top of
the PR head; never force-push to a contributor's fork.

## MyRenault app analysis

To check API behaviour against the official app (endpoints, headers,
featureIds), use the `apk-analysis` skill. Work happens in the git-ignored
`.apk_analysis/`; never commit APKs or decompiled sources.
