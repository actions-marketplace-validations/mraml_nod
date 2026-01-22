import os
import ssl
import sys
import urllib.request
from typing import Any, Dict, List
import yaml
import importlib.resources

# Security Constants
DEFAULT_TIMEOUT = 15.0
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_TOTAL_SIZE = 20 * 1024 * 1024 # 20MB
REGISTRY_BASE_URL = "https://raw.githubusercontent.com/mraml/nod-rules/main/library/"

def load_rules(sources: List[str]) -> Dict[str, Any]:
    """
    Loads and merges rules from multiple sources.
    Prioritizes user args > local defaults/ > package bundled defaults > rules.yaml
    """
    merged = {"profiles": {}, "version": "combined"}
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED

    def merge(new_data: Dict[str, Any]) -> None:
        if not new_data: return
        for profile, content in new_data.get("profiles", {}).items():
            if profile not in merged["profiles"]:
                merged["profiles"][profile] = content
            else:
                merged["profiles"][profile].update(content)

    # 1. If sources aren't provided, try to find defaults automatically
    if not sources:
        # Check local CWD 'defaults' folder first
        if os.path.isdir("defaults"):
            sources = ["defaults"]
        # Fallback to bundled package defaults
        elif importlib.resources.is_resource("nod", "defaults"):
             # For simplicity, we'll try to find the package path.
             try:
                 # Python 3.9+ pattern
                 pkg_path = importlib.resources.files("nod") / "defaults"
                 if pkg_path.is_dir():
                     sources = [str(pkg_path)]
             except Exception: pass
        
        # Final fallback
        if not sources and os.path.exists("rules.yaml"):
            sources = ["rules.yaml"]
    
    if not sources:
        # If we still have nothing, try to load bundled defaults explicitly
        try:
             pkg_path = importlib.resources.files("nod") / "defaults"
             if pkg_path.is_dir():
                 sources = [str(pkg_path)]
        except Exception: pass

    for source in sources:
        try:
            # Registry Shorthand
            if source.startswith("registry:"):
                rule_name = source.split("registry:", 1)[1]
                if not rule_name.endswith((".yaml", ".yml")): rule_name += ".yaml"
                source = REGISTRY_BASE_URL + rule_name
                print(f"Fetching from registry: {source}")

            # Remote URLs
            if source.startswith(("http://", "https://")):
                with urllib.request.urlopen(source, context=ssl_context, timeout=DEFAULT_TIMEOUT) as response:
                    merge(yaml.safe_load(response.read()))
            
            # Directories (Local or Bundled)
            elif os.path.isdir(source):
                for filename in sorted(os.listdir(source)):
                    if filename.endswith(('.yaml', '.yml')):
                        file_path = os.path.join(source, filename)
                        if os.path.getsize(file_path) > MAX_FILE_SIZE:
                            continue
                        with open(file_path, "r", encoding="utf-8") as f_in:
                            merge(yaml.safe_load(f_in))
            
            # Local Files
            elif os.path.exists(source):
                if os.path.getsize(source) > MAX_FILE_SIZE:
                    print(f"Error: Rule file {source} too large", file=sys.stderr); sys.exit(1)
                with open(source, "r", encoding="utf-8") as f:
                    merge(yaml.safe_load(f))
            else:
                # If explicit source passed but not found
                print(f"Error: Rule source not found: {source}", file=sys.stderr)
                sys.exit(1)

        except Exception as e:
            print(f"Error loading rules from {source}: {e}", file=sys.stderr)
            sys.exit(1)
            
    return merged

def load_ignore(path: str) -> List[str]:
    """Loads ignored rule IDs or file patterns from a file."""
    if os.path.exists(path):
        try:
            if os.path.getsize(path) <= 1024 * 1024:
                with open(path, "r", encoding="utf-8") as f:
                    return [line.strip() for line in f if line.strip() and not line.startswith("#")]
        except Exception: pass
    return []
