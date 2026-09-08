#!/usr/bin/env python3
"""check-register.py <file>... — count colloquial Thai words outside code blocks. Exit = number of HARD hits (capped 99)."""
import re,sys,html as H
HARD={'นะ':r'(?<!สถา)(?<!ธรรม)(?<!ปัญ)นะ(?=[\s.,;:!?)\]]|$)','ล่ะ':r'ล่ะ','แหละ':r'แหละ','ซะ':r'ซะ(?=[\s.,)]|$)','ก็':r'ก็','แค่':r'แค่','เจอ':r'เจอ','งง':r'(?<![ก-๙])งง','ทาย':r'(?<!ท้า)ทาย(?!ที่|ทอด)','พัง':r'พัง','แล็บ':r'แล็บ','เช็กลิสต์':r'เช็กลิสต์','เก็บกวาด':r'เก็บกวาด','คุณ (สรรพนาม)':r'(?<![ก-๙])คุณ(?!สมบัติ|ภาพ|ลักษณะ|ค่า)','เรา':r'(?<![ก-๙])เรา(?![ก-๙])','ผม':r'(?<![ก-๙])ผม(?![ก-๙])','ตีสาม':r'ตีสาม','ใครจะ':r'ใครจะ','ยังไง':r'ยังไง','ทำไม':r'ทำไม','แอบดู':r'แอบดู','โอเค':r'โอเค','จริง ๆ':r'จริง ๆ','เอา':r'(?<![ก-๙])เอา(?![ก-๙])','มัน':r'(?<![ก-๙])มัน(?![ก-๙])','ตอนตี':r'ตอนตี','ทีนี้':r'ทีนี้','เดี๋ยว':r'เดี๋ยว','จะได้':r'จะได้(?!รับ|เรียน|เห็น)'}
SOFT={'ลอง':r'(?<!ทด)(?<!จำ)ลอง','ดู (กริยา)':r'(?<![ก-๙])ดู(?!แล)','สั่ง':r'(?<!คำ)สั่ง(?!การ)','รัน':r'(?<![ก-๙])รัน(?!ไทม์)','อะไร':r'อะไร','ไหม':r'(?<![ก-๙])ไหม(?![ก-๙])','ตัว (ลักษณนาม)':r'(?:Pod|container|Node|node|replica|Service)\s*\d*\s*ตัว','ตาย':r'(?<![ก-๙])ตาย','หาย':r'(?<![ก-๙])หาย(?!ใจ)','ขึ้น':r'(?<![ก-๙])ขึ้น(?![ก-๙])','เยอะ':r'เยอะ','นิดหน่อย':r'นิดหน่อย','โดน':r'(?<![ก-๙])โดน','ของที่':r'ของที่','อยากได้':r'อยากได้'}
def prose(t,f):
    if f.endswith('.html'):
        t=re.sub(r'<script.*?</script>|<style.*?</style>','',t,flags=re.S); t=re.sub(r'<pre.*?</pre>|<code.*?</code>','',t,flags=re.S); t=re.sub(r'<[^>]+>',' ',t); t=H.unescape(t)
    else:
        t=re.sub(r'```.*?```','',t,flags=re.S); t=re.sub(r'`[^`\n]*`','',t)
    return t
total=0
for f in sys.argv[1:]:
    t=prose(open(f,encoding='utf-8').read(),f); hard={k:len(re.findall(p,t)) for k,p in HARD.items()}; soft={k:len(re.findall(p,t)) for k,p in SOFT.items()}
    h=sum(hard.values()); total+=h
    print(f'{"FAIL" if h else "OK  "} {f}: HARD={h} {dict((k,v) for k,v in hard.items() if v)} · SOFT={sum(soft.values())} {dict((k,v) for k,v in soft.items() if v)}')
    if h:
        for k,p in HARD.items():
            for m in list(re.finditer(p,t))[:2]: print('      ',k,'→ …'+t[max(0,m.start()-40):m.end()+30].replace('\n',' ')+'…')
sys.exit(min(total,99))
