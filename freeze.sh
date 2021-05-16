#!/bin/bash
#############################################################
## Prepare requirements.txt lockfile for Heroku
#############################################################

# Append the deploy extras (see setup.py)
REQUIREMENTS="$(pip freeze | grep -v origin-website)
.[deploy]"

echo "$REQUIREMENTS" > requirements.txt
