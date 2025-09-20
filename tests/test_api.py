# ---------------------------------------------------------------------
# CSR Proxy: Test API
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
import os
import tempfile

# Third-party modules
import pytest
from gufo.acme.clients.base import AcmeClient
from starlette.testclient import TestClient

# CSR Proxy modules
from csr_proxy.api import API
from csr_proxy.config import Config

EMAIL = "acme-000000000@gufolabs.com"

ENV_CI_CSR_PROXY_TEST_DOMAIN = "CI_CSR_PROXY_TEST_DOMAIN"
ENV_CI_CSR_PROXY_TEST_API_URL = "CI_CSR_PROXY_TEST_API_URL"
ENV_CI_CSR_PROXY_TEST_API_KEY = "CI_CSR_PROXY_TEST_API_KEY"


def to_skip_scenario() -> bool:
    return not (
        os.environ.get(ENV_CI_CSR_PROXY_TEST_DOMAIN)
        and os.environ.get(ENV_CI_CSR_PROXY_TEST_API_URL)
        and os.environ.get(ENV_CI_CSR_PROXY_TEST_API_KEY)
    )


SKIP_REASON = (
    f"{ENV_CI_CSR_PROXY_TEST_DOMAIN}, {ENV_CI_CSR_PROXY_TEST_API_URL}, {ENV_CI_CSR_PROXY_TEST_API_KEY}"
    " variables must be set"
)


@pytest.mark.skipif(to_skip_scenario(), reason=SKIP_REASON)
def test_sign() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        config = Config.default()
        config.email = EMAIL
        config.domain = os.getenv(ENV_CI_CSR_PROXY_TEST_DOMAIN)
        config.state_path = os.path.join(tmp, "state.json")
        config.pdns_api_url = os.getenv(ENV_CI_CSR_PROXY_TEST_API_URL)
        config.pdns_api_key = os.getenv(ENV_CI_CSR_PROXY_TEST_API_KEY)
        config.valid_subj = f"CN={config.domain}"
        # Generate CSR
        pk = AcmeClient.get_domain_private_key()
        csr = AcmeClient.get_domain_csr(config.domain, pk)
        for _ in range(2):
            # Test
            api = API(config)
            client = TestClient(api.app)
            response = client.post("/v1/sign", content=csr)
            assert response.status_code == 200
            # Second try
            response = client.post("/v1/sign", content=csr)
            assert response.status_code == 200


@pytest.mark.skipif(to_skip_scenario(), reason=SKIP_REASON)
def test_invalid_sub() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        config = Config.default()
        config.email = EMAIL
        config.domain = os.getenv(ENV_CI_CSR_PROXY_TEST_DOMAIN)
        config.state_path = os.path.join(tmp, "state.json")
        config.pdns_api_url = os.getenv(ENV_CI_CSR_PROXY_TEST_API_URL)
        config.pdns_api_key = os.getenv(ENV_CI_CSR_PROXY_TEST_API_KEY)
        config.valid_subj = f"CN={config.domain}"
        # Generate CSR
        pk = AcmeClient.get_domain_private_key()
        csr = AcmeClient.get_domain_csr("xxx" + config.domain, pk)
        api = API(config)
        client = TestClient(api.app)
        response = client.post("/v1/sign", content=csr)
        assert response.status_code == 400
