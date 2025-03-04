#!/usr/bin/bash

source proj_env/bin/activate

file_name=$1
dump=$2

echo "\n\nfile_name: $file_name, dump: $dump\n\n"

python pandas_numpy_eval/evaluate_functional_correctness.py --sample_file $dump/cache/$file_name.jsonl --dump $dump
