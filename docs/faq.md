---
hide:
    - navigation
---
# FAQ

## Getting Started

### What is CSR Proxy?

CSR Proxy is a small service that accepts a Certificate Signing Request (CSR)
from a client and asks an ACME server to issue a certificate for it. It uses
PowerDNS to complete the DNS-01 challenge.

### When should I use CSR Proxy?

Use CSR Proxy when an application needs a publicly trusted certificate but
the private key must be created and kept by the client. The publisher can run
the signing infrastructure without receiving the client's private key.

### Where can I find installation instructions?

See the [installation guide](installation/index.md) and the
[Docker installation guide](installation/docker.md) for a complete deployment
example.

### How does a client request a certificate?

The client creates a private key and a PEM-encoded CSR, then sends the CSR body
to `POST /v1/sign`. For example:

```bash
curl -X POST --data-binary @my.csr \
  -o my.crt https://csr-proxy.example.com/v1/sign
```

The response is the issued certificate in PEM format. Keep the private key on
the client and use it with the returned certificate.

## Certificates and ACME

### Does CSR Proxy receive or generate the client's private key?

No. The client generates the private key and includes only the CSR in the
request. CSR Proxy forwards the CSR to the ACME server and returns the signed
certificate.

### Which CSR subjects are accepted?

CSR Proxy accepts only a CSR whose subject exactly matches the configured
`CSR_PROXY_SUBJ`. Requests with a different subject receive HTTP 400. The
domain used for ACME validation is extracted from the `CN` in that configured
subject, so configure the subject and DNS delegation for the same domain.

### Which ACME servers are supported?

CSR Proxy uses the ACME protocol through `gufo-acme` and defaults to the
Let's Encrypt staging directory. Set `CSR_PROXY_ACME_DIRECTORY` to the
directory URL of the ACME server you intend to use. Staging certificates are
for testing and are not trusted by browsers.

### How is domain ownership validated?

CSR Proxy completes the ACME DNS-01 challenge through PowerDNS. The relevant
zone must be served by the configured PowerDNS instance, and the domain must
be delegated so the ACME server can resolve the challenge record. See the
[Docker installation guide](installation/docker.md) for an example DNS setup.

### Does CSR Proxy support External Account Binding (EAB)?

Yes. Configure `CSR_PROXY_EAB_KID` and `CSR_PROXY_EAB_HMAC` together when your
ACME server requires EAB. Leave both unset when it does not. The HMAC value is
provided as base64 and decoded automatically.

## Configuration and Operation

### How do I configure CSR Proxy?

The service reads settings from `CSR_PROXY_*` environment variables. The
Docker installation guide includes a working example. At minimum, configure
the subject, contact email, ACME directory, PowerDNS API URL, and PowerDNS API
key; also provide a writable state directory for the ACME account state.

### What is the state file for?

CSR Proxy saves the ACME account state at `CSR_PROXY_STATE_PATH` (by default,
`/var/lib/csr-proxy/state.json`). Persist this file across restarts so the
service can reuse its ACME account instead of registering a new one.

### Why does the default setup use Let's Encrypt staging?

The staging directory is the safe default for setup and integration checks.
Once the service and DNS delegation work, configure the production directory
if you need certificates trusted by browsers and other clients.

### Should I expose the service directly to the internet?

The API has a single signing endpoint and does not implement client
authentication. Deploy it behind HTTPS and restrict access according to your
use case. The subject check limits which certificate name can be requested,
but does not identify the caller.

### Why does a signing request fail?

Check that the CSR is valid PEM, its subject exactly matches
`CSR_PROXY_SUBJ`, the configured ACME directory is reachable, and the domain's
DNS delegation allows the ACME server to see DNS-01 challenge records. Also
verify the PowerDNS API URL, API key, zone configuration, and writable state
path. Service logs include the subject and ACME/PowerDNS client activity.

## Development

### Where is the CSR Proxy source code?

The source code, issue tracker, and project history are available in the
[CSR Proxy GitHub repository](https://github.com/gufolabs/csr_proxy/).

### How do I run the test suite?

See [Building and Testing](dev/testing.md) for development setup and test
commands. The live API signing test requires the ACME and PowerDNS test
environment variables described there.

## About Gufo

> What is "Gufo"?

*Gufo* means *the Owl* in Italian.

> Why the owls?

We love owls and the viable parts of our technologies
were proven at the project, named "the Owl".

> What is "Gufo Labs"?

[Gufo Labs](https://gufolabs.com/) is the Milan-based company specialized on
network and IT consulting, and on software research.

> What is "Gufo Stack"?

We've extracted core components behind the [NOC](https://getnoc.com/) 
and released them as independent packages, available under the terms 
of the 3-clause BSD license. Our software shares common code quality standards 
and is battle-proven under the high load. We hope our key components will help 
the engineers and the developers to build reliable networks and robust network 
management software. 
See [more for details](https://gufolabs.com/products/gufo-stack/).
