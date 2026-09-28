import sys
from pathlib import Path

D = Path(r"c:\Users\Administrator\Desktop\物理参数加入大模型学习\papers\_source_text")
n = int(sys.argv[1]) if len(sys.argv) > 1 else 2200

for p in sorted(D.glob("*.txt")):
    if p.name.startswith("_"):
        continue
    t = p.read_text(encoding="utf-8")
    body = t.split("<<<PAGE 2>>>")[0]
    body = body.replace("<<<PAGE 1>>>", "").strip()
    print(f"\n########## {p.name} ##########\n")
    print(body[:n])
