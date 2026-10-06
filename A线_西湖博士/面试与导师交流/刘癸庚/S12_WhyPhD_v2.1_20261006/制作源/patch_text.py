"""One visible text-node substitution only. No PowerPoint reconstruction or shared builder."""
from pathlib import Path
import hashlib,json,zipfile,shutil

OUT=Path(__file__).resolve().parents[1]
PI=OUT.parent
SOURCE=PI/'S12_WhyPhD_v2_20261006'
OLD='但做得越多，我越觉得自己真正缺的是'
NEW='但做得越多，我越觉得自己还需要补的是'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    src=SOURCE/'S12_WhyPhD_v2.pptx'
    dest=OUT/'S12_WhyPhD_v2.1.pptx'
    changed=[]
    with zipfile.ZipFile(src) as a,zipfile.ZipFile(dest,'w') as b:
        for info in a.infolist():
            content=a.read(info.filename)
            if info.filename=='ppt/slides/slide1.xml':
                assert content.count(OLD.encode('utf-8'))==1
                content=content.replace(OLD.encode('utf-8'),NEW.encode('utf-8'))
            b.writestr(info,content)
    with zipfile.ZipFile(src) as a,zipfile.ZipFile(dest) as b:
        assert a.namelist()==b.namelist()
        for name in a.namelist():
            if a.read(name)!=b.read(name):
                changed.append(name)
                assert b.read(name)==a.read(name).replace(OLD.encode(),NEW.encode())
        assert changed==['ppt/slides/slide1.xml']
    shutil.copyfile(SOURCE/'本页备注.md',OUT/'本页备注.md')
    report=dict(source=src.relative_to(PI).as_posix(),source_sha256=sha(src),
                output=dest.name,output_sha256=sha(dest),changed_parts=changed,
                exact_replacement_only=True,old=OLD+'理论深度和专业判断。',new=NEW+'理论深度和专业判断。',
                notes_identical=sha(SOURCE/'本页备注.md')==sha(OUT/'本页备注.md'),
                all_other_xml_parts_and_resources_identical=True,
                unchanged='Existing newline, shape names, geometry, typefaces, font sizes, colors, all other slide text, embedded notes, theme and metadata.')
    (OUT/'单句修订检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('S12 v2.1: one string changed in slide1.xml; all other parts identical')

if __name__=='__main__':main()
