#!/usr/bin/bash

file_name=$1

python pandas_numpy_eval/evaluate_functional_correctness.py --sample_file dump/cache/$file_name.jsonl
