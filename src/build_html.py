"""
HTML dashboard builder.
Generates a self-contained HTML file with inline CSS + JS.
Dark theme, Inter font, interactive tabs.
"""

import json
from html import escape


# ──────────────────── Color palette ────────────────────

BAR_GRADIENTS = [
    'linear-gradient(90deg, #6c5ce7, #a29bfe)',
    'linear-gradient(90deg, #00cec9, #55efc4)',
    'linear-gradient(90deg, #e17055, #fab1a0)',
    'linear-gradient(90deg, #fdcb6e, #ffeaa7)',
    'linear-gradient(90deg, #74b9ff, #a29bfe)',
    'linear-gradient(90deg, #fd79a8, #fdcb6e)',
    'linear-gradient(90deg, #636e72, #b2bec3)',
    'linear-gradient(90deg, #00b894, #55efc4)',
    'linear-gradient(90deg, #e17055, #fdcb6e)',
]

PAIN_COLORS = [
    'linear-gradient(90deg, #ff6b6b, #ee5a24)',
    'linear-gradient(90deg, #e17055, #fab1a0)',
    'linear-gradient(90deg, #fdcb6e, #f6e58d)',
    'linear-gradient(90deg, #74b9ff, #a29bfe)',
    'linear-gradient(90deg, #636e72, #b2bec3)',
    'linear-gradient(90deg, #636e72, #b2bec3)',
]

TAG_COLOR_MAP = {
    'green': ('var(--green-dim)', 'var(--green)'),
    'orange': ('var(--orange-dim)', 'var(--orange)'),
    'pink': ('var(--pink-dim)', 'var(--pink)'),
    'blue': ('var(--blue-dim)', 'var(--blue)'),
    'yellow': ('var(--yellow-dim)', 'var(--yellow)'),
}


def _esc(text: str) -> str:
    return escape(str(text))


# ──────────────────── CSS ────────────────────

CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

*{margin:0;padding:0;box-sizing:border-box}

:root{
  --bg:#0a0a0f;--surface:#12121a;--surface-2:#1a1a26;--surface-3:#22223a;
  --border:#2a2a3e;--text:#e8e8f0;--text-dim:#8888a8;
  --accent:#6c5ce7;--accent-light:#a29bfe;
  --green:#00cec9;--green-dim:#00cec920;
  --orange:#e17055;--orange-dim:#e1705520;
  --yellow:#fdcb6e;--yellow-dim:#fdcb6e20;
  --pink:#fd79a8;--pink-dim:#fd79a820;
  --blue:#74b9ff;--blue-dim:#74b9ff20;
  --red:#ff6b6b;--red-dim:#ff6b6b20;
}

body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);line-height:1.6;min-height:100vh}
.container{max-width:1200px;margin:0 auto;padding:2rem 1.5rem}

.header{text-align:center;margin-bottom:3rem;padding:2rem 0}
.header h1{font-size:2rem;font-weight:800;background:linear-gradient(135deg,var(--accent-light),var(--green));-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:.5rem}
.header .subtitle{color:var(--text-dim);font-size:1rem}
.stats-row{display:flex;gap:1rem;justify-content:center;margin-top:1.5rem;flex-wrap:wrap}
.stat-badge{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:.75rem 1.25rem;text-align:center}
.stat-badge .num{font-size:1.5rem;font-weight:800;color:var(--accent-light)}
.stat-badge .label{font-size:.75rem;color:var(--text-dim);text-transform:uppercase;letter-spacing:.5px}

.nav-sections{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1rem;margin-bottom:1.25rem}
.nav-section-btn{background:var(--surface);border:2px solid var(--border);border-radius:18px;padding:1.1rem 1rem;cursor:pointer;text-align:center;transition:all .2s;user-select:none}
.nav-section-btn:hover{border-color:var(--accent);transform:translateY(-2px);box-shadow:0 8px 24px #6c5ce720}
.nav-section-btn.active{border-color:var(--accent);background:linear-gradient(135deg,#6c5ce715,#6c5ce705);box-shadow:0 4px 16px #6c5ce730}
.nav-section-btn[data-section="day2"].active{border-color:var(--green);background:linear-gradient(135deg,#00cec915,#00cec905);box-shadow:0 4px 16px #00cec930}
.nav-section-btn[data-section="compare"].active{border-color:var(--yellow);background:linear-gradient(135deg,#fdcb6e15,#fdcb6e05);box-shadow:0 4px 16px #fdcb6e30}
.nav-section-btn[data-section="day2"]:hover{border-color:var(--green);box-shadow:0 8px 24px #00cec720}
.nav-section-btn[data-section="compare"]:hover{border-color:var(--yellow);box-shadow:0 8px 24px #fdcb6e20}
.nav-section-icon{font-size:1.6rem;margin-bottom:.4rem}
.nav-section-title{font-size:.95rem;font-weight:800;margin-bottom:.25rem;color:var(--text)}
.nav-section-desc{font-size:.72rem;color:var(--text-dim);line-height:1.4}

.subtabs{display:flex;gap:.4rem;margin-bottom:2rem;flex-wrap:wrap;padding:.75rem 1rem;background:var(--surface);border:1px solid var(--border);border-radius:14px}
.subtab{padding:.45rem 1rem;border-radius:8px;border:1px solid transparent;background:transparent;color:var(--text-dim);cursor:pointer;font-size:.82rem;font-weight:600;white-space:nowrap;transition:all .15s}
.subtab:hover{background:var(--surface-2);color:var(--text)}
.subtab.active{background:var(--accent);color:#fff}
#subtabs-day2 .subtab.active{background:var(--green)}

.section{display:none;animation:fadeIn .3s ease}
.section.active{display:block}
@keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.section-title{font-size:1.4rem;font-weight:800;margin-bottom:1.5rem;display:flex;align-items:center;gap:.5rem}

.portrait-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:1.5rem;margin-bottom:2rem}
.portrait-card{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:1.5rem;position:relative;overflow:hidden}
.portrait-card::before{content:'';position:absolute;top:0;left:0;right:0;height:4px;border-radius:16px 16px 0 0}
.portrait-card.p1::before{background:linear-gradient(90deg,var(--green),var(--blue))}
.portrait-card.p2::before{background:linear-gradient(90deg,var(--orange),var(--yellow))}
.portrait-card.p3::before{background:linear-gradient(90deg,var(--pink),var(--accent-light))}
.portrait-header{display:flex;align-items:center;gap:1rem;margin-bottom:1rem}
.portrait-avatar{width:56px;height:56px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:1.5rem;flex-shrink:0}
.p1 .portrait-avatar{background:var(--green-dim)}
.p2 .portrait-avatar{background:var(--orange-dim)}
.p3 .portrait-avatar{background:var(--pink-dim)}
.portrait-name{font-size:1.1rem;font-weight:700}
.portrait-desc{font-size:.8rem;color:var(--text-dim);margin-top:2px}
.portrait-tag{display:inline-block;padding:.2rem .6rem;border-radius:6px;font-size:.7rem;font-weight:600;margin-right:.3rem;margin-bottom:.3rem}
.tag-green{background:var(--green-dim);color:var(--green)}
.tag-orange{background:var(--orange-dim);color:var(--orange)}
.tag-pink{background:var(--pink-dim);color:var(--pink)}
.tag-blue{background:var(--blue-dim);color:var(--blue)}
.tag-yellow{background:var(--yellow-dim);color:var(--yellow)}
.portrait-section-label{font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:var(--text-dim);margin:1rem 0 .5rem}
.portrait-list{list-style:none}
.portrait-list li{padding:.4rem 0;font-size:.85rem;display:flex;align-items:flex-start;gap:.5rem}
.portrait-list li::before{content:'\2192';color:var(--accent-light);flex-shrink:0}
.pain-list li::before{content:'\2717';color:var(--red)}
.want-list li::before{content:'\25C6';color:var(--green)}
.need-list li::before{content:'\22B9';color:var(--yellow)}
p.portrait-who{font-size:.85rem;color:var(--text-dim)}

.bar-chart{margin-bottom:2rem}
.bar-item{display:flex;align-items:center;gap:1rem;margin-bottom:.75rem;cursor:default;transition:transform .15s}
.bar-item:hover{transform:translateX(4px)}
.bar-label{width:200px;font-size:.85rem;font-weight:600;text-align:right;flex-shrink:0}
.bar-track{flex:1;height:36px;background:var(--surface);border-radius:8px;overflow:hidden;position:relative;border:1px solid var(--border)}
.bar-fill{height:100%;border-radius:8px;display:flex;align-items:center;padding-left:.75rem;font-size:.8rem;font-weight:700;color:#fff;min-width:40px;transition:width .8s cubic-bezier(.4,0,.2,1)}
.bar-count{font-size:.8rem;font-weight:700;width:50px;text-align:center;flex-shrink:0}
.bar-people{font-size:.7rem;color:var(--text-dim);width:60px;flex-shrink:0}

.detail-panel{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:1.5rem;margin-bottom:1.5rem;display:none;animation:fadeIn .3s ease}
.detail-panel.open{display:block}
.detail-panel h3{font-size:1rem;font-weight:700;margin-bottom:.75rem}

.quote-box{background:var(--surface-2);border-left:3px solid var(--accent);border-radius:0 8px 8px 0;padding:.6rem .8rem;margin:.5rem 0;font-size:.8rem;font-style:italic;color:var(--text-dim)}
.quote-author{font-style:normal;font-weight:600;color:var(--accent-light)}

.rec-card{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:1.5rem;margin-bottom:1rem;position:relative}
.rec-card .rec-num{position:absolute;top:-10px;left:20px;background:var(--accent);color:#fff;width:28px;height:28px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:.8rem;font-weight:800}
.rec-card h3{font-size:1rem;font-weight:700;margin-bottom:.5rem}
.rec-card p{font-size:.85rem;color:var(--text-dim);line-height:1.7}
.rec-card .rec-why{margin-top:.75rem;padding-top:.75rem;border-top:1px solid var(--border);font-size:.8rem}
.rec-card .rec-why strong{color:var(--accent-light)}

.compare-row{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;margin-bottom:2rem}
.compare-col{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:1.25rem}
.compare-col.day1{border-top:3px solid var(--accent)}
.compare-col.day2{border-top:3px solid var(--green)}
.compare-col-title{font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:1rem}
.compare-col.day1 .compare-col-title{color:var(--accent-light)}
.compare-col.day2 .compare-col-title{color:var(--green)}
.compare-stat{display:flex;justify-content:space-between;align-items:center;padding:.5rem 0;border-bottom:1px solid var(--border);font-size:.85rem}
.compare-stat:last-child{border-bottom:none}
.compare-stat-val{font-weight:700;color:var(--accent-light)}
.compare-col.day2 .compare-stat-val{color:var(--green)}

.shift-card{background:var(--surface-2);border-radius:12px;padding:1rem 1.25rem;margin-bottom:.75rem;display:flex;gap:1rem;align-items:flex-start}
.shift-card .shift-icon{font-size:1.2rem;flex-shrink:0;margin-top:2px}
.shift-card .shift-title{font-size:.9rem;font-weight:700;margin-bottom:.2rem}
.shift-card .shift-text{font-size:.8rem;color:var(--text-dim);line-height:1.6}

.day2-hero{background:linear-gradient(135deg,#0a1a14,#0f1a2a);border:1px solid #00cec930;border-radius:20px;padding:1.5rem 2rem;margin-bottom:2rem}
.day2-hero h2{font-size:1.2rem;font-weight:800;color:var(--green);margin-bottom:.5rem}
.day2-hero p{font-size:.85rem;color:var(--text-dim);margin-bottom:1rem}

@media(max-width:768px){
  .bar-label{width:120px;font-size:.75rem}
  .portrait-grid{grid-template-columns:1fr}
  .compare-row{grid-template-columns:1fr}
  .header h1{font-size:1.5rem}
  .container{padding:1rem}
  .nav-sections{grid-template-columns:repeat(2,1fr)}
}
"""


# ──────────────────── JS ────────────────────

JS = r"""
const sectionMap = {};
let currentSection = '';

function initNav(sections) {
  for (const [key, cfg] of Object.entries(sections)) {
    sectionMap[key] = cfg;
  }
  currentSection = Object.keys(sections)[0];
}

function showSection(section) {
  document.querySelectorAll('.nav-section-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.section === section);
  });
  document.querySelectorAll('.subtabs').forEach(bar => bar.style.display = 'none');
  const cfg = sectionMap[section];
  if (cfg && cfg.subtabs) {
    const bar = document.getElementById(cfg.subtabs);
    if (bar) {
      bar.style.display = 'flex';
      const subs = bar.querySelectorAll('.subtab');
      subs.forEach(t => t.classList.remove('active'));
      if (subs[0]) subs[0].classList.add('active');
    }
  }
  showTabContent(cfg ? cfg.defaultTab : section);
  currentSection = section;
}

function showTab(tabId, el) {
  const cfg = sectionMap[currentSection];
  if (cfg && cfg.subtabs) {
    document.querySelectorAll('#' + cfg.subtabs + ' .subtab').forEach(t => t.classList.remove('active'));
  }
  if (el) el.classList.add('active');
  showTabContent(tabId);
}

function showTabContent(tabId) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  const target = document.getElementById(tabId);
  if (target) target.classList.add('active');
}

// Animate bars on load
document.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    document.querySelectorAll('.bar-fill').forEach(el => {
      el.style.width = el.dataset.width;
    });
  }, 100);
});
"""


# ──────────────────── HTML builders ────────────────────

def _build_bar_chart(items: list[dict], color_fn=None, show_people=False) -> str:
    """Build horizontal bar chart HTML.

    items: list of dicts with 'name', 'count', optionally 'people', 'quotes', 'job'.
    """
    if not items:
        return '<p style="color:var(--text-dim)">Нет данных</p>'

    max_val = max(item['count'] for item in items) if items else 1
    lines = ['<div class="bar-chart">']

    for i, item in enumerate(items):
        pct = (item['count'] / max_val) * 100 if max_val else 0
        color = color_fn(i) if color_fn else BAR_GRADIENTS[i % len(BAR_GRADIENTS)]
        name = _esc(item['name'])
        count = item['count']

        people_html = ''
        if show_people and 'people' in item:
            people_html = f'<div class="bar-people">{item["people"]} чел.</div>'

        lines.append(f'''<div class="bar-item">
  <div class="bar-label">{name}</div>
  <div class="bar-track">
    <div class="bar-fill" style="width:0%;background:{color}" data-width="{pct:.1f}%">{count}</div>
  </div>
  {people_html}
</div>''')

        # Quotes panel (collapsed)
        quotes = item.get('quotes', [])
        job = item.get('job', '')
        if quotes or job:
            lines.append(f'<div class="detail-panel" id="detail-{i}">')
            if job:
                lines.append(f'<h3>Job: {_esc(job)}</h3>')
            for q in quotes:
                lines.append(f'<div class="quote-box">{_esc(q)}</div>')
            lines.append('</div>')

    lines.append('</div>')
    return '\n'.join(lines)


def _build_portraits(portraits: list[dict]) -> str:
    """Build portrait cards HTML."""
    lines = ['<div class="portrait-grid">']

    for idx, p in enumerate(portraits):
        cls = f'p{idx + 1}'
        lines.append(f'<div class="portrait-card {cls}">')
        lines.append(f'''<div class="portrait-header">
  <div class="portrait-avatar">{p.get("icon", "")}</div>
  <div>
    <div class="portrait-name">\u00ab{_esc(p["title"])}\u00bb</div>
    <div class="portrait-desc">{_esc(p.get("share", ""))} \u00b7 {_esc(p.get("desc", ""))}</div>
  </div>
</div>''')

        # Tags
        tags = p.get('tags', [])
        tag_colors = p.get('tag_colors', [])
        lines.append('<div>')
        for j, tag in enumerate(tags):
            color = tag_colors[j] if j < len(tag_colors) else 'blue'
            lines.append(f'<span class="portrait-tag tag-{color}">{_esc(tag)}</span>')
        lines.append('</div>')

        # Who
        if p.get('who'):
            lines.append('<div class="portrait-section-label">Кто это</div>')
            lines.append(f'<p class="portrait-who">{_esc(p["who"])}</p>')

        # Wants
        if p.get('wants'):
            lines.append('<div class="portrait-section-label">Желания</div>')
            lines.append('<ul class="portrait-list want-list">')
            for w in p['wants']:
                lines.append(f'<li>{_esc(w)}</li>')
            lines.append('</ul>')

        # Pains
        if p.get('pains'):
            lines.append('<div class="portrait-section-label">Боли</div>')
            lines.append('<ul class="portrait-list pain-list">')
            for pain in p['pains']:
                lines.append(f'<li>{_esc(pain)}</li>')
            lines.append('</ul>')

        # Needs
        if p.get('needs'):
            lines.append('<div class="portrait-section-label">Потребности</div>')
            lines.append('<ul class="portrait-list need-list">')
            for n in p['needs']:
                lines.append(f'<li>{_esc(n)}</li>')
            lines.append('</ul>')

        lines.append('</div>')  # portrait-card

    lines.append('</div>')  # portrait-grid
    return '\n'.join(lines)


def _build_recommendations(recs: list[dict]) -> str:
    """Build recommendation cards HTML."""
    lines = []
    for i, rec in enumerate(recs, 1):
        lines.append(f'''<div class="rec-card">
  <div class="rec-num">{i}</div>
  <h3>{_esc(rec["title"])}</h3>
  <p>{_esc(rec["text"])}</p>
  <div class="rec-why"><strong>Как применить:</strong> {_esc(rec["action"])}</div>
</div>''')
    return '\n'.join(lines)


def _build_compare_section(day1: dict, day2: dict) -> str:
    """Build comparison section for two days."""
    s1 = day1['stats']
    s2 = day2['stats']

    lines = []
    lines.append('<div class="section-title">Сравнение дней</div>')

    # Stats comparison
    lines.append('<div class="compare-row">')
    lines.append('<div class="compare-col day1">')
    lines.append('<div class="compare-col-title">День 1</div>')
    lines.append(f'<div class="compare-stat"><span>Сообщений</span><span class="compare-stat-val">{s1["total_messages"]}</span></div>')
    lines.append(f'<div class="compare-stat"><span>Участников</span><span class="compare-stat-val">{s1["unique_people"]}</span></div>')
    lines.append('</div>')
    lines.append('<div class="compare-col day2">')
    lines.append('<div class="compare-col-title">День 2</div>')
    lines.append(f'<div class="compare-stat"><span>Сообщений</span><span class="compare-stat-val">{s2["total_messages"]}</span></div>')
    lines.append(f'<div class="compare-stat"><span>Участников</span><span class="compare-stat-val">{s2["unique_people"]}</span></div>')
    lines.append('</div>')
    lines.append('</div>')

    # Jobs comparison
    lines.append('<h3 style="margin:1.5rem 0 1rem;font-weight:700">Jobs to be Done</h3>')
    lines.append('<div class="compare-row">')

    lines.append('<div class="compare-col day1">')
    lines.append('<div class="compare-col-title">День 1</div>')
    for j in day1.get('jtbd', [])[:5]:
        lines.append(f'<div class="compare-stat"><span>{_esc(j["name"])}</span><span class="compare-stat-val">{j["count"]}</span></div>')
    lines.append('</div>')

    lines.append('<div class="compare-col day2">')
    lines.append('<div class="compare-col-title">День 2</div>')
    for j in day2.get('jtbd', [])[:5]:
        lines.append(f'<div class="compare-stat"><span>{_esc(j["name"])}</span><span class="compare-stat-val">{j["count"]}</span></div>')
    lines.append('</div>')

    lines.append('</div>')

    # Anxieties comparison
    lines.append('<h3 style="margin:1.5rem 0 1rem;font-weight:700">Боли и страхи</h3>')
    lines.append('<div class="compare-row">')

    lines.append('<div class="compare-col day1">')
    lines.append('<div class="compare-col-title">День 1</div>')
    for a in day1.get('anxieties', [])[:5]:
        lines.append(f'<div class="compare-stat"><span>{_esc(a["name"])}</span><span class="compare-stat-val">{a["count"]}</span></div>')
    lines.append('</div>')

    lines.append('<div class="compare-col day2">')
    lines.append('<div class="compare-col-title">День 2</div>')
    for a in day2.get('anxieties', [])[:5]:
        lines.append(f'<div class="compare-stat"><span>{_esc(a["name"])}</span><span class="compare-stat-val">{a["count"]}</span></div>')
    lines.append('</div>')

    lines.append('</div>')

    # Key shifts
    lines.append('<h3 style="margin:1.5rem 0 1rem;font-weight:700">Ключевые сдвиги</h3>')

    d1_jobs = {j['name']: j['count'] for j in day1.get('jtbd', [])}
    d2_jobs = {j['name']: j['count'] for j in day2.get('jtbd', [])}

    all_job_names = list(dict.fromkeys(list(d1_jobs.keys()) + list(d2_jobs.keys())))
    for jname in all_job_names[:5]:
        v1 = d1_jobs.get(jname, 0)
        v2 = d2_jobs.get(jname, 0)
        if v1 == 0 and v2 == 0:
            continue
        if v2 > v1:
            icon = '\u2191'
            title = f'{_esc(jname)}: рост'
        elif v2 < v1:
            icon = '\u2193'
            title = f'{_esc(jname)}: снижение'
        else:
            icon = '\u2194'
            title = f'{_esc(jname)}: без изменений'
        lines.append(f'''<div class="shift-card">
  <div class="shift-icon">{icon}</div>
  <div>
    <div class="shift-title">{title}</div>
    <div class="shift-text">День 1: {v1} \u2192 День 2: {v2}</div>
  </div>
</div>''')

    return '\n'.join(lines)


# ──────────────────── Main builder ────────────────────

def build_dashboard(day1_data: dict, day2_data: dict | None = None) -> str:
    """
    Build a complete HTML dashboard string.

    Args:
        day1_data: Analysis result dict for day 1.
        day2_data: Optional analysis result dict for day 2.

    Returns:
        Complete HTML string.
    """
    has_day2 = day2_data is not None
    s1 = day1_data['stats']

    # Header stats
    total_msgs = s1['total_messages']
    total_people = s1['unique_people']
    if has_day2:
        total_msgs += day2_data['stats']['total_messages']
        all_people = total_people + day2_data['stats']['unique_people']
    else:
        all_people = total_people

    # Navigation sections
    nav_buttons = [
        ('day1', '\U0001F4C5', 'День 1', 'Портреты, Jobs, боли, ниши'),
    ]
    if has_day2:
        nav_buttons.append(('day2', '\U0001F4C5', 'День 2', 'Jobs, продукты, ниши'))
        nav_buttons.append(('compare', '\U0001F4CA', 'Сравнение', 'Динамика между днями'))

    nav_html = '<div class="nav-sections">\n'
    for i, (key, icon, title, desc) in enumerate(nav_buttons):
        active = ' active' if i == 0 else ''
        nav_html += f'''<div class="nav-section-btn{active}" data-section="{key}" onclick="showSection('{key}')">
  <div class="nav-section-icon">{icon}</div>
  <div class="nav-section-title">{_esc(title)}</div>
  <div class="nav-section-desc">{_esc(desc)}</div>
</div>\n'''
    nav_html += '</div>\n'

    # Subtabs for day1
    subtabs_day1 = '''<div class="subtabs" id="subtabs-day1">
  <div class="subtab active" data-tab="portraits" onclick="showTab('portraits', this)">Портреты ЦА</div>
  <div class="subtab" data-tab="jobs" onclick="showTab('jobs', this)">Jobs to be Done</div>
  <div class="subtab" data-tab="pains" onclick="showTab('pains', this)">Боли и страхи</div>
  <div class="subtab" data-tab="products" onclick="showTab('products', this)">Желаемые продукты</div>
  <div class="subtab" data-tab="professions" onclick="showTab('professions', this)">Ниши аудитории</div>
  <div class="subtab" data-tab="recs" onclick="showTab('recs', this)">Рекомендации</div>
</div>'''

    subtabs_day2 = ''
    if has_day2:
        subtabs_day2 = '''<div class="subtabs" id="subtabs-day2" style="display:none">
  <div class="subtab active" data-tab="day2-overview" onclick="showTab('day2-overview', this)">Обзор</div>
  <div class="subtab" data-tab="day2-jobs" onclick="showTab('day2-jobs', this)">Jobs to be Done</div>
  <div class="subtab" data-tab="day2-products" onclick="showTab('day2-products', this)">Продукты</div>
  <div class="subtab" data-tab="day2-professions" onclick="showTab('day2-professions', this)">Ниши аудитории</div>
</div>'''

    # ── Day 1 sections ──

    # Portraits
    portraits_html = f'''<div class="section active" id="portraits">
<div class="section-title">ТОП-3 портрета целевой аудитории</div>
{_build_portraits(day1_data.get('portraits', []))}
</div>'''

    # Jobs
    jobs_html = f'''<div class="section" id="jobs">
<div class="section-title">Jobs to be Done</div>
{_build_bar_chart(day1_data.get('jtbd', []), show_people=True)}
</div>'''

    # Pains
    pains_html = f'''<div class="section" id="pains">
<div class="section-title">Боли и страхи</div>
{_build_bar_chart(day1_data.get('anxieties', []), color_fn=lambda i: PAIN_COLORS[i % len(PAIN_COLORS)])}
</div>'''

    # Products
    products_html = f'''<div class="section" id="products">
<div class="section-title">Желаемые продукты</div>
{_build_bar_chart(day1_data.get('products', []))}
</div>'''

    # Professions
    profs_html = f'''<div class="section" id="professions">
<div class="section-title">Ниши аудитории</div>
{_build_bar_chart(day1_data.get('professions', []), show_people=True)}
</div>'''

    # Recommendations
    recs_html = f'''<div class="section" id="recs">
<div class="section-title">Рекомендации для оффера</div>
{_build_recommendations(day1_data.get('recommendations', []))}
</div>'''

    # ── Day 2 sections ──
    day2_sections = ''
    if has_day2:
        d2 = day2_data
        d2s = d2['stats']

        day2_overview = f'''<div class="section" id="day2-overview">
<div class="day2-hero">
  <h2>День 2 — обзор</h2>
  <p>Сообщений: {d2s["total_messages"]} | Участников: {d2s["unique_people"]}</p>
</div>
<div class="section-title">Jobs to be Done — День 2</div>
{_build_bar_chart(d2.get('jtbd', [])[:5], show_people=True)}
</div>'''

        day2_jobs = f'''<div class="section" id="day2-jobs">
<div class="section-title">Jobs to be Done — День 2</div>
{_build_bar_chart(d2.get('jtbd', []), show_people=True)}
</div>'''

        day2_products = f'''<div class="section" id="day2-products">
<div class="section-title">Продукты — День 2</div>
{_build_bar_chart(d2.get('products', []))}
</div>'''

        day2_profs = f'''<div class="section" id="day2-professions">
<div class="section-title">Ниши аудитории — День 2</div>
{_build_bar_chart(d2.get('professions', []), show_people=True)}
</div>'''

        day2_sections = '\n'.join([day2_overview, day2_jobs, day2_products, day2_profs])

    # ── Compare section ──
    compare_section = ''
    if has_day2:
        compare_section = f'''<div class="section" id="compare">
{_build_compare_section(day1_data, day2_data)}
</div>'''

    # ── Navigation JS init ──
    nav_init_parts = ["day1: { subtabs: 'subtabs-day1', defaultTab: 'portraits' }"]
    if has_day2:
        nav_init_parts.append("day2: { subtabs: 'subtabs-day2', defaultTab: 'day2-overview' }")
        nav_init_parts.append("compare: { subtabs: null, defaultTab: 'compare' }")
    nav_init = ', '.join(nav_init_parts)

    # ── Assemble ──
    html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JTBD-анализ аудитории — Практикум по вайбкодингу</title>
<style>
{CSS}
</style>
</head>
<body>

<div class="container">

  <div class="header">
    <h1>Анализ целевой аудитории</h1>
    <div class="subtitle">Практикум по вайбкодингу &middot; Данные из чата вебинара</div>
    <div class="stats-row">
      <div class="stat-badge"><div class="num">{all_people}</div><div class="label">участников</div></div>
      <div class="stat-badge"><div class="num">{total_msgs}</div><div class="label">сообщений</div></div>
      <div class="stat-badge"><div class="num">{len(day1_data.get('jtbd', []))}</div><div class="label">Jobs to be Done</div></div>
      <div class="stat-badge"><div class="num">{len(day1_data.get('professions', []))}</div><div class="label">ниш аудитории</div></div>
    </div>
  </div>

  {nav_html}
  {subtabs_day1}
  {subtabs_day2}

  {portraits_html}
  {jobs_html}
  {pains_html}
  {products_html}
  {profs_html}
  {recs_html}

  {day2_sections}
  {compare_section}

</div>

<script>
{JS}
initNav({{ {nav_init} }});
</script>

</body>
</html>'''

    return html
