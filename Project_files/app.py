# app.py
import streamlit as st
st.set_page_config(page_title="AI Examination Analytics", layout="wide", initial_sidebar_state="expanded")
import pandas as pd
import joblib
import json
import plotly.express as px
import plotly.graph_objects as go
from database import validate_user, add_user, save_prediction, get_all_predictions, get_all_users, edit_user, delete_user
from student_view import show_student_dashboard
from admin_view import show_admin_dashboard

# ------------------- Utilities -------------------
def rerun_app():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

def safe_encode_series(series, encoder):
    if encoder is None: return series
    classes = list(encoder.classes_)
    mapping = {v: i for i, v in enumerate(classes)}
    return series.map(mapping).fillna(0).astype(int)

def generate_explanation(pred_prob, prediction, input_data):
    certainty = "high" if pred_prob > 0.85 or pred_prob < 0.15 else "moderate"
    status = "Pass" if prediction == 1 else "Fail"
    score_cols = ['tamil_score', 'english_score', 'maths_score', 'physics_score', 'chemistry_score', 'biology_score', 'computer_science_score']
    total_score = sum(input_data[col].values[0] for col in score_cols if col in input_data.columns)
    percentage = (total_score / 600) * 100
    msg = f"Student is predicted to **{status}** with {certainty} certainty ({pred_prob:.2f}). "
    msg += f"Overall performance: {percentage:.1f}%."
    return msg

# ------------------- Load Model -------------------
@st.cache_resource
def load_assets():
    try:
        model = joblib.load("model.pkl")
        columns = joblib.load("model_columns.pkl")
        encoders = {
            "gender": joblib.load("gender_encoder.pkl"),
            "part_time_job": joblib.load("part_time_job_encoder.pkl"),
            "extracurricular_activities": joblib.load("extracurricular_activities_encoder.pkl"),
            "career_aspiration": joblib.load("career_aspiration_encoder.pkl")
        }
        return model, columns, encoders
    except Exception as e:
        st.error(f"❌ Asset loading error: {e}")
        st.stop()

model, columns, encoders = load_assets()

# ------------------- Session State -------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None

# =====================================================
# LOGIN PAGE
# =====================================================
if not st.session_state.logged_in:

    # --- High-Level UI Design System & Animations ---
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@500;600;700;800&display=swap');
        
        /* Global Background & Transitions */
        .stApp { 
            background: radial-gradient(circle at 0% 0%, #F1F5F9 0%, #E2E8F0 100%); 
            font-family: 'Inter', sans-serif;
        }

        /* Animations */
        @keyframes reveal {
            0% { opacity: 0; transform: translateY(20px); filter: blur(10px); }
            100% { opacity: 1; transform: translateY(0); filter: blur(0); }
        }
        @keyframes fade {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }

        .animate-reveal { animation: reveal 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards; }
        .animate-fade { animation: fade 1.2s ease-in-out forwards; }

        /* Hide Streamlit components */
        header[data-testid="stHeader"], .stDeployButton, #MainMenu, footer { display: none !important; }
        
        /* Brand panel (Cinematic) */
        .brand-panel {
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
            border-radius: 28px;
            padding: 4rem 2.5rem;
            min-height: 85vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }
        .brand-panel::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: radial-gradient(circle at 50% 50%, rgba(99, 102, 241, 0.15) 0%, transparent 70%);
            pointer-events: none;
        }
        .brand-panel h1 {
            color: white; font-size: 2.2rem; font-weight: 800;
            text-align: center; line-height: 1.1; margin-bottom: 2rem;
            font-family: 'Outfit', sans-serif;
            background: #000000;
            padding: 1.5rem 2rem;
            border-radius: 16px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.3);
            z-index: 2;
        }
        .brand-panel .tagline {
            color: #94A3B8; font-size: 1.15rem; font-weight: 400;
            text-align: center; z-index: 2; margin-bottom: 3rem;
        }

        /* Abstract Shapes */
        .shape { position: absolute; border-radius: 50%; opacity: 0.15; filter: blur(40px); background: #6366F1; }
        .s1 { width: 300px; height: 300px; top: -50px; left: -50px; animation: float 10s infinite; }
        .s2 { width: 250px; height: 250px; bottom: -40px; right: -40px; background: #EC4899; animation: float 8s infinite reverse; }

        /* Glass Login Card */
        .login-card {
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.5);
            border-radius: 24px;
            padding: 3rem;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            animation: reveal 1s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
        }

        .stTextInput>div>div>input {
            border-radius: 12px !important;
            border: 1px solid #E2E8F0 !important;
            padding: 0.8rem 1.2rem !important;
            background: white !important;
            transition: all 0.3s ease !important;
        }
        .stTextInput>div>div>input:focus {
            border-color: #6366F1 !important;
            box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1) !important;
        }

        .stButton>button {
            width: 100%; border-radius: 12px; height: 3.2rem;
            background: #0F172A !important;
            color: white !important; font-weight: 600; border: none !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        .stButton>button:hover { 
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.3);
            background: #1E293B !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- Cinematic Content ---
    left, right = st.columns([1, 1], gap="large")
    with left:
        st.markdown("""
        <div class="brand-panel animate-fade">
            <div class="shape s1"></div>
            <div class="shape s2"></div>
            <h1>AI Student Analyzer</h1>
            <p class="tagline">Next-generation AI performance monitoring for modern educators and students.</p>
            <div style="display: flex; gap: 15px; justify-content: center; z-index: 2;">
                <div style="background: rgba(255,255,255,0.05); padding: 15px 25px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); text-align: center;">
                    <div style="font-size: 1.5rem;">🔥</div>
                    <div style="color: white; font-weight: 700;">88%</div>
                    <div style="color: #94A3B8; font-size: 0.7rem; text-transform: uppercase;">Pass Rate</div>
                </div>
                <div style="background: rgba(255,255,255,0.05); padding: 15px 25px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); text-align: center;">
                    <div style="font-size: 1.5rem;">🚀</div>
                    <div style="color: white; font-weight: 700;">AI</div>
                    <div style="color: #94A3B8; font-size: 0.7rem; text-transform: uppercase;">Engine</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown('<h2 style="font-family: \'Outfit\', sans-serif; font-weight: 800; font-size: 2rem; margin-bottom: 0.5rem;">Portal Access</h2>', unsafe_allow_html=True)
        st.markdown('<p style="color: #64748B; margin-bottom: 2rem;">Authenticating with secure AI protocols.</p>', unsafe_allow_html=True)
        
        mode = st.radio("Access Mode", ["Sign In", "Register"], horizontal=True, label_visibility="collapsed")
        
        if mode == "Sign In":
            username = st.text_input("Username Identifier", placeholder="ID #12345")
            password = st.text_input("Access Key", type="password", placeholder="••••••••")
            if st.button("Initialize"):
                role = validate_user(username, password)
                if role:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = role
                    rerun_app()
                else:
                    st.toast("🚨 Authentication Failed. Please check your credentials.", icon="🔒")
        else:
            new_user = st.text_input("New Identity")
            new_pass = st.text_input("Secret Key", type="password")
            role_sel = st.selectbox("Role Permission", ["student", "admin"])
            if st.button("Establish Identity"):
                add_user(new_user, new_pass, role=role_sel)
                st.success("Identity Verified. Proceed to Sign In.")
        

    st.stop()

# =====================================================
# DASHBOARD (after login)
# =====================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    h1, h2, h3, h4, h5, h6 { font-family: 'Outfit', sans-serif !important; }
    
    .stApp { background-color: #F4F7FE; }
    
    /* Sidebar Overhaul */
    section[data-testid="stSidebar"] { 
        background-color: #FFFFFF !important; 
        border-right: 1px solid #E2E8F0;
        box-shadow: 4px 0 24px rgba(0,0,0,0.02);
    }
    section[data-testid="stSidebar"] .stMarkdown h2 { color: #0F172A !important; font-weight: 800; font-family: 'Outfit', sans-serif !important; margin-bottom: 1rem; }
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] label {
        color: #475569 !important; font-weight: 500 !important;
    }
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        background: transparent; border-radius: 12px; padding: 0.5rem 1rem; transition: all 0.2s ease; margin-bottom: 0.25rem;
    }
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        background: #F8FAFC !important; transform: translateX(4px);
    }
    
    /* Metric Cards */
    .metric-card { 
        background: rgba(255, 255, 255, 0.85); 
        backdrop-filter: blur(20px);
        padding: 1.75rem; 
        border-radius: 20px; 
        box-shadow: 0px 4px 24px rgba(112, 144, 176, 0.08); 
        border: 1px solid rgba(255,255,255,0.8); 
        margin-bottom: 1rem; 
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover { transform: translateY(-5px); box-shadow: 0px 10px 30px rgba(112, 144, 176, 0.15); }
    .metric-label { font-size: 0.9rem; color: #64748B; font-weight: 600; text-transform: uppercase; margin-bottom: 0.75rem; font-family: 'Inter', sans-serif;}
    .metric-value { font-size: 2.2rem; font-weight: 800; color: #0F172A; font-family: 'Outfit', sans-serif; letter-spacing: -0.5px;}

    /* Modern Buttons */
    .stButton>button { 
        width: 100%; border-radius: 14px; height: 3.2rem; 
        background: linear-gradient(135deg, #4F46E5, #6366F1); 
        color: white; font-weight: 600; border: none !important;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3); transition: all 0.3s ease;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(79, 70, 229, 0.4); }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.markdown("## 📊 AI Analytics")
st.sidebar.markdown("---")
display_role = st.session_state.role['role'] if isinstance(st.session_state.role, dict) else st.session_state.role
st.sidebar.write(f"Logged in as: **{st.session_state.username}**")
st.sidebar.caption(f"Role: {display_role.capitalize()}")

if display_role == "admin":
    nav_options = ["Dashboard", "Predictions", "Batch Prediction", "Admin Settings", "Logout"]
else:
    nav_options = ["Dashboard", "Predictions", "AI Chatbot", "Logout"]

nav = st.sidebar.radio("Navigation", nav_options)

if nav == "Logout":
    st.session_state.logged_in = False
    rerun_app()

if nav == "Dashboard":
    if display_role != "admin":
        show_student_dashboard(st.session_state.username)
    else:
        show_admin_dashboard()

# Prediction View
elif nav == "Predictions":
    # ------------------- Premium SaaS Styling -------------------
    st.markdown("""
    <style>
    /* Gradient Headings */
    .pred-header {
        background: linear-gradient(135deg, #1E293B 0%, #3B82F6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 2.4rem;
        margin-bottom: 0.25rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding-top: 1rem;
    }
    .pred-subtitle {
        color: #64748B;
        font-size: 1.05rem;
        font-weight: 500;
        margin-bottom: 2rem;
        letter-spacing: 0.02em;
    }

    /* Pill-style Tab Navigation (Matching your SaaS theme) */
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        margin-right: 12px !important;
        font-family: inherit !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        color: #64748B !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: none !important;
        min-height: auto !important;
    }
    button[data-baseweb="tab"]:hover {
        color: #1E293B !important;
        background-color: rgba(241, 245, 249, 0.6) !important;
        transform: translateY(-1px) !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #2563EB, #4F46E5) !important;
        color: white !important;
        box-shadow: 0 6px 14px rgba(37, 99, 235, 0.25) !important;
        transform: translateY(-2px) !important;
    }
    div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] {
        display: none !important;
    }
    div[data-baseweb="tab-list"] {
        gap: 0;
        padding-bottom: 0.75rem;
        padding-top: 0.5rem;
        border-bottom: 2px solid #F1F5F9;
    }

    /* Form Container (Glassmorphism + Card UI) */
    [data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 2.5rem;
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
        border: 1px solid rgba(226, 232, 240, 0.8);
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    [data-testid="stForm"]:hover {
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.02);
        transform: translateY(-2px);
    }

    /* Clean Premium Inputs */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        border-radius: 10px !important;
        border: 1px solid #E2E8F0 !important;
        transition: all 0.2s ease !important;
        padding: 0.5rem 1rem !important;
        background-color: #F8FAFC !important;
    }
    .stTextInput>div>div>input:hover, .stSelectbox>div>div>div:hover, .stNumberInput>div>div:hover {
        border-color: #94A3B8 !important;
        background-color: #FFFFFF !important;
    }
    .stTextInput>div>div>input:focus-within, .stSelectbox>div>div>div:focus-within, .stNumberInput>div>div:focus-within {
        border-color: #3B82F6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
        background-color: #FFFFFF !important;
    }

    /* Modern submit button */
    [data-testid="stFormSubmitButton"]>button {
        background: linear-gradient(135deg, #1E293B, #0F172A) !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.6rem 0 !important;
        font-weight: 700 !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 6px rgba(15, 23, 42, 0.2) !important;
    }
    [data-testid="stFormSubmitButton"]>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 15px rgba(15, 23, 42, 0.3) !important;
    }

    /* File Uploader styling for Batch Prediction */
    [data-testid="stFileUploader"] {
        background-color: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 2.5rem;
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
        border: 2px dashed rgba(226, 232, 240, 0.8) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-align: center;
        margin-top: 1rem;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #3B82F6 !important;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05);
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('''
        <div class="animate-reveal">
            <div style="background: white; padding: 3rem; border-radius: 24px; border: 1px solid #E2E8F0; box-shadow: 0 10px 30px rgba(0,0,0,0.05); margin-bottom: 2rem;">
                <h1 style="font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 2.2rem; color: #0F172A; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 15px;">
                    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path></svg>
                    Performance Prediction
                </h1>
                <p style="color: #64748B; font-size: 1.1rem;">Advanced AI modeling for precise academic outcome forecasting.</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)

    if display_role == "admin":
        tab1 = st.tabs(["👤 Individual Student"])[0]
    else:
        tab1 = st.tabs(["👤 Individual Student"])[0]
    
    with tab1:
        st.markdown("#### Real-time Student Prediction")
        name = st.text_input("Student Full Name", value="")
        col1, col2 = st.columns(2)
        with col1:
            gender = st.selectbox("Gender", ["male", "female"])
            extra = st.selectbox("Extracurricular Activities", ["True", "False"])
            hours = st.number_input("Weekly Self Study Hours", 0, 40, value=0)
            total_days = st.number_input("Total Working Days", 100, 365, value=200)
            absence_days = st.number_input("Absence Days", 0, 365, value=0)
        with col2:
            tamil = st.number_input("Tamil Score", 0, 100, value=0)
            english = st.number_input("English Score", 0, 100, value=0)
            maths = st.number_input("Maths Score", 0, 100, value=0)
            physics = st.number_input("Physics Score", 0, 100, value=0)
            chemistry = st.number_input("Chemistry Score", 0, 100, value=0)
            elective = st.selectbox("Elective Subject", ["Biology", "Computer Science"])
            elective_score = st.number_input("Elective Score", 0, 100, value=0)

        # -- Reactive Processing (Runs on every keystroke) --
        if elective == "Biology":
            biology = elective_score
            computer_science = 0
            s_label = "Biology"
        else:
            computer_science = elective_score
            biology = 0
            s_label = "Computer Science"

        input_df = pd.DataFrame([[
            gender, "False", total_days, absence_days, extra, hours, "Unknown",
            maths, tamil, physics, chemistry, biology, english, computer_science
        ]], columns=columns)

        for col_name in ["gender", "part_time_job", "extracurricular_activities", "career_aspiration"]:
            if col_name in input_df.columns and col_name in encoders:
                input_df[col_name] = safe_encode_series(input_df[col_name], encoders[col_name])

        for col_name in input_df.columns:
            input_df[col_name] = pd.to_numeric(input_df[col_name], errors='coerce').fillna(0)

        pred = model.predict(input_df)[0]
        prob = model.predict_proba(input_df)[0][1]

        # --- Sub-Charts & Explanations ---
        st.markdown("---")
        st.markdown(f'<div class="animate-reveal"><h2 style="color: #0F172A; font-weight: 800; font-family: \'Outfit\', sans-serif; font-size: 1.8rem; margin-bottom: 1.5rem;">📊 Deep Analysis: {name if name else "Student Profile"}</h2></div>', unsafe_allow_html=True)
        
        score_tamil = int(tamil)
        score_english = int(english)
        score_maths = int(maths)
        score_physics = int(physics)
        score_chemistry = int(chemistry)
        score_elective = int(elective_score)
        
        total_marks = score_tamil + score_english + score_maths + score_physics + score_chemistry + score_elective
        percentage = round((total_marks / 600) * 100, 1)
        
        if elective == "Biology":
            cutoff = (score_maths / 2) + (score_physics / 4) + (score_chemistry / 4)
        else:
            cutoff = (score_maths / 2) + (score_physics / 4) + (score_elective / 4)

        attendance_val = round(((total_days - absence_days) / total_days * 100), 1) if total_days > 0 else 0

        subject_map = {"Tamil": score_tamil, "English": score_english, "Maths": score_maths, "Physics": score_physics, "Chemistry": score_chemistry, s_label: score_elective}
        strengths = [s for s, m in subject_map.items() if m >= 80]
        weaknesses = [s for s, m in subject_map.items() if m < 50]

        # Cards
        st.markdown("""
        <style>
            .analytics-card {
                background: white;
                border-radius: 20px; padding: 1.5rem;
                box-shadow: 0px 10px 25px rgba(0,0,0,0.05); border: 1px solid #F1F5F9;
                text-align: center; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); margin-bottom: 1rem;
            }
            .analytics-card:hover { transform: translateY(-3px); box-shadow: 0px 15px 35px rgba(0,0,0,0.1); border-color: #6366F1; }
            .card-label { font-size: 0.75rem; color: #64748B; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; font-family: 'Inter', sans-serif;}
            .card-value { font-size: 1.8rem; font-weight: 800; color: #0F172A; font-family: 'Outfit', sans-serif; }
            
            .prediction-box { border-radius: 24px; padding: 2.5rem; text-align: center; margin: 2rem 0; animation: reveal 0.8s ease; }
            .pass-box { background: linear-gradient(135deg, #10B981 0%, #059669 100%); color: white; box-shadow: 0 15px 30px rgba(16, 185, 129, 0.2); border: none; }
            .fail-box { background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%); color: white; box-shadow: 0 15px 30px rgba(239, 68, 68, 0.2); border: none; }
        </style>
        """, unsafe_allow_html=True)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="analytics-card"><div class="card-label">Total Marks</div><div class="card-value" style="color: #4F46E5;">{total_marks}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="analytics-card"><div class="card-label">Percentage</div><div class="card-value">{percentage}%</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="analytics-card"><div class="card-label">Cutoff Score</div><div class="card-value" style="color: #7C3AED;">{cutoff:.1f}</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="analytics-card"><div class="card-label">Attendance</div><div class="card-value">{attendance_val}%</div></div>', unsafe_allow_html=True)

        prob_pct = round(prob * 100, 1)
        if pred == 1:
            st.markdown(f"""<div class="prediction-box pass-box"><div style="font-size: 1.8rem; font-weight: 800; font-family: 'Outfit', sans-serif;">LIKELY TO PASS</div><div style="font-family: 'Inter', sans-serif; font-size: 1.1rem; margin-top: 0.5rem;">Confidence Score: <b>{prob_pct}%</b></div></div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="prediction-box fail-box"><div style="font-size: 1.8rem; font-weight: 800; font-family: 'Outfit', sans-serif;">AT RISK OF FAILING</div><div style="font-family: 'Inter', sans-serif; font-size: 1.1rem; margin-top: 0.5rem;">Pass Probability: <b>{prob_pct}%</b></div></div>""", unsafe_allow_html=True)

        st.markdown("#### 📈 Subject-wise Performance Analysis")
        chart_data = []
        for s in ["Tamil", "English", "Maths", "Physics", "Chemistry", s_label]:
            m = subject_map[s]
            perf = "Strong" if m >= 80 else "Average" if m >= 50 else "Weak"
            chart_data.append({"Subject": s, "Marks": m, "Performance": perf})
        
        c_df = pd.DataFrame(chart_data)
        c_df["Marks"] = pd.to_numeric(c_df["Marks"]) # Guaranteed Numeric Fix
        
        import plotly.graph_objects as go
        color_map = {"Strong": "#10B981", "Average": "#F59E0B", "Weak": "#EF4444"}
        
        fig = go.Figure(data=[
            go.Bar(
                name="Performance",
                x=c_df["Subject"].tolist(),
                y=c_df["Marks"].tolist(),
                text=c_df["Marks"].tolist(),
                marker_color=[color_map[p] for p in c_df["Performance"]],
                customdata=c_df[["Performance"]].values.tolist(),
                hovertemplate="<b>%{x}</b><br>Marks: %{y}<br>Performance: %{customdata[0]}<extra></extra>",
                orientation='v'
            )
        ])
        fig.update_traces(textposition="outside", marker_line_width=0)
        fig.update_layout(yaxis=dict(range=[0, 110], dtick=10, title="Marks (0-100)", gridcolor="rgba(241, 245, 249, 0.5)"), xaxis=dict(title="", tickangle=-90), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=350, margin=dict(l=0, r=0, t=20, b=0), font=dict(family="Inter", size=13), showlegend=False)
        fig.add_hline(y=50, line_dash="dash", line_color="#94A3B8", line_width=2)
        st.plotly_chart(fig, width='stretch')

        # --- Key Strengths & Weaknesses ---
        st.markdown("")
        ins1, ins2 = st.columns(2)
        with ins1:
            st.markdown("#### 💪 Key Strengths")
            if strengths:
                s_html = "".join([f'<span class="badge badge-s" style="display:inline-block; padding:0.5rem 1rem; border-radius:10px; font-weight:700; font-size:0.9rem; margin:0.3rem; background:#DCFCE7; color:#16A34A; border:1px solid #BBF7D0;">{s}</span>' for s in strengths])
                st.markdown(f'<div style="background: white; padding: 1rem; border-radius: 12px; border: 1px solid #E2E8F0;">{s_html}</div>', unsafe_allow_html=True)
            else:
                st.info("No primary strengths (>= 80) identified.")
        with ins2:
            st.markdown("#### ⚠️ Areas of Improvement")
            if weaknesses:
                w_html = "".join([f'<span class="badge badge-w" style="display:inline-block; padding:0.5rem 1rem; border-radius:10px; font-weight:700; font-size:0.9rem; margin:0.3rem; background:#FEE2E2; color:#DC2626; border:1px solid #FECACA;">{s}</span>' for s in weaknesses])
                st.markdown(f'<div style="background: white; padding: 1rem; border-radius: 12px; border: 1px solid #E2E8F0;">{w_html}</div>', unsafe_allow_html=True)
            else:
                st.success("No critical weaknesses (< 50) identified. Keep it up!")

        # Explicit SAVE PREDICTION button decoupled from the chart so everything is live!
        if st.button("Save Prediction to History", type="primary", use_container_width=True):
            in_dict = input_df.iloc[0].to_dict()
            explanation = generate_explanation(prob, pred, input_df)
            save_prediction(st.session_state.username, name, in_dict, "Pass" if pred == 1 else "Fail", prob, explanation)
            st.success("Analysis mathematically captured and stored to Dashboard aggregates!")
            
# Batch Prediction View (Moved to separate sidebar option for Admins)
elif nav == "Batch Prediction":
    if display_role != "admin":
        st.error("Access Denied.")
    else:
        st.markdown('''
            <div class="animate-reveal">
                <div style="background: white; padding: 3rem; border-radius: 24px; border: 1px solid #E2E8F0; box-shadow: 0 10px 30px rgba(0,0,0,0.05); margin-bottom: 2rem;">
                    <h1 style="font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 2.2rem; color: #0F172A; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 15px;">
                        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg>
                        Batch Processing
                    </h1>
                    <p style="color: #64748B; font-size: 1.1rem;">Instantaneous multi-record analysis with industrial-grade AI throughput.</p>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        
        st.markdown("### 📁 Batch Prediction")
        st.markdown("Upload a CSV file containing student records to process multiple predictions at once.")
        
        up = st.file_uploader("Upload CSV for Batch Prediction", type=["csv"])
        if up:
            try:
                df_upload = pd.read_csv(up)
                
                # Validation: Check if required columns exist
                required_cols = ["student_name", "gender", "total_days", "absence_days", "weekly_self_study_hours",
                                 "tamil_score", "english_score", "maths_score", "physics_score", "chemistry_score"]
                
                missing = [c for c in required_cols if c not in df_upload.columns]
                
                if missing:
                    st.error(f"❌ Missing required columns: {', '.join(missing)}")
                    st.info("💡 Your CSV should look like the individual prediction form fields.")
                else:
                    st.success(f"✅ File uploaded: {len(df_upload)} records found.")
                    
                    processed_results = []
                    
                    # Ensure elective column is handled (Biology or Computer Science)
                    for _, row in df_upload.iterrows():
                        # Determine elective
                        if "biology_score" in row and row["biology_score"] > 0:
                            bio = int(row["biology_score"])
                            cs = 0
                            elective_type = "Biology"
                        elif "computer_science_score" in row and row["computer_science_score"] > 0:
                            cs = int(row["computer_science_score"])
                            bio = 0
                            elective_type = "Computer Science"
                        else:
                            bio = 0
                            cs = 0
                            elective_type = "None"

                        # Prepare model input (must match individual prediction logic exactly)
                        # columns: gender, part_time_job, total_days, absence_days, extracurricular_activities, 
                        #          weekly_self_study_hours, career_aspiration, maths_score, tamil_score, 
                        #          physics_score, chemistry_score, biology_score, english_score, computer_science_score
                        
                        input_row = [
                            row.get("gender", "male"),
                            row.get("part_time_job", "False"),
                            int(row["total_days"]),
                            int(row["absence_days"]),
                            row.get("extracurricular_activities", "False"),
                            int(row["weekly_self_study_hours"]),
                            row.get("career_aspiration", "Unknown"),
                            int(row["maths_score"]),
                            int(row["tamil_score"]),
                            int(row["physics_score"]),
                            int(row["chemistry_score"]),
                            bio,
                            int(row["english_score"]),
                            cs
                        ]
                        
                        m_df = pd.DataFrame([input_row], columns=columns)
                        
                        # Encode
                        for cn in ["gender", "part_time_job", "extracurricular_activities", "career_aspiration"]:
                            if cn in encoders:
                                m_df[cn] = safe_encode_series(m_df[cn], encoders[cn])
                        
                        # Force Numeric
                        for cn in m_df.columns:
                            m_df[cn] = pd.to_numeric(m_df[cn], errors='coerce').fillna(0)
                        
                        # Predict
                        p = model.predict(m_df)[0]
                        pb = model.predict_proba(m_df)[0][1]
                        
                        # Analytics
                        total = int(row["tamil_score"]) + int(row["english_score"]) + int(row["maths_score"]) + \
                                int(row["physics_score"]) + int(row["chemistry_score"]) + (bio if bio > 0 else cs)
                        pct = round((total / 600) * 100, 1)
                        
                        if elective_type == "Biology":
                            cut = (int(row["maths_score"]) / 2) + (int(row["physics_score"]) / 4) + (int(row["chemistry_score"]) / 4)
                        else:
                            cut = (int(row["maths_score"]) / 2) + (int(row["physics_score"]) / 4) + (cs / 4)

                        processed_results.append({
                            "Name": row["student_name"],
                            "Total": total,
                            "Percentage": f"{pct}%",
                            "Cutoff": round(cut, 2),
                            "Outcome": "PASS" if p == 1 else "FAIL",
                            "Probability": f"{round(pb * 100, 1)}%"
                        })
                    
                    # Display Results
                    res_df = pd.DataFrame(processed_results)
                    st.markdown("#### 🗒️ Batch Prediction Results")
                    st.dataframe(res_df, width='stretch')
                    
                    # Download CSV
                    csv = res_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Results as CSV",
                        data=csv,
                        file_name="student_predictions_report.csv",
                        mime="text/csv"
                    )
            except Exception as e:
                st.error(f"❌ Error processing file: {e}")

# AI Chatbot View
elif nav == "AI Chatbot":
    st.markdown('''
        <div class="animate-reveal">
            <div style="background: #0F172A; padding: 3rem; border-radius: 24px; box-shadow: 0 20px 40px rgba(0,0,0,0.2); margin-bottom: 2rem; position: relative; overflow: hidden;">
                <div style="position: absolute; top: -20px; right: -20px; width: 150px; height: 150px; background: rgba(99, 102, 241, 0.1); border-radius: 50%; filter: blur(40px);"></div>
                <h1 style="font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 2.2rem; color: white; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 15px;">
                    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a10 10 0 0 1 10 10c0 5.523-4.477 10-10 10S2 17.523 2 12 6.477 2 12 2z"></path><path d="M12 18c-2.33 0-4.32-1.35-5.26-3.3a1 1 0 1 0-1.8.84c1.23 2.55 3.84 4.46 6.94 4.58a1 1 0 0 0 0-2z"></path><circle cx="8.5" cy="10.5" r="1.5"></circle><circle cx="15.5" cy="10.5" r="1.5"></circle></svg>
                    AI Research Assistant
                </h1>
                <p style="color: #94A3B8; font-size: 1.1rem;">Intelligent pedagogical advisor for performance optimization.</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)

    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    # Provide an API key dynamically in the UI if not in env
    if "GROQ_API_KEY" not in os.environ:
        api_key = st.text_input("Enter your Groq API Key to enable the Chatbot:", type="password")
        if st.button("Save Key"):
            if api_key:
                os.environ["GROQ_API_KEY"] = api_key
                st.success("API Key activated! You are ready to chat.")
                st.rerun() if hasattr(st, "rerun") else st.experimental_rerun()
            else:
                st.warning("Please provide a valid API Key.")
        if "GROQ_API_KEY" not in os.environ:
            st.stop()

    from groq import Groq
    from database import setup_chat_table, get_chat_history, save_chat_message, clear_chat_history
    try:
        setup_chat_table()
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        
        col1, col2 = st.columns([0.85, 0.15])
        with col2:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                clear_chat_history(st.session_state.username)
                if "chat_messages" in st.session_state:
                    del st.session_state.chat_messages
                st.rerun() if hasattr(st, "rerun") else st.experimental_rerun()
        
        if "chat_messages" not in st.session_state:
            history = get_chat_history(st.session_state.username)
            if history:
                st.session_state.chat_messages = history
            else:
                greeting = "Hello! I am your AI Study Assistant. What can I help you with today?"
                st.session_state.chat_messages = [{"role": "assistant", "content": greeting}]
                save_chat_message(st.session_state.username, "assistant", greeting)

        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Type your message here..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            save_chat_message(st.session_state.username, "user", prompt)
            
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                stream = client.chat.completions.create(
                    model="llama-3.1-8b-instant", 
                    messages=st.session_state.chat_messages,
                    stream=True
                )
                
                message_placeholder = st.empty()
                full_response = ""
                for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta is not None:
                        full_response += delta
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                st.session_state.chat_messages.append({"role": "assistant", "content": full_response})
                save_chat_message(st.session_state.username, "assistant", full_response)
    except Exception as e:
        st.error(f"Error starting Chatbot: {e}")

# Admin View
elif nav == "Admin Settings":
    if display_role != "admin":
        st.error("Access Denied: Administrator role required.")
    else:
        st.markdown('''
            <div class="animate-reveal">
                <div style="background: white; padding: 3rem; border-radius: 24px; border: 1px solid #E2E8F0; box-shadow: 0 10px 30px rgba(0,0,0,0.05); margin-bottom: 2rem;">
                    <h1 style="font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 2.2rem; color: #0F172A; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 15px;">
                        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
                        System Infrastructure
                    </h1>
                    <p style="color: #64748B; font-size: 1.1rem;">Manage institutional access, datasets, and AI configurations.</p>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        
        from database import get_all_users, add_user, edit_user, delete_user
        
        st.markdown("### 👥 User Management")
        
        # Premium SaaS internal styling for Admin UI
        st.markdown("""
        <style>
        /* Form Card Styling - Glassmorphism & Soft Shadows */
        [data-testid="stForm"] {
            background-color: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 2.2rem;
            border-radius: 16px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
            border: 1px solid rgba(226, 232, 240, 0.8);
            margin-top: 1.5rem;
            margin-bottom: 1.5rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        [data-testid="stForm"]:hover {
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.02);
            transform: translateY(-2px);
        }

        /* Custom Streamlit Tabs matching highly-premium SaaS Navigation */
        button[data-baseweb="tab"] {
            background-color: transparent !important;
            border: 1px solid transparent !important;
            border-radius: 12px !important;
            padding: 12px 24px !important;
            margin-right: 12px !important;
            font-family: inherit !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            color: #64748B !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: none !important;
            min-height: auto !important;
        }

        /* Hover State for Inactive Tabs */
        button[data-baseweb="tab"]:hover {
            color: #1E293B !important;
            background-color: rgba(241, 245, 249, 0.6) !important;
            transform: translateY(-1px) !important;
        }

        /* Active Tab - Gradient Glow Effect */
        button[data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, #2563EB, #4F46E5) !important;
            color: white !important;
            box-shadow: 0 6px 14px rgba(37, 99, 235, 0.25) !important;
            transform: translateY(-2px) !important;
        }

        /* Hide Default Tab Decorators */
        div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] {
            display: none !important;
        }

        /* Spacing for Tab Row */
        div[data-baseweb="tab-list"] {
            gap: 0;
            padding-bottom: 0.75rem;
            padding-top: 0.5rem;
            border-bottom: 2px solid #F1F5F9;
        }
        
        /* Input & Select Box Minimal Premium Styling */
        .stTextInput>div>div>input, .stSelectbox>div>div>div {
            border-radius: 10px !important;
            transition: all 0.2s ease !important;
        }
        .stTextInput>div>div>input:hover, .stSelectbox>div>div>div:hover {
            border-color: #94A3B8 !important;
        }
        .stTextInput>div>div>input:focus-within, .stSelectbox>div>div>div:focus-within {
            border-color: #3B82F6 !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
        }
        
        /* Make DataFrames clean with rounded corners */
        [data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            border: 1px solid #E2E8F0;
            margin-top: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)

        tab_view, tab_add, tab_edit, tab_del = st.tabs(["👁️ View Users", "➕ Add User", "✏️ Edit User", "🗑️ Delete User"])
        
        users_list = get_all_users()
        df_users = pd.DataFrame(users_list)
        
        with tab_view:
            # Remove 'subject' column for Admin view as per requirement
            df_view = df_users.drop(columns=['subject']) if 'subject' in df_users.columns else df_users
            st.dataframe(df_view, width='stretch')
            
            st.markdown("---")
            st.subheader("Prediction History")
            
            # --- Search Filter ---
            search_query = st.text_input("🔍 Search by Username or Student Name", "")
            
            all_preds = get_all_predictions()
            if all_preds:
                df_preds = pd.DataFrame(all_preds)
                if search_query:
                    mask = (
                        df_preds['username'].astype(str).str.contains(search_query, case=False, na=False) |
                        df_preds['student_name'].astype(str).str.contains(search_query, case=False, na=False)
                    )
                    df_preds = df_preds[mask]
                
                if not df_preds.empty:
                    st.dataframe(df_preds, use_container_width=True)
                else:
                    st.info("No matching results found.")
            else:
                st.info("No prediction history available.")
                
        with tab_add:
            st.markdown("#### Create New User")
            with st.form("add_user_form", clear_on_submit=True):
                new_user = st.text_input("Username")
                new_pass = st.text_input("Password", type="password")
                new_role = st.selectbox("Role", ["student", "admin"], key="add_role")
                new_subj = "General"  # Defaulted as per UI requirement
                    
                submitted = st.form_submit_button("Add User", use_container_width=True)
                if submitted:
                    if new_user and new_pass:
                        add_user(new_user, new_pass, role=new_role, subject=new_subj)
                        st.success(f"User '{new_user}' created successfully!")
                        rerun_app()
                    else:
                        st.error("Username and Password are required.")
                        
        with tab_edit:
            st.markdown("#### Modify Existing User")
            if not df_users.empty:
                usernames = df_users['username'].tolist()
                selected_user = st.selectbox("Select User to Edit", usernames)
                
                current_data = df_users[df_users['username'] == selected_user].iloc[0]
                
                with st.form("edit_user_form"):
                    st.text_input("Username (Read-only)", value=selected_user, disabled=True)
                    role_options = ["student", "admin"]
                    try:
                        r_index = role_options.index(current_data['role'])
                    except ValueError:
                        r_index = 0
                    edit_role = st.selectbox("New Role", role_options, index=r_index)
                    edit_subj = current_data['subject'] # Keep existing
                        
                    edit_pass = st.text_input("New Password (leave blank to keep current)", type="password")
                    
                    submitted_edit = st.form_submit_button("Update User", use_container_width=True)
                    if submitted_edit:
                        edit_user(selected_user, edit_role, edit_subj, edit_pass if edit_pass else None)
                        st.success(f"User '{selected_user}' updated!")
                        rerun_app()
            else:
                st.info("No users found.")
                
        with tab_del:
            st.markdown("#### Remove User")
            if not df_users.empty:
                usernames = df_users['username'].tolist()
                # Prevent self deletion
                curr_user = st.session_state.username
                safe_usernames = [u for u in usernames if u != curr_user]
                if safe_usernames:
                    with st.form("del_user_form"):
                        del_user = st.selectbox("Select User to Delete", safe_usernames)
                        st.markdown("<p style='color: #EF4444; font-size: 0.9rem;'>⚠️ This action cannot be undone.</p>", unsafe_allow_html=True)
                        submitted_del = st.form_submit_button("Delete User", use_container_width=True)
                        if submitted_del:
                            delete_user(del_user)
                            st.success(f"User '{del_user}' deleted!")
                            rerun_app()
                else:
                    st.warning("No other users available to delete. (You cannot delete yourself)")
            else:
                st.info("No users found.")
