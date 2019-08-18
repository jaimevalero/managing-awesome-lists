#! /bin/bash
# Order an awesome list by number stars.
#
# Tis one liner scripts extracts the number of stars from each repo from a given awesome list, and order repos by the number of start
# This one liner uses jq command, so you should have it installed in your machine

# Parameter
# Awesome List to extract, in raw

LOG_FILE=/var/log/awesome.log
#######################################################
#
# Funcion MostrarLog
#
#
#######################################################
Log( )
{
echo "[`basename $0`] [`date +'%Y_%m_%d %H:%M:%S'`] [$$] [${FUNCNAME[1]}] $@" >>  $LOG_FILE
}
RESULTS=5000

source ./.credentials
#CREDENTIALS="replace-for-your-github-user:replace-for-your-github-password"



Create_Info_Render( )
{
  URI="$1"

  OUTPUT_FILE=`echo $URI | tr \/ @  `
  CACHE_README_FILE=".cache/readme-${OUTPUT_FILE}.txt"

 Log "URI=$URI= CACHE_README_FILE=$CACHE_README_FILE="
echo ' { "repos" : [ '
while read REPO
do
  MY_FILE=`echo $REPO | tr \/ @`
  [ ` grep '"message": "Not Found",' .cache/api-$MY_FILE.json | wc -l ` -ge 1 ] && Log "Warning : Repo Vacio $REPO" && continue

  cat .cache/api-$MY_FILE.json | jq -c .
  echo ","
done < ${CACHE_README_FILE}
echo "]"
echo ' , "list" : '
MY_AWESOME_LIST=`echo $URI | tr \/ @`
cat .cache/api-$MY_AWESOME_LIST.json | jq -c .
echo ' } '
}
Create_Info_Render_Wrapper( )
{
  URI="$1"
  Log URI=$URI=
  Create_Info_Render "$URI" | tr '\n' ' '  | sed -e 's@, ]  ,@],@g'
}

Download_Api_Repo( )
{
URI="$1"
# Name of the file
OUTPUT_FILE=`echo $URI | tr \/ @  `
#Log Download_Api_Repo $URI $OUTPUT_FILE

[[  ! -f ".cache/api-${OUTPUT_FILE}.json" ]]  && curl --user  "$CREDENTIALS"  -H "Accept: application/vnd.github.mercy-preview+json"  -s  -L -k "https://api.github.com/repos/$URI" > ./.cache/api-${OUTPUT_FILE}.json

}

Download_Readme( )
{
  URI="$1"
  OUTPUT_FILE=`echo $URI | tr \/ @  `
  CACHE_README_FILE=.cache/readme-${OUTPUT_FILE}.txt

  Log URI=${URI}=
  Log OUTPUT_FILE=${OUTPUT_FILE}=
  Log CACHE_README_FILE=${CACHE_README_FILE}=

  if [[ ! -f ${CACHE_README_FILE} ]]
  then

  README_NAME=`curl -L --user  "$CREDENTIALS" -s "https:/github.com/${URI}" | grep --colour -o -i /readme.md | head -1 | cut -d\/ -f2  `
  Log Download_Readme ${README_NAME} ...

  curl -L --user  "$CREDENTIALS" -s "https://raw.githubusercontent.com/${URI}/master/${README_NAME}" | \
    egrep -E  -o  'https://github.com/.*/.*'      | \
    tr \" \  | \
    sed -e 's@[>#"\) ]?@ @g' | \
    tr '\#' ' '      |   \
    awk '{print $1}' |   \
    cut -d\/ -f 4-5  |   \
    tr -d '\)'       |   \
    tr -d ':'        |   \
    head -${RESULTS} |   \
    sort -du  > ${CACHE_README_FILE}
  fi
  Log ` ls -latr ${CACHE_README_FILE} `
}

Generate_Contents_Single_List( )
{
  AWESOME_LIST_URL=$1
  URI=`echo "${AWESOME_LIST_URL}" | egrep -o -e 'github.com/.*' | cut -d\/ -f2-3`
  Download_Api_Repo "$URI"
  Log URI=$URI

  Log Parsing ${URI} ...

  # Get name of the list - typically readme.md in upper or lowercase
  Download_Readme ${URI}

   OUTPUT_FILE=`echo $URI | tr \/ @  `
   CACHE_README_FILE=.cache/readme-${OUTPUT_FILE}.txt
   while read REPO
   do
     Download_Api_Repo $REPO
   done < ${CACHE_README_FILE}


}

Generate_Render_Readme( )
{
Update_Readme_Doc > /tmp/readme.json
./generate_render_template.py  -t template-readme.html --data /tmp/readme.json >> README.md

}
Generate_Render_Single_List( )
{
AWESOME_LIST_URL="$1"
MY_URI=`echo "${AWESOME_LIST_URL}" | egrep -o -e 'github.com/.*' | cut -d\/ -f2-3`
FILE_HTML=`echo ${MY_URI} | tr \/ @  `
Log AWESOME_LIST_URL=$AWESOME_LIST_URL= FILE_HTML=$FILE_HTML=

Generate_Contents_Single_List ${AWESOME_LIST_URL}
Create_Info_Render_Wrapper "${MY_URI}" > /tmp/lista.json

 if [ `cat /tmp/lista.json | grep ' "repos" : \[  \]' | wc -l ` -eq 1 ]
 then
  Log  ERRROR . Repos Vacios ${URI}
else
 ./generate_render_template.py  -t template-list.html --data /tmp/lista.json > var/awl-$FILE_HTML.html
fi
}
NON_WORKING="
https://github.com/ossu/computer-science
https://github.com/MunGell/awesome-for-beginners
"
AWESOME_LIST_LISTS="
https://github.com/k4m4/terminals-are-sexy
https://github.com/trimstray/the-book-of-secret-knowledge
https://github.com/josephmisiti/awesome-machine-learning
https://github.com/vinta/awesome-python
https://github.com/avelino/awesome-go
https://github.com/sindresorhus/awesome
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
https://github.com/n1trux/awesome-sysadmin
https://github.com/fasouto/awesome-dataviz
https://github.com/enaqx/awesome-react
https://github.com/jaywcjlove/awesome-mac
https://github.com/ripienaar/free-for-dev
https://github.com/ziadoz/awesome-php
https://github.com/akullpp/awesome-java
https://github.com/sorrycc/awesome-javascript
https://github.com/viatsko/awesome-vscode
https://github.com/unixorn/awesome-zsh-plugins
"
#AWESOME_LIST_LISTS="
#https://github.com/heynickc/awesome-ddd
#"

Log Inicio
for AWESOME_LIST_URL in ` echo "${AWESOME_LIST_LISTS}"`
do
  Generate_Render_Single_List ${AWESOME_LIST_URL}
done


Log Fin
./update-documentation.sh
