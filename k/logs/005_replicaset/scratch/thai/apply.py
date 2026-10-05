import json,re,sys,os
sys.path.insert(0,'/root/workspace/DevTools/k/logs/005_replicaset')
import imgcommon as c
from extract import parse, CH, K
THC="Thai text must be rendered exactly as given, correct Thai spelling, clear Thai font, no garbled glyphs"
TH=re.compile('[฀-๿]')
def write_md(items, title, path, ch):
    c.CH=ch; cc=c.CHAPTERS[ch]
    lines=["Generated with built-in image_gen via cyolo1 using 00-character-som.png as character reference","",
           f"# Final image prompts — {cc['title_th']} ({title})","",
           "ทุกภาพแนบ `01_Theory/images/00-character-som.png` เป็นภาพอ้างอิงตัวละครน้องส้ม",""]
    for it in items:
        nt=" · needs_test (สร้าง/ปรับหลังทดสอบ LAB จริง)" if it.get("needs_test") else ""
        lines+=[f"## {os.path.basename(it['path'])}","",f"> {it['id']} · {it['section']} — {it['caption_th']}{nt}","",
                "```text",it["prompt"],"```",""]
    open(path,'w',encoding='utf-8').write("\n".join(lines))
mode=sys.argv[1]  # check-md | apply
for ch,d in CH.items():
    c.CH=ch; root=c.CHAPTERS[ch]['root']
    jp=f'{K}/logs/{d}/images.json'; items=json.load(open(jp))
    if mode=='check-md':
        for kind,title,sub in [('T','Theory','01_Theory'),('L','LAB','02_LAB')]:
            p=f'{root}/{sub}/images/imagegen-prompts.md'; old=open(p).read()
            write_md([x for x in items if x['id'][0]==kind],title,f'{os.path.dirname(__file__) or "."}/_md_test',ch)
            print(ch,sub,'md matches' if open('_md_test').read()==old else 'MD DIFFERS')
        continue
    P=json.load(open(f'{ch}-patch.json'))
    ids0=[(x['id'],x['path']) for x in items]
    nchg=0
    for it in items:
        p=parse(it['prompt'],ch); q=P[it['id']]
        scene=q.get('scene',p['scene']); labels=q['labels']; extra=q['extra'].rstrip('. ')
        assert 1<=len(labels)<=7 and all(l.strip() for l in labels) and any(TH.search(l) for l in labels), it['id']
        if THC not in extra: extra=(extra+'; ' if extra else '')+THC
        new=c.prompt(" ".join(scene.split()),labels,extra,p['allow'])
        if 'caption_th' in q: it['caption_th']=q['caption_th']
        if new!=it['prompt']: nchg+=1
        it['prompt']=new
    assert [(x['id'],x['path']) for x in items]==ids0
    json.dump(items,open(jp,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
    write_md([x for x in items if x['id'][0]=='T'],'Theory',f'{root}/01_Theory/images/imagegen-prompts.md',ch)
    write_md([x for x in items if x['id'][0]=='L'],'LAB',f'{root}/02_LAB/images/imagegen-prompts.md',ch)
    print(ch,'prompts changed',nchg,'/',len(items))
