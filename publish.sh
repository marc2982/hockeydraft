#! /usr/bin/env bash

year=$1

test -n "$(git status --untracked-files=no --porcelain)" && \
    echo "repo dirty dummy" && \
    exit 1

msg=$(git show -s --format=%B HEAD)

pushd ~/localgit/marc2982.github.io

cp ~/localgit/hockeydraft/$year/index.html playoffs/$year.html

sed -i -E 's;\.\./css;css;g' playoffs/$year.html

git --no-pager diff && \
    git add playoffs/$year.html playoffs/index.html && \
    git commit -m "$msg" && \
    git push

popd
