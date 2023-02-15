"""Query Celtic Tuning from your terminal"""
import sys
from Celtic import Celtic

# Usage notes:
# python3 celtic.py AB12CDE

celtic = Celtic(sys.argv[1])

print(celtic.get_all_pretty())
