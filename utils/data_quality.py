"""
Data Quality Assessment Module
Provides comprehensive data quality scoring and analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
import streamlit as st

class DataQualityAssessor:
    """Assesses data quality and provides scoring metrics."""
    
    def __init__(self):
        self.quality_metrics = {
            'completeness': 0.0,
            'consistency': 0.0,
            'accuracy': 0.0,
            'validity': 0.0,
            'uniqueness': 0.0,
            'overall': 0.0
        }
    
    def assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Assess overall data quality of a dataframe.
        
        Args:
            df: Input dataframe
            
        Returns:
            Dictionary containing quality metrics and recommendations
        """
        results = {
            'metrics': {},
            'issues': [],
            'recommendations': [],
            'score': 0.0
        }
        
        # Calculate individual metrics
        completeness = self._calculate_completeness(df)
        consistency = self._calculate_consistency(df)
        accuracy = self._calculate_accuracy(df)
        validity = self._calculate_validity(df)
        uniqueness = self._calculate_uniqueness(df)
        
        # Store metrics
        results['metrics'] = {
            'completeness': completeness,
            'consistency': consistency,
            'accuracy': accuracy,
            'validity': validity,
            'uniqueness': uniqueness
        }
        
        # Calculate overall score (weighted average)
        weights = {'completeness': 0.25, 'consistency': 0.20, 'accuracy': 0.20, 
                  'validity': 0.20, 'uniqueness': 0.15}
        overall_score = sum(score * weights[metric] for metric, score in results['metrics'].items())
        results['score'] = overall_score
        
        # Generate issues and recommendations
        results['issues'] = self._identify_issues(df, results['metrics'])
        results['recommendations'] = self._generate_recommendations(results['issues'])
        
        return results
    
    def _calculate_completeness(self, df: pd.DataFrame) -> float:
        """Calculate completeness score (0-1)."""
        total_cells = df.size
        missing_cells = df.isna().sum().sum()
        completeness = 1 - (missing_cells / total_cells) if total_cells > 0 else 0
        return round(completeness, 3)
    
    def _calculate_consistency(self, df: pd.DataFrame) -> float:
        """Calculate consistency score (0-1)."""
        consistency_issues = 0
        total_checks = 0
        
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check for inconsistent formatting
                unique_values = df[col].dropna().unique()
                if len(unique_values) > 0:
                    # Check for mixed case inconsistencies
                    case_variations = set(str(val).lower() for val in unique_values)
                    if len(case_variations) < len(unique_values):
                        consistency_issues += 1
                    total_checks += 1
                    
                    # Check for whitespace inconsistencies
                    whitespace_issues = sum(1 for val in unique_values if str(val) != str(val).strip())
                    if whitespace_issues > 0:
                        consistency_issues += 1
                    total_checks += 1
        
        consistency = 1 - (consistency_issues / total_checks) if total_checks > 0 else 1
        return round(consistency, 3)
    
    def _calculate_accuracy(self, df: pd.DataFrame) -> float:
        """Calculate accuracy score (0-1)."""
        accuracy_issues = 0
        total_checks = 0
        
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                # Check for outliers (values beyond 3 standard deviations)
                if len(df[col].dropna()) > 0:
                    mean_val = df[col].mean()
                    std_val = df[col].std()
                    if std_val > 0:
                        outliers = abs(df[col] - mean_val) > 3 * std_val
                        accuracy_issues += outliers.sum()
                        total_checks += len(df[col].dropna())
        
        accuracy = 1 - (accuracy_issues / total_checks) if total_checks > 0 else 1
        return round(accuracy, 3)
    
    def _calculate_validity(self, df: pd.DataFrame) -> float:
        """Calculate validity score (0-1)."""
        validity_issues = 0
        total_checks = 0
        
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check for invalid characters or patterns
                for val in df[col].dropna():
                    if isinstance(val, str):
                        # Check for suspicious patterns
                        if any(char in val for char in ['<', '>', '|', '\\', '/']):
                            validity_issues += 1
                        total_checks += 1
        
        validity = 1 - (validity_issues / total_checks) if total_checks > 0 else 1
        return round(validity, 3)
    
    def _calculate_uniqueness(self, df: pd.DataFrame) -> float:
        """Calculate uniqueness score (0-1)."""
        total_rows = len(df)
        duplicate_rows = df.duplicated().sum()
        uniqueness = 1 - (duplicate_rows / total_rows) if total_rows > 0 else 1
        return round(uniqueness, 3)
    
    def _identify_issues(self, df: pd.DataFrame, metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """Identify specific data quality issues."""
        issues = []
        
        # Completeness issues
        if metrics['completeness'] < 0.9:
            missing_cols = df.columns[df.isna().all()].tolist()
            if missing_cols:
                issues.append({
                    'type': 'completeness',
                    'severity': 'high',
                    'message': f"Empty columns found: {', '.join(missing_cols)}",
                    'count': len(missing_cols)
                })
        
        # Consistency issues
        if metrics['consistency'] < 0.8:
            issues.append({
                'type': 'consistency',
                'severity': 'medium',
                'message': "Inconsistent formatting detected in text columns",
                'count': 1
            })
        
        # Accuracy issues
        if metrics['accuracy'] < 0.8:
            issues.append({
                'type': 'accuracy',
                'severity': 'medium',
                'message': "Potential outliers detected in numeric columns",
                'count': 1
            })
        
        # Uniqueness issues
        if metrics['uniqueness'] < 0.95:
            duplicate_count = df.duplicated().sum()
            issues.append({
                'type': 'uniqueness',
                'severity': 'low',
                'message': f"Duplicate rows found: {duplicate_count}",
                'count': duplicate_count
            })
        
        return issues
    
    def _generate_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on identified issues."""
        recommendations = []
        
        for issue in issues:
            if issue['type'] == 'completeness':
                recommendations.append("Consider removing empty columns or filling missing values")
            elif issue['type'] == 'consistency':
                recommendations.append("Standardize text formatting using data transformations")
            elif issue['type'] == 'accuracy':
                recommendations.append("Review and validate outlier values")
            elif issue['type'] == 'uniqueness':
                recommendations.append("Remove duplicate rows or investigate why they exist")
        
        return recommendations
    
    def show_quality_report(self, quality_results: Dict[str, Any]) -> None:
        """Display data quality report in Streamlit."""
        st.markdown("### 📊 Data Quality Report")
        
        # Overall score
        score = quality_results['score']
        score_color = "green" if score >= 0.8 else "orange" if score >= 0.6 else "red"
        st.markdown(f"**Overall Quality Score: {score:.1%}**")
        st.progress(score)
        
        # Individual metrics
        st.markdown("#### Quality Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Completeness", f"{quality_results['metrics']['completeness']:.1%}")
            st.metric("Consistency", f"{quality_results['metrics']['consistency']:.1%}")
        
        with col2:
            st.metric("Accuracy", f"{quality_results['metrics']['accuracy']:.1%}")
            st.metric("Validity", f"{quality_results['metrics']['validity']:.1%}")
        
        with col3:
            st.metric("Uniqueness", f"{quality_results['metrics']['uniqueness']:.1%}")
        
        # Issues
        if quality_results['issues']:
            st.markdown("#### 🚨 Issues Found")
            for issue in quality_results['issues']:
                severity_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                st.write(f"{severity_color.get(issue['severity'], '⚪')} {issue['message']}")
        
        # Recommendations
        if quality_results['recommendations']:
            st.markdown("#### 💡 Recommendations")
            for i, rec in enumerate(quality_results['recommendations'], 1):
                st.write(f"{i}. {rec}")
