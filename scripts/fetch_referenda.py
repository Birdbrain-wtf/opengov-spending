import json,sys,urllib.request,time
import os
RAW=os.environ.get("RAW",".cache/raw"); os.makedirs(RAW,exist_ok=True)
chain=sys.argv[1]
out=[];page=1
while True:
    u=f"https://{chain}-api.subsquare.io/gov2/referendums?page={page}&page_size=100"
    d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"curl/8.0"}),timeout=90))
    out+=d['items']
    if len(out)>=d['total'] or not d['items']: break
    page+=1
json.dump(out,open(f"{RAW}/{chain}-referenda.json","w"))
print(chain,len(out))
