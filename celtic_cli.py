"""Query Celtic Tuning from your terminal"""

import sys

from celtic_tuning import Celtic

# Usage notes:
# python3 celtic.py AB12CDE

try:
    celtic = Celtic(sys.argv[1])
except ValueError as e:
    print(e)
    sys.exit(1)

ret_type = sys.argv[2] if len(sys.argv) > 2 else "pretty"

if ret_type == "pretty":
    print(celtic.get_all().pretty_printed)
elif ret_type == "all":
    print(celtic.get_all())
else:
    print(f"Invalid type: {ret_type}")
