
FROM $CI_REGISTRY/$CI_PROJECT_NAMESPACE/lazy_images/uv

COPY ./pyproject.toml ./uv.lock /tmp/

RUN uv export --directory /tmp --format requirements.txt | pip install -r /dev/stdin && rm -f /tmp/*
