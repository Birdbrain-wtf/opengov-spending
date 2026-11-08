import json,sys,urllib.request
import os
RAW=os.environ.get("RAW",".cache/raw"); os.makedirs(RAW,exist_ok=True)
chain,ep=sys.argv[1],sys.argv[2]
out=[];page=1
while True:
    u=f"https://{chain}-api.subsquare.io/{ep}?page={page}&page_size=100"
    d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"curl/8.0"}),timeout=90))
    out+=d['items']
    if len(out)>=d['total'] or not d['items']: break
    page+=1
json.dump(out,open(f"{RAW}/{chain}-{ep.replace('/','-')}.json","w"))
print(chain,ep,len(out))
