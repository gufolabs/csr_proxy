# ---------------------------------------------------------------------
# CSR Proxy: Test config
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Third-party modules
import pytest

# CSR Proxy modules
from csr_proxy.config import Config


def test_config_default() -> None:
    Config.default()


def test_config_read() -> None:
    Config.read()


@pytest.mark.parametrize(
    ("subj", "expected"),
    [
        (
            "CN=go.getnoc.com,OU=Gufo Thor,O=Gufo Labs,L=Milano,ST=Milano,C=IT",
            "go.getnoc.com",
        ),
        (
            "CN=go.getnoc.com",
            "go.getnoc.com",
        ),
    ],
)
def test_domain(subj: str, expected: str) -> None:
    cfg = Config.default()
    cfg.valid_subj = subj
    assert cfg.domain == expected


def test_domain_invalid() -> None:
    cfg = Config.default()
    cfg.valid_subj = "go.getnoc.com"
    with pytest.raises(ValueError):
        cfg.domain
