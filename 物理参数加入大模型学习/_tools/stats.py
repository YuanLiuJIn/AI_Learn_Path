import re
from pathlib import Path

D = Path(r"c:\Users\Administrator\Desktop\物理参数加入大模型学习\papers\_source_text")

for p in sorted(D.glob("*.txt")):
    t = p.read_text(encoding="utf-8")
    words = len(re.findall(r"[A-Za-z][A-Za-z'-]*", t))
    pages = t.count("<<<PAGE")
    print(f"{p.name}\tpages={pages}\tchars={len(t)}\twords={words}")
