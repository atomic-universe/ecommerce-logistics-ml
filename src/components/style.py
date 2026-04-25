import streamlit as st


def load_css():
    st.markdown(
        """
      <style>
       @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

    :root {
        --bg:         #0D1117;
        --surface:    #161B22;
        --surface2:   #1C2330;
        --border:     #30363D;
        --accent:     #F0A500;
        --accent2:    #E05C2A;
        --text:       #E6EDF3;
        --text-muted: #7D8590;
        --green:      #3FB950;
        --red:        #F85149;
        --blue:       #58A6FF;
        --purple:     #BC8CFF;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        background-color: var(--bg) !important;
        color: var(--text) !important;
    }

    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 2rem 3rem !important; max-width: 1400px !important; }

   

    /* ── KPI Cards ── */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin: 1.5rem 0;
    }
    .kpi-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.4rem 1.6rem;
        position: relative;
        overflow: hidden;
        transition: border-color 0.2s, transform 0.2s;
    }
    .kpi-card:hover { border-color: var(--accent); transform: translateY(-2px); }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--accent), var(--accent2));
    }
    .kpi-label {
        font-size: 0.75rem; font-weight: 500;
        letter-spacing: 0.08em; text-transform: uppercase;
        color: var(--text-muted); margin-bottom: 0.5rem;
    }
    .kpi-value {
        font-family: 'Syne', sans-serif;
        font-size: 2rem; font-weight: 700;
        color: var(--text); line-height: 1;
    }
    .kpi-icon {
        position: absolute; top: 1.2rem; right: 1.4rem;
        font-size: 1.6rem; opacity: 0.15;
    }

    /* ── Hero ── */
    .hero {
        background: linear-gradient(135deg, var(--surface) 0%, var(--surface2) 100%);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 2.5rem 3rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    .hero::after {
        content: '🛒';
        position: absolute; right: 2rem; top: 50%;
        transform: translateY(-50%);
        font-size: 6rem; opacity: 0.07;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(240,165,0,0.15);
        border: 1px solid rgba(240,165,0,0.3);
        color: var(--accent);
        font-size: 0.72rem; font-weight: 600;
        letter-spacing: 0.1em; text-transform: uppercase;
        padding: 0.3rem 0.8rem; border-radius: 20px;
        margin-bottom: 1rem;
    }
    .hero-title {
        font-family: 'Syne', sans-serif;
        font-size: 2.4rem; font-weight: 800;
        color: var(--text); line-height: 1.15; margin-bottom: 0.8rem;
    }
    .hero-title span { color: var(--accent); }
    .hero-subtitle {
        font-size: 1rem; color: var(--text-muted);
        max-width: 560px; line-height: 1.6;
    }

    /* ── Section Header ── */
    .section-header {
        font-family: 'Syne', sans-serif;
        font-size: 1.1rem; font-weight: 700;
        color: var(--text); letter-spacing: 0.02em;
        margin: 2rem 0 1rem;
        padding: 0.6rem;
        border-bottom: 1px solid var(--border);
    }

    /* ── Nav page_link styling ── */
    [data-testid="stPageLink"] a {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        padding: 1.2rem !important;
        text-align: center !important;
        color: var(--text) !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease !important;
        display: block !important;
        text-decoration: none !important;
    }
    [data-testid="stPageLink"] a:hover {
        border-color: var(--accent) !important;
        background: var(--surface2) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(240,165,0,0.1) !important;
        color: var(--accent) !important;
    }

    /* ── Dataset Grid ── */
    .dataset-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.75rem; margin: 1rem 0;
    }
    .dataset-item {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px; padding: 0.9rem 1.1rem;
        display: flex; align-items: center; gap: 0.7rem;
    }
    .dataset-dot {
        width: 8px; height: 8px;
        border-radius: 50%; background: var(--accent); flex-shrink: 0;
    }
    .dataset-name { font-size: 0.8rem; color: var(--text-muted); font-family: monospace; }

    /* ── Footer ── */
    .dash-footer {
        margin-top: 4rem; padding-top: 1.5rem;
        border-top: 1px solid var(--border);
        display: flex; justify-content: space-between; align-items: center;
    }
    .dash-footer-left { font-size: 0.8rem; color: var(--text-muted); }
    .dash-footer-right { font-size: 0.75rem; color: var(--text-muted); font-family: monospace; }
    .accent { color: var(--accent); }


    
    /* ── Page Header ── */
    .page-header {
        background: linear-gradient(135deg, var(--surface) 0%, var(--surface2) 100%);
        border: 1px solid var(--border);
        border-left: 4px solid var(--accent);
        border-radius: 12px;
        padding: 1.8rem 2rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    .page-header::after {
        content: '📦';
        position: absolute; right: 1.5rem; top: 50%;
        transform: translateY(-50%);
        font-size: 4rem; opacity: 0.08;
    }
    .page-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.8rem; font-weight: 800;
        color: var(--text); margin-bottom: 0.3rem;
    }
    .page-title span { color: var(--accent); }
    .page-subtitle { font-size: 0.9rem; color: var(--text-muted); }

     /* ── Insight Box ── */
    .insight-box {
        background: rgba(240, 165, 0, 0.08);
        border: 1px solid rgba(240, 165, 0, 0.25);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin: 0.8rem 0;
        font-size: 0.85rem;
        color: var(--text-muted);
        line-height: 1.6;
    }
    .insight-box strong { color: var(--accent); }


    /* ── Star Rating ── */
    .star-row {
        display: flex; gap: 0.5rem;
        align-items: center; margin: 0.3rem 0;
    }
    .star-bar-bg {
        flex: 1; height: 8px;
        background: var(--surface2);
        border-radius: 4px; overflow: hidden;
    }
    .star-bar-fill {
        height: 100%; border-radius: 4px;
        background: linear-gradient(90deg, var(--accent), var(--accent2));
    }
    

    .result-card {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    border-radius: 20px;
    padding: 28px 20px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    border: 1px solid rgba(255,255,255,0.08);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.result-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.6);
}
.result-title {
    font-size: 0.85rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.12em;
}
.result-days {
    font-size: 2.8rem;
    font-weight: 800;
    margin: 10px 0;
}
.result-label {
    font-size: 1.2rem;
    color: #cbd5f5;
}

# Submit button.
div.stButton > button {
    background: #0f172a;
    color: #22c55e;
    border: 2px solid #22c55e;
    border-radius: 14px;
    padding: 14px 24px;
    font-size: 1rem;
    font-weight: 700;
    transition: all 0.25s ease;
  box-shadow: 0 0 10px rgba(91, 85, 188, 0.3);
}

div.stButton > button:hover {
   background: #c8e177;
  color: #0f172a;
  box-shadow: 0 0 25px rgba(167, 210, 74, 0.452);

}
div.stButton > button:disabled {
    background: #374151;
    color: #9ca3af;
    box-shadow: none;
    cursor: not-allowed;
}
        </style>
        """ ,unsafe_allow_html=True )