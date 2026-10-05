#!/usr/bin/env python3
"""Apply post-test fixes to logs/<LG>/images.json and rewrite imagegen-prompts.md (does NOT run build_images.py).
usage: patch_storyboard.py <LG> <chapter_number> <patch.json>
patch.json: {"replace": {"ID": [[old,new],...]}, "caption": {"ID": "..."}}"""
import json,sys,os
LG,CHN,PF=sys.argv[1:4]
here=os.path.join(os.path.dirname(os.path.abspath(__file__)),LG); sys.path.insert(0,here)
import imgcommon as ic; ic.configure(CHN)
P=os.path.join(here,'images.json'); d=json.load(open(P)); pt=json.load(open(PF))
for i in d:
    for a,b in pt.get('replace',{}).get(i['id'],[]):
        assert a in i['prompt'],(i['id'],a[:40]); i['prompt']=i['prompt'].replace(a,b)
        core=a.strip('"\'')
        if len(core)>=3 and core in i['prompt'] and core not in b:
            print(f"WARNING {i['id']}: old text {core!r} still appears elsewhere in the prompt (Scene/Constraints?)")
    if i['id'] in pt.get('caption',{}): i['caption_th']=pt['caption'][i['id']]
json.dump(d,open(P,'w'),ensure_ascii=False,indent=2)
c=ic.CHAPTERS[ic.CH]
ic.write_md([i for i in d if i['id'][0]=='T'],"Theory",f"{c['root']}/01_Theory/images/imagegen-prompts.md")
ic.write_md([i for i in d if i['id'][0]=='L'],"LAB",f"{c['root']}/02_LAB/images/imagegen-prompts.md")
print('patched',len(pt.get('replace',{})),'prompts,',len(pt.get('caption',{})),'captions')
