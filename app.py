import streamlit as st
import requests
import re
import html as html_lib
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
# 🔑  SECRETS / SESSION
# ─────────────────────────────────────────────
def get_secret(key: str) -> str:
    try:
        val = st.secrets.get(key, "")
        if val:
            return val
    except Exception:
        pass
    return st.session_state.get(key, "")


def strip_html(text: str) -> str:
    """Remove ALL html tags and decode entities — returns plain text."""
    if not text:
        return ""
    text = html_lib.unescape(text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&[a-zA-Z#0-9]+;', ' ', text)
    text = re.sub(r'\[\+\d+\s*chars?\]', '', text)
    return ' '.join(text.split()).strip()


# ─────────────────────────────────────────────
# ⚙️  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="UP Cyber Shield",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# 🎨  MINIMAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700&family=Noto+Sans+Devanagari:wght@400;600&family=Share+Tech+Mono&display=swap');

html, body, [class*="css"] {
    font-family: 'Rajdhani', 'Noto Sans Devanagari', sans-serif;
    background-color: #050a14 !important;
    color: #e0eaff !important;
}
.stApp { background: #050a14 !important; }

.cyber-header { text-align:center; padding:1.5rem 0 0.5rem; }
.cyber-title {
    font-family:'Share Tech Mono',monospace;
    font-size:2.4rem; font-weight:700; letter-spacing:6px;
    background:linear-gradient(135deg,#00e5ff,#ffffff,#00e5ff);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
.cyber-sub { color:#00e5ff; font-size:0.95rem; letter-spacing:2px; opacity:0.8; }
.cyber-line {
    height:2px;
    background:linear-gradient(90deg,transparent,#00e5ff,#ff4b4b,#00e5ff,transparent);
    max-width:500px; margin:1rem auto; border-radius:2px;
}

.metric-row { display:grid; grid-template-columns:repeat(4,1fr); gap:0.8rem; margin:1rem 0; }
.mcard { background:#0b1422; border:1px solid rgba(0,229,255,0.18); border-radius:10px; padding:1rem; text-align:center; }
.mcard .num { font-family:'Share Tech Mono',monospace; font-size:2rem; font-weight:700; }
.mcard .lbl { font-size:0.72rem; color:#7090b0; letter-spacing:1px; text-transform:uppercase; margin-top:0.2rem; }
.mcard.c1 .num{color:#00e5ff;} .mcard.c1{border-top:3px solid #00e5ff;}
.mcard.c2 .num{color:#ff4b4b;} .mcard.c2{border-top:3px solid #ff4b4b;}
.mcard.c3 .num{color:#39ff14;} .mcard.c3{border-top:3px solid #39ff14;}
.mcard.c4 .num{color:#ffd700;} .mcard.c4{border-top:3px solid #ffd700;}

.ticker {
    background:#0b1422; border:1px solid rgba(0,229,255,0.18);
    border-radius:8px; padding:0.5rem 1rem; margin-bottom:1rem;
    font-size:0.82rem; color:#7090b0;
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}
.ticker b { color:#ff4b4b; font-family:'Share Tech Mono',monospace; font-size:0.7rem; letter-spacing:2px; }

.news-item {
    border-left:4px solid #00e5ff;
    padding:0.8rem 1rem; margin-bottom:0.4rem;
    background:#0b1422; border-radius:0 8px 8px 0;
}
.news-item.neg { border-left-color:#ff4b4b; }
.news-item.pos { border-left-color:#39ff14; }
.news-item.aw  { border-left-color:#ffd700; }
.news-item .ntitle { font-weight:700; font-size:1rem; color:#e0eaff; line-height:1.4; }
.news-item .nmeta  { font-size:0.72rem; color:#7090b0; margin:0.25rem 0; font-family:'Share Tech Mono',monospace; }
.news-item .ndesc  { font-family:'Noto Sans Devanagari',sans-serif; font-size:0.88rem; color:#a0b8d0; line-height:1.7; }

.ai-box {
    background:linear-gradient(135deg,rgba(0,229,255,0.07),rgba(255,75,75,0.05));
    border:1px solid rgba(0,229,255,0.22); border-radius:10px;
    padding:1rem 1.2rem; margin:0.5rem 0;
    font-family:'Noto Sans Devanagari',sans-serif;
    font-size:0.9rem; line-height:1.8; color:#e0eaff;
    white-space:pre-wrap;
}

.tip-card {
    background:#0b1422; border:1px solid rgba(0,229,255,0.15);
    border-radius:10px; padding:1rem; margin-bottom:0.8rem;
}

.stTabs [data-baseweb="tab-list"] {
    background:#0b1422 !important; border-radius:10px !important;
    padding:3px !important; border:1px solid rgba(0,229,255,0.18) !important;
}
.stTabs [data-baseweb="tab"] {
    background:transparent !important; color:#7090b0 !important;
    border-radius:7px !important; font-family:'Rajdhani',sans-serif !important;
    font-weight:600 !important; padding:6px 14px !important;
}
.stTabs [aria-selected="true"] {
    background:rgba(0,229,255,0.15) !important;
    color:#00e5ff !important; border:1px solid rgba(0,229,255,0.3) !important;
}

section[data-testid="stSidebar"] {
    background:rgba(5,10,20,0.97) !important;
    border-right:1px solid rgba(0,229,255,0.15) !important;
}

.stButton > button {
    background:linear-gradient(135deg,rgba(0,229,255,0.15),rgba(0,229,255,0.05)) !important;
    border:1px solid rgba(0,229,255,0.4) !important;
    color:#00e5ff !important; border-radius:8px !important;
    font-family:'Share Tech Mono',monospace !important;
}

hr { border-color:rgba(0,229,255,0.1) !important; }
#MainMenu, footer, header { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 🔧  API FUNCTIONS
# ─────────────────────────────────────────────
def fetch_news(api_key: str, query: str = "cyber crime Uttar Pradesh") -> list:
    if not api_key:
        return []
    url = (
        "https://newsapi.org/v2/everything"
        f"?q={requests.utils.quote(query)}"
        "&language=en&sortBy=publishedAt&pageSize=15"
        f"&from={(datetime.now()-timedelta(days=14)).strftime('%Y-%m-%d')}"
        f"&apiKey={api_key}"
    )
    try:
        r = requests.get(url, timeout=10)
        return r.json().get("articles", [])
    except Exception:
        return []


def groq_call(api_key: str, prompt: str, max_tokens: int = 350) -> str:
    if not api_key:
        return "Groq API key sidebar mein enter karein."
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    models = ["llama-3.1-8b-instant", "llama3-8b-8192", "mixtral-8x7b-32768"]
    for model in models:
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.4,
                },
                timeout=25,
            )
            data = r.json()
            if "choices" in data:
                return data["choices"][0]["message"]["content"].strip()
        except Exception:
            continue
    return "Groq API se response nahi mila. API key check karein."


def groq_summarize(api_key: str, text: str) -> str:
    prompt = (
        "Tum UP Police ke liye ek cyber crime awareness assistant ho.\n"
        "Neeche di gayi khabar ko SIRF HINDI mein 3 bullet points mein summarize karo.\n"
        "Format bilkul aisa ho:\n• pehli baat\n• doosri baat\n• teesri baat\n"
        "Koi English preamble nahi. Sirf Hindi mein likho.\n\n"
        f"Khabar:\n{text[:1800]}"
    )
    return groq_call(api_key, prompt, max_tokens=300)


def groq_post(api_key: str, topic: str, platform: str, tone: str) -> str:
    prompt = (
        f"UP Police Cyber Cell ke liye {platform} par ek {tone} awareness post likho.\n"
        f"Vishay: {topic}\n"
        "Hinglish mein likho (Hindi + thoda English mix).\n"
        "Shaamil karo: 2-3 safety tips, call-to-action, "
        "hashtags: #CyberSafety #UPPolice #1930Helpline\n"
        f"{'Twitter ke liye 280 characters se kam rakho.' if 'Twitter' in platform else ''}"
    )
    return groq_call(api_key, prompt, max_tokens=250)


def classify(title: str, desc: str) -> str:
    text = (title + " " + desc).lower()
    pos_kw = ["busted", "recovered", "awareness", "crackdown", "campaign",
              "helpline", "safe", "जागरूकता", "वापस", "ध्वस्त"]
    neg_kw = ["fraud", "scam", "victim", "cheated", "fake", "phishing",
              "extortion", "loot", "ठगी", "धोखा", "फर्जी"]
    p = sum(1 for k in pos_kw if k in text)
    n = sum(1 for k in neg_kw if k in text)
    if p > n:
        return "pos"
    if n > 0:
        return "neg"
    return "aw"


# ─────────────────────────────────────────────
# 📊  DEMO DATA  (pure plain text — no HTML)
# ─────────────────────────────────────────────
DEMO = [
    {"title": "Lucknow: OTP Fraud Gang Busted — 12 Arrested by UP Cyber Cell",
     "desc": "UP Police की Cyber Cell ने Lucknow में एक बड़े OTP fraud gang को गिरफ्तार किया। 12 आरोपियों से 45 लाख रुपये की रकम बरामद की गई। पीड़ितों को refund की प्रक्रिया शुरू की गई है।",
     "source": "Amar Ujala", "date": "2026-04-17", "url": "#", "type": "pos"},
    {"title": "Kanpur: Online Loan App Scam — 200+ Victims File Complaint",
     "desc": "Kanpur में fake loan apps के जरिए 200 से अधिक लोगों से ठगी हुई। आरोपियों ने Aadhaar डेटा चुराकर fake CIBIL score दिखाया और मोटी रकम ऐंठ ली। Police जांच जारी है।",
     "source": "Dainik Jagran", "date": "2026-04-16", "url": "#", "type": "neg"},
    {"title": "Varanasi: Cyber Safety Workshop in 50 Schools — 10,000 Students Trained",
     "desc": "Varanasi Police ने 50 schools में Cyber Safety Workshop आयोजित की। 10,000 से अधिक students को digital fraud, phishing और social media safety के बारे में जागरूक किया गया।",
     "source": "Hindustan Times", "date": "2026-04-15", "url": "#", "type": "aw"},
    {"title": "Noida: Fake Job Portal Scam — IT Professionals Targeted",
     "desc": "Noida में एक fake job portal ने IT professionals से 15,000 से 50,000 रुपये registration fee ली। 85 शिकायतें दर्ज हुईं। Cybercrime portal पर FIR filed की गई।",
     "source": "Times of India UP", "date": "2026-04-14", "url": "#", "type": "neg"},
    {"title": "Agra: Cyber Cell Recovers Rs 32 Lakh for Senior Citizen Fraud Victim",
     "desc": "Agra के 68 वर्षीय senior citizen से 32 लाख रुपये की digital arrest fraud हुई थी। UP Cyber Cell ने तत्परता से action लेकर पूरी रकम वापस दिलाई। यह UP Cyber Cell की बड़ी उपलब्धि है।",
     "source": "UP Police Official", "date": "2026-04-13", "url": "#", "type": "pos"},
    {"title": "Gorakhpur: Phishing SMS Campaign Targets Bank Customers",
     "desc": "Gorakhpur में bank customers को fake KYC update SMS भेजे जा रहे हैं। UP Cyber Cell ने alert जारी किया है। किसी भी link पर click न करें और Helpline 1930 पर call करें।",
     "source": "Amar Ujala", "date": "2026-04-12", "url": "#", "type": "neg"},
    {"title": "Prayagraj: Digital Arrest Campaign — Ruko Socho Report Karo",
     "desc": "Prayagraj Police ने Ruko, Socho, Report Karo नाम से digital arrest awareness campaign शुरू किया। Rickshaw, auto, और bus stands पर जागरूकता posters लगाए गए हैं।",
     "source": "Prayagraj Police", "date": "2026-04-11", "url": "#", "type": "aw"},
    {"title": "Meerut: Cryptocurrency Fraud — Rs 1.2 Crore Scam Exposed",
     "desc": "Meerut में एक fake crypto trading platform ने investors से 1.2 crore रुपये ठगे। 3 accused arrested किए गए और 6 bank accounts में funds freeze किए गए।",
     "source": "Dainik Jagran", "date": "2026-04-10", "url": "#", "type": "neg"},
]

TIPS = [
    ("🔐", "OTP कभी Share न करें",
     "Bank, Police, या कोई भी government officer कभी OTP नहीं माँगता। OTP माँगने वाला 100% fraud है।"),
    ("📵", "Digital Arrest नहीं होता",
     "कोई भी CBI, ED, या Police agency video call पर arrest नहीं करती। ऐसी call आए तो तुरंत काटें और 1930 पर call करें।"),
    ("📞", "Helpline 1930",
     "Cyber fraud हुआ? घबराएँ नहीं। तुरंत 1930 dial करें या cybercrime.gov.in पर complaint दर्ज करें।"),
    ("🌐", "URL ध्यान से Check करें",
     "Bank की असली website का URL हमेशा https से शुरू होता है। Spelling ध्यान से देखें — एक अक्षर का फर्क fraud हो सकता है।"),
    ("💼", "Fake Job Offers से बचें",
     "Advance fee माँगने वाले job portals fraud हैं। कोई genuine company पहले पैसे नहीं माँगती।"),
    ("🔒", "Social Media Privacy",
     "Phone number, address, और Aadhaar number social media पर कभी share न करें।"),
]

UP_DISTRICTS = [
    "सभी जिले", "Lucknow", "Kanpur", "Agra", "Varanasi", "Prayagraj",
    "Meerut", "Noida", "Ghaziabad", "Gorakhpur", "Bareilly",
    "Aligarh", "Moradabad", "Saharanpur", "Firozabad",
    "Jhansi", "Mathura", "Muzaffarnagar", "Shahjahanpur",
]

# ─────────────────────────────────────────────
# 🔑  SESSION STATE
# ─────────────────────────────────────────────
for k in ["news_api_key", "groq_api_key"]:
    if k not in st.session_state:
        st.session_state[k] = ""
if "ai_results" not in st.session_state:
    st.session_state["ai_results"] = {}

# ─────────────────────────────────────────────
# 🗂️  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:0.8rem 0;'>
      <div style='font-family:"Share Tech Mono",monospace;color:#00e5ff;font-size:1.3rem;letter-spacing:3px;'>🛡️ UP CYBER</div>
      <div style='font-family:"Share Tech Mono",monospace;color:#7090b0;font-size:0.65rem;letter-spacing:4px;'>SHIELD DASHBOARD</div>
    </div>
    <hr style='border-color:rgba(0,229,255,0.15);'>
    """, unsafe_allow_html=True)

    for secret_key, session_key in [("NEWS_API_KEY", "news_api_key"), ("GROQ_API_KEY", "groq_api_key")]:
        sv = get_secret(secret_key)
        if sv and not st.session_state[session_key]:
            st.session_state[session_key] = sv

    st.markdown("**🔑 API Keys**")
    if get_secret("NEWS_API_KEY"):
        st.success("✅ NewsAPI — Secrets se loaded")
    else:
        st.text_input("NewsAPI Key", key="news_api_key", type="password", placeholder="xxxxxxxx")

    if get_secret("GROQ_API_KEY"):
        st.success("✅ Groq API — Secrets se loaded")
    else:
        st.text_input("Groq API Key", key="groq_api_key", type="password", placeholder="gsk_xxxxx")

    news_key = st.session_state["news_api_key"]
    groq_key = st.session_state["groq_api_key"]

    st.markdown("---")
    st.markdown("**📍 Filter**")
    sel_dist = st.selectbox("जिला", UP_DISTRICTS)
    sel_type = st.selectbox("Category", ["सभी", "🔴 Fraud", "🟢 Police Action", "🟡 Awareness"])
    st.markdown("---")
    fetch_btn = st.button("🔄 Live News Fetch", use_container_width=True)

    st.markdown("""
    <div style='text-align:center;margin-top:1rem;font-family:"Share Tech Mono",monospace;
                font-size:0.65rem;color:#3a5a7a;line-height:2;'>
    HELPLINE<br><span style='color:#ff4b4b;font-size:1.2rem;font-weight:700;'>1930</span><br>
    cybercrime.gov.in
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 🏠  HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="cyber-header">
  <div class="cyber-title">🛡️ UP CYBER SHIELD</div>
  <div class="cyber-sub">उत्तर प्रदेश साइबर अपराध जागरूकता डैशबोर्ड</div>
  <div class="cyber-line"></div>
</div>
""", unsafe_allow_html=True)

titles_ticker = " &nbsp;●&nbsp; ".join(html_lib.escape(d["title"][:55]) + "…" for d in DEMO[:5])
st.markdown(f'<div class="ticker"><b>⚡ LIVE</b> &nbsp; {titles_ticker}</div>', unsafe_allow_html=True)

n_neg = sum(1 for d in DEMO if d["type"] == "neg")
n_pos = sum(1 for d in DEMO if d["type"] == "pos")
n_aw  = sum(1 for d in DEMO if d["type"] == "aw")
st.markdown(f"""
<div class="metric-row">
  <div class="mcard c1"><div class="num">{len(DEMO)}</div><div class="lbl">📰 Total News</div></div>
  <div class="mcard c2"><div class="num">{n_neg}</div><div class="lbl">⚠️ Fraud Cases</div></div>
  <div class="mcard c3"><div class="num">{n_pos}</div><div class="lbl">✅ Police Action</div></div>
  <div class="mcard c4"><div class="num">{n_aw}</div><div class="lbl">📢 Campaigns</div></div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 📰  DATA LOAD + FILTER
# ─────────────────────────────────────────────
articles = list(DEMO)

if fetch_btn and news_key:
    with st.spinner("Live news fetch ho rahi hai..."):
        q = f"cyber crime {sel_dist if sel_dist != 'सभी जिले' else 'Uttar Pradesh'}"
        live = fetch_news(news_key, q)
    if live:
        articles = []
        for a in live:
            if not a.get("title"):
                continue
            t = strip_html(a.get("title", ""))
            d = strip_html(a.get("description", "") or a.get("content", ""))
            articles.append({
                "title": t,
                "desc": d or "Vistrit jaankari ke liye source par jaayein.",
                "source": a.get("source", {}).get("name", ""),
                "date": (a.get("publishedAt", "") or "")[:10],
                "url": a.get("url", "#"),
                "type": classify(t, d),
            })
        st.success(f"✅ {len(articles)} live articles mile!")
    else:
        st.warning("Live data nahi mila — demo data dikhaaya ja raha hai.")

filtered = articles
if sel_dist != "सभी जिले":
    filtered = [a for a in filtered
                if sel_dist.lower() in (a["title"] + " " + a["desc"]).lower()]
type_map = {"🔴 Fraud": "neg", "🟢 Police Action": "pos", "🟡 Awareness": "aw"}
if sel_type != "सभी":
    filtered = [a for a in filtered if a["type"] == type_map.get(sel_type, "")]

# ─────────────────────────────────────────────
# 📋  NEWS RENDERER — flat list, pure st.markdown with escaped text
# ─────────────────────────────────────────────
TYPE_LABEL = {"neg": "⚠️ FRAUD", "pos": "✅ ACTION", "aw": "📢 AWARENESS"}
TYPE_CSS   = {"neg": "neg", "pos": "pos", "aw": "aw"}


def show_news_list(news_list: list, prefix: str):
    if not news_list:
        st.info("Is category mein koi khabar nahi mili. Filter badlein.")
        return

    for i, art in enumerate(news_list):
        t   = art["title"]
        d   = art["desc"]
        src = art["source"]
        dt  = art["date"]
        url = art["url"]
        tp  = art["type"]
        lbl = TYPE_LABEL.get(tp, "📰 NEWS")
        css = TYPE_CSS.get(tp, "aw")

        # ✅ Escape everything before putting in HTML
        safe_title = html_lib.escape(t)
        safe_desc  = html_lib.escape(d)
        safe_src   = html_lib.escape(src)
        link_html  = (
            f' &nbsp;<a href="{html_lib.escape(url)}" target="_blank" '
            f'style="color:#00e5ff;font-size:0.72rem;text-decoration:none;">🔗 पढ़ें</a>'
            if url and url != "#" else ""
        )

        st.markdown(
            f'<div class="news-item {css}">'
            f'<div class="ntitle">{lbl} &nbsp; {safe_title}</div>'
            f'<div class="nmeta">📅 {dt} &nbsp;|&nbsp; 📰 {safe_src}{link_html}</div>'
            f'<div class="ndesc">{safe_desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # AI Summary — unique key per tab+index
        btn_key = f"ai_{prefix}_{i}"
        res_key = f"res_{prefix}_{i}"

        if st.button("🤖 AI Hindi Summary", key=btn_key):
            if not groq_key:
                st.warning("Sidebar mein Groq API key daalein.")
            else:
                with st.spinner("AI summary ban rahi hai..."):
                    result = groq_summarize(groq_key, t + "\n\n" + d)
                st.session_state["ai_results"][res_key] = result

        if res_key in st.session_state["ai_results"]:
            summary_text = html_lib.escape(st.session_state["ai_results"][res_key])
            st.markdown(
                f'<div class="ai-box">'
                f'<b style="color:#00e5ff;font-size:0.78rem;font-family:monospace;'
                f'letter-spacing:1px;">🤖 AI SUMMARY — HINDI</b><br><br>'
                f'{summary_text}</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<hr>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 🗂️  TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📰 Latest News",
    "🔴 Fraud Cases",
    "🟢 Police Action",
    "📢 Awareness",
    "🤖 AI Post Generator",
    "ℹ️ Cyber Tips",
])

with tab1:
    st.markdown(f"#### 📰 सभी ताज़ा खबरें — {len(filtered)} articles")
    show_news_list(filtered[:12], prefix="t1")

with tab2:
    neg_list = [a for a in filtered if a["type"] == "neg"]
    st.markdown(f"#### ⚠️ Fraud & Cyber Crime Cases — {len(neg_list)}")
    st.error(
        "🚨 ACTIVE ALERTS — "
        "Fake CBI/ED video call (Digital Arrest) • "
        "Fake loan apps blackmail • "
        "Telegram fake crypto investment"
    )
    show_news_list(neg_list, prefix="t2")

with tab3:
    pos_list = [a for a in filtered if a["type"] == "pos"]
    st.markdown(f"#### ✅ Police Actions & Success Stories — {len(pos_list)}")
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Recovered", "Rs 4.2 Cr", "April 2026")
    col2.metric("👮 Arrests",   "156",       "April 2026")
    col3.metric("📁 Cases Closed", "892",    "April 2026")
    st.markdown("---")
    show_news_list(pos_list, prefix="t3")

with tab4:
    aw_list = [a for a in filtered if a["type"] == "aw"]
    st.markdown(f"#### 📢 Awareness Campaigns — {len(aw_list)}")
    show_news_list(aw_list, prefix="t4")

with tab5:
    st.markdown("#### 🤖 AI Social Media Post Generator")
    st.caption("Groq API (Free) se Hinglish awareness posts banaayein.")

    col_a, col_b = st.columns([2, 1])
    with col_a:
        topic = st.text_area(
            "📝 Topic ya headline daalein",
            placeholder="Example: Lucknow mein OTP fraud gang 12 arrested...",
            height=90,
        )
    with col_b:
        platform = st.selectbox("Platform", ["Twitter/X", "Facebook", "Instagram", "WhatsApp"])
        tone     = st.selectbox("Tone", ["Urgent Warning", "Informative", "Motivational", "Helpful Tips"])

    if st.button("⚡ Post Generate karein", key="gen_post_main"):
        if not topic.strip():
            st.warning("Topic daalein.")
        elif not groq_key:
            st.error("Sidebar mein Groq API key daalein.")
        else:
            with st.spinner("AI post likh raha hai..."):
                result = groq_post(groq_key, topic, platform, tone)
            st.session_state["ai_results"]["gen_post"] = result

    if "gen_post" in st.session_state["ai_results"]:
        res = st.session_state["ai_results"]["gen_post"]
        st.markdown(
            f'<div class="ai-box">'
            f'<b style="color:#00e5ff;font-size:0.78rem;font-family:monospace;">✨ GENERATED POST — {html_lib.escape(platform.upper())}</b>'
            f'<br><br>{html_lib.escape(res)}</div>',
            unsafe_allow_html=True,
        )
        st.code(res, language=None)

    st.markdown("---")
    st.markdown("#### 🔁 Quick Post from Latest News")
    for i, art in enumerate(filtered[:4]):
        c1, c2 = st.columns([5, 1])
        with c1:
            st.caption(f"📰 {art['title'][:85]}…")
        with c2:
            if st.button("⚡", key=f"qpost_{i}"):
                if not groq_key:
                    st.warning("Groq key daalein.")
                else:
                    with st.spinner("..."):
                        p = groq_post(groq_key, art["title"], "Twitter/X", "Urgent Warning")
                    st.session_state["ai_results"][f"qpost_{i}"] = p
        if f"qpost_{i}" in st.session_state["ai_results"]:
            st.info(st.session_state["ai_results"][f"qpost_{i}"])

with tab6:
    st.markdown("#### 🛡️ Cyber Safety Tips — उत्तर प्रदेश")
    st.error("🆘 Cyber Fraud hua? **1930** par call karein | **cybercrime.gov.in** par report karein")
    st.markdown("---")
    for icon, title, desc in TIPS:
        st.markdown(
            f'<div class="tip-card">'
            f'<div style="font-size:1.8rem;">{icon}</div>'
            f'<div style="color:#00e5ff;font-weight:700;font-size:1rem;margin:0.3rem 0;">'
            f'{html_lib.escape(title)}</div>'
            f'<div style="color:#a0b8d0;font-family:\'Noto Sans Devanagari\',sans-serif;'
            f'font-size:0.88rem;line-height:1.7;">{html_lib.escape(desc)}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ── FOOTER ──
st.markdown(
    f'<div style="text-align:center;padding:1.5rem 0 0.5rem;margin-top:2rem;'
    f'border-top:1px solid rgba(0,229,255,0.1);'
    f'font-family:\'Share Tech Mono\',monospace;color:#3a5a7a;font-size:0.65rem;letter-spacing:2px;">'
    f'UP CYBER SHIELD &nbsp;|&nbsp; LAST UPDATE: {datetime.now().strftime("%d %b %Y %H:%M")}'
    f' &nbsp;|&nbsp; HELPLINE: 1930</div>',
    unsafe_allow_html=True,
)
