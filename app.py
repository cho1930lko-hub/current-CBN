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
# 🎨  CSS
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

/* ── NEWS CARD ── */
.news-item {
    border-left:4px solid #00e5ff;
    padding:1rem 1.2rem; margin-bottom:0.6rem;
    background:#0b1422; border-radius:0 10px 10px 0;
}
.news-item.neg { border-left-color:#ff4b4b; }
.news-item.pos { border-left-color:#39ff14; }
.news-item.aw  { border-left-color:#ffd700; }
.news-item .ntitle { font-weight:700; font-size:1.05rem; color:#e0eaff; line-height:1.4; }
.news-item .nmeta  { font-size:0.72rem; color:#7090b0; margin:0.3rem 0; font-family:'Share Tech Mono',monospace; }
.news-item .ndesc  {
    font-family:'Noto Sans Devanagari',sans-serif;
    font-size:0.9rem; color:#c0d0e8; line-height:1.8;
    margin-top:0.5rem;
    border-top:1px solid rgba(255,255,255,0.06);
    padding-top:0.5rem;
}
.read-link {
    display:inline-block;
    margin-top:0.6rem;
    padding:0.3rem 0.9rem;
    background:rgba(0,229,255,0.1);
    border:1px solid rgba(0,229,255,0.35);
    border-radius:20px;
    color:#00e5ff !important;
    font-size:0.78rem;
    font-family:'Share Tech Mono',monospace;
    letter-spacing:1px;
    text-decoration:none !important;
}
.read-link:hover { background:rgba(0,229,255,0.2); }

/* ── AI POST BOX ── */
.ai-box {
    background:linear-gradient(135deg,rgba(0,229,255,0.07),rgba(255,75,75,0.05));
    border:1px solid rgba(0,229,255,0.22); border-radius:10px;
    padding:1rem 1.2rem; margin:0.5rem 0;
    font-family:'Noto Sans Devanagari',sans-serif;
    font-size:0.9rem; line-height:1.8; color:#e0eaff;
    white-space:pre-wrap;
}

/* ── GENERATED POST CARD ── */
.post-card {
    background: linear-gradient(135deg, #0d1f35, #0a1528);
    border: 1px solid rgba(0,229,255,0.3);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin: 0.8rem 0;
    position: relative;
    overflow: hidden;
}
.post-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #00e5ff, #ff4b4b, #ffd700, #39ff14);
}
.post-card .platform-badge {
    display: inline-block;
    background: rgba(0,229,255,0.15);
    border: 1px solid rgba(0,229,255,0.3);
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: #00e5ff;
    letter-spacing: 1px;
    margin-bottom: 0.8rem;
}
.post-card .post-text {
    font-family: 'Noto Sans Devanagari', sans-serif;
    font-size: 1rem;
    line-height: 1.9;
    color: #e8f0ff;
    white-space: pre-wrap;
}
.post-card .char-count {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.68rem;
    color: #4a7090;
    margin-top: 0.8rem;
    text-align: right;
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


def groq_call(api_key: str, prompt: str, max_tokens: int = 500) -> str:
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
                    "temperature": 0.6,
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


# ── IMPROVED POST GENERATOR ──
PLATFORM_RULES = {
    "Twitter/X": {
        "limit": "280 characters MAXIMUM. Very short, punchy, 2-3 lines only.",
        "style": "Twitter post with 1-2 lines of text + hashtags. Ultra concise.",
        "emojis": "🚨⚠️🔐📵💰🛡️",
    },
    "Facebook": {
        "limit": "300-500 characters. Paragraph format, friendly tone.",
        "style": "Facebook awareness post — 2 short paragraphs, bullet tips, CTA at end.",
        "emojis": "🔴🛡️⚠️✅📞💡🙏",
    },
    "Instagram": {
        "limit": "150-250 characters caption + 10-15 hashtags at end.",
        "style": "Instagram caption — eye-catching first line, 3 emoji bullet tips, hashtag block at end.",
        "emojis": "🔴🔐💻🛡️⚡✨🚫📵",
    },
    "WhatsApp": {
        "limit": "200-350 characters. Conversational, feels like a friend warning you.",
        "style": "WhatsApp forward message — starts with bold warning, 3 tips, ends with helpline number.",
        "emojis": "🚨⛔🔐📞✅👆💬",
    },
}

TONE_GUIDE = {
    "Urgent Warning":   "URGENT, alarming, creates immediate fear/action. Use ALL CAPS for key words.",
    "Informative":      "Educational, calm, explains HOW the fraud works step by step.",
    "Motivational":     "Empowering, positive — 'You can protect yourself!' energy.",
    "Helpful Tips":     "Friendly checklist style — practical do's and don'ts.",
}

def groq_post(api_key: str, topic: str, platform: str, tone: str) -> str:
    p = PLATFORM_RULES.get(platform, PLATFORM_RULES["WhatsApp"])
    t = TONE_GUIDE.get(tone, TONE_GUIDE["Urgent Warning"])

    prompt = f"""You are a social media expert for UP Police Cyber Cell, India.

Create a {platform} post about: "{topic}"

PLATFORM RULES for {platform}:
- {p['limit']}
- Style: {p['style']}
- Suggested emojis to use (pick relevant ones): {p['emojis']}

TONE: {t}

LANGUAGE: Hindi ONLY (Devanagari script). No English words except: OTP, Cyber, Online, Helpline, FIR, Link, App.

MANDATORY elements to include naturally:
- Helpline number: 1930
- Website: cybercrime.gov.in  
- Relevant hashtags in Hindi context: #CyberSafety #UPPolice #1930Helpline #साइबर_सुरक्षा

FORMAT OUTPUT:
- Start directly with the post content (no explanation, no "Here is your post:")
- Make it READY TO COPY AND PASTE
- Use emojis generously to make it visually attractive
- Each tip/point on its own line with emoji bullet

Post:"""

    return groq_call(api_key, prompt, max_tokens=500)


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
# 📊  DEMO DATA
# ─────────────────────────────────────────────
DEMO = [
    {
        "title": "Lucknow: OTP Fraud Gang Busted — 12 Arrested by UP Cyber Cell",
        "desc": (
            "UP Police की Cyber Cell ने Lucknow में एक बड़े OTP fraud gang का पर्दाफाश किया है। "
            "इस गैंग के 12 सदस्यों को गिरफ्तार किया गया, जो पिछले 2 वर्षों से सक्रिय थे। "
            "आरोपी खुद को बैंक अधिकारी बताकर पीड़ितों से OTP मांगते थे और उनके खाते खाली कर देते थे। "
            "45 लाख रुपये नकद, 18 मोबाइल फोन, और 6 SIM card cloning devices बरामद हुईं। "
            "अब तक 200 से अधिक शिकायतें इस गैंग से जुड़ी हैं। पीड़ितों को रकम refund की प्रक्रिया शुरू की गई।"
        ),
        "source": "Amar Ujala", "date": "2026-04-17",
        "url": "https://www.amarujala.com", "type": "pos"
    },
    {
        "title": "Kanpur: Online Loan App Scam — 200+ Victims File Complaint",
        "desc": (
            "Kanpur में fake loan apps के जरिए 200 से अधिक लोगों से ठगी का मामला सामने आया है। "
            "आरोपियों ने Play Store पर नकली lending app upload की थी जो असली दिखती थी। "
            "App install करते ही contacts और gallery का access ले लिया जाता था। "
            "फिर fake CIBIL score दिखाकर 50,000 से 2 लाख तक का loan देने का झांसा दिया जाता था। "
            "Processing fee के नाम पर 5,000 से 20,000 रुपये ऐंठे जाते थे और बाद में blackmail किया जाता था। "
            "पुलिस ने मुख्य आरोपी दिल्ली से गिरफ्तार किया, जांच जारी है।"
        ),
        "source": "Dainik Jagran", "date": "2026-04-16",
        "url": "https://www.jagran.com", "type": "neg"
    },
    {
        "title": "Varanasi: Cyber Safety Workshop in 50 Schools — 10,000 Students Trained",
        "desc": (
            "Varanasi Police ने 'Safe Digital Bharat' अभियान के तहत 50 schools में Cyber Safety Workshop आयोजित की। "
            "10,000 से अधिक students को digital fraud, phishing, social media safety और online gaming addiction के बारे में जागरूक किया गया। "
            "विशेष रूप से class 8 से 12 के बच्चों को target किया गया क्योंकि वे social media पर सबसे अधिक active हैं। "
            "Workshop में fake profiles पहचानना, password security और cyber bullying से बचाव सिखाया गया। "
            "अगले 3 महीनों में 100 और schools को cover करने की योजना है।"
        ),
        "source": "Hindustan Times", "date": "2026-04-15",
        "url": "https://www.hindustantimes.com", "type": "aw"
    },
    {
        "title": "Noida: Fake Job Portal Scam — IT Professionals Targeted",
        "desc": (
            "Noida में एक fake job portal 'TechHire India' ने IT professionals को निशाना बनाया। "
            "LinkedIn जैसी दिखने वाली इस website पर MNCs के नाम से fake job listings डाली गईं। "
            "Interview के बाद 'selection' letter भेजकर 15,000 से 50,000 रुपये registration fee माँगी जाती थी। "
            "85 शिकायतें दर्ज हुईं, कुल नुकसान 28 लाख रुपये से अधिक। "
            "Cybercrime portal पर FIR filed की गई, 2 servers Maharashtra से trace किए गए। "
            "पुलिस ने alert जारी करते हुए कहा कि कोई genuine company advance fee नहीं माँगती।"
        ),
        "source": "Times of India UP", "date": "2026-04-14",
        "url": "https://timesofindia.indiatimes.com", "type": "neg"
    },
    {
        "title": "Agra: Cyber Cell Recovers Rs 32 Lakh for Senior Citizen Fraud Victim",
        "desc": (
            "Agra के 68 वर्षीय retired teacher श्री रामप्रसाद वर्मा को digital arrest fraud का शिकार बनाया गया था। "
            "आरोपियों ने CBI officer बनकर video call की और कहा कि उनके account से money laundering हो रही है। "
            "डर के कारण उन्होंने 32 लाख रुपये अलग-अलग accounts में transfer कर दिए। "
            "परिवार ने 24 घंटे के भीतर 1930 पर complaint की। "
            "UP Cyber Cell ने तत्परता से action लेकर सभी transactions freeze कराईं और पूरी 32 लाख रुपये की रकम वापस दिलाई। "
            "यह UP Cyber Cell की 2026 की सबसे बड़ी recovery है।"
        ),
        "source": "UP Police Official", "date": "2026-04-13",
        "url": "https://uppolice.gov.in", "type": "pos"
    },
    {
        "title": "Gorakhpur: Phishing SMS Campaign Targets Bank Customers",
        "desc": (
            "Gorakhpur और आसपास के जिलों में bank customers को fake KYC update SMS भेजे जा रहे हैं। "
            "SMS में लिखा होता है: 'आपका account 24 घंटे में बंद हो जाएगा, यहाँ click करें।' "
            "Link पर click करने पर एक fake bank website खुलती है जो बिल्कुल असली जैसी दिखती है। "
            "वहाँ login details और OTP enter करते ही account empty हो जाता है। "
            "अब तक 45 लोग इसके शिकार हो चुके हैं, कुल नुकसान 18 लाख रुपये। "
            "UP Cyber Cell ने alert जारी किया: Bank कभी SMS पर link नहीं भेजता। Helpline 1930 पर call करें।"
        ),
        "source": "Amar Ujala", "date": "2026-04-12",
        "url": "https://www.amarujala.com", "type": "neg"
    },
    {
        "title": "Prayagraj: Digital Arrest Campaign — 'Ruko Socho Report Karo'",
        "desc": (
            "Prayagraj Police ने 'रुको, सोचो, Report करो' नाम से एक बड़ा digital arrest awareness campaign शुरू किया है। "
            "इस campaign में 500 से अधिक rickshaw, auto और bus stands पर जागरूकता posters लगाए गए हैं। "
            "साथ ही local cable TV पर short awareness videos चलाई जा रही हैं। "
            "Mohalla-level पर volunteers को trained किया गया है जो घर-घर जाकर senior citizens को समझाते हैं। "
            "Campaign का focus है: CBI/ED/Police कभी video call पर arrest नहीं करती, घबराएँ नहीं, पहले 1930 call करें।"
        ),
        "source": "Prayagraj Police", "date": "2026-04-11",
        "url": "https://uppolice.gov.in", "type": "aw"
    },
    {
        "title": "Meerut: Cryptocurrency Fraud — Rs 1.2 Crore Scam Exposed",
        "desc": (
            "Meerut में एक fake crypto trading platform 'CryptoGainIndia' ने investors से 1.2 crore रुपये ठगे। "
            "Platform पर पहले छोटा investment डलवाया जाता था और fake profit दिखाया जाता था। "
            "जब बड़ा amount invest होता था तो platform 'maintenance mode' में चला जाता था। "
            "32 investors ने 1.5 लाख से 8 लाख तक invest किए थे। "
            "Cyber Cell ने 3 accused arrest किए — दो Meerut के, एक Delhi का। "
            "6 bank accounts में 45 लाख रुपये freeze किए गए, बाकी recovery जारी है।"
        ),
        "source": "Dainik Jagran", "date": "2026-04-10",
        "url": "https://www.jagran.com", "type": "neg"
    },
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
            t   = strip_html(a.get("title", ""))
            # ── FIX: combine description + content for maximum text ──
            desc_raw    = strip_html(a.get("description", "") or "")
            content_raw = strip_html(a.get("content", "") or "")
            # content often ends with "[+N chars]" — already stripped above
            # Prefer content if it's longer, else combine both
            if len(content_raw) > len(desc_raw):
                d = content_raw
            elif desc_raw and content_raw and content_raw not in desc_raw:
                d = desc_raw + " " + content_raw
            else:
                d = desc_raw or content_raw
            d = d or "Vistrit jaankari ke liye neeche link par click karein."
            articles.append({
                "title":  t,
                "desc":   d,
                "source": a.get("source", {}).get("name", ""),
                "date":   (a.get("publishedAt", "") or "")[:10],
                "url":    a.get("url", "#"),
                "type":   classify(t, d),
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
# 📋  NEWS RENDERER
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

        safe_title = html_lib.escape(t)
        safe_desc  = html_lib.escape(d)
        safe_src   = html_lib.escape(src)

        # ── Full article link as attractive pill button ──
        link_html = ""
        if url and url != "#":
            safe_url = html_lib.escape(url)
            link_html = (
                f'<br><a href="{safe_url}" target="_blank" class="read-link">'
                f'📖 पूरी खबर पढ़ें →</a>'
            )

        st.markdown(
            f'<div class="news-item {css}">'
            f'<div class="ntitle">{lbl} &nbsp; {safe_title}</div>'
            f'<div class="nmeta">📅 {dt} &nbsp;|&nbsp; 📰 {safe_src}</div>'
            f'<div class="ndesc">{safe_desc}{link_html}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

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

# ── TAB 5: AI POST GENERATOR (improved) ──
with tab5:
    st.markdown("#### 🤖 AI Social Media Post Generator")
    st.caption("Platform के हिसाब से emoji-rich, ready-to-paste Hindi posts बनाएँ।")

    col_a, col_b = st.columns([2, 1])
    with col_a:
        topic = st.text_area(
            "📝 Topic ya headline daalein",
            placeholder="Example: Lucknow mein OTP fraud gang 12 arrested...",
            height=90,
        )
    with col_b:
        platform = st.selectbox(
            "📱 Platform",
            ["Twitter/X", "Facebook", "Instagram", "WhatsApp"],
            help="Platform ke hisaab se post format alag hoga"
        )
        tone = st.selectbox(
            "🎯 Tone",
            ["Urgent Warning", "Informative", "Motivational", "Helpful Tips"]
        )

    # Platform preview info
    plat_info = {
        "Twitter/X":   "280 chars • Short & punchy • 2-3 hashtags",
        "Facebook":    "300-500 chars • Friendly paragraphs • Community feel",
        "Instagram":   "Caption + hashtag block • Visual-first • 10+ hashtags",
        "WhatsApp":    "Forward-friendly • 200-350 chars • Personal tone",
    }
    st.info(f"📋 **{platform}** format: {plat_info[platform]}")

    if st.button("⚡ Post Generate karein", key="gen_post_main"):
        if not topic.strip():
            st.warning("Topic daalein.")
        elif not groq_key:
            st.error("Sidebar mein Groq API key daalein.")
        else:
            with st.spinner(f"AI {platform} post likh raha hai..."):
                result = groq_post(groq_key, topic, platform, tone)
            st.session_state["ai_results"]["gen_post"] = result
            st.session_state["ai_results"]["gen_platform"] = platform

    if "gen_post" in st.session_state["ai_results"]:
        res      = st.session_state["ai_results"]["gen_post"]
        plat_out = st.session_state["ai_results"].get("gen_platform", platform)
        char_count = len(res)

        st.markdown(
            f'<div class="post-card">'
            f'<div class="platform-badge">✨ {html_lib.escape(plat_out.upper())} POST — READY TO PASTE</div>'
            f'<div class="post-text">{html_lib.escape(res)}</div>'
            f'<div class="char-count">{char_count} characters</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Copy-friendly code block
        st.code(res, language=None)
        st.caption("⬆️ Upar se copy karein aur directly paste karein!")

    st.markdown("---")
    st.markdown("#### 🔁 Quick Post from Latest News")
    st.caption("Kisi bhi khabar ka 1-click post banayein")

    for i, art in enumerate(filtered[:4]):
        c1, c2 = st.columns([5, 1])
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

with tab6:
    st.markdown("#### 🛡️ Cyber Safety Tips — उत्तर प्रदेश")
    st.error("🆘 Cyber Fraud hua? **1930** par call karein | **cybercrime.gov.in** par report karein")
    st.markdown("---")
    for icon, title_tip, desc_tip in TIPS:
        st.markdown(
            f'<div class="tip-card">'
            f'<div style="font-size:1.8rem;">{icon}</div>'
            f'<div style="color:#00e5ff;font-weight:700;font-size:1rem;margin:0.3rem 0;">'
            f'{html_lib.escape(title_tip)}</div>'
            f'<div style="color:#a0b8d0;font-family:\'Noto Sans Devanagari\',sans-serif;'
            f'font-size:0.88rem;line-height:1.7;">{html_lib.escape(desc_tip)}</div>'
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

