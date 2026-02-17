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

# Apply shared styling for hero, sections, and CTA
st.markdown("""
    <style>
    .about-hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.25);
    }
    .about-hero h2 { color: white !important; margin-bottom: 1rem !important; font-size: 1.5rem !important; }
    .about-hero p { font-size: 1.05rem; line-height: 1.6; color: rgba(255,255,255,0.95) !important; margin: 0 !important; }
    .about-section-card {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        transition: box-shadow 0.2s;
    }
    .about-section-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.06); }
    .about-cta {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.2);
    }
    .about-cta h3 { color: white !important; margin-top: 0 !important; font-size: 1.25rem !important; }
    .about-cta p { color: rgba(255,255,255,0.95) !important; margin: 0.5rem 0 !important; font-size: 0.95rem; }
    .step-header {
        font-size: clamp(1.2rem, 4vw, 1.8rem);
        font-weight: 600;
        margin: 1.5rem 0 0.75rem 0 !important;
        color: #1a202c;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="step-header">About AMR Data Harmonizer</h1>', unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class='about-hero'>
    <h2>🏥 Welcome to AMR Data Harmonizer</h2>
    <p>
        A comprehensive platform designed to address critical data cleaning challenges in 
        <strong>Antimicrobial Resistance (AMR) surveillance</strong> across African laboratories.
    </p>
</div>
""", unsafe_allow_html=True)

# Problem Statement
st.markdown("### 🔍 The Challenge")
st.caption("Common data quality issues and their impact on global surveillance.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### Common Data Quality Issues in African AMR Surveillance:
    
    - **📊 Inconsistent Data Collection**
      - Varied formats and structures across laboratories
      - Different naming conventions for organisms and antimicrobials
      - Inconsistent date formats and data entry practices
    
    - **🔬 Limited Laboratory Capacity**
      - Manual data entry leading to errors
      - Lack of standardized reporting formats
      - Limited quality assurance processes
    
    - **📁 Fragmented Data Management**
      - Data stored in multiple systems and formats
      - Difficulty in merging data from different sources
      - Lack of data harmonization
    """)

with col2:
    st.markdown("""
    #### Impact on Global Surveillance:
    
    - **🚫 Submission Barriers**
      - Data doesn't meet GLASS (Global Antimicrobial Resistance and Use Surveillance System) requirements
      - Incompatible with WHONET format
      - Missing required fields and validation failures
    
    - **📉 Reduced Data Quality**
      - Incomplete datasets
      - Inconsistent organism names and antimicrobial results
      - Missing critical metadata
    
    - **⏱️ Time-Consuming Manual Work**
      - Hours spent on data cleaning and standardization
      - High risk of human error
      - Delayed submission to global surveillance systems
    """)

st.markdown("---")

# Solution Section
st.markdown("### ✨ How AMR Data Harmonizer Solves These Problems")

solution_cols = st.columns(3)

with solution_cols[0]:
    st.markdown("""
    #### 🧹 **Intelligent Data Cleaning**
    
    - **Automatic Detection**: Identifies AMR-specific columns (organisms, antimicrobials, specimens)
    - **Flexible Cleaning**: Handles various data formats and edge cases
    - **Standardization**: Normalizes organism names, antimicrobial results, and specimen types
    - **Edge Case Handling**: Manages encoding issues, delimiters, merged cells, and more
    """)

with solution_cols[1]:
    st.markdown("""
    #### 🔗 **Smart Data Integration**
    
    - **Multi-File Merging**: Intelligently combines data from multiple sources
    - **Column Mapping**: Automatic matching with fuzzy logic
    - **Data Harmonization**: Resolves inconsistencies across datasets
    - **Quality Validation**: Ensures merged data meets standards
    """)

with solution_cols[2]:
    st.markdown("""
    #### 📤 **Global Submission Ready**
    
    - **GLASS Preparation**: Wizard-guided preparation for GLASS submission
    - **WHONET Compatibility**: Standardizes data for WHONET import
    - **Quality Assessment**: Comprehensive data quality scoring
    - **Export Options**: Multiple formats (CSV, Excel, JSON, XML)
    """)

st.markdown("---")

# Key Features
st.markdown("### 🎯 Key Features")

feature_cols = st.columns(2)

with feature_cols[0]:
    st.markdown("""
    - ✅ **Flexible AMR Data Cleaning**
      - Automatic organism name standardization
      - Antimicrobial result normalization (S/R/I/ND/NM)
      - Specimen type standardization
      - Date format handling
      - Age extraction from text
    
    - ✅ **Robust File Processing**
      - Multiple encoding support (UTF-8, Latin-1, CP1252, etc.)
      - Automatic delimiter detection
      - Handles empty files, multiple sheets, merged cells
      - Footer/summary row removal
    """)

with feature_cols[1]:
    st.markdown("""
    - ✅ **Advanced Analytics**
      - AMR resistance analysis with statistical validation
      - Antibiogram generation
      - Data quality assessment
      - Professional visualizations
    
    - ✅ **Production Ready**
      - Comprehensive error handling
      - Health monitoring
      - Security validation
      - Performance optimization
    """)

st.markdown("---")

# Use Cases
st.markdown("### 💼 Who Can Benefit?")

use_case_cols = st.columns(3)

with use_case_cols[0]:
    st.markdown("""
    **🏥 Laboratory Staff**
    - Clean and standardize daily lab data
    - Prepare data for submission
    - Generate quality reports
    """)

with use_case_cols[1]:
    st.markdown("""
    **📊 Data Managers**
    - Merge data from multiple sources
    - Harmonize inconsistent datasets
    - Ensure data quality standards
    """)

with use_case_cols[2]:
    st.markdown("""
    **🔬 Researchers**
    - Prepare data for analysis
    - Generate AMR analytics
    - Export publication-ready reports
    """)

st.markdown("---")

# Call to Action
st.markdown("""
<div class='about-cta'>
    <h3>🚀 Ready to Get Started?</h3>
    <p>
        Choose a workflow from the <strong>Home</strong> page to begin processing your AMR surveillance data. 
        The tool will guide you through each step with clear instructions.
    </p>
    <p>
        <strong>💡 Tip:</strong> Start with "Merge Multiple Files" if you have data from multiple sources, 
        or "Standardize Single File" for individual file processing.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.info("👈 Go to **Home** in the sidebar to choose your workflow and start processing.")
