# syntax = docker/dockerfile:1.2

# Best practice: Choose a stable base image and tag.
FROM python:3.11-slim-buster AS build-image

# Best practice: Make sure apt-get doesn't run in interactive mode.
RUN export DEBIAN_FRONTEND=noninteractive && \
  apt-get update && \
  apt-get install -y --no-install-recommends curl build-essential python-dev libffi-dev libssl-dev

# Install PDM.
RUN curl -sSL https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py | python3 - --version=2.3.2
ENV PATH=/root/.local/bin:${PATH}

# Need Rust for Python Cryptography >=3.5 build for linux/arm/v7.
# I'm having trouble making this work (e.g. "spurious network error" trying to
# get pyo3 dependency) after updating from 3.3.1 to 3.4.8. So for now...
# RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
# ENV PATH="/root/.cargo/bin:$PATH"
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

# We don't create the appuser yet, but we'll still use this as the WORKDIR
# so that shebangs in any scripts match up when we copy the virtualenv.
ENV ROOTDIR=/home/appuser

WORKDIR ${ROOTDIR}

# Install dependencies.
#
# Best practices:
# * `COPY` in files only when needed.
COPY pyproject.toml pdm.lock ./
RUN pdm install --prod --no-lock --no-editable

# Copy in the code.
WORKDIR ${ROOTDIR}
COPY . .

# Install application.
RUN pdm install --prod --no-lock --no-editable

# ============================================================================

FROM python:3.11-slim-buster AS run-image

# Install security updates, and some useful packages.
#
# Best practices:
# * Make sure apt-get doesn't run in interactive mode.
# * Update system packages.
# * Pre-install some useful tools.
# * Minimize system package installation.
RUN export DEBIAN_FRONTEND=noninteractive && \
  apt-get update && \
  apt-get -y upgrade && \
  apt-get install -y --no-install-recommends tini procps net-tools && \
  apt-get -y clean && \
  rm -rf /var/lib/apt/lists/*

# Create a new user to run as.
#
# Best practices: Don't run as root.
RUN useradd --create-home appuser
USER appuser
WORKDIR /home/appuser

# Copy virtualenv -- location is /build/.venv because of:
# - WORKDIR in the build phase
# - `in-project = true` in poetry.toml
# Best practices: Avoid extra chowns.
COPY --from=build-image --chown=appuser /home/appuser/.venv ./.venv
ENV PATH="/home/appuser/.venv/bin:$PATH"

# Best practices: Prepare for C crashes.
ENV PYTHONFAULTHANDLER=1

# Run the code when the image is run:
#
# Best practices:
# * Add an `init` process
# * Make sure images shut down correctly (via ENTRYPOINT [] syntax).
ENTRYPOINT ["tini", "--", "mirror"]
