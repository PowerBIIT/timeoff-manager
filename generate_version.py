#!/usr/bin/env python3
"""Generate version file with git commit hash"""
import subprocess
import json

try:
    commit_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
    commit_date = subprocess.check_output(['git', 'log', '-1', '--format=%cd', '--date=short']).decode('ascii').strip()
    branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode('ascii').strip()
    
    version_info = {
        'commit': commit_hash,
        'date': commit_date,
        'branch': branch
    }
    
    with open('version.json', 'w') as f:
        json.dump(version_info, f, indent=2)
    
    print(f"✅ Version file generated: {commit_hash} ({branch})")
except Exception as e:
    print(f"⚠️  Could not generate version: {e}")
    # Fallback version
    with open('version.json', 'w') as f:
        json.dump({'commit': 'unknown', 'date': 'unknown', 'branch': 'unknown'}, f)
