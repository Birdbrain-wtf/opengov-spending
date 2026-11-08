import json,sys,urllib.request,os
RAW=os.environ.get("RAW",".cache/raw"); os.makedirs(RAW+"/detail",exist_ok=True)
from concurrent.futures import ThreadPoolExecutor
def get(a):
    ch,i=a; p=f"{RAW}/detail/{ch}-{i}.json"
    if os.path.exists(p): return
    for t in range(3):
        try:
            d=json.load(urllib.request.urlopen(urllib.request.Request(f"https://{ch}-api.subsquare.io/gov2/referendums/{i}",headers={"User-Agent":"curl/8.0"}),timeout=60))
            d.pop('content',None); d.pop('polkassemblyContentHtml',None)
            json.dump(d,open(p,'w')); return
        except Exception as e: err=e
    print('fail',ch,i,err)
jobs=[]
for ch in ['kusama','polkadot']:
    for r in json.load(open(f"{RAW}/{ch}-referenda.json")):
        if r['state']['name'] in ('Executed','Approved','Confirming','Deciding'): jobs.append((ch,r['referendumIndex']))
with ThreadPoolExecutor(10) as ex: list(ex.map(get,jobs))
print(len(jobs),len(os.listdir(RAW+"/detail")))
