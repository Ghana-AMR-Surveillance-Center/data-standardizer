"""
AMR-Specific Data Quality Module
Comprehensive data quality assessment specifically designed for AMR surveillance data
addressing common issues in African laboratory settings.

This module addresses:
- Inconsistent data collection and reporting
- Limited laboratory capacity and quality assurance
- Fragmented data management systems
- Variability in antimicrobial susceptibility testing methods
- One Health data integration
- GLASS submission readiness
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import re
from datetime import datetime
import streamlit as st

class AMRDataQuality:
    """
    Comprehensive AMR data quality assessment and improvement.
    Specifically designed for African laboratory data quality issues.
    """
    
    # GLASS Required Fields with completeness thresholds
    GLASS_REQUIRED_FIELDS = {
        'Organism': {
            'required': True,
            'completeness_threshold': 95.0,  # Must have organism for 95% of records
            'description': 'Organism name (e.g., E. coli, S. aureus)'
        },
        'Specimen type': {
            'required': True,
            'completeness_threshold': 90.0,
            'description': 'Type of specimen (e.g., Blood, Urine, Sputum)'
        },
        'Specimen date': {
            'required': True,
            'completeness_threshold': 85.0,
            'description': 'Date when specimen was collected'
        },
        'Age in years': {
            'required': True,
            'completeness_threshold': 80.0,
            'description': 'Patient age in years'
        },
        'Gender': {
            'required': True,
            'completeness_threshold': 80.0,
            'description': 'Patient gender (M, F, O, U)'
        }
    }
    
    # Common African lab data quality issues
    COMMON_ISSUES = {
        'organism_variations': [
            'e coli', 'e.coli', 'ecoli', 'escherichia coli',
            's aureus', 's.aureus', 'saureus', 'staphylococcus aureus',
            'k pneumoniae', 'k.pneumoniae', 'klebsiella pneumoniae'
        ],
        'specimen_variations': [
            'bld', 'bl', 'blood', 'whole blood',
            'ur', 'urine', 'urine sample',
            'sput', 'sputum', 'sputum sample'
        ],
        'invalid_organisms': [
            'xxx', 'test', 'no growth', 'contamination',
            'not applicable', 'na', 'n/a', 'negative',
            'mixed', 'contaminated', 'no isolate'
        ],
        'date_formats': [
            'dd/mm/yyyy', 'mm/dd/yyyy', 'yyyy-mm-dd',
            'dd-mm-yyyy', 'dd.mm.yyyy', 'yyyy/mm/dd'
        ],
        'antimicrobial_result_variations': [
            's', 'susceptible', 'susceptibility',
            'r', 'resistant', 'resistance',
            'i', 'intermediate', 'indeterminate',
            'nd', 'not determined', 'not done',
            'nm', 'not measured', 'not measured'
        ]
    }
    
    # One Health categories
    ONE_HEALTH_CATEGORIES = {
        'human': ['blood', 'urine', 'sputum', 'csf', 'wound', 'stool', 'pus', 'tissue'],
        'animal': ['cecum', 'rectal', 'nasal', 'milk', 'meat', 'feces'],
        'environmental': ['water', 'soil', 'surface', 'air', 'food']
    }
    
    def __init__(self):
        """Initialize AMR data quality assessor."""
        self.quality_report = {}
        self.issues_found = []
        self.recommendations = []
    
    def assess_amr_data_quality(self, df: pd.DataFrame, context: str = 'glass') -> Dict[str, Any]:
        """
        Comprehensive AMR data quality assessment.
        
        Args:
            df: Input dataframe with AMR data
            context: Assessment context ('glass', 'whonet', 'general')
            
        Returns:
            Comprehensive quality assessment report
        """
        if df is None or df.empty:
            return {'error': 'DataFrame is empty or None'}
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'summary': {},
            'glass_readiness': {},
            'completeness': {},
            'consistency': {},
            'validity': {},
            'amr_specific': {},
            'one_health': {},
            'issues': [],
            'recommendations': [],
            'quality_score': 0.0,
            'glass_submission_ready': False
        }
        
        # Basic statistics
        report['summary'] = self._calculate_basic_stats(df)
        
        # GLASS readiness assessment
        report['glass_readiness'] = self._assess_glass_readiness(df)
        
        # Completeness assessment (AMR-specific)
        report['completeness'] = self._assess_amr_completeness(df)
        
        # Consistency assessment
        report['consistency'] = self._assess_amr_consistency(df)
        
        # Validity assessment
        report['validity'] = self._assess_amr_validity(df, context)
        
        # AMR-specific quality checks
        report['amr_specific'] = self._assess_amr_specific_quality(df)
        
        # One Health categorization
        report['one_health'] = self._categorize_one_health(df)
        
        # Calculate overall quality score
        report['quality_score'] = self._calculate_amr_quality_score(report)
        
        # Determine GLASS submission readiness
        report['glass_submission_ready'] = self._is_glass_ready(report)
        
        # Generate issues and recommendations
        report['issues'] = self._identify_amr_issues(report, df)
        report['recommendations'] = self._generate_amr_recommendations(report, df)
        
        self.quality_report = report
        return report
    
    def _calculate_basic_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate basic statistics."""
        return {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'total_cells': df.size,
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
            'date_range': self._get_date_range(df) if any('date' in col.lower() for col in df.columns) else None
        }
    
    def _get_date_range(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Get date range from date columns."""
        date_cols = [col for col in df.columns if 'date' in col.lower()]
        if not date_cols:
            return None
        
        dates = []
        for col in date_cols:
            try:
                date_series = pd.to_datetime(df[col], errors='coerce')
                valid_dates = date_series.dropna()
                if len(valid_dates) > 0:
                    dates.extend(valid_dates.tolist())
            except:
                pass
        
        if dates:
            return {
                'earliest': min(dates).isoformat() if dates else None,
                'latest': max(dates).isoformat() if dates else None,
                'span_days': (max(dates) - min(dates)).days if len(dates) > 1 else 0
            }
        return None
    
    def _assess_glass_readiness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess GLASS submission readiness."""
        readiness = {
            'score': 0.0,
            'required_fields_present': [],
            'required_fields_missing': [],
            'completeness_scores': {},
            'validation_passed': False,
            'critical_issues': []
        }
        
        # Import column utilities for case-insensitive matching
        from .column_utils import find_column_case_insensitive
        
        # Check required fields (case-insensitive matching)
        for field, requirements in self.GLASS_REQUIRED_FIELDS.items():
            actual_field = find_column_case_insensitive(df, field)
            if actual_field is not None:
                readiness['required_fields_present'].append(field)
                # Calculate completeness
                completeness = (df[actual_field].notna().sum() / len(df)) * 100
                readiness['completeness_scores'][field] = completeness
                
                # Check if meets threshold
                threshold = requirements.get('completeness_threshold', 80.0)
                if completeness < threshold:
                    readiness['critical_issues'].append(
                        f"{field}: {completeness:.1f}% complete (threshold: {threshold}%)"
                    )
            else:
                readiness['required_fields_missing'].append(field)
                readiness['critical_issues'].append(f"Missing required field: {field}")
        
        # Calculate readiness score
        if len(self.GLASS_REQUIRED_FIELDS) > 0:
            present_pct = len(readiness['required_fields_present']) / len(self.GLASS_REQUIRED_FIELDS) * 100
            
            # Average completeness of present fields
            if readiness['completeness_scores']:
                avg_completeness = np.mean(list(readiness['completeness_scores'].values()))
                readiness['score'] = (present_pct * 0.5) + (avg_completeness * 0.5)
            else:
                readiness['score'] = present_pct
        
        # Validation passed if score >= 80 and no critical issues
        readiness['validation_passed'] = (
            readiness['score'] >= 80.0 and 
            len(readiness['critical_issues']) == 0
        )
        
        return readiness
    
    def _assess_amr_completeness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess AMR-specific completeness."""
        completeness = {
            'overall_pct': 0.0,
            'critical_fields': {},
            'antimicrobial_completeness': {},
            'organism_completeness': 0.0,
            'specimen_completeness': 0.0,
            'patient_info_completeness': 0.0
        }
        
        # Overall completeness
        total_cells = df.size
        missing_cells = df.isna().sum().sum()
        completeness['overall_pct'] = round((1 - (missing_cells / total_cells)) * 100, 2) if total_cells > 0 else 0
        
        # Critical fields completeness
        for field in self.GLASS_REQUIRED_FIELDS.keys():
            if field in df.columns:
                field_completeness = (df[field].notna().sum() / len(df)) * 100
                completeness['critical_fields'][field] = round(field_completeness, 2)
        
        # Antimicrobial completeness
        antimicrobial_cols = self._identify_antimicrobial_columns(df)
        if antimicrobial_cols:
            for col in antimicrobial_cols:
                col_completeness = (df[col].notna().sum() / len(df)) * 100
                completeness['antimicrobial_completeness'][col] = round(col_completeness, 2)
        
        # Organism completeness
        if 'Organism' in df.columns:
            completeness['organism_completeness'] = round(
                (df['Organism'].notna().sum() / len(df)) * 100, 2
            )
        
        # Specimen completeness
        specimen_cols = [col for col in df.columns if 'specimen' in col.lower()]
        if specimen_cols:
            specimen_completeness = []
            for col in specimen_cols:
                col_completeness = (df[col].notna().sum() / len(df)) * 100
                specimen_completeness.append(col_completeness)
            completeness['specimen_completeness'] = round(np.mean(specimen_completeness), 2) if specimen_completeness else 0
        
        # Patient info completeness (age, gender)
        patient_cols = []
        if 'Age in years' in df.columns or any('age' in col.lower() for col in df.columns):
            age_col = 'Age in years' if 'Age in years' in df.columns else [col for col in df.columns if 'age' in col.lower()][0]
            patient_cols.append(age_col)
        if 'Gender' in df.columns or any('gender' in col.lower() or 'sex' in col.lower() for col in df.columns):
            gender_col = 'Gender' if 'Gender' in df.columns else [col for col in df.columns if 'gender' in col.lower() or 'sex' in col.lower()][0]
            patient_cols.append(gender_col)
        
        if patient_cols:
            patient_completeness = []
            for col in patient_cols:
                col_completeness = (df[col].notna().sum() / len(df)) * 100
                patient_completeness.append(col_completeness)
            completeness['patient_info_completeness'] = round(np.mean(patient_completeness), 2) if patient_completeness else 0
        
        return completeness
    
    def _assess_amr_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess AMR-specific consistency issues."""
        consistency = {
            'score': 100.0,
            'organism_consistency': {},
            'specimen_consistency': {},
            'antimicrobial_consistency': {},
            'date_consistency': {},
            'issues': []
        }
        
        # Organism consistency (check for variations)
        if 'Organism' in df.columns:
            organisms = df['Organism'].dropna().unique()
            variations = {}
            for org in organisms:
                org_lower = str(org).lower().strip()
                # Check for common variations
                for variation in self.COMMON_ISSUES['organism_variations']:
                    if variation in org_lower:
                        if variation not in variations:
                            variations[variation] = []
                        variations[variation].append(str(org))
            
            if variations:
                consistency['organism_consistency']['variations_found'] = len(variations)
                consistency['issues'].append(f"Found {len(variations)} organism name variations")
        
        # Specimen consistency
        specimen_cols = [col for col in df.columns if 'specimen' in col.lower() and 'type' in col.lower()]
        if specimen_cols:
            for col in specimen_cols:
                specimens = df[col].dropna().unique()
                case_variations = {}
                for spec in specimens:
                    spec_lower = str(spec).lower().strip()
                    if spec_lower not in case_variations:
                        case_variations[spec_lower] = []
                    case_variations[spec_lower].append(str(spec))
                
                inconsistent = {k: v for k, v in case_variations.items() if len(set(v)) > 1}
                if inconsistent:
                    consistency['specimen_consistency'][col] = len(inconsistent)
                    consistency['issues'].append(f"Found case inconsistencies in {col}")
        
        # Antimicrobial result consistency
        antimicrobial_cols = self._identify_antimicrobial_columns(df)
        if antimicrobial_cols:
            for col in antimicrobial_cols[:5]:  # Check first 5 to avoid too much processing
                values = df[col].dropna().unique()
                # Check for standard S/R/I/ND/NM format
                non_standard = [v for v in values if str(v).upper() not in ['S', 'R', 'I', 'ND', 'NM', 'MS', 'MR']]
                if non_standard:
                    consistency['antimicrobial_consistency'][col] = len(non_standard)
                    consistency['issues'].append(f"Non-standard values in {col}: {len(non_standard)}")
        
        # Date consistency
        date_cols = [col for col in df.columns if 'date' in col.lower()]
        if date_cols:
            for col in date_cols:
                # Try to detect date format variations
                sample_dates = df[col].dropna().head(20)
                formats_detected = set()
                for date_val in sample_dates:
                    date_str = str(date_val)
                    if '/' in date_str:
                        formats_detected.add('slash')
                    elif '-' in date_str:
                        formats_detected.add('dash')
                    elif '.' in date_str:
                        formats_detected.add('dot')
                
                if len(formats_detected) > 1:
                    consistency['date_consistency'][col] = list(formats_detected)
                    consistency['issues'].append(f"Multiple date formats detected in {col}")
        
        # Calculate consistency score
        issue_count = len(consistency['issues'])
        consistency['score'] = max(0, 100 - (issue_count * 10))
        
        return consistency
    
    def _assess_amr_validity(self, df: pd.DataFrame, context: str) -> Dict[str, Any]:
        """Assess AMR-specific validity."""
        validity = {
            'score': 100.0,
            'invalid_organisms': [],
            'invalid_ages': [],
            'invalid_genders': [],
            'invalid_dates': [],
            'invalid_antimicrobial_results': {},
            'issues': []
        }
        
        # Import column utilities for case-insensitive matching
        from .column_utils import find_column_case_insensitive, normalize_column_name
        
        # Check for invalid organisms (case-insensitive)
        organism_col = find_column_case_insensitive(df, 'Organism')
        if organism_col is not None:
            invalid_orgs = df[df[organism_col].astype(str).str.lower().isin(
                [x.lower() for x in self.COMMON_ISSUES['invalid_organisms']]
            )]
            if len(invalid_orgs) > 0:
                validity['invalid_organisms'] = invalid_orgs[organism_col].unique().tolist()
                validity['issues'].append(f"Found {len(invalid_orgs)} records with invalid organisms")
        
        # Check age validity (case-insensitive)
        age_cols = [col for col in df.columns if 'age' in normalize_column_name(col)]
        for col in age_cols:
            try:
                ages = pd.to_numeric(df[col], errors='coerce')
                invalid_mask = (ages < 0) | (ages > 120) | ages.isna()
                invalid_ages = df[invalid_mask]
                if len(invalid_ages) > 0 and col in df.columns:
                    validity['invalid_ages'].extend(invalid_ages.index.tolist())
                    validity['issues'].append(f"Found {len(invalid_ages)} records with invalid ages in {col}")
            except:
                pass
        
        # Check gender validity (case-insensitive)
        gender_cols = [col for col in df.columns if 'gender' in normalize_column_name(col) or 'sex' in normalize_column_name(col)]
        for col in gender_cols:
            valid_genders = ['M', 'F', 'O', 'U', 'Male', 'Female', 'Other', 'Unknown']
            invalid_genders = df[~df[col].astype(str).str.upper().isin([g.upper() for g in valid_genders])]
            if len(invalid_genders) > 0:
                validity['invalid_genders'].extend(invalid_genders.index.tolist())
                validity['issues'].append(f"Found {len(invalid_genders)} records with invalid gender values in {col}")
        
        # Check date validity (case-insensitive)
        date_cols = [col for col in df.columns if 'date' in normalize_column_name(col)]
        for col in date_cols:
            try:
                dates = pd.to_datetime(df[col], errors='coerce')
                invalid_dates = df[dates.isna() & df[col].notna()]
                if len(invalid_dates) > 0:
                    validity['invalid_dates'].extend(invalid_dates.index.tolist())
                    validity['issues'].append(f"Found {len(invalid_dates)} records with invalid dates in {col}")
            except:
                pass
        
        # Check antimicrobial result validity
        antimicrobial_cols = self._identify_antimicrobial_columns(df)
        for col in antimicrobial_cols[:10]:  # Check first 10
            valid_values = ['S', 'R', 'I', 'ND', 'NM', 'MS', 'MR', 's', 'r', 'i', 'nd', 'nm']
            values = df[col].dropna().astype(str).str.upper()
            invalid = ~values.isin([v.upper() for v in valid_values])
            invalid_count = invalid.sum()
            if invalid_count > 0:
                validity['invalid_antimicrobial_results'][col] = invalid_count
                validity['issues'].append(f"Found {invalid_count} invalid antimicrobial results in {col}")
        
        # Calculate validity score
        issue_count = len(validity['issues'])
        validity['score'] = max(0, 100 - (issue_count * 15))
        
        return validity
    
    def _assess_amr_specific_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess AMR-specific quality metrics."""
        amr_quality = {
            'organism_diversity': 0,
            'antimicrobial_coverage': 0,
            'specimen_diversity': 0,
            'temporal_coverage': {},
            'data_representativeness': {}
        }
        
        # Import column utilities for case-insensitive matching
        from .column_utils import find_column_case_insensitive, normalize_column_name
        
        # Organism diversity (case-insensitive)
        organism_col = find_column_case_insensitive(df, 'Organism')
        if organism_col is not None:
            invalid_orgs_lower = [x.lower() for x in self.COMMON_ISSUES['invalid_organisms']]
            valid_mask = ~df[organism_col].astype(str).str.lower().isin(invalid_orgs_lower)
            valid_organisms = df[valid_mask][organism_col]
            amr_quality['organism_diversity'] = valid_organisms.nunique()
        
        # Antimicrobial coverage
        antimicrobial_cols = self._identify_antimicrobial_columns(df)
        amr_quality['antimicrobial_coverage'] = len(antimicrobial_cols)
        
        # Specimen diversity (case-insensitive)
        specimen_cols = [col for col in df.columns if 'specimen' in normalize_column_name(col) and 'type' in normalize_column_name(col)]
        if specimen_cols:
            for col in specimen_cols:
                amr_quality['specimen_diversity'] = df[col].nunique()
                break
        
        # Temporal coverage (case-insensitive)
        date_cols = [col for col in df.columns if 'date' in normalize_column_name(col)]
        if date_cols:
            for col in date_cols:
                try:
                    dates = pd.to_datetime(df[col], errors='coerce').dropna()
                    if len(dates) > 0:
                        amr_quality['temporal_coverage'] = {
                            'earliest': dates.min().isoformat(),
                            'latest': dates.max().isoformat(),
                            'span_months': (dates.max() - dates.min()).days / 30 if len(dates) > 1 else 0,
                            'records_with_dates': len(dates),
                            'records_total': len(df)
                        }
                    break
                except:
                    pass
        
        return amr_quality
    
    def _categorize_one_health(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Categorize data by One Health domains."""
        one_health = {
            'human': 0,
            'animal': 0,
            'environmental': 0,
            'unknown': 0,
            'breakdown': {}
        }
        
        specimen_cols = [col for col in df.columns if 'specimen' in col.lower() and 'type' in col.lower()]
        if not specimen_cols:
            return one_health
        
        col = specimen_cols[0]
        specimens = df[col].dropna().astype(str).str.lower()
        
        for category, keywords in self.ONE_HEALTH_CATEGORIES.items():
            count = specimens.str.contains('|'.join(keywords), case=False, na=False).sum()
            one_health[category] = count
            one_health['breakdown'][category] = {
                'count': count,
                'percentage': round((count / len(df)) * 100, 2) if len(df) > 0 else 0
            }
        
        # Unknown category
        total_categorized = sum(one_health[cat] for cat in ['human', 'animal', 'environmental'])
        one_health['unknown'] = len(df) - total_categorized
        one_health['breakdown']['unknown'] = {
            'count': one_health['unknown'],
            'percentage': round((one_health['unknown'] / len(df)) * 100, 2) if len(df) > 0 else 0
        }
        
        return one_health
    
    def _identify_antimicrobial_columns(self, df: pd.DataFrame) -> List[str]:
        """Identify antimicrobial susceptibility columns (case-insensitive)."""
        from .column_utils import normalize_column_name
        
        antimicrobial_indicators = [
            '_sir', '_nd', '_nm', '_r', '_s', '_i',
            'ampicillin', 'amoxicillin', 'cefuroxime', 'cefotaxime', 'ceftriaxone',
            'gentamicin', 'ciprofloxacin', 'meropenem', 'imipenem', 'vancomycin',
            'azithromycin', 'erythromycin', 'clindamycin', 'tetracycline', 'chloramphenicol'
        ]
        
        antimicrobial_cols = []
        for col in df.columns:
            col_normalized = normalize_column_name(col)  # Case-insensitive, strip whitespace
            if any(indicator in col_normalized for indicator in antimicrobial_indicators):
                antimicrobial_cols.append(col)
        
        return antimicrobial_cols
    
    def _calculate_amr_quality_score(self, report: Dict[str, Any]) -> float:
        """Calculate overall AMR quality score."""
        weights = {
            'glass_readiness': 0.30,
            'completeness': 0.25,
            'consistency': 0.20,
            'validity': 0.15,
            'amr_specific': 0.10
        }
        
        scores = {
            'glass_readiness': report['glass_readiness']['score'],
            'completeness': report['completeness']['overall_pct'],
            'consistency': report['consistency']['score'],
            'validity': report['validity']['score'],
            'amr_specific': min(100, (
                (report['amr_specific']['organism_diversity'] / 10 * 30) +
                (min(report['amr_specific']['antimicrobial_coverage'] / 20, 1) * 40) +
                (min(report['amr_specific']['specimen_diversity'] / 10, 1) * 30)
            ))
        }
        
        overall_score = sum(scores[metric] * weights[metric] for metric in weights)
        return round(overall_score, 2)
    
    def _is_glass_ready(self, report: Dict[str, Any]) -> bool:
        """Determine if data is GLASS submission ready."""
        return (
            report['glass_readiness']['validation_passed'] and
            report['quality_score'] >= 75.0 and
            len(report['glass_readiness']['critical_issues']) == 0
        )
    
    def _identify_amr_issues(self, report: Dict[str, Any], df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify all AMR-specific issues."""
        issues = []
        
        # GLASS readiness issues
        if not report['glass_readiness']['validation_passed']:
            issues.append({
                'severity': 'high',
                'category': 'glass_readiness',
                'message': 'Data does not meet GLASS submission requirements',
                'details': report['glass_readiness']['critical_issues']
            })
        
        # Completeness issues
        if report['completeness']['overall_pct'] < 80:
            issues.append({
                'severity': 'high' if report['completeness']['overall_pct'] < 60 else 'medium',
                'category': 'completeness',
                'message': f"Data completeness is {report['completeness']['overall_pct']:.1f}% (target: >80%)",
                'details': report['completeness']['critical_fields']
            })
        
        # Consistency issues
        if report['consistency']['score'] < 80:
            issues.append({
                'severity': 'medium',
                'category': 'consistency',
                'message': f"Data consistency score is {report['consistency']['score']:.1f}%",
                'details': report['consistency']['issues']
            })
        
        # Validity issues
        if report['validity']['score'] < 80:
            issues.append({
                'severity': 'high',
                'category': 'validity',
                'message': f"Data validity score is {report['validity']['score']:.1f}%",
                'details': report['validity']['issues']
            })
        
        return issues
    
    def _generate_amr_recommendations(self, report: Dict[str, Any], df: pd.DataFrame) -> List[str]:
        """Generate AMR-specific recommendations."""
        recommendations = []
        
        # GLASS readiness recommendations
        if not report['glass_readiness']['validation_passed']:
            if report['glass_readiness']['required_fields_missing']:
                recommendations.append(
                    f"Add missing required fields: {', '.join(report['glass_readiness']['required_fields_missing'])}"
                )
            if report['glass_readiness']['critical_issues']:
                recommendations.append(
                    "Improve completeness of required fields to meet GLASS thresholds"
                )
        
        # Completeness recommendations
        if report['completeness']['overall_pct'] < 80:
            recommendations.append(
                f"Improve overall data completeness from {report['completeness']['overall_pct']:.1f}% to >80%"
            )
        
        # Consistency recommendations
        if report['consistency']['score'] < 80:
            recommendations.append(
                "Standardize organism names, specimen types, and antimicrobial results"
            )
        
        # Validity recommendations
        if report['validity']['score'] < 80:
            recommendations.append(
                "Remove or correct invalid organisms, ages, genders, and antimicrobial results"
            )
        
        # AMR-specific recommendations
        if report['amr_specific']['organism_diversity'] < 5:
            recommendations.append(
                f"Low organism diversity ({report['amr_specific']['organism_diversity']} species). "
                "Ensure data represents diverse pathogens."
            )
        
        if report['amr_specific']['antimicrobial_coverage'] < 10:
            recommendations.append(
                f"Limited antimicrobial coverage ({report['amr_specific']['antimicrobial_coverage']} antimicrobials). "
                "Include more antimicrobials for comprehensive surveillance."
            )
        
        return recommendations
    
    def display_amr_quality_report(self, report: Dict[str, Any]):
        """Display comprehensive AMR quality report in Streamlit."""
        st.markdown("## 🧬 AMR Data Quality Assessment Report")
        
        # Overall quality score
        score = report.get('quality_score', 0)
        score_color = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Overall Quality Score", f"{score:.1f}%", delta=None)
            st.progress(score / 100)
        with col2:
            st.metric("GLASS Ready", "✅ Yes" if report.get('glass_submission_ready') else "❌ No")
        with col3:
            st.metric("Total Records", report['summary']['total_rows'])
        with col4:
            st.metric("Total Columns", report['summary']['total_columns'])
        
        # GLASS Readiness
        st.markdown("### 📋 GLASS Submission Readiness")
        glass_readiness = report['glass_readiness']
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Readiness Score", f"{glass_readiness['score']:.1f}%")
            st.progress(glass_readiness['score'] / 100)
        with col2:
            st.metric("Required Fields", 
                     f"{len(glass_readiness['required_fields_present'])}/{len(self.GLASS_REQUIRED_FIELDS)}")
        
        if glass_readiness['completeness_scores']:
            st.markdown("**Field Completeness:**")
            for field, completeness in glass_readiness['completeness_scores'].items():
                st.progress(completeness / 100, text=f"{field}: {completeness:.1f}%")
        
        if glass_readiness['critical_issues']:
            st.error("**Critical Issues:**")
            for issue in glass_readiness['critical_issues']:
                st.write(f"- {issue}")
        
        # Quality Dimensions
        st.markdown("### 📊 Quality Dimensions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Completeness", f"{report['completeness']['overall_pct']:.1f}%")
        with col2:
            st.metric("Consistency", f"{report['consistency']['score']:.1f}%")
        with col3:
            st.metric("Validity", f"{report['validity']['score']:.1f}%")
        with col4:
            st.metric("AMR Specific", f"{report.get('amr_specific', {}).get('organism_diversity', 0)} organisms")
        
        # One Health Breakdown
        if report.get('one_health'):
            st.markdown("### 🌍 One Health Categorization")
            one_health = report['one_health']
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Human", one_health['human'])
            with col2:
                st.metric("Animal", one_health['animal'])
            with col3:
                st.metric("Environmental", one_health['environmental'])
            with col4:
                st.metric("Unknown", one_health['unknown'])
        
        # Issues
        if report.get('issues'):
            st.markdown("### 🚨 Issues Found")
            for issue in report['issues']:
                severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(issue['severity'], "⚪")
                st.write(f"{severity_icon} **{issue['category'].replace('_', ' ').title()}**: {issue['message']}")
                if 'details' in issue and issue['details']:
                    with st.expander("Details"):
                        for detail in issue['details'][:5]:  # Show first 5
                            st.write(f"- {detail}")
        
        # Recommendations
        if report.get('recommendations'):
            st.markdown("### 💡 Recommendations")
            for i, rec in enumerate(report['recommendations'], 1):
                st.write(f"{i}. {rec}")
    
    def _auto_fix_organisms(self, df: pd.DataFrame) -> pd.DataFrame:
        """Auto-fix organism name variations to GLASS standard format."""
        if 'Organism' not in df.columns:
            return df
        
        df_fixed = df.copy()
        
        # Organism name mappings for common variations
        organism_mappings = {
            'e coli': 'E. coli', 'e.coli': 'E. coli', 'ecoli': 'E. coli', 'escherichia coli': 'E. coli',
            's aureus': 'S. aureus', 's.aureus': 'S. aureus', 'saureus': 'S. aureus', 
            'staphylococcus aureus': 'S. aureus', 'staph aureus': 'S. aureus',
            'k pneumoniae': 'K. pneumoniae', 'k.pneumoniae': 'K. pneumoniae', 
            'klebsiella pneumoniae': 'K. pneumoniae', 'kpneumoniae': 'K. pneumoniae',
            'p aeruginosa': 'P. aeruginosa', 'p.aeruginosa': 'P. aeruginosa',
            'pseudomonas aeruginosa': 'P. aeruginosa', 'paeruginosa': 'P. aeruginosa',
            'a baumannii': 'A. baumannii', 'a.baumannii': 'A. baumannii',
            'acinetobacter baumannii': 'A. baumannii', 'abaumannii': 'A. baumannii',
            's pneumoniae': 'S. pneumoniae', 's.pneumoniae': 'S. pneumoniae',
            'streptococcus pneumoniae': 'S. pneumoniae', 'spneumoniae': 'S. pneumoniae',
        }
        
        def standardize_organism(name):
            if pd.isna(name):
                return name
            name_str = str(name).strip().lower()
            if name_str in organism_mappings:
                return organism_mappings[name_str]
            # Check partial matches
            for key, value in organism_mappings.items():
                if key in name_str:
                    return value
            # Return title case
            return str(name).strip().title()
        
        df_fixed['Organism'] = df_fixed['Organism'].apply(standardize_organism)
        return df_fixed
    
    def _auto_fix_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Auto-fix date format inconsistencies."""
        df_fixed = df.copy()
        date_cols = [col for col in df.columns if 'date' in col.lower()]
        
        for col in date_cols:
            try:
                # Try multiple date formats
                df_fixed[col] = pd.to_datetime(df_fixed[col], errors='coerce', infer_datetime_format=True)
            except Exception:
                pass
        
        return df_fixed
    
    def _auto_fix_completeness(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply smart imputation for missing values in critical fields."""
        df_fixed = df.copy()
        
        # Gender: use mode or 'U' for unknown
        if 'Gender' in df_fixed.columns:
            mode_gender = df_fixed['Gender'].mode()
            if len(mode_gender) > 0:
                fill_value = str(mode_gender.iloc[0])
            else:
                fill_value = 'U'
            df_fixed['Gender'] = df_fixed['Gender'].fillna(fill_value)
        
        # Age: use median or mean
        age_cols = [col for col in df_fixed.columns if 'age' in col.lower()]
        for col in age_cols:
            if df_fixed[col].dtype in ['int64', 'float64']:
                median_age = df_fixed[col].median()
                if not pd.isna(median_age):
                    df_fixed[col] = df_fixed[col].fillna(median_age)
        
        # Specimen type: use mode
        specimen_cols = [col for col in df_fixed.columns if 'specimen' in col.lower() and 'type' in col.lower()]
        for col in specimen_cols:
            mode_specimen = df_fixed[col].mode()
            if len(mode_specimen) > 0:
                fill_value = str(mode_specimen.iloc[0])
                df_fixed[col] = df_fixed[col].fillna(fill_value)
        
        return df_fixed
    
    def comprehensive_auto_fix(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all auto-fixes comprehensively."""
        df_fixed = df.copy()
        
        # Apply all fixes in sequence
        df_fixed = self._auto_fix_organisms(df_fixed)
        df_fixed = self._auto_fix_dates(df_fixed)
        df_fixed = self._auto_fix_completeness(df_fixed)
        
        # Standardize gender values
        if 'Gender' in df_fixed.columns:
            gender_mappings = {
                'male': 'M', 'm': 'M', 'man': 'M',
                'female': 'F', 'f': 'F', 'woman': 'F',
                'other': 'O', 'o': 'O',
                'unknown': 'U', 'u': 'U', 'unspecified': 'U'
            }
            def standardize_gender(gender):
                if pd.isna(gender):
                    return 'U'
                gender_str = str(gender).strip().lower()
                return gender_mappings.get(gender_str, str(gender).strip().upper()[:1])
            df_fixed['Gender'] = df_fixed['Gender'].apply(standardize_gender)
        
        # Standardize specimen types
        specimen_cols = [col for col in df_fixed.columns if 'specimen' in col.lower() and 'type' in col.lower()]
        for col in specimen_cols:
            specimen_mappings = {
                'blood': 'Blood', 'bld': 'Blood', 'bl': 'Blood',
                'urine': 'Urine', 'ur': 'Urine',
                'sputum': 'Sputum', 'sput': 'Sputum',
                'csf': 'CSF', 'cerebrospinal fluid': 'CSF',
                'wound': 'Wound', 'swab': 'Swab',
                'stool': 'Stool', 'feces': 'Stool'
            }
            def standardize_specimen(specimen):
                if pd.isna(specimen):
                    return specimen
                spec_str = str(specimen).strip().lower()
                return specimen_mappings.get(spec_str, str(specimen).strip().title())
            df_fixed[col] = df_fixed[col].apply(standardize_specimen)
        
        # Standardize antimicrobial results
        antimicrobial_cols = self._identify_antimicrobial_columns(df_fixed)
        for col in antimicrobial_cols:
            result_mappings = {
                's': 'S', 'susceptible': 'S', 'susceptibility': 'S',
                'r': 'R', 'resistant': 'R', 'resistance': 'R',
                'i': 'I', 'intermediate': 'I', 'indeterminate': 'I',
                'nd': 'ND', 'not determined': 'ND', 'not done': 'ND',
                'nm': 'NM', 'not measured': 'NM'
            }
            def standardize_result(value):
                if pd.isna(value):
                    return value
                value_str = str(value).strip().upper()
                if value_str in ['S', 'R', 'I', 'ND', 'NM']:
                    return value_str
                value_lower = str(value).strip().lower()
                return result_mappings.get(value_lower, value_str)
            df_fixed[col] = df_fixed[col].apply(standardize_result)
        
        return df_fixed

