import re
s=open('check.py').read()
s=s.replace("re.sub(r'```.*?```', '', text, flags=re.S)","re.sub(r'^```.*?^```', '', text, flags=re.S | re.M)")
s=s.replace("re.findall(r'```yaml\\n(.*?)```', text, re.S)","re.findall(r'^```yaml\\n(.*?)^```', text, re.S | re.M)")
s=s.replace("'ASKPASS', '13001', 'agent'","'ASKPASS', 'agent'")
s=s.replace("""for w in ['NodePort', 'Deployment', 'ReplicaSet', 'DaemonSet', 'Ingress']:
    for m in re.finditer(r'\\b' + w + r'\\b', lab_wo):""","""lab_wo2 = lab_wo.replace('["Ingress"]', '').replace('Policy Types: Ingress', '')
for w in ['NodePort', 'Deployment', 'ReplicaSet', 'DaemonSet', 'Ingress']:
    for m in re.finditer(r'\\b' + w + r'\\b', lab_wo2):""")
open('check.py','w').write(s)
l=open('lab3.md').read()
a=l.index('ส่วนสำคัญของ `som-shop.yaml`'); b=l.index('- **ไม่มี `metadata.namespace`**')
l=l[:a]+re.sub(r'^( *)\.\.\.$', r'\1# ... (ตัด)', l[a:b], flags=re.M)+l[b:]
open('lab3.md','w').write(l)
