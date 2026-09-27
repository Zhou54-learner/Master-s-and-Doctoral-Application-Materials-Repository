"""DEFENSE archival utility. Never imports or executes research code. Exclusive writes."""
from pathlib import Path
import csv, hashlib, json, os, shutil, stat, time, zipfile
from datetime import datetime

ROOT = Path('F:/1A硕博申请')
OUT = ROOT / '07_Research_Defense'
REC = OUT / '98_Archive_Records'
TH = OUT / '01_Thesis_Microwave_Absorber'
DESK = Path('E:/360MoveData/Users/zzj/OneDrive/桌面')
FIELDS = ['filename','type','source','copy','accessible_copy','project','classification','original_file','later_summary','multiple_versions','trusted_version','copied','missing_original','bytes','source_mtime','sha256','note']
loose=[]; archives=[]; errors=[]

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()

def row(p,dst,project,kind='ORIGINAL',note='原位置既存文件；不证明个人作者归属'):
    st=p.stat()
    return dict(zip(FIELDS,[p.name,p.suffix.lower() or '(no extension)',p.as_posix(),str(dst),'',project,kind,'yes' if kind!='APPLICATION' else 'no','yes' if kind=='APPLICATION' else 'unconfirmed','见版本关系及同名/哈希清单','不按文件名或修改时间判定最终版','pending','no',st.st_size,datetime.fromtimestamp(st.st_mtime).isoformat(),' ',note]))

def copy(p,dst,project,kind='ORIGINAL',note='原位置既存文件；不证明个人作者归属'):
    dst.parent.mkdir(parents=True,exist_ok=True)
    r=row(p,dst.relative_to(OUT).as_posix(),project,kind,note)
    before=p.stat()
    with open(p,'rb') as src,open(dst,'xb') as target:
        h=hashlib.sha256()
        for b in iter(lambda:src.read(4*1024*1024),b''):target.write(b);h.update(b)
    shutil.copystat(p,dst)
    r['sha256']=h.hexdigest()
    assert sha(dst)==r['sha256'],str(dst)
    assert (before.st_size,before.st_mtime_ns)==(p.stat().st_size,p.stat().st_mtime_ns),str(p)
    dst.chmod(stat.S_IREAD)
    r['copied']='yes;SHA256 verified';loose.append(r)
    return r

def tree(src,dst,project):
    for d,dirs,files in os.walk(src):
        for f in sorted(files):
            p=Path(d)/f
            kind='REFERENCE' if ('其他组' in p.parts or '模板' in f or f.startswith(('沈振宇','邢文文','硕士学位论文-李禧龙'))) else 'ORIGINAL'
            copy(p,dst/p.relative_to(src),project,kind)

def write_csv(path,rows):
    with open(path,'x',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)

def main():
    REC.mkdir(parents=True,exist_ok=True)
    # Keep original relative paths inside each source snapshot.
    tree(DESK/'毕业设计',TH/'00_Original_Documents/E_毕业设计','Thesis')
    tree(Path('E:/2024/yxy组代码'),OUT/'02_Dusty_Plasma/01_MATLAB_Code/E_yxy组代码','Dusty_Plasma')
    tree(Path('E:/2024/data figure'),OUT/'02_Dusty_Plasma/03_Figures/E_data_figure','Dusty_Plasma')
    copy(Path('E:/2024/data figure.zip'),OUT/'02_Dusty_Plasma/04_Original_Archives/data figure.zip','Dusty_Plasma')
    tree(Path('E:/2024/大创'),OUT/'03_Absorbing_Materials_Project/01_Project_Documents/E_大创','Materials')
    for name in ['z-雨田修改稿.docx','论文素材.docx']:
        copy(DESK/name,OUT/'03_Absorbing_Materials_Project/04_Manuscript'/name,'Materials',note='团队稿/素材；修订作者身份与本人具体贡献待核')
    for name in ['全国大学生创新年会学术论文 3.0 .pdf','用于无线通信的磁纳米合金_石墨烯复合型吸波材料设计_雨田.pdf']:
        copy(DESK/name,OUT/'03_Absorbing_Materials_Project/00_Paper/Desktop_versions'/name,'Materials',note='同主题成果/历史版本；不凭文件名判定本人贡献')
    copy(DESK/'2_202410759992X-专利申请受理通知书(3).pdf',OUT/'03_Absorbing_Materials_Project/01_Project_Documents/专利关联线索/2_202410759992X-专利申请受理通知书(3).pdf','Materials',note='受理通知线索；不证明授权或本人核心发明贡献')
    for name in ['大创结题证书扫描版.jpg','大创结题证书原图版.jpg','大创国家级平台查询截图_202410213227.png']:
        copy(ROOT/'个人资料'/name,OUT/'03_Absorbing_Materials_Project/01_Project_Documents/申请目录已归档证据'/name,'Materials')
    copy(ROOT/'个人资料/论文1.pdf',OUT/'03_Absorbing_Materials_Project/00_Paper/论文1.pdf','Materials')
    copy(ROOT/'个人资料/论文2.pdf',OUT/'02_Dusty_Plasma/00_Paper/论文2.pdf','Dusty_Plasma')
    acceptance=DESK/'毕业设计/结题/终稿/附件2：2024年中国国际大学生创新大赛培育项目结题验收书1.3(1).docx'
    copy(acceptance,OUT/'03_Absorbing_Materials_Project/01_Project_Documents'/acceptance.name,'Materials',note='跨项目便利副本；填报编辑稿，不是同编号国家级结题证明')
    app=OUT/'00_Application_Claims'
    for p in (ROOT/'A线工作区/材料').rglob('*'):
        if p.is_file() and p.suffix.lower() in {'.md','.pdf','.docx'}:
            if any(x in p.name for x in ['简历','CV_','CV.','CV增密','材料版本','changelog']):
                copy(p,app/'CV_Master'/p.relative_to(ROOT/'A线工作区/材料'),'Application','APPLICATION')
    for rel in ['A线工作区/材料审计与申请人事实.md','A线工作区/毕设与新增个人证据核验_20260926.md','A线工作区/材料/推荐人事实支持包_v0.1_INTERNAL.md','A线工作区/材料/晶格波项目贡献与复述底稿_v0.1_INTERNAL.md','A线工作区/材料/荣誉与学籍证据登记_20260926.md','A线工作区/材料/历史版本/中文CV_v0.2_修改与真实性检查.md','A线工作区/材料/科研口述与面试追问_v0.1_INTERNAL.md','A线工作区/材料/Research_Project_Sheet_v1.0_READY.md','A线工作区/材料/对外PDF/Zijing_Zhou_Research_Project_v1.0.pdf']:
        copy(ROOT/rel,app/'Contribution_Record'/rel,'Application','APPLICATION',note='后期申请整理，非科研原始记录；副本内旧相对链接按原路径解释')
    for rel in ['A线_PI_总表_v1.md','西湖-朱一舟组/A线_PI_01_朱一舟.md','A线工作区/招生核验与PI行动表.md','A线工作区/材料/个人陈述内容母版_v0.1_INTERNAL.md','A线工作区/材料/个人申请资料准备清单.md']:
        copy(ROOT/rel,app/'Applicant_Profile'/rel,'Application','APPLICATION',note='含历史分析判断；新事实基准优先，不作能力证明')
    copy(DESK/'论文、专利、奖项.docx',app/'Contribution_Record/历史个人成果清单/论文、专利、奖项.docx','Application','APPLICATION',note='历史混合成果清单；部分列项不是本人署名/获奖，按最新审计纠正')
    print('Small source trees and application claims copied:',len(loose),flush=True)
    # Full F source archive, including every solver internal file. ZIP_STORED avoids altering member bytes.
    src=Path('F:/biyesheji'); arcdir=TH/'80_Full_Source_Snapshot';arcdir.mkdir(parents=True,exist_ok=True)
    for top in sorted(src.iterdir(),key=lambda p:(p.name=='temp',p.name)):
        label=top.name if top.is_dir() else '_root_'+top.name
        zpath=arcdir/(label+'.zip'); ipath=REC/('F_biyesheji_'+label+'.csv')
        count=size=0; started=time.time(); ext={}
        with zipfile.ZipFile(zpath,'x',compression=zipfile.ZIP_STORED,allowZip64=True,strict_timestamps=False) as z,open(ipath,'x',encoding='utf-8-sig',newline='') as inv:
            w=csv.DictWriter(inv,fieldnames=FIELDS);w.writeheader()
            iterator=(Path(d)/f for d,ds,fs in os.walk(top) for f in sorted(fs)) if top.is_dir() else iter([top])
            for p in iterator:
                rel=p.relative_to(src); member=rel.as_posix(); r=row(p,zpath.relative_to(OUT).as_posix()+'::'+member,'Thesis')
                st=p.stat();h=hashlib.sha256();zi=zipfile.ZipInfo.from_file(p,member,strict_timestamps=False)
                with open(p,'rb') as f,z.open(zi,'w',force_zip64=True) as target:
                    for b in iter(lambda:f.read(1024*1024),b''):target.write(b);h.update(b)
                assert (st.st_size,st.st_mtime_ns)==(p.stat().st_size,p.stat().st_mtime_ns),str(p)
                r['sha256']=h.hexdigest();r['copied']='yes;archive member;CRC validation in archive report'
                suffix=p.suffix.lower(); ext[suffix]=ext.get(suffix,0)+1
                # Easy access: all models; source code and plain exports outside CST internals.
                internal=any(x.lower() in {'model','modelcache','result','sp','3d'} for x in rel.parts[:-1])
                dest=None
                if rel.parts[0]=='code': dest=TH/'02_Python_Code/Origin_Unresolved/F_biyesheji'/rel
                elif suffix=='.cst': dest=TH/'03_CST_Models/F_biyesheji'/rel
                elif not internal and suffix in {'.txt','.csv','.xlsx','.xls','.json','.log','.py','.md','.pdf','.zip','.png','.jpg','.bmp'}:
                    category='06_Figures' if suffix in {'.png','.jpg','.bmp','.pdf'} else '04_Raw_and_Processed_Exports'
                    dest=TH/category/'F_biyesheji'/rel
                if dest:
                    cr=copy(p,dest,'Thesis');assert cr['sha256']==r['sha256'];r['accessible_copy']=cr['copy']
                w.writerow(r);count+=1;size+=st.st_size
                if count%25000==0:print(label,count,'files',round(size/1024**3,2),'GiB',flush=True);inv.flush()
        # Verify all archived members, not just ZIP directory headers.
        with zipfile.ZipFile(zpath) as z:
            bad=z.testzip();assert bad is None,(zpath,bad)
            assert len(z.infolist())==count
        zpath.chmod(stat.S_IREAD)
        archives.append({'source':top.as_posix(),'archive':zpath.relative_to(OUT).as_posix(),'inventory':ipath.relative_to(OUT).as_posix(),'files':count,'source_bytes':size,'archive_bytes':zpath.stat().st_size,'sha256':sha(zpath),'all_members_crc_verified':True,'extensions':ext})
        print('DONE',label,count,'files',round(time.time()-started,1),'seconds',flush=True)
        (REC/'progress.json').write_text(json.dumps(archives,ensure_ascii=False,indent=2),encoding='utf-8')
    write_csv(REC/'Loose_Files.csv',loose)
    report={'snapshot_date':'2026-09-26','archives':archives,'loose_files':len(loose),'loose_bytes':sum(x['bytes'] for x in loose),'errors':errors,'all_loose_sha256_verified':True,'source_files_not_modified':True}
    (REC/'Copy_Verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('COMPLETE',len(loose),'loose copies;',sum(x['files'] for x in archives),'archived F-source files',flush=True)

if __name__=='__main__':main()
