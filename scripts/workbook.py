import csv,sys,json
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter
OUT=sys.argv[1]
wb=Workbook(); first=True
def sheet(name,path,widths=None):
    global first
    ws=wb.active if first else wb.create_sheet(); first=False; ws.title=name
    rows=list(csv.reader(open(path)))
    for i,r in enumerate(rows):
        out=[]
        for v in r:
            try: out.append(float(v) if i and v not in('',) and not v.startswith('0x') and v.replace('.','',1).replace('-','',1).isdigit() else v)
            except: out.append(v)
        ws.append(out)
    for c in ws[1]: c.font=Font(bold=True)
    ws.freeze_panes='A2'; ws.auto_filter.ref=ws.dimensions
    for j,h in enumerate(rows[0],1): ws.column_dimensions[get_column_letter(j)].width=min(60,max(10,len(h)+2)) if h!='title' else 70
sheet('By year',f'{OUT}/data/summary-by-year.csv')
sheet('By category',f'{OUT}/data/summary-by-category.csv')
sheet('By network and category',f'{OUT}/data/summary-by-network-category.csv')
sheet('Agentic cost model',f'{OUT}/data/agentic-cost-model.csv')
sheet('Cohort scenario',f'{OUT}/data/cohort-scenario.csv')
sheet('Governance tooling',f'{OUT}/data/governance-tooling.csv')
sheet('Referenda',f'{OUT}/data/referenda.csv')
sheet('Spend lines',f'{OUT}/data/spend-lines.csv')
wb.save(f'{OUT}/opengov-spending.xlsx'); print('workbook ok')
