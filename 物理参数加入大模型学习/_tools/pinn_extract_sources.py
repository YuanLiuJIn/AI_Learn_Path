from html.parser import HTMLParser
from pathlib import Path
class TextParser(HTMLParser):
    def __init__(self): super().__init__(); self.skip=0; self.parts=[]
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'): self.skip+=1
        if tag in ('p','h1','h2','h3','div'): self.parts.append('\n')
    def handle_endtag(self,tag):
        if tag in ('script','style'): self.skip=max(0,self.skip-1)
        if tag in ('p','h1','h2','h3','div'): self.parts.append('\n')
    def handle_data(self,data):
        if not self.skip: self.parts.append(data)
root=Path(__file__).resolve().parent.parent/'docs/pinn_recent_survey/sources'
for p in root.glob('*.html'):
    parser=TextParser();parser.feed(p.read_text(encoding='utf-8-sig'))
    lines=[' '.join(x.split()) for x in ''.join(parser.parts).splitlines()]
    p.with_suffix('.txt').write_text('\n'.join(x for x in lines if x),encoding='utf-8')
    print(p.stem)
