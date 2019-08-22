#! /bin/bash

# Generate doc for the readme.md file


README_JSON_DATA=/tmp/kk-readme.json
INDEX_JSON_DATA=/tmp/kk-index.json
TOPIC_JSON_DATA=/tmp/kk-topic.json
REPOS_WITH_LABELS_FILE=/tmp/labels.json

README_PARTIAL_DOC=/tmp/kk-readme.md
INDEX_PARTIAL_DOC=/tmp/kk-index.html
source ./lib-actions.sh

Generate_Render_Index( )
{
  RESULTS=50000000

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

  cat ${INDEX_JSON_DATA}.2  | jq -c .  |   jq   --slurp '.'  | jq -c .  | sed -e 's@^@ { "list" :  { "full_name" : "This list contains every mentioned repo in every awesome list." , "description" : "This list contains all the repos mentioned on all the awesome list."} ,  "repos" :  @g'  | sed -e 's@$@ }@g'     > ${INDEX_JSON_DATA}


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

Document_Navbar( )
{
  ./generate_render_template.py  -t template-navbar.html --data ${README_JSON_DATA} >  views/layout/navbar.html
  ls -altr  views/layout/navbar.html
}

Document_Topics( )
{
  cat $INDEX_JSON_DATA | jq -c ".repos[]|{ full_name , topics}" | grep -v '"topics":\[\]'  > ${REPOS_WITH_LABELS_FILE}

  # Label in more than one repo
  TOPICS_LIST=` cat $INDEX_JSON_DATA | jq ".repos[]|.topics"   | grep \" | cut -d\" -f2 | sort  | uniq -c | sort -k1 -n  -r | grep -v "   1 "  |  awk '{print $2}'  | head`

  rm -rf var/topics/     ; mkdir var/topics/
  rm -rf .cache/topics/  ; mkdir .cache/topics/

  for topic in $TOPICS_LIST
  do
    Log "Topic: $topic"
    TOPIC_FILE=".cache/topics/$topic"
    grep "\"$topic\"" ${REPOS_WITH_LABELS_FILE} | jq -r .full_name >> "${TOPIC_FILE}"
    Generate_Topic_Json "${TOPIC_FILE}" > $TOPIC_JSON_DATA
    Generate_Render_Topic $TOPIC_JSON_DATA
  done


}


Generate_Topic_Json( )
{
  TOPIC_FILE="$1"
  TOPIC_NAME=`basename "$1"`
  Log TOPIC_NAME=$TOPIC_NAME= TOPIC_FILE=$TOPIC_FILE=
  # Check every repo is in cache
  while read my_topic_file ; do Download_Api_Repo "$my_topic_file" ; done < "${TOPIC_FILE}"

  echo " { \"list\" : \"${TOPIC_NAME}\"  , \"repos\" :  "
  cat "${TOPIC_FILE}" | tr \/ \@ | sed -e 's@^@.cache/api-@g' -e 's@$@.json@g' | xargs cat | jq -c  "
   {
     full_name,
     description,
     topics,
     created_at,
     pushed_at,
     stargazers_count,
     language
      }"  | jq  --slurp .
  echo " } "

}



Generate_Render_Topic( )
{
  TOPIC_JSON_DATA="$1"
  TOPIC=`cat $TOPIC_JSON_DATA | jq -r .list  | cut -d\/ -f3-100`
  ./generate_render_template.py  -t template-topic.html --data ${TOPIC_JSON_DATA} > "var/topics/$TOPIC.html"
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

  # Document navbar
  Document_Navbar
  Generate_Render_Index

  # Topics
  Document_Topics
}



source ./lib-actions.sh

#Main
#git add . ; git commit -m "Templatin'" ;  git push origin master
