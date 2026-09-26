#!/usr/bin/env python3
"""Lossless crops of the real LAB 3 screenshots for README readability.

Source = host-captures/*.png (the genuine browser captures, byte-identical to the
full-size copies kept in 003_LAB_Docker_Build_Push/images/). Every crop is a pure
PIL .crop() of the original pixels saved as PNG: no resize, no redraw, no text edits.
Boxes were chosen by inspecting grid overlays (readability/inspect/) and measured
text rows (readability/rows.txt). Each crop is re-verified pixel-for-pixel below.
Box = (left, top, right, bottom) in original pixels.
"""
import hashlib, json, pathlib
from PIL import Image, ImageChops

W = pathlib.Path(__file__).resolve().parent.parent
SRC = W / 'host-captures'
IMG = W.parent.parent / '003_LAB_Docker_Build_Push' / 'images'
R = W / 'readability'

# stage pages: main = log panel left 1400 px, tail = right end of long command lines (overlaps main)
M = [
    # source, crop name, box, why
    ('jenkins-01-unlock', 'lab3_jenkins_01_unlock_crop', (1220, 15, 2220, 415), 'modal only; empty lower modal and grey backdrop dropped'),
    ('jenkins-02-signin', 'lab3_jenkins_02_signin_crop', (2160, 420, 2680, 830), 'sign-in form at native size; left artwork and empty right half dropped'),
    ('jenkins-03-dashboard', 'lab3_jenkins_03_dashboard_crop', (0, 0, 1540, 390), 'side menu + job row through Last Success column'),
    ('jenkins-09-plugins', 'lab3_jenkins_09_plugins_crop', (0, 0, 1100, 1244), 'plugin names/versions/descriptions; far-right Health/Enabled columns dropped'),
    ('jenkins-05-ssh-credential', 'lab3_jenkins_05_ssh_credential_crop', (1420, 200, 2020, 1050), 'Update credential modal at native size'),
    ('jenkins-06-dockerhub-credential', 'lab3_jenkins_06_dockerhub_credential_crop', (1420, 295, 2020, 955), 'Update credential modal at native size'),
    ('jenkins-04-credentials', 'lab3_jenkins_04_credentials_crop', (0, 0, 1100, 310), 'breadcrumb + both credential rows'),
    ('jenkins-08-new-pipeline', 'lab3_jenkins_08_new_pipeline_crop', (1270, 55, 2170, 1000), 'New Item form column'),
    ('jenkins-07-pipeline-config', 'lab3_jenkins_07_pipeline_config_crop', (0, 0, 1400, 1150), 'Configure menu + Pipeline section + script editor + Save'),
    ('jenkins-10-build-parameters', 'lab3_jenkins_10_build_parameters_crop', (0, 0, 1400, 860), 'job menu, build list, all 5 parameter fields + Build'),
    ('jenkins-11-build2-success', 'lab3_jenkins_11_build2_success_graph', (1020, 185, 2420, 280), 'stage graph Start..End'),
    ('jenkins-11-build2-success', 'lab3_jenkins_11_build2_success_log', (345, 312, 1745, 515), 'Post Actions log incl. full digest line (ends x=1602)'),
    ('stage-01-connect', 'lab3_stage_01_connect_crop', (345, 312, 1745, 800), 'log panel; every line ends before x=1343'),
    ('stage-02-clone', 'lab3_stage_02_clone_crop', (345, 312, 1745, 525), 'log panel left part'),
    ('stage-02-clone', 'lab3_stage_02_clone_tail', (930, 430, 1930, 470), 'right end of ssh line (ends x=1906)'),
    ('stage-03-build', 'lab3_stage_03_build_crop', (345, 312, 1745, 480), 'log panel left part'),
    ('stage-03-build', 'lab3_stage_03_build_tail', (880, 430, 1880, 468), 'right end of ssh line (ends x=1857)'),
    ('stage-04-test', 'lab3_stage_04_test_crop', (345, 312, 1745, 650), 'log panel; every line ends before x=1518'),
    ('stage-05-push', 'lab3_stage_05_push_crop', (345, 312, 1745, 800), 'log panel; every line ends before x=1492'),
    ('stage-06-clean', 'lab3_stage_06_clean_crop', (345, 312, 1745, 675), 'log panel left part'),
    ('stage-06-clean', 'lab3_stage_06_clean_tail', (1720, 430, 2900, 505), 'right end of ssh + line 0 (end x=2730/2873)'),
    ('stage-07-pull', 'lab3_stage_07_pull_crop', (345, 312, 1745, 480), 'log panel left part'),
    ('stage-07-pull', 'lab3_stage_07_pull_tail', (1320, 430, 2310, 468), 'right end of ssh line with DIGEST (ends x=2288)'),
    ('stage-08-deploy', 'lab3_stage_08_deploy_crop', (345, 312, 1745, 730), 'log panel left part'),
    ('stage-08-deploy', 'lab3_stage_08_deploy_tail', (1050, 430, 2050, 505), 'right end of ssh + line 0 (end x=2008/2026)'),
    ('jenkins-12-invalid-parameter', 'lab3_jenkins_12_invalid_parameter_graph', (1020, 185, 2420, 280), 'stage graph: Connect failed, rest skipped'),
    ('jenkins-12-invalid-parameter', 'lab3_jenkins_12_invalid_parameter_log', (0, 312, 1400, 740), 'stage list (skipped icons) + error log'),
    ('jenkins-13-missing-branch', 'lab3_jenkins_13_missing_branch_graph', (1020, 185, 2420, 280), 'stage graph: Clone failed, rest skipped'),
    ('jenkins-13-missing-branch', 'lab3_jenkins_13_missing_branch_log', (0, 312, 1400, 740), 'stage list + Clone log incl. fatal line'),
    ('jenkins-13-missing-branch', 'lab3_jenkins_13_missing_branch_tail', (1100, 430, 2120, 505), 'right end of ssh + line 0 (end x=1992/2095)'),
    ('github-01-source', 'lab3_github_01_source_crop', (500, 95, 1770, 680), 'breadcrumb + file table'),
    ('github-02-dockerfile', 'lab3_github_02_dockerfile_crop', (500, 95, 1770, 866), 'breadcrumb + Dockerfile lines 1-29'),
    ('hub-02-pushed-tags', 'lab3_hub_02_pushed_tags_crop', (690, 90, 1760, 905), 'repo header, filter, both tags with digest'),
    ('hub-03-image-digest', 'lab3_hub_03_image_digest_crop', (690, 90, 1760, 995), 'tag title, full manifest digest, layers'),
    ('app-01-version1', 'lab3_app_01_version1_chip', (1400, 0, 2000, 42), 'top bar version chip (full storefront still shown)'),
    ('app-03-version2', 'lab3_app_03_version2_chip', (1400, 0, 2000, 42), 'top bar version chip (full storefront still shown)'),
    ('app-04-build2-info', 'lab3_app_04_build2_info_left', (1505, 810, 2410, 1085), 'Deployment info column 1: Version/Git commit/Container'),
    ('app-04-build2-info', 'lab3_app_04_build2_info_right', (2410, 810, 3315, 1085), 'Deployment info column 2: Jenkins build/Built at/Health API'),
    ('@hub-pat-full', 'lab3_hub_04_pat_setup_crop', (760, 70, 1665, 600), 'Account settings menu (Personal access tokens) + Create access token form'),
]
# figure 9 source: host coordinator's real browser capture (JPEG bytes in a .png name), archived untouched in readability/;
# its decoded pixels are stored once as a real PNG full-size copy, crops come from those pixels
EXTRA = {'hub-pat-full': (R / 'hub-pat-full.png', IMG / 'lab3_hub_04_pat_setup.png')}
for orig, full in EXTRA.values():
    Image.open(orig).convert('RGB').save(full, optimize=True)

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest = []
for src, name, box, why in M:
    sp = EXTRA[src[1:]][1] if src.startswith('@') else SRC / f'{src}.png'
    im = Image.open(sp).convert('RGB')
    l, t, r, b = box
    assert 0 <= l < r <= im.width and 0 <= t < b <= im.height, (name, box, im.size)
    out = IMG / f'{name}.png'
    im.crop(box).save(out, optimize=True)
    back = Image.open(out).convert('RGB')
    assert ImageChops.difference(back, im.crop(box)).getbbox() is None, f'{name} not lossless'
    manifest.append({'crop': f'images/{name}.png', 'source': str(sp.relative_to(W.parent.parent)) if src.startswith('@') else f'host-captures/{src}.png', 'source_sha256': sha(sp),
                     'full_size_in_readme': f'images/{sp.name}' if src.startswith('@') else f'images/lab3_{src.replace("-", "_")}.png', 'box_ltrb': box,
                     'size': back.size, 'crop_sha256': sha(out), 'why': why})
    print(f'{name:48s} {back.size[0]}x{back.size[1]}  {why}')
(R / 'crop-manifest.json').write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + '\n')
print(len(manifest), 'crops, all pixel-identical to their source boxes')
