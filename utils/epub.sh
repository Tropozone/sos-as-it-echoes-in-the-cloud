#!/bin/bash

find . -name "*.epub" -type f -print0 | while read -d $'\0' path
do
  name=$(basename "${path}")
  newname="${name%.epub}.txt"

  echo "******"
  echo "Converting: ${path}"
  ebook-convert "${path}" "txt/${newname}"
done