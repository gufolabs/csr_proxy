# ---------------------------------------------------------------------
# CSR Proxy: Configuration
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""Config class."""
# Python modules
import os
import re
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Type

DEFAULT_API_PORT = 8000
DEFAULT_SUBJ = (
    "CN=go.getnoc.com,OU=Gufo Thor,O=Gufo Labs,L=Milano,ST=Milano,C=IT"
)
DEFAULT_STATE_PATH = "/var/lib/csr-proxy/state.json"
DEFAULT_EMAIL = "test@example.com"
DEFAULT_ACME_DIRECTORY = (
    "https://acme-staging-v02.api.letsencrypt.org/directory"
)
DEFAULT_PDNS_API_URL = ""
DEFAULT_PDNS_API_KEY = "12345"

rx_subj = re.compile("CN=(.+?)(,|$)")


@dataclass
class Config(object):
    """
    The service's configuration.

    Attributes:
        api_port: API port to listen.
        valid_subj: Certificate subject to pass.
        state_path: A path to store ACME client state.
            Must be readable and writable.
        email: An email to register on ACME service.
        acme_directoy: ACME directory URL.
        pdns_api_url: Root URL of the PowerDNS api.
        pdns_api_key: API key to authorize on PowerDNS.
    """

    api_port: int
    valid_subj: str
    state_path: Path
    email: str
    acme_directory: str
    pdns_api_url: str
    pdns_api_key: str

    @classmethod
    def default(cls: Type["Config"]) -> "Config":
        """
        Get default config.

        Returns:
            Config instance.
        """
        return Config(
            api_port=DEFAULT_API_PORT,
            valid_subj=DEFAULT_SUBJ,
            state_path=Path(DEFAULT_STATE_PATH),
            email=DEFAULT_EMAIL,
            acme_directory=DEFAULT_ACME_DIRECTORY,
            pdns_api_url=DEFAULT_PDNS_API_URL,
            pdns_api_key=DEFAULT_PDNS_API_KEY,
        )

    @classmethod
    def read(cls: Type["Config"], prefix: str = "CSR_PROXY_") -> "Config":
        """
        Read config from environment.

        Returns:
            Config instance.
        """

        def _get(env_name: str, default: str) -> str:
            full_env_name = f"{prefix}{env_name}"
            return os.getenv(full_env_name, str(default))

        return Config(
            api_port=int(_get("API_PORT", str(DEFAULT_API_PORT))),
            valid_subj=_get("SUBJ", DEFAULT_SUBJ),
            state_path=Path(_get("STATE_PATH", DEFAULT_STATE_PATH)),
            email=_get("EMAIL", DEFAULT_EMAIL),
            acme_directory=_get(
                "ACME_DIRECTORY",
                DEFAULT_ACME_DIRECTORY,
            ),
            pdns_api_url=_get("PDNS_API_URL", DEFAULT_PDNS_API_URL),
            pdns_api_key=_get("PDNS_API_KEY", DEFAULT_PDNS_API_KEY),
        )

    @cached_property
    def domain(self: "Config") -> str:
        """
        Get domain name.

        Returns:
            Domain name.
        """
        match = rx_subj.match(self.valid_subj)
        if match is None:
            msg = f"Invalid subject: {self.valid_subj}"
            raise ValueError(msg)
        return match.group(1)
