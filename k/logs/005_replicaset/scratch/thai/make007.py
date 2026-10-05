import json
items={x['id']:x for x in json.load(open('007-items.json'))}
P={}
def keep(i): P[i]={'labels':items[i]['labels'],'extra':items[i]['extra']}
def S(i,labels,extra): P[i]={'labels':labels,'extra':extra}
def add(i,lab,pos,at_end=True):
    L=list(items[i]['labels']); L=L+[lab] if at_end else [lab]+L
    S(i,L,items[i]['extra']+'; '+pos)
def rep(i,pairs,extra_pairs=None,addlab=None,addpos=None):
    L=list(items[i]['labels']); E=items[i]['extra']
    for a,b in pairs:
        L=[b if l==a else l for l in L]; E=E.replace("'"+a+"'","'"+b+"'")
    for a,b in (extra_pairs or []): assert a in E,(i,a); E=E.replace(a,b)
    if addlab: L.append(addlab); E+='; '+addpos
    S(i,L,E)

add('T01','เปลี่ยนรุ่นเอง ร้านสะดุด',"'เปลี่ยนรุ่นเอง ร้านสะดุด' is a smaller subtitle directly below the title banner")
rep('T02',[('no history','ไม่มีประวัติรุ่น')])
S('T03',['อุปมาในบทนี้']+items['T03']['labels'],"'อุปมาในบทนี้' is the board title at the top; below it exactly six rows and each row has exactly one of the six labels 'Deployment', 'pod-template-hash', 'RollingUpdate', 'Recreate', 'rollout history', 'rollout undo' in that order; the shutters, sticker and signboard icons carry no text")
rep('T04',[('ReplicaSet (old) 0','ReplicaSet รุ่นเก่า 0'),('ReplicaSet (new) 3','ReplicaSet รุ่นใหม่ 3')],
    [('supervisor labels as listed under each supervisor robot',"'Deployment: web' on the manager robot; 'ReplicaSet รุ่นเก่า 0' under the faded left supervisor robot; 'ReplicaSet รุ่นใหม่ 3' under the bright right supervisor robot")])
add('T05','แก้ RS ตรง ๆ ไม่ได้',"'แก้ RS ตรง ๆ ไม่ได้' is a title banner at the top")
rep('T06',[('strategy','strategy (วิธีเปลี่ยนรุ่น)')],
    [('exactly seven field lines',"exactly seven field lines in this order: 'replicas', 'selector', 'template', 'strategy (วิธีเปลี่ยนรุ่น)', 'minReadySeconds', 'revisionHistoryLimit', 'progressDeadlineSeconds'")])
add('T07','ไม่แตะคลัสเตอร์',"'ไม่แตะคลัสเตอร์' on a small tag hanging on the dotted line to the control tower")
add('T08','อ่านคอลัมน์ get deploy',"'อ่านคอลัมน์ get deploy' is the scoreboard title above the three headers")
add('T09','hash แยกรุ่นไม่ปนกัน',"'hash แยกรุ่นไม่ปนกัน' is a title banner at the top")
rep('T10',[('revision +1','เกิด revision ใหม่')])
rep('T11',[(f'old {a} / new {b}',f'เก่า {a} / ใหม่ {b}') for a,b in [(3,0),(3,1),(2,1),(2,2),(1,2),(1,3),(0,3)]],
    [('exactly one of the seven labels on its left in the listed order',"exactly one of the seven labels on its left in the listed order, from 'เก่า 3 / ใหม่ 0' at the top to 'เก่า 0 / ใหม่ 3' at the bottom")])
rep('T12',[('maxSurge 25% → 3 (max 13)','maxSurge 25% → 3 (สูงสุด 13)'),('maxUnavailable 25% → 2 (min 8)','maxUnavailable 25% → 2 (ต่ำสุด 8)'),
           ('replicas: 3 → +1 / -0','replicas: 3 → +1 / -0'),],
    [("the side card has the two 'replicas: 3' and 'replicas: 4' lines","the side card has the two lines 'replicas: 3 → +1 / -0' and 'replicas: 4 → +1 / -1'")])
rep('T13',[('OPEN','เปิดขาย'),('CLOSED','ปิดร้าน')])
add('T14','db ต้องมีตัวเดียว',"'db ต้องมีตัวเดียว' is a title banner across the top above both panels")
add('T15','รอไฟเขียวก่อน',"'รอไฟเขียวก่อน' in a small speech bubble from the manager robot's raised hand")
add('T16','ตั้ง probe ให้ถูก',"'ตั้ง probe ให้ถูก' as the right panel heading")
add('T17','ลำดับการปิด Pod',"'ลำดับการปิด Pod' is a title banner at the top above the timeline")
add('T18','ปิดบูธเก่าแบบไม่สะดุด',"'ปิดบูธเก่าแบบไม่สะดุด' is a title banner at the top")
add('T19','รุ่นใหม่ค้าง ร้านยังขาย',"'รุ่นใหม่ค้าง ร้านยังขาย' is a title banner at the top")
add('T20','ต้องสั่งย้อนรุ่นเอง',"'ต้องสั่งย้อนรุ่นเอง' is a title banner at the top")
add('T21','สมุดบันทึกรุ่น',"'สมุดบันทึกรุ่น' on the logbook spine")
add('T22','ลืม annotate ข้อความซ้ำ',"'ลืม annotate ข้อความซ้ำ' beside the small warning triangle")
add('T23','ย้อนรุ่น = revision ใหม่',"'ย้อนรุ่น = revision ใหม่' is a title banner at the top")
keep('T24')
S('T25',items['T25']['labels']+['แก้หลายอย่าง รุ่นเดียว'],"'kubectl rollout pause' on the pause sign; 'kubectl rollout resume' on the resume sign; each change card has exactly one of 'image', 'env', 'resources'; 'แก้หลายอย่าง รุ่นเดียว' on the single combined rollout arrow")
S('T26',items['T26']['labels']+['ไว้ใช้ย้อนรุ่น','ย้อนรุ่นไม่ได้'],items['T26']['extra']+"; 'ไว้ใช้ย้อนรุ่น' on a small tag on the shelf of sleeping robots; 'ย้อนรุ่นไม่ได้' under the inset's empty shelf")
rep('T27',[],[("'kubectl apply -f' on the folder","'kubectl apply -f' on the folder with 'แนะนำ' next to its check mark"),
              ('exactly five buttons, each with one of the first five labels',"exactly five buttons, each with one of 'kubectl set image', 'kubectl set env', 'kubectl scale', 'kubectl edit', 'kubectl patch'")],
    'แนะนำ',"no other text on the buttons")
add('T28','ไฟล์ชนะ',"'ไฟล์ชนะ' is a title banner at the top")
keep('T29'); keep('T30')
add('T31','อาการ rollout พัง',"'อาการ rollout พัง' is a title banner at the top")
add('T32','สลับทีเดียว',"'สลับทีเดียว' is a title banner at the top")
add('T33','แบ่งลูกค้าลองรุ่นใหม่',"'แบ่งลูกค้าลองรุ่นใหม่' is a title banner at the top")
keep('T34')
S('T35',['สรุปคำสั่ง']+items['T35']['labels'],"'สรุปคำสั่ง' is the board title at the top; below it exactly six rows, each row has exactly one of 'kubectl set image', 'kubectl scale', 'rollout status', 'rollout history', 'rollout undo', 'rollout restart' in the listed order; icons carry no text")
add('T36','เรื่องต่อไป',"'เรื่องต่อไป' is a small banner above the four chests")
add('L01','เตรียมคลัสเตอร์',"'เตรียมคลัสเตอร์' is a title banner at the top")
add('L02','Deployment แรก',"'Deployment แรก' is a title banner at the top")
keep('L03')
add('L04','เก่าลด ใหม่เพิ่ม',"'เก่าลด ใหม่เพิ่ม' is a title banner at the top")
add('L05','คำตอบปนกันช่วงสั้น',"'คำตอบปนกันช่วงสั้น' is a title banner at the top")
rep('L06',[('rollout history','ประวัติรุ่น (history)')])
add('L07','ได้ revision เดียว',"'ได้ revision เดียว' on the single new logbook page in the left scene")
S('L08',['Pod สูงสุด / Ready ต่ำสุด']+items['L08']['labels'],"'Pod สูงสุด / Ready ต่ำสุด' is the title at the top; exactly three lanes, each with exactly one of 'rolling.yaml: max 5, min 3', 'nosurge.yaml: max 4, min 3', 'recreate.yaml: min 0' at its left in that order")
add('L09','rollout ค้าง',"'rollout ค้าง' is a heading above the right scene")
add('L10','image ผิด ร้านยังขาย',"'image ผิด ร้านยังขาย' is a title banner at the top")
rep('L11',[('no preStop','ไม่มี preStop')])
add('L12','Deployment รับเลี้ยง RS',"'Deployment รับเลี้ยง RS' is a title banner at the top")
S('L13',items['L13']['labels']+['สลับทั้งชุด','ลองรุ่นใหม่บางส่วน'],items['L13']['extra']+"; 'สลับทั้งชุด' is the left half heading; 'ลองรุ่นใหม่บางส่วน' is the right half heading")
add('L14','ร้านน้องส้มโปรดักชัน',"'ร้านน้องส้มโปรดักชัน' is a title banner at the top of the map")
add('L15','ยังไม่มีผู้จัดการร้าน',"'ยังไม่มีผู้จัดการร้าน' in a thought bubble above Nong Som")
add('L16','รับเลี้ยงด้วย Deployment',"'รับเลี้ยงด้วย Deployment' is a title banner at the top")
keep('L17'); keep('L18'); keep('L19')
add('L20','รุ่นพัง ร้านยังขาย',"'รุ่นพัง ร้านยังขาย' is a title banner at the top")
keep('L21')
add('L22','db ลืมข้อมูล',"'db ลืมข้อมูล' is a title banner at the top")
keep('L23')

def q(L): return ', '.join("'"+l+"'" for l in L)
P['T09']['extra']=P['T09']['extra'].replace("each hash label appears once on its robot's blueprint sticker","'pod-template-hash=6f58b8bd67' appears once on the first robot's blueprint sticker and 'pod-template-hash=7c987cc6b4' once on the second robot's blueprint sticker")
P['T11']['extra']="exactly seven rows, each row has exactly one of the seven labels on its left in this order from top to bottom: "+q(P['T11']['labels'])+"; the booth counts in each row match its label exactly; never more than four booths in one row; awnings carry no text"
P['T21']['extra']=P['T21']['extra'].replace("exactly three rows with the three row labels","exactly three rows reading "+q(P['T21']['labels'][2:5])+" from top to bottom")
P['T34']['extra']="exactly four rows and each row has exactly one of the four labels in this order: "+q(P['T34']['labels'])+"; no other text in the cells"
P['T36']['extra']=P['T36']['extra'].replace("exactly four chests, each with exactly one of the four labels","exactly four chests, each with exactly one of "+q(P['T36']['labels'][:4]))
P['L23']['extra']="exactly six rows: five ticked rows with "+q(P['L23']['labels'][:5])+" in order, and the unticked bottom row with 'db ยังลืมข้อมูล'"
for i in P: assert P[i]['extra']
assert set(P)==set(items),set(items)^set(P)
for i,p in P.items(): assert len(p['labels'])<=7,i
json.dump(P,open('007-patch.json','w'),ensure_ascii=False,indent=1)
print(sum(P[i]['labels']!=items[i]['labels'] for i in P),'changed')
