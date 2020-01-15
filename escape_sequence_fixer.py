import argparse
import ast
import difflib
import sys
import warnings

from io import BytesIO
from tokenize import tokenize, STRING


def has_invalid_escape_sequence(string):
    # There is a better way but this is much simpler
    # https://github.com/PyCQA/pycodestyle/blob/d219c684f117be77927d33146e76a5364161e518/pycodestyle.py#L1560
    with warnings.catch_warnings(record=True) as w:
        warnings.filterwarnings("always", category=DeprecationWarning)
        compile(string, "<stdin>", "exec")
        return any("invalid escape" in str(warning.message) for warning in w)


def add_raw_string_prefix(start_index, line):
    return line[:start_index] + "r" + line[start_index:]


def process_file(fileobj):
    source = fileobj.read()
    actual_lines = source.splitlines(keepends=True)
    expected_lines = source.splitlines(keepends=True)
    tokens = tokenize(BytesIO(source.encode("utf-8")).readline)
    for toknum, tokval, start_index, end_index, line in tokens:
        if toknum == STRING:
            start_lineno, start = start_index
            end_lineno, end = end_index
            string = tokval
            if has_invalid_escape_sequence(string):
                line = add_raw_string_prefix(start, line)
                line_numbers = slice(start_lineno - 1, end_lineno)
                expected_lines[line_numbers] = line.splitlines(keepends=True)

    return actual_lines, expected_lines


def generate_patch(actual_lines, expected_lines, filename):
    patch = difflib.unified_diff(
        actual_lines, expected_lines, fromfile=filename, tofile=filename
    )
    return "".join(patch)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        nargs="+",
        default=sys.stdin,
        type=argparse.FileType(encoding="utf-8"),
        help="List of files as input.",
    )
    parser.add_argument(
        "--output",
        nargs="?",
        default=sys.stdout,
        type=argparse.FileType("w", encoding="utf-8"),
        help="Output file for the patch.",
    )
    namespace = parser.parse_args()

    for fileobj in namespace.input:
        filename = fileobj.name
        actual_lines, expected_lines = process_file(fileobj)
        patch = generate_patch(actual_lines, expected_lines, filename)
        namespace.output.write(patch)
        namespace.output.write("\n")


if __name__ == "__main__":
    main()
