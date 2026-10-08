"""Export saved chart objects in an isolated Excel instance, read-only, no links."""
from pathlib import Path
import json
import win32com.client
OUT=Path(__file__).resolve().parent.parent
books=json.loads((OUT/'历史资产核查/全部工作簿图件核查.json').read_text(encoding='utf8'))
app=win32com.client.DispatchEx('Excel.Application');app.Visible=False
app.DisplayAlerts=False;app.AskToUpdateLinks=False;app.AutomationSecurity=3
seen=set();reports=[]
try:
 for row in books:
  if not row['charts'] or row['sha256'] in seen:continue
  seen.add(row['sha256']);book=None
  try:
   book=app.Workbooks.Open(row['path'],UpdateLinks=0,ReadOnly=True)
   for ws in book.Worksheets:
    for i in range(1,ws.ChartObjects().Count+1):
     chart=ws.ChartObjects(i).Chart
     dest=OUT/'历史资产核查'/f'Excel原图_{len(reports)+1:02}.png'
     ok=chart.Export(str(dest),'PNG')
     reports.append(dict(source=row['path'],sheet=ws.Name,chart_index=i,excel_version=str(app.Version),output=dest.relative_to(OUT).as_posix(),success=bool(ok),series_count=chart.SeriesCollection().Count))
  finally:
   if book is not None:book.Close(False)
finally:app.Quit()
(OUT/'历史资产核查/Excel实际渲染.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(reports,ensure_ascii=False))
