#! /usr/bin/env bash

test -n "$(git status --untracked-files=no --porcelain)" && \
    echo "repo dirty dummy" && \
    exit 1

msg=$(git show -s --format=%B HEAD)

pushd ~/localgit/marc2982.github.io

cp ~/localgit/hockeydraft/2024/index.html playoffs/2024.html

sed -i -E 's;\.\./css;css;g' playoffs/2024.html

git --no-pager diff && \
    git add playoffs/2024.html && \
    git commit -m "$msg" && \
    git push

popd
