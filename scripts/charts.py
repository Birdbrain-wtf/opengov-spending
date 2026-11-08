import csv,sys,collections
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
OUT=sys.argv[1]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.edgecolor':'#c9c8c2','axes.labelcolor':'#52514e','xtick.color':'#52514e','ytick.color':'#52514e'})
INK='#0b0b0b'; SURF='#fcfcfb'
C={'Software and infrastructure':'#2a78d6','People, judgement and reach':'#eb6834','Capital deployed':'#1baf7a'}
rows=list(csv.DictReader(open(f'{OUT}/data/summary-by-group-year.csv')))
years=sorted({r['year'] for r in rows}); groups=list(C)
v={(r['group'],r['year']):float(r['usd_at_approval'])/1e6 for r in rows}
fig,ax=plt.subplots(figsize=(10,5.6),facecolor=SURF); ax.set_facecolor(SURF)
bottom=[0]*len(years)
for g in groups:
    h=[v.get((g,y),0) for y in years]
    ax.bar(years,h,bottom=bottom,color=C[g],width=0.6,edgecolor=SURF,linewidth=2,label=g)
    bottom=[b+x for b,x in zip(bottom,h)]
for i,t in enumerate(bottom): ax.text(i,t+2,f"${t:,.1f}m",ha='center',va='bottom',color=INK,fontsize=11)
ax.set_ylabel('US$ million at the price on the day of approval')
for s in ['top','right']: ax.spines[s].set_visible(False)
ax.yaxis.grid(True,color='#ebeae6'); ax.set_axisbelow(True)
ax.legend(frameon=False,loc='upper right')
ax.set_title('Kusama and Polkadot OpenGov treasury spending, by year',loc='left',color=INK,fontsize=14,pad=14)
fig.text(0.01,0.01,'2026 runs to 8 November. Kusama from 2022, Polkadot from June 2023. Source: Subsquare API, OKX daily index prices.',fontsize=8.5,color='#52514e')
fig.tight_layout(rect=(0,0.03,1,1)); fig.savefig(f'{OUT}/charts/spend-by-year.png',dpi=160); plt.close(fig)

cats=list(csv.DictReader(open(f'{OUT}/data/agentic-cost-model.csv')))
cats.sort(key=lambda r:float(r['usd_at_approval']))
fig,ax=plt.subplots(figsize=(10,7.4),facecolor=SURF); ax.set_facecolor(SURF)
y=range(len(cats))
hist=[float(r['usd_at_approval'])/1e6 for r in cats]; lo=[float(r['agentic_low_usd'])/1e6 for r in cats]; hi=[float(r['agentic_high_usd'])/1e6 for r in cats]
ax.barh([i+0.2 for i in y],hist,height=0.36,color='#9a9890',edgecolor=SURF,linewidth=2,label='Approved, 2022 to 2026')
ax.barh([i-0.2 for i in y],hi,height=0.36,color=[C[r['group']] for r in cats],edgecolor=SURF,linewidth=2,label='Same work today, upper estimate')
for i,(a,b,c) in enumerate(zip(hist,lo,hi)): ax.text(max(a,c)+0.6,i,f"${a:,.1f}m  ->  ${b:,.1f}m to ${c:,.1f}m",va='center',fontsize=9,color=INK)
ax.set_yticks(list(y)); ax.set_yticklabels([r['category'] for r in cats],fontsize=9.5)
ax.set_xlabel('US$ million'); ax.set_xlim(0,max(hist)*1.55)
for s in ['top','right']: ax.spines[s].set_visible(False)
ax.xaxis.grid(True,color='#ebeae6'); ax.set_axisbelow(True)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color='#9a9890',label='Approved, 2022 to 2026'),Patch(color=C['Software and infrastructure'],label='Today, upper estimate: software and infrastructure'),Patch(color=C['People, judgement and reach'],label='Today, upper estimate: people, judgement and reach'),Patch(color=C['Capital deployed'],label='Today: capital deployed (unchanged)')],frameon=False,loc='lower right',fontsize=9)
ax.set_title('What the same work might cost with agentic development',loc='left',color=INK,fontsize=14,pad=14)
fig.text(0.01,0.01,'Second edition. Birdbrain assumptions, not measurements: labour share x share of labour that remains. See data/agentic-cost-model.csv.',fontsize=8.5,color='#52514e')
fig.tight_layout(rect=(0,0.03,1,1)); fig.savefig(f'{OUT}/charts/cost-today-by-category.png',dpi=160); plt.close(fig)
print('ok')
