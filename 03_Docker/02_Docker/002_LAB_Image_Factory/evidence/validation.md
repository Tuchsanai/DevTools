# Validation evidence

ทดสอบจริงวันที่ 2026-08-12 ด้วย Docker BuildKit และ Playwright CLI

```text
build #2: WORKDIR / RUN adduser / COPY => CACHED
{"status": "ok"}
health=healthy
image=devtools/image-factory:1.0.0
user=app
uid=10001(app) gid=101(app)
OCI label version=1.0.0
same_image=yes after changing APP_THEME / APP_STAGE
```

ภาพ: `images/actual-image-factory.png`

