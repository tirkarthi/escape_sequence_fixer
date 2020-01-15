# Escape sequence fixer

A simple script to fix invalid escape sequences deprecation warning by converting the string to raw strings.

# Usage

```python
# /tmp/foo.py

import re

numbers = re.compile("\d")
```

This will produce a warning regarding invalid escape sequence as below :

```
$ python -Wall /tmp/foo.py
/tmp/foo.py:3: DeprecationWarning: invalid escape sequence \d
  numbers = re.compile("\d")
```

Using `escape_seq_fixer.py` will create a patch to conver the strings to raw strings. The patch can be applied with `patch -p0 < fixer.patch`

```
python escape_sequence_fixer.py --input /tmp/foo.py
--- /tmp/foo.py
+++ /tmp/foo.py
@@ -1,3 +1,3 @@
 import re

-numbers = re.compile("\d")
+numbers = re.compile(r"\d")
```

# Help

```
usage: escape_sequence_fixer.py [-h] [--input INPUT [INPUT ...]]
                                [--output [OUTPUT]]

optional arguments:
  -h, --help            show this help message and exit
  --input INPUT [INPUT ...]
                        List of files as input.
  --output [OUTPUT]     Output file for the patch.
```