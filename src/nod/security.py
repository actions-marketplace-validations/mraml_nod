import os
import hmac
import hashlib
import json
import sys
from datetime import datetime
from typing import Dict, Any

def sign_attestation(attestation: Dict[str, Any]) -> None:
    """Signs the attestation using HMAC if key is present."""
    secret = os.environ.get("NOD_SECRET_KEY")
    if secret:
        payload = f"{attestation['aggregate_hash']}|{attestation['timestamp']}|{attestation['max_severity_gap']}"
        attestation["signature"] = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        attestation["signed"] = True
    else:
        attestation["signed"] = False

def freeze(policy_version: str, attestation: Dict[str, Any], path: str = "nod.lock") -> None:
    """Freezes the current compliance state to a lockfile."""
    lock = {
        "version": policy_version,
        "aggregate_hash": attestation.get("aggregate_hash"),
        "files": attestation.get("files_audited", []),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    if k := os.environ.get("NOD_SECRET_KEY"):
        p = f"{lock['aggregate_hash']}|{lock['timestamp']}"
        lock["signature"] = hmac.new(k.encode(), p.encode(), hashlib.sha256).hexdigest()

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(lock, f, indent=2)
        print(f"✅ Baseline frozen to {path}")
    except Exception as e:
        print(f"Error freezing: {e}", file=sys.stderr)
        sys.exit(1)

def verify(current_attestation: Dict[str, Any], path: str = "nod.lock") -> bool:
    """Verifies current state against the frozen lockfile."""
    if not os.path.exists(path):
        print(f"Error: {path} not found.", file=sys.stderr)
        return False
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            lock = json.load(f)

        if k := os.environ.get("NOD_SECRET_KEY"):
            if not (sig := lock.get("signature")):
                print("❌ Lockfile unsigned (Secret key present).")
                return False
            exp = hmac.new(k.encode(), f"{lock['aggregate_hash']}|{lock['timestamp']}".encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(sig, exp):
                print("❌ Signature Mismatch (Tampering detected).")
                return False
            print("🔒 Lockfile Signature Verified.")

        if current_attestation["aggregate_hash"] != lock.get("aggregate_hash"):
            print("❌ Verification Failed: Compliance Drift Detected.")
            return False

        print("✅ Verification Passed: No drift.")
        return True
    except Exception as e:
        print(f"Error verifying: {e}", file=sys.stderr)
        return False
