{{/* แม่พิมพ์ย่อยที่ใช้ซ้ำทุกไฟล์ (ไฟล์ขึ้นต้นด้วย _ ไม่ถูก render เป็น object) */}}

{{/* คำนำหน้าชื่อทุก object: fullnameOverride หรือชื่อ release (release som → som-web, som-db) */}}
{{- define "som-shop.fullname" -}}
{{- default .Release.Name .Values.fullnameOverride | trunc 40 | trimSuffix "-" -}}
{{- end -}}

{{/* ป้ายมาตรฐานที่ทุก object ควรมี */}}
{{- define "som-shop.labels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Values.web.image.tag | default .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
{{- end -}}

{{/* image ของหน้าร้าน: tag ว่าง = appVersion ของ chart */}}
{{- define "som-shop.webImage" -}}
{{ .Values.web.image.repository }}:{{ .Values.web.image.tag | default .Chart.AppVersion }}
{{- end -}}

{{/* รหัสฐานข้อมูล: --set db.password > Secret เดิมในคลัสเตอร์ (lookup) > error (required) */}}
{{- define "som-shop.dbPassword" -}}
{{- $old := lookup "v1" "Secret" .Release.Namespace (printf "%s-db-secret" (include "som-shop.fullname" .)) -}}
{{- if .Values.db.password -}}
{{- .Values.db.password -}}
{{- else if $old -}}
{{- index $old.data "POSTGRES_PASSWORD" | b64dec -}}
{{- else -}}
{{- required "ติดตั้งครั้งแรกต้องตั้งรหัสฐานข้อมูล: --set db.password=<รหัส>" .Values.db.password -}}
{{- end -}}
{{- end -}}
