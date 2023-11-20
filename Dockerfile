FROM python:3.12-slim-bullseye AS dev
COPY .requirements /tmp
RUN \
    set -x \
    && apt-get update \
    && apt-get install -y --no-install-recommends git\
    && pip install --upgrade pip\
    && pip install --upgrade build\
    && pip install \
    -r /tmp/deps.txt\
    -r /tmp/test.txt\
    -r /tmp/lint.txt\
    -r /tmp/docs.txt\
    -r /tmp/ipython.txt

FROM python:3.12-slim-bullseye AS container
RUN \
    set -x\
    && pip install --upgrade pip\
    && pip install csr_proxy==0.1.0