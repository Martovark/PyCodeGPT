import fire
import os
import sys

p = os.getcwd()
print(p)
sys.path.append(p)

from pandas_numpy_eval.data import HUMAN_EVAL
from pandas_numpy_eval.evaluation import evaluate_functional_correctness


def entry_point(
    sample_file: str,
    dump: str,
    k: int = 1,
    n_workers: int = 4,
    timeout: float = 10.0,
    problem_file: str = HUMAN_EVAL,
):
    """
    Evaluates the functional correctness of generated samples, and writes
    results to f"{sample_file}_results.jsonl.gz"
    """
    if isinstance(k, int):
        k = [k]
    results = evaluate_functional_correctness(
        sample_file,
        k=k,
        n_workers=n_workers,
        dump=dump,
        timeout=timeout,
        problem_file=problem_file,
    )
    print(results)


def main():
    fire.Fire(entry_point)


sys.exit(main())
