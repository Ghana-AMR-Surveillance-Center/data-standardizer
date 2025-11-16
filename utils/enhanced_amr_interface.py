"""
Enhanced AMR Interface Module
Provides advanced controls and scientific reporting for antimicrobial resistance analysis
with confidence intervals, statistical validation, and comprehensive dashboards.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional, Tuple
import logging
import warnings
import io
from .enhanced_amr_analytics import EnhancedAMRAnalytics
from .user_feedback import user_feedback

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

class EnhancedAMRInterface:
    """
    Enhanced AMR interface with scientific rigor and advanced controls
    """
    
    def __init__(self):
        self.amr_analytics = EnhancedAMRAnalytics()
        self.data_format = None  # 'nd_nm' or 'rsi'
    
    def render_enhanced_amr_analysis_page(self):
        """Render the enhanced AMR analysis page with advanced controls"""
        st.title("🧬 Enhanced AMR Analytics")
        st.markdown("**Scientific Antimicrobial Resistance Analysis with Statistical Validation**")
        
        # Sidebar controls
        self._render_analysis_controls()
        
        # Main content
        if 'amr_data' not in st.session_state or st.session_state.amr_data is None:
            self._render_data_upload_section()
        else:
            self._render_analysis_dashboard()
    
    def _render_analysis_controls(self):
        """Render advanced analysis controls in sidebar"""
        st.sidebar.markdown("### 🔬 Analysis Controls")
        
        # Statistical parameters
        st.sidebar.markdown("#### Statistical Parameters")
        confidence_level = st.sidebar.slider(
            "Confidence Level (%)", 
            min_value=90, max_value=99, value=95, step=1,
            help="Confidence level for interval estimation"
        )
        
        min_sample_size = st.sidebar.slider(
            "Minimum Sample Size", 
            min_value=10, max_value=100, value=30, step=5,
            help="Minimum sample size for reliable analysis"
        )
        
        # Display options
        st.sidebar.markdown("#### Display Options")
        show_confidence_intervals = st.sidebar.checkbox(
            "Show Confidence Intervals", 
            value=True,
            help="Display confidence intervals on visualizations"
        )
        
        filter_reliable_only = st.sidebar.checkbox(
            "Show Reliable Results Only", 
            value=True,
            help="Filter out results with inadequate sample sizes"
        )
        
        show_power_analysis = st.sidebar.checkbox(
            "Show Power Analysis", 
            value=True,
            help="Display statistical power analysis results"
        )
        
        # Store settings in session state
        st.session_state.analysis_settings = {
            'confidence_level': confidence_level / 100,
            'min_sample_size': min_sample_size,
            'show_confidence_intervals': show_confidence_intervals,
            'filter_reliable_only': filter_reliable_only,
            'show_power_analysis': show_power_analysis
        }
    
    def _render_data_upload_section(self):
        """Render data upload section with format detection"""
        st.markdown("### 📤 Upload AMR Data")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose AMR data file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload data in ND/NM format (zone diameters/MICs) or R/S/I format"
        )
        
        if uploaded_file is not None:
            try:
                # Security validation first
                from utils.security import security_manager
                security_validation = security_manager.validate_file_upload(uploaded_file)
                
                if not security_validation['valid']:
                    for error in security_validation['errors']:
                        user_feedback.show_error(f"Security validation failed: {error}")
                        logger.warning(f"AMR file upload rejected: {uploaded_file.name} - {error}")
                    return
                
                if security_validation.get('warnings'):
                    for warning in security_validation['warnings']:
                        st.warning(f"⚠️ {warning}")
                        logger.info(f"AMR file upload warning: {uploaded_file.name} - {warning}")
                
                # Read file
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file, low_memory=False)
                else:
                    df = pd.read_excel(uploaded_file)
                
                # Detect data format
                self.data_format = self._detect_data_format(df)
                
                # Validate data
                validation_result = self._validate_amr_data(df)
                
                if validation_result['valid']:
                    # Store data
                    st.session_state.amr_data = df
                    st.session_state.data_format = self.data_format
                    st.session_state.validation_result = validation_result
                    
                    # Show success message
                    user_feedback.show_success(f"Successfully uploaded {len(df)} rows with {len(df.columns)} columns")
                    
                    # Display data summary
                    self._display_data_summary(df, validation_result)
                    
                    st.rerun()
                else:
                    user_feedback.show_error("Data validation failed. Please check your data format.")
                    st.error("Validation errors:")
                    for error in validation_result['errors']:
                        st.error(f"• {error}")
                        
            except Exception as e:
                user_feedback.show_error(f"Error reading file: {str(e)}")
                logger.error(f"Error reading uploaded file: {str(e)}")
    
    def _detect_data_format(self, df: pd.DataFrame) -> str:
        """Detect whether data is in ND/NM or R/S/I format"""
        # Check for ND/NM columns
        nd_cols = [col for col in df.columns if '_ND' in col]
        nm_cols = [col for col in df.columns if '_NM' in col]
        
        if nd_cols or nm_cols:
            return 'nd_nm'
        
        # Check for R/S/I columns
        rsi_indicators = ['_R', '_S', '_I', 'RESISTANT', 'SUSCEPTIBLE', 'INTERMEDIATE']
        rsi_cols = [col for col in df.columns if any(indicator in col.upper() for indicator in rsi_indicators)]
        
        if rsi_cols:
            return 'rsi'
        
        return 'unknown'
    
    def _validate_amr_data(self, df: pd.DataFrame) -> Dict:
        """Validate AMR data format and completeness"""
        errors = []
        warnings = []
        
        # Check for required columns
        if 'Organism' not in df.columns:
            errors.append("Missing 'Organism' column")
        
        # Check data format
        if self.data_format == 'nd_nm':
            nd_cols = [col for col in df.columns if '_ND' in col]
            nm_cols = [col for col in df.columns if '_NM' in col]
            
            if not nd_cols and not nm_cols:
                errors.append("No ND/NM columns found in ND/NM format data")
            else:
                warnings.append(f"Found {len(nd_cols)} ND columns and {len(nm_cols)} NM columns")
        
        elif self.data_format == 'rsi':
            rsi_indicators = ['_R', '_S', '_I', 'RESISTANT', 'SUSCEPTIBLE', 'INTERMEDIATE']
            rsi_cols = [col for col in df.columns if any(indicator in col.upper() for indicator in rsi_indicators)]
            
            if not rsi_cols:
                errors.append("No R/S/I columns found in R/S/I format data")
            else:
                warnings.append(f"Found {len(rsi_cols)} R/S/I columns")
        
        # Check organism data quality
        if 'Organism' in df.columns:
            organism_counts = df['Organism'].value_counts()
            valid_organisms = organism_counts[~organism_counts.index.isin(['xxx', 'nan', '', 'no growth', 'not applicable'])]
            
            if len(valid_organisms) == 0:
                errors.append("No valid organisms found (all are xxx, nan, or no growth)")
            else:
                warnings.append(f"Found {len(valid_organisms)} valid organisms")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'format': self.data_format
        }
    
    def _display_data_summary(self, df: pd.DataFrame, validation_result: Dict):
        """Display data summary and validation results"""
        with st.expander("📊 Data Summary", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Rows", len(df))
            with col2:
                st.metric("Total Columns", len(df.columns))
            with col3:
                st.metric("Data Format", validation_result['format'].upper())
            
            # Show warnings if any
            if validation_result['warnings']:
                for warning in validation_result['warnings']:
                    st.info(f"ℹ️ {warning}")
            
            # Show sample data
            st.markdown("**Sample Data:**")
            st.dataframe(df.head(), width='stretch')
    
    def _render_analysis_dashboard(self):
        """Render the main analysis dashboard"""
        df = st.session_state.amr_data
        settings = st.session_state.analysis_settings
        
        # Calculate enhanced resistance rates
        with st.spinner("🔬 Calculating resistance rates with statistical validation..."):
            resistance_rates = self.amr_analytics.calculate_enhanced_resistance_rates(
                df, 
                confidence_level=settings['confidence_level'],
                min_sample_size=settings['min_sample_size']
            )
        
        if resistance_rates.empty:
            user_feedback.show_warning("No resistance rates could be calculated. Please check your data.")
            return
        
        # Store results
        st.session_state.resistance_rates = resistance_rates
        
        # Analysis tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview", "🔬 Statistical Analysis", "📈 Visualizations", 
            "📋 Detailed Results", "📄 Scientific Report"
        ])
        
        with tab1:
            self._render_overview_tab(resistance_rates)
        
        with tab2:
            self._render_statistical_analysis_tab(resistance_rates)
        
        with tab3:
            self._render_visualizations_tab(resistance_rates, settings)
        
        with tab4:
            self._render_detailed_results_tab(resistance_rates, settings)
        
        with tab5:
            self._render_scientific_report_tab(resistance_rates)
    
    def _render_overview_tab(self, resistance_rates: pd.DataFrame):
        """Render overview tab with key metrics"""
        st.header("📊 Analysis Overview")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_analyses = len(resistance_rates)
            st.metric("Total Analyses", total_analyses)
        
        with col2:
            reliable_analyses = len(resistance_rates[resistance_rates['Sample_Size_Adequate'] == True])
            reliability_pct = (reliable_analyses / total_analyses) * 100 if total_analyses > 0 else 0
            st.metric("Reliable Analyses", f"{reliable_analyses} ({reliability_pct:.1f}%)")
        
        with col3:
            avg_sample_size = resistance_rates['Total_Tested'].mean()
            st.metric("Avg Sample Size", f"{avg_sample_size:.1f}")
        
        with col4:
            avg_power = resistance_rates['Power'].mean()
            st.metric("Avg Statistical Power", f"{avg_power:.3f}")
        
        # Summary statistics
        st.subheader("📈 Resistance Rate Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            resistance_stats = resistance_rates['Resistance_Rate_%'].describe()
            st.dataframe(resistance_stats.to_frame('Resistance Rate (%)'), width='stretch')
        
        with col2:
            # Histogram of resistance rates
            fig = px.histogram(
                resistance_rates, 
                x='Resistance_Rate_%', 
                nbins=20,
                title="Distribution of Resistance Rates",
                labels={'Resistance_Rate_%': 'Resistance Rate (%)', 'count': 'Frequency'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Top organisms and antimicrobials
        st.subheader("🔬 Data Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            organism_counts = resistance_rates['Organism'].value_counts().head(10)
            st.markdown("**Top Organisms:**")
            st.dataframe(organism_counts.to_frame('Analyses'), width='stretch')
        
        with col2:
            am_counts = resistance_rates['Antimicrobial'].value_counts().head(10)
            st.markdown("**Top Antimicrobials:**")
            st.dataframe(am_counts.to_frame('Analyses'), width='stretch')
    
    def _render_statistical_analysis_tab(self, resistance_rates: pd.DataFrame):
        """Render statistical analysis tab"""
        st.header("🔬 Statistical Analysis")
        
        # Statistical summary dashboard
        st.subheader("📊 Statistical Summary Dashboard")
        dashboard_fig = self.amr_analytics.create_statistical_summary_dashboard(resistance_rates)
        if dashboard_fig:
            st.plotly_chart(dashboard_fig, use_container_width=True)
        else:
            st.warning("Unable to generate statistical summary dashboard")
        
        # Sample size analysis
        st.subheader("📏 Sample Size Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Sample size distribution
            fig = px.box(
                resistance_rates, 
                y='Total_Tested',
                title="Sample Size Distribution",
                labels={'Total_Tested': 'Sample Size'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Reliability by sample size
            reliability_by_size = resistance_rates.groupby(
                pd.cut(resistance_rates['Total_Tested'], bins=5)
            )['Sample_Size_Adequate'].mean()
            
            fig = px.bar(
                x=reliability_by_size.index.astype(str),
                y=reliability_by_size.values,
                title="Reliability by Sample Size Range",
                labels={'x': 'Sample Size Range', 'y': 'Reliability Rate'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Confidence interval analysis
        st.subheader("📐 Confidence Interval Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CI width distribution
            fig = px.histogram(
                resistance_rates,
                x='CI_Width_%',
                nbins=20,
                title="Confidence Interval Width Distribution",
                labels={'CI_Width_%': 'CI Width (%)', 'count': 'Frequency'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # CI width vs sample size
            fig = px.scatter(
                resistance_rates,
                x='Total_Tested',
                y='CI_Width_%',
                color='Sample_Size_Adequate',
                title="CI Width vs Sample Size",
                labels={'Total_Tested': 'Sample Size', 'CI_Width_%': 'CI Width (%)'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_visualizations_tab(self, resistance_rates: pd.DataFrame, settings: Dict):
        """Render visualizations tab"""
        st.header("📈 Advanced Visualizations")
        
        # Enhanced antibiogram
        st.subheader("🧬 Enhanced Antibiogram")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            antibiogram_fig = self.amr_analytics.create_enhanced_antibiogram(
                resistance_rates,
                show_confidence_intervals=settings['show_confidence_intervals'],
                filter_reliable_only=settings['filter_reliable_only']
            )
            
            if antibiogram_fig:
                st.plotly_chart(antibiogram_fig, use_container_width=True)
            else:
                st.warning("Unable to generate antibiogram")
        
        with col2:
            st.markdown("**Legend:**")
            st.markdown("• **Blue**: Low resistance (0-25%)")
            st.markdown("• **Yellow**: Moderate resistance (25-50%)")
            st.markdown("• **Orange**: High resistance (50-75%)")
            st.markdown("• **Red**: Very high resistance (75-100%)")
            
            if settings['show_confidence_intervals']:
                st.markdown("• **±X%**: Wide confidence interval")
        
        # Additional visualizations
        st.subheader("📊 Additional Analyses")
        
        # Organism resistance patterns
        organism_resistance = resistance_rates.groupby('Organism')['Resistance_Rate_%'].mean().sort_values(ascending=True)
        
        fig = px.bar(
            x=organism_resistance.values,
            y=organism_resistance.index,
            orientation='h',
            title="Average Resistance Rate by Organism",
            labels={'x': 'Average Resistance Rate (%)', 'y': 'Organism'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Antimicrobial resistance patterns
        am_resistance = resistance_rates.groupby('Antimicrobial')['Resistance_Rate_%'].mean().sort_values(ascending=True)
        
        fig = px.bar(
            x=am_resistance.values,
            y=am_resistance.index,
            orientation='h',
            title="Average Resistance Rate by Antimicrobial",
            labels={'x': 'Average Resistance Rate (%)', 'y': 'Antimicrobial'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_detailed_results_tab(self, resistance_rates: pd.DataFrame, settings: Dict):
        """Render detailed results tab"""
        st.header("📋 Detailed Analysis Results")
        
        # Filters
        st.subheader("🔍 Filter Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            organisms = ['All'] + sorted(resistance_rates['Organism'].unique().tolist())
            selected_organism = st.selectbox("Filter by Organism", organisms)
        
        with col2:
            antimicrobials = ['All'] + sorted(resistance_rates['Antimicrobial'].unique().tolist())
            selected_antimicrobial = st.selectbox("Filter by Antimicrobial", antimicrobials)
        
        with col3:
            min_resistance = st.slider("Minimum Resistance Rate (%)", 0, 100, 0)
        
        # Apply filters
        filtered_data = resistance_rates.copy()
        
        if selected_organism != 'All':
            filtered_data = filtered_data[filtered_data['Organism'] == selected_organism]
        
        if selected_antimicrobial != 'All':
            filtered_data = filtered_data[filtered_data['Antimicrobial'] == selected_antimicrobial]
        
        filtered_data = filtered_data[filtered_data['Resistance_Rate_%'] >= min_resistance]
        
        if settings['filter_reliable_only']:
            filtered_data = filtered_data[filtered_data['Sample_Size_Adequate'] == True]
        
        # Display results
        st.subheader(f"📊 Filtered Results ({len(filtered_data)} analyses)")
        
        if not filtered_data.empty:
            # Summary statistics for filtered data
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Analyses", len(filtered_data))
            with col2:
                avg_resistance = filtered_data['Resistance_Rate_%'].mean()
                st.metric("Avg Resistance Rate", f"{avg_resistance:.1f}%")
            with col3:
                avg_ci_width = filtered_data['CI_Width_%'].mean()
                st.metric("Avg CI Width", f"{avg_ci_width:.1f}%")
            with col4:
                reliable_pct = (filtered_data['Sample_Size_Adequate'].sum() / len(filtered_data)) * 100
                st.metric("Reliability", f"{reliable_pct:.1f}%")
            
            # Detailed table
            display_columns = [
                'Organism', 'Antimicrobial', 'Test_Type', 'Total_Tested',
                'Resistant', 'Susceptible', 'Resistance_Rate_%',
                'CI_Lower_%', 'CI_Upper_%', 'CI_Width_%',
                'Sample_Size_Adequate', 'Power', 'Recommendation'
            ]
            
            st.dataframe(
                filtered_data[display_columns].sort_values('Resistance_Rate_%', ascending=False),
                width='stretch',
                height=400
            )
            
            # Download options
            st.subheader("💾 Download Results")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                csv_data = filtered_data.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv_data,
                    "enhanced_amr_results.csv",
                    "text/csv"
                )
            
            with col2:
                # Create Excel data using BytesIO
                import io
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    filtered_data.to_excel(writer, index=False, sheet_name='AMR_Results')
                excel_data = excel_buffer.getvalue()
                
                st.download_button(
                    "Download Excel",
                    excel_data,
                    "enhanced_amr_results.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            with col3:
                if st.button("📊 Generate Report PDF"):
                    st.info("PDF generation feature coming soon!")
        else:
            st.warning("No results match the selected filters")
    
    def _render_scientific_report_tab(self, resistance_rates: pd.DataFrame):
        """Render scientific report tab"""
        st.header("📄 Scientific Report")
        
        # Generate report
        with st.spinner("🔬 Generating scientific report..."):
            report = self.amr_analytics.generate_scientific_report(resistance_rates)
        
        if 'error' in report:
            st.error(f"Error generating report: {report['error']}")
            return
        
        # Report sections
        st.subheader("📋 Executive Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Total Analyses:** {report['summary_statistics']['total_analyses']}")
            st.markdown(f"**Reliable Analyses:** {report['summary_statistics']['reliable_analyses']} ({report['summary_statistics']['reliability_percentage']:.1f}%)")
            st.markdown(f"**Average Sample Size:** {report['summary_statistics']['average_sample_size']}")
        
        with col2:
            st.markdown(f"**Average CI Width:** {report['summary_statistics']['average_ci_width']}%")
            st.markdown(f"**Average Power:** {report['summary_statistics']['average_power']}")
            st.markdown(f"**High Power Analyses:** {report['quality_assessment']['high_power_analyses']}")
        
        # Methodology
        st.subheader("🔬 Methodology")
        
        methodology = report['methodology']
        st.markdown(f"**Confidence Level:** {methodology['confidence_level']}")
        st.markdown(f"**Minimum Sample Size:** {methodology['minimum_sample_size']}")
        st.markdown(f"**Statistical Method:** {methodology['statistical_method']}")
        st.markdown(f"**Power Analysis:** {methodology['power_analysis']}")
        st.markdown(f"**Data Validation:** {methodology['data_validation']}")
        
        # Data distribution
        st.subheader("📊 Data Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Top Organisms:**")
            for org, count in list(report['data_distribution']['top_organisms'].items())[:5]:
                st.markdown(f"• {org}: {count} analyses")
        
        with col2:
            st.markdown("**Top Antimicrobials:**")
            for am, count in list(report['data_distribution']['top_antimicrobials'].items())[:5]:
                st.markdown(f"• {am}: {count} analyses")
        
        # Quality assessment
        st.subheader("✅ Quality Assessment")
        
        quality = report['quality_assessment']
        st.markdown(f"**Reliable Analyses:** {quality['reliable_analyses_percentage']:.1f}%")
        st.markdown(f"**Average Sample Size:** {quality['average_sample_size']:.1f}")
        st.markdown(f"**Average CI Width:** {quality['average_ci_width']:.1f}%")
        st.markdown(f"**Average Power:** {quality['average_power']:.3f}")
        st.markdown(f"**High Power Analyses:** {quality['high_power_analyses']}")
        
        # Recommendations
        st.subheader("💡 Recommendations")
        
        for i, recommendation in enumerate(report['recommendations'], 1):
            st.markdown(f"{i}. {recommendation}")
        
        # Download report
        st.subheader("💾 Download Report")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Download Text Report"):
                report_text = self._format_report_as_text(report)
                st.download_button(
                    "Download Text Report",
                    report_text,
                    "amr_scientific_report.txt",
                    "text/plain"
                )
        
        with col2:
            if st.button("📊 Download Data Summary"):
                summary_data = pd.DataFrame([
                    {'Metric': 'Total Analyses', 'Value': report['summary_statistics']['total_analyses']},
                    {'Metric': 'Reliable Analyses', 'Value': report['summary_statistics']['reliable_analyses']},
                    {'Metric': 'Reliability %', 'Value': f"{report['summary_statistics']['reliability_percentage']:.1f}%"},
                    {'Metric': 'Avg Sample Size', 'Value': f"{report['summary_statistics']['average_sample_size']:.1f}"},
                    {'Metric': 'Avg CI Width', 'Value': f"{report['summary_statistics']['average_ci_width']:.1f}%"},
                    {'Metric': 'Avg Power', 'Value': f"{report['summary_statistics']['average_power']:.3f}"}
                ])
                csv_data = summary_data.to_csv(index=False)
                st.download_button(
                    "Download Summary CSV",
                    csv_data,
                    "amr_summary.csv",
                    "text/csv"
                )
    
    def _format_report_as_text(self, report: Dict) -> str:
        """Format report as plain text"""
        text = "ENHANCED AMR ANALYSIS SCIENTIFIC REPORT\n"
        text += "=" * 50 + "\n\n"
        
        # Executive Summary
        text += "EXECUTIVE SUMMARY\n"
        text += "-" * 20 + "\n"
        summary = report['summary_statistics']
        text += f"Total Analyses: {summary['total_analyses']}\n"
        text += f"Reliable Analyses: {summary['reliable_analyses']} ({summary['reliability_percentage']:.1f}%)\n"
        text += f"Average Sample Size: {summary['average_sample_size']}\n"
        text += f"Average CI Width: {summary['average_ci_width']}%\n"
        text += f"Average Power: {summary['average_power']}\n\n"
        
        # Methodology
        text += "METHODOLOGY\n"
        text += "-" * 15 + "\n"
        methodology = report['methodology']
        text += f"Confidence Level: {methodology['confidence_level']}\n"
        text += f"Minimum Sample Size: {methodology['minimum_sample_size']}\n"
        text += f"Statistical Method: {methodology['statistical_method']}\n"
        text += f"Power Analysis: {methodology['power_analysis']}\n"
        text += f"Data Validation: {methodology['data_validation']}\n\n"
        
        # Recommendations
        text += "RECOMMENDATIONS\n"
        text += "-" * 20 + "\n"
        for i, rec in enumerate(report['recommendations'], 1):
            text += f"{i}. {rec}\n"
        
        return text
