import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from database import get_all_predictions

def show_admin_dashboard():
    st.title("🚀 Global Analytics Dashboard")
    
    all_preds = get_all_predictions()
    total_students = len(all_preds) if all_preds else 0
    
    sums = {"Tamil": 0, "English": 0, "Maths": 0, "Physics": 0, "Chemistry": 0, "Biology": 0, "CS": 0}
    counts = {"Tamil": 0, "English": 0, "Maths": 0, "Physics": 0, "Chemistry": 0, "Biology": 0, "CS": 0}
    passes = 0
    total_score_sum = 0
    
    if all_preds:
        for p in all_preds:
            try:
                data = json.loads(p["input_json"]) if isinstance(p["input_json"], str) else p["input_json"]
                for sub in ["tamil_score", "english_score", "maths_score", "physics_score", "chemistry_score"]:
                    sub_key = sub.replace("_score", "").capitalize()
                    val = int(data.get(sub, 0))
                    sums[sub_key] += val
                    counts[sub_key] += 1
                
                if data.get("biology_score", 0) > 0:
                    sums["Biology"] += int(data.get("biology_score", 0))
                    counts["Biology"] += 1
                if data.get("computer_science_score", 0) > 0:
                    sums["CS"] += int(data.get("computer_science_score", 0))
                    counts["CS"] += 1
                
                if p["result"] == "Pass":
                    passes += 1
                
                t_score = sum([int(data.get(k, 0)) for k in ["tamil_score", "english_score", "maths_score", "physics_score", "chemistry_score", "biology_score", "computer_science_score"]])
                total_score_sum += (t_score / 600) * 100
            except Exception:
                pass

    avg_score_val = round(total_score_sum / total_students, 1) if total_students > 0 else 0
    pass_rate_val = round((passes / total_students) * 100, 1) if total_students > 0 else 0
    
    avg_dict = {k: (sums[k]/counts[k] if counts[k] else 0) for k in sums}
    top_sub = max(avg_dict, key=avg_dict.get) if total_students > 0 else "N/A"

    # --- High-Class Metric Cards ---
    st.markdown("""
    <style>
    .metric-card-new {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: reveal 0.8s ease-out forwards;
    }
    .metric-card-new:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        border-color: #6366F1;
        background: white;
    }
    .label-new { font-size: 0.75rem; color: #64748B; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem; }
    .value-new { font-size: 2rem; font-weight: 800; color: #1E293B; font-family: 'Outfit', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="animate-reveal">', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-card-new"><div class="label-new">Total Predictions</div><div class="value-new">{total_students}</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card-new"><div class="label-new">Average Score</div><div class="value-new">{avg_score_val}%</div></div>', unsafe_allow_html=True)
    with m3:
        p_color = "#10B981" if pass_rate_val >= 50 else "#EF4444"
        st.markdown(f'<div class="metric-card-new"><div class="label-new">System Pass Rate</div><div class="value-new" style="color: {p_color}">{pass_rate_val}%</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card-new"><div class="label-new">Leading Subject</div><div class="value-new" style="color: #6366F1">{top_sub}</div></div>', unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Subject-wise Performance Analysis")
        df_chart = pd.DataFrame({
            "Subject": ["Tamil", "English", "Maths", "Physics", "Chemistry", "Biology", "CS"],
            "Score": [round(avg_dict[k]) for k in ["Tamil", "English", "Maths", "Physics", "Chemistry", "Biology", "CS"]]
        })
        
        fig = go.Figure(data=[
            go.Bar(
                name='Score', 
                x=df_chart["Subject"].tolist(), 
                y=df_chart["Score"].tolist(), 
                text=df_chart["Score"].tolist(), 
                marker_color="#6366F1",
                marker_line_width=0,
                opacity=0.9
            )
        ])
        fig.update_traces(textposition="outside", hovertemplate="<b>%{x}</b><br>Global Average: %{y}<extra></extra>")
        fig.update_layout(
            showlegend=False, 
            margin=dict(l=0, r=0, t=30, b=0), 
            height=380, 
            yaxis=dict(range=[0, 115], gridcolor="#F1F5F9", title="Average Marks"), 
            xaxis=dict(gridcolor="rgba(0,0,0,0)", title=""),
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter", size=12)
        )
        fig.add_hline(y=50, line_dash="dash", line_color="#CBD5E1", line_width=1)
        st.plotly_chart(fig, width='stretch')

    with c2:
        st.subheader("Pass/Fail Distribution")
        if total_students > 0:
            fig_pie = px.pie(
                names=["Pass", "Fail"], 
                values=[passes, total_students - passes], 
                color_discrete_sequence=["#10B981", "#EF4444"], 
                hole=0.65
            )
            fig_pie.update_traces(textinfo="percent", marker=dict(line=dict(color='#FFFFFF', width=3)))
            fig_pie.update_layout(
                margin=dict(l=0, r=0, t=30, b=0), 
                height=380, 
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter", size=12)
            )
            st.plotly_chart(fig_pie, width='stretch')
            st.info("No system data available yet.")
    st.markdown('</div>', unsafe_allow_html=True)
