import streamlit as st
import requests
import re
import html as html_lib
import json
from datetime import datetime, timedelta

# ──────────────────────────────────────────────────────────
# AUTO REFRESH — हर 2 घंटे (7200 सेकंड)
# ──────────────────────────────────────────────────────────
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=7200 * 1000, key="auto_news_refresh")
except ImportError:
    pass   # library install न हो तो silently skip

# ──────────────────────────────────────────────────────────
# 🔑  SECRETS / SESSION
# ──────────────────────────────────────────────────────────
def get_secret(key: str) -> str:
    try:
        val = st.secrets.get(key, "")
        if val:
            return val
    except Exception:
        pass
    return st.session_state.get(key, "")


def strip_html(text: str) -> str:
    if not text:
        return ""
    text = html_lib.unescape(text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&[a-zA-Z#0-9]+;', ' ', text)
    text = re.sub(r'\[\+\d+\s*chars?\]', '', text)
    return ' '.join(text.split()).strip()


# ──────────────────────────────────────────────────────────
# ⚙️  PAGE CONFIG
# ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="UP Cyber Shield",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────
# 🎨  THEME — Dark / Light
# ──────────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"

DARK = {
    "bg":        "#050a14",
    "bg2":       "#0b1422",
    "text":      "#e0eaff",
    "subtext":   "#7090b0",
    "accent":    "#00e5ff",
    "border":    "rgba(0,229,255,0.18)",
    "card_bg":   "#0b1422",
    "hr":        "rgba(0,229,255,0.1)",
    "tip_text":  "#a0b8d0",
}
LIGHT = {
    "bg":        "#f0f4ff",
    "bg2":       "#ffffff",
    "text":      "#0a1628",
    "subtext":   "#4a6080",
    "accent":    "#0070a8",
    "border":    "rgba(0,100,180,0.25)",
    "card_bg":   "#ffffff",
    "hr":        "rgba(0,100,180,0.15)",
    "tip_text":  "#334455",
}
T = DARK if st.session_state["theme"] == "dark" else LIGHT

# ──────────────────────────────────────────────────────────
# 🎨  CSS — Dynamic (theme-aware) + Skeleton + Mobile
# ──────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700&family=Noto+Sans+Devanagari:wght@400;600&family=Share+Tech+Mono&display=swap');

html, body, [class*="css"] {{
    font-family: 'Rajdhani', 'Noto Sans Devanagari', sans-serif;
    background-color: {T['bg']} !important;
    color: {T['text']} !important;
}}
.stApp {{ background: {T['bg']} !important; }}

/* ── HEADER ── */
.cyber-header {{ text-align:center; padding:1.5rem 0 0.5rem; }}
.cyber-title {{
    font-family:'Share Tech Mono',monospace;
    font-size:2.4rem; font-weight:700; letter-spacing:6px;
    background:linear-gradient(135deg,#00e5ff,#ffffff,#00e5ff);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}}
.cyber-sub {{ color:{T['accent']}; font-size:0.95rem; letter-spacing:2px; opacity:0.8; }}
.cyber-line {{
    height:2px;
    background:linear-gradient(90deg,transparent,#00e5ff,#ff4b4b,#00e5ff,transparent);
    max-width:500px; margin:1rem auto; border-radius:2px;
}}

/* ── METRICS ── */
.metric-row {{ display:grid; grid-template-columns:repeat(4,1fr); gap:0.8rem; margin:1rem 0; }}
@media(max-width:600px){{ .metric-row {{ grid-template-columns:repeat(2,1fr); }} }}
.mcard {{ background:{T['card_bg']}; border:1px solid {T['border']}; border-radius:10px; padding:1rem; text-align:center; }}
.mcard .num {{ font-family:'Share Tech Mono',monospace; font-size:2rem; font-weight:700; }}
.mcard .lbl {{ font-size:0.72rem; color:{T['subtext']}; letter-spacing:1px; text-transform:uppercase; margin-top:0.2rem; }}
.mcard.c1 .num{{color:#00e5ff;}} .mcard.c1{{border-top:3px solid #00e5ff;}}
.mcard.c2 .num{{color:#ff4b4b;}} .mcard.c2{{border-top:3px solid #ff4b4b;}}
.mcard.c3 .num{{color:#39ff14;}} .mcard.c3{{border-top:3px solid #39ff14;}}
.mcard.c4 .num{{color:#ffd700;}} .mcard.c4{{border-top:3px solid #ffd700;}}

/* ── TICKER ── */
.ticker {{
    background:{T['card_bg']}; border:1px solid {T['border']};
    border-radius:8px; padding:0.5rem 1rem; margin-bottom:1rem;
    font-size:0.82rem; color:{T['subtext']};
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}}
.ticker b {{ color:#ff4b4b; font-family:'Share Tech Mono',monospace; font-size:0.7rem; letter-spacing:2px; }}

/* ── DEMO BANNER ── */
.demo-banner {{
    background:linear-gradient(135deg,rgba(255,165,0,0.15),rgba(255,100,0,0.1));
    border:1px solid rgba(255,165,0,0.5); border-left:4px solid #ffa500;
    border-radius:8px; padding:0.6rem 1rem; margin-bottom:1rem;
    font-family:'Share Tech Mono',monospace; font-size:0.78rem;
    color:#ffa500; letter-spacing:1px;
}}

/* ── NEWS CARD ── */
.news-item {{
    border-left:4px solid {T['accent']};
    padding:1rem 1.2rem; margin-bottom:0.6rem;
    background:{T['card_bg']}; border-radius:0 10px 10px 0;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}}
.news-item:hover {{ transform:translateX(3px); box-shadow:0 4px 20px rgba(0,229,255,0.1); }}
.news-item.neg {{ border-left-color:#ff4b4b; }}
.news-item.pos {{ border-left-color:#39ff14; }}
.news-item.aw  {{ border-left-color:#ffd700; }}
.news-item .ntitle {{ font-weight:700; font-size:1.05rem; color:{T['text']}; line-height:1.4; }}
.news-item .nmeta  {{ font-size:0.72rem; color:{T['subtext']}; margin:0.3rem 0; font-family:'Share Tech Mono',monospace; }}
.news-item .ndesc  {{
    font-family:'Noto Sans Devanagari',sans-serif;
    font-size:0.9rem; color:{'#c0d0e8' if T['bg']=='#050a14' else '#334455'}; line-height:1.8;
    margin-top:0.5rem; border-top:1px solid rgba(128,128,128,0.12); padding-top:0.5rem;
}}
.bookmark-badge {{
    display:inline-block; background:rgba(255,215,0,0.15);
    border:1px solid rgba(255,215,0,0.4); border-radius:20px;
    padding:0.15rem 0.6rem; font-size:0.68rem;
    color:#ffd700; font-family:'Share Tech Mono',monospace;
    margin-left:0.5rem; vertical-align:middle;
}}
.read-link {{
    display:inline-block; margin-top:0.6rem; padding:0.3rem 0.9rem;
    background:rgba(0,229,255,0.1); border:1px solid rgba(0,229,255,0.35);
    border-radius:20px; color:{T['accent']} !important;
    font-size:0.78rem; font-family:'Share Tech Mono',monospace;
    letter-spacing:1px; text-decoration:none !important;
}}
.read-link:hover {{ background:rgba(0,229,255,0.2); }}

/* ── AI BOX ── */
.ai-box {{
    background:linear-gradient(135deg,rgba(0,229,255,0.07),rgba(255,75,75,0.05));
    border:1px solid rgba(0,229,255,0.22); border-radius:10px;
    padding:1rem 1.2rem; margin:0.5rem 0;
    font-family:'Noto Sans Devanagari',sans-serif;
    font-size:0.9rem; line-height:1.8; color:{T['text']}; white-space:pre-wrap;
}}

/* ── POST CARD ── */
.post-card {{
    background:linear-gradient(135deg,{'#0d1f35,#0a1528' if T['bg']=='#050a14' else '#e8f4ff,#f0f8ff'});
    border:1px solid rgba(0,229,255,0.3); border-radius:14px;
    padding:1.4rem 1.6rem; margin:0.8rem 0; position:relative; overflow:hidden;
}}
.post-card::before {{
    content:''; position:absolute; top:0; left:0; right:0; height:3px;
    background:linear-gradient(90deg,#00e5ff,#ff4b4b,#ffd700,#39ff14);
}}
.post-card .platform-badge {{
    display:inline-block; background:rgba(0,229,255,0.15);
    border:1px solid rgba(0,229,255,0.3); border-radius:20px;
    padding:0.2rem 0.8rem; font-family:'Share Tech Mono',monospace;
    font-size:0.7rem; color:#00e5ff; letter-spacing:1px; margin-bottom:0.8rem;
}}
.post-card .post-text {{
    font-family:'Noto Sans Devanagari',sans-serif; font-size:1rem;
    line-height:1.9; color:{T['text']}; white-space:pre-wrap;
}}
.post-card .char-count {{
    font-family:'Share Tech Mono',monospace; font-size:0.68rem;
    color:{T['subtext']}; margin-top:0.8rem; text-align:right;
}}

/* ── TIP CARD ── */
.tip-card {{
    background:{T['card_bg']}; border:1px solid {T['border']};
    border-radius:10px; padding:1rem; margin-bottom:0.8rem;
}}

/* ── SKELETON LOADING ── */
.skeleton {{
    background: linear-gradient(90deg, {T['card_bg']} 25%, rgba(0,229,255,0.06) 50%, {T['card_bg']} 75%);
    background-size: 400% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 8px; margin-bottom: 0.5rem;
}}
@keyframes shimmer {{ 0%{{background-position:100% 0}} 100%{{background-position:-100% 0}} }}
.skel-title  {{ height:22px; width:75%; margin-bottom:8px; }}
.skel-meta   {{ height:14px; width:40%; margin-bottom:12px; }}
.skel-body   {{ height:80px; width:100%; }}
.skel-card   {{
    border-left:4px solid rgba(0,229,255,0.2); padding:1rem 1.2rem;
    margin-bottom:0.6rem; background:{T['card_bg']}; border-radius:0 10px 10px 0;
}}

/* ── SEARCH BOX ── */
.stTextInput > div > input {{
    background:{T['card_bg']} !important; color:{T['text']} !important;
    border:1px solid {T['border']} !important; border-radius:8px !important;
    font-family:'Share Tech Mono',monospace !important;
}}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {{
    background:{T['card_bg']} !important; border-radius:10px !important;
    padding:3px !important; border:1px solid {T['border']} !important;
    flex-wrap:wrap !important;
}}
.stTabs [data-baseweb="tab"] {{
    background:transparent !important; color:{T['subtext']} !important;
    border-radius:7px !important; font-family:'Rajdhani',sans-serif !important;
    font-weight:600 !important; padding:6px 12px !important;
}}
.stTabs [aria-selected="true"] {{
    background:rgba(0,229,255,0.15) !important;
    color:{T['accent']} !important; border:1px solid rgba(0,229,255,0.3) !important;
}}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {{
    background:{'rgba(5,10,20,0.97)' if T['bg']=='#050a14' else 'rgba(230,240,255,0.97)'} !important;
    border-right:1px solid {T['border']} !important;
}}
@media(max-width:768px){{
    section[data-testid="stSidebar"] {{ width:260px !important; }}
}}

/* ── BUTTONS ── */
.stButton > button {{
    background:linear-gradient(135deg,rgba(0,229,255,0.15),rgba(0,229,255,0.05)) !important;
    border:1px solid rgba(0,229,255,0.4) !important; color:{T['accent']} !important;
    border-radius:8px !important; font-family:'Share Tech Mono',monospace !important;
    transition: all 0.2s ease !important;
}}
.stButton > button:hover {{
    background:linear-gradient(135deg,rgba(0,229,255,0.28),rgba(0,229,255,0.12)) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(0,229,255,0.2) !important;
}}

/* ── CHAT BUBBLE ── */
.chat-user {{
    background:rgba(0,229,255,0.1); border:1px solid rgba(0,229,255,0.25);
    border-radius:12px 12px 2px 12px; padding:0.7rem 1rem; margin:0.4rem 0;
    font-family:'Noto Sans Devanagari',sans-serif; font-size:0.9rem; color:{T['text']};
    max-width:80%; margin-left:auto; text-align:right;
}}
.chat-ai {{
    background:rgba(57,255,20,0.07); border:1px solid rgba(57,255,20,0.2);
    border-radius:2px 12px 12px 12px; padding:0.7rem 1rem; margin:0.4rem 0;
    font-family:'Noto Sans Devanagari',sans-serif; font-size:0.9rem; color:{T['text']};
    max-width:85%; white-space:pre-wrap; line-height:1.7;
}}
.chat-label {{
    font-family:'Share Tech Mono',monospace; font-size:0.65rem;
    color:{T['subtext']}; margin-bottom:0.2rem; letter-spacing:1px;
}}

/* ── GSHEET STATUS ── */
.gsheet-ok  {{ color:#39ff14; font-family:'Share Tech Mono',monospace; font-size:0.8rem; }}
.gsheet-off {{ color:#ffa500; font-family:'Share Tech Mono',monospace; font-size:0.8rem; }}

/* ── TREND CARD ── */
.trend-card {{
    background:linear-gradient(135deg,rgba(0,229,255,0.07),rgba(57,255,20,0.04));
    border:1px solid rgba(0,229,255,0.2); border-radius:12px;
    padding:1.2rem 1.4rem; margin-bottom:1rem;
    font-family:'Noto Sans Devanagari',sans-serif;
    font-size:0.92rem; line-height:1.8; color:{T['text']};
    white-space:pre-wrap;
}}

hr {{ border-color:{T['hr']} !important; }}
#MainMenu, footer, header {{ visibility:hidden; }}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────
# 🔧  SESSION STATE INIT
# ──────────────────────────────────────────────────────────
DEFAULTS = {
    "news_api_key":  "",
    "groq_api_key":  "",
    "gsheet_url":    "",
    "ai_results":    {},
    "using_demo":    True,
    "bookmarks":     [],
    "chat_history":  [],
    "articles_cache": [],
    "last_fetch":    None,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ──────────────────────────────────────────────────────────
# 🔧  API HELPERS
# ──────────────────────────────────────────────────────────
def fetch_news(api_key: str, query: str = "cyber crime Uttar Pradesh") -> list:
    if not api_key:
        return []
    url = (
        "https://newsapi.org/v2/everything"
        f"?q={requests.utils.quote(query)}"
        "&language=en&sortBy=publishedAt&pageSize=20"
        f"&from={(datetime.now()-timedelta(days=14)).strftime('%Y-%m-%d')}"
        f"&apiKey={api_key}"
    )
    try:
        r = requests.get(url, timeout=10)
        return r.json().get("articles", [])
    except Exception:
        return []


def groq_call(api_key: str, prompt: str, system: str = "", max_tokens: int = 600) -> str:
    if not api_key:
        return "Groq API key sidebar mein enter karein."
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    models = ["llama-3.1-8b-instant", "llama3-8b-8192", "mixtral-8x7b-32768"]
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    for model in models:
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json={"model": model, "messages": messages,
                      "max_tokens": max_tokens, "temperature": 0.65},
                timeout=30,
            )
            data = r.json()
            if "choices" in data:
                return data["choices"][0]["message"]["content"].strip()
        except Exception:
            continue
    return "Groq API se response nahi mila. API key check karein."


def groq_summarize(api_key: str, text: str) -> str:
    return groq_call(
        api_key,
        f"Khabar:\n{text[:1800]}",
        system=(
            "Tum UP Police ke cyber crime awareness assistant ho. "
            "Sirf Hindi mein 3 bullet points mein summarize karo. "
            "Format: • pehli baat\n• doosri baat\n• teesri baat\n"
            "Koi English preamble nahi."
        ),
        max_tokens=300,
    )


def groq_trend_analyze(api_key: str, all_articles: list) -> str:
    headlines = "\n".join(f"- {a['title']} ({a['date']})" for a in all_articles[:12])
    return groq_call(
        api_key,
        f"Yeh hain recent cyber crime headlines UP se:\n{headlines}",
        system=(
            "Tum UP Police ke senior cyber analyst ho. In headlines ko dekh kar "
            "SIRF HINDI mein analysis do:\n"
            "1. Is hafte ka sabse bada trend kya hai?\n"
            "2. Kaunsa district/area sabse zyada affected hai?\n"
            "3. Kaunsi fraud type sabse common hai?\n"
            "4. Police ke liye 2 actionable recommendations.\n"
            "Concise rakho, bullet points use karo."
        ),
        max_tokens=500,
    )


def groq_chat(api_key: str, question: str, history: list) -> str:
    msgs = []
    for h in history[-6:]:   # last 6 turns context
        msgs.append({"role": h["role"], "content": h["content"]})
    msgs.append({"role": "user", "content": question})
    if not api_key:
        return "Groq API key sidebar mein daalein."
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    system = (
        "Tum 'Cyber Shield Assistant' ho — UP Police ka AI cyber crime expert. "
        "Sirf Hindi mein jawab do. Aam insaan ki bhasha mein samjhao. "
        "Hamesha 1930 helpline aur cybercrime.gov.in mention karo jab relevant ho. "
        "Short, clear answers do. Bullet points use karo jab list ho."
    )
    full_msgs = [{"role": "system", "content": system}] + msgs
    for model in ["llama-3.1-8b-instant", "llama3-8b-8192"]:
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json={"model": model, "messages": full_msgs,
                      "max_tokens": 500, "temperature": 0.7},
                timeout=25,
            )
            data = r.json()
            if "choices" in data:
                return data["choices"][0]["message"]["content"].strip()
        except Exception:
            continue
    return "Response nahi mila."


# ── Google Sheets push (Web App URL mode) ──
def push_to_gsheet(ws_url: str, articles: list) -> tuple[bool, str]:
    """
    Google Apps Script Web App URL pe POST karo.
    Script side pe doGET/doPost handle hona chahiye.
    """
    if not ws_url:
        return False, "Google Sheet URL configure nahi hai."
    payload = [
        {
            "title":  a["title"],
            "date":   a["date"],
            "source": a["source"],
            "type":   a["type"],
            "url":    a["url"],
            "desc":   a["desc"][:300],
        }
        for a in articles[:20]
    ]
    try:
        r = requests.post(ws_url, json=payload, timeout=15)
        if r.status_code == 200:
            return True, f"{len(payload)} articles sheet mein save ho gaye!"
        return False, f"Error {r.status_code}: {r.text[:100]}"
    except Exception as e:
        return False, f"Connection error: {str(e)[:80]}"


# ── HTML Export ──
def build_html_report(articles: list) -> str:
    now = datetime.now().strftime("%d %b %Y %H:%M")
    rows = ""
    color_map = {"neg": "#ff4b4b", "pos": "#39ff14", "aw": "#ffd700"}
    label_map = {"neg": "⚠️ FRAUD", "pos": "✅ ACTION", "aw": "📢 AWARENESS"}
    for a in articles:
        clr = color_map.get(a["type"], "#00e5ff")
        lbl = label_map.get(a["type"], "📰")
        rows += f"""
        <div style="border-left:4px solid {clr};padding:1rem 1.2rem;margin-bottom:1rem;
                    background:#0b1422;border-radius:0 10px 10px 0;">
          <div style="font-weight:700;font-size:1rem;color:#e0eaff;">{lbl} &nbsp; {html_lib.escape(a['title'])}</div>
          <div style="font-size:0.72rem;color:#7090b0;margin:0.3rem 0;font-family:monospace;">
            📅 {a['date']} &nbsp;|&nbsp; 📰 {html_lib.escape(a['source'])}
          </div>
          <div style="font-size:0.88rem;color:#c0d0e8;line-height:1.7;margin-top:0.4rem;">
            {html_lib.escape(a['desc'])}
          </div>
          {'<a href="' + html_lib.escape(a["url"]) + '" style="color:#00e5ff;font-size:0.78rem;">📖 पूरी खबर →</a>' if a.get('url','#') != '#' else ''}
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>UP Cyber Shield — Report {now}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;600&family=Share+Tech+Mono&display=swap');
  body {{ background:#050a14; color:#e0eaff; font-family:'Noto Sans Devanagari','Share Tech Mono',sans-serif; margin:0; padding:2rem; }}
  h1 {{ font-family:'Share Tech Mono',monospace; color:#00e5ff; letter-spacing:4px; font-size:1.8rem; }}
  .sub {{ color:#7090b0; font-size:0.85rem; margin-bottom:2rem; }}
  .stats {{ display:grid; grid-template-columns:repeat(4,1fr); gap:1rem; margin-bottom:2rem; }}
  .stat {{ background:#0b1422; border-radius:10px; padding:1rem; text-align:center; }}
  .stat .n {{ font-family:'Share Tech Mono',monospace; font-size:1.8rem; font-weight:700; }}
  footer {{ text-align:center; color:#3a5a7a; font-family:monospace; font-size:0.7rem; margin-top:3rem; border-top:1px solid rgba(0,229,255,0.1); padding-top:1rem; }}
</style>
</head>
<body>
<h1>🛡️ UP CYBER SHIELD</h1>
<div class="sub">उत्तर प्रदेश साइबर अपराध जागरूकता रिपोर्ट &nbsp;|&nbsp; {now} &nbsp;|&nbsp; Helpline: 1930</div>
<div class="stats">
  <div class="stat"><div class="n" style="color:#00e5ff">{len(articles)}</div><div style="color:#7090b0;font-size:0.72rem;">TOTAL NEWS</div></div>
  <div class="stat"><div class="n" style="color:#ff4b4b">{sum(1 for a in articles if a['type']=='neg')}</div><div style="color:#7090b0;font-size:0.72rem;">FRAUD CASES</div></div>
  <div class="stat"><div class="n" style="color:#39ff14">{sum(1 for a in articles if a['type']=='pos')}</div><div style="color:#7090b0;font-size:0.72rem;">POLICE ACTION</div></div>
  <div class="stat"><div class="n" style="color:#ffd700">{sum(1 for a in articles if a['type']=='aw')}</div><div style="color:#7090b0;font-size:0.72rem;">AWARENESS</div></div>
</div>
{rows}
<footer>UP CYBER SHIELD &nbsp;|&nbsp; Generated: {now} &nbsp;|&nbsp; cybercrime.gov.in &nbsp;|&nbsp; 1930</footer>
</body>
</html>"""


# ── Post Generator ──
PLATFORM_RULES = {
    "Twitter/X":  {"limit":"280 chars MAX. 2-3 lines.", "style":"Short punchy tweet + hashtags.", "emojis":"🚨⚠️🔐📵💰🛡️"},
    "Facebook":   {"limit":"300-500 chars, paragraph.", "style":"Friendly awareness post.", "emojis":"🔴🛡️⚠️✅📞💡🙏"},
    "Instagram":  {"limit":"150-250 chars + 10-15 hashtags.", "style":"Eye-catching caption.", "emojis":"🔴🔐💻🛡️⚡✨🚫📵"},
    "WhatsApp":   {"limit":"200-350 chars, conversational.", "style":"Forward-friendly warning.", "emojis":"🚨⛔🔐📞✅👆💬"},
}
TONE_GUIDE = {
    "Urgent Warning": "URGENT, alarming. ALL CAPS for key words.",
    "Informative":    "Educational, calm, step-by-step.",
    "Motivational":   "Empowering, positive energy.",
    "Helpful Tips":   "Friendly checklist, do's and don'ts.",
}

def groq_post(api_key: str, topic: str, platform: str, tone: str) -> str:
    p = PLATFORM_RULES.get(platform, PLATFORM_RULES["WhatsApp"])
    t = TONE_GUIDE.get(tone, TONE_GUIDE["Urgent Warning"])
    return groq_call(
        api_key,
        f'Topic: "{topic}"\n\nPlatform: {platform}\nRules: {p["limit"]} | {p["style"]} | Emojis: {p["emojis"]}\nTone: {t}\n\nStart directly with post content. No preamble.',
        system=(
            "Tum UP Police Cyber Cell ke social media expert ho. "
            "SIRF HINDI (Devanagari) mein likho. "
            "Allowed English: OTP, Cyber, Online, Helpline, FIR, Link, App. "
            "Hamesha include karo: helpline 1930, cybercrime.gov.in, relevant hashtags. "
            "Ready-to-paste format do."
        ),
        max_tokens=500,
    )


def classify(title: str, desc: str) -> str:
    text = (title + " " + desc).lower()
    pos_kw = ["busted","recovered","awareness","crackdown","campaign","helpline","safe","जागरूकता","वापस","ध्वस्त"]
    neg_kw = ["fraud","scam","victim","cheated","fake","phishing","extortion","loot","ठगी","धोखा","फर्जी"]
    p = sum(1 for k in pos_kw if k in text)
    n = sum(1 for k in neg_kw if k in text)
    if p > n: return "pos"
    if n > 0: return "neg"
    return "aw"


# ──────────────────────────────────────────────────────────
# 📊  DEMO DATA — Dynamic dates
# ──────────────────────────────────────────────────────────
def build_demo_articles() -> list:
    today = datetime.now()
    raw = [
        {"title":"Lucknow: OTP Fraud Gang Busted — 12 Arrested by UP Cyber Cell",
         "desc":"UP Police की Cyber Cell ने Lucknow में एक बड़े OTP fraud gang का पर्दाफाश किया। 12 सदस्य गिरफ्तार, 45 लाख रुपये नकद और 6 SIM card cloning devices बरामद। आरोपी बैंक अधिकारी बनकर OTP माँगते थे। 200+ शिकायतें इस गैंग से जुड़ी हैं।",
         "source":"Amar Ujala","days_ago":0,"url":"https://www.amarujala.com","type":"pos"},
        {"title":"Kanpur: Online Loan App Scam — 200+ Victims File Complaint",
         "desc":"Kanpur में fake loan apps से 200 से अधिक लोगों की ठगी। App install करते ही contacts और gallery access हो जाती थी। Processing fee के नाम पर 5,000-20,000 रुपये ऐंठे जाते थे। मुख्य आरोपी दिल्ली से गिरफ्तार।",
         "source":"Dainik Jagran","days_ago":1,"url":"https://www.jagran.com","type":"neg"},
        {"title":"Varanasi: Cyber Safety Workshop — 10,000 Students Trained",
         "desc":"Varanasi Police के 'Safe Digital Bharat' अभियान में 50 schools में Workshop। 10,000 students को phishing, social media safety और cyber bullying से बचाव सिखाया। अगले 3 महीनों में 100 और schools कवर होंगी।",
         "source":"Hindustan Times","days_ago":2,"url":"https://www.hindustantimes.com","type":"aw"},
        {"title":"Noida: Fake Job Portal Scam — IT Professionals Targeted",
         "desc":"Noida में fake portal 'TechHire India' ने IT professionals को निशाना बनाया। Selection letter भेजकर 15,000-50,000 रुपये registration fee माँगी। 85 शिकायतें, कुल नुकसान 28 लाख+। Police ने alert जारी किया।",
         "source":"Times of India UP","days_ago":3,"url":"https://timesofindia.indiatimes.com","type":"neg"},
        {"title":"Agra: Cyber Cell Recovers Rs 32 Lakh for Senior Citizen",
         "desc":"Agra के 68 वर्षीय retired teacher को digital arrest fraud का शिकार बनाया गया। परिवार ने 1930 पर complaint की। UP Cyber Cell ने 24 घंटे में सभी transactions freeze करा दीं और 32 लाख वापस दिलाए — 2026 की सबसे बड़ी recovery।",
         "source":"UP Police Official","days_ago":4,"url":"https://uppolice.gov.in","type":"pos"},
        {"title":"Gorakhpur: Phishing SMS — Fake KYC Link Targeting Bank Customers",
         "desc":"Gorakhpur में bank customers को fake KYC SMS आ रहे हैं — 'account 24 घंटे में बंद होगा।' Link पर जाने पर fake website और OTP enter करते ही account खाली। 45 शिकार, 18 लाख नुकसान। 1930 पर call करें।",
         "source":"Amar Ujala","days_ago":5,"url":"https://www.amarujala.com","type":"neg"},
        {"title":"Prayagraj: 'Ruko Socho Report Karo' Digital Arrest Awareness Drive",
         "desc":"Prayagraj Police ने 500+ rickshaw-auto stands पर posters लगाए। Cable TV पर awareness videos चल रही हैं। Senior citizens को घर-घर जाकर समझाया जा रहा है — CBI/ED कभी video call पर arrest नहीं करती।",
         "source":"Prayagraj Police","days_ago":6,"url":"https://uppolice.gov.in","type":"aw"},
        {"title":"Meerut: Crypto Fraud — Rs 1.2 Crore Scam on 32 Investors",
         "desc":"Meerut में fake platform 'CryptoGainIndia' ने 32 investors से 1.2 crore ठगे। पहले छोटा profit दिखाया, फिर बड़ा amount आते ही 'maintenance mode।' 3 accused arrest, 6 accounts में 45 लाख freeze।",
         "source":"Dainik Jagran","days_ago":7,"url":"https://www.jagran.com","type":"neg"},
    ]
    articles = []
    for item in raw:
        articles.append({
            "title":   item["title"],
            "desc":    item["desc"],
            "source":  item["source"],
            "date":    (today - timedelta(days=item["days_ago"])).strftime("%Y-%m-%d"),
            "url":     item["url"],
            "type":    item["type"],
            "is_demo": True,
        })
    articles.sort(key=lambda x: x["date"], reverse=True)
    return articles


DEMO = build_demo_articles()

TIPS = [
    ("🔐","OTP कभी Share न करें","Bank, Police, या कोई भी government officer कभी OTP नहीं माँगता। OTP माँगने वाला 100% fraud है।"),
    ("📵","Digital Arrest नहीं होता","CBI, ED, या Police कभी video call पर arrest नहीं करती। ऐसी call आए तो तुरंत काटें और 1930 पर call करें।"),
    ("📞","Helpline 1930","Cyber fraud हुआ? घबराएँ नहीं। तुरंत 1930 dial करें या cybercrime.gov.in पर complaint दर्ज करें।"),
    ("🌐","URL ध्यान से Check करें","Bank की असली website का URL https से शुरू होता है। एक अक्षर का फर्क भी fraud हो सकता है।"),
    ("💼","Fake Job Offers से बचें","Advance fee माँगने वाले job portals fraud हैं। कोई genuine company पहले पैसे नहीं माँगती।"),
    ("🔒","Social Media Privacy","Phone number, address, और Aadhaar social media पर कभी share न करें।"),
]

UP_DISTRICTS = [
    "सभी जिले","Lucknow","Kanpur","Agra","Varanasi","Prayagraj",
    "Meerut","Noida","Ghaziabad","Gorakhpur","Bareilly",
    "Aligarh","Moradabad","Saharanpur","Firozabad","Jhansi",
    "Mathura","Muzaffarnagar","Shahjahanpur",
]


# ──────────────────────────────────────────────────────────
# 🗂️  SIDEBAR
# ──────────────────────────────────────────────────────────
with st.sidebar:
    # Theme toggle
    col_logo, col_theme = st.columns([3,1])
    with col_logo:
        st.markdown("""
        <div style='padding:0.6rem 0;'>
          <div style='font-family:"Share Tech Mono",monospace;color:#00e5ff;font-size:1.2rem;letter-spacing:3px;'>🛡️ UP CYBER</div>
          <div style='font-family:"Share Tech Mono",monospace;color:#7090b0;font-size:0.6rem;letter-spacing:4px;'>SHIELD DASHBOARD</div>
        </div>""", unsafe_allow_html=True)
    with col_theme:
        st.markdown("<div style='padding-top:0.8rem;'>", unsafe_allow_html=True)
        if st.button("🌙" if st.session_state["theme"]=="dark" else "☀️", help="Theme toggle"):
            st.session_state["theme"] = "light" if st.session_state["theme"]=="dark" else "dark"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"<hr style='border-color:{T['border']};'>", unsafe_allow_html=True)

    # Secrets auto-load
    for sk, sess in [("NEWS_API_KEY","news_api_key"),("GROQ_API_KEY","groq_api_key"),("GSHEET_URL","gsheet_url")]:
        sv = get_secret(sk)
        if sv and not st.session_state[sess]:
            st.session_state[sess] = sv

    st.markdown("**🔑 API Keys**")
    if get_secret("NEWS_API_KEY"):
        st.success("✅ NewsAPI — Secrets se loaded")
    else:
        st.text_input("NewsAPI Key", key="news_api_key", type="password", placeholder="xxxxxxxx")
    if get_secret("GROQ_API_KEY"):
        st.success("✅ Groq API — Secrets se loaded")
    else:
        st.text_input("Groq API Key", key="groq_api_key", type="password", placeholder="gsk_xxxxx")

    st.markdown("---")

    # Google Sheets section
    st.markdown("**📊 Google Sheets (Optional)**")
    if get_secret("GSHEET_URL"):
        st.markdown('<span class="gsheet-ok">✅ Sheet URL — Secrets se loaded</span>', unsafe_allow_html=True)
    else:
        st.text_input("Apps Script Web App URL", key="gsheet_url",
                      placeholder="https://script.google.com/macros/s/...")
    st.caption("Sheet setup karne ka tarika: Tab 📊 mein dekho")

    st.markdown("---")
    st.markdown("**📍 Filters**")
    sel_dist = st.selectbox("जिला", UP_DISTRICTS)
    sel_type = st.selectbox("Category", ["सभी","🔴 Fraud","🟢 Police Action","🟡 Awareness"])

    # Date range filter
    date_range = st.slider(
        "📅 Kitne din purani khabar?",
        min_value=1, max_value=14, value=14,
        help="Sirf itne din purani news dikhao"
    )

    st.markdown("---")
    fetch_btn = st.button("🔄 Live News Fetch", use_container_width=True)

    # Auto-refresh status
    next_refresh = (datetime.now() + timedelta(hours=2)).strftime("%H:%M")
    st.markdown(
        f'<div style="font-family:monospace;font-size:0.65rem;color:#3a5a7a;text-align:center;margin-top:0.5rem;">'
        f'🔁 Auto-refresh: {next_refresh} baje</div>',
        unsafe_allow_html=True,
    )

    st.markdown("""
    <div style='text-align:center;margin-top:1rem;font-family:"Share Tech Mono",monospace;
                font-size:0.65rem;color:#3a5a7a;line-height:2;'>
    HELPLINE<br><span style='color:#ff4b4b;font-size:1.2rem;font-weight:700;'>1930</span><br>
    cybercrime.gov.in
    </div>""", unsafe_allow_html=True)

news_key = st.session_state["news_api_key"]
groq_key = st.session_state["groq_api_key"]
gsheet_url = st.session_state["gsheet_url"]


# ──────────────────────────────────────────────────────────
# 🏠  HEADER
# ──────────────────────────────────────────────────────────
st.markdown("""
<div class="cyber-header">
  <div class="cyber-title">🛡️ UP CYBER SHIELD</div>
  <div class="cyber-sub">उत्तर प्रदेश साइबर अपराध जागरूकता डैशबोर्ड</div>
  <div class="cyber-line"></div>
</div>""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────
# 📰  DATA LOAD + AUTO-REFRESH LOGIC
# ──────────────────────────────────────────────────────────
articles = list(DEMO)

# Auto-fetch if key available and cache is old (>2 hours)
def should_auto_fetch() -> bool:
    if not news_key:
        return False
    last = st.session_state.get("last_fetch")
    if last is None:
        return True
    return (datetime.now() - last).total_seconds() > 7200

def process_live(raw_list: list) -> list:
    result = []
    for a in raw_list:
        if not a.get("title"):
            continue
        t = strip_html(a.get("title",""))
        d_raw = strip_html(a.get("description","") or "")
        c_raw = strip_html(a.get("content","") or "")
        d = c_raw if len(c_raw) > len(d_raw) else (
            d_raw + " " + c_raw if (d_raw and c_raw and c_raw not in d_raw) else d_raw or c_raw
        )
        d = d or "Vistrit jaankari ke liye neeche link par click karein."
        result.append({
            "title":  t,
            "desc":   d,
            "source": a.get("source",{}).get("name",""),
            "date":   (a.get("publishedAt","") or "")[:10],
            "url":    a.get("url","#"),
            "type":   classify(t, d),
            "is_demo": False,
        })
    result.sort(key=lambda x: x["date"], reverse=True)
    return result

# Auto-fetch on load
if should_auto_fetch():
    with st.spinner("🔄 News auto-refresh ho rahi hai..."):
        q = "cyber crime Uttar Pradesh"
        live = fetch_news(news_key, q)
    if live:
        processed = process_live(live)
        st.session_state["articles_cache"] = processed
        st.session_state["last_fetch"] = datetime.now()
        st.session_state["using_demo"] = False
        st.toast(f"✅ {len(processed)} latest articles refresh ho gaye!", icon="🔄")
        articles = processed

elif st.session_state["articles_cache"]:
    articles = st.session_state["articles_cache"]
    st.session_state["using_demo"] = False

# Manual fetch button
if fetch_btn:
    if news_key:
        with st.spinner("Live news fetch ho rahi hai..."):
            sel_q = f"cyber crime {sel_dist if sel_dist != 'सभी जिले' else 'Uttar Pradesh'}"
            live = fetch_news(news_key, sel_q)
        if live:
            processed = process_live(live)
            st.session_state["articles_cache"] = processed
            st.session_state["last_fetch"] = datetime.now()
            st.session_state["using_demo"] = False
            articles = processed
            st.toast(f"✅ {len(processed)} live articles mile!", icon="📰")
        else:
            st.warning("Live data nahi mila — demo data dikhaaya ja raha hai.")
    else:
        st.warning("Sidebar mein NewsAPI key daalein pehle.")

# Date range filter
cutoff_date = (datetime.now() - timedelta(days=date_range)).strftime("%Y-%m-%d")
articles = [a for a in articles if a.get("date","") >= cutoff_date]

# District + Category filter
if sel_dist != "सभी जिले":
    articles = [a for a in articles if sel_dist.lower() in (a["title"]+" "+a["desc"]).lower()]
type_map = {"🔴 Fraud":"neg","🟢 Police Action":"pos","🟡 Awareness":"aw"}
if sel_type != "सभी":
    articles = [a for a in articles if a["type"] == type_map.get(sel_type,"")]

filtered = articles


# ──────────────────────────────────────────────────────────
# 📊  TICKER + METRICS
# ──────────────────────────────────────────────────────────
if filtered:
    titles_ticker = " &nbsp;●&nbsp; ".join(html_lib.escape(d["title"][:55])+"…" for d in filtered[:5])
    st.markdown(f'<div class="ticker"><b>⚡ LIVE</b> &nbsp; {titles_ticker}</div>', unsafe_allow_html=True)

n_neg = sum(1 for d in filtered if d["type"]=="neg")
n_pos = sum(1 for d in filtered if d["type"]=="pos")
n_aw  = sum(1 for d in filtered if d["type"]=="aw")
n_bkm = len(st.session_state["bookmarks"])
st.markdown(f"""
<div class="metric-row">
  <div class="mcard c1"><div class="num">{len(filtered)}</div><div class="lbl">📰 Total News</div></div>
  <div class="mcard c2"><div class="num">{n_neg}</div><div class="lbl">⚠️ Fraud Cases</div></div>
  <div class="mcard c3"><div class="num">{n_pos}</div><div class="lbl">✅ Police Action</div></div>
  <div class="mcard c4"><div class="num">{n_bkm}</div><div class="lbl">🔖 Bookmarked</div></div>
</div>""", unsafe_allow_html=True)

# Search bar — GLOBAL
search_q = st.text_input("🔍 News Search करें", placeholder="OTP fraud, digital arrest, Lucknow...", label_visibility="collapsed")
if search_q:
    sq = search_q.lower()
    filtered = [a for a in filtered if sq in a["title"].lower() or sq in a["desc"].lower()]
    st.caption(f'🔍 "{search_q}" — {len(filtered)} results')


# ──────────────────────────────────────────────────────────
# 📋  NEWS RENDERER — with Skeleton + Bookmark
# ──────────────────────────────────────────────────────────
TYPE_LABEL = {"neg":"⚠️ FRAUD","pos":"✅ ACTION","aw":"📢 AWARENESS"}
TYPE_CSS   = {"neg":"neg","pos":"pos","aw":"aw"}

def show_skeleton(n: int = 3):
    """Loading skeleton cards dikhao"""
    for _ in range(n):
        st.markdown("""
        <div class="skel-card">
          <div class="skeleton skel-title"></div>
          <div class="skeleton skel-meta"></div>
          <div class="skeleton skel-body"></div>
        </div>""", unsafe_allow_html=True)


def show_news_list(news_list: list, prefix: str, show_skeleton_first: bool = False):
    if not news_list:
        st.info("Is category mein koi khabar nahi mili. Filter badlein.")
        return

    # Demo banner
    news_api_present = bool(get_secret("NEWS_API_KEY") or st.session_state.get("news_api_key",""))
    is_showing_demo = any(a.get("is_demo") for a in news_list)
    if is_showing_demo and not news_api_present:
        today_str = datetime.now().strftime("%d %b %Y")
        st.markdown(
            f'<div class="demo-banner">⚠️ DEMO MODE — Sample data hai. '
            f'Real news ke liye NewsAPI key add karein. '
            f'Dates aaj ({today_str}) se relative hain.</div>',
            unsafe_allow_html=True,
        )

    for i, art in enumerate(news_list):
        t   = art["title"]
        d   = art["desc"]
        src = art["source"]
        dt  = art["date"]
        url = art["url"]
        tp  = art["type"]
        lbl = TYPE_LABEL.get(tp,"📰 NEWS")
        css = TYPE_CSS.get(tp,"aw")

        # Bookmark check
        is_bookmarked = t in st.session_state["bookmarks"]
        bkm_badge = '<span class="bookmark-badge">🔖 Saved</span>' if is_bookmarked else ""

        safe_t   = html_lib.escape(t)
        safe_d   = html_lib.escape(d)
        safe_src = html_lib.escape(src)
        link_html = ""
        if url and url != "#":
            link_html = f'<br><a href="{html_lib.escape(url)}" target="_blank" class="read-link">📖 पूरी खबर पढ़ें →</a>'

        st.markdown(
            f'<div class="news-item {css}">'
            f'<div class="ntitle">{lbl} &nbsp; {safe_t}{bkm_badge}</div>'
            f'<div class="nmeta">📅 {dt} &nbsp;|&nbsp; 📰 {safe_src}</div>'
            f'<div class="ndesc">{safe_d}{link_html}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns([2, 2, 1])
        btn_key = f"ai_{prefix}_{i}"
        res_key = f"res_{prefix}_{i}"
        bkm_key = f"bkm_{prefix}_{i}"

        with col1:
            if st.button("🤖 AI Summary", key=btn_key):
                if not groq_key:
                    st.warning("Groq API key daalein.")
                else:
                    with st.spinner("AI summary ban rahi hai..."):
                        result = groq_summarize(groq_key, t + "\n\n" + d)
                    st.session_state["ai_results"][res_key] = result
                    st.toast("✅ Summary ready!", icon="🤖")

        with col2:
            bkm_label = "🔖 Remove" if is_bookmarked else "🔖 Save"
            if st.button(bkm_label, key=bkm_key):
                if is_bookmarked:
                    st.session_state["bookmarks"].remove(t)
                    st.toast("Bookmark hataya gaya", icon="🗑️")
                else:
                    st.session_state["bookmarks"].append(t)
                    st.toast("✅ Bookmark ho gaya!", icon="🔖")
                st.rerun()

        if res_key in st.session_state["ai_results"]:
            st.markdown(
                f'<div class="ai-box">'
                f'<b style="color:#00e5ff;font-size:0.78rem;font-family:monospace;letter-spacing:1px;">🤖 AI SUMMARY — HINDI</b><br><br>'
                f'{html_lib.escape(st.session_state["ai_results"][res_key])}</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<hr>", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────
# 🗂️  TABS
# ──────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "📰 Latest",
    "🔴 Fraud",
    "🟢 Action",
    "📢 Awareness",
    "📈 AI Trends",
    "🤖 Post Gen",
    "💬 AI Chat",
    "🔖 Saved",
    "ℹ️ Tips",
])

# ── TAB 1: LATEST NEWS ──
with tab1:
    st.markdown(f"#### 📰 सभी ताज़ा खबरें — {len(filtered)} articles")
    if st.session_state.get("last_fetch"):
        st.caption(f"🕐 Last fetch: {st.session_state['last_fetch'].strftime('%d %b %Y %H:%M')} | Auto-refresh: हर 2 घंटे")
    show_news_list(filtered[:12], prefix="t1")

# ── TAB 2: FRAUD CASES ──
with tab2:
    neg_list = [a for a in filtered if a["type"]=="neg"]
    st.markdown(f"#### ⚠️ Fraud & Cyber Crime Cases — {len(neg_list)}")
    st.error("🚨 ACTIVE ALERTS — Fake CBI/ED video call (Digital Arrest) • Fake loan apps • Crypto investment fraud")
    show_news_list(neg_list, prefix="t2")

# ── TAB 3: POLICE ACTION ──
with tab3:
    pos_list = [a for a in filtered if a["type"]=="pos"]
    st.markdown(f"#### ✅ Police Actions & Success Stories — {len(pos_list)}")
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Recovered", "Rs 4.2 Cr", datetime.now().strftime('%B %Y'))
    c2.metric("👮 Arrests",   "156",       datetime.now().strftime('%B %Y'))
    c3.metric("📁 Cases Closed","892",     datetime.now().strftime('%B %Y'))
    st.markdown("---")
    show_news_list(pos_list, prefix="t3")

# ── TAB 4: AWARENESS ──
with tab4:
    aw_list = [a for a in filtered if a["type"]=="aw"]
    st.markdown(f"#### 📢 Awareness Campaigns — {len(aw_list)}")
    show_news_list(aw_list, prefix="t4")

# ── TAB 5: AI TREND ANALYZER ──
with tab5:
    st.markdown("#### 📈 AI Trend Analyzer")
    st.caption("सभी news को AI se analyze karke UP mein cyber crime ke trends nikalo")

    all_for_trend = st.session_state["articles_cache"] or DEMO
    col_t1, col_t2 = st.columns([3,1])
    with col_t2:
        if st.button("🧠 Trend Analyze karein", key="do_trend"):
            if not groq_key:
                st.error("Groq API key daalein.")
            else:
                with st.spinner("AI sab khabrein padh raha hai aur trends nikal raha hai..."):
                    trend_result = groq_trend_analyze(groq_key, all_for_trend)
                st.session_state["ai_results"]["trend"] = trend_result
                st.toast("✅ Trend analysis ready!", icon="📈")

    if "trend" in st.session_state["ai_results"]:
        st.markdown(
            f'<div class="trend-card">'
            f'<b style="color:#00e5ff;font-size:0.82rem;font-family:monospace;letter-spacing:2px;">🧠 AI CYBER TREND REPORT — UP</b><br><br>'
            f'{html_lib.escape(st.session_state["ai_results"]["trend"])}'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    # Basic charts using streamlit native
    st.markdown("#### 📊 Category Distribution")
    all_arts = st.session_state["articles_cache"] or DEMO
    neg_c = sum(1 for a in all_arts if a["type"]=="neg")
    pos_c = sum(1 for a in all_arts if a["type"]=="pos")
    aw_c  = sum(1 for a in all_arts if a["type"]=="aw")
    import pandas as pd
    chart_df = pd.DataFrame({
        "Category": ["⚠️ Fraud Cases", "✅ Police Action", "📢 Awareness"],
        "Count":    [neg_c, pos_c, aw_c],
    })
    st.bar_chart(chart_df.set_index("Category"), color="#00e5ff")

    # District frequency
    st.markdown("#### 📍 District Mentions")
    dist_list = ["Lucknow","Kanpur","Agra","Varanasi","Prayagraj","Meerut","Noida","Gorakhpur","Ghaziabad","Bareilly"]
    dist_counts = {}
    for dist in dist_list:
        cnt = sum(1 for a in all_arts if dist.lower() in (a["title"]+" "+a["desc"]).lower())
        if cnt > 0:
            dist_counts[dist] = cnt
    if dist_counts:
        df2 = pd.DataFrame({"District": list(dist_counts.keys()), "News Count": list(dist_counts.values())})
        st.bar_chart(df2.set_index("District"), color="#ff4b4b")

    # HTML Export button
    st.markdown("---")
    st.markdown("#### 📄 HTML Report Export")
    if st.button("⬇️ HTML Report Generate karein", key="gen_html"):
        html_content = build_html_report(filtered or DEMO)
        now_str = datetime.now().strftime("%Y%m%d_%H%M")
        st.download_button(
            label="📥 Download HTML Report",
            data=html_content.encode("utf-8"),
            file_name=f"UP_Cyber_Shield_Report_{now_str}.html",
            mime="text/html",
            key="dl_html",
        )
        st.toast("✅ HTML Report ready — Download karein!", icon="📄")

    # Google Sheets push
    st.markdown("---")
    st.markdown("#### 📊 Google Sheets Export")

    gsheet_configured = bool(gsheet_url)
    if gsheet_configured:
        st.markdown('<span class="gsheet-ok">✅ Google Sheet URL configured hai</span>', unsafe_allow_html=True)
        if st.button("📤 News Google Sheet mein Save karein", key="push_sheet"):
            with st.spinner("Google Sheets mein data bhej raha hai..."):
                ok, msg = push_to_gsheet(gsheet_url, filtered or DEMO)
            if ok:
                st.success(msg)
                st.toast("✅ Sheet updated!", icon="📊")
            else:
                st.error(msg)
    else:
        st.markdown('<span class="gsheet-off">⚠️ Google Sheet configure nahi hai</span>', unsafe_allow_html=True)
        with st.expander("📘 Google Sheets kaise setup karein? (Step-by-step)"):
            st.markdown("""
**Step 1 — Google Sheet banao**
- sheets.google.com pe new sheet banao
- Columns: Title | Date | Source | Type | URL | Description

**Step 2 — Apps Script banao**
- Sheet mein: Extensions → Apps Script
- Neeche diya code paste karo:

```javascript
function doPost(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var data  = JSON.parse(e.postData.contents);
  data.forEach(function(row) {
    sheet.appendRow([row.title, row.date, row.source, row.type, row.url, row.desc]);
  });
  return ContentService.createTextOutput("OK");
}
```

**Step 3 — Deploy karein**
- Deploy → New deployment → Web App
- Execute as: Me | Access: Anyone
- Deploy → URL copy karo

**Step 4 — URL yahan dalo**
- Sidebar mein "Apps Script Web App URL" field mein paste karo
- Ya `.streamlit/secrets.toml` mein: `GSHEET_URL = "https://..."`
            """)


# ── TAB 6: AI POST GENERATOR ──
with tab6:
    st.markdown("#### 🤖 AI Social Media Post Generator")
    st.caption("Platform ke hisaab se emoji-rich, ready-to-paste Hindi posts banayein.")

    col_a, col_b = st.columns([2,1])
    with col_a:
        topic = st.text_area("📝 Topic ya headline daalein",
            placeholder="Example: Lucknow mein OTP fraud gang 12 arrested...", height=90)
    with col_b:
        platform = st.selectbox("📱 Platform", ["Twitter/X","Facebook","Instagram","WhatsApp"])
        tone     = st.selectbox("🎯 Tone", ["Urgent Warning","Informative","Motivational","Helpful Tips"])

    plat_info = {
        "Twitter/X": "280 chars • Short & punchy",
        "Facebook":  "300-500 chars • Community feel",
        "Instagram": "Caption + hashtag block",
        "WhatsApp":  "200-350 chars • Forward-friendly",
    }
    st.info(f"📋 **{platform}** — {plat_info[platform]}")

    if st.button("⚡ Post Generate karein", key="gen_post_main"):
        if not topic.strip():
            st.warning("Topic daalein.")
        elif not groq_key:
            st.error("Groq API key daalein.")
        else:
            with st.spinner(f"AI {platform} post likh raha hai..."):
                result = groq_post(groq_key, topic, platform, tone)
            st.session_state["ai_results"]["gen_post"]     = result
            st.session_state["ai_results"]["gen_platform"] = platform
            st.toast("✅ Post ready!", icon="✨")

    if "gen_post" in st.session_state["ai_results"]:
        res      = st.session_state["ai_results"]["gen_post"]
        plat_out = st.session_state["ai_results"].get("gen_platform", platform)
        st.markdown(
            f'<div class="post-card">'
            f'<div class="platform-badge">✨ {html_lib.escape(plat_out.upper())} — READY TO PASTE</div>'
            f'<div class="post-text">{html_lib.escape(res)}</div>'
            f'<div class="char-count">{len(res)} characters</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.code(res, language=None)
        st.caption("⬆️ Copy karein aur directly paste karein!")

    st.markdown("---")
    st.markdown("#### 🔁 Quick Post — Latest Headlines se")
    for i, art in enumerate((filtered or DEMO)[:4]):
        c1, c2 = st.columns([5,1])
        with c1:
            st.caption(f"📰 {art['title'][:85]}…")
        with c2:
            if st.button("⚡", key=f"qpost_{i}", help="Iska post banao"):
                if not groq_key:
                    st.warning("Groq key daalein.")
                else:
                    with st.spinner("..."):
                        p = groq_post(groq_key, art["title"], "WhatsApp", "Urgent Warning")
                    st.session_state["ai_results"][f"qpost_{i}"] = p
                    st.toast("✅ Post ready!", icon="⚡")

        if f"qpost_{i}" in st.session_state["ai_results"]:
            qres = st.session_state["ai_results"][f"qpost_{i}"]
            st.markdown(
                f'<div class="post-card">'
                f'<div class="platform-badge">⚡ WHATSAPP — QUICK POST</div>'
                f'<div class="post-text">{html_lib.escape(qres)}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.code(qres, language=None)


# ── TAB 7: AI CHATBOT ──
with tab7:
    st.markdown("#### 💬 Cyber Shield AI Assistant")
    st.caption("Koi bhi cyber crime sawaal puchho — Hindi mein jawab milega")

    if not groq_key:
        st.warning("💡 Groq API key sidebar mein daalein chatbot use karne ke liye.")
    else:
        # Chat history display
        chat_container = st.container()
        with chat_container:
            if not st.session_state["chat_history"]:
                st.markdown(
                    '<div class="chat-ai">'
                    '<div class="chat-label">🤖 CYBER SHIELD AI</div>'
                    'Namaste! Main Cyber Shield AI Assistant hoon. 🛡️<br>'
                    'Aap mujhse cyber crime ke baare mein kuch bhi pooch sakte hain:<br><br>'
                    '• OTP fraud se kaise bachein?<br>'
                    '• Digital arrest kya hota hai?<br>'
                    '• Online ठगी हो गई, अब क्या करूँ?<br>'
                    '• Fake job offer kaise pehchanen?'
                    '</div>',
                    unsafe_allow_html=True,
                )
            for msg in st.session_state["chat_history"]:
                if msg["role"] == "user":
                    st.markdown(
                        f'<div class="chat-user"><div class="chat-label">👤 AAP</div>{html_lib.escape(msg["content"])}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div class="chat-ai"><div class="chat-label">🤖 CYBER SHIELD AI</div>{html_lib.escape(msg["content"])}</div>',
                        unsafe_allow_html=True,
                    )

        # Input
        user_q = st.text_input("💬 Sawaal likhein...", key="chat_input",
                               placeholder="जैसे: OTP fraud se kaise bachein?")

        col_send, col_clear = st.columns([3,1])
        with col_send:
            if st.button("📤 Send", key="chat_send") and user_q.strip():
                st.session_state["chat_history"].append({"role":"user","content":user_q})
                with st.spinner("AI soch raha hai..."):
                    reply = groq_chat(groq_key, user_q, st.session_state["chat_history"])
                st.session_state["chat_history"].append({"role":"assistant","content":reply})
                st.rerun()
        with col_clear:
            if st.button("🗑️ Clear", key="chat_clear"):
                st.session_state["chat_history"] = []
                st.rerun()

        # Quick questions
        st.markdown("**💡 Quick Sawaal:**")
        quick_qs = ["Digital arrest kya hai?","1930 helpline kab call karein?","OTP fraud se kaise bachein?","Fake job offer kaise pehchanen?"]
        qcols = st.columns(2)
        for idx, qq in enumerate(quick_qs):
            with qcols[idx % 2]:
                if st.button(qq, key=f"qq_{idx}"):
                    st.session_state["chat_history"].append({"role":"user","content":qq})
                    with st.spinner("..."):
                        reply = groq_chat(groq_key, qq, st.session_state["chat_history"])
                    st.session_state["chat_history"].append({"role":"assistant","content":reply})
                    st.rerun()


# ── TAB 8: BOOKMARKS ──
with tab8:
    st.markdown("#### 🔖 Saved / Bookmarked News")
    bkm_titles = st.session_state["bookmarks"]
    if not bkm_titles:
        st.info("Abhi koi news save nahi ki. News cards mein 🔖 Save button dabao.")
    else:
        all_arts_pool = st.session_state["articles_cache"] or DEMO
        saved_arts = [a for a in all_arts_pool if a["title"] in bkm_titles]

        if not saved_arts:
            st.warning("Saved news is session mein nahi mili. Naya fetch karne par wapas aayengi.")
        else:
            # HTML Export of bookmarks
            if st.button("📄 Saved News ka HTML Export", key="bkm_html"):
                html_bkm = build_html_report(saved_arts)
                now_str  = datetime.now().strftime("%Y%m%d_%H%M")
                st.download_button(
                    "📥 Download",
                    data=html_bkm.encode("utf-8"),
                    file_name=f"UP_Cyber_Saved_{now_str}.html",
                    mime="text/html",
                    key="dl_bkm_html",
                )
            show_news_list(saved_arts, prefix="bkm")

        if st.button("🗑️ Sab Bookmarks Clear karein", key="clear_bkm"):
            st.session_state["bookmarks"] = []
            st.rerun()


# ── TAB 9: TIPS ──
with tab9:
    st.markdown("#### 🛡️ Cyber Safety Tips — उत्तर प्रदेश")
    st.error("🆘 Cyber Fraud hua? **1930** par call karein | **cybercrime.gov.in** par report karein")
    st.markdown("---")
    for icon, title_tip, desc_tip in TIPS:
        st.markdown(
            f'<div class="tip-card">'
            f'<div style="font-size:1.8rem;">{icon}</div>'
            f'<div style="color:{T["accent"]};font-weight:700;font-size:1rem;margin:0.3rem 0;">{html_lib.escape(title_tip)}</div>'
            f'<div style="color:{T["tip_text"]};font-family:\'Noto Sans Devanagari\',sans-serif;'
            f'font-size:0.88rem;line-height:1.7;">{html_lib.escape(desc_tip)}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ──────────────────────────────────────────────────────────
# 🔻 FOOTER
# ──────────────────────────────────────────────────────────
last_upd = st.session_state["last_fetch"].strftime("%d %b %Y %H:%M") if st.session_state["last_fetch"] else datetime.now().strftime("%d %b %Y %H:%M")
st.markdown(
    f'<div style="text-align:center;padding:1.5rem 0 0.5rem;margin-top:2rem;'
    f'border-top:1px solid {T["hr"]};'
    f'font-family:\'Share Tech Mono\',monospace;color:#3a5a7a;font-size:0.65rem;letter-spacing:2px;">'
    f'UP CYBER SHIELD v2.0 &nbsp;|&nbsp; LAST UPDATE: {last_upd}'
    f' &nbsp;|&nbsp; AUTO-REFRESH: हर 2 घंटे &nbsp;|&nbsp; HELPLINE: 1930</div>',
    unsafe_allow_html=True,
)
