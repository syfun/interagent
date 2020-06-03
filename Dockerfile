FROM python:3.8-slim-buster as builder

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

ARG PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/

COPY ./packages packages
COPY ./requirements requirements
COPY ./requirements.txt requirements.txt

RUN pip install --upgrade pip \
    && pip install --no-cache-dir \
    --index-url $PIP_INDEX_URL \
    --requirement requirements.txt


FROM python:3.8-slim-buster

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY --from=builder /opt/venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

COPY . /app
COPY ./scripts /scripts

RUN chmod +x /scripts

WORKDIR /app

ENTRYPOINT ["/scripts/entrypoint"]
