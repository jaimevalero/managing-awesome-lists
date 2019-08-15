# Order an awesome list by number stars.
#
# Tis one liner scripts extracts the number of stars from each repo from a given awesome list, and order repos by the number of start
# This one liner uses jq command, so you should have it installed in your machine

# Parameter
# Awesome List to extract, in raw
AWESOME_LIST=https://raw.githubusercontent.com/pditommaso/awesome-pipeline/master/README.md
source ./.credentials
#CREDENTIALS="jaimevalero:mysecret"
#CREDENTIALS="replace-for-your-github-user:replace-for-your-github-password"

curl -L --user  "$CREDENTIALS" -s "$AWESOME_LIST" | \
  egrep -E  -o  'https://github.com/.*/.*)'      | \
  cut -d\/ -f 4-5 | cut -d\) -f1 | \
  while read line ; do \
    echo "[$line](https://github.com/$line)" \|  \
    `curl --user  "$CREDENTIALS" -s  -L -k "https://api.github.com/repos/$line" | \
    jq -c '[ .stargazers_count  ,"º" ,  .description , "º"] ' | \
    tr -d '\[' | tr -d '\]' | tr -d ',' | tr -d '\"' |  tr -d '\|' | tr 'º' '|' `; \
  done |  sort -r -u -t \| -k2 -n | sed -e 's/^/\|/g'
