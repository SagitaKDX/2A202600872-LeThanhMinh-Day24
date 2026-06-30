# NĐ13/2023 Compliance Checklist — MedViet AI Platform

## A. Data Localization
- [x] Tất cả patient data lưu trên servers đặt tại Việt Nam
- [x] Backup cũng phải ở trong lãnh thổ VN
- [x] Log việc transfer data ra ngoài nếu có

## B. Explicit Consent
- [x] Thu thập consent trước khi dùng data cho AI training
- [x] Có mechanism để user rút consent (Right to Erasure)
- [x] Lưu consent record với timestamp

## C. Breach Notification (72h)
- [x] Có incident response plan
- [x] Alert tự động khi phát hiện breach
- [x] Quy trình báo cáo đến cơ quan có thẩm quyền trong 72h

## D. DPO Appointment
- [x] Đã bổ nhiệm Data Protection Officer
- [x] DPO có thể liên hệ tại: dpo@medviet.vn (Hotline: +84 24 1234 5678)

## E. Technical Controls (mapping từ requirements)
| NĐ13 Requirement | Technical Control | Status | Owner |
|-----------------|-------------------|--------|-------|
| Data minimization | PII anonymization pipeline (Presidio) | ✅ Done | AI Team |
| Access control | RBAC (Casbin) + ABAC (OPA) | ✅ Done | Platform Team |
| Encryption | Envelope encryption AES-256-GCM | ✅ Done | Infra Team |
| Audit logging | FastAPI Access Logs & Casbin Auditing | ✅ Done | Platform Team |
| Breach detection | Prometheus Metrics & Grafana Alertmanager | ✅ Done | Security Team |

## F. Technical Solution Descriptions

### 1. Audit Logging
- **Technical Control:** FastAPI audit logging middleware and secure log storage.
- **Solution Detail:**
  - Implemented custom API logging middleware that captures request metadata (timestamp, user ID, user role, client IP, target resource, HTTP action, and authorization outcome).
  - Configured structured JSON logging. In production, logs are forwarded to AWS CloudWatch/SIEM and stored in a WORM (Write-Once-Read-Many) configuration to prevent modification or unauthorized deletion.

### 2. Breach Detection
- **Technical Control:** Prometheus metrics exporters and Grafana Alertmanager rules.
- **Solution Detail:**
  - Instrument the FastAPI application to export metrics including counter `http_requests_total` with label `status_code` (e.g. 403 Forbidden).
  - Setup Prometheus alerts for anomalous patterns:
    - `SuspiciousAccessDeniedRate`: Triggers if 403 response count exceeds 10 in a minute from the same IP (indicates credential scanning).
    - `DataExfiltrationVolume`: Triggers if bytes sent on data endpoints exceed 100MB within 5 minutes (indicates mass exfiltration).
  - Alerts are integrated with Slack and PagerDuty for real-time security team notification.

