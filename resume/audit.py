"""
Checks every number in every tailored resume PDF against the master profile.
Anything printed is a number the profile doesn't contain: confirm it or remove it before sending.
Line-wrap artifacts (e.g. '2019' followed by a newline) can show up as false positives; check them by eye.

  python3 resume/audit.py resume/private/master-profile.md "resume/private/jobs/*/*.pdf"
"""
import glob
import re
import subprocess
import sys

def norm(s):
    return re.sub(r'[\s, ]', '', s).lower()

profile = norm(open(sys.argv[1]).read())
number = re.compile(r'(?:₹|\$)?\d[\d,]*(?:\.\d+)?(?:x|%|L|Cr|K|M)?\+?')
small_counts = {str(n) for n in range(0, 41)}

for pdf in sorted(glob.glob(sys.argv[2])):
    text = subprocess.run(['pdftotext', pdf, '-'], capture_output=True, text=True).stdout
    missing = sorted({m for m in number.findall(text)
                      if norm(m).rstrip('+') not in small_counts
                      and norm(m).rstrip('+').lstrip('₹$') not in profile})
    print(f"{pdf}: {', '.join(missing) if missing else 'all numbers found in profile'}")
