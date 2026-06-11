#!/bin/bash
# Deploy script: fetch stats, optionally skip, and push
# Usage: ./scripts/deploy.sh [--skip-stats]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Fetch and inject stats unless --skip-stats is passed
if [[ "$1" != "--skip-stats" ]]; then
    echo "=== Fetching OpenRouter stats ==="
    if OPENROUTER_MANAGEMENT_KEY="$(grep OPENROUTER_MANAGEMENT_KEY /Users/saint/.env 2>/dev/null | cut -d= -f2-)" python3 "$SCRIPT_DIR/fetch_or_stats.py" 2>/dev/null > /tmp/or_stats.html; then
        echo "=== Injecting stats ==="
        python3 -c "
import re
with open('/tmp/or_stats.html', 'r') as f:
    stats_html = f.read()
with open('index.html', 'r') as f:
    content = f.read()
pattern = r'<!-- OR-START -->.*?<!-- OR-END -->'
replacement = '<!-- OR-START -->' + stats_html + '<!-- OR-END -->'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)
with open('index.html', 'w') as f:
    f.write(content)
print('Stats injected.')
"
    else
        echo "WARNING: Could not fetch stats. Proceeding with existing content."
    fi
else
    echo "=== Skipping stats fetch (--skip-stats) ==="
fi

# Commit and push
echo "=== Committing ==="
git add -A
if git diff --cached --quiet; then
    echo "No changes to commit."
else
    git commit -m "update: portfolio deploy $(date '+%Y-%m-%d %H:%M')"
fi

echo "=== Pushing to origin/main ==="
git push origin main

echo "=== Deploy complete ==="
echo "Site should update at https://saintlex.sbs in a few minutes."
