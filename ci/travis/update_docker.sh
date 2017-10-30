#!/usr/bin/env bash

set -e

target=/tmp/memote-docker

git clone "https://github.com/opencobra/memote-docker.git" "${target}"
cd "${target}"

git config user.name "Deployment Bot"
git config user.email "deploy@travis-ci.org"
git remote rm origin
git remote add origin "https://user:${GITHUB_TOKEN}@github.com/opencobra/memote-docker.git" &> /dev/null

git checkout master
pip install pipenv
rm -f Pipfile.lock
pipenv install memote==${TRAVIS_TAG}
git add .
git commit -m "feat: publish ${TRAVIS_TAG} on $(date +'%F %T')"
git push origin master
git tag "${TRAVIS_TAG}"
git push origin "${TRAVIS_TAG}"
cd "${TRAVIS_BUILD_DIR}"

