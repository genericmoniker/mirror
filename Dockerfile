# Best practice: Choose a stable base image and tag.
FROM python:3.8-slim-buster AS build-image

# Best practice: Make sure apt-get doesn't run in interactive mode.
RUN export DEBIAN_FRONTEND=noninteractive && \
  apt-get update && \
  apt-get install -y --no-install-recommends curl build-essential python-dev libffi-dev libssl-dev

# NodeSource repostiory and nodejs
# Best practice: Make sure apt-get doesn't run in interactive mode.
RUN curl -sL https://deb.nodesource.com/setup_15.x | bash -
RUN export DEBIAN_FRONTEND=noninteractive && \
  apt-get install -y --no-install-recommends nodejs

# Install poetry.
ENV POETRY_HOME=/opt/poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python - --no-modify-path
ENV PATH=$POETRY_HOME/bin:$PATH

WORKDIR /build

# Install dependencies.
#
# Best practices:
# * `COPY` in files only when needed.

# Backend dependencies
COPY pyproject.toml poetry.lock poetry.toml ./
RUN poetry install --no-root

# Frontend dependencies
COPY frontend/package.json frontend/package-lock.json ./frontend/
WORKDIR /build/frontend
RUN npm install

# Copy in the code.
WORKDIR /build
COPY . .

# Backend "PEP 517" build (to copy a wheel to the virtual environment)
RUN pip install .

# Frontend build
WORKDIR /build/frontend
RUN npm run build

# ============================================================================

FROM python:3.8-slim-buster AS run-image

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

# Copy backend virtualenv (location is /build/.venv because of:
# - WORKDIR in the build phase
# - `in-project = true` in poetry.toml
# Best practices: Avoid extra chowns.
COPY --from=build-image --chown=appuser /build/.venv ./.venv
ENV PATH="/home/appuser/.venv/bin:$PATH"

# Copy frontend.
COPY --from=build-image --chown=appuser /build/frontend/public ./frontend/public

# Best practices: Prepare for C crashes.
ENV PYTHONFAULTHANDLER=1

# Run the code when the image is run:
#
# Best practices:
# * Add an `init` process
# * Make sure images shut down correctly (via ENTRYPOINT [] syntax).
ENTRYPOINT ["tini", "--", "mirror"]
