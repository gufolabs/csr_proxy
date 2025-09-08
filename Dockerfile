FROM python:3.13-slim-trixie AS dev
COPY .requirements /tmp
RUN \
    set -x \
    && apt-get update \
    && apt-get -y dist-upgrade \
    && apt-get -y autoremove\
    && apt-get install -y --no-install-recommends git\
    && pip install --upgrade pip\
    && pip install --upgrade build\
    && pip install \
    -r /tmp/deps.txt\
    -r /tmp/test.txt\
    -r /tmp/lint.txt\
    -r /tmp/docs.txt\
    -r /tmp/ipython.txt

FROM python:3.13-slim-trixie AS build
COPY pyproject.toml /workspace/
COPY src/ /workspace/src/
WORKDIR /workspace/
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