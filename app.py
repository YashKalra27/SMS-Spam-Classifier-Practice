import streamlit as st
import pickle
import string
import nltk

@st.cache_resource
def download_nltk_dependencies():
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    nltk.download('stopwords', quiet=True)

download_nltk_dependencies()

from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

# ==================== Page Config ==================== #
st.set_page_config(page_title="Neural Threat Detection | Spam Guard", page_icon="🛡️", layout="centered")

ps = PorterStemmer()

@st.cache_data
def transform_text(text):
    text = text.lower()
    text = nltk.word_tokenize(text)

    y = []
    for i in text:
        if i.isalnum():
            y.append(i)

    text = y[:]
    y.clear()

    for i in text:
        if i not in stopwords.words('english') and i not in string.punctuation:
            y.append(i)

    text = y[:]
    y.clear()

    for i in text:
        y.append(ps.stem(i))

    return " ".join(y)

# ==================== Load Assets ==================== #
@st.cache_resource
def load_models():
    tfidf = pickle.load(open('vectorizer.pkl','rb'))
    model = pickle.load(open('model.pkl','rb'))
    return tfidf, model

tfidf, model = load_models()

# ==================== UI CSS Styling ==================== #
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* App background */
    .stApp {
        background: #0b0e14;
        color: #e2e8f0;
        overflow-x: hidden;
    }

    /* Ambient Animated Orbs */
    .blob1 {
        position: fixed;
        top: -10%; left: -10%;
        width: 50vw; height: 50vw;
        background: radial-gradient(circle, rgba(0,242,254,0.15) 0%, transparent 70%);
        border-radius: 50%;
        z-index: -10;
        pointer-events: none;
        animation: float1 20s infinite ease-in-out alternate;
    }
    .blob2 {
        position: fixed;
        bottom: -15%; right: -10%;
        width: 60vw; height: 60vw;
        background: radial-gradient(circle, rgba(239,68,68,0.08) 0%, transparent 60%);
        border-radius: 50%;
        z-index: -10;
        pointer-events: none;
        animation: float2 25s infinite ease-in-out alternate;
    }
    
    @keyframes float1 { 0% { transform: translate(0,0) scale(1); } 100% { transform: translate(10%, 15%) scale(1.1); } }
    @keyframes float2 { 0% { transform: translate(0,0) scale(1); } 100% { transform: translate(-10%, -10%) scale(1.05); } }

    /* Hide standard top padding */
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 2rem !important;
        z-index: 5;
    }

    /* Custom Title */
    .cyber-title {
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
        letter-spacing: -1.5px;
        transition: text-shadow 0.3s ease;
    }
    .cyber-title:hover {
        text-shadow: 0 0 20px rgba(0, 242, 254, 0.4);
    }
    
    .hud-container {
        display: flex;
        justify-content: center;
        gap: 15px;
        margin-bottom: 40px;
        margin-top: -5px;
    }
    .hud-badge {
        font-family: monospace;
        font-size: 0.85rem;
        padding: 4px 12px;
        border-radius: 20px;
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(148, 163, 184, 0.3);
        color: #94a3b8;
        letter-spacing: 1px;
    }
    .hud-badge.active {
        color: #00f2fe;
        border-color: rgba(0, 242, 254, 0.5);
        box-shadow: 0 0 10px rgba(0, 242, 254, 0.2);
    }
    
    /* Text Area Styling */
    .stTextArea>div>div>textarea {
        background-color: rgba(15, 23, 42, 0.7) !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        color: #f8fafc !important;
        border-radius: 12px;
        font-size: 1.1rem;
        padding: 1.2rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4) inset;
        backdrop-filter: blur(5px);
    }
    
    .stTextArea>div>div>textarea:focus {
        border-color: #00f2fe !important;
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.2) inset !important;
    }

    .stTextArea label { display: none !important; }
    
    /* Custom Button */
    .stButton>button {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        color: #0f172a;
        font-weight: 800;
        font-size: 1.1rem;
        border: none;
        border-radius: 8px;
        padding: 0.8rem 2rem;
        width: 100%;
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 242, 254, 0.6);
        color: #ffffff;
    }
    
    /* Result Cards */
    .result-card-safe, .result-card-spam {
        border-radius: 12px;
        padding: 2.5rem;
        text-align: center;
        margin-top: 1rem;
        backdrop-filter: blur(10px);
        animation: slideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    .result-card-safe {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.2) 100%);
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-left: 6px solid #10b981;
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.15);
    }
    
    .result-card-spam {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.2) 100%);
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-left: 6px solid #ef4444;
        box-shadow: 0 10px 25px rgba(239, 68, 68, 0.2);
    }
    
    .result-title-safe { color: #34d399; font-size: 2.4rem; font-weight: 800; margin-bottom: 0.5rem; }
    .result-title-spam { color: #f87171; font-size: 2.4rem; font-weight: 800; margin-bottom: 0.5rem; }
    
    .result-desc { color: #cbd5e1; font-size: 1.15rem; font-weight: 300; margin: 0; }
    
    /* Probability Bar */
    .prob-wrap { margin-top: 25px; text-align: left; }
    .prob-title { font-family: monospace; font-size: 0.9rem; color: #94a3b8; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px;}
    .prob-container {
        width: 100%; height: 10px; background-color: rgba(255,255,255,0.05); border-radius: 10px; overflow: hidden;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .prob-bar-spam { height: 100%; background: linear-gradient(90deg, #f87171, #ef4444); border-radius: 10px; box-shadow: 0 0 10px rgba(239, 68, 68, 0.6); }
    .prob-bar-safe { height: 100%; background: linear-gradient(90deg, #34d399, #10b981); border-radius: 10px; box-shadow: 0 0 10px rgba(16, 185, 129, 0.6); }
    
    .prob-text { font-family: monospace; font-weight: 700; font-size: 1.1rem; float: right; margin-top: -22px;}
    .prob-text.danger { color: #f87171; }
    .prob-text.safe { color: #34d399; }

    /* Decorative Separator */
    .separator { height: 1px; background: linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.2), transparent); margin: 2.5rem 0; }
    
    /* Footer */
    .footer { position: fixed; bottom: 10px; left: 0; right: 0; text-align: center; color: #475569; font-size: 0.85rem; font-weight: 300; letter-spacing: 1px; z-index: 10;}
    
    @keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
st.markdown("<div class='blob1'></div><div class='blob2'></div>", unsafe_allow_html=True)

# ==================== Core Application Structure ==================== #

st.markdown('<h1 class="cyber-title">Neural Threat Detection</h1>', unsafe_allow_html=True)
st.markdown("""
<div class="hud-container">
    <span class="hud-badge active">SYS: ONLINE</span>
    <span class="hud-badge">MDL: NaiveBayes_v2</span>
    <span class="hud-badge">DB: 5572+ SIGS</span>
</div>
""", unsafe_allow_html=True)

input_sms = st.text_area("Hidden_Label", height=180, placeholder="Paste email, SMS, or suspicious text blob here...")

# Centering the submit button visually
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    submit_btn = st.button('INITIATE DEEP SCAN', use_container_width=True)

if submit_btn:
    if not input_sms.strip():
        st.warning("Please explicitly enter raw text to analyze.")
    else:
        with st.spinner("Analyzing linguistic patterns and structural payloads..."):
            
            transformed_sms = transform_text(input_sms)
            vector_input = tfidf.transform([transformed_sms])
            
            # Predict Logic with Probabilities
            result = model.predict(vector_input)[0]
            probabilities = model.predict_proba(vector_input)[0]
            
            # Extract probability (0 is Safe, 1 is Spam)
            spam_prob = round(probabilities[1] * 100, 1)
            safe_prob = round(probabilities[0] * 100, 1)
            
            st.markdown("<div class='separator'></div>", unsafe_allow_html=True)
            
            if result == 1:
                # Fill percentage bar based on confidence
                prog_width = f"width: {spam_prob}%;"
                st.markdown(f"""
                <div class="result-card-spam">
                    <div class="result-title-spam">🚨 THREAT DETECTED</div>
                    <p class="result-desc">Our neural engine has categorized this signature strictly as <b>Malicious Spam</b>.</p>
                    <div class="prob-wrap">
                        <div class="prob-title">Threat Signature Match Confidence</div>
                        <div class="prob-text danger">{spam_prob}%</div>
                        <div class="prob-container"><div class="prob-bar-spam" style="{prog_width}"></div></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                prog_width = f"width: {safe_prob}%;"
                st.markdown(f"""
                <div class="result-card-safe">
                    <div class="result-title-safe">✅ SAFE ORIGIN</div>
                    <p class="result-desc">No manipulative or suspicious semantic signatures were detected.</p>
                    <div class="prob-wrap">
                        <div class="prob-title">Origin Safety Confidence Metric</div>
                        <div class="prob-text safe">{safe_prob}%</div>
                        <div class="prob-container"><div class="prob-bar-safe" style="{prog_width}"></div></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# Footer overlay
st.markdown("<div class='footer'>Developed by Komal Mittal</div>", unsafe_allow_html=True)
