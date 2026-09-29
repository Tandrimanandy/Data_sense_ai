"""
DataSense AI - Statistics Engine
Computes descriptive and inferential statistics
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
from scipy import stats as scipy_stats


class StatisticsEngine:
    """Engine for statistical analysis"""
    
    def compute_descriptive_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Compute descriptive statistics"""
        stats = {}
        
        # Overall summary
        stats['summary'] = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'memory_mb': df.memory_usage(deep=True).sum() / (1024 * 1024)
        }
        
        # Per-column statistics
        stats['columns'] = {}
        
        for col in df.columns:
            col_stats = {}
            series = df[col]
            
            # Data type
            col_stats['dtype'] = str(series.dtype)
            
            # Null count
            col_stats['null_count'] = int(series.isna().sum())
            col_stats['null_percent'] = float(series.isna().sum() / len(series) * 100)
            
            # Unique count
            col_stats['unique_count'] = int(series.nunique())
            
            if pd.api.types.is_numeric_dtype(series):
                # Numeric statistics
                numeric_series = series.dropna()
                
                if len(numeric_series) > 0:
                    col_stats['mean'] = float(numeric_series.mean())
                    col_stats['median'] = float(numeric_series.median())
                    col_stats['std'] = float(numeric_series.std())
                    col_stats['min'] = float(numeric_series.min())
                    col_stats['max'] = float(numeric_series.max())
                    col_stats['q25'] = float(numeric_series.quantile(0.25))
                    col_stats['q50'] = float(numeric_series.quantile(0.50))
                    col_stats['q75'] = float(numeric_series.quantile(0.75))
                    col_stats['skewness'] = float(numeric_series.skew())
                    col_stats['kurtosis'] = float(numeric_series.kurtosis())
                    col_stats['variance'] = float(numeric_series.var())
                    
                    # Range
                    col_stats['range'] = col_stats['max'] - col_stats['min']
                    col_stats['iqr'] = col_stats['q75'] - col_stats['q25']
            else:
                # Categorical statistics
                col_stats['top_values'] = series.value_counts().head(5).to_dict()
                col_stats['mode'] = str(series.mode().iloc[0]) if len(series.mode()) > 0 else None
            
            stats['columns'][col] = col_stats
        
        return stats
    
    def compute_correlation_matrix(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute correlation matrix for numeric columns"""
        numeric_df = df.select_dtypes(include=[np.number])
        return numeric_df.corr()
    
    def compute_covariance_matrix(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute covariance matrix"""
        numeric_df = df.select_dtypes(include=[np.number])
        return numeric_df.cov()
    
    def t_test(self, series1: pd.Series, series2: pd.Series) -> Dict[str, float]:
        """Perform independent t-test"""
        data1 = series1.dropna()
        data2 = series2.dropna()
        
        if len(data1) < 2 or len(data2) < 2:
            return {'error': 'Insufficient data for t-test'}
        
        t_stat, p_value = scipy_stats.ttest_ind(data1, data2)
        
        return {
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'significant': p_value < 0.05
        }
    
    def chi_square_test(self, series1: pd.Series, series2: pd.Series) -> Dict[str, float]:
        """Perform chi-square test of independence"""
        # Create contingency table
        contingency = pd.crosstab(series1, series2)
        
        if contingency.size < 4:
            return {'error': 'Insufficient data for chi-square test'}
        
        chi2, p_value, dof, expected = scipy_stats.chi2_contingency(contingency)
        
        return {
            'chi_square': float(chi2),
            'p_value': float(p_value),
            'degrees_of_freedom': int(dof),
            'significant': p_value < 0.05
        }
    
    def anova_test(self, *groups) -> Dict[str, float]:
        """Perform one-way ANOVA"""
        # Filter out empty groups
        valid_groups = [g.dropna() for g in groups if len(g.dropna()) > 0]
        
        if len(valid_groups) < 2:
            return {'error': 'Need at least 2 groups for ANOVA'}
        
        f_stat, p_value = scipy_stats.f_oneway(*valid_groups)
        
        return {
            'f_statistic': float(f_stat),
            'p_value': float(p_value),
            'significant': p_value < 0.05
        }
    
    def confidence_interval(self, series: pd.Series, confidence: float = 0.95) -> tuple:
        """Compute confidence interval for the mean"""
        data = series.dropna()
        
        if len(data) < 2:
            return (None, None)
        
        mean = data.mean()
        sem = scipy_stats.sem(data)
        
        ci = scipy_stats.t.interval(confidence, len(data)-1, loc=mean, scale=sem)
        
        return (float(ci[0]), float(ci[1]))
    
    def normality_test(self, series: pd.Series) -> Dict[str, float]:
        """Test for normality using Shapiro-Wilk test"""
        data = series.dropna()
        
        if len(data) < 3:
            return {'error': 'Insufficient data for normality test'}
        
        # Limit to 5000 samples for Shapiro-Wilk
        if len(data) > 5000:
            data = data.sample(5000, random_state=42)
        
        stat, p_value = scipy_stats.shapiro(data)
        
        return {
            'statistic': float(stat),
            'p_value': float(p_value),
            'is_normal': p_value > 0.05
        }
    
    def get_distribution_info(self, series: pd.Series) -> Dict[str, Any]:
        """Get information about the distribution"""
        data = series.dropna()
        
        if len(data) < 2:
            return {'error': 'Insufficient data'}
        
        # Calculate moments
        info = {
            'mean': float(data.mean()),
            'median': float(data.median()),
            'mode': float(data.mode().iloc[0]) if len(data.mode()) > 0 else None,
            'std': float(data.std()),
            'variance': float(data.var()),
            'skewness': float(data.skew()),
            'kurtosis': float(data.kurtosis()),
            'range': float(data.max() - data.min())
        }
        
        # Determine skewness type
        if info['skewness'] < -0.5:
            info['skew_type'] = 'left-skewed'
        elif info['skewness'] > 0.5:
            info['skew_type'] = 'right-skewed'
        else:
            info['skew_type'] = 'approximately symmetric'
        
        # Determine kurtosis type
        if info['kurtosis'] < 0:
            info['kurt_type'] = 'platykurtic (flat)'
        elif info['kurtosis'] > 0:
            info['kurt_type'] = 'leptokurtic (peaked)'
        else:
            info['kurt_type'] = 'mesokurtic (normal)'
        
        return info