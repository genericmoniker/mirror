#!/bin/bash

# Multi-platform Docker image build.

set -euo pipefail

IMAGE_NAME="genericmoniker/mirror"

# Get the Git commit and branch.
GIT_COMMIT=$(set -e && git rev-parse --short HEAD)
GIT_BRANCH=$(set -e && git rev-parse --abbrev-ref HEAD)

# Get the default Git branch; default to master if it can't figure it out.
GIT_DEFAULT_BRANCH=$(git rev-parse --abbrev-ref origin/HEAD || echo origin/master)
GIT_DEFAULT_BRANCH=$(basename "${GIT_DEFAULT_BRANCH}")

# Set two complete image names:
IMAGE_WITH_COMMIT="${IMAGE_NAME}:commit-${GIT_COMMIT}"
IMAGE_WITH_BRANCH="${IMAGE_NAME}:${GIT_BRANCH}"
IMAGE_WITH_DEFAULT_BRANCH="${IMAGE_NAME}:${GIT_DEFAULT_BRANCH}"
# Pull previous versions of the image, if any.
#
# Best practices:
# * Warm up the build cache, per-branch.
docker pull "${IMAGE_WITH_BRANCH}" || true
docker pull "${IMAGE_WITH_DEFAULT_BRANCH}" || true

# Build the image, giving it two names.
#
# Best practices:
# * Warm up the build cache, per-branch (not doing ATM).
# * Don't rely on the `latest` tag.
# * Record the build's version control revision and branch.
docker buildx build \
       -t "${IMAGE_WITH_COMMIT}" \
       -t "${IMAGE_WITH_BRANCH}" \
       --label "git-commit=${GIT_COMMIT}" \
       --label "git-branch=${GIT_BRANCH}" \
       --platform linux/amd64,linux/arm64,linux/arm/v7 \
       --push \
       .

       # --cache-from "${IMAGE_WITH_BRANCH}" \
       # --cache-from "${IMAGE_WITH_DEFAULT_BRANCH}" \
