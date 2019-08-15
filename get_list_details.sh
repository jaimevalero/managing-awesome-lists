#! /bin/bash
# Order an awesome list by number stars.
#
# Tis one liner scripts extracts the number of stars from each repo from a given awesome list, and order repos by the number of start
# This one liner uses jq command, so you should have it installed in your machine

# Parameter
# Awesome List to extract, in raw
#AWESOME_LIST=https://raw.githubusercontent.com/pditommaso/awesome-pipeline/master/README.md
source ./.credentials
#CREDENTIALS="replace-for-your-github-user:replace-for-your-github-password"

AWESOME_LIST_URL=${1:https://github.com/trimstray/the-book-of-secret-knowledge}
OUTPUT_FILE=$2

URI=`echo "${AWESOME_LIST_URL}" | egrep -o -e 'github.com/.*' | cut -d\/ -f2-3`

echo '| Link  | Stars | Description'                      > $OUTPUT_FILE
echo '| ------------- | ------------- | ------------- |' >> $OUTPUT_FILE
curl -L --user  "$CREDENTIALS" -s "https://raw.githubusercontent.com/${URI}/master/README.md" | \
  egrep -E  -o  'https://github.com/.*/.*'      | \
  tr \" \  | \
  sed -e 's@[>#"\) ]?@ @g' | \
  tr '\#' ' ' | \
  awk '{print $1}' | \
  cut -d\/ -f 4-5  | head | \
  while read line ; do \
    echo "[$line](https://github.com/$line)" \|  \
    `curl --user  "$CREDENTIALS" -s  -L -k "https://api.github.com/repos/$line" |  \
    jq -c '[ .stargazers_count  ,"º" ,  .description , "º"] ' | \
    tr -d '\[' | tr -d '\]' | tr -d ',' | tr -d '\"' |  tr -d '\|' | tr 'º' '|' `; \
  done |  sort -r -u -t \| -k2 -n | sed -e 's/^/\|/g' >> $OUTPUT_FILE


