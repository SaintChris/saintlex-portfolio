#!/usr/bin/env python3
"""Fetch OpenRouter activity data and generate live stats for portfolio."""

import json
import subprocess
import sys
from datetime import datetime

def get_key():
    """Get OpenRouter management key from env or .env file."""
    import os
    key = os.environ.get('OPENROUTER_MANAGEMENT_KEY')
    if key:
        return key
    # Fallback: read from .env file
    try:
        with open('/Users/saint/.env', 'r') as f:
            for line in f:
                if line.strip().startswith('OPENROUTER_MANAGEMENT_KEY='):
                    return line.strip().split('=', 1)[1]
    except FileNotFoundError:
        pass
    raise ValueError("OPENROUTER_MANAGEMENT_KEY not found in env or .env file")

def fetch_activity(key):
    import urllib.request
    url = "https://openrouter.ai/api/v1/activity"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())

def fetch_auth(key):
    import urllib.request
    url = "https://openrouter.ai/api/v1/auth/key"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())

def aggregate(data):
    """Aggregate activity data into portfolio-ready stats."""
    total_requests = 0
    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_reasoning_tokens = 0
    total_usage_cost = 0.0
    models_used = set()
    daily = {}

    for entry in data:
        reqs = entry.get('requests', 0)
        pt = entry.get('prompt_tokens', 0)
        ct = entry.get('completion_tokens', 0)
        rt = entry.get('reasoning_tokens', 0)
        cost = entry.get('usage', 0) or 0
        model = entry.get('model', 'unknown')
        date = entry.get('date', '')[:10]

        total_requests += reqs
        total_prompt_tokens += pt
        total_completion_tokens += ct
        total_reasoning_tokens += rt
        total_usage_cost += cost
        models_used.add(model)

        if date not in daily:
            daily[date] = {'requests': 0, 'tokens': 0, 'cost': 0.0}
        daily[date]['requests'] += reqs
        daily[date]['tokens'] += pt + ct
        daily[date]['cost'] += cost

    return {
        'total_requests': total_requests,
        'total_prompt_tokens': total_prompt_tokens,
        'total_completion_tokens': total_completion_tokens,
        'total_reasoning_tokens': total_reasoning_tokens,
        'total_tokens': total_prompt_tokens + total_completion_tokens + total_reasoning_tokens,
        'total_usage_cost': total_usage_cost,
        'models_count': len(models_used),
        'models_list': sorted(models_used),
        'daily': daily,
        'last_updated': datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
    }

def format_number(n):
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)

def generate_html(stats, auth_data):
    """Generate the OpenRouter live stats section HTML."""
    key_info = auth_data.get('data', {})
    key_label = key_info.get('label', 'Management Key')
    
    # Top models by requests
    model_reqs = {}
    model_tokens = {}
    # We need raw data for this - use the daily breakdown instead
    
    daily_sorted = sorted(stats['daily'].items(), reverse=True)
    recent_days = daily_sorted[:7]
    
    daily_rows = ""
    for date, d in recent_days:
        daily_rows += f"""
                            <tr>
                                <td class="text-slateText font-mono text-[10px]">{date}</td>
                                <td class="text-white font-mono text-[10px] text-right">{format_number(d['requests'])}</td>
                                <td class="text-white font-mono text-[10px] text-right">{format_number(d['tokens'])}</td>
                                <td class="text-cyberGreen font-mono text-[10px] text-right">${d['cost']:.4f}</td>
                            </tr>"""

    html = f'''<!-- ═══ OPENROUTER LIVE STATS ═══ -->
            <section id="openrouter-stats" class="space-y-6 scroll-mt-24">
                <div class="section-label-mono">// Live AI Activity</div>
                <h2 class="text-2xl lg:text-3xl font-black text-white uppercase tracking-tight">OpenRouter Dashboard</h2>
                <p class="text-slateText max-w-2xl leading-relaxed">Live usage data from my OpenRouter management API. This is real-time data from the AI models powering my agentic infrastructure — updated on every page load.</p>
                
                <!-- Key Status -->
                <div class="bg-cardBg border border-hudGray/60 rounded-xl p-4 font-mono text-[11px] flex items-center justify-between max-w-lg">
                    <div class="flex items-center gap-2">
                        <span class="h-2 w-2 rounded-full bg-cyberGreen animate-pulse"></span>
                        <span class="text-slateText">API Key:</span>
                        <span class="text-white font-bold">{key_label}</span>
                    </div>
                    <span class="text-cyberGreen text-[10px] font-bold">ACTIVE</span>
                </div>

                <!-- Main Stats Grid -->
                <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div class="stat-box">
                        <div class="stat-num text-cyberGreen">{format_number(stats['total_requests'])}</div>
                        <div class="stat-label">Total Requests</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-num text-teal-400">{format_number(stats['total_tokens'])}</div>
                        <div class="stat-label">Tokens Processed</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-num text-purple-400">{stats['models_count']}</div>
                        <div class="stat-label">Models Used</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-num text-amber-400">${stats['total_usage_cost']:.2f}</div>
                        <div class="stat-label">Total Cost</div>
                    </div>
                </div>

                <!-- Token Breakdown -->
                <div class="bg-cardBg border border-hudGray/60 rounded-xl p-5">
                    <p class="text-[10px] uppercase tracking-widest text-slateText font-mono font-bold mb-3">Token Breakdown</p>
                    <div class="grid grid-cols-3 gap-3">
                        <div class="text-center">
                            <div class="font-mono text-lg font-bold text-cyberGreen">{format_number(stats['total_prompt_tokens'])}</div>
                            <div class="text-[9px] text-slateText font-mono uppercase">Prompt</div>
                        </div>
                        <div class="text-center">
                            <div class="font-mono text-lg font-bold text-teal-400">{format_number(stats['total_completion_tokens'])}</div>
                            <div class="text-[9px] text-slateText font-mono uppercase">Completion</div>
                        </div>
                        <div class="text-center">
                            <div class="font-mono text-lg font-bold text-purple-400">{format_number(stats['total_reasoning_tokens'])}</div>
                            <div class="text-[9px] text-slateText font-mono uppercase">Reasoning</div>
                        </div>
                    </div>
                </div>

                <!-- Daily Activity Table -->
                <div class="bg-cardBg border border-hudGray/60 rounded-xl p-5">
                    <p class="text-[10px] uppercase tracking-widest text-slateText font-mono font-bold mb-3">Daily Activity (Last 7 Days)</p>
                    <table class="w-full text-left">
                        <thead>
                            <tr class="border-b border-hudGray/40">
                                <th class="text-slateText font-mono text-[10px] pb-2 font-normal">Date</th>
                                <th class="text-slateText font-mono text-[10px] pb-2 font-normal text-right">Requests</th>
                                <th class="text-slateText font-mono text-[10px] pb-2 font-normal text-right">Tokens</th>
                                <th class="text-slateText font-mono text-[10px] pb-2 font-normal text-right">Cost</th>
                            </tr>
                        </thead>
                        <tbody>
                            {daily_rows}
                        </tbody>
                    </table>
                </div>

                <!-- Models Used -->
                <div class="bg-cardBg border border-hudGray/60 rounded-xl p-5">
                    <p class="text-[10px] uppercase tracking-widest text-slateText font-mono font-bold mb-3">Models Used ({stats['models_count']})</p>
                    <div class="flex flex-wrap gap-2">
                        {''.join(f'<span class="tech-pill">{m}</span>' for m in stats['models_list'][:20])}
                        {f'<span class="tech-pill">+{stats["models_count"] - 20} more</span>' if stats['models_count'] > 20 else ''}
                    </div>
                </div>

                <!-- Last Updated -->
                <p class="text-gray-500 font-mono text-[9px] text-right">Last updated: {stats['last_updated']}</p>
            </section>'''
    return html

def main():
    key = get_key()
    print("Fetching auth data...", file=sys.stderr)
    auth = fetch_auth(key)
    print("Fetching activity data...", file=sys.stderr)
    activity = fetch_activity(key)
    
    if 'data' in activity:
        stats = aggregate(activity['data'])
    else:
        print(f"Unexpected response: {activity}", file=sys.stderr)
        sys.exit(1)
    
    html = generate_html(stats, auth)
    print(html)

if __name__ == '__main__':
    main()
