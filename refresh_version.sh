#! /bin/bash

# Refresh version,
# Re-render navbar template
# download json from api
# Re render from the new template
 ./get_list_details.sh   ;
./update-documentation.sh ;
./get_list_details.sh   ;
./update-documentation.sh ;

# Push changes
##git add . ; git commit -m "Refresh version" ;  git push origin master
