import {readFileSync, writeFileSync} from 'node:fs';
import {resolve} from 'node:path';

const root = resolve(import.meta.dirname, '..');
const target = resolve(root, process.argv[2] || 'Fullstack_Slides.html');

// Only assets used by the current 45-slide, two-lab deck belong here.
const files = {
  skillspace_exterior: ['media/generated/skillspace-exterior.png', 'image/png'],
  skillspace_training: ['media/generated/skillspace-training-room.png', 'image/png'],
  skillspace_lab: ['media/generated/skillspace-computer-lab.png', 'image/png'],
  ui_web_01: ['002_LAB_Docker_Compose/images/ui-web-01-overview.png', 'image/png'],
  ui_web_02: ['002_LAB_Docker_Compose/images/ui-web-02-tickets.png', 'image/png'],
  ui_web_05: ['002_LAB_Docker_Compose/images/ui-web-05-priority.png', 'image/png'],
  ui_web_06: ['002_LAB_Docker_Compose/images/ui-web-06-submit.png', 'image/png'],
  ui_web_07: ['002_LAB_Docker_Compose/images/ui-web-07-new-card.png', 'image/png'],
  ui_web_08: ['002_LAB_Docker_Compose/images/ui-web-08-assignee.png', 'image/png'],
  ui_web_10: ['002_LAB_Docker_Compose/images/ui-web-10-assigned.png', 'image/png'],
  loans: ['002_LAB_Docker_Compose/images/ui-loans.png', 'image/png'],
  parts: ['002_LAB_Docker_Compose/images/ui-parts.png', 'image/png'],
};

const html = readFileSync(target, 'utf8');
const pattern = /<script id="assets">window\.ASSETS=(\{[\s\S]*?\});<\/script>/;
const match = html.match(pattern);
if (!match) throw new Error('ไม่พบบล็อก window.ASSETS ในสไลด์');

const assets = {};
for (const [key, [relativePath, mime]] of Object.entries(files)) {
  const bytes = readFileSync(resolve(root, relativePath));
  assets[key] = `data:${mime};base64,${bytes.toString('base64')}`;
}

const replacement = `<script id="assets">window.ASSETS=${JSON.stringify(assets)};</script>`;
writeFileSync(target, html.replace(pattern, replacement));
console.log(`embedded ${Object.keys(files).length} assets into ${target}`);
