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

source ./.credentials

Download_Api_Repo( )
{
  URI="$1"
  # Name of the file
  OUTPUT_FILE=`echo $URI | tr \/ @  `
  API_REPO_JSON_FILE=".cache/api-${OUTPUT_FILE}.json"
  Log Download_Api_Repo $URI $OUTPUT_FILE ${API_REPO_JSON_FILE}

  [[  ! -f ".cache/api-${OUTPUT_FILE}.json" ]]  && curl --user  "$CREDENTIALS"  -H "Accept: application/vnd.github.mercy-preview+json"  -s  -L -k "https://api.github.com/repos/$URI"  | jq -c  "
{
 full_name,
 description,
 topics,
 created_at,
 pushed_at,
 stargazers_count,
 language
}"  > "${API_REPO_JSON_FILE}"
  [ `cat "${API_REPO_JSON_FILE}" | jq .  | grep null | wc -l ` -ge 5 ]   && Log "WARNING repo $URI vacio" && rm -f "${API_REPO_JSON_FILE}"
  [ -s "${API_REPO_JSON_FILE}" ] ||  Log "WARNING repo $URI vacio"
  [ -s "${API_REPO_JSON_FILE}" ] ||  rm -f "${API_REPO_JSON_FILE}"
  #[ `grep "Not Found" "./.cache/api-${OUTPUT_FILE}.json"  | wc -l ` -ge 1 ] && Log "WARNING repo $URI vacio" && rm -f ./.cache/api-${OUTPUT_FILE}.json
  [ -f "${API_REPO_JSON_FILE}" ]  && ls -altr "${API_REPO_JSON_FILE}"
}
