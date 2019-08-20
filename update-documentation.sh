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
INDEX_JSON_DATA=/tmp/kk-index.json

README_PARTIAL_DOC=/tmp/kk-readme.md
INDEX_PARTIAL_DOC=/tmp/kk-index.html

Generate_Index_Json_Data( )
{
  RESULTS=10000

  > $INDEX_JSON_DATA.2
  echo "Generando el json para el index"
  for i in ` find .cache/ -name 'api-*' | head -${RESULTS}`
  do
    [ ! -s $i ]  && echo $i no exite && continue
    [ ` grep "Malformed request" $i | wc -l ` -eq 1 ]  && echo borrando "$i" && rm -f "$i"   && continue
    cat "$i" | jq -c  "
 {
   full_name,
   description,
   topics,
   created_at,
   pushed_at,
   stargazers_count,
   language
    }"   >> ${INDEX_JSON_DATA}.2
  done
  grep full_name  ${INDEX_JSON_DATA}.2 | wc -l

  cat ${INDEX_JSON_DATA}.2  | jq -c .  |   jq   --slurp '.'  | jq -c .  | sed -e 's@^@ { "list" :  { "full_name" : "This list contains every mentioned repo in every awesome list" , "description" : "This list contains all the repos mentioned on all the awesome list."} ,  "repos" :  @g'  | sed -e 's@$@ }@g'     > ${INDEX_JSON_DATA}


  rm -f  ${INDEX_JSON_DATA}.2
  echo "Generado json  ${INDEX_JSON_DATA} con:" `cat  ${INDEX_JSON_DATA} | grep --colour  repos | jq ".repos|length"` repos

  ./generate_render_template.py  -t template-index.html --data ${INDEX_JSON_DATA} > index.html

}


Generate_Readme_Json_Data_Inner( )
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
Generate_Index( )
{
  ./generate_render_template.py  -t template-index.html --data ${INDEX_JSON_DATA}
}
Generate_Partial_Doc( )
{
  ./generate_render_template.py  -t template-readme.html --data ${README_JSON_DATA}
}
Generate_Readme_Json_Data( )
{
  Generate_Readme_Json_Data_Inner| tr '\n' ' ' | sed -e  's@, ]@]@g'
}

Document_Index( )
{

  INDEX_FILE=index.html
  cat $INDEX_PARTIAL_DOC > $INDEX_FILE

}

Document_Readme( )
{

  README_FILE=README.md
  cat $README_PARTIAL_DOC > $README_FILE

}

Main( )
{

  source ./.credentials
  # First   : Generate json data
  # Then    : Generate partial doc
  # Finally : Write results to repo file
  Generate_Readme_Json_Data > ${README_JSON_DATA}
  Generate_Partial_Doc      > ${README_PARTIAL_DOC}
  Document_Readme

  Generate_Index_Json_Data
}

Main
#git add . ; git commit -m "Templatin'" ;  git push origin master
