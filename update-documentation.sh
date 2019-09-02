#! /bin/bash

# Generate doc for the readme.md file


REPOS_WITH_LABELS_FILE=/tmp/labels.json

README_PARTIAL_DOC=/tmp/kk-readme.md
INDEX_PARTIAL_DOC=/tmp/kk-index.html
export INDEX_JSON_DATA=/tmp/kk-index.json
export README_JSON_DATA=/tmp/kk-readme.json

source ./lib-actions.sh

Render_Index( )
{
  RESULTS=50000000

  > $INDEX_JSON_DATA.2
  echo "Generando el json para el index"
  for i in ` find .cache/ -name 'api-*' | head -${RESULTS}`
  do
    [ ! -s $i ]  && echo $i no existe && continue
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

  cat ${INDEX_JSON_DATA}.2  | jq -c .  |   jq   --slurp '.'  | jq -c .  | sed -e 's@^@ { "list" :  { "full_name" : "This list contains every mentioned repo in every awesome list." , "description" : "This list contains all the repos mentioned on all the awesome list."} ,  "repos" :  @g'  | sed -e 's@$@ }@g'     > ${INDEX_JSON_DATA}


  rm -f  ${INDEX_JSON_DATA}.2
  echo "Generado json  ${INDEX_JSON_DATA} con:" `cat  ${INDEX_JSON_DATA} | grep --colour  repos | jq ".repos|length"` repos

  ./generate_render_template.py  -t template-index.html --data ${INDEX_JSON_DATA} > index.html

}

Generate_Readme_Json_Data_Inner( )
{
  Log Empezando
  LIST_FILELIST=`find .cache/ | grep readme- | grep -v  'cache/raw' | sed -e 's@/readme-@/api-@g' -e 's@.txt$@.json@g'| sort -du `

  for LIST_FILE  in `echo ${LIST_FILELIST}`
  do
    SHORT_NAME=`cat ${LIST_FILE} | jq -c .full_name | cut -d\/ -f2 | cut -d\" -f1 |  sed -e 's@^awesome-@@g' `
    cat $LIST_FILE  | sed -e "s@{\"full_name\"@ { \"name\" : \"${SHORT_NAME}\" , \"full_name\" @g" > /tmp/kk-temp
    cat /tmp/kk-temp > $LIST_FILE
  done


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
  Log Empezando
  Generate_Readme_Json_Data_Inner| tr '\n' ' ' | sed -e  's@, ]@]@g'
}

Document_Index( )
{

  INDEX_FILE=index.html
  cat $INDEX_PARTIAL_DOC > $INDEX_FILE

}

Render_Readme( )
{

  README_FILE=README.md
  cat $README_PARTIAL_DOC > $README_FILE

}

Render_Navbar( )
{

  ./generate_render_template.py  -t template-navbar.html --data ${README_JSON_DATA} >  views/layout/navbar.html
  ls -altr  views/layout/navbar.html
}


Check_Repos_Are_Downloaded( )
{
  TOPIC_FILE="$1"
  while read my_topic_file ; do Download_Api_Repo "$my_topic_file" ; done < "${TOPIC_FILE}"
}

Main( )
{

  source ./.credentials
  # First   : Generate json data
  # Then    : Generate partial doc
  # Finally : Write results to repo file
  Generate_Readme_Json_Data > ${README_JSON_DATA}
  Generate_Partial_Doc      > ${README_PARTIAL_DOC}
  Render_Readme

  # Document navbar
  Render_Navbar
  Render_Index

  # Topics
  Render_Topics
}




Main
#git add . ; git commit -m "Templatin'" ;  git push origin master
