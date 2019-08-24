#! /bin/bash

source ./lib-actions.sh


# Render all elements
Regenerate_All_HTML( )
{

### Index
./generate_render_template.py  -t template-index.html --data ${INDEX_JSON_DATA} > index.html

### NavBar
./generate_render_template.py  -t template-navbar.html --data ${README_JSON_DATA} >  views/layout/navbar.html

### Readme
./generate_render_template.py  -t template-readme.html --data /tmp/readme.json >> README.md

### Topics
Render_Topics

### Listas
./get_list_details.sh
}

Regenerate_All_HTML
