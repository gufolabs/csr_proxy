---
hide:
    - navigation
---
# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

To see unreleased changes, please see the [CHANGELOG on the master branch](https://github.com/gufolabs/csr_proxy/blob/master/CHANGELOG.md) guide.

## [Unreleased]

### Added

* `--trace-format` option.

### Changed

* uvicorn 0.36.0

### Security

* docker: Install security patches.
* docker: Use python:3.13-slim-trixie as base.
* Gufo ACME 0.6.0

### Infrastructure

* Replace black with ruff format
* ruff 0.11.2
* mypy 1.13.0
* Codecov integration.
* Move dependencies to pyproject.toml

## 0.2.0 - 2023-11-23

### Added

* External Account Binding support.

## 0.1.0 - 2023-11-20

### Added

* Initial release.