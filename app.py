import streamlit as st
from openai import OpenAI
import time

# --- КОНФИГ ---
st.set_page_config(page_title="EcoRouter AI — Intelligent Gateway", page_icon="⚡", layout="wide")

# --- API KEYS ---
# Для продакшена используйте st.secrets["GROQ_API_KEY"] и st.secrets["GEMINI_API_KEY"]
# Локально можно использовать прямые ключи для разработки
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    # Fallback для локальной разработки
    GROQ_API_KEY = "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"
    GEMINI_API_KEY = "AIzaSyAoFLkwdsGciiBq6y_ae3oOQtiNwc1QT7U"

# --- CUSTOM CSS (Green emerald theme) ---
st.markdown("""
<style>
    .stApp { background-color: #0a0a10; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0e0e16 0%, #0a0a10 100%); border-right: 1px solid rgba(255,255,255,0.07); }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p { color: #ebebec !important; }
    
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(255,255,255,0.03) 0%, rgba(16,185,129,0.02) 100%);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 16px;
        padding: 22px 26px;
        transition: all 0.3s ease;
    }
    [data-testid="stMetric"]:hover {
        border-color: rgba(16,185,129,0.25);
        box-shadow: 0 4px 24px rgba(16,185,129,0.08);
        transform: translateY(-1px);
    }
    [data-testid="stMetricValue"] { color: #10b981 !important; font-weight: 800 !important; font-size: 28px !important; }
    [data-testid="stMetricLabel"] { color: #9494a8 !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.06em; }
    [data-testid="stMetricDelta"] > div { font-weight: 600 !important; }
    
    .eco-header {
        background: linear-gradient(135deg, rgba(16,185,129,0.08) 0%, rgba(10,10,16,0.98) 60%);
        border: 1px solid rgba(16,185,129,0.15);
        border-radius: 20px;
        padding: 40px 44px;
        margin-bottom: 32px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(16,185,129,0.06);
    }
    .eco-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(16,185,129,0.08) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }
    .eco-header h1 { color: #f0f0f2; font-size: 34px; font-weight: 800; margin: 0 0 10px 0; letter-spacing: -0.03em; }
    .eco-header p { color: #9494a8; font-size: 15px; margin: 0; line-height: 1.7; max-width: 620px; }
    .eco-badge {
        display: inline-block; padding: 6px 16px; background: rgba(16,185,129,0.12);
        border: 1px solid rgba(16,185,129,0.25); border-radius: 8px;
        font-size: 11px; font-weight: 700; color: #10b981; text-transform: uppercase;
        letter-spacing: 0.08em; margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(16,185,129,0.1);
    }
    .eco-link {
        display: inline-flex; align-items: center; gap: 6px;
        margin-top: 14px; padding: 8px 18px;
        background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.2);
        border-radius: 10px; color: #10b981; font-size: 13px; font-weight: 600;
        text-decoration: none; transition: all 0.2s;
    }
    .eco-link:hover { background: rgba(16,185,129,0.2); color: #34d399; }

    .eco-welcome {
        text-align: center;
        padding: 60px 32px;
        color: #4e4e62;
    }
    .eco-welcome h3 { color: #8c8ca0; font-size: 20px; font-weight: 600; margin-bottom: 12px; }
    .eco-welcome p { font-size: 14px; line-height: 1.7; max-width: 480px; margin: 0 auto 24px; }
    .eco-welcome .hint {
        display: inline-block; padding: 8px 16px;
        background: rgba(16,185,129,0.06); border: 1px solid rgba(16,185,129,0.12);
        border-radius: 8px; font-size: 13px; color: #8c8ca0;
    }
    .eco-welcome .hint code { color: #10b981; font-weight: 600; }
    
    .route-pill {
        display: inline-flex; align-items: center; gap: 8px;
        padding: 10px 18px; border-radius: 12px; font-size: 13px; font-weight: 600;
        margin-bottom: 10px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.15);
    }
    .route-pill.easy { background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.2); color: #10b981; }
    .route-pill.hard { background: rgba(251,191,36,0.1); border: 1px solid rgba(251,191,36,0.2); color: #fbbf24; }
    .route-pill.manual { background: rgba(96,165,250,0.1); border: 1px solid rgba(96,165,250,0.2); color: #60a5fa; }
    .route-pill .dot { width: 8px; height: 8px; border-radius: 50%; }
    .route-pill.easy .dot { background: #10b981; box-shadow: 0 0 8px rgba(16,185,129,0.4); }
    .route-pill.hard .dot { background: #fbbf24; box-shadow: 0 0 8px rgba(251,191,36,0.4); }
    .route-pill.manual .dot { background: #60a5fa; box-shadow: 0 0 8px rgba(96,165,250,0.4); }
    
    [data-testid="stChatMessage"] {
        background: linear-gradient(135deg, rgba(255,255,255,0.02) 0%, rgba(16,185,129,0.01) 100%) !important;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 18px !important;
        transition: all 0.2s ease;
    }
    [data-testid="stChatMessage"]:hover {
        border-color: rgba(255,255,255,0.1);
    }
    
    hr { border-color: rgba(255,255,255,0.05) !important; }
    header[data-testid="stHeader"] { background: rgba(8,8,12,0.95) !important; backdrop-filter: blur(12px); }
    
    .sidebar-footer { color: #4e4e62; font-size: 11px; text-align: center; padding: 16px 0; border-top: 1px solid rgba(255,255,255,0.05); margin-top: 8px; }
    .sidebar-footer span { color: #10b981; font-weight: 600; }

    /* Section card */
    .sidebar-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.03) 0%, rgba(16,185,129,0.02) 100%);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 14px;
        padding: 18px 16px;
        margin: 8px 0 16px 0;
        transition: all 0.3s ease;
    }
    .sidebar-card:hover {
        border-color: rgba(16,185,129,0.15);
        box-shadow: 0 4px 20px rgba(16,185,129,0.05);
    }
    .sidebar-card-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        font-weight: 700;
        color: #ebebec;
        margin-bottom: 14px;
        letter-spacing: 0.02em;
    }
    .sidebar-card-title .icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        border-radius: 8px;
        font-size: 14px;
    }
    .sidebar-card-title .icon.green { background: rgba(16,185,129,0.12); }
    .sidebar-card-title .icon.blue { background: rgba(96,165,250,0.12); }
    .sidebar-card-title .icon.purple { background: rgba(139,92,246,0.12); }

    /* Budget bar */
    .budget-bar { 
        background: rgba(255,255,255,0.04); border-radius: 8px; height: 10px; 
        margin: 10px 0; overflow: hidden;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.2);
    }
    .budget-fill { 
        height: 100%; border-radius: 8px; transition: width 0.5s ease;
        box-shadow: 0 0 8px rgba(16,185,129,0.3);
    }
    .budget-fill.safe { background: linear-gradient(90deg, #10b981, #34d399); }
    .budget-fill.warn { background: linear-gradient(90deg, #fbbf24, #f59e0b); box-shadow: 0 0 8px rgba(251,191,36,0.3); }
    .budget-fill.danger { background: linear-gradient(90deg, #f87171, #ef4444); box-shadow: 0 0 8px rgba(248,113,113,0.3); }
    .budget-stats {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: #8888a8;
        margin-top: 4px;
    }
    .budget-stats strong { font-weight: 700; }
    .budget-pct {
        text-align: center;
        font-size: 22px;
        font-weight: 800;
        margin: 8px 0 4px 0;
        letter-spacing: -0.03em;
    }
    .budget-pct.safe { color: #10b981; }
    .budget-pct.warn { color: #fbbf24; }
    .budget-pct.danger { color: #f87171; }
    .budget-pct-label {
        text-align: center;
        font-size: 10px;
        color: #4e4e62;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 10px;
    }

    /* Power indicator */
    .power-info {
        background: rgba(255,255,255,0.025);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 14px 16px;
        margin: 8px 0;
        font-size: 12px;
        color: #8c8ca0;
        transition: all 0.3s ease;
    }
    .power-info:hover {
        border-color: rgba(255,255,255,0.1);
    }
    .power-info strong { color: #ebebec; }
    .power-info .accent { color: #10b981; font-weight: 700; }
    .power-mode-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .power-mode-badge .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        animation: pulse-dot 2s infinite;
    }
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }
    .power-mode-badge.eco { background: rgba(6,182,212,0.1); border: 1px solid rgba(6,182,212,0.2); color: #06b6d4; }
    .power-mode-badge.eco .dot { background: #06b6d4; box-shadow: 0 0 6px rgba(6,182,212,0.5); }
    .power-mode-badge.balance { background: rgba(139,92,246,0.1); border: 1px solid rgba(139,92,246,0.2); color: #8b5cf6; }
    .power-mode-badge.balance .dot { background: #8b5cf6; box-shadow: 0 0 6px rgba(139,92,246,0.5); }
    .power-mode-badge.max { background: rgba(244,63,94,0.1); border: 1px solid rgba(244,63,94,0.2); color: #f43f5e; }
    .power-mode-badge.max .dot { background: #f43f5e; box-shadow: 0 0 6px rgba(244,63,94,0.5); }
    .power-model-info {
        font-size: 11px;
        color: #6b6b80;
        margin-top: 6px;
        padding-top: 8px;
        border-top: 1px solid rgba(255,255,255,0.04);
        line-height: 1.6;
    }
    .power-model-info code {
        background: rgba(255,255,255,0.05);
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 10px;
        color: #9494a8;
    }

    /* Custom input styling */
    [data-testid="stNumberInput"] input {
        background: rgba(16,185,129,0.05) !important;
        border-color: rgba(16,185,129,0.15) !important;
        color: #ebebec !important;
    }
    [data-testid="stNumberInput"] input:focus {
        border-color: rgba(16,185,129,0.4) !important;
        box-shadow: 0 0 12px rgba(16,185,129,0.1) !important;
    }

    /* Buttons */
    .stButton > button {
        border-color: rgba(16,185,129,0.2) !important;
        color: #ebebec !important;
    }
    .stButton > button:hover {
        border-color: rgba(16,185,129,0.4) !important;
        background: rgba(16,185,129,0.1) !important;
    }

    /* Slider accent */
    [data-testid="stSlider"] [role="slider"] {
        background-color: #10b981 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "total_savings" not in st.session_state:
    st.session_state.total_savings = 0.0
if "total_requests" not in st.session_state:
    st.session_state.total_requests = 0
if "total_routing_time" not in st.session_state:
    st.session_state.total_routing_time = 0.0
if "total_spent" not in st.session_state:
    st.session_state.total_spent = 0.0

# --- КЛИЕНТЫ (Мульти-вендорность) ---
# Check if user provided custom keys
if "custom_groq_key" not in st.session_state:
    st.session_state.custom_groq_key = ""
if "custom_gemini_key" not in st.session_state:
    st.session_state.custom_gemini_key = ""

def get_clients():
    gk = st.session_state.custom_groq_key or GROQ_API_KEY
    gmk = st.session_state.custom_gemini_key or GEMINI_API_KEY
    gc = OpenAI(api_key=gk, base_url="https://api.groq.com/openai/v1")
    gmc = OpenAI(api_key=gmk, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
    return gc, gmc

groq_client, gemini_client = get_clients()

# --- САЙДБАР ---
with st.sidebar:
    st.markdown("### ⚙ Настройки шлюза")
    
    # --- BUDGET CARD ---
    st.markdown("""
    <div class="sidebar-card">
        <div class="sidebar-card-title">
            <div class="icon green">💰</div>
            Лимит бюджета
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    budget_col1, budget_col2 = st.columns([2, 1])
    with budget_col1:
        budget_slider = st.slider(
            "Слайдер",
            min_value=10, max_value=10000, value=500, step=10,
            format="$%d",
            label_visibility="collapsed"
        )
    with budget_col2:
        budget_input = st.number_input(
            "Точная сумма ($)",
            min_value=1, max_value=100000, value=budget_slider, step=1,
            label_visibility="collapsed"
        )
    budget_limit = budget_input if budget_input != budget_slider else budget_slider
    
    # Budget progress
    spent = st.session_state.total_spent
    pct = min(100, (spent / budget_limit) * 100) if budget_limit > 0 else 0
    bar_class = "safe" if pct < 70 else ("warn" if pct < 90 else "danger")
    remaining = max(0, budget_limit - spent)
    
    st.markdown(f"""
    <div class="budget-pct {bar_class}">{pct:.0f}%</div>
    <div class="budget-pct-label">использовано</div>
    <div class="budget-bar"><div class="budget-fill {bar_class}" style="width:{pct:.1f}%;"></div></div>
    <div class="budget-stats">
        <span>Потрачено: <strong style="color:#e2e2f0;">${spent:.2f}</strong></span>
        <span>Осталось: <strong style="color:#10b981;">${remaining:,.2f}</strong></span>
    </div>
    <div class="budget-stats" style="margin-top:6px;">
        <span>Лимит: <strong style="color:#9494a8;">${budget_limit:,}</strong></span>
    </div>
    """, unsafe_allow_html=True)
    
    if pct >= 80:
        st.warning(f"⚠ Бюджет исчерпан на {pct:.0f}%!")
    
    st.divider()
    
    # --- POWER CARD ---
    st.markdown("""
    <div class="sidebar-card">
        <div class="sidebar-card-title">
            <div class="icon purple">⚡</div>
            Мощность / Экономия
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    power_level = st.slider(
        "Баланс мощности",
        min_value=10, max_value=100, value=50, step=10,
        help="10% = только бесплатные модели, 100% = максимальное качество",
        label_visibility="collapsed"
    )
    
    if power_level <= 30:
        power_mode = "Экономия"
        power_desc = "Groq Llama — бесплатная модель, $0"
        power_color = "#06b6d4"
        power_badge = "eco"
        power_icon = "🌿"
        power_models = "Все запросы → <code>llama-3.1-8b-instant</code> (Groq, бесплатно)"
    elif power_level <= 70:
        power_mode = "Баланс"
        power_desc = "Умная маршрутизация: простые → Llama, сложные → Gemini"
        power_color = "#8b5cf6"
        power_badge = "balance"
        power_icon = "⚖️"
        power_models = "EASY → <code>llama-3.1-8b</code> · HARD → <code>gemini-1.5-flash</code>"
    else:
        power_mode = "Макс. мощность"
        power_desc = "Максимальное качество через Google Gemini"
        power_color = "#f43f5e"
        power_badge = "max"
        power_icon = "🚀"
        power_models = "Все запросы → <code>gemini-1.5-flash</code> (Google)"
    
    st.markdown(f"""
    <div class="power-info">
        <div class="power-mode-badge {power_badge}">
            <span class="dot"></span>
            {power_icon} {power_mode} · {power_level}%
        </div>
        <div style="font-size:12px; color:#9494a8; margin-top:4px;">{power_desc}</div>
        <div class="power-model-info">
            {power_models}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.markdown("##### Маршрутизация")
    
    routing_mode = st.radio("Режим:", 
                            ["Auto (LLM-Judge)", "Ручной выбор модели"],
                            index=0, label_visibility="collapsed")
    
    manual_model = None
    if routing_mode == "Ручной выбор модели":
        manual_model = st.selectbox("Модель:", [
            "gemini-1.5-flash", "llama-3.1-8b-instant", 
            "llama-3.3-70b-versatile", "gemma2-9b-it"
        ])
    
    judge_model = st.selectbox("Модель-судья:", [
        "llama-3.1-8b-instant", "llama-3.3-70b-versatile", 
        "mixtral-8x7b-32768", "gemma2-9b-it"
    ])
    
    st.divider()
    st.markdown("##### Свои API-ключи")
    st.caption("Подключите свои ключи для работы через ваш аккаунт")
    custom_groq = st.text_input("Groq API Key", type="password", value=st.session_state.custom_groq_key, placeholder="gsk_...")
    custom_gemini = st.text_input("Gemini API Key", type="password", value=st.session_state.custom_gemini_key, placeholder="AIza...")
    if custom_groq != st.session_state.custom_groq_key or custom_gemini != st.session_state.custom_gemini_key:
        st.session_state.custom_groq_key = custom_groq
        st.session_state.custom_gemini_key = custom_gemini
        st.rerun()
    
    st.divider()
    if st.button("Очистить чат", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_savings = 0.0
        st.session_state.total_requests = 0
        st.session_state.total_routing_time = 0.0
        st.session_state.total_spent = 0.0
        st.rerun()
    
    st.markdown(
        '<div class="sidebar-footer">EcoRouter AI <span>v3.0</span><br>Multi-Vendor Gateway<br>Groq · Gemini · Meta Llama</div>',
        unsafe_allow_html=True
    )

# --- HEADER ---
st.markdown("""
<div class="eco-header">
    <div class="eco-badge">Live Demo — Multi-Vendor LLM Gateway</div>
    <h1>EcoRouter AI</h1>
    <p>Мульти-вендорный шлюз: Meta Llama (Groq) + Google Gemini. Система маршрутизирует каждый запрос в оптимальную модель за 0.1 секунды.</p>
    <a href="https://ecorouter-ai.pages.dev" target="_blank" class="eco-link">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
        Открыть сайт EcoRouter
    </a>
</div>
""", unsafe_allow_html=True)

# --- LIVE METRICS ---
if st.session_state.total_requests > 0:
    col1, col2, col3, col4, col5 = st.columns(5)
    avg_routing = round(st.session_state.total_routing_time / max(1, st.session_state.total_requests), 2)
    with col1:
        st.metric("Сэкономлено", f"${st.session_state.total_savings:.2f}", 
                  delta="vs Direct API")
    with col2:
        st.metric("Потрачено", f"${st.session_state.total_spent:.2f}",
                  delta=f"из ${budget_limit:,}")
    with col3:
        st.metric("Запросов", st.session_state.total_requests)
    with col4:
        st.metric("Роутинг", f"{avg_routing}s",
                  delta="Fast" if avg_routing < 0.5 else None, delta_color="normal")
    with col5:
        co2 = round(st.session_state.total_savings * 0.042, 2)
        st.metric("CO₂", f"{co2}g",
                  delta="ESG+" if co2 > 0 else None, delta_color="normal")
    st.divider()

# --- WELCOME STATE ---
if not st.session_state.messages:
    st.markdown("""
    <div class="eco-welcome">
        <h3>Начните диалог с мульти-вендорным шлюзом</h3>
        <p>Система оценивает сложность запроса и направляет его в оптимальную модель. Meta Llama для рутины, Google Gemini для сложных задач.</p>
        <div class="hint">Попробуйте: <code>Привет!</code> → Groq/Llama · <code>Напиши бизнес-план</code> → Gemini</div>
    </div>
    """, unsafe_allow_html=True)

# --- CHAT HISTORY ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- ЛОГИКА ---
user_input = st.chat_input("Введите промпт...")

if user_input:
    # === BUDGET CAP CHECK ===
    budget_exceeded = st.session_state.total_spent >= budget_limit
    
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Determine routing
    cost_saved = 0
    cost_actual = 0
    routing_time = 0
    
    if routing_mode == "Ручной выбор модели":
        target_model = manual_model
        if "gemini" in target_model:
            active_client = gemini_client
        else:
            active_client = groq_client
        st.markdown(f'<div class="route-pill manual"><div class="dot"></div>Ручной → <code>{target_model}</code></div>', unsafe_allow_html=True)
    else:
        # === BUDGET KILL-SWITCH ===
        if budget_exceeded:
            target_model = "llama-3.1-8b-instant"
            active_client = groq_client
            routing_time = 0
            cost_saved = 0.032
            cost_actual = 0.0
            st.markdown(
                f'<div class="route-pill hard" style="background:rgba(248,113,113,0.1);border-color:rgba(248,113,113,0.2);color:#f87171;">'
                f'<div class="dot" style="background:#f87171;box-shadow:0 0 8px rgba(248,113,113,0.4);"></div>'
                f'🛡️ Budget Cap достигнут (${budget_limit}). Все запросы → бесплатная модель <code>{target_model}</code></div>',
                unsafe_allow_html=True
            )
        else:
            # === POWER LEVEL OVERRIDE ===
            if power_level <= 30:
                # Economy mode — skip judge, always free model
                target_model = "llama-3.1-8b-instant"
                active_client = groq_client
                routing_time = 0
                cost_saved = 0.032
                cost_actual = 0.0
                st.markdown(
                    f'<div class="route-pill easy"><div class="dot"></div>'
                    f'💚 Режим экономии → <code>{target_model}</code> (Meta/Groq) · $0.00 · Мгновенно</div>',
                    unsafe_allow_html=True
                )
            elif power_level > 70:
                # Max power — always Gemini
                target_model = "gemini-1.5-flash"
                active_client = gemini_client
                routing_time = 0
                cost_saved = 0.005
                cost_actual = 0.003
                st.markdown(
                    f'<div class="route-pill hard"><div class="dot"></div>'
                    f'🧠 Максимальная мощность → <code>{target_model}</code> (Google) · Качество max</div>',
                    unsafe_allow_html=True
                )
            else:
                # === BALANCED: LLM-Judge routing ===
                with st.spinner("Анализ когнитивной нагрузки..."):
                    judge_prompt = f"""Ты - умный маршрутизатор. Оцени сложность задачи. 
Если это простой вопрос, приветствие, базовый перевод, короткий факт или легкая математика, ответь ровно одним словом: EASY
Если это сложный код, архитектура, бизнес-план, длинная генерация текста или сложная логика, ответь ровно одним словом: HARD
Запрос пользователя: {user_input}"""
                    
                    try:
                        start_time = time.time()
                        judge_response = groq_client.chat.completions.create(
                            model=judge_model,
                            messages=[{"role": "user", "content": judge_prompt}],
                            temperature=0
                        )
                        decision = judge_response.choices[0].message.content.strip().upper()
                        routing_time = round(time.time() - start_time, 2)
                    except Exception as e:
                        decision = "HARD"
                        routing_time = 0

                if "EASY" in decision:
                    target_model = "llama-3.1-8b-instant"
                    active_client = groq_client
                    cost_saved = 0.028
                    cost_actual = 0.0
                    st.markdown(
                        f'<div class="route-pill easy"><div class="dot"></div>'
                        f'⚡ EASY → <code>{target_model}</code> (Meta/Groq) · Экономия ~96% · {routing_time}s</div>',
                        unsafe_allow_html=True
                    )
                else:
                    target_model = "gemini-1.5-flash"
                    active_client = gemini_client
                    cost_saved = 0.012
                    cost_actual = 0.003
                    st.markdown(
                        f'<div class="route-pill hard"><div class="dot"></div>'
                        f'🧠 HARD → <code>{target_model}</code> (Google Gemini) · Качество max · {routing_time}s</div>',
                        unsafe_allow_html=True
                    )

    # === GENERATION WITH FALLBACK ===
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            response = active_client.chat.completions.create(
                model=target_model,
                messages=[{"role": "user", "content": user_input}],
                stream=True
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
                    
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            # === FALLBACK SYSTEM ===
            st.markdown(
                f'<div class="route-pill hard" style="background:rgba(248,113,113,0.1);border-color:rgba(248,113,113,0.2);color:#f87171;">'
                f'<div class="dot" style="background:#f87171;box-shadow:0 0 8px rgba(248,113,113,0.4);"></div>'
                f'⚠️ {target_model} недоступна. Включаю Fallback...</div>',
                unsafe_allow_html=True
            )
            
            # Try Groq fallback
            fallback_model = "llama-3.3-70b-versatile"
            try:
                fallback_response = groq_client.chat.completions.create(
                    model=fallback_model,
                    messages=[{"role": "user", "content": user_input}],
                    stream=True
                )
                
                for chunk in fallback_response:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                cost_actual = 0.0
                cost_saved = 0.029
                
                st.markdown(
                    f'<div class="route-pill easy" style="background:rgba(96,165,250,0.1);border-color:rgba(96,165,250,0.2);color:#60a5fa;">'
                    f'<div class="dot" style="background:#60a5fa;box-shadow:0 0 8px rgba(96,165,250,0.4);"></div>'
                    f'🔄 Fallback успешен → <code>{fallback_model}</code> через Groq</div>',
                    unsafe_allow_html=True
                )
                
            except Exception as fallback_e:
                st.error(f"Ошибка Fallback: {fallback_e}")
                st.stop()
        
        if full_response:
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.session_state.total_requests += 1
            st.session_state.total_savings += cost_saved
            st.session_state.total_spent += cost_actual
            st.session_state.total_routing_time += routing_time
            st.rerun()
