# **nod: AI Spec Compliance Gatekeeper**

**nod** is a platform-agnostic, rule-based linter that ensures AI/LLM specifications contain critical security and compliance elements **before** any agentic or automated development begins.

## **🚀 The Core Philosophy: "The Final Nod"**

Automated agents and agentic workflows (like Ralph, AutoGPT, or custom CI/CD builders) are powerful but "compliance-blind." They build exactly what is in the specification.

**nod** ensures that the specification itself is legally and ethically sound before an agent ever touches it.

* **Agnostic Integration:** Works as a pre-requisite for *any* agentic development tool or manual coding process.  
* **Shift-Left Security:** Identifies missing risk assessments or oversight mechanisms at the design phase.  
* **Deterministic Guardrails:** Replaces vague human "vibes" with a strict, rule-based audit trail.

## **✨ Key Features**

* **Policy-as-Code:** Define your compliance standards in simple YAML.  
* **Gap Severity Model:** Categorizes issues as **CRITICAL**, **HIGH**, **MEDIUM**, or **LOW** to help security teams prioritize.  
* **Attestation Artifacts:** Generates a signed `nod-attestation.json` providing a tamper-proof audit trail of the design phase.  
* **Remote Rule Registry:** Point `nod` to a URL to always use the latest industry-standard rules (e.g., specific to your organization).  
* **Actionable Remediation:** Failures point directly to standardized templates to help developers fix gaps quickly.  
* **Agent-Friendly Output:** Generates remediation summaries formatted specifically for downstream LLMs to understand and potentially fix.

## **⚠️ Important Disclaimer**

**nod** verifies the *presence and alignment* of policy elements within a specification. It is a blueprint auditor; it does not guarantee the security of the final running code, which requires independent runtime auditing. A "green light" from **nod** means the **intent** matches the policy.

## **🛠️ Installation**

**nod** is a single-file Python tool. You can drop it directly into your repo or install it via your pipeline setup.

**Requirements:** Python 3.8+, `PyYAML`

```
pip install pyyaml
```

## **📖 Usage**

### **1\. Local Development (Check before you push)**

You can run **nod** directly on your laptop to audit drafts.

```
# Basic Scan
python nod.py specs/model-card.md --rules rules.yaml

# Strict Mode (Recommended)
# Ensures that required sections are not just present, but actually contain content.
python nod.py specs/model-card.md --rules rules.yaml --strict
```

### **2\. Local Git Hook (Automated Safety)**

Prevent yourself from pushing non-compliant specs by adding this to your `.git/hooks/pre-commit`:

```
#!/bin/sh
# .git/hooks/pre-commit
echo "Running nod compliance check..."
python nod.py specs/model-card.md --rules rules.yaml --strict --min-severity HIGH
```

### **3\. Enforcing Severity Gates**

You can control the "Gatekeeper" level. For example, block builds only on **HIGH** or **CRITICAL** issues, but allow **MEDIUM** gaps to pass with a warning:

```
python nod.py specs/model-card.md --min-severity HIGH
```

### **4\. Using Remote Rules (Plugin Architecture)**

Centralize your compliance logic by hosting the YAML file on a secure endpoint:

```
python nod.py specs/model-card.md --rules [https://security.my-org.com/ai-policy-v2.yaml](https://security.my-org.com/ai-policy-v2.yaml)
```

## **🤖 Downstream Agent Support**

**nod** generates a `nod-attestation.json` artifact. This file contains a `remediation_summary` field designed for Agentic AI.

**Example Scenario:**

1. **nod** fails a build because the "Human Oversight" section is missing.  
2. The pipeline passes the `nod-attestation.json` to an agent (like Ralph).  
3. The agent reads the summary: `"- [HIGH] Human Oversight: Describe how humans will monitor model decisions."`  
4. The agent prompts the user or attempts to draft the missing section based on the linked template.

## **⚙️ Configuration (`rules.yaml`)**

You can define multiple "Profiles" (e.g., EU AI Act, NIST, Corporate Policy) in one file.

```
profiles:
  eu_ai_act:
    badge_label: "EU AI Act Aligned"
    requirements:
      - id: "#+.*Risk Categorization"
        severity: "CRITICAL"
        remediation: "Define if the system is High-Risk under Annex III."
        template_url: "[https://example.com/templates/eu-risk-mapping.md](https://example.com/templates/eu-risk-mapping.md)"
    red_flags:
      - pattern: "biometric identification"
        severity: "CRITICAL"
        remediation: "High-risk biometric usage detected. Requires Legal approval."
```

## **🚦 CI/CD Integration (GitHub Actions)**

Add this to `.github/workflows/nod-audit.yml` to guard your main branch:

```
name: AI Compliance Gatekeeper
on: [pull_request]

jobs:
  compliance-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install pyyaml
      - name: Run nod
        run: |
          # Fails the build if HIGH or CRITICAL gaps are found
          python nod.py specs/ai-prd.md --rules rules.yaml --strict --min-severity HIGH
      - name: Upload Attestation
        uses: actions/upload-artifact@v4
        with:
          name: nod-attestation
          path: nod-attestation.json
```

## **🛡️ License**

Apache 2.0

