#!/usr/bin/env bash
python main.py $1 && clang code.ll && ./a.out && echo ''
