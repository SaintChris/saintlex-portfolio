#!/bin/bash
# Build script: fetch OpenRouter stats and inject into portfolio
# Run this before deploying: ./scripts/build.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== Fetching OpenRouter live stats ==="
STATS_HTML=$(python3 "$SCRIPT_DIR/fetch_or_stats.py" 2>/dev/null)

if [ -z "$STATS_HTML" ]; then
    echo "ERROR: Failed to fetch OpenRouter stats. Using placeholder."
    STATS_HTML="<!-- OpenRouter stats unavailable -->"
fi

echo "=== Injecting stats into index.html ==="

# Create a marker-based injection
# We'll replace everything between the OR-START and OR-END markers
python3 -c "
import re
import sys

stats_html = '''$STATS_HTML'''

with open('$PROJECT_DIR/index.html', 'r') as f:
    content = f.read()

# Check if markers exist
if '<!-- OR-START -->' in content and '<!-- OR-END -->' in content:
    # Replace existing section
    pattern = r'<!-- OR-START -->.*?<!-- OR-END -->'
    replacement = '<!-- OR-START -->' + stats_html + '<!-- OR-END -->'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
else:
    # Insert before the contact section
    insert_marker = '<!-- ═══ 7. CONTACT ═══ -->'
    if insert_marker in content:
        content = content.replace(insert_marker, stats_html + '\n\n            ' + insert_marker)
    else:
        print('WARNING: Could not find insertion point. Appending before </main>.')
        content = content.replace('</main>', stats_html + '\n\n        </main>')

with open('$PROJECT_DIR/index.html', 'w') as f:
    f.write(content)

print('=== Build complete ===')
print('OpenRouter stats injected into index.html')
print('Deploy with: ./scripts/deploy.sh')
"
