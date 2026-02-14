"""
Enhanced AMR Interface for AMR Data Harmonizer
Professional interface optimized for real-world antimicrobial susceptibility data

Features:
- Professional visualizations with consistent styling
- Data quality assessment and guidance
- Interactive dashboards and summaries
- Optimized for the specific dataset characteristics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import base64
from typing import Dict, List, Optional, Union
import zipfile
from datetime import datetime
import logging
import warnings

from .amr_analytics import AMRAnalytics
from .ast_detector import ASTDataDetector

# Configure logging
logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')

class AMRInterface:
    """
    Enhanced Streamlit interface for professional AMR analytics
    """
    
    def __init__(self):
        self.amr_analytics = AMRAnalytics()
        self.ast_detector = ASTDataDetector()
    
    def render_enhanced_amr_analysis_page(self):
        """
        Render the enhanced AMR analysis page with professional styling
        """
        st.title("🧬 Enhanced AMR Analytics")
        st.markdown("---")
        
        # Check if data is available
        if 'processed_data' not in st.session_state or st.session_state.processed_data is None:
            self._render_data_upload_section()
            return
        
        df = st.session_state.processed_data
        
        # Professional header with data summary
        self._render_data_summary_header(df)
        
        # Sidebar controls
        self._render_enhanced_sidebar_controls(df)
        
        # Main analysis area
        analysis_type = st.session_state.get('amr_analysis_type', 'Dashboard')
        
        if analysis_type == 'Dashboard':
            self._render_professional_dashboard(df)
        elif analysis_type == 'Antibiogram':
            self._render_enhanced_antibiogram(df)
        elif analysis_type == 'Resistance Patterns':
            self._render_resistance_patterns_analysis(df)
        elif analysis_type == 'Data Quality':
            self._render_data_quality_analysis(df)
        elif analysis_type == 'Export Reports':
            self._render_export_section(df)
    
    def _render_data_upload_section(self):
        """Enhanced data upload section with validation"""
        st.warning("⚠️ No data available for AMR analysis. Please upload your antimicrobial susceptibility data.")
        
        # Upload section with enhanced styling
        st.subheader("📤 Upload Antimicrobial Susceptibility Data")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Choose a CSV or Excel file containing antimicrobial susceptibility data",
                type=['csv', 'xlsx', 'xls'],
                help="Upload data with columns for organisms, antimicrobials, and susceptibility results"
            )
        
        with col2:
            st.info("""
            **Expected Format:**
            - Organism column
            - Antimicrobial columns ending with '_ND' or '_NM'
            - Zone diameter values (mm)
            """)
        
        if uploaded_file is not None:
            try:
                logger.info(f"Processing uploaded file: {uploaded_file.name}")
                
                # Security validation first
                from utils.security import security_manager
                security_validation = security_manager.validate_file_upload(uploaded_file)
                
                if not security_validation['valid']:
                    for error in security_validation['errors']:
                        st.error(f"❌ Security validation failed: {error}")
                        logger.warning(f"AMR file upload rejected: {uploaded_file.name} - {error}")
                    return
                
                if security_validation.get('warnings'):
                    for warning in security_validation['warnings']:
                        st.warning(f"⚠️ {warning}")
                        logger.info(f"AMR file upload warning: {uploaded_file.name} - {warning}")
                
                # Read the file
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file, encoding='utf-8')
                else:
                    df = pd.read_excel(uploaded_file, engine='openpyxl')
                
                # Enhanced validation
                validation_result = self._validate_amr_data(df)
                
                if validation_result['valid']:
                    # Store in session state
                    st.session_state.processed_data = df
                    st.session_state.amr_steps['upload'] = True
                    
                    st.success(f"✅ Successfully uploaded {len(df)} records with {len(df.columns)} columns")
                    
                    # Show validation summary
                    self._display_validation_summary(validation_result)
                    
                    # Detect AST data type
                    with st.spinner("🔍 Analyzing AST data format..."):
                        detection_result = self.ast_detector.detect_ast_data_type(df)
                    
                    # Show detection results
                    self._display_ast_detection_results(detection_result)
                    
                    # Store detection result in session state
                    st.session_state.ast_detection_result = detection_result
                    
                    st.rerun()
                else:
                    st.error("❌ Data validation failed. Please check your file format.")
                    for error in validation_result['errors']:
                        st.error(f"• {error}")
                    
            except Exception as e:
                logger.error(f"Error reading uploaded file: {str(e)}")
                st.error(f"❌ Error reading file: {str(e)}")
                st.info("Please ensure your file is a valid CSV or Excel file and try again.")
    
    def _validate_amr_data(self, df: pd.DataFrame) -> Dict:
        """Validate AMR data format and content"""
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'summary': {}
        }
        
        try:
            # Check if empty
            if df.empty:
                validation['valid'] = False
                validation['errors'].append("File is empty")
                return validation
            
            # Check required columns
            required_columns = ['Organism']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                validation['valid'] = False
                validation['errors'].append(f"Missing required columns: {', '.join(missing_columns)}")
            
            # Check antimicrobial columns
            am_cols = [col for col in df.columns if any(x in col for x in ['_ND', '_NM']) and not col.endswith('_ND') and not col.endswith('_NM')]
            
            if not am_cols:
                validation['warnings'].append("No antimicrobial susceptibility columns found")
            else:
                validation['summary']['antimicrobial_count'] = len(am_cols)
            
            # Check data completeness
            if am_cols:
                completeness = (df[am_cols].notna().sum().sum() / (len(df) * len(am_cols))) * 100
                validation['summary']['completeness'] = round(completeness, 1)
                
                if completeness < 10:
                    validation['warnings'].append(f"Very low data completeness: {completeness:.1f}%")
                elif completeness < 30:
                    validation['warnings'].append(f"Low data completeness: {completeness:.1f}%")
            
            # Check organism diversity
            unique_orgs = df['Organism'].nunique()
            validation['summary']['organism_count'] = unique_orgs
            
            if unique_orgs < 5:
                validation['warnings'].append(f"Low organism diversity: {unique_orgs} unique organisms")
            
            validation['summary']['total_records'] = len(df)
            
        except Exception as e:
            validation['valid'] = False
            validation['errors'].append(f"Validation error: {str(e)}")
        
        return validation
    
    def _display_validation_summary(self, validation: Dict):
        """Display validation summary in an organized way"""
        with st.expander("📊 Data Validation Summary", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Records", validation['summary'].get('total_records', 0))
            
            with col2:
                st.metric("Organisms", validation['summary'].get('organism_count', 0))
            
            with col3:
                st.metric("Antimicrobials", validation['summary'].get('antimicrobial_count', 0))
            
            if 'completeness' in validation['summary']:
                st.metric("Data Completeness", f"{validation['summary']['completeness']}%")
            
            if validation['warnings']:
                st.warning("⚠️ Warnings:")
            for warning in validation['warnings']:
                st.write(f"• {warning}")
    
    def _display_ast_detection_results(self, detection_result: Dict):
        """Display AST data type detection results"""
        with st.expander("🔍 AST Data Type Detection", expanded=True):
            # Main detection info
            col1, col2, col3 = st.columns(3)
            
            with col1:
                data_type = detection_result.get('data_type', 'unknown')
                if data_type == 'interpreted':
                    st.metric("Data Type", "📊 Interpreted (R/S/I)", help="Data is already in interpreted format")
                elif data_type == 'breakpoint':
                    st.metric("Data Type", "📏 Breakpoints", help="Data contains raw breakpoints requiring CLSI interpretation")
                elif data_type == 'mixed':
                    st.metric("Data Type", "🔀 Mixed", help="Data contains both interpreted and breakpoint columns")
                else:
                    st.metric("Data Type", "❓ Unknown", help="Unable to determine data format")
            
            with col2:
                confidence = detection_result.get('confidence', 0)
                st.metric("Confidence", f"{confidence}%", help="Detection confidence level")
            
            with col3:
                columns_analyzed = detection_result.get('columns_analyzed', 0)
                st.metric("Columns Analyzed", columns_analyzed, help="Number of AST columns analyzed")
            
            # Detailed breakdown
            if detection_result.get('data_type') in ['interpreted', 'mixed']:
                interpreted_cols = detection_result.get('interpreted_columns', 0)
                st.info(f"📊 **Interpreted Columns**: {interpreted_cols}")
            
            if detection_result.get('data_type') in ['breakpoint', 'mixed']:
                breakpoint_cols = detection_result.get('breakpoint_columns', 0)
                st.info(f"📏 **Breakpoint Columns**: {breakpoint_cols}")
            
            # Recommendations
            st.subheader("💡 Recommendations")
            recommendations = detection_result.get('recommendations', [])
            for rec in recommendations:
                st.write(f"• {rec}")
            
            # Analysis method
            analysis_method = self.ast_detector.get_analysis_method(detection_result.get('data_type', 'unknown'))
            if analysis_method == 'direct_resistance_analysis':
                st.success("✅ **Analysis Method**: Direct resistance analysis (no CLSI interpretation needed)")
            elif analysis_method == 'clsi_interpretation_analysis':
                st.info("🧬 **Analysis Method**: CLSI breakpoint interpretation will be applied")
            elif analysis_method == 'hybrid_analysis':
                st.warning("🔀 **Analysis Method**: Mixed approach - some columns interpreted directly, others via CLSI")
            else:
                st.error("❌ **Analysis Method**: Manual review required")
    
    def _render_data_summary_header(self, df: pd.DataFrame):
        """Render professional data summary header with AST detection info"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Isolates", len(df))
        
        with col2:
            unique_orgs = df['Organism'].nunique()
            st.metric("Unique Organisms", unique_orgs)
        
        with col3:
            am_cols = [col for col in df.columns if any(x in col for x in ['_ND', '_NM']) and not col.endswith('_ND') and not col.endswith('_NM')]
            st.metric("Antimicrobials Tested", len(am_cols))
        
        with col4:
            if am_cols:
                completeness = (df[am_cols].notna().sum().sum() / (len(df) * len(am_cols))) * 100
                st.metric("Data Completeness", f"{completeness:.1f}%")
        
        # Show AST detection info if available
        if hasattr(st.session_state, 'ast_detection_result'):
            detection_result = st.session_state.ast_detection_result
            data_type = detection_result.get('data_type', 'unknown')
            confidence = detection_result.get('confidence', 0)
            
            st.info(f"🔍 **AST Data Type**: {data_type.upper()} (Confidence: {confidence}%)")
        
        st.markdown("---")
    
    def _render_enhanced_sidebar_controls(self, df: pd.DataFrame):
        """Render enhanced sidebar controls"""
        st.sidebar.header("🔧 Analysis Controls")
        
        # Analysis type selection
        analysis_types = [
            'Dashboard',
            'Antibiogram', 
            'Resistance Patterns',
            'Data Quality',
            'Export Reports'
        ]
        
        selected_analysis = st.sidebar.selectbox(
            "Analysis Type",
            options=analysis_types,
            index=0,
            help="Select the type of AMR analysis to perform"
        )
        
        st.session_state['amr_analysis_type'] = selected_analysis
        
        # Organism filter
        organisms = df['Organism'].unique() if 'Organism' in df.columns else []
        organisms = [org for org in organisms if pd.notna(org) and org != 'xxx']
        
        selected_organism = st.sidebar.selectbox(
            "Filter by Organism",
            options=['All Organisms'] + list(organisms),
            help="Choose specific organism or analyze all organisms"
        )
        
        st.session_state['selected_organism'] = selected_organism
        
        # Additional filters
        st.sidebar.markdown("---")
        st.sidebar.subheader("📊 Display Options")
        
        show_data_preview = st.sidebar.checkbox("Show Data Preview", value=False)
        st.session_state['show_data_preview'] = show_data_preview
        
        if show_data_preview:
            self._render_data_preview(df)
    
    def _render_data_preview(self, df: pd.DataFrame):
        """Render data preview in sidebar"""
        st.sidebar.markdown("---")
        st.sidebar.subheader("👀 Data Preview")
        
        # Show first few rows
        st.sidebar.dataframe(df.head(5), use_container_width=True)
        
        # Show organism distribution
        org_counts = df['Organism'].value_counts().head(5)
        st.sidebar.write("**Top Organisms:**")
        for org, count in org_counts.items():
            st.sidebar.write(f"• {org}: {count}")
    
    def _render_professional_dashboard(self, df: pd.DataFrame):
        """Render professional analysis dashboard"""
        st.header("📊 AMR Analysis Dashboard")
        
        # Data quality summary
        quality_summary = self.amr_analytics.create_data_quality_summary(df)
        
        if quality_summary:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Data Quality Score", f"{quality_summary.get('quality_score', 0)}%")
            
            with col2:
                st.metric("Overall Completeness", f"{quality_summary.get('overall_completeness', 0)}%")
            
            with col3:
                st.metric("Antimicrobial Coverage", f"{quality_summary.get('total_antimicrobials', 0)}")
        
        # Main dashboard visualization
        with st.spinner("Generating analysis dashboard..."):
            dashboard_fig = self.amr_analytics.create_resistance_summary_dashboard(df)
            
            if dashboard_fig:
                st.plotly_chart(dashboard_fig, use_container_width=True)
            else:
                st.warning("Unable to generate dashboard. Please check your data format.")
        
        # Organism distribution
        st.subheader("🦠 Organism Distribution")
        org_dist_fig = self.amr_analytics.create_organism_distribution_chart(df)
        
        if org_dist_fig:
            st.plotly_chart(org_dist_fig, use_container_width=True)
        
        # Download options
        self._render_enhanced_download_options(df, "dashboard")
    
    def _render_enhanced_antibiogram(self, df: pd.DataFrame):
        """Render enhanced antibiogram analysis"""
        st.header("🧪 Professional Antibiogram")
        
        selected_organism = st.session_state.get('selected_organism', 'All Organisms')
        
        with st.spinner("Generating professional antibiogram..."):
            antibiogram_fig = self.amr_analytics.create_professional_antibiogram(
                df, 
                selected_organism if selected_organism != 'All Organisms' else None
            )
            
            if antibiogram_fig:
                st.plotly_chart(antibiogram_fig, use_container_width=True)
                
                # Interpretation guide
                st.subheader("📖 Interpretation Guide")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info("""
                    **Resistance Rate Interpretation:**
                    - **0-20%**: Low resistance
                    - **21-40%**: Moderate resistance  
                    - **41-60%**: High resistance
                    - **61-80%**: Very high resistance
                    - **81-100%**: Extremely high resistance
                    """)
                
                with col2:
                    st.info("""
                    **Color Coding:**
                    - **Blue**: Low resistance (0-25%)
                    - **Yellow**: Moderate resistance (25-50%)
                    - **Orange**: High resistance (50-75%)
                    - **Red**: Very high resistance (75-100%)
                    """)
            else:
                st.warning("Unable to generate antibiogram. This may be due to insufficient data or missing antimicrobial columns.")
        
        # Download options
        self._render_enhanced_download_options(df, "antibiogram")
    
    def _render_resistance_patterns_analysis(self, df: pd.DataFrame):
        """Render resistance patterns analysis"""
        st.header("🛡️ Resistance Pattern Analysis")
        
        # Calculate resistance rates
        with st.spinner("Calculating resistance patterns..."):
            resistance_rates = self.amr_analytics.calculate_resistance_rates_enhanced(df)
        
        if resistance_rates.empty:
            st.warning("No resistance data available for analysis.")
            return
        
        # Summary statistics
        st.subheader("📈 Summary Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Average resistance by organism
            avg_resistance = resistance_rates.groupby('Organism')['Resistance_Rate_%'].mean().sort_values(ascending=False)
            st.write("**Average Resistance Rates by Organism:**")
            st.dataframe(
                avg_resistance.reset_index().rename(columns={'Resistance_Rate_%': 'Avg Resistance Rate (%)'}),
                width='stretch'
            )
        
        with col2:
            # Most resistant antimicrobials
            am_resistance = resistance_rates.groupby('Antimicrobial')['Resistance_Rate_%'].mean().sort_values(ascending=False)
            st.write("**Most Resistant Antimicrobials:**")
            st.dataframe(
                am_resistance.reset_index().rename(columns={'Resistance_Rate_%': 'Avg Resistance Rate (%)'}),
                width='stretch'
            )
        
        # Detailed resistance table with filters
        st.subheader("📋 Detailed Resistance Rates")
        
        # Add filters
        col1, col2 = st.columns(2)
        
        with col1:
            min_resistance = st.slider("Minimum Resistance Rate (%)", 0, 100, 0)
        
        with col2:
            min_tested = st.slider("Minimum Number Tested", 1, 100, 1)
        
        # Filter data
        filtered_rates = resistance_rates[
            (resistance_rates['Resistance_Rate_%'] >= min_resistance) &
            (resistance_rates['Total_Tested'] >= min_tested)
        ]
        
        st.dataframe(
            filtered_rates.sort_values('Resistance_Rate_%', ascending=False),
            width='stretch'
        )
        
        # Download options
        self._render_enhanced_download_options(df, "resistance_patterns")
    
    def _render_data_quality_analysis(self, df: pd.DataFrame):
        """Render data quality analysis"""
        st.header("🔍 Data Quality Analysis")
        
        quality_summary = self.amr_analytics.create_data_quality_summary(df)
        
        if not quality_summary:
            st.warning("Unable to generate data quality analysis.")
            return
        
        # Quality metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Overall Quality Score", f"{quality_summary.get('quality_score', 0)}%")
        
        with col2:
            st.metric("Data Completeness", f"{quality_summary.get('overall_completeness', 0)}%")
        
        with col3:
            st.metric("Antimicrobial Coverage", quality_summary.get('total_antimicrobials', 0))
        
        with col4:
            st.metric("Organism Diversity", quality_summary.get('unique_organisms', 0))
        
        # Data completeness by antimicrobial
        st.subheader("📊 Data Completeness by Antimicrobial")
        
        completeness_data = quality_summary.get('data_completeness', {})
        if completeness_data:
            completeness_df = pd.DataFrame([
                {'Antimicrobial': am, 'Completeness (%)': completeness}
                for am, completeness in completeness_data.items()
            ]).sort_values('Completeness (%)', ascending=True)
            
            fig = px.bar(
                completeness_df,
                x='Completeness (%)',
                y='Antimicrobial',
                orientation='h',
                title="Data Completeness by Antimicrobial",
                color='Completeness (%)',
                color_continuous_scale='RdYlGn'
            )
            
            fig.update_layout(height=max(400, len(completeness_df) * 25))
            st.plotly_chart(fig, use_container_width=True)
        
        # Organism distribution
        st.subheader("🦠 Organism Distribution")
        
        org_dist = quality_summary.get('organism_distribution', {})
        if org_dist:
            org_df = pd.DataFrame([
                {'Organism': org, 'Count': count}
                for org, count in org_dist.items()
            ])
            
            fig = px.pie(
                org_df,
                values='Count',
                names='Organism',
                title="Distribution of Isolates by Organism"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Quality recommendations
        st.subheader("💡 Quality Recommendations")
        
        recommendations = []
        
        if quality_summary.get('overall_completeness', 0) < 50:
            recommendations.append("Consider improving data collection to increase completeness")
        
        if quality_summary.get('unique_organisms', 0) < 10:
            recommendations.append("Include more diverse organism types for better analysis")
        
        if quality_summary.get('total_antimicrobials', 0) < 15:
            recommendations.append("Test against more antimicrobials for comprehensive analysis")
        
        if recommendations:
            for rec in recommendations:
                st.info(f"• {rec}")
        else:
            st.success("✅ Data quality is good for AMR analysis!")
    
    def _render_export_section(self, df: pd.DataFrame):
        """Render enhanced export section"""
        st.header("📥 Export Analysis Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Professional Charts")
            
            if st.button("Generate Professional Charts", type="primary"):
                with st.spinner("Generating professional charts..."):
                    charts = self.amr_analytics.export_professional_charts(df, format='png')
                    
                    if charts:
                        # Create zip file
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                            for chart_name, chart_data in charts.items():
                                zip_file.writestr(f"{chart_name}.png", chart_data)
                        
                        zip_buffer.seek(0)
                        
                        st.download_button(
                            label="📥 Download Professional Charts (ZIP)",
                            data=zip_buffer.getvalue(),
                            file_name=f"amr_professional_charts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                            mime="application/zip"
                        )
                        
                        st.success("Professional charts ready for download!")
                    else:
                        st.warning("No charts generated. Please check your data.")
        
        with col2:
            st.subheader("📋 Data Export")
            
            if st.button("Export Analysis Data", type="primary"):
                with st.spinner("Preparing data export..."):
                    # Generate resistance rates
                    resistance_rates = self.amr_analytics.calculate_resistance_rates_enhanced(df)
                    
                    # Create Excel file
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        resistance_rates.to_excel(writer, sheet_name='Resistance_Rates', index=False)
                        df.to_excel(writer, sheet_name='Raw_Data', index=False)
                        
                        # Add quality summary
                        quality_summary = self.amr_analytics.create_data_quality_summary(df)
                        if quality_summary:
                            quality_df = pd.DataFrame([quality_summary])
                            quality_df.to_excel(writer, sheet_name='Quality_Summary', index=False)
                    
                    output.seek(0)
                    
                    st.download_button(
                        label="📥 Download Analysis Data (Excel)",
                        data=output.getvalue(),
                        file_name=f"amr_analysis_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                    st.success("Analysis data ready for download!")
    
    def _render_enhanced_download_options(self, df: pd.DataFrame, analysis_type: str):
        """Render enhanced download options"""
        st.markdown("---")
        st.subheader("📥 Download Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Download Charts", key=f"download_charts_{analysis_type}"):
                self._download_professional_charts(df, analysis_type)
        
        with col2:
            if st.button("📋 Download Data", key=f"download_data_{analysis_type}"):
                self._download_analysis_data(df, analysis_type)
        
        with col3:
            if st.button("📄 Download Report", key=f"download_report_{analysis_type}"):
                self._download_analysis_report(df, analysis_type)
    
    def _download_professional_charts(self, df: pd.DataFrame, analysis_type: str):
        """Download professional charts"""
        try:
            charts = self.amr_analytics.export_professional_charts(df, format='png')
            
            if not charts:
                st.error("No charts available for download.")
                return
            
            # Create zip file
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for chart_name, chart_data in charts.items():
                    zip_file.writestr(f"{chart_name}_{analysis_type}.png", chart_data)
            
            zip_buffer.seek(0)
            
            st.download_button(
                label="📥 Download Professional Charts (ZIP)",
                data=zip_buffer.getvalue(),
                file_name=f"amr_professional_charts_{analysis_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip"
            )
            
            st.success("Professional charts ready for download!")
            
        except Exception as e:
            st.error(f"Error generating charts: {str(e)}")
    
    def _download_analysis_data(self, df: pd.DataFrame, analysis_type: str):
        """Download analysis data"""
        try:
            resistance_rates = self.amr_analytics.calculate_resistance_rates_enhanced(df)
            quality_summary = self.amr_analytics.create_data_quality_summary(df)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                resistance_rates.to_excel(writer, sheet_name='Resistance_Rates', index=False)
                df.to_excel(writer, sheet_name='Raw_Data', index=False)
                
                if quality_summary:
                    quality_df = pd.DataFrame([quality_summary])
                    quality_df.to_excel(writer, sheet_name='Quality_Summary', index=False)
            
            output.seek(0)
            
            st.download_button(
                label="📥 Download Analysis Data (Excel)",
                data=output.getvalue(),
                file_name=f"amr_analysis_data_{analysis_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.success("Analysis data ready for download!")
            
        except Exception as e:
            st.error(f"Error generating data file: {str(e)}")
    
    def _download_analysis_report(self, df: pd.DataFrame, analysis_type: str):
        """Download analysis report"""
        try:
            quality_summary = self.amr_analytics.create_data_quality_summary(df)
            
            report = []
            report.append("# Enhanced AMR Analysis Report")
            report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("")
            
            # Summary statistics
            report.append("## Summary Statistics")
            report.append(f"- Total isolates: {quality_summary.get('total_records', 0)}")
            report.append(f"- Unique organisms: {quality_summary.get('unique_organisms', 0)}")
            report.append(f"- Antimicrobials tested: {quality_summary.get('total_antimicrobials', 0)}")
            report.append(f"- Data completeness: {quality_summary.get('overall_completeness', 0)}%")
            report.append(f"- Quality score: {quality_summary.get('quality_score', 0)}%")
            report.append("")
            
            # Organism distribution
            org_dist = quality_summary.get('organism_distribution', {})
            if org_dist:
                report.append("## Organism Distribution")
                for org, count in list(org_dist.items())[:10]:
                    report.append(f"- {org}: {count}")
                report.append("")
            
            # Data completeness
            completeness = quality_summary.get('data_completeness', {})
            if completeness:
                report.append("## Data Completeness by Antimicrobial")
                for am, comp in sorted(completeness.items(), key=lambda x: x[1], reverse=True)[:10]:
                    report.append(f"- {am}: {comp}%")
                report.append("")
            
            report_text = "\n".join(report)
            
            st.download_button(
                label="📥 Download Analysis Report (TXT)",
                data=report_text.encode('utf-8'),
                file_name=f"amr_analysis_report_{analysis_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
            
            st.success("Analysis report ready for download!")
            
        except Exception as e:
            st.error(f"Error generating report: {str(e)}")
