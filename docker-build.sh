#!/bin/bash

# Multi-platform Docker image build.

set -euo pipefail

IMAGE_NAME="genericmoniker/mirror"
CACHE_IMAGE_NAME="genericmoniker/mirror-cache"

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
CACHE_IMAGE_WITH_BRANCH="${CACHE_IMAGE_NAME}:${GIT_BRANCH}"

# Build the image, giving it two names.
#
# Best practices:
# * Warm up the build cache, per-branch.
# * Don't rely on the `latest` tag.
# * Record the build's version control revision and branch.
#
# Multiplatform build:
# * linux/arm/v7 to run on Raspberry Pi 2
# * linux/arm64 could be added for new Pis
# * linux/amd64 could be added to run on desktop
docker buildx build \
       -t "${IMAGE_WITH_COMMIT}" \
       -t "${IMAGE_WITH_BRANCH}" \
       --label "git-commit=${GIT_COMMIT}" \
       --label "git-branch=${GIT_BRANCH}" \
       --platform linux/arm/v7 \
       --progress plain \
       --push \
       --cache-from=type=registry,ref="${CACHE_IMAGE_WITH_BRANCH}" \
       --cache-to=type=registry,ref="${CACHE_IMAGE_WITH_BRANCH}",mode=max \
       .
