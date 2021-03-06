import argparse
import difflib
import sys

from io import BytesIO
from tokenize import tokenize, STRING


def has_invalid_escape_sequence(text):
    # Adapted from https://github.com/PyCQA/pycodestyle/blob/d219c684f117be77927d33146e76a5364161e518/pycodestyle.py#L1560
    valid = [
        "\n",
        "\\",
        "'",
        '"',
        "a",
        "b",
        "f",
        "n",
        "r",
        "t",
        "v",
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "x",
        # Escape sequences only recognized in string literals
        "N",
        "u",
        "U",
    ]

    quote = text[-3:] if text[-3:] in ('"""', "'''") else text[-1]
    # Extract string modifiers (e.g. u or r)
    quote_pos = text.index(quote)
    prefix = text[:quote_pos].lower()
    start = quote_pos + len(quote)
    string = text[start:-len(quote)]

    if "r" not in prefix:
        pos = string.find("\\")
        while pos >= 0:
            pos += 1
            if string[pos] not in valid:
                return True
            else:
                pos = string.find("\\", pos + 1)


def add_raw_string_prefix(start_index, line):
    return line[:start_index] + "r" + line[start_index:]


def process_file(fileobj):
    source = fileobj.read()
    actual_lines = source.splitlines(keepends=True)
    expected_lines = source.splitlines(keepends=True)
    previous_line_indices = (None, None)
    prefix_count = 0
    tokens = tokenize(BytesIO(source.encode("utf-8")).readline)
    for toknum, tokval, start_index, end_index, line in tokens:
        if toknum == STRING:
            start_line, start = start_index
            end_line, end = end_index
            if has_invalid_escape_sequence(tokval):
                # If we found a escape sequence for a string token on the same
                # line as last replacement then use the previous string which
                # has the fix. Since the previous string has r added then increment
                # start by 1. For multiple occurrences keep using the string and increment
                # prefix count. Once we reach next line then reset the prefix counter for next
                # iteration of fixes.
                # "\d" + "\d" + "\d"
                # previous_line = r"\d" + "\d" + "\d", prefix_count = 1
                # previous_line = r"\d" + r"\d" + "\d", prefix_count = 2
                # previous_line = r"\d" + r"\d" + r"\d", prefix_count = 3

                if (start_line, end_line) == previous_line_indices:
                    line = previous_line
                    prefix_count += 1
                else:
                    prefix_count = 0

                line = add_raw_string_prefix(start + prefix_count, line)
                line_numbers = slice(start_line - 1, end_line)
                expected_lines[line_numbers] = line.splitlines(keepends=True)
                previous_line = line
                previous_line_indices = (start_line, end_line)

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
