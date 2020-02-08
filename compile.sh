#!/usr/bin/env bash
python main.py $1 && clang code.ll 
echo '_______________________________________'
echo 'CODE OUTPUT:'
./a.out && echo ''
