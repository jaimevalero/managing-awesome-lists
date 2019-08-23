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
  #Log Download_Api_Repo $URI $OUTPUT_FILE

  [[  ! -f ".cache/api-${OUTPUT_FILE}.json" ]]  && curl --user  "$CREDENTIALS"  -H "Accept: application/vnd.github.mercy-preview+json"  -s  -L -k "https://api.github.com/repos/$URI"  | jq -c  "
{
 full_name,
 description,
 topics,
 created_at,
 pushed_at,
 stargazers_count,
 language
  }"  > ./.cache/api-${OUTPUT_FILE}.json

}
