import re
import sys
from pathlib import Path

from pypdf import PdfReader

SRC = Path(r"c:\Users\Administrator\Desktop\物理参数加入大模型学习\papers")
OUT = SRC / "_source_text"
OUT.mkdir(parents=True, exist_ok=True)

HEADING = re.compile(
    r"^(\d{1,2}(?:\.\d{1,2}){0,3})\.?\s+([A-Z][A-Za-z0-9 ,\-–:()/]{2,80})$"
)


def clean(t: str) -> str:
    """把 PDF 硬换行还原成段落。"""
    t = t.replace("\r\n", "\n")
    t = re.sub(r"(\w)-\n(\w)", r"\1\2", t)          # 断词连字符
    t = re.sub(r"(?<!\n)\n(?!\n)", " ", t)          # 段内换行 -> 空格
    t = re.sub(r"[ \t]{2,}", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def main() -> None:
    outlines = []
    for pdf in sorted(SRC.glob("*.pdf")):
        reader = PdfReader(str(pdf))
        raw_parts, clean_parts = [], []
        for i, page in enumerate(reader.pages, 1):
            try:
                txt = page.extract_text() or ""
            except Exception as exc:  # noqa: BLE001
                txt = f"[EXTRACT_ERROR: {exc}]"
            raw_parts.append(f"\n<<<PAGE {i}>>>\n{txt.replace(chr(13), '')}")
            clean_parts.append(f"\n<<<PAGE {i}>>>\n{clean(txt)}")

        raw_body = "\n".join(raw_parts)
        clean_body = "\n".join(clean_parts)
        (OUT / f"{pdf.stem}.raw.txt").write_text(raw_body, encoding="utf-8")
        (OUT / f"{pdf.stem}.txt").write_text(clean_body, encoding="utf-8")

        words = len(re.findall(r"[A-Za-z][A-Za-z'-]*", clean_body))
        print(f"{pdf.name}\tpages={len(reader.pages)}\twords={words}")

        heads = []
        for line in raw_body.splitlines():
            m = HEADING.match(line.strip())
            if m and not m.group(2).lower().startswith(("see", "and", "of")):
                heads.append(f"  p?  {line.strip()}")
        outlines.append(f"\n=== {pdf.stem} ===\n" + "\n".join(heads))

    (OUT / "_outlines.txt").write_text("\n".join(outlines), encoding="utf-8")
    print("outline written")


if __name__ == "__main__":
    sys.exit(main())
