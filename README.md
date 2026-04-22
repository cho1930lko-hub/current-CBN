# 🛡️ UP Cyber Shield Dashboard

> **उत्तर प्रदेश साइबर अपराध जागरूकता डैशबोर्ड**  
> A real-time Cyber Crime Awareness Dashboard for Uttar Pradesh — built with Streamlit + Groq AI (Free APIs only)

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Free APIs](https://img.shields.io/badge/APIs-100%25%20Free-brightgreen?style=flat-square)

---

## 🚀 Features

| Feature | Description |
|---|---|
| 📰 **Live News Feed** | UP cyber crime news via NewsAPI (free tier) |
| 🤖 **AI Hindi Summary** | Groq LLaMA3 se Hindi mein summary |
| ⚡ **Post Generator** | Twitter/Facebook awareness posts auto-generate |
| 🗂️ **Smart Tabs** | Fraud Cases / Police Action / Awareness separated |
| 📍 **District Filter** | All 18+ UP districts filter |
| 🎨 **Dark Cyber UI** | Beautiful cyber-themed dark dashboard |
| 📊 **Stats Cards** | Live metrics (arrests, recovered amount, campaigns) |

---

## 🔑 Free API Keys Setup

### 1. NewsAPI (Free — 100 requests/day)
1. Go to [newsapi.org](https://newsapi.org/register)
2. Sign up for free account
3. Copy your API key

### 2. Groq API (Free — very generous limits)
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up → API Keys → Create Key
3. Copy your `gsk_xxxx` key

---

## 📦 Installation & Run

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/up-cyber-shield.git
cd up-cyber-shield

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the dashboard
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

---

## 🌐 Deploy on Streamlit Cloud (Free)

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set `app.py` as main file
5. Add API keys in **Secrets** section:
```toml
NEWS_API_KEY = "your_key_here"
GROQ_API_KEY = "gsk_your_key_here"
```
6. Click Deploy! ✅

---

## 📁 Project Structure

```
up-cyber-shield/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## 🎨 Dashboard Tabs

| Tab | Content |
|---|---|
| 📰 Latest News | All cyber crime news (filtered) |
| 🔴 Fraud Cases | Negative incidents — scams, frauds |
| 🟢 Police Action | Arrests, recoveries, crackdowns |
| 📢 Awareness | Campaigns, workshops, drives |
| 🤖 AI Post Generator | Auto-generate social media posts |
| ℹ️ Cyber Tips | Safety tips in Hindi |

---

## 🆘 Cyber Crime Helpline

```
📞 1930       ← National Cyber Crime Helpline
🌐 cybercrime.gov.in
```

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit + Custom CSS (Dark Cyber Theme)
- **AI**: Groq API (LLaMA 3 8B) — Free
- **News**: NewsAPI — Free
- **Language**: Python 3.9+

---

## 📄 License
MIT License — Free to use and modify.

---

*Made with ❤️ for Digital Safety in Uttar Pradesh*
