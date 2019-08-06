#!/bin/sh

conda create -n torexitnode_simple python=3.7
conda activate torexitnode_simple
conda install --file www/tor/requirements.txt
