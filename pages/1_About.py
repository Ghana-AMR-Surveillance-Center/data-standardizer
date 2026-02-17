"""
AMR Data Harmonizer - About Page
Platform overview, challenges, solutions, and features.
"""

import streamlit as st

st.set_page_config(
    page_title="About - AMR Data Harmonizer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar - About page specific content
with st.sidebar:
    # Logo/branding (match main app)
    import os
    logo_paths = ["Png/logo.png", "Png/amr-secretariat.png", "Png/drmichaeladu-logo.png"]
    logo_loaded = False
    for lp in logo_paths:
        try:
            if os.path.exists(lp):
                st.image(lp, use_container_width=True)
                logo_loaded = True
                break
        except Exception:
            continue
    if not logo_loaded:
        st.markdown("### 🧬 AMR Data Harmonizer")
    
    st.markdown("**About** — Platform overview, challenges, and features.")
    st.markdown("---")
    
    st.markdown("**📋 On this page**")
    st.markdown("""
    - 🔍 The Challenge  
    - ✨ Our Solution  
    - 🎯 Key Features  
    - 💼 Who Benefits  
    - 🚀 Get Started
    """)
    st.markdown("---")
    
    st.markdown("**✨ Quick highlights**")
    st.success("GLASS & WHONET ready")
    st.success("No coding required")
    st.success("African lab context")
    st.markdown("---")
    
    if st.button("🚀 Go to App", type="primary", use_container_width=True, key="sidebar_cta"):
        st.switch_page("app.py")
    
    st.markdown("---")
    st.caption("v2.0.0 | © 2025 drmichaeladu")

# Enhanced styling with responsive design
st.markdown("""
    <style>
    /* Hero */
    .about-hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: clamp(1.5rem, 4vw, 2.5rem);
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    .about-hero h2 { color: white !important; margin-bottom: 0.75rem !important; font-size: clamp(1.4rem, 4vw, 1.75rem) !important; font-weight: 700; }
    .about-hero .tagline { font-size: clamp(0.95rem, 2vw, 1.1rem); opacity: 0.95; line-height: 1.7; margin-bottom: 0.5rem; }
    .about-hero .badges { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1rem; }
    .about-hero .badge { background: rgba(255,255,255,0.25); padding: 0.4rem 0.85rem; border-radius: 20px; font-size: 0.8rem; font-weight: 500; }
    /* Section titles - left accent */
    .about-section-title {
        font-size: clamp(1.2rem, 3vw, 1.35rem);
        font-weight: 600;
        color: #1a202c;
        margin: 2.5rem 0 1rem 0;
        padding: 0.5rem 0 0.5rem 1rem;
        border-left: 4px solid #667eea;
        background: linear-gradient(90deg, rgba(102,126,234,0.06) 0%, transparent 100%);
        border-radius: 0 8px 8px 0;
    }
    /* Cards - equal height, improved spacing */
    .about-card {
        background: #fff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        min-height: 140px;
        display: flex;
        flex-direction: column;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: all 0.2s ease;
    }
    .about-card:hover { border-color: #667eea; box-shadow: 0 4px 16px rgba(102, 126, 234, 0.12); }
    .about-card h4 { color: #334155; margin: 0 0 0.6rem 0 !important; font-size: 1.05rem; font-weight: 600; }
    .about-card ul { margin: 0.5rem 0 0 1rem !important; padding: 0 !important; flex: 1; }
    .about-card li { margin-bottom: 0.4rem; line-height: 1.45; font-size: 0.95rem; }
    /* CTA */
    .about-cta {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: clamp(1.5rem, 3vw, 2rem);
        border-radius: 16px;
        color: white;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.25);
        margin-top: 2rem;
    }
    .about-cta h3 { color: white !important; margin: 0 0 0.75rem 0 !important; font-size: clamp(1.2rem, 3vw, 1.35rem) !important; }
    .about-cta p { color: rgba(255,255,255,0.95) !important; margin: 0.4rem 0 !important; font-size: 0.98rem; line-height: 1.6; }
    /* Footer */
    .about-footer { text-align: center; color: #64748b; font-size: 0.85rem; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #e2e8f0; }
    /* Page header */
    .step-header { font-size: clamp(1.2rem, 4vw, 1.8rem); font-weight: 600; margin: 0 0 1rem 0 !important; color: #1a202c; padding-bottom: 0.5rem; border-bottom: 3px solid #667eea; }
    /* Responsive */
    @media (max-width: 768px) {
        .about-card { min-height: auto; }
        .about-section-title { margin: 2rem 0 0.75rem 0; }
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="step-header">About AMR Data Harmonizer</h1>', unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class='about-hero'>
    <h2>🧬 AMR Data Harmonizer</h2>
    <p class='tagline'>
        A comprehensive platform designed to address critical data cleaning challenges in 
        <strong>Antimicrobial Resistance (AMR) surveillance</strong> across African laboratories.
    </p>
    <p class='tagline' style='margin-bottom:0'>
        Transform fragmented, inconsistent lab data into submission-ready formats for GLASS and WHONET.
    </p>
    <div class='badges'>
        <span class='badge'>GLASS Ready</span>
        <span class='badge'>WHONET Compatible</span>
        <span class='badge'>African Context</span>
        <span class='badge'>No Coding Required</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Quick nav + primary CTA
nav_col1, nav_col2 = st.columns([2, 1])
with nav_col1:
    with st.expander("📋 Jump to section", expanded=False):
        st.markdown("**The Challenge** · **Our Solution** · **Key Features** · **Who Benefits** · **Get Started**")
with nav_col2:
    if st.button("🚀 Get Started", type="primary", use_container_width=True, help="Go to workflow selection"):
        st.switch_page("app.py")

st.markdown("---")

# The Challenge
st.markdown('<p class="about-section-title">🔍 The Challenge</p>', unsafe_allow_html=True)
st.caption("Common data quality issues in African AMR surveillance and their impact on global reporting.")

ch_col1, ch_col2 = st.columns(2)

with ch_col1:
    st.markdown("""
    <div class='about-card'>
    <h4>📊 Data Quality Issues</h4>
    <ul>
    <li><strong>Inconsistent Collection</strong> — Varied formats, naming conventions, and date formats across laboratories</li>
    <li><strong>Limited Capacity</strong> — Manual data entry, lack of standardized formats, limited QA processes</li>
    <li><strong>Fragmented Management</strong> — Data in multiple systems, difficulty merging, no harmonization</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

with ch_col2:
    st.markdown("""
    <div class='about-card'>
    <h4>📉 Impact on Global Surveillance</h4>
    <ul>
    <li><strong>Submission Barriers</strong> — Data doesn't meet GLASS/WHONET requirements</li>
    <li><strong>Reduced Quality</strong> — Incomplete datasets, inconsistent organism names</li>
    <li><strong>Time-Consuming</strong> — Hours on manual cleaning, high error risk, delayed submission</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Our Solution
st.markdown('<p class="about-section-title">✨ Our Solution</p>', unsafe_allow_html=True)

sol_col1, sol_col2, sol_col3 = st.columns(3)

with sol_col1:
    st.markdown("""
    <div class='about-card'>
    <h4>🧹 Intelligent Data Cleaning</h4>
    <ul>
    <li>Automatic AMR column detection</li>
    <li>Organism & antimicrobial standardization</li>
    <li>Encoding, delimiter & merged cell handling</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

with sol_col2:
    st.markdown("""
    <div class='about-card'>
    <h4>🔗 Smart Data Integration</h4>
    <ul>
    <li>Multi-file merging with fuzzy matching</li>
    <li>Column mapping & harmonization</li>
    <li>Quality validation built-in</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

with sol_col3:
    st.markdown("""
    <div class='about-card'>
    <h4>📤 Global Submission Ready</h4>
    <ul>
    <li>GLASS & WHONET wizards</li>
    <li>Step-by-step guidance</li>
    <li>Export: CSV, Excel, JSON, XML</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Key Features
st.markdown('<p class="about-section-title">🎯 Key Features</p>', unsafe_allow_html=True)

feat_col1, feat_col2 = st.columns(2)

with feat_col1:
    st.markdown("""
    <div class='about-card'>
    <h4>Data Cleaning & Processing</h4>
    <ul>
    <li>Organism name standardization (S/R/I/ND/NM)</li>
    <li>Specimen type & date format handling</li>
    <li>Multiple encodings (UTF-8, Latin-1, CP1252)</li>
    <li>Auto delimiter detection, merged cells, footer removal</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

with feat_col2:
    st.markdown("""
    <div class='about-card'>
    <h4>Analytics & Production</h4>
    <ul>
    <li>AMR resistance analysis with CLSI compliance</li>
    <li>Antibiogram generation & visualizations</li>
    <li>Error handling, health monitoring, security validation</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Who Benefits
st.markdown('<p class="about-section-title">💼 Who Can Benefit</p>', unsafe_allow_html=True)

ben_col1, ben_col2, ben_col3 = st.columns(3)

with ben_col1:
    st.markdown("""
    <div class='about-card'>
    <h4>🏥 Laboratory Staff</h4>
    <ul>
    <li>Clean daily lab data</li>
    <li>Prepare for submission</li>
    <li>Generate quality reports</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

with ben_col2:
    st.markdown("""
    <div class='about-card'>
    <h4>📊 Data Managers</h4>
    <ul>
    <li>Merge multiple sources</li>
    <li>Harmonize datasets</li>
    <li>Ensure quality standards</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

with ben_col3:
    st.markdown("""
    <div class='about-card'>
    <h4>🔬 Researchers</h4>
    <ul>
    <li>Prepare data for analysis</li>
    <li>Generate AMR analytics</li>
    <li>Export publication-ready reports</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# CTA
st.markdown("""
<div class='about-cta'>
    <h3>🚀 Ready to Get Started?</h3>
    <p>
        Choose a workflow from the <strong>App</strong> page to begin. The tool guides you through each step with clear instructions.
    </p>
    <p>
        <strong>💡 Tip:</strong> <strong>Merge Multiple Files</strong> for multi-source data · 
        <strong>Standardize Single File</strong> for individual files · 
        <strong>GLASS</strong> and <strong>WHONET Wizards</strong> for step-by-step guidance.
    </p>
</div>
""", unsafe_allow_html=True)

# Bottom CTA button
st.markdown("")
if st.button("🚀 Go to App — Choose Your Workflow", type="primary", use_container_width=True, key="cta_bottom"):
    st.switch_page("app.py")

# Footer with compact nav hint
st.markdown("---")
st.caption("👈 Use **App** in the sidebar or the button above to choose your workflow.")

# Footer
st.markdown('<p class="about-footer">AMR Data Harmonizer v2.0.0 | © 2025 drmichaeladu</p>', unsafe_allow_html=True)
