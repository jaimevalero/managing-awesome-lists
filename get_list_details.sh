#! /bin/bash
# Order an awesome list by number stars.
#
# Tis one liner scripts extracts the number of stars from each repo from a given awesome list, and order repos by the number of start
# This one liner uses jq command, so you should have it installed in your machine

# Parameter
# Awesome List to extract, in raw

LOG_FILE=/var/log/`basename $0`.log
#######################################################
#
# Funcion MostrarLog
#
#
#######################################################
Log( )
{
#echo "[`basename $0`] [`date +'%Y_%m_%d %H:%M:%S'`] [$$] [${FUNCNAME[1]}] $@" | /usr/bin/tee -a $LOG_FILE
a=0
}


source ./.credentials
#CREDENTIALS="replace-for-your-github-user:replace-for-your-github-password"
RESULTS=3

Create_Info_Render( )
{
  URI=$1
  README_LIST_FILE=`echo ${URI}| tr \/ @  `
#Log URI=$URI= README_LIST_FILE=$README_LIST_FILE=
echo ' { "repos" : [ '
while read REPO
do
  MY_FILE=`echo $REPO | tr \/ @`
  cat .cache/api-$MY_FILE.json | jq -c .
  echo ","
done < .cache/readme-${README_LIST_FILE}.txt
echo "]"
echo ' , "list" : '
MY_AWESOME_LIST=`echo $URI | tr \/ @`
cat .cache/api-$MY_AWESOME_LIST.json | jq -c .
echo ' } '
}
Create_Info_Render_Wrapper( )
{
  URI=$1
  README_LIST_FILE=`echo ${URI}| tr \/ @  `
  Log URI=$URI= README_LIST_FILE=$README_LIST_FILE=
  Create_Info_Render $URI | tr '\n' ' '  | sed -e 's@, ]  ,@],@g'
}

Download_Api_Repo( )
{
URI="$1"
# Name of the file
OUTPUT_FILE=`echo $URI | tr \/ @  `
Log Download_Api_Repo $URI $OUTPUT_FILE

[[  ! -f ".cache/api-${OUTPUT_FILE}.json" ]]  && curl --user  "$CREDENTIALS" -s  -L -k "https://api.github.com/repos/$URI" > ./.cache/api-${OUTPUT_FILE}.json

}

Download_Readme( )
{
  Log Download_Readme ${URI} ...
  URI="$1"
  if [[ ! -f  .cache/readme-${OUTPUT_FILE}.txt ]]
  then
  OUTPUT_FILE=`echo $URI | tr \/ @  `

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
    sort -du  > .cache/readme-${OUTPUT_FILE}.txt
  fi
}
Generate_Single_List( )
{
  AWESOME_LIST_URL=$1
  URI=`echo "${AWESOME_LIST_URL}" | egrep -o -e 'github.com/.*' | cut -d\/ -f2-3`
  Download_Api_Repo "$URI"
  Log URI=$URI

  Log Parsing ${URI} ...

  # Get name of the list - typically readme.md in upper or lowercase
  Download_Readme ${URI}

   README_LIST_FILE=`echo ${URI}| tr \/ @  `
   while read REPO
   do
     Download_Api_Repo $REPO
   done < .cache/readme-${README_LIST_FILE}.txt


}

NON_WORKING="
https://github.com/ossu/computer-science
https://github.com/MunGell/awesome-for-beginners
"
AWESOME_LIST_LISTS="
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
"
#AWESOME_LIST_LISTS="
#https://github.com/heynickc/awesome-ddd
#"


for AWESOME_LIST_URL in ` echo "${AWESOME_LIST_LISTS}"`
do
  Generate_Single_List ${AWESOME_LIST_URL}
done
#Create_Info_Render_Wrapper heynickc@awesome-ddd > /tmp/lista.json

#./generate_render_template.py  --template template-list.j2 --data /tmp/lista.json
