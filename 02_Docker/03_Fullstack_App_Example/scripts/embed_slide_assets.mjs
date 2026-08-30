import {readFileSync, writeFileSync} from 'node:fs';
import {resolve} from 'node:path';

const root = resolve(import.meta.dirname, '..');
const target = resolve(root, process.argv[2] || 'Fullstack_Gateway_Broker_Slides.html');

const files = {
  skillspace_exterior: ['media/generated/skillspace-exterior.png', 'image/png'],
  skillspace_training: ['media/generated/skillspace-training-room.png', 'image/png'],
  skillspace_lab: ['media/generated/skillspace-computer-lab.png', 'image/png'],
  github_seed_source: ['media/screenshots/github-seed-source.png', 'image/png'],
  github_initdb_folder: ['media/screenshots/github-initdb-folder.png', 'image/png'],

  v_req: ['media/remotion/out/requirement-journey-web.mp4', 'video/mp4'],
  v_req_poster: ['media/remotion/out/requirement-journey-poster.png', 'image/png'],

  ui_swagger_01: ['002_LAB_Build_The_API/images/ui-swagger-01-docs.png', 'image/png'],
  ui_swagger_02: ['002_LAB_Build_The_API/images/ui-swagger-02-dashboard.png', 'image/png'],
  ui_swagger_03: ['002_LAB_Build_The_API/images/ui-swagger-03-try-dashboard.png', 'image/png'],
  ui_swagger_04: ['002_LAB_Build_The_API/images/ui-swagger-04-execute-dashboard.png', 'image/png'],
  ui_swagger_05: ['002_LAB_Build_The_API/images/ui-swagger-05-dashboard-200.png', 'image/png'],
  ui_swagger_06: ['002_LAB_Build_The_API/images/ui-swagger-06-post-ticket.png', 'image/png'],
  ui_swagger_07: ['002_LAB_Build_The_API/images/ui-swagger-07-try-ticket.png', 'image/png'],
  ui_swagger_08: ['002_LAB_Build_The_API/images/ui-swagger-08-request-body.png', 'image/png'],
  ui_swagger_09: ['002_LAB_Build_The_API/images/ui-swagger-09-created.png', 'image/png'],

  ui_web_01: ['003_LAB_Build_The_Web/images/ui-web-01-overview.png', 'image/png'],
  ui_web_02: ['003_LAB_Build_The_Web/images/ui-web-02-tickets.png', 'image/png'],
  ui_web_03: ['003_LAB_Build_The_Web/images/ui-web-03-asset.png', 'image/png'],
  ui_web_04: ['003_LAB_Build_The_Web/images/ui-web-04-details.png', 'image/png'],
  ui_web_05: ['003_LAB_Build_The_Web/images/ui-web-05-priority.png', 'image/png'],
  ui_web_06: ['003_LAB_Build_The_Web/images/ui-web-06-submit.png', 'image/png'],
  ui_web_07: ['003_LAB_Build_The_Web/images/ui-web-07-new-card.png', 'image/png'],
  ui_web_08: ['003_LAB_Build_The_Web/images/ui-web-08-assignee.png', 'image/png'],
  ui_web_09: ['003_LAB_Build_The_Web/images/ui-web-09-assign.png', 'image/png'],
  ui_web_10: ['003_LAB_Build_The_Web/images/ui-web-10-assigned.png', 'image/png'],

  ui_net_01: ['004_LAB_Connect_Them/images/ui-net-01-overview.png', 'image/png'],
  ui_net_02: ['004_LAB_Connect_Them/images/ui-net-02-tickets.png', 'image/png'],
  ui_net_03: ['004_LAB_Connect_Them/images/ui-net-03-loans.png', 'image/png'],
  ui_net_04: ['004_LAB_Connect_Them/images/ui-net-04-parts.png', 'image/png'],
  ui_net_05: ['004_LAB_Connect_Them/images/ui-net-05-back.png', 'image/png'],

  ui_compose_01: ['005_LAB_Compose_And_Ship/images/ui-compose-01-overview.png', 'image/png'],
  ui_compose_02: ['005_LAB_Compose_And_Ship/images/ui-compose-02-tickets.png', 'image/png'],
  ui_compose_03: ['005_LAB_Compose_And_Ship/images/ui-compose-03-back-overview.png', 'image/png'],

  ui_hub_01: ['005_LAB_Compose_And_Ship/images/ui-hub-01-home.png', 'image/png'],
  ui_hub_02: ['005_LAB_Compose_And_Ship/images/ui-hub-02-username.png', 'image/png'],
  ui_hub_03: ['005_LAB_Compose_And_Ship/images/ui-hub-03-password.png', 'image/png'],
  ui_hub_04: ['005_LAB_Compose_And_Ship/images/ui-hub-04-avatar.png', 'image/png'],
  ui_hub_05: ['005_LAB_Compose_And_Ship/images/ui-hub-05-account-settings.png', 'image/png'],
  ui_hub_06: ['005_LAB_Compose_And_Ship/images/ui-hub-06-token-list.png', 'image/png'],
  ui_hub_07: ['005_LAB_Compose_And_Ship/images/ui-hub-07-description.png', 'image/png'],
  ui_hub_08: ['005_LAB_Compose_And_Ship/images/ui-hub-08-expiration.png', 'image/png'],
  ui_hub_09: ['005_LAB_Compose_And_Ship/images/ui-hub-09-permission.png', 'image/png'],
  ui_hub_10: ['005_LAB_Compose_And_Ship/images/ui-hub-10-generate.png', 'image/png'],
  ui_hub_11: ['005_LAB_Compose_And_Ship/images/ui-hub-11-copy.png', 'image/png'],
  ui_hub_12: ['005_LAB_Compose_And_Ship/images/ui-hub-12-revoke-menu.png', 'image/png'],
  ui_hub_13: ['005_LAB_Compose_And_Ship/images/ui-hub-13-revoke-delete.png', 'image/png'],
  ui_hub_14: ['005_LAB_Compose_And_Ship/images/ui-hub-14-revoke-confirm.png', 'image/png'],
  ui_hub_15: ['005_LAB_Compose_And_Ship/images/ui-hub-15-revoke-done.png', 'image/png'],

  ui_hub_push_01: ['005_LAB_Compose_And_Ship/images/ui-hub-push-01-repositories.png', 'image/png'],
  ui_hub_push_02: ['005_LAB_Compose_And_Ship/images/ui-hub-push-02-api.png', 'image/png'],
  ui_hub_push_03: ['005_LAB_Compose_And_Ship/images/ui-hub-push-03-api-tags.png', 'image/png'],
  ui_hub_push_04: ['005_LAB_Compose_And_Ship/images/ui-hub-push-04-web.png', 'image/png'],
  ui_hub_push_05: ['005_LAB_Compose_And_Ship/images/ui-hub-push-05-web-tags.png', 'image/png'],
};

const html = readFileSync(target, 'utf8');
const pattern = /<script id="assets">window\.ASSETS=(\{[\s\S]*?\});<\/script>/;
const match = html.match(pattern);
if (!match) throw new Error('ไม่พบบล็อก window.ASSETS ในสไลด์');

const assets = JSON.parse(match[1]);
for (const obsoleteKey of ['ui_github_01', 'ui_github_02', 'ui_github_03', 'ui_github_04']) {
  delete assets[obsoleteKey];
}
for (const [key, [relativePath, mime]] of Object.entries(files)) {
  const bytes = readFileSync(resolve(root, relativePath));
  assets[key] = `data:${mime};base64,${bytes.toString('base64')}`;
}

const replacement = `<script id="assets">window.ASSETS=${JSON.stringify(assets)};</script>`;
writeFileSync(target, html.replace(pattern, replacement));
console.log(`embedded ${Object.keys(files).length} assets into ${target}`);
