"""
Enhanced AMR Analytics Module for GLASS Data Standardizer
Optimized for real-world antimicrobial susceptibility data with professional visualizations

Based on analysis of the actual dataset characteristics:
- 1085 records with 26 antimicrobials
- Mixed data completeness (1.1% to 49.9%)
- 100 unique organisms (E. coli dominant: 336 records)
- Food safety context (specimen types: cecum, chicken, etc.)
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple, Optional, Union
import io
import base64
from datetime import datetime
import logging
import warnings
from functools import lru_cache

from .ast_detector import ASTDataDetector
from .cache_manager import streamlit_cache_dataframe

# Configure logging
logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')

class AMRAnalytics:
    """
    Enhanced AMR Analytics optimized for real-world data characteristics
    """
    
    def __init__(self):
        self.clsi_breakpoints = self._load_clsi_breakpoints()
        self.antimicrobial_classes = self._define_antimicrobial_classes()
        self.organism_groups = self._define_organism_groups()
        self.color_palettes = self._define_color_palettes()
        self.ast_detector = ASTDataDetector()
        
    @lru_cache(maxsize=1)
    def _load_clsi_breakpoints(self) -> Dict:
        """Load CLSI breakpoints optimized for the dataset's antimicrobials"""
        return {
            'disk_diffusion': {
                'Escherichia coli': {
                    'AMK': {'S': 17, 'I': 15, 'R': 14},
                    'AMC': {'S': 18, 'I': 14, 'R': 13},
                    'AMP': {'S': 17, 'I': 14, 'R': 13},
                    'AZM': {'S': 18, 'I': 14, 'R': 13},
                    'CHL': {'S': 18, 'I': 13, 'R': 12},
                    'CIP': {'S': 21, 'I': 16, 'R': 15},
                    'CAZ': {'S': 18, 'I': 15, 'R': 14},
                    'CTX': {'S': 23, 'I': 20, 'R': 19},
                    'CRO': {'S': 23, 'I': 20, 'R': 19},
                    'FOX': {'S': 18, 'I': 15, 'R': 14},
                    'GEN': {'S': 15, 'I': 13, 'R': 12},
                    'MEM': {'S': 23, 'I': 20, 'R': 19},
                    'NAL': {'S': 19, 'I': 14, 'R': 13},
                    'OXY': {'S': 15, 'I': 12, 'R': 11},
                    'PEF': {'S': 21, 'I': 16, 'R': 15},
                    'SXT': {'S': 16, 'I': 11, 'R': 10},
                    'TCY': {'S': 19, 'I': 15, 'R': 14},
                    'TMP': {'S': 16, 'I': 11, 'R': 10},
                    'VAN': {'S': 17, 'I': 15, 'R': 14},
                },
                'Klebsiella pneumoniae': {
                    'AMK': {'S': 17, 'I': 15, 'R': 14},
                    'AMC': {'S': 18, 'I': 14, 'R': 13},
                    'AMP': {'S': 17, 'I': 14, 'R': 13},
                    'CIP': {'S': 21, 'I': 16, 'R': 15},
                    'CAZ': {'S': 18, 'I': 15, 'R': 14},
                    'CTX': {'S': 23, 'I': 20, 'R': 19},
                    'CRO': {'S': 23, 'I': 20, 'R': 19},
                    'FOX': {'S': 18, 'I': 15, 'R': 14},
                    'GEN': {'S': 15, 'I': 13, 'R': 12},
                    'MEM': {'S': 23, 'I': 20, 'R': 19},
                    'SXT': {'S': 16, 'I': 11, 'R': 10},
                    'TCY': {'S': 19, 'I': 15, 'R': 14},
                },
                'Enterococcus faecium': {
                    'AMP': {'S': 17, 'I': 14, 'R': 13},
                    'CIP': {'S': 21, 'I': 16, 'R': 15},
                    'GEN': {'S': 15, 'I': 13, 'R': 12},
                    'LNZ': {'S': 21, 'I': 20, 'R': 19},
                    'OXY': {'S': 15, 'I': 12, 'R': 11},
                    'VAN': {'S': 17, 'I': 15, 'R': 14},
                },
                'Enterococcus faecalis': {
                    'AMP': {'S': 17, 'I': 14, 'R': 13},
                    'CIP': {'S': 21, 'I': 16, 'R': 15},
                    'GEN': {'S': 15, 'I': 13, 'R': 12},
                    'LNZ': {'S': 21, 'I': 20, 'R': 19},
                    'OXY': {'S': 15, 'I': 12, 'R': 11},
                    'VAN': {'S': 17, 'I': 15, 'R': 14},
                }
            }
        }
    
    def _define_antimicrobial_classes(self) -> Dict:
        """Define antimicrobial classes with proper grouping"""
        return {
            'Beta-lactams': ['AMP', 'AMC', 'CTX', 'CRO', 'CAZ', 'FOX', 'TZP'],
            'Aminoglycosides': ['AMK', 'GEN'],
            'Fluoroquinolones': ['CIP', 'PEF', 'NAL'],
            'Tetracyclines': ['TCY', 'OXY'],
            'Phenicols': ['CHL'],
            'Sulfonamides': ['SXT', 'TMP'],
            'Macrolides': ['AZM'],
            'Glycopeptides': ['VAN'],
            'Oxazolidinones': ['LNZ'],
            'Carbapenems': ['MEM'],
            'Others': ['CCV', 'CTC', 'OXA', 'OXO', 'TGC']
        }
    
    def _define_organism_groups(self) -> Dict:
        """Define organism groups for better analysis"""
        return {
            'Enterobacteriaceae': ['eco', 'kpn', 'sal', 'oth'],
            'Enterococcus': ['efa', 'efm'],
            'Staphylococcus': ['sau', 'sap'],
            'Streptococcus': ['spn', 'spy'],
            'Acinetobacter': ['aba'],
            'Pseudomonas': ['pmi'],
            'Bacillus': ['bce'],
            'Other': ['xxx', 'oth']
        }
    
    def _define_color_palettes(self) -> Dict:
        """Define professional color palettes for visualizations"""
        return {
            'resistance': ['#2E8B57', '#FFD700', '#FF6347', '#DC143C'],  # Green, Gold, Tomato, Crimson
            'organisms': px.colors.qualitative.Set3,
            'antimicrobials': px.colors.qualitative.Pastel,
            'heatmap': 'RdYlBu_r',
            'trends': px.colors.qualitative.Dark24
        }
    
    def detect_and_process_ast_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Detect AST data type and process accordingly
        
        Args:
            df: DataFrame containing AST data
            
        Returns:
            Tuple of (processed_dataframe, detection_info)
        """
        try:
            # Detect AST data type
            detection_result = self.ast_detector.detect_ast_data_type(df)
            
            logger.info(f"AST data type detected: {detection_result['data_type']} "
                       f"(confidence: {detection_result['confidence']}%)")
            
            if detection_result['data_type'] == 'interpreted':
                # Data is already interpreted, process directly
                processed_df = self._process_interpreted_data(df, detection_result)
                
            elif detection_result['data_type'] == 'breakpoint':
                # Data contains breakpoints, apply CLSI interpretation
                processed_df = self.interpret_susceptibility_enhanced(df)
                
            elif detection_result['data_type'] == 'mixed':
                # Mixed data, handle each column appropriately
                processed_df = self._process_mixed_data(df, detection_result)
                
            else:
                # Unknown data type, try to process as breakpoints
                logger.warning("Unknown AST data type, attempting breakpoint interpretation")
                processed_df = self.interpret_susceptibility_enhanced(df)
            
            return processed_df, detection_result
            
        except Exception as e:
            logger.error(f"Error in detect_and_process_ast_data: {str(e)}")
            return df, {
                'data_type': 'error',
                'confidence': 0,
                'recommendations': [f'Error processing data: {str(e)}']
            }
    
    def _process_interpreted_data(self, df: pd.DataFrame, detection_result: Dict) -> pd.DataFrame:
        """
        Process data that is already in interpreted format (R/S/I)
        
        Args:
            df: DataFrame with interpreted data
            detection_result: Detection results
            
        Returns:
            Processed DataFrame with standardized interpreted data
        """
        try:
            df_processed = df.copy()
            
            # Get interpreted columns
            interpreted_columns = []
            for col, analysis in detection_result.get('column_analysis', {}).items():
                if analysis['type'] == 'interpreted':
                    interpreted_columns.append(col)
            
            # Convert to standard format
            df_processed = self.ast_detector.convert_interpreted_to_breakpoints(
                df_processed, interpreted_columns
            )
            
            # Create interpretation columns for consistency
            for col in interpreted_columns:
                if col in df_processed.columns:
                    interpret_col = f"{col}_INTERPRETATION"
                    df_processed[interpret_col] = df_processed[col]
            
            logger.info(f"Processed {len(interpreted_columns)} interpreted columns")
            return df_processed
            
        except Exception as e:
            logger.error(f"Error processing interpreted data: {str(e)}")
            return df
    
    def _process_mixed_data(self, df: pd.DataFrame, detection_result: Dict) -> pd.DataFrame:
        """
        Process data with mixed interpreted and breakpoint columns
        
        Args:
            df: DataFrame with mixed data
            detection_result: Detection results
            
        Returns:
            Processed DataFrame
        """
        try:
            df_processed = df.copy()
            
            # Process interpreted columns
            interpreted_columns = []
            breakpoint_columns = []
            
            for col, analysis in detection_result.get('column_analysis', {}).items():
                if analysis['type'] == 'interpreted':
                    interpreted_columns.append(col)
                elif analysis['type'] == 'breakpoint':
                    breakpoint_columns.append(col)
            
            # Process interpreted columns
            if interpreted_columns:
                df_processed = self.ast_detector.convert_interpreted_to_breakpoints(
                    df_processed, interpreted_columns
                )
                
                # Create interpretation columns
                for col in interpreted_columns:
                    if col in df_processed.columns:
                        interpret_col = f"{col}_INTERPRETATION"
                        df_processed[interpret_col] = df_processed[col]
            
            # Process breakpoint columns
            if breakpoint_columns:
                # Apply CLSI interpretation to breakpoint columns
                for col in breakpoint_columns:
                    if col in df_processed.columns:
                        # Extract antimicrobial name
                        if '_ND' in col:
                            am_name = col.split('_ND')[0]
                        elif '_NM' in col:
                            am_name = col.split('_NM')[0]
                        else:
                            am_name = col
                        
                        interpret_col = f"{am_name}_INTERPRETATION"
                        df_processed[interpret_col] = 'Not Tested'
                        
                        # Apply CLSI interpretation
                        for idx, row in df_processed.iterrows():
                            organism = str(row.get('Organism', '')).lower()
                            value = row[col]
                            
                            if pd.isna(value) or value == '':
                                continue
                            
                            try:
                                value = float(value)
                                interpretation = self._interpret_breakpoint_value(
                                    organism, am_name, value
                                )
                                df_processed.loc[idx, interpret_col] = interpretation
                            except (ValueError, TypeError):
                                continue
            
            logger.info(f"Processed mixed data: {len(interpreted_columns)} interpreted, "
                       f"{len(breakpoint_columns)} breakpoint columns")
            return df_processed
            
        except Exception as e:
            logger.error(f"Error processing mixed data: {str(e)}")
            return df
    
    def _interpret_breakpoint_value(self, organism: str, antimicrobial: str, value: float) -> str:
        """
        Interpret a single breakpoint value using CLSI guidelines
        
        Args:
            organism: Organism name
            antimicrobial: Antimicrobial name
            value: Breakpoint value (zone diameter or MIC)
            
        Returns:
            Interpretation (S/I/R or 'No Breakpoints')
        """
        try:
            # Check if we have breakpoints for this organism and antimicrobial
            if (organism in self.clsi_breakpoints['disk_diffusion'] and
                antimicrobial in self.clsi_breakpoints['disk_diffusion'][organism]):
                
                breakpoints = self.clsi_breakpoints['disk_diffusion'][organism][antimicrobial]
                
                if value >= breakpoints['S']:
                    return 'S'
                elif value >= breakpoints['I']:
                    return 'I'
                else:
                    return 'R'
            else:
                return 'No Breakpoints'
                
        except Exception as e:
            logger.warning(f"Error interpreting breakpoint: {str(e)}")
            return 'No Breakpoints'
    
    def interpret_susceptibility_enhanced(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enhanced susceptibility interpretation with better handling of real-world data
        """
        try:
            if df is None or df.empty:
                return pd.DataFrame()
            
            df_interpreted = df.copy()
            
            # Get antimicrobial columns
            am_cols = [col for col in df.columns if any(x in col for x in ['_ND', '_NM']) and not col.endswith('_ND') and not col.endswith('_NM')]
            
            if not am_cols:
                return df_interpreted
            
            logger.info(f"Interpreting susceptibility for {len(am_cols)} antimicrobials")
            
            for col in am_cols:
                try:
                    if '_ND' in col:
                        am_name = col.split('_ND')[0]
                        test_type = 'disk_diffusion'
                    elif '_NM' in col:
                        am_name = col.split('_NM')[0]
                        test_type = 'mic'
                    else:
                        continue
                    
                    interpret_col = f"{am_name}_INTERPRETATION"
                    df_interpreted[interpret_col] = 'Not Tested'
                    
                    # Process in batches for better performance
                    for idx, row in df.iterrows():
                        try:
                            organism = str(row['Organism']).lower()
                            zone_diameter = row[col]
                            
                            if pd.isna(zone_diameter) or zone_diameter == '':
                                continue
                            
                            try:
                                zone_diameter = float(zone_diameter)
                            except (ValueError, TypeError):
                                continue
                            
                            # Get breakpoints
                            if (test_type in self.clsi_breakpoints and 
                                organism in self.clsi_breakpoints[test_type] and
                                am_name in self.clsi_breakpoints[test_type][organism]):
                                
                                breakpoints = self.clsi_breakpoints[test_type][organism][am_name]
                                
                                if zone_diameter >= breakpoints['S']:
                                    df_interpreted.loc[idx, interpret_col] = 'S'
                                elif zone_diameter >= breakpoints['I']:
                                    df_interpreted.loc[idx, interpret_col] = 'I'
                                else:
                                    df_interpreted.loc[idx, interpret_col] = 'R'
                            else:
                                df_interpreted.loc[idx, interpret_col] = 'No Breakpoints'
                                
                        except Exception as e:
                            continue
                            
                except Exception as e:
                    logger.warning(f"Error processing {col}: {str(e)}")
                    continue
            
            return df_interpreted
            
        except Exception as e:
            logger.error(f"Error in interpret_susceptibility_enhanced: {str(e)}")
            return df
    
    def create_professional_antibiogram(self, df: pd.DataFrame, organism: str = None) -> go.Figure:
        """
        Create a professional antibiogram heatmap with enhanced styling
        """
        try:
            if df is None or df.empty:
                return None
            
            # Use provided resistance rates or calculate if not provided
            if 'Resistance_Rate_%' not in df.columns:
                resistance_rates = self.calculate_resistance_rates_enhanced(df)
                if resistance_rates.empty:
                    return None
            else:
                resistance_rates = df
            
            # Filter by organism if specified
            if organism and organism != 'All Organisms':
                resistance_rates = resistance_rates[resistance_rates['Organism'] == organism]
            
            if resistance_rates.empty:
                return None
            
            # Create pivot table
            antibiogram = resistance_rates.pivot_table(
                index='Organism',
                columns='Antimicrobial',
                values='Resistance_Rate_%',
                fill_value=0,
                aggfunc='mean'
            ).round(1)
            
            # Sort by resistance rate for better visualization
            if len(antibiogram) > 1:
                avg_resistance = antibiogram.mean(axis=1).sort_values(ascending=False)
                antibiogram = antibiogram.loc[avg_resistance.index]
            
            # Create professional heatmap
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
            
            # Professional styling
            fig.update_layout(
                title=dict(
                    text=f"Antimicrobial Resistance Profile{' - ' + organism if organism and organism != 'All Organisms' else ''}",
                    x=0.5,
                    font=dict(size=16, family="Arial, sans-serif")
                ),
                xaxis=dict(
                    title="Antimicrobial",
                    title_font=dict(size=12, family="Arial, sans-serif"),
                    tickfont=dict(size=10),
                    tickangle=45
                ),
                yaxis=dict(
                    title="Organism",
                    title_font=dict(size=12, family="Arial, sans-serif"),
                    tickfont=dict(size=10)
                ),
                height=max(400, len(antibiogram.index) * 40),
                width=max(800, len(antibiogram.columns) * 60),
                margin=dict(l=100, r=50, t=80, b=100),
                font=dict(family="Arial, sans-serif", size=10)
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating professional antibiogram: {str(e)}")
            return None
    
    def create_organism_distribution_chart(self, df: pd.DataFrame) -> go.Figure:
        """
        Create a professional organism distribution chart
        """
        try:
            if df is None or df.empty:
                return None
            
            org_counts = df['Organism'].value_counts()
            
            # Group small organisms into "Others" for better visualization
            threshold = 5
            major_orgs = org_counts[org_counts >= threshold]
            others_count = org_counts[org_counts < threshold].sum()
            
            if others_count > 0:
                major_orgs['Others'] = others_count
            
            # Create donut chart for better visual appeal
            fig = go.Figure(data=[go.Pie(
                labels=major_orgs.index,
                values=major_orgs.values,
                hole=0.4,
                textinfo='label+percent',
                textposition='auto',
                marker=dict(
                    colors=self.color_palettes['organisms'][:len(major_orgs)],
                    line=dict(color='white', width=2)
                ),
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
            )])
            
            fig.update_layout(
                title=dict(
                    text="Distribution of Isolates by Organism",
                    x=0.5,
                    font=dict(size=16, family="Arial, sans-serif")
                ),
                showlegend=True,
                height=500,
                width=600,
                margin=dict(t=80, b=50, l=50, r=50),
                font=dict(family="Arial, sans-serif", size=11)
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating organism distribution chart: {str(e)}")
            return None
    
    def create_resistance_summary_dashboard(self, df: pd.DataFrame) -> go.Figure:
        """
        Create a comprehensive resistance summary dashboard
        """
        try:
            if df is None or df.empty:
                return None
            
            # Calculate resistance rates
            resistance_rates = self.calculate_resistance_rates_enhanced(df)
            
            if resistance_rates.empty:
                return None
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    'Resistance Rate by Antimicrobial',
                    'Resistance Rate by Organism',
                    'Antimicrobial Class Analysis',
                    'Data Completeness'
                ),
                specs=[[{"type": "bar"}, {"type": "bar"}],
                       [{"type": "bar"}, {"type": "bar"}]]
            )
            
            # 1. Resistance by antimicrobial
            am_resistance = resistance_rates.groupby('Antimicrobial')['Resistance_Rate_%'].mean().sort_values(ascending=True)
            fig.add_trace(
                go.Bar(
                    x=am_resistance.values,
                    y=am_resistance.index,
                    orientation='h',
                    name='Resistance Rate',
                    marker_color='lightcoral',
                    hovertemplate='%{y}: %{x:.1f}%<extra></extra>'
                ),
                row=1, col=1
            )
            
            # 2. Resistance by organism (top 10)
            org_resistance = resistance_rates.groupby('Organism')['Resistance_Rate_%'].mean().sort_values(ascending=True).tail(10)
            fig.add_trace(
                go.Bar(
                    x=org_resistance.values,
                    y=org_resistance.index,
                    orientation='h',
                    name='Resistance Rate',
                    marker_color='lightblue',
                    hovertemplate='%{y}: %{x:.1f}%<extra></extra>'
                ),
                row=1, col=2
            )
            
            # 3. Antimicrobial class analysis
            class_rates = self._calculate_class_resistance_rates(resistance_rates)
            if not class_rates.empty:
                fig.add_trace(
                    go.Bar(
                        x=class_rates['Class'],
                        y=class_rates['Resistance_Rate_%'],
                        name='Class Resistance',
                        marker_color='lightgreen',
                        hovertemplate='%{x}: %{y:.1f}%<extra></extra>'
                    ),
                    row=2, col=1
                )
            
            # 4. Data completeness
            am_cols = [col for col in df.columns if any(x in col for x in ['_ND', '_NM']) and not col.endswith('_ND') and not col.endswith('_NM')]
            completeness = [(df[col].notna().sum() / len(df)) * 100 for col in am_cols[:10]]  # Top 10
            am_names = [col.split('_')[0] for col in am_cols[:10]]
            
            fig.add_trace(
                go.Bar(
                    x=am_names,
                    y=completeness,
                    name='Data Completeness',
                    marker_color='gold',
                    hovertemplate='%{x}: %{y:.1f}%<extra></extra>'
                ),
                row=2, col=2
            )
            
            # Update layout
            fig.update_layout(
                title=dict(
                    text="AMR Analysis Dashboard",
                    x=0.5,
                    font=dict(size=18, family="Arial, sans-serif")
                ),
                height=800,
                width=1200,
                showlegend=False,
                font=dict(family="Arial, sans-serif", size=10)
            )
            
            # Update axes
            fig.update_xaxes(tickangle=45, row=2, col=1)
            fig.update_xaxes(tickangle=45, row=2, col=2)
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating resistance summary dashboard: {str(e)}")
            return None
    
    @streamlit_cache_dataframe(max_age_seconds=1800)
    def calculate_resistance_rates_enhanced(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enhanced resistance rate calculation with automatic AST data type detection
        """
        try:
            if df is None or df.empty:
                return pd.DataFrame()
            
            # Look for interpretation columns or create them from ND/NM columns
            interpret_cols = [col for col in df.columns if col.endswith('_INTERPRETATION')]
            
            # If no interpretation columns found, look for ND/NM columns and create interpretations
            if not interpret_cols:
                nd_cols = [col for col in df.columns if '_ND' in col]
                nm_cols = [col for col in df.columns if '_NM' in col]
                
                if not nd_cols and not nm_cols:
                    return pd.DataFrame()
                
                # Create interpretation columns from ND/NM data
                df_interpreted = df.copy()
                for col in nd_cols + nm_cols:
                    am_name = col.split('_ND')[0] if '_ND' in col else col.split('_NM')[0]
                    interpret_col = f"{am_name}_INTERPRETATION"
                    
                    # Convert ND/NM values to interpretations
                    df_interpreted[interpret_col] = df_interpreted[col].apply(
                        lambda x: self._convert_nd_nm_to_interpretation(x, col)
                    )
                    interpret_cols.append(interpret_col)
            else:
                df_interpreted = df.copy()
            
            if not interpret_cols:
                return pd.DataFrame()
            
            results = []
            
            # Get organisms with sufficient data
            organisms = df_interpreted['Organism'].dropna().unique()
            organisms = [org for org in organisms if str(org).lower() not in ['xxx', 'nan', '', 'no growth', 'not applicable']]
            
            # Filter out organisms with less than 5 isolates for meaningful analysis
            organism_counts = df_interpreted['Organism'].value_counts()
            organisms = [org for org in organisms if organism_counts.get(org, 0) >= 5]
            
            for org in organisms:
                org_data = df_interpreted[df_interpreted['Organism'] == org]
                
                for col in interpret_cols:
                    am_name = col.replace('_INTERPRETATION', '')
                    tested_data = org_data[org_data[col] != 'Not Tested']
                    
                    if len(tested_data) == 0:
                        continue
                    
                    resistant = len(tested_data[tested_data[col] == 'R'])
                    intermediate = len(tested_data[tested_data[col] == 'I'])
                    susceptible = len(tested_data[tested_data[col] == 'S'])
                    total_tested = len(tested_data)
                    
                    if total_tested > 0:
                        resistance_rate = (resistant / total_tested) * 100
                        intermediate_rate = (intermediate / total_tested) * 100
                        susceptibility_rate = (susceptible / total_tested) * 100
                        
                        results.append({
                            'Organism': org,
                            'Antimicrobial': am_name,
                            'Total_Tested': total_tested,
                            'Resistant': resistant,
                            'Intermediate': intermediate,
                            'Susceptible': susceptible,
                            'Resistance_Rate_%': round(resistance_rate, 1),
                            'Intermediate_Rate_%': round(intermediate_rate, 1),
                            'Susceptibility_Rate_%': round(susceptibility_rate, 1)
                        })
            
            return pd.DataFrame(results)
            
        except Exception as e:
            logger.error(f"Error in calculate_resistance_rates_enhanced: {str(e)}")
            return pd.DataFrame()
    
    def _calculate_class_resistance_rates(self, resistance_rates: pd.DataFrame) -> pd.DataFrame:
        """Calculate resistance rates by antimicrobial class"""
        try:
            # Map antimicrobials to classes
            am_to_class = {}
            for class_name, ams in self.antimicrobial_classes.items():
                for am in ams:
                    am_to_class[am] = class_name
            
            resistance_rates['Class'] = resistance_rates['Antimicrobial'].map(am_to_class)
            resistance_rates = resistance_rates.dropna(subset=['Class'])
            
            if resistance_rates.empty:
                return pd.DataFrame()
            
            # Calculate average resistance by class
            class_rates = resistance_rates.groupby('Class')['Resistance_Rate_%'].mean().reset_index()
            class_rates = class_rates.sort_values('Resistance_Rate_%', ascending=False)
            
            return class_rates
            
        except Exception as e:
            logger.error(f"Error calculating class resistance rates: {str(e)}")
            return pd.DataFrame()
    
    def _convert_nd_nm_to_interpretation(self, value, column_name: str) -> str:
        """
        Convert ND/NM values to R/S/I interpretations
        
        Args:
            value: The value from ND/NM column
            column_name: Name of the column (to determine if it's ND or NM)
            
        Returns:
            Interpretation string (R/S/I/Not Tested)
        """
        try:
            if pd.isna(value) or value == '' or str(value).lower() in ['nan', 'xxx', 'no growth']:
                return 'Not Tested'
            
            # Convert to float if possible
            try:
                numeric_value = float(value)
            except (ValueError, TypeError):
                return 'Not Tested'
            
            # Determine if it's ND (disk diffusion) or NM (MIC)
            is_nd = '_ND' in column_name
            is_nm = '_NM' in column_name
            
            if is_nd:
                # Disk diffusion interpretation (zone diameter in mm)
                # More realistic thresholds based on typical CLSI breakpoints
                if numeric_value >= 18:  # Susceptible
                    return 'S'
                elif numeric_value >= 13:  # Intermediate
                    return 'I'
                else:  # Resistant
                    return 'R'
            elif is_nm:
                # MIC interpretation (lower values = more susceptible)
                if numeric_value <= 1:  # Generally susceptible
                    return 'S'
                elif numeric_value <= 4:  # Generally intermediate
                    return 'I'
                else:  # Generally resistant
                    return 'R'
            else:
                return 'Not Tested'
                
        except Exception as e:
            logger.error(f"Error converting ND/NM value {value}: {str(e)}")
            return 'Not Tested'
    
    def create_data_quality_summary(self, df: pd.DataFrame) -> Dict:
        """
        Create a comprehensive data quality summary
        """
        try:
            if df is None or df.empty:
                return {}
            
            am_cols = [col for col in df.columns if any(x in col for x in ['_ND', '_NM']) and not col.endswith('_ND') and not col.endswith('_NM')]
            
            summary = {
                'total_records': len(df),
                'total_antimicrobials': len(am_cols),
                'unique_organisms': df['Organism'].nunique(),
                'data_completeness': {},
                'organism_distribution': {},
                'quality_score': 0
            }
            
            # Calculate data completeness
            total_cells = len(df) * len(am_cols)
            filled_cells = sum(df[col].notna().sum() for col in am_cols)
            overall_completeness = (filled_cells / total_cells) * 100 if total_cells > 0 else 0
            
            summary['overall_completeness'] = round(overall_completeness, 1)
            
            # Individual antimicrobial completeness
            for col in am_cols:
                completeness = (df[col].notna().sum() / len(df)) * 100
                summary['data_completeness'][col] = round(completeness, 1)
            
            # Organism distribution
            org_counts = df['Organism'].value_counts()
            summary['organism_distribution'] = org_counts.head(10).to_dict()
            
            # Quality score calculation
            quality_factors = [
                overall_completeness / 100,  # Data completeness
                min(1.0, len(am_cols) / 20),  # Antimicrobial coverage
                min(1.0, df['Organism'].nunique() / 50),  # Organism diversity
            ]
            summary['quality_score'] = round(sum(quality_factors) / len(quality_factors) * 100, 1)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error creating data quality summary: {str(e)}")
            return {}
    
    def export_professional_charts(self, df: pd.DataFrame, format: str = 'png') -> Dict[str, bytes]:
        """
        Export professional-quality charts
        """
        charts = {}
        
        try:
            if df is None or df.empty:
                return charts
            
            logger.info(f"Exporting professional charts in {format.upper()} format")
            
            # Antibiogram
            try:
                antibiogram_fig = self.create_professional_antibiogram(df)
                if antibiogram_fig:
                    charts['professional_antibiogram'] = antibiogram_fig.to_image(format=format, width=1200, height=800)
            except Exception as e:
                logger.warning(f"Error exporting antibiogram: {str(e)}")
            
            # Organism distribution
            try:
                org_dist_fig = self.create_organism_distribution_chart(df)
                if org_dist_fig:
                    charts['organism_distribution'] = org_dist_fig.to_image(format=format, width=800, height=600)
            except Exception as e:
                logger.warning(f"Error exporting organism distribution: {str(e)}")
            
            # Summary dashboard
            try:
                dashboard_fig = self.create_resistance_summary_dashboard(df)
                if dashboard_fig:
                    charts['resistance_dashboard'] = dashboard_fig.to_image(format=format, width=1400, height=1000)
            except Exception as e:
                logger.warning(f"Error exporting dashboard: {str(e)}")
            
            logger.info(f"Professional chart export completed: {len(charts)} charts generated")
            
        except Exception as e:
            logger.error(f"Error in export_professional_charts: {str(e)}")
        
        return charts
