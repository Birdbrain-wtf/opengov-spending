import json,urllib.request,time,datetime,os
RAW=os.environ.get("RAW",".cache/raw"); os.makedirs(RAW,exist_ok=True)
for sym in ['KSM','DOT']:
    rows={};after=int(time.time()*1000)+86400000
    while True:
        u=f"https://www.okx.com/api/v5/market/history-index-candles?instId={sym}-USD&bar=1Dutc&limit=100&after={after}"
        d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"curl/8.0"}),timeout=30))['data']
        if not d: break
        for c in d: rows[int(c[0])]=float(c[4])
        after=min(int(c[0]) for c in d)
        if after<1667260800000: break
        time.sleep(0.15)
    with open(f"{RAW}/price-{sym}.csv","w") as f:
        f.write('date,close_usd\n')
        for t in sorted(rows): f.write(f"{datetime.datetime.utcfromtimestamp(t/1000).date()},{rows[t]}\n")
    print(sym,len(rows))
