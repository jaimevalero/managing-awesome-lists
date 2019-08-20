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


Main( )
{

  source ./.credentials
  # First   : Generate json data
  # Then    : Generate partial doc
  # Finally : Write results to repo file

}

Main
git add . ; git commit -m "Templatin'" ;  git push origin master
