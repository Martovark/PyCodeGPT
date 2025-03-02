from typing import Iterable, Dict
import gzip
import json
import os
import re
import textwrap


ROOT = os.path.dirname(os.path.abspath(__file__))

# --------------------------------------------------------
# You can choose from the two options "pandas" or "numpy".
# --------------------------------------------------------
LIB = os.getenv("LIB")
assert LIB == "pandas" or LIB == "numpy"

HUMAN_EVAL = (
    os.path.join(ROOT, "..", "data", "PandasEval.jsonl.gz")
    if LIB == "pandas"
    else os.path.join(ROOT, "..", "data", "NumpyEval.jsonl.gz")
)

print("***" * 20)
print("load eval from {}".format(HUMAN_EVAL.split("/")[-1].replace(".jsonl.gz", "")))
print("***" * 20)


def read_problems(evalset_file: str = HUMAN_EVAL) -> Dict[str, Dict]:
    """
    Reads the problems from the evaluation set
    """
    return {task["task_id"]: task for task in stream_jsonl(evalset_file)}


def extract_python_code(markdown_text):
    # Regex pattern to extract Python code blocks
    pattern = r"```python\n(.*?)\n```"

    # Find all matches in the markdown text
    matches = re.findall(pattern, markdown_text, re.DOTALL)

    return matches


def get_function_body(func):
    import ast
    import inspect

    # Get the source code of the function
    # print(f"Before extraction: {func}")
    func = extract_python_code(func)[0]
    # print(f"After extraction: {func}")
    source = inspect.getsource(func)

    # Parse the source code into an AST
    tree = ast.parse(source)

    # Extract the function definition node
    func_def = tree.body[0]

    # Extract the body of the function
    body = func_def.body

    # Convert AST nodes back to source code
    body_source = ast.get_source_segment(source, body[0])

    # Join all lines of the body, excluding any docstrings
    body_lines = []
    for node in body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Str):
            continue  # Skip docstrings
        body_lines.append(ast.get_source_segment(source, node))

    return "\n".join(body_lines)


import autopep8


def auto_indent_code(code: str) -> str:
    """
    Auto-indent the provided Python code using autopep8.

    Args:
        code (str): The Python code to be formatted.

    Returns:
        str: The formatted Python code.
    """
    # Format the code using autopep8
    formatted_code = autopep8.fix_code(code)
    return formatted_code


def remove_func_name(solution: str):
    solution = solution.split("\n")
    len_before = len(solution)
    solution = list(filter(lambda x: not x.startswith("def "), solution))
    len_after = len(solution)

    solution = "\n".join(solution)
    solution = auto_indent_code(solution)

    if len_before != len_after:
        solution = textwrap.indent(solution, "    ")
    return solution


def hook(dct):
    if "parsed_predict" in dct:
        try:
            parsed_predict = dct.pop("parsed_predict")
            if isinstance(parsed_predict, list):
                assert len(parsed_predict) == 1, (
                    f"len of parsed_predict must be 1, but len: {len(parsed_predict)}"
                )
                parsed_predict = parsed_predict[0]
            solution = extract_python_code(parsed_predict)[0]
            solution = remove_func_name(solution)
            dct["completion"] = solution
        except:
            print("Empty completion!")
            dct["completion"] = ""
    return dct


def stream_jsonl(filename: str) -> Iterable[Dict]:
    """
    Parses each jsonl line and yields it as a dictionary
    """
    if filename.endswith(".gz"):
        with open(filename, "rb") as gzfp:
            with gzip.open(gzfp, "rt") as fp:
                for line in fp:
                    if any(not x.isspace() for x in line):
                        dct = json.loads(line, object_hook=hook)
                        yield dct
    else:
        with open(filename, "r") as fp:
            for line in fp:
                if any(not x.isspace() for x in line):
                    dct = json.loads(line, object_hook=hook)
                    yield dct


def write_jsonl(filename: str, data: Iterable[Dict], append: bool = False):
    """
    Writes an iterable of dictionaries to jsonl
    """
    if append:
        mode = "ab"
    else:
        mode = "wb"
    filename = os.path.expanduser(filename)
    if filename.endswith(".gz"):
        with open(filename, mode) as fp:
            with gzip.GzipFile(fileobj=fp, mode="wb") as gzfp:
                for x in data:
                    gzfp.write((json.dumps(x) + "\n").encode("utf-8"))
    else:
        with open(filename, mode) as fp:
            for x in data:
                fp.write((json.dumps(x) + "\n").encode("utf-8"))
