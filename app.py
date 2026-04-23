import streamlit as st
import requests
import re
import json
import html as html_module
from datetime import datetime, timedelta
import os

# ─────────────────────────────────────────────
# 🔑  SECRETS AUTO-LOAD (Streamlit Cloud support)
# ─────────────────────────────────────────────
def get_secret(key: str) -> str:
    try:
        val = st.secrets.get(key, "")
        if val:
            return val
    except Exception:
        pass
    return st.session_state.get(key, "")


def clean_text(text: str) -> str:
    """Strip ALL HTML tags, decode entities, remove NewsAPI junk, then HTML-escape for safe rendering."""
    if not text:
        return ""
    # Decode HTML entities like &amp; &nbsp; &#39; etc
    text = html_module.unescape(text)
    # Remove ALL HTML tags including </div> <div class="..."> etc
    text = re.sub(r'<[^>]+>', ' ', text)
    # Remove leftover entities
    text = re.sub(r'&[a-zA-Z#0-9]+;', ' ', text)
    # Remove NewsAPI truncation marker [+245 chars]
    text = re.sub(r'\[\+\d+\s*chars?\]', '', text)
    # Collapse whitespace
    text = ' '.join(text.split()).strip()
    # ✅ HTML-escape so < > & don't break st.markdown unsafe_allow_html rendering
    text = html_module.escape(text)
    return text

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
# 🎨  CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Noto+Sans+Devanagari:wght@400;600;700&family=Share+Tech+Mono&display=swap');

:root {
    --bg-main:    #050a14;
    --bg-card:    #0b1422;
    --bg-glass:   rgba(11, 20, 34, 0.85);
    --accent-1:   #00e5ff;
    --accent-2:   #ff4b4b;
    --accent-3:   #39ff14;
    --accent-4:   #ffd700;
    --text-main:  #e0eaff;
    --text-dim:   #7090b0;
    --border:     rgba(0, 229, 255, 0.18);
}

html, body, [class*="css"] {
    font-family: 'Rajdhani', 'Noto Sans Devanagari', sans-serif;
    background-color: var(--bg-main) !important;
    color: var(--text-main) !important;
}

.stApp {
    background:
        linear-gradient(rgba(0,229,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,229,255,0.03) 1px, transparent 1px),
        radial-gradient(ellipse at 20% 50%, rgba(0,229,255,0.06) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 20%, rgba(255,75,75,0.06) 0%, transparent 50%),
        #050a14;
    background-size: 50px 50px, 50px 50px, 100% 100%, 100% 100%, 100% 100%;
}

.cyber-header {
    text-align: center;
    padding: 2rem 0 1rem;
    position: relative;
}
.cyber-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 2.8rem;
    font-weight: 700;
    letter-spacing: 6px;
    text-transform: uppercase;
    background: linear-gradient(135deg, #00e5ff 0%, #ffffff 50%, #00e5ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: none;
    margin: 0;
    line-height: 1.1;
}
.cyber-subtitle {
    font-family: 'Noto Sans Devanagari', sans-serif;
    font-size: 1rem;
    color: var(--accent-1);
    letter-spacing: 3px;
    margin-top: 0.4rem;
    opacity: 0.8;
}
.cyber-line {
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent-1), var(--accent-2), var(--accent-1), transparent);
    margin: 1.2rem auto;
    max-width: 600px;
    border-radius: 2px;
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 1.5rem 0;
}
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}
.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 30px rgba(0,229,255,0.15);
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.metric-card.cyan::before  { background: var(--accent-1); }
.metric-card.red::before   { background: var(--accent-2); }
.metric-card.green::before { background: var(--accent-3); }
.metric-card.gold::before  { background: var(--accent-4); }
.metric-number {
    font-family: 'Share Tech Mono', monospace;
    font-size: 2.2rem;
    font-weight: 700;
    line-height: 1;
}
.metric-card.cyan  .metric-number { color: var(--accent-1); }
.metric-card.red   .metric-number { color: var(--accent-2); }
.metric-card.green .metric-number { color: var(--accent-3); }
.metric-card.gold  .metric-number { color: var(--accent-4); }
.metric-label {
    font-size: 0.78rem;
    color: var(--text-dim);
    margin-top: 0.3rem;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.news-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent-1);
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    transition: all 0.2s;
    position: relative;
}
.news-card:hover {
    border-left-color: var(--accent-2);
    background: rgba(0,229,255,0.04);
    transform: translateX(4px);
}
.news-card.negative { border-left-color: var(--accent-2); }
.news-card.positive { border-left-color: var(--accent-3); }
.news-card.awareness{ border-left-color: var(--accent-4); }
.news-title {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-main);
    margin-bottom: 0.4rem;
    line-height: 1.4;
}
.news-meta {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    color: var(--text-dim);
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-bottom: 0.5rem;
}
.news-summary {
    font-family: 'Noto Sans Devanagari', sans-serif;
    font-size: 0.88rem;
    color: #a0b8d0;
    line-height: 1.6;
    border-top: 1px solid var(--border);
    padding-top: 0.6rem;
    margin-top: 0.6rem;
}
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.badge-red    { background: rgba(255,75,75,0.15);  color: var(--accent-2); border: 1px solid rgba(255,75,75,0.3); }
.badge-green  { background: rgba(57,255,20,0.12);  color: var(--accent-3); border: 1px solid rgba(57,255,20,0.3); }
.badge-cyan   { background: rgba(0,229,255,0.12);  color: var(--accent-1); border: 1px solid rgba(0,229,255,0.3); }
.badge-gold   { background: rgba(255,215,0,0.12);  color: var(--accent-4); border: 1px solid rgba(255,215,0,0.3); }

section[data-testid="stSidebar"] {
    background: rgba(5,10,20,0.95) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] .stTextInput input {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-main) !important;
    border-radius: 8px !important;
    font-family: 'Share Tech Mono', monospace !important;
}
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-main) !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid var(--border) !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-dim) !important;
    border-radius: 8px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.5px !important;
    padding: 8px 16px !important;
    border: none !important;
    transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(0,229,255,0.15) !important;
    color: var(--accent-1) !important;
    border: 1px solid rgba(0,229,255,0.3) !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1.5rem !important;
}

.stButton > button {
    background: linear-gradient(135deg, rgba(0,229,255,0.15), rgba(0,229,255,0.05)) !important;
    border: 1px solid rgba(0,229,255,0.4) !important;
    color: var(--accent-1) !important;
    border-radius: 8px !important;
    font-family: 'Share Tech Mono', monospace !important;
    letter-spacing: 1px !important;
    font-size: 0.85rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: rgba(0,229,255,0.25) !important;
    box-shadow: 0 0 15px rgba(0,229,255,0.3) !important;
    transform: translateY(-1px) !important;
}

.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--accent-1) !important;
    font-family: 'Rajdhani', sans-serif !important;
}

.stSpinner > div {
    border-top-color: var(--accent-1) !important;
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-main); }
::-webkit-scrollbar-thumb { background: rgba(0,229,255,0.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent-1); }

.ai-box {
    background: linear-gradient(135deg, rgba(0,229,255,0.08), rgba(255,75,75,0.06));
    border: 1px solid rgba(0,229,255,0.25);
    border-radius: 12px;
    padding: 1.4rem;
    margin: 1rem 0;
    font-family: 'Noto Sans Devanagari', sans-serif;
    font-size: 0.92rem;
    line-height: 1.8;
    color: var(--text-main);
}
.ai-box-title {
    font-family: 'Share Tech Mono', monospace;
    color: var(--accent-1);
    font-size: 0.8rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.district-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin: 0.8rem 0;
}
.district-pill {
    background: rgba(0,229,255,0.1);
    border: 1px solid rgba(0,229,255,0.25);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.78rem;
    color: var(--accent-1);
    font-family: 'Share Tech Mono', monospace;
    letter-spacing: 0.5px;
}

.alert-box {
    background: rgba(255,75,75,0.1);
    border: 1px solid rgba(255,75,75,0.3);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    font-family: 'Noto Sans Devanagari', sans-serif;
}
.alert-title {
    color: var(--accent-2);
    font-weight: 700;
    font-size: 0.95rem;
    margin-bottom: 0.4rem;
}

.ticker-wrap {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.6rem 1rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    overflow: hidden;
}
.ticker-label {
    font-family: 'Share Tech Mono', monospace;
    color: var(--accent-2);
    font-size: 0.7rem;
    letter-spacing: 2px;
    white-space: nowrap;
    background: rgba(255,75,75,0.15);
    border: 1px solid rgba(255,75,75,0.3);
    padding: 2px 10px;
    border-radius: 4px;
}
.ticker-text {
    font-size: 0.82rem;
    color: var(--text-dim);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 🔧  HELPERS / API CALLS
# ─────────────────────────────────────────────

def fetch_news(api_key: str, district: str = "Uttar Pradesh") -> list:
    if not api_key or api_key == "YOUR_NEWSAPI_KEY":
        return []
    query = f"cyber crime {district}"
    url = (
        f"https://newsapi.org/v2/everything"
        f"?q={requests.utils.quote(query)}"
        f"&language=en"
        f"&sortBy=publishedAt"
        f"&pageSize=15"
        f"&from={(datetime.now()-timedelta(days=14)).strftime('%Y-%m-%d')}"
        f"&apiKey={api_key}"
    )
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        return data.get("articles", [])
    except Exception:
        return []


def groq_summarize(api_key: str, text: str, lang: str = "Hindi") -> str:
    if not api_key or api_key == "YOUR_GROQ_API_KEY":
        return "⚠️ Groq API key configure karein sidebar mein."
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    prompt = (
        f"You are a cyber crime awareness assistant for Uttar Pradesh, India.\n"
        f"Summarize the following news in {lang} in 2-3 concise bullet points. "
        f"Focus on: what happened, district/location if mentioned, impact.\n\n"
        f"News:\n{text[:2000]}\n\n"
        f"Reply ONLY in {lang} bullet points. No English preamble."
    )
    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300,
        "temperature": 0.4,
    }
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers, json=payload, timeout=20
        )
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"AI Error: {e}"


def groq_generate_post(api_key: str, news_title: str, post_type: str) -> str:
    if not api_key or api_key == "YOUR_GROQ_API_KEY":
        return "⚠️ Groq API key configure karein."
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    prompt = (
        f"Create a {post_type} social media post in Hindi+English mix (Hinglish) "
        f"for UP Police Cyber Cell awareness page. Topic: {news_title}.\n"
        f"Include: 1-2 relevant emojis, 2-3 safety tips, call-to-action, "
        f"hashtags: #CyberSafety #UPPolice #DigitalSuraksha #1930Helpline.\n"
        f"Keep it under 280 characters for Twitter. Be urgent but helpful."
    )
    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200,
        "temperature": 0.7,
    }
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers, json=payload, timeout=20
        )
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error: {e}"


def classify_article(title: str, description: str) -> str:
    text = (title + " " + (description or "")).lower()
    neg_kw = ["fraud", "scam", "victim", "cheated", "arrested", "fake", "phishing",
              "extortion", "loot", "ठगी", "धोखा", "फर्जी", "गिरफ्तार"]
    pos_kw = ["busted", "recovered", "awareness", "crackdown", "action", "helpline",
              "safe", "campaign", "जागरूकता", "गिरोह ध्वस्त", "वापस"]
    neg = sum(1 for k in neg_kw if k in text)
    pos = sum(1 for k in pos_kw if k in text)
    if pos > neg:
        return "positive"
    elif neg > 0:
        return "negative"
    return "awareness"


# ─────────────────────────────────────────────
# 📊  DEMO DATA
# ─────────────────────────────────────────────
DEMO_NEWS = [
    {"title": "Lucknow: OTP Fraud Gang Busted — 12 Arrested by UP Cyber Cell",
     "description": "UP Police की Cyber Cell ने Lucknow में एक बड़े OTP fraud gang को गिरफ्तार किया। 12 आरोपियों से ₹45 लाख की रकम बरामद। पीड़ितों को refund की प्रक्रिया शुरू।",
     "source": "Amar Ujala", "publishedAt": "2026-04-17", "url": "#",
     "district": "Lucknow", "type": "positive"},
    {"title": "Kanpur: Online Loan App Scam — 200+ Victims File Complaint",
     "description": "Kanpur में fake loan apps के ज़रिए 200 से अधिक लोगों से ठगी। आरोपियों ने Aadhaar डेटा चुराकर fake CIBIL score दिखाया। Police investigating.",
     "source": "Dainik Jagran", "publishedAt": "2026-04-16", "url": "#",
     "district": "Kanpur", "type": "negative"},
    {"title": "Varanasi: Cyber Safety Workshop in 50 Schools — 10,000 Students Trained",
     "description": "Varanasi Police ने 50 schools में Cyber Safety Workshop आयोजित की। 10,000 से अधिक students को digital fraud, phishing और social media safety के बारे में educate किया गया।",
     "source": "Hindustan Times", "publishedAt": "2026-04-15", "url": "#",
     "district": "Varanasi", "type": "awareness"},
    {"title": "Noida: Fake Job Portal Scam — IT Professionals Targeted",
     "description": "Noida में एक fake job portal ने IT professionals से ₹15,000–50,000 registration fee ली। 85 शिकायतें दर्ज। Cybercrime portal पर FIR filed।",
     "source": "Times of India UP", "publishedAt": "2026-04-14", "url": "#",
     "district": "Noida", "type": "negative"},
    {"title": "Agra: Cyber Cell Recovers ₹32 Lakh for Senior Citizen Fraud Victim",
     "description": "Agra के 68 वर्षीय senior citizen से ₹32 लाख की digital arrest fraud हुई थी। UP Cyber Cell ने तत्परता से action लेकर पूरी रकम वापस दिलाई।",
     "source": "UP Police Official", "publishedAt": "2026-04-13", "url": "#",
     "district": "Agra", "type": "positive"},
    {"title": "Gorakhpur: Phishing SMS Campaign Targets Bank Customers",
     "description": "Gorakhpur में bank customers को fake KYC update SMS भेजे जा रहे हैं। UP Cyber Cell ने alert जारी किया — किसी भी link पर click न करें, Helpline 1930 पर call करें।",
     "source": "Amar Ujala", "publishedAt": "2026-04-12", "url": "#",
     "district": "Gorakhpur", "type": "negative"},
    {"title": "Prayagraj: Digital Arrest Awareness Campaign — 'Ruko, Socho, Report Karo'",
     "description": "Prayagraj Police ने 'Ruko, Socho, Report Karo' नाम से digital arrest awareness campaign शुरू किया। Rickshaw, auto, और bus stands पर posters लगाए गए।",
     "source": "Prayagraj Police", "publishedAt": "2026-04-11", "url": "#",
     "district": "Prayagraj", "type": "awareness"},
    {"title": "Meerut: Cryptocurrency Fraud — ₹1.2 Crore Scam Exposed",
     "description": "Meerut में एक fake crypto trading platform ने investors से ₹1.2 crore ठगे। 3 accused arrested, funds frozen in 6 bank accounts by Cyber Cell.",
     "source": "Dainik Jagran", "publishedAt": "2026-04-10", "url": "#",
     "district": "Meerut", "type": "negative"},
]

AWARENESS_TIPS = [
    ("OTP कभी Share न करें", "Bank, Police, या कोई भी government officer कभी OTP नहीं माँगता।", "🔐"),
    ("Digital Arrest नहीं होता", "कोई भी agency video call पर arrest नहीं करती। यह fraud है। Call काटें।", "📵"),
    ("Helpline 1930", "Cyber fraud हुआ? तुरंत 1930 dial करें या cybercrime.gov.in पर report करें।", "📞"),
    ("URL ध्यान से Check करें", "Bank website का URL हमेशा https:// से शुरू होना चाहिए। Spelling check करें।", "🌐"),
    ("Fake Job Offers", "Advance fee माँगने वाले job portals से सावधान। Verified company को direct contact करें।", "💼"),
    ("Social Media Privacy", "अपना phone number, address, और Aadhaar social media पर share न करें।", "🔒"),
]

UP_DISTRICTS = [
    "Lucknow", "Kanpur", "Agra", "Varanasi", "Prayagraj", "Meerut",
    "Noida", "Ghaziabad", "Gorakhpur", "Bareilly", "Aligarh", "Moradabad",
    "Saharanpur", "Firozabad", "Jhansi", "Mathura", "Muzaffarnagar", "Shahjahanpur"
]

# ─────────────────────────────────────────────
# 🔑  SESSION STATE INIT
# ─────────────────────────────────────────────
if "news_api_key" not in st.session_state:
    st.session_state["news_api_key"] = ""
if "groq_api_key" not in st.session_state:
    st.session_state["groq_api_key"] = ""

# AI summary results store — tab+title key se store karo
if "ai_summaries" not in st.session_state:
    st.session_state["ai_summaries"] = {}

# ─────────────────────────────────────────────
# 🗂️  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:1rem 0;'>
        <div style='font-family:"Share Tech Mono",monospace; color:#00e5ff; font-size:1.4rem; letter-spacing:3px;'>🛡️ UP CYBER</div>
        <div style='font-family:"Share Tech Mono",monospace; color:#7090b0; font-size:0.7rem; letter-spacing:4px;'>SHIELD DASHBOARD</div>
    </div>
    <hr style='border-color:rgba(0,229,255,0.15); margin:0.5rem 0 1.2rem;'>
    """, unsafe_allow_html=True)

    _secret_news = get_secret("NEWS_API_KEY")
    _secret_groq = get_secret("GROQ_API_KEY")
    if _secret_news and not st.session_state["news_api_key"]:
        st.session_state["news_api_key"] = _secret_news
    if _secret_groq and not st.session_state["groq_api_key"]:
        st.session_state["groq_api_key"] = _secret_groq

    news_from_secret = bool(_secret_news)
    groq_from_secret = bool(_secret_groq)

    st.markdown("**🔑 API Keys**")
    if news_from_secret:
        st.success("✅ NewsAPI — Secrets se load hua")
    else:
        st.text_input("NewsAPI Key (Free)", key="news_api_key", type="password",
                      help="newsapi.org पर free account बनाएँ", placeholder="xxxxxxxxxxxxxxxx")

    if groq_from_secret:
        st.success("✅ Groq API — Secrets se load hua")
    else:
        st.text_input("Groq API Key (Free)", key="groq_api_key", type="password",
                      help="console.groq.com पर free account बनाएँ", placeholder="gsk_xxxxxxxxxxxx")

    news_api_key = st.session_state.get("news_api_key", "")
    groq_api_key = st.session_state.get("groq_api_key", "")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**📍 Filter**")
    selected_district = st.selectbox("जिला चुनें", ["सभी जिले"] + UP_DISTRICTS)
    selected_type = st.selectbox(
        "Category",
        ["सभी", "🔴 Negative Cases", "🟢 Positive Actions", "🟡 Awareness"]
    )

    st.markdown("<br>", unsafe_allow_html=True)
    fetch_live = st.button("🔄 Live Data Fetch", use_container_width=True)

    st.markdown("""
    <hr style='border-color:rgba(0,229,255,0.1);'>
    <div style='font-family:"Share Tech Mono",monospace; font-size:0.65rem; color:#3a5a7a; text-align:center; line-height:2;'>
    CYBERCRIME HELPLINE<br>
    <span style='color:#ff4b4b; font-size:1.1rem;'>1930</span><br>
    cybercrime.gov.in
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 🏠  HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="cyber-header">
    <div class="cyber-title">🛡️ UP CYBER SHIELD</div>
    <div class="cyber-subtitle">उत्तर प्रदेश साइबर अपराध जागरूकता डैशबोर्ड</div>
    <div class="cyber-line"></div>
</div>
""", unsafe_allow_html=True)

ticker_items = " &nbsp;●&nbsp; ".join([n["title"][:60] + "…" for n in DEMO_NEWS[:5]])
st.markdown(f"""
<div class="ticker-wrap">
    <span class="ticker-label">⚡ LIVE</span>
    <span class="ticker-text">{ticker_items}</span>
</div>
""", unsafe_allow_html=True)

neg_count = sum(1 for n in DEMO_NEWS if n["type"] == "negative")
pos_count = sum(1 for n in DEMO_NEWS if n["type"] == "positive")
aw_count  = sum(1 for n in DEMO_NEWS if n["type"] == "awareness")

st.markdown(f"""
<div class="metric-grid">
    <div class="metric-card cyan">
        <div class="metric-number">{len(DEMO_NEWS)}</div>
        <div class="metric-label">📰 Total News</div>
    </div>
    <div class="metric-card red">
        <div class="metric-number">{neg_count}</div>
        <div class="metric-label">⚠️ Fraud Cases</div>
    </div>
    <div class="metric-card green">
        <div class="metric-number">{pos_count}</div>
        <div class="metric-label">✅ Police Actions</div>
    </div>
    <div class="metric-card gold">
        <div class="metric-number">{aw_count}</div>
        <div class="metric-label">📢 Campaigns</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 📰  DATA + FILTER
# ─────────────────────────────────────────────
articles = DEMO_NEWS.copy()

if fetch_live and news_api_key:
    with st.spinner("Fetching live news..."):
        district_q = selected_district if selected_district != "सभी जिले" else "Uttar Pradesh"
        live = fetch_news(news_api_key, district_q)
        if live:
            articles = [
                {
                    "title": a.get("title", ""),
                    "description": a.get("description", "") or a.get("content", ""),
                    "source": a.get("source", {}).get("name", "News"),
                    "publishedAt": a.get("publishedAt", "")[:10],
                    "url": a.get("url", "#"),
                    "district": district_q,
                    "type": classify_article(a.get("title",""), a.get("description","")),
                }
                for a in live if a.get("title")
            ]
            st.success(f"✅ {len(articles)} live articles loaded!")

filtered = articles
if selected_district != "सभी जिले":
    filtered = [a for a in filtered if
                selected_district.lower() in a.get("district", "").lower() or
                selected_district.lower() in (a.get("title","") + a.get("description","")).lower()]
type_map = {"🔴 Negative Cases": "negative", "🟢 Positive Actions": "positive", "🟡 Awareness": "awareness"}
if selected_type != "सभी":
    filtered = [a for a in filtered if a.get("type") == type_map.get(selected_type, "")]

# ─────────────────────────────────────────────
# 🃏  NEWS CARD RENDERER
# ✅ FIX: tab_prefix parameter added — duplicate key error solved
# ─────────────────────────────────────────────
def render_news_card(article: dict, show_ai: bool = False, tab_prefix: str = "default", card_index: int = 0):
    a_type = article.get("type", "awareness")
    badge_map = {
        "negative": ("badge-red",   "⚠️ FRAUD"),
        "positive": ("badge-green", "✅ ACTION"),
        "awareness":("badge-gold",  "📢 AWARENESS"),
    }
    badge_cls, badge_txt = badge_map.get(a_type, ("badge-cyan", "📰 NEWS"))
    district_tag = article.get("district", "UP")
    date_str     = article.get("publishedAt", "")[:10]
    source       = article.get("source", "")
    url          = article.get("url", "#")
    link_html    = (
        f'<a href="{url}" target="_blank" style="color:#00e5ff;'
        f' text-decoration:none; font-size:0.78rem;">🔗 Read More</a>'
        if url != "#" else ""
    )

    title_clean = clean_text(article.get("title", ""))
    desc_raw    = article.get("description", "") or article.get("content", "") or ""
    desc_clean  = clean_text(desc_raw)
    desc_show   = desc_clean[:300] + ("…" if len(desc_clean) > 300 else "")
    if not desc_show.strip():
        desc_show = "विस्तृत जानकारी के लिए 'Read More' पर click करें।"

    st.markdown(f"""
    <div class="news-card {a_type}">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;
                    flex-wrap:wrap; gap:0.5rem; margin-bottom:0.5rem;">
            <span class="badge {badge_cls}">{badge_txt}</span>
            <span class="badge badge-cyan">📍 {district_tag}</span>
        </div>
        <div class="news-title">{title_clean}</div>
        <div class="news-meta">
            <span>📅 {date_str}</span>
            <span>📰 {source}</span>
            {link_html}
        </div>
        <div class="news-summary">{desc_show}</div>
    </div>
    """, unsafe_allow_html=True)

    if show_ai:
        # ✅ UNIQUE KEY: tab_prefix + card_index — kabhi duplicate nahi hoga
        btn_key     = f"ai_btn_{tab_prefix}_{card_index}"
        summary_key = f"ai_sum_{tab_prefix}_{card_index}"

        if st.button("🤖 AI Hindi Summary", key=btn_key):
            if not groq_api_key:
                st.warning("⚠️ Sidebar में Groq API key डालें।")
            else:
                with st.spinner("AI summarizing..."):
                    summary = groq_summarize(
                        groq_api_key,
                        title_clean + " " + article.get("description", "")
                    )
                st.session_state["ai_summaries"][summary_key] = summary

        # Summary already generated hai toh show karo
        if summary_key in st.session_state["ai_summaries"]:
            st.markdown(f"""
            <div class="ai-box">
                <div class="ai-box-title">🤖 AI SUMMARY (Hindi)</div>
                {st.session_state["ai_summaries"][summary_key]}
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 🗂️  MAIN TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📰 Latest News",
    "🔴 Fraud Cases",
    "🟢 Police Action",
    "📢 Awareness",
    "🤖 AI Post Generator",
    "ℹ️ Cyber Tips"
])

# ── TAB 1: ALL NEWS ──
with tab1:
    st.markdown(
        f"### 📰 सभी ताज़ा खबरें &nbsp;"
        f"<span style='font-size:0.8rem; color:#7090b0;'>({len(filtered)} articles)</span>",
        unsafe_allow_html=True
    )
    if not filtered:
        st.info("कोई article नहीं मिला। Filter बदलें या Live Fetch करें।")
    for idx, art in enumerate(filtered[:10]):
        render_news_card(art, show_ai=True, tab_prefix="tab1", card_index=idx)

# ── TAB 2: FRAUD CASES ──
with tab2:
    neg_articles = [a for a in filtered if a.get("type") == "negative"]
    st.markdown(
        f"### ⚠️ Fraud & Cyber Crime Cases &nbsp;"
        f"<span style='font-size:0.8rem; color:#7090b0;'>({len(neg_articles)} cases)</span>",
        unsafe_allow_html=True
    )
    st.markdown("""
    <div class="alert-box">
        <div class="alert-title">🚨 ACTIVE ALERTS — UP Cyber Cell</div>
        <div style='font-family:"Noto Sans Devanagari",sans-serif; font-size:0.85rem; color:#e0eaff; line-height:1.8;'>
            • <b>Digital Arrest Scam:</b> Fake CBI/ED officers video call करके डरा रहे हैं।<br>
            • <b>Loan App Fraud:</b> Fake apps phone gallery access लेकर blackmail कर रहे हैं।<br>
            • <b>Investment Scam:</b> Telegram groups में fake crypto returns का झांसा दे रहे हैं।
        </div>
    </div>
    """, unsafe_allow_html=True)
    if not neg_articles:
        st.success("✅ आपके filter में कोई fraud case नहीं मिला!")
    for idx, art in enumerate(neg_articles):
        render_news_card(art, show_ai=True, tab_prefix="tab2", card_index=idx)

# ── TAB 3: POSITIVE ACTIONS ──
with tab3:
    pos_articles = [a for a in filtered if a.get("type") == "positive"]
    st.markdown(
        f"### ✅ Police Actions & Success Stories &nbsp;"
        f"<span style='font-size:0.8rem; color:#7090b0;'>({len(pos_articles)} stories)</span>",
        unsafe_allow_html=True
    )
    st.markdown("""
    <div style='background:rgba(57,255,20,0.07); border:1px solid rgba(57,255,20,0.2);
                border-radius:10px; padding:1rem 1.2rem; margin-bottom:1rem;'>
        <div style='color:#39ff14; font-family:"Share Tech Mono",monospace; font-size:0.8rem;
                    letter-spacing:2px; margin-bottom:0.5rem;'>📊 UP CYBER CELL — APRIL 2026 STATS</div>
        <div style='display:grid; grid-template-columns:repeat(3,1fr); gap:1rem; font-family:"Rajdhani",sans-serif;'>
            <div style='text-align:center;'>
                <div style='font-size:1.8rem; color:#39ff14; font-family:"Share Tech Mono",monospace;'>₹4.2Cr</div>
                <div style='font-size:0.75rem; color:#7090b0;'>Recovered</div>
            </div>
            <div style='text-align:center;'>
                <div style='font-size:1.8rem; color:#39ff14; font-family:"Share Tech Mono",monospace;'>156</div>
                <div style='font-size:0.75rem; color:#7090b0;'>Arrests</div>
            </div>
            <div style='text-align:center;'>
                <div style='font-size:1.8rem; color:#39ff14; font-family:"Share Tech Mono",monospace;'>892</div>
                <div style='font-size:0.75rem; color:#7090b0;'>Cases Closed</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if not pos_articles:
        st.info("Filter बदलें।")
    for idx, art in enumerate(pos_articles):
        render_news_card(art, show_ai=True, tab_prefix="tab3", card_index=idx)

# ── TAB 4: AWARENESS CAMPAIGNS ──
with tab4:
    aw_articles = [a for a in filtered if a.get("type") == "awareness"]
    st.markdown(
        f"### 📢 Awareness Campaigns &nbsp;"
        f"<span style='font-size:0.8rem; color:#7090b0;'>({len(aw_articles)} campaigns)</span>",
        unsafe_allow_html=True
    )
    districts_str = " ".join([f'<span class="district-pill">{d}</span>' for d in UP_DISTRICTS])
    st.markdown(f'<div class="district-pills">{districts_str}</div>', unsafe_allow_html=True)
    if not aw_articles:
        st.info("Filter बदलें।")
    for idx, art in enumerate(aw_articles):
        render_news_card(art, show_ai=True, tab_prefix="tab4", card_index=idx)

# ── TAB 5: AI POST GENERATOR ──
with tab5:
    st.markdown("### 🤖 AI-Powered Social Media Post Generator")
    st.markdown("""
    <div style='background:rgba(0,229,255,0.06); border:1px solid rgba(0,229,255,0.2);
                border-radius:10px; padding:1rem; margin-bottom:1rem; font-size:0.85rem;
                color:#a0b8d0; font-family:"Noto Sans Devanagari",sans-serif;'>
    Groq API (Free) की मदद से cyber crime awareness के लिए X/Twitter, Facebook, या Instagram
    posts तुरंत generate करें।
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        post_topic = st.text_area(
            "📝 News headline या topic डालें",
            placeholder="Example: Lucknow mein OTP fraud gang pakda gaya, 12 arrested...",
            height=100
        )
    with col2:
        post_platform = st.selectbox("Platform", ["Twitter/X", "Facebook", "Instagram", "WhatsApp"])
        post_tone     = st.selectbox("Tone", ["Urgent Warning ⚠️", "Informative 📊", "Motivational 👏", "Helpful Tips 💡"])

    if st.button("⚡ Generate Post", key="gen_post_main", use_container_width=True):
        if not post_topic:
            st.warning("Topic डालें।")
        elif not groq_api_key:
            st.error("Sidebar में Groq API key डालें।")
        else:
            with st.spinner("AI post likh raha hai..."):
                post = groq_generate_post(groq_api_key, post_topic, f"{post_platform} {post_tone}")
            st.markdown(f"""
            <div class="ai-box">
                <div class="ai-box-title">✨ GENERATED POST — {post_platform.upper()}</div>
                <div style='font-family:"Noto Sans Devanagari",sans-serif; white-space:pre-wrap;'>{post}</div>
            </div>
            """, unsafe_allow_html=True)
            st.code(post, language=None)

    st.markdown("---")
    st.markdown("#### 🔁 Quick Generate from Latest News")
    for i, art in enumerate(filtered[:4]):
        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown(
                f"<div style='font-size:0.85rem; color:#a0b8d0; padding:0.3rem 0;'>"
                f"📰 {art['title'][:80]}…</div>",
                unsafe_allow_html=True
            )
        with c2:
            # ✅ UNIQUE KEY: tab5_quick_ + index
            if st.button("⚡ Post", key=f"tab5_quick_{i}"):
                with st.spinner("Generating..."):
                    p = groq_generate_post(groq_api_key, art["title"], "Twitter awareness")
                st.markdown(
                    f'<div class="ai-box"><div class="ai-box-title">✨ POST</div>{p}</div>',
                    unsafe_allow_html=True
                )

# ── TAB 6: CYBER TIPS ──
with tab6:
    st.markdown("### 🛡️ Cyber Safety Tips — उत्तर प्रदेश")
    st.markdown("""
    <div style='background:rgba(255,215,0,0.07); border:1px solid rgba(255,215,0,0.2);
                border-radius:10px; padding:1rem 1.2rem; margin-bottom:1.5rem;'>
        <div style='color:#ffd700; font-family:"Share Tech Mono",monospace; font-size:0.8rem;
                    letter-spacing:2px; margin-bottom:0.5rem;'>⚡ REMEMBER</div>
        <div style='color:#e0eaff; font-family:"Noto Sans Devanagari",sans-serif; font-size:1rem; line-height:1.8;'>
        🆘 Cyber Fraud हो तो: <b style='color:#ff4b4b; font-size:1.2rem;'>1930</b> पर call करें |
        <b>cybercrime.gov.in</b> पर report करें
        </div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(2)
    for i, (title, desc, icon) in enumerate(AWARENESS_TIPS):
        with cols[i % 2]:
            st.markdown(f"""
            <div style='background:var(--bg-card); border:1px solid var(--border);
                        border-radius:10px; padding:1.2rem; margin-bottom:1rem; transition:all 0.2s;'>
                <div style='font-size:2rem; margin-bottom:0.5rem;'>{icon}</div>
                <div style='color:#00e5ff; font-family:"Rajdhani",sans-serif; font-weight:700;
                            font-size:1rem; margin-bottom:0.4rem;'>{title}</div>
                <div style='color:#a0b8d0; font-family:"Noto Sans Devanagari",sans-serif;
                            font-size:0.85rem; line-height:1.6;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 🔽  FOOTER
# ─────────────────────────────────────────────
st.markdown(f"""
<div style='text-align:center; padding:2rem 0 1rem; margin-top:3rem;
            border-top:1px solid rgba(0,229,255,0.1);'>
    <div style='font-family:"Share Tech Mono",monospace; color:#3a5a7a; font-size:0.7rem; letter-spacing:3px;'>
    UP CYBER SHIELD DASHBOARD &nbsp;|&nbsp;
    LAST UPDATE: {datetime.now().strftime("%d %b %Y %H:%M")} &nbsp;|&nbsp;
    HELPLINE: 1930
    </div>
</div>
""", unsafe_allow_html=True)
