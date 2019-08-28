#! /bin/bash
LOG_FILE=/var/log/awesome.log
#######################################################
#
# Funcion MostrarLog
#
#
#######################################################

export INDEX_JSON_DATA=/tmp/kk-index.json
export README_JSON_DATA=/tmp/kk-readme.json
export AWESOME_LIST_LISTS=
AWESOME_LIST_LISTS=`cat lists.txt`

Log( )
{
  THIS_SCRIPT=`basename "$0"`
  ALL_ARGUMENTS="$*"
  echo "[${THIS_SCRIPT}] [`date +'%Y_%m_%d %H:%M:%S'`] [$$] [${FUNCNAME[1]}] ${ALL_ARGUMENTS}" >>  $LOG_FILE
}

source .credentials

Download_Api_Repo( )
{
  URI="$1"
  # Name of the file
  OUTPUT_FILE=`echo "$URI" | tr \/ @  `
  API_REPO_JSON_FILE=".cache/api-${OUTPUT_FILE}.json"
  #Log Download_Api_Repo $URI $OUTPUT_FILE ${API_REPO_JSON_FILE}


  cat $KK | grep $AA | wc -l < /dev/null

  [[  ! -f ".cache/api-${OUTPUT_FILE}.json" ]]  && curl --user  "$CREDENTIALS"  -H "Accept: application/vnd.github.mercy-preview+json"  -s  -L -k "https://api.github.com/repos/$URI" | jq -c  "
{
 full_name,
 description,
 topics,
 created_at,
 pushed_at,
 stargazers_count,
 language
}"  > "${API_REPO_JSON_FILE}"
  [ ` cat "${API_REPO_JSON_FILE}" | jq .  | grep -c null  ` -ge 5 ]   && Log "WARNING repo $URI vacio" && rm -f "${API_REPO_JSON_FILE}"
  [ -s "${API_REPO_JSON_FILE}" ] ||  Log "WARNING repo $URI vacio"
  [ -s "${API_REPO_JSON_FILE}" ] ||  rm -f "${API_REPO_JSON_FILE}"
  #[ `grep "Not Found" "./.cache/api-${OUTPUT_FILE}.json"  | wc -l ` -ge 1 ] && Log "WARNING repo $URI vacio" && rm -f ./.cache/api-${OUTPUT_FILE}.json
  [ -f "${API_REPO_JSON_FILE}" ]  && ls -altr "${API_REPO_JSON_FILE}"
}


Generate_Topic_Json( )
{
  TOPIC_FILE="$1"
  TOPIC_NAME=`basename "$TOPIC_FILE"`
  Log TOPIC_NAME=$TOPIC_NAME= TOPIC_FILE=$TOPIC_FILE=
  # Check every repo is in cache
  Check_Repos_Are_Downloaded "${TOPIC_FILE}" 1>/dev/null 2>/dev/null

  echo " { \"list\" : \"${TOPIC_NAME}\"  , \"repos\" :  "
  cat "${TOPIC_FILE}" | tr \/ \@ | sed -e 's@^@.cache/api-@g' -e 's@$@.json@g' | xargs cat | jq -c  "
   {
     full_name,
     description,
     topics,
     created_at,
     stargazers_count,
     language
      }"  | jq  --slurp .
  echo " } "

}

Render_Topics( )
{
  cat $INDEX_JSON_DATA | jq -c ".repos[]|{ full_name , topics}" | grep -v '"topics":\[\]'  > ${REPOS_WITH_LABELS_FILE}

  # Label in more than one repo
  DEBUG=100000

  TOPICS_LIST=` cat $INDEX_JSON_DATA | jq ".repos[]|.topics"   | grep \" | cut -d\" -f2 | sort  | uniq -c | sort -k1 -n  -r | grep -v "   1 "  |  awk '{print $2}' | sort -du | head -$DEBUG `

  mkdir var/topics/     2>/dev/null
  mkdir .cache/topics/  2>/dev/null

  for topic in ${TOPICS_LIST}
  do
    Log "Topic: $topic"
    TOPIC_FILE=".cache/topics/$topic"
    THIS_TOPIC_JSON_DATA="/tmp/topic-${topic}.json"
    # We only generate intermediate data if dont exists
    if [ ! -s "${TOPIC_FILE}"      ]; then  grep "\"$topic\"" ${REPOS_WITH_LABELS_FILE} | jq -r .full_name > "${TOPIC_FILE}"    ; fi
    Generate_Topic_Json "${TOPIC_FILE}"   > "${THIS_TOPIC_JSON_DATA}"
    cat "${THIS_TOPIC_JSON_DATA}" | jq . 1>/dev/null 2>/dev/null
    RESUL=$?
    [ $RESUL -ne 0 ] && Log "Error $topic no tiene json correcto de datos en ${THIS_TOPIC_JSON_DATA}"
    Render_Topic "$THIS_TOPIC_JSON_DATA"
  done


}


Render_Topic( )
{

  THIS_TOPIC_JSON_DATA="$1"
  TOPIC=`cat "$THIS_TOPIC_JSON_DATA" | jq -r .list  | cut -d\/ -f3-100`
  Log "THIS_TOPIC_JSON_DATA=$THIS_TOPIC_JSON_DATA="
  Log "./generate_render_template.py  -t template-topic.html --data '${THIS_TOPIC_JSON_DATA}' > 'var/topics/$TOPIC.html' "
  ./generate_render_template.py  -t template-topic.html --data "${THIS_TOPIC_JSON_DATA}" > "var/topics/$TOPIC.html"
  ls -altr "var/topics/$TOPIC.html"
}
