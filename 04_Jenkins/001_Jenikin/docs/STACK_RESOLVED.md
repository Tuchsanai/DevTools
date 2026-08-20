# Stack resolved — Phase 5 GitHub contract

Resolved and verified on **2026-08-20 (UTC)**. Base Jenkins/Docker measurements came from the clean `devtools-jk0` chain; the Phase 5 GitHub relay and reconnect proof came from `devtools-jk-lab` with Jenkins `20080→8080` and webapp `20800→8000`.

## Image resolution

| Image | Resolved digest / image ID | Verified role |
|---|---|---|
| `tuchsanai/devtools:2569_1` | `sha256:d8050fe96efdfa8c716b3c0e2d6d092afc73fb610143a92d13a5063f5d29b858` | Outer DinD lab environment |
| `jenkins/jenkins:lts-jdk21` | `sha256:8547df3b0db2803d158ecc9499207a056bb30c23fddc18bb5b4a4dc14e77dd09` | Jenkins **2.568.2** base |
| `deltaprojects/smee-client@sha256:20ea24c8c81bb3f3aa332c8939503e3c5bee048bb5a98ba2249d73a41a556e33` | `sha256:20ea24c8c81bb3f3aa332c8939503e3c5bee048bb5a98ba2249d73a41a556e33` | GitHub webhook relay; smee-client **1.2.2**, Node **v14.15.0**, `linux/amd64` only |
| `python:3.12-slim` | `sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a` | LAB 3 smoke image base |
| `jenkins-bootstrap-u0:2569` | local image `sha256:7d621d329f05e823cad732390b1942c8c0f25e0c29a0617b43af465fb7ac45f8` | Frozen suggested plugins + skip-wizard Groovy init |
| `jenkins-docker:2569` | local image `sha256:ad52d02280f2ea1dd7c5b5f7d84f4ecf2298e9b7b038b705d0abe43bd187ba5c` | Jenkins base + Docker CLI **29.7.2** |

The custom-image values are local content IDs from the final clean build; upstream values are pulled repository digests. There is no local registry image or container.

## Runtime versions

- Jenkins: `2.568.2`
- Docker CLI inside Jenkins: `29.7.2`
- Generic Webhook Trigger: `2.4.2` and active
- smee-client CLI: `1.2.2`; Node: `v14.15.0`; image architecture: **amd64-only** (`linux/amd64`, accepted classroom risk)

## External API and relay contract

| Interface | Locked version / authentication | Runtime result |
|---|---|---|
| GitHub REST API | `X-GitHub-Api-Version: 2022-11-28`; PAT classic scopes `public_repo` + `admin:repo_hook` | Authenticated helper checks `/user`, repository and hook state without logging the token |
| smee relay | `smee-hello` / `smee-webapp`, one channel and token per repository, `--restart unless-stopped` on `cicd-net` | Restart test exit 0: args/channel unchanged, `Connected` count advanced to 2, and the following push produced exactly one successful build ([`logs/U-P5-5.log`](../logs/U-P5-5.log)) |

## Active Jenkins plugins

The real wizard installed 92 suggested plugins. LAB 5 added Generic Webhook Trigger, giving 93 active plugins in the resolved LAB 5 state.

```text
count=93
ant:520.vd082ecfb_16a_9
antisamy-markup-formatter:173.v680e3a_b_69ff3
apache-httpcomponents-client-4-api:4.5.14-269.vfa_2321039a_83
asm-api:9.10.1-216.va_9256d3b_844b_
bootstrap5-api:5.3.8-1048.va_c299057e35c
bouncycastle-api:2.30.1.84-291.v9f17b_21896e2
branch-api:2.1280.v0d4e5b_b_460ef
build-timeout:1.41
caffeine-api:3.2.4-208.v7e2da_a_7db_82b_
checks-api:415.vf022234a_931d
cloudbees-folder:6.1106.v3a_d9a_6d2465e
commons-lang3-api:3.20.0-109.ve43756e2d2b_4
commons-text-api:1.15.0-218.va_61573470393
credentials-binding:728.v902a_273b_8947
credentials:1511.v2e3cb_0008ef0
dark-theme:652.vea_da_dfea_e769
display-url-api:2.217.va_6b_de84cc74b_
durable-task:686.v80ff80875b_82
echarts-api:6.1.0-1306.vcee1648c16a_4
eddsa-api:0.3.0.1-29.v67e9a_1c969b_b_
email-ext:2038.v7b_8817a_499d9
font-awesome-api:7.3.1-1013.v0835a_879ec6d
generic-webhook-trigger:2.4.2
git-client:6.6.1
git:5.10.1
github-api:1.330-492.v3941a_032db_2a_
github-branch-source:1983.vfa_27ed961853
github:1.47.0
gradle:2.19.1252.v15196b_5a_6e10
gson-api:2.14.0-201.v8eefe5515533
instance-identity:203.v15e81a_1b_7a_38
ionicons-api:94.vcc3065403257
jackson-annotations2-api:2.22-19.v10a_a_582ea_26e
jackson2-api:2.22.1-443.vc91f592333c4
jackson3-api:3.2.2-96.v599957900a_1a_
jakarta-activation-api:2.1.4-1
jakarta-mail-api:2.1.5-1
jakarta-xml-bind-api:4.0.9-19.v2b_a_5b_44d9a_1c
javax-activation-api:1.2.0-8
jaxb:2.3.9-143.v5979df3304e6
jjwt-api:0.13.0-141.vd58b_a_9592b_6c
joda-time-api:2.14.3-200.v65623733c99f
jquery3-api:3.7.1-687.v68d468e40b_30
json-api:20260814-226.v20f9685d642c
json-path-api:3.0.0-218.vcd4dd1355de2
jsoup:1.23.1-103.v4fde9422cc6f
junit:1422.v580465cc5d44
ldap:807.809.vd3a_4e5e4ec98
mailer:534.v1b_36f5864073
matrix-auth:3.3
matrix-project:905.vcc6831e8760a_
mina-sshd-api-common:2.19.0-192.v2b_a_7b_2c1dc71
mina-sshd-api-core:2.19.0-192.v2b_a_7b_2c1dc71
okhttp-api:5.3.2-200.vedb_720a_cf1f8
pipeline-build-step:599.v4b_67ea_11b_152
pipeline-github-lib:65.v203688e7727e
pipeline-graph-view:998.vc30deece0e36
pipeline-groovy-lib:798.v5cc688825312
pipeline-input-step:560.v56198a_642157
pipeline-milestone-step:152.v6e22b_8cfc66c
pipeline-model-api:2.2293.v6e7193cec599
pipeline-model-definition:2.2293.v6e7193cec599
pipeline-model-extensions:2.2293.v6e7193cec599
pipeline-stage-step:345.va_96187909426
pipeline-stage-tags-metadata:2.2293.v6e7193cec599
plain-credentials:199.v9f8e1f741799
plugin-util-api:7.1341.v039f146993d9
prism-api:1.30.0-741.v034eb_0b_0a_a_fa_
resource-disposer:0.25
scm-api:728.vc30dcf7a_0df5
script-security:1412.v7737b_3405f86
snakeyaml-api:2.5-149.v72471e9c6371
snakeyaml-engine-api:3.1.1-12.v4320c7d6f89c
ssh-credentials:372.va_250881b_08cd
ssh-slaves:3.1097.v868116049892
structs:362.va_b_695ef4fdf9
theme-manager:346.v06cca_64c6a_37
timestamper:1.30
token-macro:477.vd4f0dc3cb_cf1
trilead-api:2.284.v1974ea_324382
variant:70.va_d9f17f859e0
woodstox-core-api:7.2.2-10.vcb_629759b_2c2
workflow-aggregator:608.v67378e9d3db_1
workflow-api:1413.v2ff1a_5e720fa_
workflow-basic-steps:1098.v808b_fd7f8cf4
workflow-cps:4370.v49a_6937566b_6
workflow-durable-task-step:1479.v56e587f413a_7
workflow-job:1590.v49101d088542
workflow-multibranch:841.vec5b_9e1806ec
workflow-scm-step:466.va_d69e602552b_
workflow-step-api:724.v538c2362b_dfb_
workflow-support:1015.v785e5a_b_b_8b_22
ws-cleanup:0.49
```

The 92 suggested-plugin entries are frozen verbatim in `tools/bootstrap/plugins.txt`; `generic-webhook-trigger:2.4.2` is installed by `up_to_lab5.sh`.

## Docker Hub proof

| Repository | Visibility | Proof from final clean chain |
|---|---|---|
| `tuchsanai/ci-demo` | public | Jenkins build `docker-build-push #1` logged `Login Succeeded`, pushed tag `1`, and `docker manifest inspect docker.io/tuchsanai/ci-demo:1` exited 0; manifest digest `sha256:4dc3c925fda216ec6e429db5d06348a4345e57fd43790d996bbb71beefcf9dbd` |

The repository was created idempotently through Docker Hub API v2 when absent. Credentials were supplied only through `DOCKER_USER`/`DOCKER_TOKEN`; the token is not recorded here or in the verification log.

## Measured elapsed times

| Operation | Elapsed |
|---|---:|
| Pull Jenkins base for the real wizard | 12.9 s |
| Real Jenkins wizard + suggested plugins + freeze list | 135.3 s |
| Final clean `up_to_lab1.sh` | 42.1 s |
| Final clean `up_to_lab2.sh` | 11.3 s |
| Final clean `up_to_lab3.sh` including Hub push | 44.4 s |
| Phase 5 relay restart/reconnect test | about 10 s |

Base-stack commands and timings are in `logs/U0.log`. Phase 5 image pull/bootstrap evidence is in `logs/U-P5-1.log`; relay restart/reconnect and the subsequent exactly-one-build proof are in `logs/U-P5-5.log`.
