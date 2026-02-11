"""
Enhanced Data Quality Reporter
Comprehensive data quality reporting with visualizations and detailed metrics.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

class EnhancedQualityReporter:
    """
    Enhanced data quality reporting with comprehensive metrics, visualizations, and actionable insights.
    """
    
    def __init__(self):
        self.report_generated = False
        self.quality_report = {}
    
    def generate_comprehensive_report(self, df: pd.DataFrame, context: str = "general") -> Dict[str, Any]:
        """
        Generate comprehensive data quality report.
        
        Args:
            df: Input dataframe
            context: Context for reporting ('general', 'glass', 'whonet', 'amr')
            
        Returns:
            Comprehensive quality report dictionary
        """
        if df is None or df.empty:
            return {'error': 'DataFrame is empty or None'}
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'summary': {},
            'completeness': {},
            'consistency': {},
            'validity': {},
            'accuracy': {},
            'uniqueness': {},
            'issues': [],
            'recommendations': [],
            'column_details': {},
            'visualizations': {}
        }
        
        # Basic statistics
        report['summary'] = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'total_cells': df.size,
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
        }
        
        # Completeness analysis
        report['completeness'] = self._analyze_completeness(df)
        
        # Consistency analysis
        report['consistency'] = self._analyze_consistency(df)
        
        # Validity analysis
        report['validity'] = self._analyze_validity(df, context)
        
        # Accuracy analysis
        report['accuracy'] = self._analyze_accuracy(df)
        
        # Uniqueness analysis
        report['uniqueness'] = self._analyze_uniqueness(df)
        
        # Column-level details
        report['column_details'] = self._analyze_columns(df, context)
        
        # Overall quality score
        report['overall_score'] = self._calculate_overall_score(report)
        
        # Issues and recommendations
        report['issues'] = self._identify_all_issues(report, df, context)
        report['recommendations'] = self._generate_recommendations(report, context)
        
        # Generate visualizations
        report['visualizations'] = self._generate_visualizations(df, report)
        
        self.quality_report = report
        self.report_generated = True
        
        return report
    
    def _analyze_completeness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive completeness analysis."""
        total_cells = df.size
        missing_cells = df.isna().sum().sum()
        completeness_pct = (1 - (missing_cells / total_cells)) * 100 if total_cells > 0 else 0
        
        # Column-level completeness
        column_completeness = {}
        for col in df.columns:
            missing = df[col].isna().sum()
            total = len(df)
            column_completeness[col] = {
                'missing_count': int(missing),
                'missing_pct': (missing / total * 100) if total > 0 else 0,
                'complete_pct': ((total - missing) / total * 100) if total > 0 else 0
            }
        
        # Row-level completeness
        row_completeness = df.notna().sum(axis=1) / len(df.columns) * 100
        
        return {
            'overall_pct': round(completeness_pct, 2),
            'missing_cells': int(missing_cells),
            'total_cells': int(total_cells),
            'column_level': column_completeness,
            'row_completeness_stats': {
                'mean': round(row_completeness.mean(), 2),
                'min': round(row_completeness.min(), 2),
                'max': round(row_completeness.max(), 2),
                'std': round(row_completeness.std(), 2)
            },
            'critical_columns': [col for col, stats in column_completeness.items() 
                               if stats['missing_pct'] > 50]
        }
    
    def _analyze_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive consistency analysis."""
        issues = []
        consistency_score = 100.0
        
        for col in df.columns:
            if df[col].dtype == 'object':
                values = df[col].dropna()
                if len(values) > 0:
                    # Case consistency
                    case_variations = {}
                    for val in values:
                        val_lower = str(val).lower()
                        if val_lower not in case_variations:
                            case_variations[val_lower] = []
                        case_variations[val_lower].append(str(val))
                    
                    inconsistent_cases = {k: v for k, v in case_variations.items() if len(set(v)) > 1}
                    if inconsistent_cases:
                        issues.append({
                            'column': col,
                            'type': 'case_inconsistency',
                            'count': len(inconsistent_cases),
                            'examples': list(inconsistent_cases.values())[:3]
                        })
                    
                    # Whitespace consistency
                    whitespace_issues = sum(1 for val in values if str(val) != str(val).strip())
                    if whitespace_issues > 0:
                        issues.append({
                            'column': col,
                            'type': 'whitespace_inconsistency',
                            'count': whitespace_issues
                        })
                    
                    # Format consistency (for dates, numbers stored as strings)
                    if col.lower().find('date') >= 0:
                        date_formats = set()
                        for val in values.head(100):
                            val_str = str(val)
                            # Try to detect date format
                            if '/' in val_str or '-' in val_str:
                                date_formats.add('has_separator')
                            if len(val_str) == 8 and val_str.isdigit():
                                date_formats.add('numeric_8')
                        
                        if len(date_formats) > 1:
                            issues.append({
                                'column': col,
                                'type': 'date_format_inconsistency',
                                'count': len(date_formats)
                            })
        
        if issues:
            consistency_score = max(0, 100 - (len(issues) * 10))
        
        return {
            'score': round(consistency_score, 2),
            'issues': issues,
            'issue_count': len(issues)
        }
    
    def _analyze_validity(self, df: pd.DataFrame, context: str) -> Dict[str, Any]:
        """Comprehensive validity analysis."""
        issues = []
        validity_score = 100.0
        
        # Context-specific validation rules
        validation_rules = self._get_validation_rules(context)
        
        for col in df.columns:
            col_lower = col.lower()
            
            # Check against context-specific rules
            if col in validation_rules:
                rules = validation_rules[col]
                invalid_count = 0
                
                for idx, value in df[col].items():
                    if pd.isna(value):
                        continue
                    
                    # Check allowed values
                    if 'allowed_values' in rules:
                        if str(value).upper() not in [v.upper() for v in rules['allowed_values']]:
                            invalid_count += 1
                    
                    # Check value range
                    if 'range' in rules and pd.api.types.is_numeric_dtype(df[col]):
                        min_val, max_val = rules['range']
                        try:
                            val = float(value)
                            if val < min_val or val > max_val:
                                invalid_count += 1
                        except (ValueError, TypeError):
                            invalid_count += 1
                
                if invalid_count > 0:
                    issues.append({
                        'column': col,
                        'type': 'invalid_values',
                        'count': invalid_count,
                        'rule': rules
                    })
            
            # General validity checks
            if df[col].dtype == 'object':
                # Check for suspicious characters
                suspicious_chars = ['<', '>', '|', '\\', '/', '\x00']
                for char in suspicious_chars:
                    count = df[col].astype(str).str.contains(char, regex=False, na=False).sum()
                    if count > 0:
                        issues.append({
                            'column': col,
                            'type': 'suspicious_characters',
                            'character': char,
                            'count': int(count)
                        })
        
        if issues:
            validity_score = max(0, 100 - (len(issues) * 5))
        
        return {
            'score': round(validity_score, 2),
            'issues': issues,
            'issue_count': len(issues)
        }
    
    def _analyze_accuracy(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive accuracy analysis."""
        issues = []
        accuracy_score = 100.0
        
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                values = df[col].dropna()
                if len(values) > 10:
                    # Outlier detection (using IQR method)
                    Q1 = values.quantile(0.25)
                    Q3 = values.quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outliers = values[(values < lower_bound) | (values > upper_bound)]
                    if len(outliers) > 0:
                        issues.append({
                            'column': col,
                            'type': 'outliers',
                            'count': len(outliers),
                            'outlier_pct': round(len(outliers) / len(values) * 100, 2)
                        })
        
        if issues:
            total_outliers = sum(issue['count'] for issue in issues)
            accuracy_score = max(0, 100 - (total_outliers * 0.1))
        
        return {
            'score': round(accuracy_score, 2),
            'issues': issues,
            'issue_count': len(issues)
        }
    
    def _analyze_uniqueness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive uniqueness analysis."""
        total_rows = len(df)
        duplicate_rows = df.duplicated().sum()
        uniqueness_pct = (1 - (duplicate_rows / total_rows)) * 100 if total_rows > 0 else 100
        
        # Check for potential key columns
        potential_keys = []
        for col in df.columns:
            unique_count = df[col].nunique()
            if unique_count == total_rows and df[col].notna().sum() == total_rows:
                potential_keys.append(col)
        
        return {
            'overall_pct': round(uniqueness_pct, 2),
            'duplicate_rows': int(duplicate_rows),
            'unique_rows': int(total_rows - duplicate_rows),
            'potential_key_columns': potential_keys
        }
    
    def _analyze_columns(self, df: pd.DataFrame, context: str) -> Dict[str, Any]:
        """Detailed column-level analysis."""
        column_details = {}
        
        for col in df.columns:
            details = {
                'dtype': str(df[col].dtype),
                'non_null_count': int(df[col].notna().sum()),
                'null_count': int(df[col].isna().sum()),
                'unique_count': int(df[col].nunique()),
                'completeness_pct': round((df[col].notna().sum() / len(df)) * 100, 2)
            }
            
            # Add statistics based on data type
            if pd.api.types.is_numeric_dtype(df[col]):
                details['statistics'] = {
                    'mean': round(df[col].mean(), 2) if df[col].notna().any() else None,
                    'median': round(df[col].median(), 2) if df[col].notna().any() else None,
                    'std': round(df[col].std(), 2) if df[col].notna().any() else None,
                    'min': round(df[col].min(), 2) if df[col].notna().any() else None,
                    'max': round(df[col].max(), 2) if df[col].notna().any() else None
                }
            else:
                # Most common values
                value_counts = df[col].value_counts().head(5)
                details['top_values'] = value_counts.to_dict()
            
            column_details[col] = details
        
        return column_details
    
    def _get_validation_rules(self, context: str) -> Dict[str, Dict]:
        """Get validation rules based on context."""
        rules = {}
        
        if context == 'glass':
            rules = {
                'Gender': {'allowed_values': ['M', 'F', 'O', 'U']},
                'Age in years': {'range': (0, 120)}
            }
        elif context == 'whonet':
            rules = {
                'SIR': {'allowed_values': ['S', 'R', 'I', 'ND', 'NM']},
                'AGE': {'range': (0, 120)}
            }
        
        return rules
    
    def _calculate_overall_score(self, report: Dict[str, Any]) -> float:
        """Calculate overall quality score."""
        weights = {
            'completeness': 0.30,
            'consistency': 0.20,
            'validity': 0.20,
            'accuracy': 0.15,
            'uniqueness': 0.15
        }
        
        scores = {
            'completeness': report['completeness']['overall_pct'],
            'consistency': report['consistency']['score'],
            'validity': report['validity']['score'],
            'accuracy': report['accuracy']['score'],
            'uniqueness': report['uniqueness']['overall_pct']
        }
        
        overall = sum(scores[metric] * weights[metric] for metric in weights)
        return round(overall, 2)
    
    def _identify_all_issues(self, report: Dict[str, Any], df: pd.DataFrame, context: str) -> List[Dict[str, Any]]:
        """Identify all data quality issues."""
        issues = []
        
        # Completeness issues
        if report['completeness']['overall_pct'] < 80:
            issues.append({
                'severity': 'high' if report['completeness']['overall_pct'] < 50 else 'medium',
                'category': 'completeness',
                'message': f"Data completeness is {report['completeness']['overall_pct']:.1f}% (target: >80%)",
                'affected_columns': report['completeness'].get('critical_columns', [])
            })
        
        # Consistency issues
        if report['consistency']['issue_count'] > 0:
            issues.append({
                'severity': 'medium',
                'category': 'consistency',
                'message': f"Found {report['consistency']['issue_count']} consistency issues",
                'details': report['consistency']['issues']
            })
        
        # Validity issues
        if report['validity']['issue_count'] > 0:
            issues.append({
                'severity': 'high',
                'category': 'validity',
                'message': f"Found {report['validity']['issue_count']} validity issues",
                'details': report['validity']['issues']
            })
        
        # Accuracy issues
        if report['accuracy']['issue_count'] > 0:
            issues.append({
                'severity': 'low',
                'category': 'accuracy',
                'message': f"Found {report['accuracy']['issue_count']} potential accuracy issues (outliers)",
                'details': report['accuracy']['issues']
            })
        
        # Uniqueness issues
        if report['uniqueness']['duplicate_rows'] > 0:
            issues.append({
                'severity': 'medium',
                'category': 'uniqueness',
                'message': f"Found {report['uniqueness']['duplicate_rows']} duplicate rows",
            })
        
        return issues
    
    def _generate_recommendations(self, report: Dict[str, Any], context: str) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Completeness recommendations
        if report['completeness']['overall_pct'] < 80:
            recommendations.append(
                f"Improve data completeness: Currently {report['completeness']['overall_pct']:.1f}%. "
                f"Focus on columns with >50% missing values: {', '.join(report['completeness'].get('critical_columns', [])[:5])}"
            )
        
        # Consistency recommendations
        if report['consistency']['issue_count'] > 0:
            recommendations.append(
                "Standardize data formats: Fix case inconsistencies, whitespace issues, and format variations"
            )
        
        # Validity recommendations
        if report['validity']['issue_count'] > 0:
            recommendations.append(
                "Fix invalid values: Review and correct values that don't meet validation rules"
            )
        
        # Uniqueness recommendations
        if report['uniqueness']['duplicate_rows'] > 0:
            recommendations.append(
                f"Remove or merge {report['uniqueness']['duplicate_rows']} duplicate rows"
            )
        
        return recommendations
    
    def _generate_visualizations(self, df: pd.DataFrame, report: Dict[str, Any]) -> Dict[str, Any]:
        """Generate visualization data."""
        visualizations = {}
        
        # Completeness heatmap
        completeness_data = []
        for col, stats in report['completeness']['column_level'].items():
            completeness_data.append({
                'column': col,
                'completeness': stats['complete_pct']
            })
        
        if completeness_data:
            completeness_df = pd.DataFrame(completeness_data)
            visualizations['completeness_chart'] = {
                'type': 'bar',
                'data': completeness_df.to_dict('records')
            }
        
        return visualizations
    
    def display_comprehensive_report(self, report: Dict[str, Any]):
        """Display comprehensive quality report in Streamlit."""
        st.markdown("## 📊 Comprehensive Data Quality Report")
        
        # Overall score
        score = report.get('overall_score', 0)
        score_color = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Overall Quality Score", f"{score:.1f}%", delta=None)
            st.progress(score / 100)
        
        with col2:
            st.metric("Total Rows", report['summary']['total_rows'])
        with col3:
            st.metric("Total Columns", report['summary']['total_columns'])
        with col4:
            st.metric("Memory Usage", f"{report['summary']['memory_usage_mb']:.1f} MB")
        
        # Quality dimensions
        st.markdown("### Quality Dimensions")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Completeness", f"{report['completeness']['overall_pct']:.1f}%")
        with col2:
            st.metric("Consistency", f"{report['consistency']['score']:.1f}%")
        with col3:
            st.metric("Validity", f"{report['validity']['score']:.1f}%")
        with col4:
            st.metric("Accuracy", f"{report['accuracy']['score']:.1f}%")
        with col5:
            st.metric("Uniqueness", f"{report['uniqueness']['overall_pct']:.1f}%")
        
        # Issues
        if report.get('issues'):
            st.markdown("### 🚨 Issues Found")
            for issue in report['issues']:
                severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(issue['severity'], "⚪")
                st.write(f"{severity_icon} **{issue['category'].title()}**: {issue['message']}")
        
        # Recommendations
        if report.get('recommendations'):
            st.markdown("### 💡 Recommendations")
            for i, rec in enumerate(report['recommendations'], 1):
                st.write(f"{i}. {rec}")
        
        # Column details
        with st.expander("📋 Column Details", expanded=False):
            column_details_df = pd.DataFrame(report['column_details']).T
            st.dataframe(column_details_df, use_container_width=True)

