import json,os,sys,csv,datetime,collections
PRICES=sys.argv[1]; OUT=sys.argv[2]
RAW=os.environ.get('RAW','.cache/raw')
DEC={'kusama':12,'polkadot':10}; NAT={'kusama':'KSM','polkadot':'DOT'}
def prices(sym):
    p={}
    for row in csv.DictReader(open(f'{PRICES}/price-{sym}.csv')): p[row['date']]=float(row['close_usd'])
    return p
PR={'KSM':prices('KSM'),'DOT':prices('DOT')}
def price(sym,date):
    d=datetime.date.fromisoformat(date)
    for k in range(10):
        s=(d-datetime.timedelta(days=k)).isoformat()
        if s in PR[sym]: return PR[sym][s]
    return None
latest={s:PR[s][max(PR[s])] for s in PR}; latest_date=max(PR['KSM'])
def walk(x):
    if isinstance(x,dict):
        if 'section' in x and 'method' in x and 'args' in x:
            yield x
            for a in x['args']: yield from walk(a.get('value'))
        else:
            for v in x.values(): yield from walk(v)
    elif isinstance(x,list):
        for v in x: yield from walk(v)
def asset(ak,ch):
    s=json.dumps(ak)
    if '"globalConsensus": {"polkadot"' in s: return 'DOT',10
    if '"globalConsensus": {"kusama"' in s: return 'KSM',12
    if '"generalIndex": 1984' in s: return 'USDT',6
    if '"generalIndex": 1337' in s: return 'USDC',6
    if '"generalIndex": 30' in s and ch=='polkadot': return 'DED',10
    if 'generalIndex' in s: return 'OTHER:'+s[:80],0
    return NAT[ch],DEC[ch]
def toint(v):
    return int(v,16) if isinstance(v,str) and v.startswith('0x') else int(v)
def args(c): return {a['name']:a['value'] for a in c['args']}
bounties={}
for ch in DEC:
    for b in json.load(open(f'{RAW}/{ch}-treasury-bounties.json')):
        v=(b.get('onchainData') or {}).get('value')
        if v is not None: bounties[(ch,b['bountyIndex'])]=(toint(v),b.get('title'),(b.get('onchainData') or {}).get('state',{}).get('state'))
v2={}
for ch in DEC:
    for s in json.load(open(f'{RAW}/{ch}-treasury-spends.json')):
        v2.setdefault((ch,s.get('referendumIndex')),[]).append((toint(s['meta']['amount']),s['state'] if isinstance(s['state'],str) else s['state'].get('state')))
rows=[];review=[]
OVR={}
for ov in csv.DictReader(open(sys.argv[3])): OVR.setdefault((ov['network'],int(ov['referendum'])),[]).append(ov)
TRACK={0:'root',1:'whitelisted_caller',2:'wish_for_change',10:'staking_admin',11:'treasurer',12:'lease_admin',13:'fellowship_admin',14:'general_admin',15:'auction_admin',20:'referendum_canceller',21:'referendum_killer',30:'small_tipper',31:'big_tipper',32:'small_spender',33:'medium_spender',34:'big_spender'}
for ch in DEC:
    L=json.load(open(f'{RAW}/{ch}-referenda.json'))
    for r in L:
        i=r['referendumIndex']; st=r['state']['name']
        if st!='Executed': continue
        d=json.load(open(f'{RAW}/detail/{ch}-{i}.json'))
        o=d['onchainData']; date=datetime.datetime.utcfromtimestamp(r['state']['indexer']['blockTime']/1000).date().isoformat()
        items=[]
        for c in walk(o.get('proposal')):
            m=f"{c['section']}.{c['method']}"; a=args(c)
            if m in ('treasury.spendLocal',) or (m=='treasury.spend' and 'assetKind' not in a and 'asset_kind' not in a):
                items.append(('local',NAT[ch],toint(a['amount'])/10**DEC[ch],'paid (automatic)'))
            elif m=='treasury.spend':
                sym,dec=asset(a.get('assetKind') or a.get('asset_kind'),ch); amt=toint(a['amount'])
                stl=[s for (am,s) in v2.get((ch,i),[]) if am==amt]
                items.append(('v2',sym,amt/10**dec if dec else 0,(stl[0].lower() if stl else 'unknown')))
            elif m in ('bounties.approveBounty','bounties.approveBountyWithCurator'):
                bid=int(a.get('bountyId') or a.get('bounty_id')); b=bounties.get((ch,bid))
                items.append(('bounty',NAT[ch],(b[0]/10**DEC[ch]) if b else 0,f"bounty #{bid} {(b[2] or '').lower() if b else 'value unknown'}"))
            elif m=='treasury.proposeSpend':
                items.append(('local',NAT[ch],toint(a['value'])/10**DEC[ch],'paid (automatic)'))
            elif m=='multiAssetBounties.fundBounty':
                sym,dec=asset(a.get('assetKind'),ch); items.append(('bounty',sym,toint(a['value'])/10**dec if dec else 0,'multi-asset bounty funded'))
            elif c['section'] in ('balances','assets') and 'ransfer' in c['method']:
                review.append((ch,i,r['title'],m,json.dumps(a)[:200]))
        for ov in OVR.get((ch,i),[]): items.append((ov['kind'],ov['asset'],float(ov['amount']),ov['payout_status']))
        if not items:
            t=(r['title'] or '').lower()
            if any(w in t for w in ['fund','dot','ksm','usd','spend','bounty','grant','treasury','loan','payment','retro']):
                review.append((ch,i,r['title'],'NO-SPEND',(o.get('proposal') or {}).get('call',{}).get('section','?')))
            continue
        for k,(kind,sym,amt,status) in enumerate(items):
            if sym in ('USDT','USDC'): usd=amt; px=1.0; now=amt
            elif sym in ('KSM','DOT'): px=price(sym,date); usd=amt*px; now=amt*latest[sym]
            else: px=None; usd=None; now=None
            rows.append(dict(network=ch,referendum=i,item=k+1,date=date,year=date[:4],track=TRACK.get(r['track'],str(r['track'])),title=(r['title'] or '').strip(),kind=kind,asset=sym,amount=round(amt,6),price_usd_at_approval=px,usd_at_approval=None if usd is None else round(usd,2),usd_at_today_price=None if now is None else round(now,2),payout_status=status,proposer=r.get('proposer'),url=f"https://{ch}.subsquare.io/referenda/{i}"))
json.dump({'rows':rows,'review':review,'latest':latest,'latest_date':latest_date},open(OUT,'w'),indent=0)
print(len(rows),'rows',len(review),'to review')
for ch in DEC:
    tot=collections.defaultdict(float)
    for x in rows:
        if x['network']==ch and x['usd_at_approval']: tot[x['year']]+=x['usd_at_approval']
    print(ch,{k:round(v/1e6,2) for k,v in sorted(tot.items())},round(sum(tot.values())/1e6,1))
