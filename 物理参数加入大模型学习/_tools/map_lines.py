import sys
from pathlib import Path

D = Path(r"c:\Users\Administrator\Desktop\物理参数加入大模型学习\papers\_source_text")
path = next(D.glob(f"*{sys.argv[1]}*.txt"))
if path.name.endswith(".raw.txt"):
    path = Path(str(path).replace(".raw.txt", ".txt"))

lines = path.read_text(encoding="utf-8").splitlines()
print(f"# {path.name}  total_lines={len(lines)}")
for i, line in enumerate(lines, 1):
    s = " ".join(line.split())
    if not s:
        continue
    print(f"{i:>4} | len={len(s):>5} | {s[:110]}")
