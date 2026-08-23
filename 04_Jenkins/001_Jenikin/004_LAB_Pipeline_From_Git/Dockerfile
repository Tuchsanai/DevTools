FROM nginx:1.29-alpine

ARG VCS_REF=unknown
ARG BUILD_DATE=unknown
ARG SOURCE_URL=unknown
LABEL org.opencontainers.image.title="hello-ci" \
      org.opencontainers.image.description="LAB Pipeline from Git deterministic web artifact" \
      org.opencontainers.image.source="$SOURCE_URL" \
      org.opencontainers.image.revision="$VCS_REF" \
      org.opencontainers.image.created="$BUILD_DATE"

COPY app/index.html /usr/share/nginx/html/index.html
COPY hello.sh /usr/local/bin/hello-ci-test
RUN chmod 0755 /usr/local/bin/hello-ci-test \
    && /usr/local/bin/hello-ci-test | grep -Fx 'Hello from GitHub'

EXPOSE 80
HEALTHCHECK --interval=10s --timeout=2s --retries=3 \
  CMD wget -qO- http://127.0.0.1/ | grep -Fq 'Pipeline จาก GitHub' || exit 1
CMD ["nginx", "-g", "daemon off;"]
