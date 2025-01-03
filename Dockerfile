# syntax = docker/dockerfile:1.2
ARG PYTHON_VERSION=3.12
ARG DEBIAN_RELEASE=bookworm

# Best practice: Choose a stable base image and tag.
FROM python:${PYTHON_VERSION}-slim-${DEBIAN_RELEASE} AS build-image

# The scope for ARG is kind of wacky -- repeat here after the FROM statement
# to make it available in the rest of the Dockerfile.
ARG PYTHON_VERSION

# Best practice: Make sure apt-get doesn't run in interactive mode.
RUN export DEBIAN_FRONTEND=noninteractive && \
  apt-get update && \
  apt-get install -y --no-install-recommends curl build-essential python3-dev libffi-dev libssl-dev

# Install PDM.
RUN curl -sSL https://pdm-project.org/install-pdm.py | python${PYTHON_VERSION} - --version=2.22.1
ENV PATH=/root/.local/bin:${PATH}

# We don't create the appuser yet, but we'll still use this as the WORKDIR
# so that shebangs in any scripts match up when we copy the virtualenv.
ENV ROOTDIR=/home/appuser

WORKDIR ${ROOTDIR}

# Install dependencies.
COPY pyproject.toml pdm.lock ./
RUN pdm install --prod --frozen-lockfile --no-editable

# ============================================================================

FROM python:${PYTHON_VERSION}-slim-${DEBIAN_RELEASE} AS run-image

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

# Copy virtualenv from build image.
# Best practices: Avoid extra chowns.
COPY --from=build-image --chown=appuser /home/appuser/.venv ./.venv
ENV PATH="/home/appuser/.venv/bin:$PATH"

# Copy in the application code.
WORKDIR ${ROOTDIR}
COPY . .

# Best practices: Prepare for C crashes.
ENV PYTHONFAULTHANDLER=1

# Run the code when the image is run:
#
# Best practices:
# * Add an `init` process
# * Make sure images shut down correctly (via ENTRYPOINT [] syntax).
CMD ["tini", "--", "uvicorn", "--host", "0.0.0.0", "--port", "5000", "--app-dir", "src", "--log-config", "conf/uvicorn.logger.json", "mirror.main:app"]
