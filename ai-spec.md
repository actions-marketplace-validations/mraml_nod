# AI Project: MedScan - Radiology Assistant

> Policy Version: 1.8.0  
> Generated: January 14, 2026  
> Document Status: APPROVED

<!-- SOURCE: medical-ai-spec.md -->

---

## Risk Categorization

This system is categorized as **High-Risk** under EU AI Act Annex III, Article 6(2) as it is intended as a medical device within the meaning of Regulation (EU) 2017/745 for diagnostic purposes.

**Risk Justification:** The AI system provides diagnostic suggestions for medical imaging that could directly influence patient care decisions. While physicians maintain final authority, the system's recommendations may affect clinical judgment and patient outcomes.

**Mitigation:** All outputs require mandatory physician review before clinical action.

---

## Human Oversight Measures

A human reviewer (licensed radiologist) will audit 15% of all generated outputs via the admin dashboard on a weekly basis. All cases flagged as "low confidence" (<80%) are automatically escalated to senior physicians for review before results are shown to the ordering physician.

**Override Authority:** Physicians maintain full authority to override, modify, or dismiss any system recommendation. All overrides are logged with mandatory reason codes for continuous improvement analysis.

**Audit Trail:** Every prediction is logged with physician final decision, enabling retrospective analysis of AI vs. human agreement rates.

---

## Human Oversight Measures

### Primary Review Protocol
All diagnostic suggestions undergo mandatory review by licensed physicians before any clinical action. The system operates exclusively in advisory mode with zero autonomous decision-making authority.

### Audit Framework
- **Sampling Rate:** 15% of all outputs audited weekly via stratified random sampling
- **Auditors:** Board-certified radiologists from independent review panel (no development team members)
- **Methodology:** Blind comparison against gold-standard diagnoses from multi-reader consensus
- **Escalation:** Cases with severity discrepancy >2 levels trigger immediate senior physician review and potential model freeze

### Quality Assurance Dashboard
Real-time monitoring dashboard tracks:
- Inter-rater agreement between AI and physicians
- Override rates by department and shift
- Time-to-diagnosis metrics
- False negative rate for critical conditions

### Override Authority
All physicians can override system recommendations with mandatory reason code. System learns from override patterns to identify model drift.

---

## Technical Documentation

### Complete Documentation Repository
- **Architecture Diagrams:** `/docs/architecture/sentinel-system-design.pdf`
- **API Reference:** `https://api-docs.company.internal/sentinel/v1`
- **Model Cards:** `/docs/model-cards/` (detailed specifications for each neural network)
- **Runbook:** `https://wiki.company.com/sentinel/runbook`
- **Incident Response:** `https://wiki.company.com/sentinel/incident-response`

### Model Architecture Details
- **Ensemble Strategy:** Weighted voting (ResNet: 30%, EfficientNet: 35%, ViT: 35%)
- **Inference Pipeline:** Preprocessing → Model Ensemble → Calibration (Platt Scaling) → Confidence Thresholding
- **Hardware Requirements:** NVIDIA A100 GPU (40GB VRAM minimum)
- **Container Image:** `gcr.io/company/sentinel:v1.2.3` (signed with Cosign)

### Repository Links
- **Training Code:** `https://github.company.com/ai-team/sentinel-training`
- **Inference Service:** `https://github.company.com/ai-team/sentinel-api`
- **Data Pipeline:** `https://github.company.com/data-eng/sentinel-etl`

---

## PII Filtering

### Pre-Processing Redaction
Before any image reaches the model, a preprocessing pipeline strips personally identifiable information from DICOM headers:
- **Patient Name:** Replaced with anonymized ID (UUID)
- **MRN (Medical Record Number):** Hashed with HMAC-SHA256
- **Date of Birth:** Binned to 5-year age ranges
- **Address/Geocoding:** Truncated to 3-digit ZIP code

### Pattern-Based Scanning
All text outputs scanned for:
- **SSN:** Regex `\d{3}-\d{2}-\d{4}`
- **Credit Card Numbers:** Luhn algorithm validation
- **Email Addresses:** RFC 5322 compliant patterns

### De-identification Pipeline
All patient identifiers replaced with anonymized UUIDs before entering training pipeline. Mapping table stored in HIPAA-compliant secure enclave (AWS HealthLake).

---

## PII Filtering

### Automated Redaction
- **Pre-Inference:** DICOM headers stripped of patient name, MRN, DOB
- **Post-Inference:** Output JSON validated against schema to prevent PHI leakage
- **Logging:** All logs scrubbed of PII using Microsoft Presidio

### K-Anonymity
Geographic data generalized to zip code level with k-anonymity ≥ 1000 patients per zip code.

### Regular Expression Patterns
- SSN: `\d{3}-\d{2}-\d{4}` (blocked)
- Credit Card: Luhn algorithm validation (blocked)
- Email: RFC 5322 patterns (redacted in logs)

---

## PII Filtering

### Automated Redaction
All patient identifiers stripped from DICOM headers before model inference:
- Patient Name → Anonymized ID (SHA-256 hash)
- Medical Record Number → Pseudonymized ID (deterministic encryption)
- Date of Birth → Age bucket (<40, 40-60, 60-80, >80)

### Re-identification Risk
K-anonymity of at least 100 maintained for all exported datasets. Differential privacy noise (ε=1.0) applied to aggregate statistics.

### PII Detection
Automated scanning for 47 PII patterns (SSN, CCN, Email, Phone) using regex + NER models before any data egress.

---

## PII Filtering

### Redaction Layers
- **Pre-Processing:** DICOM headers scrubbed of patient names, MRNs, dates of birth
- **At-Rest Storage:** All PII encrypted separately from imaging data
- **Output Layer:** Final diagnosis reports undergo PII detection scan before rendering

### Detection Patterns
- SSN: `\d{3}-\d{2}-\d{4}`
- Credit Card: Luhn algorithm validation + regex
- Email: RFC 5322 compliant pattern matching
- Phone Numbers: E.164 format validation

### False Positive Handling
Medical Reference Numbers (MRNs) that resemble SSNs are allowlisted via hash-based exception list reviewed monthly.

---

## PII Filtering

### Pre-Processing Pipeline
All DICOM images pass through automated PII scrubbing:
1. **Header Redaction:** Patient names, MRNs removed from metadata
2. **OCR Scanning:** Tesseract OCR detects burned-in text annotations
3. **Anonymization:** Replace identifiers with consistent pseudonyms (HMAC-based)

### K-Anonymity
All reported aggregate statistics maintain k-anonymity ≥ 100 (i.e., any reported subgroup contains at least 100 patients).

### PII Detection
- Regex patterns for SSN: `\d{3}-\d{2}-\d{4}`
- Credit card numbers detected via Luhn algorithm
- Email addresses: RFC 5322 validation and redaction

### De-identification Standard
All datasets comply with HIPAA Safe Harbor method (18 identifiers removed).

---

## Encryption at Rest

All persistent data encrypted using **AES-256-GCM** with keys managed via AWS KMS.

### Covered Assets
- Model weights (`.pth` files)
- Training datasets (DICOM images)
- Inference logs (PostgreSQL)
- Vector embeddings (FAISS indices)

### Key Rotation
Encryption keys rotated every 180 days via automated AWS KMS key rotation policy.

---

## Encryption in Transit

All network communication secured with **TLS 1.3**:
- API Gateway → Backend Services
- Database connections (PostgreSQL with SSL)
- Inter-service mesh communication (Istio mTLS)
- External API endpoints (HTTPS only, HSTS enabled)

### Certificate Management
Certificates managed via AWS Certificate Manager with auto-renewal. Minimum 2048-bit RSA keys.

---

## Authentication Mechanisms

### User Authentication
- **Healthcare Providers:** SAML 2.0 SSO via hospital identity provider
- **Admin Users:** OAuth 2.0 with Multi-Factor Authentication (TOTP required)
- **Service Accounts:** mTLS certificate-based authentication

### Session Management
- JWT tokens with 15-minute expiration
- Refresh tokens rotated on use (30-day max lifetime)
- Secure, HttpOnly, SameSite cookies

---

## Authorization Policy

### Role-Based Access Control (RBAC)
| Role | Permissions |
|------|-------------|
| **Viewer** | Read-only access to diagnoses |
| **Physician** | Request diagnoses, view results, override recommendations |
| **Senior Physician** | All Physician + review low-confidence cases |
| **Admin** | User management, system configuration |
| **Data Scientist** | Model training, dataset access (de-identified only) |
| **Auditor** | Read-only access to all logs and audit trails |

### Principle of Least Privilege
All service accounts limited to minimum required permissions. Quarterly access reviews conducted.

---

## Secrets Management

### Strategy
- **Vault:** HashiCorp Vault for centralized secrets storage
- **Rotation:** Automatic 90-day rotation for API keys and database credentials
- **Injection:** Secrets injected at runtime via Kubernetes external-secrets-operator
- **No Hardcoding:** Static analysis (Gitleaks, TruffleHog) runs on every commit

### Encryption Keys
- **Master Keys:** AWS KMS with automatic rotation
- **Data Encryption Keys:** Generated per-object, wrapped by master key
- **Backup:** Key material backed up to offline HSM

---

## Audit Logging

### Logged Events
1. **Security Events:** Authentication attempts, authorization failures, privilege escalations
2. **Clinical Events:** Diagnosis requests, physician overrides, confidence threshold violations
3. **Administrative Events:** User creation/deletion, role changes, system configuration updates
4. **Data Events:** Training data access, model updates, dataset modifications

### Log Shipping
- **Destination:** Splunk Cloud (SOC 2 Type II certified)
- **Retention:** 7 years in compliance with HIPAA
- **Alerting:** Real-time alerts for critical events (failed logins >5 in 10 min, admin actions)

### Integrity Protection
Logs cryptographically signed with HMAC-SHA256. Immutable storage via AWS QLDB.

---

## Rate Limiting

### API Tier Limits
- **Physician Tier:** 1,000 requests/hour per user
- **Service Tier:** 10,000 requests/hour per service account
- **Public Health Check:** 100 requests/minute (unauthenticated)

### Throttling Strategy
- **Burst Allowance:** 2x sustained rate for 60 seconds
- **Backoff:** Exponential backoff with 429 responses
- **DDoS Protection:** AWS Shield Advanced with CloudFront

---

## Data Retention Policy

### Patient Data
- **Medical Imaging:** 7 years post-encounter (HIPAA requirement)
- **Diagnosis Records:** 10 years (state medical records law)
- **Audit Logs:** 7 years (regulatory compliance)

### Training Data
- **Identified Data:** Deleted after de-identification (60 days)
- **De-identified Data:** Permanent retention for research
- **Model Artifacts:** 10 years (regulatory traceability)

### Deletion Procedures
- **User Requests:** Right to deletion honored within 30 days (GDPR/CCPA)
- **Secure Deletion:** Cryptographic erasure (delete encryption keys), followed by overwriting

---

## Energy Consumption

### Carbon Footprint Analysis
- **Training (Sentinel v1.0):** Estimated 520 kWh = 234 kg CO₂e (using US grid average)
- **Inference:** 0.015 kWh per case = 0.0068 kg CO₂e
- **Annual Estimate (50K cases):** 340 kg CO₂e total

### Green AI Initiatives
- **Carbon-Aware Training:** Training scheduled during low-carbon grid hours (overnight, using ElectricityMaps API)
- **Model Compression:** 40% parameter reduction via pruning/quantization reduces inference energy by 35%
- **Renewable Energy:** Data center powered by 78% renewable energy (AWS renewable commitment)

### Monitoring
Real-time energy consumption tracked via NVIDIA NVML APIs and logged to sustainability dashboard.

---

## PII Filtering

### Pre-Processing Pipeline
1. **DICOM Header Scrubbing:** Remove patient name, MRN, date of birth before inference
2. **Regex-Based Detection:** Scan for SSN patterns (`\d{3}-\d{2}-\d{4}`), credit cards (Luhn validated)
3. **NER Model:** Named Entity Recognition detects person names, addresses, phone numbers
4. **Redaction:** Detected PII replaced with tokens (`[REDACTED_NAME]`, `[REDACTED_SSN]`)

### False Positive Handling
Medical terms (e.g., "John's disease") whitelisted. Manual review for ambiguous cases.

---

## Model Theft Protection

### Query Complexity Limits
- **Batch Size:** Max 20 images per request
- **Concurrent Requests:** Max 5 per API key
- **Query Fingerprinting:** Detect sequential probing patterns (e.g., incrementing patient IDs)

### Watermarking
- **Technique:** Proprietary embedding adds imperceptible noise to output probability distributions
- **Detection:** Forensic analysis can identify stolen model outputs with 98% confidence
- **Legal:** Watermark serves as proof of IP theft in litigation

### Model Obfuscation
- **Ensemble Diversity:** Three architecturally distinct models prevent single-point extraction
- **Output Perturbation:** Add random noise (σ=0.01) to confidence scores (preserves accuracy within 0.2%)

---

## Supply Chain Security

### Software Bill of Materials (SBOM)
Generated via Syft on every build. Includes:
- Base Docker images (provenance verified)
- Python packages (pinned versions with hashes)
- Pre-trained model weights (checksums verified)

### Vulnerability Scanning
- **Container Images:** Trivy scans daily
- **Python Dependencies:** Snyk scans on every commit
- **Threshold:** Zero critical, zero high-severity CVEs in production

### Vendor Verification
- **PyTorch:** Official checksums verified against torchvision releases
- **NVIDIA Drivers:** Signed by NVIDIA code-signing certificate
- **Third-Party Models:** Only ONNX/GGUF models from verified sources (Hugging Face Model Hub with >10K downloads)

---

## Cross-Reference Validation

This specification maintains strict traceability between threats and controls:

- **Threat T-001** (Adversarial Attack) is mitigated by **Control C-001** (Adversarial Detection)
- **Threat T-002** (Model Extraction) is mitigated by **Control C-002** (Rate Limiting & Watermarking)
- **Threat T-003** (Data Poisoning) is mitigated by **Control C-003** (Data Provenance & Multi-Party Approval)

All threats have corresponding controls. All controls trace back to specific threats or compliance requirements.

---

## Evidence and Documentation

Supporting documentation for this specification includes:

- [Architecture Diagram](./docs/architecture-diagram.pdf)
- [DPIA Report](./docs/DPIA-2025-12-15.pdf)
- [Fairness Audit Report](./docs/fairness-audit-Q4-2025.pdf)
- [Penetration Test Results](./docs/pentest-2025-12.pdf)
- [FDA 510(k) Submission](./docs/FDA-510k-draft.pdf)

---

## Version Control

**Specification Version:** 2.1.0  
**Last Updated:** January 14, 2026  
**Change Log:**
- v2.1.0: Added energy consumption analysis, enhanced PII filtering
- v2.0.0: Major revision for FDA submission compliance
- v1.5.0: Added cross-reference validation, threat modeling
- v1.0.0: Initial specification

**Document Hash (SHA-256):** `a3f5c9e2b8d1f4e7c0a9b3d6e8f1c4a7b9d2e5f8c1a4b7d0e3f6c9a2b5d8e1f4`

---

## Approval Signatures

| Role | Name | Signature | Date |
|------|------|-----------|------|
| **Chief AI Officer** | Dr. Sarah Chen | ✓ Approved | Jan 10, 2026 |
| **VP Engineering** | Mark Sullivan | ✓ Approved | Jan 12, 2026 |
| **General Counsel** | Jennifer Martinez | ✓ Approved | Jan 10, 2026 |
| **CISO** | Robert Kim | ✓ Approved | Jan 11, 2026 |

---

*This specification is a living document and will be updated as the Sentinel project evolves. All changes require approval from the Chief AI Officer and undergo legal review.*
