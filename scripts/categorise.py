import json,re,sys,csv,collections
d=json.load(open(sys.argv[1])); MAN={}
for r in csv.DictReader(open(sys.argv[2])): MAN[(r['network'],int(r['referendum']))]=r['category']
RULES=[
 ('Governance tooling', r'voting bot|proof of chaos|bounty manager'),
 ('Education and talent', r'encode'),
 ('Developer tooling and SDKs', r'substrate-api-client|python|reactive ?dot|faucet|debugger|regionx|fast sync|open communication layer|api gateways'),
 ('Marketing and media', r'polkaworld|aiweb3|polkadot insider|dotcast|news|x account|amplification|creadores|teachmedefi|live-streamer|substrate in bits|behind the code|chain of blocks'),
 ('Infrastructure operations', r'onfinality|network health'),
 ('Grants and incubation programmes', r'polkabiz'),
 ('Events and community', r'pulse|sanctuary|belgrade|safari|blockchain rio|discord risk'),
 ('Business development and partnerships', r'veles|kheopswap|pinkdrop|assetportal|cyborg|generative artists|texas blockchain|asset conversion'),
 ('Explorers, data and indexing', r'nominator insight|1kv insights|parasnaps|polkadot live|visualize polkadot'),
 ('Research', r'private transfers|redot'),
 ('Liquidity, loans and incentives', r'liquidity|loan|\blp\b|incentive program|incentives|airdrop|gigahydration|yield|money market|stellaswap|\bpool\b|lst|liquid staking|vdot|market mak|rwa'),
 ('Governance tooling', r'polkassembly|subsquare|opengov\.watch|opengov watch|dotreasury|governance (tool|platform|ui|app|dashboard)|delegat(e|ion) (dashboard|program|platform)|voting app|polkaassembly|subsocial|governance analytics|referendum (tracker|tool)|og tracker|opengov tracker|treasury guardian|decentralized voices|dv cohort|proof of personhood'),
 ('Explorers, data and indexing', r'subscan|statescan|explorer|indexer|indexing|subsquid|sqd|substrate-etl|dune|token terminal|polkaholic|analytics|dashboard|data partnership|messari|data platform|parity index|chain data|coinmarketcap|coingecko|defillama|artemis'),
 ('Wallets and user apps', r'wallet|subwallet|talisman|nova |nova wallet|polkadot\.js|polkadot-js|ledger|fearless|polkagate|enkrypt|mimir|signer|vault app|polkadot app|mobile app|super ?app|dapp'),
 ('Developer tooling and SDKs', r'sdk|papi|polkadot-api|chopsticks|paraspell|ink!|inkubator|ink |smart contract|tooling|subxt|apillon|developer (tool|experience)|dev ?tool|library|cli |zombienet|subway|orml|typink|dedot|pop cli|frame|asset transfer api|xcm (tools|sdk)|polkavm|revive|solidity|evm'),
 ('Core protocol and clients', r'gossamer|kagome|jam|fellowship|salary|polkadot host|runtime|bridge|snowbridge|hyperbridge|storage|bulletin|light client|smoldot|consensus|parachain(s)? (protocol|research)|protocol development|polkadot hub|hub launch|elastic scaling|coretime'),
 ('Infrastructure operations', r'\brpc|ibp|infrastructure builders|collator|paseo|testnet|node operat|boot ?node|validator program|relayer|archive node|hosting|server cost|monitoring|telemetry'),
 ('Security and audits', r'audit|assurance legion|\bpal\b|dotpal|security|bug bounty|ciso|openzeppelin|oak security|srlabs|pentest|white ?hat'),
 ('Education and talent', r'academy|\bpba\b|education|course|bootcamp|talent|university|student|curriculum|tutorial|workshop|school|learn|onboarding program|polkatalent'),
 ('Events and community', r'event|decoded|conference|meetup|hackathon|ambassador|community|moderation|summit|sub0|kbw|ethdenver|token2049|devcon|consensus 20|afterparty|party|meetups|dark prague|festival|tip\b|tipper|sub zero'),
 ('Marketing and media', r'marketing|sponsor|indy|indycar|racing|sports|campaign|advert|brand|media|content|podcast|documentary|film|video|influencer|x spaces|twitter|press|pr |kol|newsletter|magazine|social|music|heroic|esports|billboard|ads\b|youtube|tv|show'),
 ('Business development and partnerships', r'business development|\bbd\b|partnership|integration|listing|exchange|brave|mythical|mythos|games bounty|gaming|game|onramp|on-ramp|payments?|card|merchant|enterprise|institutional|the tie|adoption|launch on polkadot|chainflip|stablecoin|brale|bloque|virto|encointer|kreivo|usdc|usdt'),
 ('Grants and incubation programmes', r'grant|incubat|accelerat|relayers|ami bounty|fast-grants|rfp|bounty program|kusama vision|builders program|venture|prize|pioneers'),
 ('Legal, administration and treasury operations', r'legal|foundation|cayman|compliance|refund|reimburs|deposit|accounting|treasury report|administration|admin|budget|treasury management|custod|tax|kyc|pcf|community foundation|curator fee'),
 ('Research', r'research|futarchy|study|paper|economics|tokenomics|privacy|glove|zk|cryptograph'),
]
def cat(ch,i,title):
    if (ch,i) in MAN: return MAN[(ch,i)],'manual'
    t=' '+title.lower()+' '
    for c,rx in RULES:
        if re.search(rx,t): return c,'keyword'
    return 'Uncategorised','none'
for r in d['rows']:
    r['category'],r['category_method']=cat(r['network'],r['referendum'],r['title'])
ST={}
for o in csv.DictReader(open(sys.argv[4])): ST[(o['network'],int(o['referendum']))]=o
for r in d['rows']:
    o=ST.get((r['network'],r['referendum']))
    if o and (o['counted']=='no' or (o['counted']=='partial' and r['asset'] in ('USDC','USDT'))):
        r['payout_status']=o['payout_status']
    bad=any(x in r['payout_status'] for x in ('expired','voided','failed'))
    r['counted']='no' if bad else 'yes'
json.dump(d,open(sys.argv[3],'w'))
tot=collections.defaultdict(float); un=collections.defaultdict(float)
for r in d['rows']:
    if r['counted']=='yes': tot[r['category']]+=r['usd_at_approval'] or 0
for k,v in sorted(tot.items(),key=lambda x:-x[1]): print(f"{k:50s} {v/1e6:8.2f}m")
