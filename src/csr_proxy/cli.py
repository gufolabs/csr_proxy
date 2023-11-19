# ---------------------------------------------------------------------
# CSR Proxy: Main entrypoint
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""Command line parsing and service starting."""
# Python modules
import argparse
import os
import sys
from enum import IntEnum
from typing import List

# CSR Proxy modules
from . import __version__
from .api import API
from .config import Config
from .log import logger

NAME: str = "csr-proxy"


class ExitCode(IntEnum):
    """
    Cli exit codes.

    Attributes:
        OK: Successful exit
    """

    OK = 0
    ERR = 1


class Cli(object):
    """Command-line proceessing."""

    def run(self: "Cli", args: List[str]) -> ExitCode:
        """
        Run csr-proxy from arguments.

        Args:
            args: List of command-line arguments.

        Returns:
            Exit code
        """
        # Read config from environment
        config = Config.read()
        # Parse args
        ns = self._parse_args(config, args)
        if ns.version:
            return self.handle_version()
        # Prepare configuration
        self._apply_namespace(config, ns)
        # Validate configuration
        if not self._validate_config(config):
            return ExitCode.ERR
        # Run
        API.run(config)
        return ExitCode.OK

    @staticmethod
    def _parse_args(config: Config, args: List[str]) -> argparse.Namespace:
        """
        Parse command-line arguments and return Namespace.

        Args:
            config: Service default config.
            args: Command-line arguments.

        Returns:
            argparse Namespace.
        """
        parser = argparse.ArgumentParser(
            prog=NAME,
            description=(
                "Simple service to sign the clients' CSR"
                "via the ACME server."
            ),
        )
        parser.add_argument("-v", "--version", action="store_true")
        parser.add_argument(
            "--api-port", type=int, default=config.api_port, help="API Port"
        )
        parser.add_argument(
            "--valid-subj", default=config.valid_subj, help="Valid CSR subject"
        )
        parser.add_argument(
            "--state-path", default=config.state_path, help="State file path"
        )
        parser.add_argument(
            "--email", default=config.email, help="Registration email"
        )
        parser.add_argument(
            "--acme-directory",
            default=config.acme_directory,
            help="ACME Directory URL",
        )
        parser.add_argument(
            "--pdns-api-url",
            default=config.pdns_api_url,
            help="PowerDNS API Root URL",
        )
        parser.add_argument(
            "--pdns-api-key",
            default=config.pdns_api_key,
            help="PowerDNS API key",
        )
        return parser.parse_args(args)

    @staticmethod
    def _apply_namespace(config: Config, ns: argparse.Namespace) -> None:
        """
        Apply command-line args to config.

        Args:
            config: Config
            ns: Namespace
        """
        if ns.api_port:
            config.api_port = ns.api_port
        if ns.valid_subj:
            config.valid_subj = ns.valid_subj
        if ns.state_path:
            config.state_path = ns.state_path
        if ns.email:
            config.email = ns.email
        if ns.acme_directory:
            config.acme_directory = ns.acme_directory
        if ns.pdns_api_url:
            config.pdns_api_url = ns.pdns_api_url
        if ns.pdns_api_key:
            config.pdns_api_key = ns.pdns_api_key

    @staticmethod
    def _validate_config(config: Config) -> bool:
        """
        Validate configuration.

        Args:
            config: Config instance.

        Returns:
            True - if config is valid.
            False - otherwise.
        """
        # Check state file
        if not os.access(config.state_path, os.R_OK):
            logger.error("%s is not readable. Stoppig", config.state_path)
            return False
        if not os.access(config.state_path, os.W_OK):
            logger.error("%s is not writabl. Stoppig", config.state_path)
            return False
        if not config.pdns_api_url:
            logger.error("--pdns-api-url is missed")
            return False
        if not config.pdns_api_key:
            logger.error("--pdns-api-key is missed")
            return False
        return True

    def handle_version(self: "Cli") -> ExitCode:
        """
        Process `--version` flag.

        Returns:
            Exit code.
        """
        print(f"{NAME} v{__version__}")
        return ExitCode.OK


def main() -> int:
    """Run `csr-proxy` with command-line arguments."""
    return Cli().run(sys.argv[1:]).value
