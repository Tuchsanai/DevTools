import json,re,sys,os
sys.path.insert(0,'/root/workspace/DevTools/k/logs/005_replicaset')
import imgcommon as c
K='/root/workspace/DevTools/k'
CH={'005':'005_replicaset','006':'006_service','007':'007_deployment'}
OUT=os.path.dirname(os.path.abspath(__file__))
def parse(p,ch):
    lines=p.split('\n')
    assert lines[-2].startswith('Text (verbatim') and lines[-1].startswith('Constraints: '),lines[-2][:40]
    m=re.match(r'Text \(verbatim, exactly (\d+) short label instances; a label listed twice appears exactly twice\): (.*)\.$',lines[-2])
    n=int(m.group(1)); labels=re.findall(r'"((?:[^"\\]|\\.)*)"',m.group(2))
    assert len(labels)==n,(n,labels)
    cons=lines[-1][len('Constraints: '):]
    pre=c.BASE_CONS+c.LATER[ch]
    allow=False
    if cons.startswith(pre): rest=cons[len(pre):]
    elif cons.startswith(c.BASE_CONS): rest=cons[len(c.BASE_CONS):]; allow=True
    else: raise Exception('cons')
    assert rest.endswith('.')
    rest=rest[:-1]
    extra=rest[2:] if rest.startswith('; ') else rest
    assert not rest or rest.startswith('; ')
    scene=[l for l in lines if l.startswith('Scene: ')][0][7:]
    return dict(head=lines[:-2],labels=labels,extra=extra,allow=allow,scene=scene)
if __name__=='__main__':
    for ch,d in CH.items():
        items=json.load(open(f'{K}/logs/{d}/images.json'))
        out=[]
        for it in items:
            p=parse(it['prompt'],ch)
            # roundtrip check
            c.CH=ch
            assert c.prompt(p['scene'],p['labels'],p['extra'],p['allow'])==it['prompt'],it['id']
            out.append(dict(id=it['id'],file=os.path.basename(it['path']),section=it['section'],caption_th=it['caption_th'],scene=p['scene'],labels=p['labels'],extra=p['extra']))
        json.dump(out,open(f'{OUT}/{ch}-items.json','w'),ensure_ascii=False,indent=1)
        print(ch,len(out))
