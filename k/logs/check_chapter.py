import re,os,json,sys,unicodedata
from urllib.parse import unquote
D,LG=sys.argv[1],sys.argv[2]; os.chdir(D); used=set()
for f in ['README.md','01_Theory/README.md','02_LAB/README.md']:
    s=open(f).read(); d=os.path.dirname(f)
    srcs=re.findall(r'<img[^>]+src="([^"]+)"',s)+re.findall(r'!\[[^\]]*\]\(([^)\s]+)',s)
    links=[x for x in re.findall(r'\]\(([^)#\s][^)\s]*)\)',s) if not x.startswith('[')]
    bad=[x for x in set(srcs+links) if not x.startswith('http') and not os.path.exists(os.path.normpath(os.path.join(d,x.split('#')[0])))]
    for x in srcs: used.add(os.path.normpath(os.path.join(d,x)))
    ids=set(re.findall(r'id="([^"]+)"',s)); heads=set()
    for h in re.findall(r'^#{1,6} (.+)$',s,flags=re.M):
        t=re.sub(r'[`*]','',h).strip().lower(); t=''.join(c for c in t if unicodedata.category(c)[0] in 'LMN' or c in ' -_'); heads.add(t.replace(' ','-'))
    miss=[a for a in re.findall(r'\]\(#([^)]+)\)',s) if unquote(a) not in ids|heads]
    leak=[w for w in ['2224','172.18.0.1','askpass','tuchsanai@','1300'] if w in s]
    print(f"  {f}: {len(s)//1024}KB imgs={len(srcs)} bad={bad} missing_anchor={len(miss)} leak={leak}")
allimgs={os.path.normpath(i['path'].split(D+'/')[1]) for i in json.load(open(f'../logs/{LG}/images.json'))}
print('  unused:',sorted(allimgs-used),' missing files:',[p for p in allimgs if not os.path.exists(p)])
