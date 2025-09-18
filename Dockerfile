FROM python:3.13-slim-trixie AS dev
COPY . /workspaces/csr_proxy
WORKDIR /workspaces/csr_proxy
RUN \
    set -x \
    && apt-get update \
    && apt-get -y dist-upgrade \
    && apt-get -y autoremove\
    && apt-get install -y --no-install-recommends git\
    && pip install --upgrade pip\
    && pip install --upgrade build\
    && pip install -e .[deps,test,lint,docs,ipython,test-extra]

FROM python:3.13-slim-trixie AS build
RUN \
    set -x \
    && apt-get update \
    && apt-get install -y --no-install-recommends git\
    && pip install --upgrade pip\
    && pip install --upgrade build\
    && python -m build --wheel

FROM python:3.13-slim-trixie AS container
COPY --from=build /workspace/dist/csr_proxy-*.whl /tmp
WORKDIR /
ENTRYPOINT /usr/local/bin/csr-proxy
RUN \
    set -x\
    && apt-get update \
    && apt-get -y dist-upgrade \
    && apt-get -y autoremove\
    && pip install --upgrade pip \
    && pip install /tmp/csr_proxy-*.whl \
    && rm /tmp/csr_proxy*