#!/usr/bin/env python3
"""Fetch OpenRouter activity data and generate live stats for portfolio."""

import json
import sys
from datetime import datetime


def get_key():
    """Get OpenRouter management key from env or .env file."""
    import os
    key = os.environ.get('OPENROUTER_MANAGEMENT_KEY')
    if key:
        return key
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
    model_stats = {}

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

        if model not in model_stats:
            model_stats[model] = {'requests': 0, 'tokens': 0, 'cost': 0.0}
        model_stats[model]['requests'] += reqs
        model_stats[model]['tokens'] += pt + ct + rt
        model_stats[model]['cost'] += cost

    # Sort model stats by requests descending
    sorted_models = sorted(model_stats.items(), key=lambda x: x[1]['requests'], reverse=True)

    return {
        'total_requests': total_requests,
        'total_prompt_tokens': total_prompt_tokens,
        'total_completion_tokens': total_completion_tokens,
        'total_reasoning_tokens': total_reasoning_tokens,
        'total_tokens': total_prompt_tokens + total_completion_tokens + total_reasoning_tokens,
        'total_usage_cost': total_usage_cost,
        'models_count': len(models_used),
        'models_list': sorted(models_used),
        'model_stats': sorted_models,
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
    """Generate the OpenRouter live stats section HTML with interactivity."""
    key_info = auth_data.get('data', {})
    api_online = bool(key_info)

    status_color = "bg-cyberGreen" if api_online else "bg-red-500"
    status_text = "LIVE" if api_online else "DOWN"
    status_text_color = "text-cyberGreen" if api_online else "text-red-500"

    daily_sorted = sorted(stats['daily'].items(), reverse=True)
    recent_days = daily_sorted[:7]
    day_count = len(recent_days) or 1

    # --- Daily table rows (with data attributes for sorting) ---
    daily_rows = ""
    for date, d in recent_days:
        daily_rows += f"""
                            <tr class="or-daily-row" data-date="{date}" data-requests="{d['requests']}" data-tokens="{d['tokens']}" data-cost="{d['cost']:.6f}">
                                <td class="text-slateText font-mono text-[10px] py-1">{date}</td>
                                <td class="text-white font-mono text-[10px] text-right">{format_number(d['requests'])}</td>
                                <td class="text-white font-mono text-[10px] text-right">{format_number(d['tokens'])}</td>
                                <td class="text-cyberGreen font-mono text-[10px] text-right">${d['cost']:.4f}</td>
                            </tr>"""

    # --- Bar chart data ---
    max_reqs = max((d['requests'] for _, d in recent_days), default=1) or 1
    chart_bars = ""
    chart_labels = ""
    for date, d in reversed(recent_days):  # chronological order
        pct = (d['requests'] / max_reqs) * 100
        short_date = date[5:]  # MM-DD
        chart_bars += f"""
                            <div class="or-bar flex-1 bg-cyberGreen/80 hover:bg-cyberGreen rounded-t transition-all duration-200 relative group cursor-pointer" style="height: {pct:.1f}%">
                                <div class="or-bar-tooltip absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-black/90 border border-hudGray/60 rounded text-[9px] text-white font-mono whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                                    {d['requests']} req · {format_number(d['tokens'])} tok · ${d['cost']:.4f}
                                </div>
                            </div>"""
        chart_labels += f'<span class="flex-1 text-slateText text-[8px] font-mono text-center">{short_date}</span>'

    # --- Model list (all, with search filter) ---
    model_pills = ""
    for m in stats['models_list']:
        ms = dict(stats['model_stats'])[m]
        model_pills += f"""
                        <span class="or-model-pill tech-pill cursor-pointer hover:border-cyberGreen/50 transition-all" data-model="{m}" data-requests="{ms['requests']}" onclick="window.open('https://openrouter.ai/{m}', '_blank')">{m}</span>"""

    # Top 10 models table
    top_models_rows = ""
    for m, ms in stats['model_stats'][:10]:
        top_models_rows += f"""
                            <tr class="border-b border-hudGray/20 hover:bg-white/5 transition-colors cursor-pointer" onclick="window.open('https://openrouter.ai/{m}', '_blank')">
                                <td class="text-slateText font-mono text-[10px] py-1.5 max-w-[180px] truncate" title="{m}">{m}</td>
                                <td class="text-white font-mono text-[10px] text-right">{format_number(ms['requests'])}</td>
                                <td class="text-white font-mono text-[10px] text-right">{format_number(ms['tokens'])}</td>
                                <td class="text-cyberGreen font-mono text-[10px] text-right">${ms['cost']:.4f}</td>
                            </tr>"""

    # Build the HTML using a template to avoid f-string brace conflicts with JS/CSS
    # All dynamic values are inserted via .replace() placeholders
    html = '''<!-- ═══ OPENROUTER LIVE STATS ═══ -->
            <section id="openrouter-stats" class="space-y-6 scroll-mt-24">
                <div class="section-label-mono">// Live AI Activity</div>
                <h2 class="text-2xl lg:text-3xl font-black text-white uppercase tracking-tight">OpenRouter Dashboard</h2>
                <p class="text-slateText max-w-2xl leading-relaxed">Live usage data from my OpenRouter management API. This is real-time data from the AI models powering my agentic infrastructure — updated on every page load.</p>

                <!-- API Status -->
                <div class="bg-cardBg border border-hudGray/60 rounded-xl p-4 font-mono text-[11px] flex items-center justify-between max-w-lg">
                    <div class="flex items-center gap-2">
                        <span class="h-2 w-2 rounded-full __STATUS_COLOR__ animate-pulse"></span>
                        <span class="text-slateText">OpenRouter API</span>
                    </div>
                    <span class="__STATUS_TEXT_COLOR__ text-[10px] font-bold">__STATUS_TEXT__</span>
                </div>

                <!-- View Toggle -->
                <div class="flex items-center gap-2">
                    <span class="text-[9px] text-slateText font-mono uppercase tracking-widest mr-1">View:</span>
                    <button id="or-view-total" class="or-view-btn px-3 py-1.5 rounded-md text-[10px] font-mono font-bold transition-all bg-cyberGreen text-black" onclick="orSwitchView('total')">Total</button>
                    <button id="or-view-daily" class="or-view-btn px-3 py-1.5 rounded-md text-[10px] font-mono font-bold transition-all bg-hudGray text-slateText hover:text-white" onclick="orSwitchView('daily')">Daily Avg</button>
                </div>

                <!-- Main Stats Grid -->
                <div id="or-stats-grid" class="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div class="stat-box">
                        <div class="stat-num text-cyberGreen" id="or-stat-requests" data-total="__TOTAL_REQUESTS__" data-daily="__DAILY_REQUESTS__">__TOTAL_REQUESTS__</div>
                        <div class="stat-label" id="or-stat-requests-label">Total Requests</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-num text-teal-400" id="or-stat-tokens" data-total="__TOTAL_TOKENS__" data-daily="__DAILY_TOKENS__">__TOTAL_TOKENS__</div>
                        <div class="stat-label" id="or-stat-tokens-label">Tokens Processed</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-num text-purple-400" id="or-stat-models">__MODELS_COUNT__</div>
                        <div class="stat-label">Models Used</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-num text-amber-400" id="or-stat-cost" data-total="__TOTAL_COST__" data-daily="__DAILY_COST__">__TOTAL_COST__</div>
                        <div class="stat-label" id="or-stat-cost-label">Total Cost</div>
                    </div>
                </div>

                <!-- Token Breakdown -->
                <div class="bg-cardBg border border-hudGray/60 rounded-xl p-5">
                    <p class="text-[10px] uppercase tracking-widest text-slateText font-mono font-bold mb-3">Token Breakdown</p>
                    <div class="grid grid-cols-3 gap-3">
                        <div class="text-center">
                            <div class="font-mono text-lg font-bold text-cyberGreen">__PROMPT_TOKENS__</div>
                            <div class="text-[9px] text-slateText font-mono uppercase">Prompt</div>
                        </div>
                        <div class="text-center">
                            <div class="font-mono text-lg font-bold text-teal-400">__COMPLETION_TOKENS__</div>
                            <div class="text-[9px] text-slateText font-mono uppercase">Completion</div>
                        </div>
                        <div class="text-center">
                            <div class="font-mono text-lg font-bold text-purple-400">__REASONING_TOKENS__</div>
                            <div class="text-[9px] text-slateText font-mono uppercase">Reasoning</div>
                        </div>
                    </div>
                </div>

                <!-- Bar Chart -->
                <div class="bg-cardBg border border-hudGray/60 rounded-xl p-5">
                    <p class="text-[10px] uppercase tracking-widest text-slateText font-mono font-bold mb-3">Requests Per Day</p>
                    <div class="flex items-end gap-1.5 h-32 mb-2">
                        __CHART_BARS__
                    </div>
                    <div class="flex gap-1.5">
                        __CHART_LABELS__
                    </div>
                </div>

                <!-- Daily Activity Table (Sortable) -->
                <div class="bg-cardBg border border-hudGray/60 rounded-xl p-5">
                    <div class="flex items-center justify-between mb-3">
                        <p class="text-[10px] uppercase tracking-widest text-slateText font-mono font-bold">Daily Activity</p>
                        <span class="text-[8px] text-slateText font-mono">Click headers to sort</span>
                    </div>
                    <table class="w-full text-left" id="or-daily-table">
                        <thead>
                            <tr class="border-b border-hudGray/40">
                                <th class="or-sort-header text-slateText font-mono text-[10px] pb-2 font-normal cursor-pointer hover:text-white transition-colors" data-col="date" data-dir="desc">Date ↕</th>
                                <th class="or-sort-header text-slateText font-mono text-[10px] pb-2 font-normal text-right cursor-pointer hover:text-white transition-colors" data-col="requests" data-dir="desc">Requests ↕</th>
                                <th class="or-sort-header text-slateText font-mono text-[10px] pb-2 font-normal text-right cursor-pointer hover:text-white transition-colors" data-col="tokens" data-dir="desc">Tokens ↕</th>
                                <th class="or-sort-header text-slateText font-mono text-[10px] pb-2 font-normal text-right cursor-pointer hover:text-white transition-colors" data-col="cost" data-dir="desc">Cost ↕</th>
                            </tr>
                        </thead>
                        <tbody id="or-daily-tbody">
                            __DAILY_ROWS__
                        </tbody>
                    </table>
                </div>

                <!-- Top Models Table -->
                <div class="bg-cardBg border border-hudGray/60 rounded-xl p-5">
                    <p class="text-[10px] uppercase tracking-widest text-slateText font-mono font-bold mb-3">Top Models by Requests</p>
                    <table class="w-full text-left">
                        <thead>
                            <tr class="border-b border-hudGray/40">
                                <th class="text-slateText font-mono text-[10px] pb-2 font-normal">Model</th>
                                <th class="text-slateText font-mono text-[10px] pb-2 font-normal text-right">Requests</th>
                                <th class="text-slateText font-mono text-[10px] pb-2 font-normal text-right">Tokens</th>
                                <th class="text-slateText font-mono text-[10px] pb-2 font-normal text-right">Cost</th>
                            </tr>
                        </thead>
                        <tbody>
                            __TOP_MODELS_ROWS__
                        </tbody>
                    </table>
                </div>

                <!-- All Models (Searchable) -->
                <div class="bg-cardBg border border-hudGray/60 rounded-xl p-5">
                    <div class="flex items-center justify-between mb-3">
                        <p class="text-[10px] uppercase tracking-widest text-slateText font-mono font-bold">All Models (__MODELS_COUNT__)</p>
                        <input id="or-model-search" type="text" placeholder="Filter models..." class="bg-black/30 border border-hudGray/40 rounded px-2 py-1 text-[10px] text-white font-mono placeholder-gray-600 focus:outline-none focus:border-cyberGreen/40 w-44 transition-colors" oninput="orFilterModels(this.value)" />
                    </div>
                    <div id="or-model-list" class="flex flex-wrap gap-2">
                        __MODEL_PILLS__
                    </div>
                    <p id="or-model-count" class="text-[9px] text-slateText font-mono mt-2">__MODELS_COUNT__ models</p>
                </div>

                <!-- Footer: refresh info + button -->
                <div class="flex items-center justify-between">
                    <p class="text-gray-500 font-mono text-[9px]">Auto-refreshes every 1 hour · Last updated: __LAST_UPDATED__</p>
                    <button id="or-refresh-btn" class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[10px] font-mono font-bold transition-all bg-hudGray text-slateText hover:text-white hover:bg-hudGray/80 border border-hudGray/50" onclick="orTriggerRefresh(this)">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                        Refresh Now
                    </button>
                </div>
            </section>

            <script>
            (function() {
                // -- Trigger GitHub Actions workflow_dispatch --
                window.orTriggerRefresh = function(btn) {
                    var originalHTML = btn.innerHTML;
                    btn.innerHTML = '<svg class="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></svg> Opening...';
                    btn.disabled = true;
                    btn.classList.add('opacity-75', 'cursor-not-allowed');
                    window.open('https://github.com/SaintChris/saintlex-portfolio/actions/workflows/update-or-stats.yml', '_blank');
                    btn.innerHTML = '<svg class="w-3 h-3 text-cyberGreen" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg> Opened - click Run';
                    setTimeout(function() {
                        btn.innerHTML = originalHTML;
                        btn.disabled = false;
                        btn.classList.remove('opacity-75', 'cursor-not-allowed');
                    }, 4000);
                };
                // -- View Toggle --
                window.orSwitchView = function(view) {
                    var btns = document.querySelectorAll('.or-view-btn');
                    btns.forEach(function(b) {
                        b.classList.remove('bg-cyberGreen', 'text-black');
                        b.classList.add('bg-hudGray', 'text-slateText');
                    });
                    var activeBtn = document.getElementById('or-view-' + view);
                    activeBtn.classList.remove('bg-hudGray', 'text-slateText');
                    activeBtn.classList.add('bg-cyberGreen', 'text-black');
                    var fields = [
                        {id: 'or-stat-requests', labelId: 'or-stat-requests-label', label: 'Requests'},
                        {id: 'or-stat-tokens', labelId: 'or-stat-tokens-label', label: 'Tokens Processed'},
                        {id: 'or-stat-cost', labelId: 'or-stat-cost-label', label: 'Cost'}
                    ];
                    fields.forEach(function(f) {
                        var el = document.getElementById(f.id);
                        var labelEl = document.getElementById(f.labelId);
                        if (el) {
                            var val = el.getAttribute('data-' + view);
                            if (val) el.textContent = val;
                        }
                        if (labelEl) {
                            labelEl.textContent = (view === 'daily' ? 'Daily Avg ' : 'Total ') + f.label;
                        }
                    });
                };
                // -- Table Sorting --
                document.querySelectorAll('.or-sort-header').forEach(function(th) {
                    th.addEventListener('click', function() {
                        var col = this.getAttribute('data-col');
                        var dir = this.getAttribute('data-dir');
                        var newDir = dir === 'asc' ? 'desc' : 'asc';
                        this.setAttribute('data-dir', newDir);
                        document.querySelectorAll('.or-sort-header').forEach(function(h) {
                            h.textContent = h.textContent.replace(/[↑↓]/g, '↕');
                        });
                        this.textContent = this.textContent.replace('↕', newDir === 'asc' ? '↑' : '↓');
                        var tbody = document.getElementById('or-daily-tbody');
                        var rows = Array.from(tbody.querySelectorAll('.or-daily-row'));
                        rows.sort(function(a, b) {
                            var va, vb;
                            if (col === 'date') {
                                va = a.getAttribute('data-date');
                                vb = b.getAttribute('data-date');
                                return newDir === 'asc' ? va.localeCompare(vb) : vb.localeCompare(va);
                            }
                            va = parseFloat(a.getAttribute('data-' + col));
                            vb = parseFloat(b.getAttribute('data-' + col));
                            return newDir === 'asc' ? va - vb : vb - va;
                        });
                        rows.forEach(function(r) { tbody.appendChild(r); });
                    });
                });
                // -- Model Filter --
                window.orFilterModels = function(query) {
                    var q = query.toLowerCase().trim();
                    var pills = document.querySelectorAll('.or-model-pill');
                    var visible = 0;
                    pills.forEach(function(p) {
                        var model = p.getAttribute('data-model').toLowerCase();
                        var match = !q || model.includes(q);
                        p.style.display = match ? 'inline-block' : 'none';
                        if (match) visible++;
                    });
                    var countEl = document.getElementById('or-model-count');
                    if (countEl) countEl.textContent = visible + ' of ' + pills.length + ' models';
                };
            })();
            </script>'''

    # Now replace all placeholders with actual values
    replacements = {
        '__STATUS_COLOR__': status_color,
        '__STATUS_TEXT_COLOR__': status_text_color,
        '__STATUS_TEXT__': status_text,
        '__TOTAL_REQUESTS__': format_number(stats['total_requests']),
        '__DAILY_REQUESTS__': format_number(int(stats['total_requests']/day_count)),
        '__TOTAL_TOKENS__': format_number(stats['total_tokens']),
        '__DAILY_TOKENS__': format_number(int(stats['total_tokens']/day_count)),
        '__MODELS_COUNT__': str(stats['models_count']),
        '__TOTAL_COST__': f"${stats['total_usage_cost']:.2f}",
        '__DAILY_COST__': f"${stats['total_usage_cost']/day_count:.2f}",
        '__PROMPT_TOKENS__': format_number(stats['total_prompt_tokens']),
        '__COMPLETION_TOKENS__': format_number(stats['total_completion_tokens']),
        '__REASONING_TOKENS__': format_number(stats['total_reasoning_tokens']),
        '__CHART_BARS__': chart_bars,
        '__CHART_LABELS__': chart_labels,
        '__DAILY_ROWS__': daily_rows,
        '__TOP_MODELS_ROWS__': top_models_rows,
        '__MODEL_PILLS__': model_pills,
        '__LAST_UPDATED__': stats['last_updated'],
    }
    for key, val in replacements.items():
        html = html.replace(key, val)

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
