
FROM ghcr.io/astral-sh/uv:python3.12-trixie

COPY ./pyproject.toml ./uv.lock /tmp/

RUN uv export --directory /tmp --format requirements.txt | pip install -r /dev/stdin

RUN rm -f /tmp/*
