# This Dockerfile implements the following best practices from the "Python on
# Docker Production Quickstart"
# (https://pythonspeed.com/products/productionquickstart/)
#
# * Choose a stable base image and tag.
# * Make sure `apt-get` doesn't run in interactive mode.
# * Update system packages.
# * Don't run as root.
# * Prepare for C crashes.
# * Pre-install some useful tools.
# * Make sure your image shuts down correctly.
# * Add an `init` process.
# * `COPY` in files only when needed.
# * Avoid extra chowns.
# * Minimize system package installation.
# * Reduce disk usage from `pip` installs.
#
# There are many other best practices you may wish to implement; see the
# Quickstart for details.

# Best practice: Choose a stable base image and tag.
FROM python:3.8-slim-buster

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
  apt-get install -y --no-install-recommends curl tini procps net-tools build-essential python-dev libffi-dev libssl-dev && \
  apt-get -y clean && \
  rm -rf /var/lib/apt/lists/*

# NodeSource repostiory and nodejs
RUN curl -sL https://deb.nodesource.com/setup_15.x | bash -
RUN export DEBIAN_FRONTEND=noninteractive && \
  apt-get install -y --no-install-recommends nodejs

# Create a new user to run as.
#
# Best practices: Don't run as root.
RUN useradd --create-home appuser
USER appuser
WORKDIR /home/appuser

# Install poetry.
ENV POETRY_HOME=/home/appuser/poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python - --no-modify-path
ENV PATH=$POETRY_HOME/bin:$PATH

# Install dependencies.
#
# Best practices:
# * `COPY` in files only when needed.
# * Reduce disk usage from `pip` installs.
COPY pyproject.toml poetry.lock poetry.toml ./

# Backend dependencies
RUN poetry install --no-root

# Frontend dependencies
WORKDIR /home/appuser/frontend
RUN npm install

# Copy in the code.
#
# Best practices: Avoid extra chowns.
WORKDIR /home/appuser
COPY --chown=appuser . .

# Backend build
RUN poetry install

# Frontend build
WORKDIR /home/appuser/frontend
RUN npm run build

# Best practices: Prepare for C crashes.
ENV PYTHONFAULTHANDLER=1

# Run the code when the image is run:
#
# Best practices:
# * Add an `init` process
# * Make sure images shut down correctly (via ENTRYPOINT [] syntax).
ENTRYPOINT ["tini", "--", "poetry", "run", "mirror"]
