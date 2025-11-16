"""
AST Data Type Detection Module
Automatically detects whether AST columns contain interpreted results (R/S/I) or raw breakpoints
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Tuple, Optional, Union
import logging

logger = logging.getLogger(__name__)

class ASTDataDetector:
    """
    Detects AST data format and provides appropriate processing methods
    """
    
    def __init__(self):
        self.interpreted_patterns = {
            'R': r'^R$',
            'S': r'^S$', 
            'I': r'^I$',
            'Resistant': r'^Resistant$',
            'Susceptible': r'^Susceptible$',
            'Intermediate': r'^Intermediate$',
            'Sensitive': r'^Sensitive$'
        }
        
        self.breakpoint_patterns = {
            'numeric': r'^\d+(\.\d+)?$',
            'zone_diameter': r'^\d{1,2}(\.\d+)?$',  # 6-50mm typical range
            'mic_value': r'^\d+(\.\d+)?$'  # MIC values
        }
    
    def detect_ast_data_type(self, df: pd.DataFrame) -> Dict:
        """
        Detect the type of AST data in the DataFrame
        
        Args:
            df: DataFrame containing AST data
            
        Returns:
            Dictionary with detection results and recommendations
        """
        try:
            if df is None or df.empty:
                return {
                    'data_type': 'unknown',
                    'confidence': 0,
                    'columns_analyzed': 0,
                    'recommendations': ['No data available for analysis']
                }
            
            # Find AST columns
            ast_columns = self._find_ast_columns(df)
            
            if not ast_columns:
                return {
                    'data_type': 'unknown',
                    'confidence': 0,
                    'columns_analyzed': 0,
                    'recommendations': ['No AST columns found. Expected columns ending with _ND, _NM, or containing antimicrobial names.']
                }
            
            # Analyze each column
            column_analysis = {}
            interpreted_count = 0
            breakpoint_count = 0
            mixed_count = 0
            
            for col in ast_columns:
                analysis = self._analyze_column(df[col])
                column_analysis[col] = analysis
                
                if analysis['type'] == 'interpreted':
                    interpreted_count += 1
                elif analysis['type'] == 'breakpoint':
                    breakpoint_count += 1
                elif analysis['type'] == 'mixed':
                    mixed_count += 1
            
            # Determine overall data type
            total_columns = len(ast_columns)
            interpreted_ratio = interpreted_count / total_columns
            breakpoint_ratio = breakpoint_count / total_columns
            mixed_ratio = mixed_count / total_columns
            
            if interpreted_ratio >= 0.7:
                data_type = 'interpreted'
                confidence = interpreted_ratio
            elif breakpoint_ratio >= 0.7:
                data_type = 'breakpoint'
                confidence = breakpoint_ratio
            elif mixed_ratio >= 0.5:
                data_type = 'mixed'
                confidence = mixed_ratio
            else:
                data_type = 'unknown'
                confidence = max(interpreted_ratio, breakpoint_ratio, mixed_ratio)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                data_type, confidence, column_analysis, ast_columns
            )
            
            return {
                'data_type': data_type,
                'confidence': round(confidence * 100, 1),
                'columns_analyzed': total_columns,
                'interpreted_columns': interpreted_count,
                'breakpoint_columns': breakpoint_count,
                'mixed_columns': mixed_count,
                'column_analysis': column_analysis,
                'recommendations': recommendations,
                'ast_columns': ast_columns
            }
            
        except Exception as e:
            logger.error(f"Error detecting AST data type: {str(e)}")
            return {
                'data_type': 'error',
                'confidence': 0,
                'columns_analyzed': 0,
                'recommendations': [f'Error during analysis: {str(e)}']
            }
    
    def _find_ast_columns(self, df: pd.DataFrame) -> List[str]:
        """Find columns that likely contain AST data"""
        ast_columns = []
        
        # Look for columns with common AST patterns
        for col in df.columns:
            col_lower = col.lower()
            
            # Check for antimicrobial name patterns
            if any(pattern in col_lower for pattern in ['_nd', '_nm', 'zone', 'mic', 'breakpoint']):
                ast_columns.append(col)
            # Check for common antimicrobial abbreviations
            elif any(am in col_lower for am in [
                'amp', 'amc', 'amk', 'azm', 'chl', 'cip', 'caz', 'ctx', 'cro', 
                'fox', 'gen', 'mem', 'nal', 'oxy', 'pef', 'sxt', 'tcy', 'tmp', 'van'
            ]):
                ast_columns.append(col)
            # Columns that end with SIR (e.g., CiprofloxacinSIR)
            elif col_lower.endswith('sir'):
                ast_columns.append(col)
            # Check for resistance phenotype columns
            elif any(pattern in col_lower for pattern in ['resistance', 'susceptibility', 'phenotype']):
                ast_columns.append(col)
            else:
                # Value-based detection for interpreted RSI columns regardless of name
                try:
                    series = df[col].dropna().astype(str).head(50).str.upper()
                    if len(series) == 0:
                        continue
                    valid = series.isin(['R', 'S', 'I', 'RES', 'RESISTANT', 'SUSCEPTIBLE', 'SENSITIVE', 'INTERMEDIATE', 'INT'])
                    if valid.mean() >= 0.6:
                        ast_columns.append(col)
                except Exception:
                    pass
        
        return ast_columns
    
    def _analyze_column(self, series: pd.Series) -> Dict:
        """Analyze a single column to determine its data type"""
        try:
            # Remove NaN values
            clean_series = series.dropna()
            
            if len(clean_series) == 0:
                return {
                    'type': 'empty',
                    'confidence': 0,
                    'sample_values': [],
                    'details': 'No data in column'
                }
            
            # Get sample values for analysis
            sample_values = clean_series.head(20).astype(str).tolist()
            
            # Check for interpreted values
            interpreted_matches = 0
            for pattern_name, pattern in self.interpreted_patterns.items():
                matches = sum(1 for val in sample_values if re.match(pattern, val, re.IGNORECASE))
                interpreted_matches += matches
            
            # Check for breakpoint values
            breakpoint_matches = 0
            for pattern_name, pattern in self.breakpoint_patterns.items():
                matches = sum(1 for val in sample_values if re.match(pattern, val))
                breakpoint_matches += matches
            
            # Check for numeric values that could be breakpoints
            numeric_values = 0
            for val in sample_values:
                try:
                    num_val = float(val)
                    if 0 <= num_val <= 100:  # Reasonable range for zone diameters or MIC
                        numeric_values += 1
                except (ValueError, TypeError):
                    pass
            
            total_samples = len(sample_values)
            interpreted_ratio = interpreted_matches / total_samples if total_samples > 0 else 0
            breakpoint_ratio = max(breakpoint_matches, numeric_values) / total_samples if total_samples > 0 else 0
            
            # Determine type
            if interpreted_ratio >= 0.8:
                data_type = 'interpreted'
                confidence = interpreted_ratio
            elif breakpoint_ratio >= 0.8:
                data_type = 'breakpoint'
                confidence = breakpoint_ratio
            elif interpreted_ratio >= 0.3 and breakpoint_ratio >= 0.3:
                data_type = 'mixed'
                confidence = min(interpreted_ratio, breakpoint_ratio)
            else:
                data_type = 'unknown'
                confidence = max(interpreted_ratio, breakpoint_ratio)
            
            return {
                'type': data_type,
                'confidence': round(confidence * 100, 1),
                'sample_values': sample_values[:5],
                'interpreted_ratio': interpreted_ratio,
                'breakpoint_ratio': breakpoint_ratio,
                'details': f'Analyzed {total_samples} values'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing column: {str(e)}")
            return {
                'type': 'error',
                'confidence': 0,
                'sample_values': [],
                'details': f'Error: {str(e)}'
            }
    
    def _generate_recommendations(self, data_type: str, confidence: float, 
                                column_analysis: Dict, ast_columns: List[str]) -> List[str]:
        """Generate recommendations based on detection results"""
        recommendations = []
        
        if data_type == 'interpreted':
            recommendations.append("✅ Data appears to be already interpreted (R/S/I format)")
            recommendations.append("📊 Ready for direct resistance analysis")
            recommendations.append("🔍 No CLSI breakpoint interpretation needed")
            
        elif data_type == 'breakpoint':
            recommendations.append("📏 Data appears to contain raw breakpoints (zone diameters/MIC)")
            recommendations.append("🧬 CLSI breakpoint interpretation will be applied")
            recommendations.append("📊 Resistance rates will be calculated from breakpoints")
            
        elif data_type == 'mixed':
            recommendations.append("⚠️ Mixed data format detected")
            recommendations.append("🔧 Some columns are interpreted, others are breakpoints")
            recommendations.append("💡 Consider standardizing data format for better analysis")
            
        else:
            recommendations.append("❓ Unable to determine data format")
            recommendations.append("🔍 Please check your data format")
            recommendations.append("💡 Expected: R/S/I values or numeric breakpoints")
        
        # Add specific column recommendations
        if column_analysis:
            interpreted_cols = [col for col, analysis in column_analysis.items() 
                              if analysis['type'] == 'interpreted']
            breakpoint_cols = [col for col, analysis in column_analysis.items() 
                             if analysis['type'] == 'breakpoint']
            
            if interpreted_cols:
                recommendations.append(f"📋 Interpreted columns: {', '.join(interpreted_cols[:3])}")
            if breakpoint_cols:
                recommendations.append(f"📏 Breakpoint columns: {', '.join(breakpoint_cols[:3])}")
        
        return recommendations
    
    def convert_interpreted_to_breakpoints(self, df: pd.DataFrame, 
                                         interpreted_columns: List[str]) -> pd.DataFrame:
        """
        Convert interpreted columns to a standard format for analysis
        
        Args:
            df: DataFrame with interpreted data
            interpreted_columns: List of columns containing interpreted data
            
        Returns:
            DataFrame with standardized interpreted data
        """
        try:
            df_converted = df.copy()
            
            for col in interpreted_columns:
                if col in df_converted.columns:
                    # Standardize values
                    df_converted[col] = df_converted[col].astype(str).str.upper()
                    
                    # Map various formats to standard R/S/I
                    mapping = {
                        'RESISTANT': 'R',
                        'SUSCEPTIBLE': 'S', 
                        'SENSITIVE': 'S',
                        'INTERMEDIATE': 'I',
                        'R': 'R',
                        'S': 'S',
                        'I': 'I'
                    }
                    
                    df_converted[col] = df_converted[col].map(mapping).fillna(df_converted[col])
            
            return df_converted
            
        except Exception as e:
            logger.error(f"Error converting interpreted data: {str(e)}")
            return df
    
    def get_analysis_method(self, data_type: str) -> str:
        """
        Get the recommended analysis method based on data type
        
        Args:
            data_type: Detected data type ('interpreted', 'breakpoint', 'mixed', 'unknown')
            
        Returns:
            Recommended analysis method
        """
        method_mapping = {
            'interpreted': 'direct_resistance_analysis',
            'breakpoint': 'clsi_interpretation_analysis', 
            'mixed': 'hybrid_analysis',
            'unknown': 'manual_review_required'
        }
        
        return method_mapping.get(data_type, 'manual_review_required')
    
    def create_analysis_summary(self, detection_result: Dict) -> str:
        """
        Create a human-readable summary of the detection results
        
        Args:
            detection_result: Results from detect_ast_data_type
            
        Returns:
            Formatted summary string
        """
        summary = []
        summary.append("🔍 AST Data Type Detection Results")
        summary.append("=" * 40)
        summary.append(f"Data Type: {detection_result['data_type'].upper()}")
        summary.append(f"Confidence: {detection_result['confidence']}%")
        summary.append(f"Columns Analyzed: {detection_result['columns_analyzed']}")
        
        if detection_result['data_type'] in ['interpreted', 'mixed']:
            summary.append(f"Interpreted Columns: {detection_result.get('interpreted_columns', 0)}")
        
        if detection_result['data_type'] in ['breakpoint', 'mixed']:
            summary.append(f"Breakpoint Columns: {detection_result.get('breakpoint_columns', 0)}")
        
        summary.append("\n📋 Recommendations:")
        for rec in detection_result['recommendations']:
            summary.append(f"  {rec}")
        
        return "\n".join(summary)
