# AGENTS.md

CSR Proxy is a small Starlette/uvicorn service that receives a client's
Certificate Signing Request (CSR), forwards it to an RFC-8555 ACME server via the
`gufo-acme` `PowerDnsAcmeClient` (doing the DNS-01 challenge through PowerDNS), and
returns the signed certificate. Part of the Gufo Stack. Single endpoint:
`POST /v1/sign`. Code lives under `src/csr_proxy/` (setuptools src-layout, `py.typed`,
mypy-strict).

## Layout

- `src/csr_proxy/` — `api.py` (API + ACME orchestration), `cli.py` (arg parsing + run),
  `config.py` (`Config`, env reading), `log.py` (logger). `__init__.py` holds `__version__`.
- `tests/` — pytest. `test_project.py` asserts the repo layout; `test_ci.py` pins GitHub
  Action versions.
- `docs/` — MkDocs Material site (build target in CI).
- `.github/workflows/` — `py-tests.yml` (lint + test matrix), `publish.yml`,
  `build-docs.yml`, `docker-master.yml` (multi-stage build+push), `security.yml` (safety).

## Dev environment

- Python 3.11–3.14 (CI runs 3.11/3.12/3.13/3.14). Easiest start: the VS Code Dev Container
  (`.devcontainer/devcontainer.json`, builds Dockerfile `target=dev`, sets `PYTHONPATH: src`).
- **Run development commands only through `scripts/run-dev`.** This includes linters,
  formatters, type checkers, tests, build and docs commands, and project scripts. For
  example: `scripts/run-dev ruff check -q src/ tests/` or
  `scripts/run-dev pytest -v`. Running these commands or scripts directly on the host or
  inside a shell is prohibited; `scripts/run-dev` executes them in the repository's
  running devcontainer.
- Install (all extras, as the Dockerfile `dev` stage does):
  `scripts/run-dev pip install -e '.[test,lint,docs,test-extra]'`
  For lint only: `scripts/run-dev pip install -e '.[lint]'`.
- `PYTHONPATH=src` is required outside the container (CI and devcontainer both set it);
  agent-run commands still go through `scripts/run-dev`.
- Entry point: `csr-proxy` → `csr_proxy.cli:main`. Run locally:
  `scripts/run-dev csr-proxy` (reads config from `CSR_PROXY_*` env vars; `--help` for flags).

## Build & test (commands to pass to `scripts/run-dev`; based on CI / docs/dev/testing.md)

- Format (check / fix): `scripts/run-dev ruff format --check src/ tests/` /
  `scripts/run-dev ruff format src/ tests/`
  (docs also include `examples/`, but that directory does not exist locally).
- Lint: `scripts/run-dev ruff check -q src/ tests/`   (ruff autofixes; `F401` is unfixable).
- Types: `scripts/run-dev mypy src/`   (config is `strict = true`; `--strict` is the docs alias).
- Tests: `scripts/run-dev pytest -v`
  (coverage: `scripts/run-dev pytest -v --cov --cov-branch --cov-report=xml tests/`).
- Build a wheel (as `Dockerfile` `build` stage / `publish.yml` do):
  `scripts/run-dev python -m build --sdist --wheel` → artifacts in `dist/`.
- Docs: `scripts/run-dev mkdocs serve` (local) /
  `scripts/run-dev mkdocs gh-deploy --strict --force` (CI).
- No Makefile/tox; there are no npm/Rust/go targets — despite `docs/dev` and gufo-stack
  conventions mentioning Rust, this package is pure Python.

## Conventions

- **Ruff** is the formatter and linter (replaced black). `line-length = 79`, target
  `py311`, Google-style docstrings, double-quoted docstrings. Full rule set is broad
  (E/F/W/C90/I/D/YTT/ANN/S/BLE/B/A/C4/EM/ISC/ICN/PT/RET/SIM/PLC/PLW/PLR/PIE/RUF/UP).
  `pyproject.toml [tool.ruff.lint.per-file-ignores]` relaxes annotations/docstrings in
  `tests/*.py` and `__init__.py` — keep test files annotation-light as the config expects.
- **Mypy strict**: every public function/method is fully annotated, including the `self`
  arg (e.g. `def run(self: "Cli", ...)`). New code must pass `mypy src/` clean.
- **Import order** (enforced by ruff `isort`, first-party=`src`): group blocks with
  `# Python modules`, `# Third-party modules`, `# CSR Proxy modules` comment headers.
- **Copyright header** at the top of every source file:
  `# CSR Proxy: <title>` / `# Copyright (C) 2023-26, Gufo Labs` / separator lines.
- **Config** is a `@dataclass` populated by `Config.read()` from `CSR_PROXY_*` env vars
  (or `Config.default()`). `domain` is a `@cached_property` regex-extracted from
  `valid_subj` — a mismatched subject raises `ValueError`.
- **Version bump** (docs/dev/common.md): change `__version__` in
  `src/csr_proxy/__init__.py` AND add a section to `CHANGELOG.md` (Keep a Changelog,
  SemVer). Currently `0.3.0`.
- Tests aim for 100% coverage whenever possible.

## Pitfalls

- **`test_api.py` tests are gated behind env vars** `CI_CSR_PROXY_TEST_DOMAIN`,
  `CI_CSR_PROXY_TEST_API_URL`, `CI_CSR_PROXY_TEST_API_KEY` (skipif otherwise). A bare
  `pytest -v` runs the *other* suites but silently skips the real signing test; the only
  way to exercise `/v1/sign` end-to-end is with those three set to a live ACME + PowerDNS.
- **Default `acme_directory` is Let's Encrypt *staging*** — any real signing without
  explicit config hits staging, not production.
- **CLI validation is strict** (`cli._validate_config`): a readable+writable
  `state_path` dir, a non-empty `pdns_api_url` + `pdns_api_key`, and `eab_kid`/`eab_hmac`
  must be set *together or neither* — a lone EAB pair aborts startup.
- **`tests/test_ci.py` hard-pins Action versions** (`checkout@v6`, `cache@v5`,
  `setup-python@v6`, etc.). Bumping one Action label in a workflow breaks this test —
  update its `VERSIONS` list in lockstep.
- **`tests/test_project.py`** checks a fixed `REQUIRED_FILES` list (must stay sorted) —
  do not rename/move `docs/dev/*`, `CITATION.cff`, `SECURITY.md`, etc. without updating it.
- **Don't hand-edit** `src/csr_proxy.egg-info/`, `build/`, `dist/`, `.coverage`,
  `.ruff_cache` — generated, gitignored.
- Coverage config (`include = ["src/*"]`) and the src-layout packaging
  (`package-dir={"":"src"}`) mean imports are `from csr_proxy.api import ...`, not
  `from src.csr_proxy...`.
