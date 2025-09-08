# ---------------------------------------------------------------------
# CSR Proxy: API handler
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""API endpoint."""

# Python modules
import asyncio
import os
from typing import Optional

import uvicorn
from cryptography import x509

# Third-party modules
from gufo.acme.clients.powerdns import PowerDnsAcmeClient
from gufo.acme.types import ExternalAccountBinding
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

# CSR Proxy modules
from . import __version__
from .config import Config
from .log import logger


class API(object):
    """
    API Enpoint.

    Accepts the client requests and orchestrates
    DNS and ACME servers.

    Args:
        config: Service configuration.
    """

    def __init__(self: "API", config: Config) -> None:
        self.config = config
        self.app = self._get_app()
        self.client_state: Optional[bytes] = None
        self.client_lock = asyncio.Lock()
        self.sign_lock = asyncio.Lock()

    async def get_client(self: "API") -> PowerDnsAcmeClient:
        """
        Get PowerDnsAcmeClient instance.

        Updates state when necessary.

        Returns:
            Configured ACME client.
        """
        async with self.client_lock:
            # Read state file when necessary
            if not self.client_state and os.path.exists(
                self.config.state_path
            ):
                logger.warning(
                    "Reading state file from %s", self.config.state_path
                )
                with open(self.config.state_path, "rb") as fp:
                    self.client_state = fp.read()
            # Try to instantiate from state
            if self.client_state:
                return PowerDnsAcmeClient.from_state(
                    self.client_state,
                    api_url=self.config.pdns_api_url,
                    api_key=self.config.pdns_api_key,
                )
            # Register new account
            key = PowerDnsAcmeClient.get_key()
            client = PowerDnsAcmeClient(
                self.config.acme_directory,
                key=key,
                api_url=self.config.pdns_api_url,
                api_key=self.config.pdns_api_key,
            )
            if self.config.eab_kid and self.config.eab_hmac:
                eab = ExternalAccountBinding(
                    kid=self.config.eab_kid,
                    hmac_key=PowerDnsAcmeClient.decode_auto_base64(
                        self.config.eab_hmac
                    ),
                )
            else:
                eab = None
            await client.new_account(self.config.email, external_binding=eab)
            # Save state
            self.client_state = client.get_state()
            logger.warning(
                "Writing client state to %s", self.config.state_path
            )
            with open(self.config.state_path, "wb") as fp:
                fp.write(self.client_state)
            return client

    @staticmethod
    def get_subj(csr: bytes) -> str:
        """
        Get subject from CSR.

        Arguments:
            csr: CSR in PEM format.

        Returns:
            CSR subject.
        """
        c = x509.load_pem_x509_csr(csr)
        return c.subject.rfc4514_string()

    async def sign(self: "API", request: Request) -> Response:
        """
        Sign endpoint.

        Accepts client's CSR, signs it and
        returns the signed certificate.

        Args:
            request: HTTP request.

        Returns:
            HTTP Response.
        """
        # Fetch CSR
        csr_body = await request.body()
        # Check subject
        subj = self.get_subj(csr_body)
        logger.warning("Signing request: %s", subj)
        if subj != self.config.valid_subj:
            logger.error(
                "Invalid subject. Expecting '%s' got '%s'",
                self.config.valid_subj,
                subj,
            )
            return Response("Invalid subject", status_code=400)
        # Get innitialized ACME client
        async with await self.get_client() as client, self.sign_lock:
            cert = await client.sign(self.config.domain, csr_body)
        return Response(cert)

    def _get_app(self: "API") -> Starlette:
        """
        Get Startlette app.

        Returns:
            Initialized Starlette instance.
        """
        return Starlette(
            routes=[Route("/v1/sign", endpoint=self.sign, methods=["POST"])]
        )

    @staticmethod
    def run(config: Optional[Config]) -> None:
        """Run service."""
        config = config or Config.read()
        api = API(config)
        logger.warning("Runnning csr-proxy v%s", __version__)
        uvicorn.run(api.app, host=config.api_host, port=config.api_port)
