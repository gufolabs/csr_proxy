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
from typing import Optional, Type

DEFAULT_TRACE_FORMAT = "terse"
DEFAULT_API_HOST = "127.0.0.1"
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
        trace_format: Traceback format. "terse" or "extend"
        api_host: API host to listen.
        api_port: API port to listen.
        valid_subj: Certificate subject to pass.
        state_path: A path to store ACME client state.
            Must be readable and writable.
        email: An email to register on ACME service.
        acme_directoy: ACME directory URL.
        pdns_api_url: Root URL of the PowerDNS api.
        pdns_api_key: API key to authorize on PowerDNS.
        eab_kid: Optional external account binding key id.
        eab_hmac: Optional external account binding HMAC (base64).
    """

    trace_format: str
    api_host: str
    api_port: int
    valid_subj: str
    state_path: Path
    email: str
    acme_directory: str
    pdns_api_url: str
    pdns_api_key: str
    eab_kid: Optional[str] = None
    eab_hmac: Optional[str] = None

    @classmethod
    def default(cls: Type["Config"]) -> "Config":
        """
        Get default config.

        Returns:
            Config instance.
        """
        return Config(
            trace_format=DEFAULT_TRACE_FORMAT,
            api_host=DEFAULT_API_HOST,
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

        def _maybe_get(env_name: str) -> Optional[str]:
            full_env_name = f"{prefix}{env_name}"
            return os.getenv(full_env_name)

        return Config(
            trace_format=_get("TRACE_FORMAT", DEFAULT_TRACE_FORMAT),
            api_host=_get("API_HOST", DEFAULT_API_HOST),
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
            eab_kid=_maybe_get("EAB_KID"),
            eab_hmac=_maybe_get("EAB_HMAC"),
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
