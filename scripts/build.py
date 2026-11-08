import json,csv,sys,collections,os
CAT,ASSUME,OUT=sys.argv[1],sys.argv[2],sys.argv[3]
d=json.load(open(CAT)); rows=d['rows']
A={r['category']:r for r in csv.DictReader(open(ASSUME))}
os.makedirs(f'{OUT}/data',exist_ok=True); os.makedirs(f'{OUT}/charts',exist_ok=True)
for r in rows:
    a=A[r['category']]; r['group']=a['group']
    u=r['usd_at_approval'] if r['counted']=='yes' and r['usd_at_approval'] else 0
    ls=float(a['labour_share'])
    r['usd_counted']=round(u,2)
    r['agentic_low_usd']=round(u*((1-ls)+ls*float(a['remaining_low'])),2)
    r['agentic_high_usd']=round(u*((1-ls)+ls*float(a['remaining_high'])),2)
F=['network','referendum','item','date','year','track','title','category','category_method','group','kind','asset','amount','price_usd_at_approval','usd_at_approval','usd_at_today_price','payout_status','counted','usd_counted','agentic_low_usd','agentic_high_usd','proposer','url']
with open(f'{OUT}/data/spend-lines.csv','w',newline='') as f:
    w=csv.DictWriter(f,F,extrasaction='ignore'); w.writeheader(); w.writerows(sorted(rows,key=lambda r:(r['network'],r['referendum'],r['item'])))
ref=collections.OrderedDict()
for r in rows:
    k=(r['network'],r['referendum'])
    x=ref.setdefault(k,dict(network=r['network'],referendum=r['referendum'],date=r['date'],track=r['track'],title=r['title'],category=r['category'],group=r['group'],assets=set(),usd_counted=0,usd_at_today_price=0,agentic_low_usd=0,agentic_high_usd=0,lines=0,url=r['url']))
    x['assets'].add(r['asset']); x['lines']+=1
    for f2 in ['usd_counted','agentic_low_usd','agentic_high_usd']: x[f2]+=r[f2]
    if r['counted']=='yes': x['usd_at_today_price']+=r['usd_at_today_price'] or 0
R=list(ref.values())
for x in R:
    x['assets']='+'.join(sorted(x['assets']))
    for f2 in ['usd_counted','usd_at_today_price','agentic_low_usd','agentic_high_usd']: x[f2]=round(x[f2],2)
R.sort(key=lambda x:-x['usd_counted'])
with open(f'{OUT}/data/referenda.csv','w',newline='') as f:
    w=csv.DictWriter(f,list(R[0].keys())); w.writeheader(); w.writerows(R)
def agg(keyf):
    t=collections.OrderedDict()
    for r in rows:
        k=keyf(r); x=t.setdefault(k,[0,0,0,0,set()])
        x[0]+=r['usd_counted']; x[1]+=r['agentic_low_usd']; x[2]+=r['agentic_high_usd']
        if r['counted']=='yes': x[3]+=r['usd_at_today_price'] or 0
        x[4].add((r['network'],r['referendum']))
    return t
S={}
for name,kf,hdr in [('by-year',lambda r:(r['network'],r['year']),['network','year']),('by-category',lambda r:(r['category'],r['group']),['category','group']),('by-network-category',lambda r:(r['network'],r['category']),['network','category']),('by-group-year',lambda r:(r['group'],r['year']),['group','year'])]:
    t=agg(kf); out=[]
    for k,v in sorted(t.items(),key=lambda kv:(-kv[1][0]) if name=='by-category' else kv[0]):
        out.append(dict(zip(hdr,k),referenda=len(v[4]),usd_at_approval=round(v[0]),usd_same_tokens_today=round(v[3]),agentic_low_usd=round(v[1]),agentic_high_usd=round(v[2])))
    with open(f'{OUT}/data/summary-{name}.csv','w',newline='') as f:
        w=csv.DictWriter(f,list(out[0].keys())); w.writeheader(); w.writerows(out)
    S[name]=out
with open(f'{OUT}/data/agentic-cost-model.csv','w',newline='') as f:
    cats={o['category']:o for o in S['by-category']}
    fl=['category','group','labour_share','remaining_low','remaining_high','usd_at_approval','agentic_low_usd','agentic_high_usd','label','rationale']
    w=csv.DictWriter(f,fl); w.writeheader()
    for c,a in A.items():
        o=cats.get(c,{}); w.writerow({**{k:a[k] for k in fl if k in a},'usd_at_approval':o.get('usd_at_approval',0),'agentic_low_usd':o.get('agentic_low_usd',0),'agentic_high_usd':o.get('agentic_high_usd',0)})
gov=[x for x in R if x['category']=='Governance tooling']
def who(t):
    t=t.lower()
    for k,n in [('polkassembly','Polkassembly'),('subsquare','Subsquare / OpenSquare'),('opensquare','Subsquare / OpenSquare'),('dotreasury','Subsquare / OpenSquare'),('og tracker','OpenGov.Watch (OG Tracker)'),('opengov.watch','OpenGov.Watch (OG Tracker)')]:
        if k in t: return n
    return 'Other governance tools'
with open(f'{OUT}/data/governance-tooling.csv','w',newline='') as f:
    w=csv.DictWriter(f,['platform']+list(gov[0].keys())); w.writeheader()
    for x in gov: w.writerow({'platform':who(x['title']),**x})
G=collections.defaultdict(lambda:[0,0]); 
for x in gov: G[who(x['title'])][0]+=x['usd_counted']; G[who(x['title'])][1]+=1
S['gov']={k:[round(v[0]),v[1]] for k,v in G.items()}
tot=lambda net=None:sum(r['usd_counted'] for r in rows if net in (None,r['network']))
S['totals']={'all':round(tot()),'kusama':round(tot('kusama')),'polkadot':round(tot('polkadot')),
 'today_all':round(sum((r['usd_at_today_price'] or 0) for r in rows if r['counted']=='yes')),
 'agentic_low':round(sum(r['agentic_low_usd'] for r in rows)),'agentic_high':round(sum(r['agentic_high_usd'] for r in rows)),
 'lines':len(rows),'referenda':len(R),'excluded_lines':sum(1 for r in rows if r['counted']=='no'),
 'latest_prices':d['latest'],'latest_date':d['latest_date'],
 'bounty_usd':round(sum(r['usd_counted'] for r in rows if r['kind']=='bounty')),
 'native_share':round(sum(r['usd_counted'] for r in rows if r['asset'] in('DOT','KSM'))/tot(),3)}
grp=collections.defaultdict(lambda:[0,0,0])
for r in rows: g=grp[r['group']]; g[0]+=r['usd_counted']; g[1]+=r['agentic_low_usd']; g[2]+=r['agentic_high_usd']
S['groups']={k:[round(x) for x in v] for k,v in grp.items()}
json.dump(S,open(f'{OUT}/../summary.json','w'),indent=1,default=list)
print(json.dumps(S['totals'],indent=1)); print(json.dumps(S['groups'],indent=1)); print(S['gov'])
for o in S['by-category']: print(f"{o['category']:48s} {o['usd_at_approval']/1e6:7.2f} {o['agentic_low_usd']/1e6:6.2f}-{o['agentic_high_usd']/1e6:6.2f}")
for o in S['by-year']: print(o)
C={r['key']:r for r in csv.DictReader(open(os.path.join(os.path.dirname(ASSUME),'cohort-assumptions.csv')))}
sw=[o for o in S['by-category'] if o['group']=='Software and infrastructure']
spend=sum(o['usd_at_approval'] for o in sw)
nonlab=sum(o['usd_at_approval']*(1-float(A[o['category']]['labour_share'])) for o in sw)
def cohort(s):
    g=lambda k:float(C[k][s])
    p=g('people')*g('cost_per_person_year_usd')*g('years'); i=g('people')*g('inference_per_person_year_usd')*g('years')
    return dict(people=p,inference=i,external_signoff=g('external_signoff_usd'),non_labour_from_data=nonlab,total=p+i+g('external_signoff_usd')+nonlab)
lo,hi=cohort('low'),cohort('high')
with open(f'{OUT}/data/cohort-scenario.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['line','low_usd','high_usd','source'])
    src={'people':'inputs/cohort-assumptions.csv','inference':'inputs/cohort-assumptions.csv','external_signoff':'inputs/cohort-assumptions.csv','non_labour_from_data':'approved software spend x (1 - labour share), inputs/model-assumptions.csv','total':'sum'}
    for k in lo: w.writerow([k,round(lo[k]),round(hi[k]),src[k]])
    w.writerow(['software_and_infrastructure_approved',round(spend),round(spend),'data/summary-by-category.csv'])
S['cohort']={'low':{k:round(v) for k,v in lo.items()},'high':{k:round(v) for k,v in hi.items()},'software_approved':round(spend),'software_labour_approved':round(spend-nonlab)}
json.dump(S,open(f'{OUT}/../summary.json','w'),indent=1,default=list)
print(S['cohort'])
