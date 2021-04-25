#!/bin/bash


find ../../Google\ Drive/data -name "*.epub" -type f -print0 | while read -d $'\0' path
do
  name=$(basename "${path}")
  newname="${name%.epub}.txt"
  newpath="${path/.epub/.txt}"
  if test ! -f "$newname"; then 
    echo "******"
    echo "Converting: ${path}"
    ebook-convert "${path}" "${newpath}"
  fi
done