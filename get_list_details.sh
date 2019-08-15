#! /bin/bash
# Order an awesome list by number stars.
#
# Tis one liner scripts extracts the number of stars from each repo from a given awesome list, and order repos by the number of start
# This one liner uses jq command, so you should have it installed in your machine

# Parameter
# Awesome List to extract, in raw
source ./.credentials
#CREDENTIALS="replace-for-your-github-user:replace-for-your-github-password"
RESULTS=50000

Generate_Single_List( )
{
  AWESOME_LIST_URL=$1
  URI=`echo "${AWESOME_LIST_URL}" | egrep -o -e 'github.com/.*' | cut -d\/ -f2-3`
  echo Parsing ${URI} ...

  README_NAME=`curl -L --user  "$CREDENTIALS" -s "https:/github.com/${URI}" | grep --colour -o -i /readme.md | head -1 | cut -d\/ -f2  `
  # Name of the file
  OUTPUT_FILE=`echo $URI | tr \/ @  | sed -e 's@$@.md@'`

  echo '| Link  | Stars   | Description'                      > $OUTPUT_FILE
  echo '| ------------- | ------------- | ------------- |' >> $OUTPUT_FILE
  curl -L --user  "$CREDENTIALS" -s "https://raw.githubusercontent.com/${URI}/master/${README_NAME}" | \
    egrep -E  -o  'https://github.com/.*/.*'      | \
    tr \" \  | \
    sed -e 's@[>#"\) ]?@ @g' | \
    tr '\#' ' '      |   \
    awk '{print $1}' |   \
    cut -d\/ -f 4-5  |   \
    tr -d '\)'       |   \
    tr -d ':'        |   \
    sort -du         |   \
    grep -v ${URI}   |   \
    head -${RESULTS} |   \
    while read line ; do \
      echo "[$line](https://github.com/$line)" \|  \
      `curl --user  "$CREDENTIALS" -s  -L -k "https://api.github.com/repos/$line" |  \
      jq -c '[ .stargazers_count  ,"º" ,  .description , "º"] ' | \
      tr -d '\[' | tr -d '\]' | tr -d ',' | tr -d '\"'  |  tr -d '\|' | tr 'º' '|' `; \
    done |  sort -r -u -t \| -k2 -n | sed -e 's/^/\|/g' | sed -e 's@) | @) | :star: @g' >> $OUTPUT_FILE

}

AWESOME_LIST_LISTS="
https://github.com/trimstray/the-book-of-secret-knowledge
https://github.com/josephmisiti/awesome-machine-learning
https://github.com/vinta/awesome-python
"
AWESOME_LIST_LISTS="
https://github.com/avelino/awesome-go
"
a="
https://github.com/sindresorhus/awesome
https://github.com/ossu/computer-science
https://github.com/Kickball/awesome-selfhosted
https://github.com/sindresorhus/awesome-nodejs
https://github.com/prakhar1989/awesome-courses
https://github.com/tiimgreen/github-cheat-sheet
https://github.com/dypsilon/frontend-dev-bookmarks
https://github.com/binhnguyennus/awesome-scalability
https://github.com/serhii-londar/open-source-mac-os-apps
https://github.com/alebcay/awesome-shell
https://github.com/veggiemonk/awesome-docker
https://github.com/lukasz-madon/awesome-remote-job
https://github.com/ChristosChristofidis/awesome-deep-learning
https://github.com/30-seconds/30-seconds-of-css
https://github.com/MunGell/awesome-for-beginners
https://github.com/phanan/htaccess
https://github.com/academic/awesome-datascience
https://github.com/onurakpolat/awesome-bigdata
https://github.com/bharathgs/Awesome-pytorch-list
https://github.com/davidsonfellipe/awesome-wpo
https://github.com/thibmaek/awesome-raspberry-pi
https://github.com/rshipp/awesome-malware-analysis
https://github.com/agarrharr/awesome-cli-apps
https://github.com/heynickc/awesome-ddd
https://github.com/AllThingsSmitty/jquery-tips-everyone-should-know
https://github.com/sdras/awesome-actions
"
for AWESOME_LIST_URL in ` echo "${AWESOME_LIST_LISTS}"`
do
  Generate_Single_List ${AWESOME_LIST_URL}
done
