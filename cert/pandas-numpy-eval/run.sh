#!/usr/bin/bash

source proj_env/bin/activate

file_name=$1
dump=$2

echo "file_name: $file_name, dump: $dump"

python pandas_numpy_eval/evaluate_functional_correctness.py --sample_file $dump/cache/$file_name.jsonl --dump $dump
