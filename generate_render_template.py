#!/usr/bin/env python

from flask import render_template
import jinja2
import sys
import json
import argparse

parser = argparse.ArgumentParser(description='Apply Jinja template to a file')
parser.add_argument('-t','--template', help='Jinja2 template file', required=True)
parser.add_argument('-d','--data', help='Json or yaml file', required=True)
args = vars(parser.parse_args())


with open(args['data'] ) as json_file:
    data = json.load(json_file)


# In this case, we will load templates off the filesystem.
# This means we must construct a FileSystemLoader object.
#
# The search path can be used to make finding templates by
#   relative paths much easier.  In this case, we are using
#   absolute paths and thus set it to the filesystem root.
templateLoader = jinja2.FileSystemLoader(["views","templates"])

# Provides the data necessary to read and
#   parse our templates.  We pass in the loader object here.
templateEnv = jinja2.Environment(loader=templateLoader)


# Read the template file using the environment object.
# This also constructs our Template object.
template = templateEnv.get_template(args['template'])



# Finally, process the template to produce our final text.
outputText = template.render(data=data)

print(outputText)
