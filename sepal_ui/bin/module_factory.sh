#!/bin/bash

# get the parent path 
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

# execute python script with the appropiate python version
/usr/bin/python3 ../scripts/sepal_module_skeleton.py