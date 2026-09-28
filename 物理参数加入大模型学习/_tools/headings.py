import re
import sys
from pathlib import Path

D = Path(r"c:\Users\Administrator\Desktop\物理参数加入大模型学习\papers\_source_text")

name = sys.argv[1]
path = next(D.glob(f"*{name}*.raw.txt"))
text = path.read_text(encoding="utf-8")

print(f"### {path.name}")
for i, line in enumerate(text.splitlines()):
    s = line.strip()
    if not s or s.startswith("<<<PAGE"):
        continue
    if len(s) > 70 or len(s) < 3:
        continue
    if s[-1] in ".,;:—-":
        continue
    if not re.match(r"^[A-Z0-9(]", s):
        continue
    print(f"{i}\t{s}")
