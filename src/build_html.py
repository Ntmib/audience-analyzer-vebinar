"""
HTML dashboard builder — multi-launch, multi-source, 3-level navigation.
Generates a self-contained HTML file with inline CSS + JS.
Dark theme, Inter font, interactive tabs.

API:
    build_dashboard(launches: list[dict]) -> str

Each launch dict:
    {
        "id": "2026-03-08",
        "name": "Практикум по вайбкодингу",
        "dates": "9-11 марта 2026",
        "sources": [
            {"type": "chat", "label": "День 1", "data": analyze_day_result},
            {"type": "chat", "label": "День 2", "data": analyze_day_result},
            {"type": "survey", "label": "Анкеты", "data": analyze_day_result},
            {"type": "sales", "label": "Отдел продаж", "data": analyze_day_result},
        ],
        "comparison": {...}  # optional
    }
"""

import json
from html import escape


# ──────────────────── Helpers ────────────────────

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
]

FORCE_COLORS = {
    'push': '#e17055',
    'pull': '#00cec9',
    'anxiety': '#fd79a8',
    'habit': '#fdcb6e',
}

FORCE_LABELS = {
    'push': 'Push (толчок)',
    'pull': 'Pull (притяжение)',
    'anxiety': 'Anxiety (тревога)',
    'habit': 'Habit (привычка)',
}

FUD_COLORS = {
    'fear': '#ff6b6b',
    'uncertainty': '#fdcb6e',
    'doubt': '#74b9ff',
}

FUD_LABELS = {
    'fear': 'Страх (Fear)',
    'uncertainty': 'Неопределённость (Uncertainty)',
    'doubt': 'Сомнение (Doubt)',
}


def _esc(text) -> str:
    return escape(str(text))


def _json_embed(data) -> str:
    """Embed data as JSON for JS consumption."""
    return json.dumps(data, ensure_ascii=False, default=str)




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

/* Header */
.header{text-align:center;margin-bottom:2rem;padding:2rem 0}
.header h1{font-size:2rem;font-weight:800;background:linear-gradient(135deg,var(--accent-light),var(--green));-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:.5rem}
.header .subtitle{color:var(--text-dim);font-size:1rem}
.stats-row{display:flex;gap:1rem;justify-content:center;margin-top:1.5rem;flex-wrap:wrap}
.stat-badge{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:.75rem 1.25rem;text-align:center}
.stat-badge .num{font-size:1.5rem;font-weight:800;color:var(--accent-light)}
.stat-badge .label{font-size:.75rem;color:var(--text-dim);text-transform:uppercase;letter-spacing:.5px}

/* Level 0: Launch selector */
.launch-bar{display:flex;gap:.5rem;margin-bottom:1.5rem;flex-wrap:wrap;justify-content:center}
.launch-pill{padding:.6rem 1.4rem;border-radius:12px;border:2px solid var(--border);background:var(--surface);cursor:pointer;text-align:center;transition:all .2s;user-select:none;position:relative}
.launch-pill:hover{border-color:var(--accent);transform:translateY(-2px);box-shadow:0 6px 20px #6c5ce720}
.launch-pill.active{border-color:var(--accent);background:linear-gradient(135deg,#6c5ce715,#6c5ce705);box-shadow:0 4px 16px #6c5ce730}
.launch-pill .lp-name{font-size:.9rem;font-weight:700}
.launch-pill .lp-dates{font-size:.7rem;color:var(--text-dim)}
.launch-pill .lp-badge{position:absolute;top:-6px;right:-6px;background:var(--accent);color:#fff;font-size:.6rem;font-weight:800;padding:2px 6px;border-radius:8px}

/* Level 1: Source tabs */
.source-tabs{display:flex;gap:.5rem;margin-bottom:1rem;flex-wrap:wrap;padding:.6rem .8rem;background:var(--surface);border:1px solid var(--border);border-radius:14px}
.source-tab{padding:.5rem 1.1rem;border-radius:10px;border:1px solid transparent;background:transparent;color:var(--text-dim);cursor:pointer;font-size:.85rem;font-weight:600;white-space:nowrap;transition:all .15s}
.source-tab:hover{background:var(--surface-2);color:var(--text)}
.source-tab.active{background:var(--accent);color:#fff}
.source-tab[data-type="survey"].active{background:var(--green)}
.source-tab[data-type="sales"].active{background:var(--orange)}
.source-tab[data-type="comparison"].active{background:var(--yellow);color:#000}
.source-tab[data-type="combined"].active{background:var(--pink)}

/* Level 2: Analysis subtabs */
.subtabs{display:flex;gap:.4rem;margin-bottom:2rem;flex-wrap:wrap;padding:.6rem .8rem;background:var(--surface-2);border:1px solid var(--border);border-radius:12px}
.subtab{padding:.4rem .9rem;border-radius:8px;border:none;background:transparent;color:var(--text-dim);cursor:pointer;font-size:.8rem;font-weight:600;white-space:nowrap;transition:all .15s}
.subtab:hover{background:var(--surface-3);color:var(--text)}
.subtab.active{background:var(--accent);color:#fff}

/* Sections */
.section{display:none;animation:fadeIn .3s ease}
.section.visible{display:block}
@keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.section-title{font-size:1.4rem;font-weight:800;margin-bottom:1.5rem;display:flex;align-items:center;gap:.5rem}
.launch-panel{display:none}
.launch-panel.visible{display:block}
.source-panel{display:none}
.source-panel.visible{display:block}

/* Portraits */
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

/* Bar charts */
.bar-chart{margin-bottom:2rem}
.bar-item{display:flex;align-items:center;gap:1rem;margin-bottom:.75rem;transition:transform .15s}
.bar-item:hover{transform:translateX(4px)}
.bar-label{width:200px;font-size:.85rem;font-weight:600;text-align:right;flex-shrink:0}
.bar-track{flex:1;height:36px;background:var(--surface);border-radius:8px;overflow:hidden;position:relative;border:1px solid var(--border)}
.bar-fill{height:100%;border-radius:8px;display:flex;align-items:center;padding-left:.75rem;font-size:.8rem;font-weight:700;color:#fff;min-width:40px;transition:width .8s cubic-bezier(.4,0,.2,1)}
.bar-count{font-size:.8rem;font-weight:700;width:50px;text-align:center;flex-shrink:0}
.bar-people{font-size:.7rem;color:var(--text-dim);width:60px;flex-shrink:0}

/* Quote boxes */
.quote-box{background:var(--surface-2);border-left:3px solid var(--accent);border-radius:0 8px 8px 0;padding:.6rem .8rem;margin:.5rem 0;font-size:.8rem;font-style:italic;color:var(--text-dim);position:relative}
.quote-author{font-style:normal;font-weight:600;color:var(--accent-light)}
.quote-copy{position:absolute;top:.4rem;right:.4rem;background:var(--surface-3);border:1px solid var(--border);border-radius:6px;padding:.2rem .5rem;font-size:.65rem;cursor:pointer;color:var(--text-dim);opacity:0;transition:opacity .2s}
.quote-box:hover .quote-copy{opacity:1}
.quote-copy.copied{color:var(--green);border-color:var(--green)}

/* Expandable sections */
.expandable-header{cursor:pointer;display:flex;align-items:center;gap:.5rem;padding:.6rem;border-radius:8px;transition:background .15s}
.expandable-header:hover{background:var(--surface-2)}
.expandable-header .arrow{transition:transform .2s;font-size:.7rem}
.expandable-header.open .arrow{transform:rotate(90deg)}
.expandable-body{display:none;padding:.5rem 0 .5rem 1.5rem}
.expandable-body.open{display:block}

/* Forces of Progress */
.forces-container{display:grid;gap:1rem;margin-bottom:2rem}
.force-row{display:flex;align-items:center;gap:1rem;padding:1rem;background:var(--surface);border:1px solid var(--border);border-radius:12px}
.force-label{width:160px;flex-shrink:0}
.force-label .fl-name{font-size:.9rem;font-weight:700}
.force-label .fl-desc{font-size:.7rem;color:var(--text-dim)}
.force-bar-track{flex:1;height:28px;background:var(--surface-2);border-radius:8px;overflow:hidden}
.force-bar-fill{height:100%;border-radius:8px;display:flex;align-items:center;padding-left:.75rem;font-size:.8rem;font-weight:700;color:#fff;min-width:30px;transition:width .8s cubic-bezier(.4,0,.2,1)}
.force-count{width:40px;text-align:center;font-size:.9rem;font-weight:700;flex-shrink:0}
.force-people{width:60px;font-size:.7rem;color:var(--text-dim);flex-shrink:0}
.forces-balance{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:1.5rem;text-align:center;margin-bottom:1.5rem}
.forces-balance .fb-score{font-size:3rem;font-weight:900}
.forces-balance .fb-label{font-size:.85rem;color:var(--text-dim);margin-top:.3rem}
.forces-balance .fb-flag{margin-top:.75rem;padding:.6rem 1rem;border-radius:10px;font-size:.85rem;font-weight:600;display:inline-block}
.fb-flag.warning{background:var(--red-dim);color:var(--red);border:1px solid #ff6b6b40}
.fb-flag.positive{background:var(--green-dim);color:var(--green);border:1px solid #00cec940}
.fb-flag.neutral{background:var(--yellow-dim);color:var(--yellow);border:1px solid #fdcb6e40}

/* FUD Analysis */
.fud-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem;margin-bottom:2rem}
.fud-col{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:1.25rem;position:relative;overflow:hidden}
.fud-col::before{content:'';position:absolute;top:0;left:0;right:0;height:3px}
.fud-col.fud-fear::before{background:var(--red)}
.fud-col.fud-uncertainty::before{background:var(--yellow)}
.fud-col.fud-doubt::before{background:var(--blue)}
.fud-col-title{font-size:1rem;font-weight:700;margin-bottom:.5rem}
.fud-col-count{font-size:2rem;font-weight:900;margin-bottom:.5rem}
.fud-col .fud-bar{height:8px;background:var(--surface-2);border-radius:4px;margin-bottom:1rem;overflow:hidden}
.fud-col .fud-bar-fill{height:100%;border-radius:4px;transition:width .8s}
.fud-tactic{background:var(--surface-2);border-radius:10px;padding:.75rem;margin-top:.75rem}
.fud-tactic-label{font-size:.7rem;font-weight:700;text-transform:uppercase;color:var(--text-dim);letter-spacing:.5px;margin-bottom:.3rem}
.fud-tactic-text{font-size:.8rem;line-height:1.5}

/* Value Equation */
.ve-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1.5rem}
.ve-card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:1.25rem;text-align:center}
.ve-card .ve-label{font-size:.75rem;font-weight:700;text-transform:uppercase;color:var(--text-dim);letter-spacing:.5px;margin-bottom:.5rem}
.ve-card .ve-score{font-size:2.5rem;font-weight:900;margin-bottom:.3rem}
.ve-card .ve-direction{font-size:.7rem;color:var(--text-dim)}
.ve-card .ve-bar{height:8px;background:var(--surface-2);border-radius:4px;margin-top:.75rem;overflow:hidden}
.ve-card .ve-bar-fill{height:100%;border-radius:4px;transition:width .8s}
.ve-overall{background:var(--surface);border:2px solid var(--accent);border-radius:16px;padding:1.5rem;text-align:center;margin-bottom:1.5rem}
.ve-overall .vo-score{font-size:3rem;font-weight:900;color:var(--accent-light)}
.ve-overall .vo-label{font-size:.85rem;color:var(--text-dim)}
.ve-recs{margin-top:1rem}
.ve-rec-item{background:var(--surface-2);border-radius:10px;padding:.75rem 1rem;margin-bottom:.5rem;font-size:.85rem;display:flex;gap:.5rem;align-items:flex-start}
.ve-rec-item::before{content:'\26A0';flex-shrink:0}

/* Message Hierarchy */
.mh-level{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:1.25rem;margin-bottom:1rem}
.mh-level-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:.75rem}
.mh-level-name{font-size:1rem;font-weight:700}
.mh-level-count{font-size:.75rem;color:var(--text-dim);background:var(--surface-2);padding:.2rem .6rem;border-radius:6px}
.mh-level-desc{font-size:.78rem;color:var(--text-dim);margin-bottom:.75rem}
.mh-quote-card{background:var(--surface-2);border-radius:10px;padding:.8rem 1rem;margin-bottom:.5rem;position:relative}
.mh-quote-text{font-size:.9rem;font-weight:500;line-height:1.5;margin-bottom:.3rem}
.mh-quote-usage{font-size:.7rem;color:var(--text-dim)}
.mh-top10{border:2px solid var(--accent);border-radius:16px;padding:1.5rem;margin-bottom:1.5rem}
.mh-top10 h3{font-size:1.1rem;font-weight:800;margin-bottom:1rem;color:var(--accent-light)}

/* PMF Proxy */
.pmf-container{text-align:center;margin-bottom:2rem}
.pmf-score{font-size:3.5rem;font-weight:900;margin-bottom:.3rem}
.pmf-label-text{font-size:1rem;font-weight:600;margin-bottom:1rem}
.pmf-breakdown{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;max-width:600px;margin:0 auto}
.pmf-segment{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1rem}
.pmf-segment .ps-num{font-size:1.5rem;font-weight:800}
.pmf-segment .ps-label{font-size:.7rem;color:var(--text-dim);text-transform:uppercase}

/* Recommendations */
.rec-card{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:1.5rem;margin-bottom:1rem;position:relative}
.rec-card .rec-num{position:absolute;top:-10px;left:20px;background:var(--accent);color:#fff;width:28px;height:28px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:.8rem;font-weight:800}
.rec-card h3{font-size:1rem;font-weight:700;margin-bottom:.5rem}
.rec-card p{font-size:.85rem;color:var(--text-dim);line-height:1.7}
.rec-card .rec-why{margin-top:.75rem;padding-top:.75rem;border-top:1px solid var(--border);font-size:.8rem}
.rec-card .rec-why strong{color:var(--accent-light)}

/* Comparison */
.compare-row{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;margin-bottom:2rem}
.compare-col{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:1.25rem}
.compare-col.col-a{border-top:3px solid var(--accent)}
.compare-col.col-b{border-top:3px solid var(--green)}
.compare-col-title{font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:1rem}
.compare-col.col-a .compare-col-title{color:var(--accent-light)}
.compare-col.col-b .compare-col-title{color:var(--green)}
.compare-stat{display:flex;justify-content:space-between;align-items:center;padding:.5rem 0;border-bottom:1px solid var(--border);font-size:.85rem}
.compare-stat:last-child{border-bottom:none}
.compare-stat-val{font-weight:700;color:var(--accent-light)}
.compare-col.col-b .compare-stat-val{color:var(--green)}
.shift-card{background:var(--surface-2);border-radius:12px;padding:1rem 1.25rem;margin-bottom:.75rem;display:flex;gap:1rem;align-items:flex-start}
.shift-card .shift-icon{font-size:1.2rem;flex-shrink:0;margin-top:2px}
.shift-card .shift-title{font-size:.9rem;font-weight:700;margin-bottom:.2rem}
.shift-card .shift-text{font-size:.8rem;color:var(--text-dim);line-height:1.6}
.delta-up{color:var(--green)}
.delta-down{color:var(--red)}
.delta-same{color:var(--text-dim)}

/* Responsive */
@media(max-width:900px){
  .fud-grid{grid-template-columns:1fr}
  .ve-grid{grid-template-columns:repeat(2,1fr)}
  .pmf-breakdown{grid-template-columns:repeat(2,1fr)}
}
@media(max-width:768px){
  .bar-label{width:120px;font-size:.75rem}
  .portrait-grid{grid-template-columns:1fr}
  .compare-row{grid-template-columns:1fr}
  .header h1{font-size:1.5rem}
  .container{padding:1rem}
  .force-label{width:100px}
  .ve-grid{grid-template-columns:1fr 1fr}
}
"""


# ──────────────────── JavaScript ────────────────────

JS = r"""
/* Navigation state */
let currentLaunch = 0;
let currentSource = {};
let currentSubtab = {};

function initDashboard() {
  showLaunch(0);
  setTimeout(function() {
    document.querySelectorAll('.bar-fill, .force-bar-fill, .fud-bar-fill, .ve-bar-fill').forEach(function(el) {
      if (el.dataset.width) el.style.width = el.dataset.width;
    });
  }, 150);
}

function showLaunch(idx) {
  currentLaunch = idx;
  document.querySelectorAll('.launch-pill').forEach(function(p) {
    p.classList.toggle('active', parseInt(p.dataset.launch) === idx);
  });
  document.querySelectorAll('.launch-panel').forEach(function(p) {
    p.classList.toggle('visible', parseInt(p.dataset.launch) === idx);
  });
  if (!currentSource[idx]) {
    var firstTab = document.querySelector('.launch-panel[data-launch="' + idx + '"] .source-tab');
    if (firstTab) currentSource[idx] = firstTab.dataset.source;
  }
  showSource(currentSource[idx] || '', idx);
}

function showSource(sourceKey, launchIdx) {
  if (launchIdx === undefined) launchIdx = currentLaunch;
  currentSource[launchIdx] = sourceKey;
  var panel = document.querySelector('.launch-panel[data-launch="' + launchIdx + '"]');
  if (!panel) return;
  panel.querySelectorAll('.source-tab').forEach(function(t) {
    t.classList.toggle('active', t.dataset.source === sourceKey);
  });
  panel.querySelectorAll('.source-panel').forEach(function(p) {
    p.classList.toggle('visible', p.dataset.source === sourceKey);
  });
  var cKey = launchIdx + '-' + sourceKey;
  if (!currentSubtab[cKey]) {
    var firstSub = panel.querySelector('.source-panel[data-source="' + sourceKey + '"] .subtab');
    if (firstSub) currentSubtab[cKey] = firstSub.dataset.subtab;
  }
  showSubtab(currentSubtab[cKey] || '', sourceKey, launchIdx);
}

function showSubtab(subtabKey, sourceKey, launchIdx) {
  if (launchIdx === undefined) launchIdx = currentLaunch;
  if (sourceKey === undefined) sourceKey = currentSource[launchIdx];
  var cKey = launchIdx + '-' + sourceKey;
  currentSubtab[cKey] = subtabKey;
  var sourcePanel = document.querySelector('.launch-panel[data-launch="' + launchIdx + '"] .source-panel[data-source="' + sourceKey + '"]');
  if (!sourcePanel) return;
  sourcePanel.querySelectorAll('.subtab').forEach(function(t) {
    t.classList.toggle('active', t.dataset.subtab === subtabKey);
  });
  sourcePanel.querySelectorAll('.section').forEach(function(s) {
    s.classList.toggle('visible', s.dataset.section === subtabKey);
  });
  setTimeout(function() {
    sourcePanel.querySelectorAll('.section.visible .bar-fill, .section.visible .force-bar-fill, .section.visible .fud-bar-fill, .section.visible .ve-bar-fill').forEach(function(el) {
      if (el.dataset.width) el.style.width = el.dataset.width;
    });
  }, 50);
}

function copyQuote(btn) {
  var box = btn.closest('.quote-box') || btn.closest('.mh-quote-card');
  var textEl = box.querySelector('.q-text') || box.querySelector('.mh-quote-text');
  if (!textEl) return;
  navigator.clipboard.writeText(textEl.textContent.trim()).then(function() {
    btn.textContent = 'OK';
    btn.classList.add('copied');
    setTimeout(function() { btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 1500);
  });
}

function toggleExpand(id) {
  var header = document.getElementById('eh-' + id);
  var body = document.getElementById('eb-' + id);
  if (!header || !body) return;
  header.classList.toggle('open');
  body.classList.toggle('open');
}

document.addEventListener('DOMContentLoaded', initDashboard);
"""


# ──────────────────── HTML Section Builders ────────────────────

def _build_bar_chart(items, color_fn=None, show_people=False, uid_prefix='') -> str:
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
        # Expandable quotes
        quotes = item.get('quotes', [])
        job = item.get('job', '')
        if quotes:
            eid = f'{uid_prefix}bar-{i}'
            lines.append(f'<div class="expandable-header" id="eh-{eid}" onclick="toggleExpand(\'{eid}\')">')
            lines.append(f'  <span class="arrow">\u25B6</span> <span style="font-size:.78rem;color:var(--text-dim)">{len(quotes)} цитат</span>')
            lines.append('</div>')
            lines.append(f'<div class="expandable-body" id="eb-{eid}">')
            if job:
                lines.append(f'<p style="font-size:.8rem;color:var(--accent-light);margin-bottom:.5rem">Job: {_esc(job)}</p>')
            for q in quotes:
                lines.append(f'<div class="quote-box"><span class="q-text">{_esc(q)}</span><button class="quote-copy" onclick="copyQuote(this)">Copy</button></div>')
            lines.append('</div>')
    lines.append('</div>')
    return '\n'.join(lines)


def _build_portraits(portraits) -> str:
    if not portraits:
        return '<p style="color:var(--text-dim)">Нет данных</p>'
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
        tags = p.get('tags', [])
        tag_colors = p.get('tag_colors', [])
        lines.append('<div>')
        for j, tag in enumerate(tags):
            color = tag_colors[j] if j < len(tag_colors) else 'blue'
            lines.append(f'<span class="portrait-tag tag-{color}">{_esc(tag)}</span>')
        lines.append('</div>')
        if p.get('who'):
            lines.append('<div class="portrait-section-label">Кто это</div>')
            lines.append(f'<p class="portrait-who">{_esc(p["who"])}</p>')
        for section, label, list_cls in [('wants', 'Желания', 'want-list'), ('pains', 'Боли', 'pain-list'), ('needs', 'Потребности', 'need-list')]:
            sec_items = p.get(section, [])
            if sec_items:
                lines.append(f'<div class="portrait-section-label">{label}</div>')
                lines.append(f'<ul class="portrait-list {list_cls}">')
                for w in sec_items:
                    lines.append(f'<li>{_esc(w)}</li>')
                lines.append('</ul>')
        lines.append('</div>')
    lines.append('</div>')
    return '\n'.join(lines)


def _build_forces(forces_data, uid_prefix='') -> str:
    if not forces_data:
        return '<p style="color:var(--text-dim)">Нет данных</p>'
    forces = forces_data.get('forces', [])
    balance = forces_data.get('balance_score', 0)
    flag = forces_data.get('flag', '')
    drive = forces_data.get('drive', 0)
    resist = forces_data.get('resist', 0)

    max_count = max((f['count'] for f in forces), default=1) or 1

    lines = []
    # Balance card
    if balance > 20:
        flag_cls = 'positive'
    elif balance < -10:
        flag_cls = 'warning'
    else:
        flag_cls = 'neutral'

    if balance > 0:
        score_color = 'var(--green)'
    elif balance < 0:
        score_color = 'var(--red)'
    else:
        score_color = 'var(--yellow)'

    lines.append(f'''<div class="forces-balance">
  <div class="fb-score" style="color:{score_color}">{balance:+.0f}</div>
  <div class="fb-label">Drive ({drive}) vs Resist ({resist})</div>
  <div class="fb-flag {flag_cls}">{_esc(flag)}</div>
</div>''')

    # Force bars
    lines.append('<div class="forces-container">')
    for f in forces:
        name = f['name']
        color = FORCE_COLORS.get(name, '#6c5ce7')
        label = FORCE_LABELS.get(name, name)
        pct = (f['count'] / max_count) * 100 if max_count else 0
        lines.append(f'''<div class="force-row">
  <div class="force-label"><div class="fl-name" style="color:{color}">{_esc(label)}</div><div class="fl-desc">{_esc(f.get("description", ""))}</div></div>
  <div class="force-bar-track"><div class="force-bar-fill" style="width:0%;background:{color}" data-width="{pct:.1f}%"></div></div>
  <div class="force-count" style="color:{color}">{f['count']}</div>
  <div class="force-people">{f.get('people', 0)} чел.</div>
</div>''')
        # Expandable quotes
        quotes = f.get('quotes', [])
        if quotes:
            eid = f'{uid_prefix}force-{name}'
            lines.append(f'<div class="expandable-header" id="eh-{eid}" onclick="toggleExpand(\'{eid}\')">')
            lines.append(f'  <span class="arrow">\u25B6</span> <span style="font-size:.78rem;color:var(--text-dim)">{len(quotes)} цитат</span>')
            lines.append('</div>')
            lines.append(f'<div class="expandable-body" id="eb-{eid}">')
            for q in quotes:
                lines.append(f'<div class="quote-box"><span class="q-text">{_esc(q)}</span><button class="quote-copy" onclick="copyQuote(this)">Copy</button></div>')
            lines.append('</div>')
    lines.append('</div>')
    return '\n'.join(lines)


def _build_jtbd_combined(jtbd, emotional, social, uid_prefix='') -> str:
    """Build Jobs to be Done section with 3 sub-sections."""
    lines = []
    lines.append('<h3 style="margin-bottom:1rem;font-weight:700;color:var(--accent-light)">\u25C6 Функциональные Jobs</h3>')
    lines.append(_build_bar_chart(jtbd or [], show_people=True, uid_prefix=uid_prefix + 'fj-'))
    lines.append('<h3 style="margin:2rem 0 1rem;font-weight:700;color:var(--blue)">\u25C6 Эмоциональные Jobs</h3>')
    lines.append(_build_bar_chart(emotional or [], show_people=True, uid_prefix=uid_prefix + 'ej-',
                                  color_fn=lambda i: 'linear-gradient(90deg, #74b9ff, #a29bfe)'))
    lines.append('<h3 style="margin:2rem 0 1rem;font-weight:700;color:var(--green)">\u25C6 Социальные Jobs</h3>')
    lines.append(_build_bar_chart(social or [], show_people=True, uid_prefix=uid_prefix + 'sj-',
                                  color_fn=lambda i: 'linear-gradient(90deg, #00cec9, #55efc4)'))
    return '\n'.join(lines)


def _build_fud(fud_data, uid_prefix='') -> str:
    if not fud_data:
        return '<p style="color:var(--text-dim)">Нет данных</p>'
    breakdown = fud_data.get('breakdown', [])
    total = fud_data.get('total', 0) or 1
    dominant = fud_data.get('dominant', '')

    lines = ['<div class="fud-grid">']
    for item in breakdown:
        name = item['name']
        color = FUD_COLORS.get(name, '#888')
        label = FUD_LABELS.get(name, name)
        fud_cls = f'fud-{name}'
        pct = (item['count'] / total) * 100 if total else 0
        is_dom = ' (доминирует)' if name == dominant else ''

        lines.append(f'<div class="fud-col {fud_cls}">')
        lines.append(f'  <div class="fud-col-title" style="color:{color}">{_esc(label)}{is_dom}</div>')
        lines.append(f'  <div class="fud-col-count" style="color:{color}">{item["count"]}</div>')
        lines.append(f'  <div class="fud-bar"><div class="fud-bar-fill" style="width:0%;background:{color}" data-width="{pct:.1f}%"></div></div>')

        for q in item.get('quotes', [])[:3]:
            lines.append(f'  <div class="quote-box"><span class="q-text">{_esc(q)}</span><button class="quote-copy" onclick="copyQuote(this)">Copy</button></div>')

        tactic = item.get('closing_tactic', '')
        if tactic:
            lines.append(f'''  <div class="fud-tactic">
    <div class="fud-tactic-label">Как закрывать</div>
    <div class="fud-tactic-text">{_esc(tactic)}</div>
  </div>''')
        lines.append('</div>')
    lines.append('</div>')
    return '\n'.join(lines)


def _build_value_equation(ve_data) -> str:
    if not ve_data:
        return '<p style="color:var(--text-dim)">Нет данных</p>'
    params = ve_data.get('parameters', [])
    overall = ve_data.get('overall_score', 0)
    recs = ve_data.get('recommendations', [])

    directions = {
        'dream_outcome': '\u2191 чем выше, тем лучше',
        'perceived_likelihood': '\u2191 чем выше, тем лучше',
        'time_delay': '\u2193 чем ниже, тем лучше',
        'effort_sacrifice': '\u2193 чем ниже, тем лучше',
    }

    lines = []
    o_color = 'var(--green)' if overall > 0 else 'var(--red)' if overall < 0 else 'var(--yellow)'
    lines.append(f'''<div class="ve-overall">
  <div class="vo-score" style="color:{o_color}">{overall:+.1f}</div>
  <div class="vo-label">Value Equation Score</div>
</div>''')

    lines.append('<div class="ve-grid">')
    for p in params:
        score = p['score']
        key = p['key']
        label = p['label']
        if key in ('time_delay', 'effort_sacrifice'):
            color = 'var(--green)' if score > 0 else 'var(--red)' if score < -5 else 'var(--yellow)'
        else:
            color = 'var(--green)' if score > 5 else 'var(--red)' if score < 0 else 'var(--yellow)'
        bar_pct = min(abs(score) * 3, 100)
        direction = directions.get(key, '')

        lines.append(f'''<div class="ve-card">
  <div class="ve-label">{_esc(label)}</div>
  <div class="ve-score" style="color:{color}">{score:+.1f}</div>
  <div class="ve-direction">{_esc(direction)}</div>
  <div class="ve-bar"><div class="ve-bar-fill" style="width:0%;background:{color}" data-width="{bar_pct:.0f}%"></div></div>
  <div style="font-size:.7rem;color:var(--text-dim);margin-top:.5rem">boost: {p['boost']} / weaken: {p['weaken']}</div>
</div>''')
    lines.append('</div>')

    if recs:
        lines.append('<div class="ve-recs">')
        for r in recs:
            lines.append(f'<div class="ve-rec-item">{_esc(r)}</div>')
        lines.append('</div>')

    return '\n'.join(lines)


def _build_message_hierarchy(mh_data, uid_prefix='') -> str:
    if not mh_data:
        return '<p style="color:var(--text-dim)">Нет данных</p>'
    levels = mh_data.get('levels', {})
    top10 = mh_data.get('top10', [])

    lines = []

    if top10:
        lines.append('<div class="mh-top10">')
        lines.append('<h3>\u2B50 ТОП-10 самых мощных цитат</h3>')
        for i, q in enumerate(top10):
            level = q.get('level', '')
            lines.append(f'''<div class="mh-quote-card">
  <div class="mh-quote-text">{_esc(q["quote"])}</div>
  <div class="mh-quote-usage">Score: {q["score"]} \u00b7 Level: {_esc(level)}</div>
  <button class="quote-copy" onclick="copyQuote(this)">Copy</button>
</div>''')
        lines.append('</div>')

    level_order = ['headline', 'proof', 'objection', 'desire', 'context']
    level_icons = {'headline': '\U0001F4E2', 'proof': '\U0001F4CA', 'objection': '\u26A0', 'desire': '\u2764', 'context': '\U0001F4DD'}
    for lname in level_order:
        ldata = levels.get(lname)
        if not ldata:
            continue
        icon = level_icons.get(lname, '')
        lines.append(f'''<div class="mh-level">
  <div class="mh-level-header">
    <div class="mh-level-name">{icon} {_esc(ldata["label"])}</div>
    <div class="mh-level-count">{ldata["count"]} цитат</div>
  </div>
  <div class="mh-level-desc">{_esc(ldata["description"])}</div>''')
        for q in ldata.get('quotes', []):
            lines.append(f'''  <div class="mh-quote-card">
    <div class="mh-quote-text">{_esc(q["quote"])}</div>
    <div class="mh-quote-usage">{_esc(q.get("usage", ""))}</div>
    <button class="quote-copy" onclick="copyQuote(this)">Copy</button>
  </div>''')
        lines.append('</div>')

    return '\n'.join(lines)


def _build_pmf(pmf_data) -> str:
    if not pmf_data:
        return '<p style="color:var(--text-dim)">Нет данных</p>'

    score = pmf_data.get('score', 0)
    level = pmf_data.get('level', 'red')
    label = pmf_data.get('label', '')
    hot = pmf_data.get('hot', 0)
    warm = pmf_data.get('warm', 0)
    curious = pmf_data.get('curious', 0)
    cold = pmf_data.get('cold', 0)

    color_map = {'green': 'var(--green)', 'yellow': 'var(--yellow)', 'red': 'var(--red)'}
    color = color_map.get(level, 'var(--text-dim)')

    lines = ['<div class="pmf-container">']
    lines.append(f'''<div class="pmf-score" style="color:{color}">{score:.1f}%</div>
<div class="pmf-label-text" style="color:{color}">{_esc(label)}</div>''')

    lines.append('<div class="pmf-breakdown">')
    segments = [
        (hot, '\U0001F525 Горячие', 'var(--red)'),
        (warm, '\u2600 Тёплые', 'var(--orange)'),
        (curious, '\U0001F50D Любопытные', 'var(--blue)'),
        (cold, '\u2744 Холодные', 'var(--text-dim)'),
    ]
    for val, seg_label, seg_color in segments:
        lines.append(f'''<div class="pmf-segment">
  <div class="ps-num" style="color:{seg_color}">{val}</div>
  <div class="ps-label">{seg_label}</div>
</div>''')
    lines.append('</div>')

    hot_quotes = pmf_data.get('hot_quotes', [])
    if hot_quotes:
        lines.append('<div style="text-align:left;margin-top:1.5rem">')
        lines.append('<h4 style="font-size:.9rem;font-weight:700;margin-bottom:.75rem">\U0001F525 Горячие цитаты</h4>')
        for q in hot_quotes:
            lines.append(f'<div class="quote-box"><span class="q-text">{_esc(q)}</span><button class="quote-copy" onclick="copyQuote(this)">Copy</button></div>')
        lines.append('</div>')

    warm_quotes = pmf_data.get('warm_quotes', [])
    if warm_quotes:
        lines.append('<div style="text-align:left;margin-top:1rem">')
        lines.append('<h4 style="font-size:.9rem;font-weight:700;margin-bottom:.75rem">\u2600 Тёплые цитаты</h4>')
        for q in warm_quotes:
            lines.append(f'<div class="quote-box"><span class="q-text">{_esc(q)}</span><button class="quote-copy" onclick="copyQuote(this)">Copy</button></div>')
        lines.append('</div>')

    lines.append('</div>')
    return '\n'.join(lines)


def _build_recommendations(recs) -> str:
    if not recs:
        return '<p style="color:var(--text-dim)">Нет данных</p>'
    lines = []
    for i, rec in enumerate(recs, 1):
        lines.append(f'''<div class="rec-card">
  <div class="rec-num">{i}</div>
  <h3>{_esc(rec["title"])}</h3>
  <p>{_esc(rec["text"])}</p>
  <div class="rec-why"><strong>Как применить:</strong> {_esc(rec["action"])}</div>
</div>''')
    return '\n'.join(lines)


def _build_comparison(sources) -> str:
    """Build comparison between multiple chat day sources."""
    chat_sources = [s for s in sources if s.get('type') == 'chat' and s.get('data')]
    if len(chat_sources) < 2:
        return '<p style="color:var(--text-dim)">Нужно минимум 2 источника для сравнения</p>'

    lines = []
    lines.append('<div class="section-title">\u2194 Сравнение дней</div>')

    # Stats comparison
    lines.append('<div class="compare-row">')
    for i, src in enumerate(chat_sources[:2]):
        col_cls = 'col-a' if i == 0 else 'col-b'
        data = src['data']
        s = data.get('stats', {})
        lines.append(f'<div class="compare-col {col_cls}">')
        lines.append(f'<div class="compare-col-title">{_esc(src["label"])}</div>')
        lines.append(f'<div class="compare-stat"><span>Сообщений</span><span class="compare-stat-val">{s.get("total_messages", 0)}</span></div>')
        lines.append(f'<div class="compare-stat"><span>Участников</span><span class="compare-stat-val">{s.get("unique_people", 0)}</span></div>')
        lines.append('</div>')
    lines.append('</div>')

    # Jobs comparison
    lines.append('<h3 style="margin:1.5rem 0 1rem;font-weight:700">Jobs to be Done</h3>')
    lines.append('<div class="compare-row">')
    for i, src in enumerate(chat_sources[:2]):
        col_cls = 'col-a' if i == 0 else 'col-b'
        data = src['data']
        lines.append(f'<div class="compare-col {col_cls}">')
        lines.append(f'<div class="compare-col-title">{_esc(src["label"])}</div>')
        for j in data.get('jtbd', [])[:5]:
            lines.append(f'<div class="compare-stat"><span>{_esc(j["name"])}</span><span class="compare-stat-val">{j["count"]}</span></div>')
        lines.append('</div>')
    lines.append('</div>')

    # FUD comparison
    lines.append('<h3 style="margin:1.5rem 0 1rem;font-weight:700">FUD-анализ</h3>')
    lines.append('<div class="compare-row">')
    for i, src in enumerate(chat_sources[:2]):
        col_cls = 'col-a' if i == 0 else 'col-b'
        data = src['data']
        fud = data.get('fud', {})
        lines.append(f'<div class="compare-col {col_cls}">')
        lines.append(f'<div class="compare-col-title">{_esc(src["label"])}</div>')
        for fb in fud.get('breakdown', []):
            lines.append(f'<div class="compare-stat"><span>{_esc(FUD_LABELS.get(fb["name"], fb["name"]))}</span><span class="compare-stat-val">{fb["count"]}</span></div>')
        lines.append('</div>')
    lines.append('</div>')

    # Key shifts
    lines.append('<h3 style="margin:1.5rem 0 1rem;font-weight:700">Ключевые сдвиги</h3>')
    d1_jobs = {j['name']: j['count'] for j in chat_sources[0]['data'].get('jtbd', [])}
    d2_jobs = {j['name']: j['count'] for j in chat_sources[1]['data'].get('jtbd', [])}
    all_names = list(dict.fromkeys(list(d1_jobs.keys()) + list(d2_jobs.keys())))
    for jname in all_names[:8]:
        v1 = d1_jobs.get(jname, 0)
        v2 = d2_jobs.get(jname, 0)
        if v1 == 0 and v2 == 0:
            continue
        if v2 > v1:
            icon = '\u2191'
            cls = 'delta-up'
        elif v2 < v1:
            icon = '\u2193'
            cls = 'delta-down'
        else:
            icon = '\u2194'
            cls = 'delta-same'
        lines.append(f'''<div class="shift-card">
  <div class="shift-icon {cls}">{icon}</div>
  <div>
    <div class="shift-title">{_esc(jname)}</div>
    <div class="shift-text">{_esc(chat_sources[0]["label"])}: {v1} \u2192 {_esc(chat_sources[1]["label"])}: {v2}</div>
  </div>
</div>''')

    return '\n'.join(lines)


def _build_combined_analysis(sources) -> str:
    """Build aggregate view across all sources."""
    all_data = [s['data'] for s in sources if s.get('data')]
    if not all_data:
        return '<p style="color:var(--text-dim)">Нет данных</p>'

    lines = []
    lines.append('<div class="section-title">\U0001F4CA Сводный анализ</div>')

    total_msgs = sum(d.get('stats', {}).get('total_messages', 0) for d in all_data)
    total_people = sum(d.get('stats', {}).get('unique_people', 0) for d in all_data)
    lines.append(f'''<div class="stats-row" style="margin-bottom:2rem">
  <div class="stat-badge"><div class="num">{total_people}</div><div class="label">участников (всего)</div></div>
  <div class="stat-badge"><div class="num">{total_msgs}</div><div class="label">сообщений (всего)</div></div>
  <div class="stat-badge"><div class="num">{len(sources)}</div><div class="label">источников</div></div>
</div>''')

    # Source breakdown
    lines.append('<h3 style="margin-bottom:1rem;font-weight:700">По источникам</h3>')
    for src in sources:
        if not src.get('data'):
            continue
        s = src['data'].get('stats', {})
        lines.append(f'''<div class="shift-card">
  <div class="shift-icon">\U0001F4C4</div>
  <div>
    <div class="shift-title">{_esc(src["label"])}</div>
    <div class="shift-text">{s.get("total_messages", 0)} сообщений \u00b7 {s.get("unique_people", 0)} участников</div>
  </div>
</div>''')

    # Aggregate top jobs
    job_agg = {}
    for d in all_data:
        for j in d.get('jtbd', []):
            name = j['name']
            if name not in job_agg:
                job_agg[name] = {'name': name, 'count': 0, 'people': 0}
            job_agg[name]['count'] += j['count']
            job_agg[name]['people'] += j.get('people', 0)
    top_jobs = sorted(job_agg.values(), key=lambda x: x['count'], reverse=True)[:10]

    if top_jobs:
        lines.append('<h3 style="margin:2rem 0 1rem;font-weight:700">ТОП Jobs (агрегат)</h3>')
        lines.append(_build_bar_chart(top_jobs, show_people=True, uid_prefix='combined-jobs-'))

    return '\n'.join(lines)


# ──────────────────── Source panel builder ────────────────────

ANALYSIS_SUBTABS = [
    ('portraits', 'Портреты ЦА'),
    ('forces', 'Forces of Progress'),
    ('jtbd', 'Jobs to be Done'),
    ('fud', 'FUD-анализ'),
    ('products', 'Желаемые продукты'),
    ('professions', 'Ниши аудитории'),
    ('value_eq', 'Value Equation'),
    ('msg_hierarchy', 'Цитаты для контента'),
    ('pmf', 'PMF Score'),
    ('recs', 'Рекомендации'),
]


def _build_source_panel(source, launch_idx, source_idx) -> str:
    """Build a complete source panel with subtabs and all analysis sections."""
    data = source.get('data')
    source_key = f's{source_idx}'

    if not data:
        return f'<div class="source-panel" data-source="{source_key}"><p style="color:var(--text-dim)">Нет данных</p></div>'

    uid = f'l{launch_idx}-{source_key}-'
    lines = [f'<div class="source-panel" data-source="{source_key}">']

    # Subtabs
    lines.append('<div class="subtabs">')
    for i, (key, label) in enumerate(ANALYSIS_SUBTABS):
        active = ' active' if i == 0 else ''
        lines.append(f'  <div class="subtab{active}" data-subtab="{key}" onclick="showSubtab(\'{key}\', \'{source_key}\', {launch_idx})">{label}</div>')
    lines.append('</div>')

    # Portraits
    lines.append('<div class="section visible" data-section="portraits">')
    lines.append('<div class="section-title">Портреты ЦА</div>')
    lines.append(_build_portraits(data.get('portraits', [])))
    lines.append('</div>')

    # Forces of Progress
    lines.append('<div class="section" data-section="forces">')
    lines.append('<div class="section-title">Forces of Progress</div>')
    lines.append(_build_forces(data.get('forces'), uid_prefix=uid))
    lines.append('</div>')

    # JTBD (combined: functional + emotional + social)
    lines.append('<div class="section" data-section="jtbd">')
    lines.append('<div class="section-title">Jobs to be Done</div>')
    lines.append(_build_jtbd_combined(
        data.get('jtbd', []),
        data.get('emotional_jobs', []),
        data.get('social_jobs', []),
        uid_prefix=uid,
    ))
    lines.append('</div>')

    # FUD
    lines.append('<div class="section" data-section="fud">')
    lines.append('<div class="section-title">FUD-анализ</div>')
    lines.append(_build_fud(data.get('fud'), uid_prefix=uid))
    lines.append('</div>')

    # Products
    lines.append('<div class="section" data-section="products">')
    lines.append('<div class="section-title">Желаемые продукты</div>')
    lines.append(_build_bar_chart(data.get('products', []), uid_prefix=uid + 'prod-'))
    lines.append('</div>')

    # Professions
    lines.append('<div class="section" data-section="professions">')
    lines.append('<div class="section-title">Ниши аудитории</div>')
    lines.append(_build_bar_chart(data.get('professions', []), show_people=True, uid_prefix=uid + 'prof-'))
    lines.append('</div>')

    # Value Equation
    lines.append('<div class="section" data-section="value_eq">')
    lines.append('<div class="section-title">Value Equation</div>')
    lines.append(_build_value_equation(data.get('value_equation')))
    lines.append('</div>')

    # Message Hierarchy
    lines.append('<div class="section" data-section="msg_hierarchy">')
    lines.append('<div class="section-title">Цитаты для контента (Message Hierarchy)</div>')
    lines.append(_build_message_hierarchy(data.get('message_hierarchy'), uid_prefix=uid))
    lines.append('</div>')

    # PMF Proxy
    lines.append('<div class="section" data-section="pmf">')
    lines.append('<div class="section-title">PMF Proxy Score</div>')
    lines.append(_build_pmf(data.get('pmf_proxy')))
    lines.append('</div>')

    # Recommendations
    lines.append('<div class="section" data-section="recs">')
    lines.append('<div class="section-title">Рекомендации</div>')
    lines.append(_build_recommendations(data.get('recommendations', [])))
    lines.append('</div>')

    lines.append('</div>')  # source-panel
    return '\n'.join(lines)


# ──────────────────── Main builder ────────────────────

def build_dashboard(launches, day2_data=None) -> str:
    """
    Build a complete HTML dashboard string.

    New API:
        build_dashboard(launches: list[dict]) -> str

    Legacy API (backward compatible):
        build_dashboard(day1_data: dict, day2_data: dict = None) -> str

    Args:
        launches: List of launch dicts, or a single analysis dict (legacy).
        day2_data: Optional second day data (legacy mode only).

    Returns:
        Complete HTML string.
    """
    # Handle legacy call: build_dashboard(day1_data, day2_data=None)
    if isinstance(launches, dict):
        launches = [_legacy_to_launch(launches, day2_data)]

    if not launches:
        return '<html><body><h1>Нет данных</h1></body></html>'

    # Compute global stats
    total_msgs = 0
    total_people = 0
    total_sources = 0
    for launch in launches:
        for src in launch.get('sources', []):
            data = src.get('data')
            if data:
                total_msgs += data.get('stats', {}).get('total_messages', 0)
                total_people += data.get('stats', {}).get('unique_people', 0)
                total_sources += 1

    first_name = launches[0].get('name', 'Анализ аудитории')
    first_dates = launches[0].get('dates', '')

    # Build launch panels
    launch_pills = []
    launch_panels = []

    for li, launch in enumerate(launches):
        name = launch.get('name', f'Запуск {li + 1}')
        dates = launch.get('dates', '')
        sources = launch.get('sources', [])
        active = ' active' if li == 0 else ''

        launch_pills.append(
            f'<div class="launch-pill{active}" data-launch="{li}" onclick="showLaunch({li})">'
            f'<div class="lp-name">{_esc(name)}</div>'
            f'<div class="lp-dates">{_esc(dates)}</div>'
            f'<div class="lp-badge">{len(sources)}</div>'
            f'</div>'
        )

        visible = ' visible' if li == 0 else ''
        panel_lines = [f'<div class="launch-panel{visible}" data-launch="{li}">']

        # Source tabs
        has_comparison = len([s for s in sources if s.get('type') == 'chat']) >= 2
        panel_lines.append('<div class="source-tabs">')
        for si, src in enumerate(sources):
            src_key = f's{si}'
            src_active = ' active' if si == 0 else ''
            src_type = src.get('type', 'chat')
            panel_lines.append(
                f'<div class="source-tab{src_active}" data-source="{src_key}" data-type="{src_type}" '
                f'onclick="showSource(\'{src_key}\', {li})">{_esc(src["label"])}</div>'
            )
        if has_comparison:
            panel_lines.append(
                f'<div class="source-tab" data-source="compare" data-type="comparison" '
                f'onclick="showSource(\'compare\', {li})">Сравнение</div>'
            )
        if len(sources) > 1:
            panel_lines.append(
                f'<div class="source-tab" data-source="combined" data-type="combined" '
                f'onclick="showSource(\'combined\', {li})">Сводный анализ</div>'
            )
        panel_lines.append('</div>')

        # Source panels
        for si, src in enumerate(sources):
            panel_lines.append(_build_source_panel(src, li, si))

        # Comparison panel
        if has_comparison:
            panel_lines.append('<div class="source-panel" data-source="compare">')
            panel_lines.append(_build_comparison(sources))
            panel_lines.append('</div>')

        # Combined panel
        if len(sources) > 1:
            panel_lines.append('<div class="source-panel" data-source="combined">')
            panel_lines.append(_build_combined_analysis(sources))
            panel_lines.append('</div>')

        panel_lines.append('</div>')  # launch-panel
        launch_panels.append('\n'.join(panel_lines))

    # Show launch bar only if multiple launches
    launch_bar_html = ''
    if len(launches) > 1:
        launch_bar_html = '<div class="launch-bar">\n' + '\n'.join(launch_pills) + '\n</div>'

    # Assemble final HTML
    newline = '\n'
    html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JTBD-анализ аудитории \u2014 {_esc(first_name)}</title>
<style>
{CSS}
</style>
</head>
<body>

<div class="container">

  <div class="header">
    <h1>Анализ целевой аудитории</h1>
    <div class="subtitle">{_esc(first_name)} &middot; {_esc(first_dates)}</div>
    <div class="stats-row">
      <div class="stat-badge"><div class="num">{total_people}</div><div class="label">участников</div></div>
      <div class="stat-badge"><div class="num">{total_msgs}</div><div class="label">сообщений</div></div>
      <div class="stat-badge"><div class="num">{total_sources}</div><div class="label">источников</div></div>
      <div class="stat-badge"><div class="num">{len(launches)}</div><div class="label">запусков</div></div>
    </div>
  </div>

  {launch_bar_html}

  {newline.join(launch_panels)}

</div>

<script>
{JS}
</script>

</body>
</html>'''

    return html


# ──────────────────── Legacy compatibility ────────────────────

def _legacy_to_launch(day1_data: dict, day2_data: dict = None) -> dict:
    """Convert old-style call to new launch format."""
    sources = [{'type': 'chat', 'label': 'День 1', 'data': day1_data}]
    if day2_data:
        sources.append({'type': 'chat', 'label': 'День 2', 'data': day2_data})
    return {
        'id': 'legacy',
        'name': 'Анализ аудитории',
        'dates': '',
        'sources': sources,
    }
