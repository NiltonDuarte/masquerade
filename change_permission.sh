#!/bin/bash

#file chaging file permission on git is not working
#this should be made by:
#git update-index --chmod=+x <file>

chmod +x ./source/controller*.py
chmod +x ./source/agent*.py 

chmod +x ./testes/controller*.py
chmod +x ./testes/agent*.py 