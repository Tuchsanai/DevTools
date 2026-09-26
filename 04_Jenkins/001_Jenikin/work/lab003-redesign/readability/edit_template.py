#!/usr/bin/env python3
"""One-off edit of README.tmpl.md: swap full-width screenshots for linked lossless crops (make_crops.py).

Each crop links to its untouched full-size capture; captions disclose the crop.
Idempotent guard: refuses to run twice. Figure 9 (Docker Hub) is left alone until the PAT capture arrives.
"""
import pathlib, re
W = pathlib.Path(__file__).resolve().parent.parent
p = W / 'README.tmpl.md'
t = p.read_text()
assert '_crop.png' not in t, 'template already edited'

TAG = 'ภาพหน้าจอจริงแบบครอป'
CLICK = ' — คลิกภาพเพื่อเปิดภาพเต็ม'
link = lambda alt, crop, full: f'[![{alt}](./images/{crop}.png)](./images/{full}.png)'

# full image file -> list of (alt suffix, crop file); order = display order
CROPS = {
    'lab3_github_01_source': [('', 'lab3_github_01_source_crop')],
    'lab3_github_02_dockerfile': [('', 'lab3_github_02_dockerfile_crop')],
    'lab3_jenkins_01_unlock': [('', 'lab3_jenkins_01_unlock_crop')],
    'lab3_jenkins_02_signin': [('', 'lab3_jenkins_02_signin_crop')],
    'lab3_jenkins_03_dashboard': [('', 'lab3_jenkins_03_dashboard_crop')],
    'lab3_jenkins_09_plugins': [('', 'lab3_jenkins_09_plugins_crop')],
    'lab3_jenkins_05_ssh_credential': [('', 'lab3_jenkins_05_ssh_credential_crop')],
    'lab3_jenkins_06_dockerhub_credential': [('', 'lab3_jenkins_06_dockerhub_credential_crop')],
    'lab3_jenkins_04_credentials': [('', 'lab3_jenkins_04_credentials_crop')],
    'lab3_jenkins_08_new_pipeline': [('', 'lab3_jenkins_08_new_pipeline_crop')],
    'lab3_jenkins_07_pipeline_config': [('', 'lab3_jenkins_07_pipeline_config_crop')],
    'lab3_jenkins_10_build_parameters': [('', 'lab3_jenkins_10_build_parameters_crop')],
    'lab3_jenkins_11_build2_success': [(' — กราฟ stage', 'lab3_jenkins_11_build2_success_graph'), (' — log Post Actions', 'lab3_jenkins_11_build2_success_log')],
    'lab3_stage_01_connect': [('', 'lab3_stage_01_connect_crop')],
    'lab3_stage_02_clone': [('', 'lab3_stage_02_clone_crop'), (' — ท้ายบรรทัด ssh', 'lab3_stage_02_clone_tail')],
    'lab3_stage_03_build': [('', 'lab3_stage_03_build_crop'), (' — ท้ายบรรทัด ssh', 'lab3_stage_03_build_tail')],
    'lab3_stage_04_test': [('', 'lab3_stage_04_test_crop')],
    'lab3_stage_05_push': [('', 'lab3_stage_05_push_crop')],
    'lab3_stage_06_clean': [('', 'lab3_stage_06_clean_crop'), (' — ท้ายบรรทัด ssh', 'lab3_stage_06_clean_tail')],
    'lab3_stage_07_pull': [('', 'lab3_stage_07_pull_crop'), (' — ท้ายบรรทัด ssh', 'lab3_stage_07_pull_tail')],
    'lab3_stage_08_deploy': [('', 'lab3_stage_08_deploy_crop'), (' — ท้ายบรรทัด ssh', 'lab3_stage_08_deploy_tail')],
    'lab3_app_04_build2_info': [(' — คอลัมน์ซ้าย', 'lab3_app_04_build2_info_left'), (' — คอลัมน์ขวา', 'lab3_app_04_build2_info_right')],
    'lab3_hub_02_pushed_tags': [('', 'lab3_hub_02_pushed_tags_crop')],
    'lab3_hub_03_image_digest': [('', 'lab3_hub_03_image_digest_crop')],
    'lab3_jenkins_12_invalid_parameter': [(' — กราฟ stage', 'lab3_jenkins_12_invalid_parameter_graph'), (' — log Connect', 'lab3_jenkins_12_invalid_parameter_log')],
    'lab3_jenkins_13_missing_branch': [(' — กราฟ stage', 'lab3_jenkins_13_missing_branch_graph'), (' — log Clone', 'lab3_jenkins_13_missing_branch_log'), (' — ท้ายบรรทัด ssh', 'lab3_jenkins_13_missing_branch_tail')],
}
# storefront: keep the full screenshot (layout is the point), add the chip crop under it
CHIP = {'lab3_app_01_version1': 'lab3_app_01_version1_chip', 'lab3_app_03_version2': 'lab3_app_03_version2_chip'}

# extra sentence appended to the caption, explains multi-part crops
NOTE = {
    'lab3_jenkins_11_build2_success': ' ภาพบนคือกราฟ stage ภาพล่างคือ log ของ Post Actions จากภาพหน้าจอเดียวกัน',
    'lab3_jenkins_12_invalid_parameter': ' ภาพบนคือกราฟ stage ภาพล่างคือรายการ stage และ log จากภาพหน้าจอเดียวกัน',
    'lab3_jenkins_13_missing_branch': ' ภาพบนคือกราฟ stage ภาพกลางคือรายการ stage และ log ภาพล่างคือท้ายบรรทัดคำสั่งยาวจากภาพหน้าจอเดียวกัน (ซ้อนกับภาพกลางบางส่วน)',
    'lab3_app_04_build2_info': ' ภาพซ้าย/ขวาของตาราง Deployment ถูกแยกเป็นสองภาพ บน = คอลัมน์ซ้าย ล่าง = คอลัมน์ขวา',
}
TAIL = ' · ภาพล่างคือท้ายบรรทัดคำสั่งยาวจากภาพหน้าจอเดียวกัน (ซ้อนกับภาพบนบางส่วน)'

def caption_after(t, pos):
    m = re.compile(r'\n\n(\*ภาพที่ \d+ [^\n]*\*)\n').match(t, pos)
    assert m, t[pos:pos + 200]
    return m

n = 0
for full, parts in CROPS.items():
    m = re.search(r'^!\[([^\]]*)\]\(\./images/' + full + r'\.png\)$', t, re.M); assert m, full
    alt = m.group(1)
    block = '\n\n'.join(link(alt + suf, crop, full) for suf, crop in parts)
    c = caption_after(t, m.end()); cap = c.group(1)
    if '(ภาพหน้าจอจริง' in cap:
        i = cap.index('(ภาพหน้าจอจริง'); j = cap.index(')', i)
        cap = cap[:i] + '(' + TAG + cap[i + len('(ภาพหน้าจอจริง'):j] + CLICK + cap[j:]
    else:  # stage figures 18-25 had no tag
        cap = re.sub(r'^\*ภาพที่ (\d+) ', lambda k: f'*ภาพที่ {k.group(1)} ({TAG}{CLICK}) ', cap)
    extra = NOTE.get(full, TAIL if any(c.endswith('_tail') for _, c in parts) else '')
    cap = cap[:-1] + extra + '*'
    t = t[:m.start()] + block + '\n\n' + cap + '\n' + t[c.end():]; n += 1

for full, chip in CHIP.items():
    m = re.search(r'^!\[([^\]]*)\]\(\./images/' + full + r'\.png\)$', t, re.M); assert m, full
    alt = m.group(1)
    block = f'[![{alt}](./images/{full}.png)](./images/{full}.png)\n\n{link("chip เวอร์ชันบนแถบด้านบน (ครอป)", chip, full)}'
    c = caption_after(t, m.end()); cap = c.group(1)
    cap = cap.replace('(ภาพหน้าจอจริง)', '(ภาพหน้าจอจริง ภาพบนเต็มจอ ภาพล่างครอปเฉพาะ chip จากภาพเดียวกัน' + CLICK + ')')
    assert 'ครอปเฉพาะ chip' in cap, cap
    t = t[:m.start()] + block + '\n\n' + cap + '\n' + t[c.end():]; n += 1

# plugins caption: the capture is the alphabetical head of Installed plugins, not a Pipeline-only view
old = 'plugin กลุ่ม Pipeline ที่ติดตั้งจากชุด suggested plugins*'
assert old in t; t = t.replace(old, 'ส่วนต้นของหน้า Installed plugins (เรียงตามชื่อ) หลังติดตั้งชุด suggested plugins*')

old = '| `images/` | แผนภาพประกอบ 2 ภาพ (`lab3_diagram_*`) และภาพหน้าจอจริงจากรอบทดสอบ |'
assert old in t
t = t.replace(old, '| `images/` | แผนภาพประกอบ 2 ภาพ (`lab3_diagram_*`) และภาพหน้าจอจริงจากรอบทดสอบ — ไฟล์ที่ลงท้าย `_crop`, `_tail`, `_graph`, `_log`, `_chip`, `_left`, `_right` คือส่วนที่ตัดออกจากภาพเต็มชื่อเดียวกันแบบพิกเซลตรงตัว (ไม่ย่อ ไม่แก้ไขเนื้อหา) เพื่อให้อ่านตัวอักษรได้ ภาพเต็มยังอยู่ครบและเปิดได้ด้วยการคลิกภาพใน README |')
p.write_text(t)
print('edited', n, 'figures')
