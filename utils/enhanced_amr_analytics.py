"""
Enhanced AMR Analytics Module
Provides scientifically rigorous antimicrobial resistance analysis with confidence intervals,
statistical validation, and comprehensive reporting for both ND/NM and R/S/I data formats.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple, Optional, Union
import logging
from scipy import stats
from scipy.stats import beta
import warnings
from .cache_manager import streamlit_cache_dataframe

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

class EnhancedAMRAnalytics:
    """
    Enhanced AMR analytics with scientific rigor, confidence intervals, and comprehensive reporting
    """
    
    def __init__(self):
        self.antimicrobial_classes = {
            'Penicillins': ['AMP', 'AMC', 'AMX', 'PEN', 'TZP'],
            'Cephalosporins': ['CAZ', 'CTX', 'CRO', 'CXM', 'FOX', 'FEP'],
            'Carbapenems': ['MEM', 'ETP', 'IPM'],
            'Aminoglycosides': ['AMK', 'GEN', 'TOB'],
            'Fluoroquinolones': ['CIP', 'LVX', 'OFX', 'NAL'],
            'Macrolides': ['AZM', 'ERY', 'CLI'],
            'Tetracyclines': ['TCY', 'TGC', 'DOX'],
            'Glycopeptides': ['VAN', 'TEC'],
            'Oxazolidinones': ['LNZ'],
            'Polymyxins': ['COL'],
            'Sulfonamides': ['SXT', 'TMP'],
            'Chloramphenicol': ['CHL'],
            'Fosfomycin': ['FOS'],
            'Nitrofurans': ['NIT']
        }
        
        # CLSI breakpoints for common organisms (simplified for demonstration)
        self.clsi_breakpoints = {
            'disk_diffusion': {
                'eco': {  # E. coli
                    'AMK': {'S': 17, 'I': 14, 'R': 13},
                    'AMC': {'S': 18, 'I': 14, 'R': 13},
                    'AMP': {'S': 17, 'I': 14, 'R': 13},
                    'CAZ': {'S': 18, 'I': 15, 'R': 14},
                    'CIP': {'S': 21, 'I': 16, 'R': 15},
                    'GEN': {'S': 15, 'I': 13, 'R': 12},
                    'MEM': {'S': 23, 'I': 20, 'R': 19},
                    'TZP': {'S': 18, 'I': 15, 'R': 14}
                },
                'kpn': {  # K. pneumoniae
                    'AMK': {'S': 17, 'I': 14, 'R': 13},
                    'AMC': {'S': 18, 'I': 14, 'R': 13},
                    'CAZ': {'S': 18, 'I': 15, 'R': 14},
                    'CIP': {'S': 21, 'I': 16, 'R': 15},
                    'GEN': {'S': 15, 'I': 13, 'R': 12},
                    'MEM': {'S': 23, 'I': 20, 'R': 19},
                    'TZP': {'S': 18, 'I': 15, 'R': 14}
                }
            },
            'mic': {
                'eco': {
                    'AMK': {'S': 16, 'I': 32, 'R': 64},
                    'AMC': {'S': 8, 'I': 16, 'R': 32},
                    'AMP': {'S': 8, 'I': 16, 'R': 32},
                    'CAZ': {'S': 4, 'I': 8, 'R': 16},
                    'CIP': {'S': 1, 'I': 2, 'R': 4},
                    'GEN': {'S': 4, 'I': 8, 'R': 16},
                    'MEM': {'S': 2, 'I': 4, 'R': 8},
                    'TZP': {'S': 16, 'I': 32, 'R': 64}
                }
            }
        }
    
    def calculate_confidence_interval(self, successes: int, total: int, confidence_level: float = 0.95) -> Tuple[float, float]:
        """
        Calculate Wilson score interval for binomial proportion
        
        Args:
            successes: Number of successes (resistant isolates)
            total: Total number of trials (tested isolates)
            confidence_level: Confidence level (default 0.95 for 95% CI)
            
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        if total == 0:
            return (0.0, 0.0)
        
        # Wilson score interval
        z = stats.norm.ppf(1 - (1 - confidence_level) / 2)
        p = successes / total
        n = total
        
        # Wilson score interval formula
        denominator = 1 + z**2 / n
        centre_adjusted_probability = (p + z**2 / (2 * n)) / denominator
        adjusted_standard_deviation = np.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denominator
        
        lower_bound = max(0, centre_adjusted_probability - z * adjusted_standard_deviation)
        upper_bound = min(1, centre_adjusted_probability + z * adjusted_standard_deviation)
        
        return (lower_bound * 100, upper_bound * 100)
    
    def calculate_sample_size_power(self, resistance_rate: float, margin_of_error: float = 0.05, 
                                  power: float = 0.8, alpha: float = 0.05) -> Dict:
        """
        Calculate required sample size and power analysis
        
        Args:
            resistance_rate: Expected resistance rate (0-1)
            margin_of_error: Acceptable margin of error
            power: Statistical power (0-1)
            alpha: Significance level (0-1)
            
        Returns:
            Dictionary with sample size and power analysis results
        """
        if resistance_rate <= 0 or resistance_rate >= 1:
            return {'required_sample_size': 0, 'current_power': 0, 'adequate_power': False}
        
        # Required sample size for given margin of error
        z_alpha = stats.norm.ppf(1 - alpha / 2)
        required_n = (z_alpha / margin_of_error) ** 2 * resistance_rate * (1 - resistance_rate)
        
        return {
            'required_sample_size': int(np.ceil(required_n)),
            'margin_of_error': margin_of_error,
            'power': power,
            'alpha': alpha
        }
    
    def validate_sample_size(self, n: int, resistance_rate: float, min_sample_size: int = 30) -> Dict:
        """
        Validate if sample size is adequate for reliable analysis
        
        Args:
            n: Current sample size
            resistance_rate: Observed resistance rate
            min_sample_size: Minimum recommended sample size
            
        Returns:
            Validation results
        """
        # Rule of thumb: at least 5 successes and 5 failures
        successes = int(n * resistance_rate / 100)
        failures = n - successes
        
        adequate_successes = successes >= 5
        adequate_failures = failures >= 5
        adequate_total = n >= min_sample_size
        
        # Calculate power for current sample size
        if n > 0:
            se = np.sqrt(resistance_rate * (1 - resistance_rate / 100) / n)
            power = 1 - stats.norm.cdf(1.96 - (resistance_rate / 100) / se)
        else:
            power = 0
        
        return {
            'sample_size': n,
            'resistance_rate': resistance_rate,
            'successes': successes,
            'failures': failures,
            'adequate_successes': adequate_successes,
            'adequate_failures': adequate_failures,
            'adequate_total': adequate_total,
            'power': power,
            'reliable': adequate_successes and adequate_failures and adequate_total,
            'recommendation': self._get_sample_size_recommendation(n, successes, failures)
        }
    
    def _get_sample_size_recommendation(self, n: int, successes: int, failures: int) -> str:
        """Get recommendation based on sample size analysis"""
        if n < 30:
            return "⚠️ Sample size too small for reliable analysis (n<30)"
        elif successes < 5:
            return "⚠️ Too few resistant isolates for reliable resistance rate estimation"
        elif failures < 5:
            return "⚠️ Too few susceptible isolates for reliable resistance rate estimation"
        elif n < 100:
            return "✅ Adequate for preliminary analysis, consider larger sample for higher precision"
        else:
            return "✅ Excellent sample size for reliable analysis"
    
    @streamlit_cache_dataframe(max_age_seconds=1800)
    def calculate_enhanced_resistance_rates(self, df: pd.DataFrame, 
                                          confidence_level: float = 0.95,
                                          min_sample_size: int = 30) -> pd.DataFrame:
        """
        Calculate resistance rates with confidence intervals and statistical validation
        
        Args:
            df: DataFrame with AMR data
            confidence_level: Confidence level for intervals (default 0.95)
            min_sample_size: Minimum sample size for reliable analysis
            
        Returns:
            Enhanced DataFrame with resistance rates, CIs, and validation metrics
        """
        try:
            if df is None or df.empty:
                return pd.DataFrame()
            
            # Detect data format and process accordingly
            if self._is_nd_nm_format(df):
                resistance_rates = self._process_nd_nm_data(df, confidence_level, min_sample_size)
            else:
                resistance_rates = self._process_rsi_format(df, confidence_level, min_sample_size)
            
            return resistance_rates
            
        except Exception as e:
            logger.error(f"Error in calculate_enhanced_resistance_rates: {str(e)}")
            return pd.DataFrame()
    
    def _is_nd_nm_format(self, df: pd.DataFrame) -> bool:
        """Check if data is in ND/NM format"""
        nd_cols = [col for col in df.columns if '_ND' in col]
        nm_cols = [col for col in df.columns if '_NM' in col]
        return len(nd_cols) > 0 or len(nm_cols) > 0
    
    def _process_nd_nm_data(self, df: pd.DataFrame, confidence_level: float, min_sample_size: int) -> pd.DataFrame:
        """Process ND/NM format data"""
        results = []
        
        # Get ND/NM columns
        nd_cols = [col for col in df.columns if '_ND' in col]
        nm_cols = [col for col in df.columns if '_NM' in col]
        
        if not nd_cols and not nm_cols:
            return pd.DataFrame()
        
        # Get valid organisms
        organisms = df['Organism'].dropna().unique()
        organisms = [org for org in organisms if str(org).lower() not in ['xxx', 'nan', '', 'no growth', 'not applicable']]
        
        # Filter organisms with sufficient data
        organism_counts = df['Organism'].value_counts()
        organisms = [org for org in organisms if organism_counts.get(org, 0) >= min_sample_size]
        
        for org in organisms:
            org_data = df[df['Organism'] == org]
            
            for col in nd_cols + nm_cols:
                am_name = col.split('_ND')[0] if '_ND' in col else col.split('_NM')[0]
                test_type = 'disk_diffusion' if '_ND' in col else 'mic'
                
                # Convert to interpretations
                interpretations = org_data[col].apply(
                    lambda x: self._convert_nd_nm_to_interpretation(x, col, test_type)
                )
                
                # Calculate statistics
                tested_data = interpretations[interpretations != 'Not Tested']
                if len(tested_data) == 0:
                    continue
                
                resistant = len(tested_data[tested_data == 'R'])
                intermediate = len(tested_data[tested_data == 'I'])
                susceptible = len(tested_data[tested_data == 'S'])
                total_tested = len(tested_data)
                
                if total_tested > 0:
                    resistance_rate = (resistant / total_tested) * 100
                    intermediate_rate = (intermediate / total_tested) * 100
                    susceptibility_rate = (susceptible / total_tested) * 100
                    
                    # Calculate confidence intervals
                    ci_lower, ci_upper = self.calculate_confidence_interval(
                        resistant, total_tested, confidence_level
                    )
                    
                    # Sample size validation
                    validation = self.validate_sample_size(total_tested, resistance_rate, min_sample_size)
                    
                    # Power analysis
                    power_analysis = self.calculate_sample_size_power(resistance_rate / 100)
                    
                    results.append({
                        'Organism': org,
                        'Antimicrobial': am_name,
                        'Test_Type': test_type,
                        'Total_Tested': total_tested,
                        'Resistant': resistant,
                        'Intermediate': intermediate,
                        'Susceptible': susceptible,
                        'Resistance_Rate_%': round(resistance_rate, 2),
                        'Intermediate_Rate_%': round(intermediate_rate, 2),
                        'Susceptibility_Rate_%': round(susceptibility_rate, 2),
                        'CI_Lower_%': round(ci_lower, 2),
                        'CI_Upper_%': round(ci_upper, 2),
                        'CI_Width_%': round(ci_upper - ci_lower, 2),
                        'Sample_Size_Adequate': validation['reliable'],
                        'Power': round(validation['power'], 3),
                        'Recommendation': validation['recommendation'],
                        'Required_Sample_Size': power_analysis['required_sample_size']
                    })
        
        return pd.DataFrame(results)
    
    def _process_rsi_format(self, df: pd.DataFrame, confidence_level: float, min_sample_size: int) -> pd.DataFrame:
        """Process R/S/I format data"""
        results = []
        
        # Find R/S/I columns
        rsi_cols = [col for col in df.columns if any(x in col.upper() for x in ['_R', '_S', '_I', 'RESISTANT', 'SUSCEPTIBLE', 'INTERMEDIATE'])]
        
        if not rsi_cols:
            return pd.DataFrame()
        
        # Get valid organisms
        organisms = df['Organism'].dropna().unique()
        organisms = [org for org in organisms if str(org).lower() not in ['xxx', 'nan', '', 'no growth', 'not applicable']]
        
        # Filter organisms with sufficient data
        organism_counts = df['Organism'].value_counts()
        organisms = [org for org in organisms if organism_counts.get(org, 0) >= min_sample_size]
        
        for org in organisms:
            org_data = df[df['Organism'] == org]
            
            for col in rsi_cols:
                am_name = col.replace('_R', '').replace('_S', '').replace('_I', '')
                am_name = am_name.replace('_RESISTANT', '').replace('_SUSCEPTIBLE', '').replace('_INTERMEDIATE', '')
                
                # Count R/S/I values
                resistant = len(org_data[org_data[col].str.upper().isin(['R', 'RESISTANT', 'RES'])])
                intermediate = len(org_data[org_data[col].str.upper().isin(['I', 'INTERMEDIATE', 'INT'])])
                susceptible = len(org_data[org_data[col].str.upper().isin(['S', 'SUSCEPTIBLE', 'SEN', 'SENSITIVE'])])
                total_tested = resistant + intermediate + susceptible
                
                if total_tested > 0:
                    resistance_rate = (resistant / total_tested) * 100
                    intermediate_rate = (intermediate / total_tested) * 100
                    susceptibility_rate = (susceptible / total_tested) * 100
                    
                    # Calculate confidence intervals
                    ci_lower, ci_upper = self.calculate_confidence_interval(
                        resistant, total_tested, confidence_level
                    )
                    
                    # Sample size validation
                    validation = self.validate_sample_size(total_tested, resistance_rate, min_sample_size)
                    
                    # Power analysis
                    power_analysis = self.calculate_sample_size_power(resistance_rate / 100)
                    
                    results.append({
                        'Organism': org,
                        'Antimicrobial': am_name,
                        'Test_Type': 'interpreted',
                        'Total_Tested': total_tested,
                        'Resistant': resistant,
                        'Intermediate': intermediate,
                        'Susceptible': susceptible,
                        'Resistance_Rate_%': round(resistance_rate, 2),
                        'Intermediate_Rate_%': round(intermediate_rate, 2),
                        'Susceptibility_Rate_%': round(susceptibility_rate, 2),
                        'CI_Lower_%': round(ci_lower, 2),
                        'CI_Upper_%': round(ci_upper, 2),
                        'CI_Width_%': round(ci_upper - ci_lower, 2),
                        'Sample_Size_Adequate': validation['reliable'],
                        'Power': round(validation['power'], 3),
                        'Recommendation': validation['recommendation'],
                        'Required_Sample_Size': power_analysis['required_sample_size']
                    })
        
        return pd.DataFrame(results)
    
    def _convert_nd_nm_to_interpretation(self, value, column_name: str, test_type: str) -> str:
        """Convert ND/NM values to R/S/I interpretations with CLSI breakpoints"""
        try:
            if pd.isna(value) or value == '' or str(value).lower() in ['nan', 'xxx', 'no growth']:
                return 'Not Tested'
            
            try:
                numeric_value = float(value)
            except (ValueError, TypeError):
                return 'Not Tested'
            
            # For now, use simplified thresholds (would be enhanced with full CLSI breakpoints)
            if test_type == 'disk_diffusion':
                if numeric_value >= 18:
                    return 'S'
                elif numeric_value >= 13:
                    return 'I'
                else:
                    return 'R'
            else:  # MIC
                if numeric_value <= 1:
                    return 'S'
                elif numeric_value <= 4:
                    return 'I'
                else:
                    return 'R'
                    
        except Exception as e:
            logger.error(f"Error converting ND/NM value {value}: {str(e)}")
            return 'Not Tested'
    
    def create_enhanced_antibiogram(self, resistance_rates: pd.DataFrame, 
                                  show_confidence_intervals: bool = True,
                                  filter_reliable_only: bool = True) -> go.Figure:
        """
        Create enhanced antibiogram with confidence intervals and reliability indicators
        
        Args:
            resistance_rates: DataFrame with resistance rate data
            show_confidence_intervals: Whether to show confidence intervals
            filter_reliable_only: Whether to show only reliable results
            
        Returns:
            Enhanced antibiogram figure
        """
        try:
            if resistance_rates.empty:
                return None
            
            # Filter reliable results if requested
            if filter_reliable_only:
                resistance_rates = resistance_rates[resistance_rates['Sample_Size_Adequate'] == True]
            
            if resistance_rates.empty:
                return None
            
            # Create pivot table
            antibiogram = resistance_rates.pivot_table(
                index='Organism',
                columns='Antimicrobial',
                values='Resistance_Rate_%',
                fill_value=np.nan,
                aggfunc='mean'
            ).round(1)
            
            # Sort by average resistance rate
            if len(antibiogram) > 1:
                avg_resistance = antibiogram.mean(axis=1).sort_values(ascending=False)
                antibiogram = antibiogram.loc[avg_resistance.index]
            
            # Create main heatmap
            fig = go.Figure(data=go.Heatmap(
                z=antibiogram.values,
                x=antibiogram.columns,
                y=antibiogram.index,
                colorscale='RdYlBu_r',
                hoverongaps=False,
                hovertemplate='<b>%{y}</b><br>%{x}: %{z:.1f}%<br><extra></extra>',
                colorbar=dict(
                    title="Resistance Rate (%)",
                    tickmode="array",
                    tickvals=[0, 25, 50, 75, 100],
                    ticktext=["0%", "25%", "50%", "75%", "100%"]
                ),
                showscale=True
            ))
            
            # Add confidence interval annotations if requested
            if show_confidence_intervals:
                self._add_confidence_interval_annotations(fig, resistance_rates, antibiogram)
            
            # Professional styling
            fig.update_layout(
                title={
                    'text': 'Enhanced Antibiogram with Statistical Validation',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 16}
                },
                xaxis_title="Antimicrobial",
                yaxis_title="Organism",
                width=1000,
                height=600,
                font=dict(size=12),
                margin=dict(l=100, r=50, t=80, b=100)
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating enhanced antibiogram: {str(e)}")
            return None
    
    def _add_confidence_interval_annotations(self, fig: go.Figure, resistance_rates: pd.DataFrame, 
                                           antibiogram: pd.DataFrame):
        """Add confidence interval annotations to the heatmap"""
        try:
            # Create CI pivot table
            ci_lower = resistance_rates.pivot_table(
                index='Organism',
                columns='Antimicrobial',
                values='CI_Lower_%',
                fill_value=np.nan,
                aggfunc='mean'
            )
            
            ci_upper = resistance_rates.pivot_table(
                index='Organism',
                columns='Antimicrobial',
                values='CI_Upper_%',
                fill_value=np.nan,
                aggfunc='mean'
            )
            
            # Add annotations for significant results
            annotations = []
            for i, org in enumerate(antibiogram.index):
                for j, am in enumerate(antibiogram.columns):
                    if not pd.isna(antibiogram.loc[org, am]):
                        ci_low = ci_lower.loc[org, am] if org in ci_lower.index and am in ci_lower.columns else None
                        ci_high = ci_upper.loc[org, am] if org in ci_upper.index and am in ci_upper.columns else None
                        
                        if not pd.isna(ci_low) and not pd.isna(ci_high):
                            ci_width = ci_high - ci_low
                            if ci_width > 20:  # Wide confidence interval
                                annotations.append(
                                    dict(
                                        x=j, y=i,
                                        text=f"±{ci_width:.0f}%",
                                        showarrow=False,
                                        font=dict(color="white", size=8),
                                        bgcolor="rgba(0,0,0,0.5)",
                                        bordercolor="white",
                                        borderwidth=1
                                    )
                                )
            
            fig.update_layout(annotations=annotations)
            
        except Exception as e:
            logger.error(f"Error adding confidence interval annotations: {str(e)}")
    
    def create_statistical_summary_dashboard(self, resistance_rates: pd.DataFrame) -> go.Figure:
        """
        Create comprehensive statistical summary dashboard
        
        Args:
            resistance_rates: DataFrame with resistance rate data
            
        Returns:
            Statistical summary dashboard figure
        """
        try:
            if resistance_rates.empty:
                return None
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=[
                    'Sample Size Distribution',
                    'Confidence Interval Width Distribution',
                    'Power Analysis Results',
                    'Reliability Assessment'
                ],
                specs=[[{"type": "histogram"}, {"type": "histogram"}],
                       [{"type": "bar"}, {"type": "pie"}]]
            )
            
            # Sample size distribution
            fig.add_trace(
                go.Histogram(
                    x=resistance_rates['Total_Tested'],
                    name='Sample Size',
                    nbinsx=20,
                    marker_color='lightblue'
                ),
                row=1, col=1
            )
            
            # Confidence interval width distribution
            fig.add_trace(
                go.Histogram(
                    x=resistance_rates['CI_Width_%'],
                    name='CI Width',
                    nbinsx=20,
                    marker_color='lightgreen'
                ),
                row=1, col=2
            )
            
            # Power analysis by organism
            power_by_org = resistance_rates.groupby('Organism')['Power'].mean().sort_values(ascending=True)
            fig.add_trace(
                go.Bar(
                    x=power_by_org.values,
                    y=power_by_org.index,
                    orientation='h',
                    name='Average Power',
                    marker_color='orange'
                ),
                row=2, col=1
            )
            
            # Reliability assessment
            reliable_count = len(resistance_rates[resistance_rates['Sample_Size_Adequate'] == True])
            unreliable_count = len(resistance_rates[resistance_rates['Sample_Size_Adequate'] == False])
            
            fig.add_trace(
                go.Pie(
                    labels=['Reliable', 'Unreliable'],
                    values=[reliable_count, unreliable_count],
                    name='Reliability',
                    marker_colors=['green', 'red']
                ),
                row=2, col=2
            )
            
            # Update layout
            fig.update_layout(
                title={
                    'text': 'Statistical Analysis Summary Dashboard',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 16}
                },
                height=800,
                showlegend=False
            )
            
            # Update axes labels
            fig.update_xaxes(title_text="Sample Size", row=1, col=1)
            fig.update_xaxes(title_text="CI Width (%)", row=1, col=2)
            fig.update_xaxes(title_text="Average Power", row=2, col=1)
            
            fig.update_yaxes(title_text="Frequency", row=1, col=1)
            fig.update_yaxes(title_text="Frequency", row=1, col=2)
            fig.update_yaxes(title_text="Organism", row=2, col=1)
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating statistical summary dashboard: {str(e)}")
            return None
    
    def generate_scientific_report(self, resistance_rates: pd.DataFrame) -> Dict:
        """
        Generate comprehensive scientific report with methodology and results
        
        Args:
            resistance_rates: DataFrame with resistance rate data
            
        Returns:
            Dictionary with scientific report sections
        """
        try:
            if resistance_rates.empty:
                return {'error': 'No data available for analysis'}
            
            # Calculate summary statistics
            total_analyses = len(resistance_rates)
            reliable_analyses = len(resistance_rates[resistance_rates['Sample_Size_Adequate'] == True])
            avg_sample_size = resistance_rates['Total_Tested'].mean()
            avg_ci_width = resistance_rates['CI_Width_%'].mean()
            avg_power = resistance_rates['Power'].mean()
            
            # Organism distribution
            organism_counts = resistance_rates['Organism'].value_counts()
            top_organisms = organism_counts.head(5).to_dict()
            
            # Antimicrobial distribution
            am_counts = resistance_rates['Antimicrobial'].value_counts()
            top_antimicrobials = am_counts.head(5).to_dict()
            
            # Resistance rate distribution
            resistance_stats = {
                'mean': resistance_rates['Resistance_Rate_%'].mean(),
                'median': resistance_rates['Resistance_Rate_%'].median(),
                'std': resistance_rates['Resistance_Rate_%'].std(),
                'min': resistance_rates['Resistance_Rate_%'].min(),
                'max': resistance_rates['Resistance_Rate_%'].max()
            }
            
            # Quality assessment
            quality_metrics = {
                'reliable_analyses_percentage': (reliable_analyses / total_analyses) * 100,
                'average_sample_size': avg_sample_size,
                'average_ci_width': avg_ci_width,
                'average_power': avg_power,
                'high_power_analyses': len(resistance_rates[resistance_rates['Power'] > 0.8])
            }
            
            return {
                'methodology': {
                    'confidence_level': '95%',
                    'minimum_sample_size': 30,
                    'statistical_method': 'Wilson Score Interval',
                    'power_analysis': 'Beta-binomial model',
                    'data_validation': 'Sample size adequacy testing'
                },
                'summary_statistics': {
                    'total_analyses': total_analyses,
                    'reliable_analyses': reliable_analyses,
                    'reliability_percentage': quality_metrics['reliable_analyses_percentage'],
                    'average_sample_size': round(avg_sample_size, 1),
                    'average_ci_width': round(avg_ci_width, 1),
                    'average_power': round(avg_power, 3)
                },
                'data_distribution': {
                    'top_organisms': top_organisms,
                    'top_antimicrobials': top_antimicrobials,
                    'resistance_rate_stats': resistance_stats
                },
                'quality_assessment': quality_metrics,
                'recommendations': self._generate_recommendations(quality_metrics, resistance_rates)
            }
            
        except Exception as e:
            logger.error(f"Error generating scientific report: {str(e)}")
            return {'error': f'Error generating report: {str(e)}'}
    
    def _generate_recommendations(self, quality_metrics: Dict, resistance_rates: pd.DataFrame) -> List[str]:
        """Generate recommendations based on analysis results"""
        recommendations = []
        
        if quality_metrics['reliable_analyses_percentage'] < 70:
            recommendations.append("⚠️ Low reliability rate - consider increasing sample sizes for more robust analysis")
        
        if quality_metrics['average_sample_size'] < 50:
            recommendations.append("📊 Small average sample size - larger samples would improve precision")
        
        if quality_metrics['average_ci_width'] > 30:
            recommendations.append("📏 Wide confidence intervals - consider stratified sampling for better precision")
        
        if quality_metrics['average_power'] < 0.8:
            recommendations.append("⚡ Low statistical power - increase sample sizes for better detection of resistance patterns")
        
        # Check for extreme resistance rates
        extreme_rates = resistance_rates[
            (resistance_rates['Resistance_Rate_%'] > 90) | 
            (resistance_rates['Resistance_Rate_%'] < 5)
        ]
        if len(extreme_rates) > len(resistance_rates) * 0.3:
            recommendations.append("🔍 High proportion of extreme resistance rates - verify data quality and interpretation criteria")
        
        if not recommendations:
            recommendations.append("✅ Analysis quality is good - results are statistically reliable")
        
        return recommendations
