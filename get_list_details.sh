#!/bin/bash
# Order an awesome list by number stars.
#
# This scripts extracts the number of stars from each repo from a given awesome list, and order repos by the number of start
# uses jq command, so you should have it installed in your machine


source ./.credentials

# In the credentials file :
#CREDENTIALS="replace-for-your-github-user:replace-for-your-github-password"

source ./lib-actions.sh
Log "Inicio get_list_details"

Create_Info_Render( )
{
  URI="$1"

  OUTPUT_FILE=`echo $URI | tr \/ @  `
  CACHE_README_FILE=".cache/readme-${OUTPUT_FILE}.txt"

  Log "URI=$URI= CACHE_README_FILE=$CACHE_README_FILE=  OUTPUT_FILE=$OUTPUT_FILE="

echo ' { '
  echo '  "list" : '
  MY_AWESOME_LIST=`echo $URI | tr \/ @`
  cat .cache/api-${MY_AWESOME_LIST}.json | jq -c .

echo '  , "repos" : '
cat  ${CACHE_README_FILE} | tr \/ @ |  sed -e 's@^@.cache/api-@g'  -e 's@$@.json@g' | xargs cat  |  grep -v '"message": "Not Found",' | grep  [0-9] | jq --slurp . 2>/dev/null
echo ' } '

  #echo " {  \"list\" :  \"repos\" :
  #while read REPO
  #do
  #  MY_FILE=`echo $REPO | tr \/ @`
  #  [ -f ".cache/api-$MY_FILE.json" ]  ||  echo "Warning : Repo Vacio $REPO" && continue
  #  [ ` grep '"message": "Not Found",' ".cache/api-$MY_FILE.json" | wc -l ` -ge 1 ] && echo "Warning : Repo Vacio $REPO" && continue

  #  cat .cache/api-$MY_FILE.json | jq -c .
  #  echo ","
  #done < ${CACHE_README_FILE}
  #echo "]"
  #echo ' , "list" : '
  #MY_AWESOME_LIST=`echo $URI | tr \/ @`
  #cat .cache/api-$MY_AWESOME_LIST.json | jq -c .
  #echo ' } '
}
Create_Info_Render_Wrapper( )
{
  URI="$1"
  Log URI=$URI=
  Create_Info_Render "$URI" | tr '\n' ' '  | sed -e 's@, ]  ,@],@g'
}


Download_Readme( )
{
  URI="$1"
  OUTPUT_FILE=`echo $URI | tr \/ @  `
  CACHE_README_FILE=.cache/readme-${OUTPUT_FILE}.txt
  RAW_CACHE_README_FILE=.cache/raw_readme-${OUTPUT_FILE}.txt
  Log URI=${URI}=   OUTPUT_FILE=${OUTPUT_FILE}=   CACHE_README_FILE=${CACHE_README_FILE}=
  RESULTS=5000

  if [[ ! -s ${CACHE_README_FILE} ]]
  then
    Refresh_Credentials  ;     echo $CREDENTIALS
    README_NAME=`curl -L --user  "$CREDENTIALS" -s "https:/github.com/${URI}" | grep --colour -o -i /readme.md | head -1 | cut -d\/ -f2  `

    if [[ ! -f ${RAW_CACHE_README_FILE} ]]
    then
      Log Download_Readme README_NAME=${README_NAME}= ...
      Refresh_Credentials  ;     echo $CREDENTIALS
      curl -L --user  "$CREDENTIALS" -s "https://raw.githubusercontent.com/${URI}/master/${README_NAME}" > ${RAW_CACHE_README_FILE}
    fi
    Log Raw readme $URI` ls -latr ${RAW_CACHE_README_FILE} `
    ls -latr ${RAW_CACHE_README_FILE}


    cat ${RAW_CACHE_README_FILE} | \
      egrep -E  -o  'https://github.com/.*/.*'      | \
      tr \" \  | \
      sed -e 's@[>#"\) ]?@ @g' | \
      tr '\#' ' '      |   \
      awk '{print $1}' |   \
      cut -d\/ -f 4-5  |   \
      tr -d '\)'       |   \
      tr -d ':'        |   \
      tr -d ','        |   \
      head -${RESULTS} |   \
      sort -du  > ${CACHE_README_FILE}
  fi
  ls -latr ${CACHE_README_FILE}
  Log ` ls -latr ${CACHE_README_FILE} `
}

Generate_Contents_Single_List( )
{
  AWESOME_LIST_URL=$1
  URI=`echo "${AWESOME_LIST_URL}" | egrep -o -e 'github.com/.*' | cut -d\/ -f2-3`
  Log URI=$URI

  Download_Api_Repo "$URI"

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
  echo "./generate_render_template.py  -t template-readme.html --data /tmp/readme.json"
  ./generate_render_template.py  -t template-readme.html --data /tmp/readme.json >> README.md

}

Generate_Render_Single_List( )
{
  AWESOME_LIST_URL="$1"
  MY_URI=`echo "${AWESOME_LIST_URL}" | egrep -o -e 'github.com/.*' | cut -d\/ -f2-3`
  FILE_HTML=`echo ${MY_URI} | tr \/ @  `
  LISTA_JSON_DATA="/tmp/lista-${FILE_HTML}.json"
  Log Preparando lista AWESOME_LIST_URL=$AWESOME_LIST_URL= FILE_HTML=$FILE_HTML=

  Generate_Contents_Single_List ${AWESOME_LIST_URL}
  Create_Info_Render_Wrapper "${MY_URI}" > ${LISTA_JSON_DATA}

  if [ `cat ${LISTA_JSON_DATA} | grep ' "repos" : \[  \]' | wc -l ` -eq 1 ]
  then
    Log  ERRROR . Repos Vacios ${URI}
  else
     echo"  ./generate_render_template.py  -t template-list.html --data ${LISTA_JSON_DATA} "
    ./generate_render_template.py  -t template-list.html --data ${LISTA_JSON_DATA} > var/awl-$FILE_HTML.html
    ls -altr   var/awl-$FILE_HTML.html
  fi
}

NON_WORKING="
https://github.com/ossu/computer-science
https://github.com/MunGell/awesome-for-beginners
"



Main( )
{
source ./lib-actions.sh
Log "Iniciando"
mkdir .cache 2>/dev/null

for AWESOME_LIST_URL in ` echo "${AWESOME_LIST_LISTS}"`
do
  Generate_Render_Single_List ${AWESOME_LIST_URL}
done

Log Fin

}

Main
#./update-documentation.sh
