#! /bin/bash

# Generate doc for the readme.md file

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
README_JSON_DATA=/tmp/kk-readme.json
README_PARTIAL_DOC=/tmp/kk-readme.md



Generate_Data_Readme_Doc( )
{
  LIST_FILELIST=`find .cache/ | grep readme- | sed -e 's@/readme-@/api-@g' -e 's@.txt$@.json@g'| sort -du `

  echo ' { "repos" : [ '
  for LIST_FILE  in `echo ${LIST_FILELIST}`
  do
    cat ${LIST_FILE} | jq -c .
    echo ","
  done
  echo "]"
  echo " } "

}
Generate_Partial_Doc( )
{
  ./generate_render_template.py  -t template-readme.html --data ${README_JSON_DATA}
}
Generate_Json_Data( )
{
  Generate_Data_Readme_Doc| tr '\n' ' ' | sed -e  's@, ]@]@g'
}

Document_Readme( )
{

    README_FILE=README.md
    cat $README_PARTIAL_DOC > $README_FILE

}

Main( )
{

  source ./.credentials
  # Generate json data
  Generate_Json_Data > ${README_JSON_DATA}

  # Generate partial doc
  Generate_Partial_Doc > ${README_PARTIAL_DOC}

  # Update doc
  Document_Readme

}

Main
git add . ; git commit -m "Templatin'" ;  git push origin master
