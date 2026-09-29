"""
DataSense AI - ML Engine
Local machine learning algorithms without external APIs
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal, QThread

from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    silhouette_score, mean_squared_error, mean_absolute_error,
    r2_score, accuracy_score, classification_report
)
from scipy import stats as scipy_stats


class MLEngine(QObject):
    """Machine learning engine for local AI analysis"""
    
    # Signals
    progress_updated = pyqtSignal(str)  # progress_message
    analysis_complete = pyqtSignal(dict)  # results
    
    def __init__(self):
        super().__init__()
        self._results: Dict[str, Any] = {}
    
    def run_full_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Run comprehensive AI analysis"""
        self._results = {}
        
        try:
            # 1. Pattern Detection
            self.progress_updated.emit("Detecting patterns...")
            self._results['patterns'] = self._detect_patterns(df)
            
            # 2. Correlation Analysis
            self.progress_updated.emit("Analyzing correlations...")
            self._results['correlations'] = self._correlation_analysis(df)
            
            # 3. Clustering
            self.progress_updated.emit("Performing clustering...")
            self._results['clustering'] = self._clustering_analysis(df)
            
            # 4. Outlier Detection
            self.progress_updated.emit("Detecting outliers...")
            self._results['outliers'] = self._outlier_detection(df)
            
            # 5. Regression Analysis
            self.progress_updated.emit("Running regression...")
            self._results['regression'] = self._regression_analysis(df)
            
            # 6. Classification (if applicable)
            self.progress_updated.emit("Building classification model...")
            self._results['classification'] = self._classification_analysis(df)
            
            # Emit completion
            self.analysis_complete.emit(self._results)
            return self._results
            
        except Exception as e:
            self._results['error'] = str(e)
            self.analysis_complete.emit(self._results)
            return self._results
    
    def _detect_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect patterns in the data"""
        patterns = {}
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) < 2:
                continue
            
            # Basic statistics
            patterns[col] = {
                'mean': float(series.mean()),
                'median': float(series.median()),
                'std': float(series.std()),
                'min': float(series.min()),
                'max': float(series.max()),
                'q25': float(series.quantile(0.25)),
                'q75': float(series.quantile(0.75)),
                'skewness': float(series.skew()),
                'kurtosis': float(series.kurtosis())
            }
        
        return patterns
    
    def _correlation_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform correlation analysis"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.shape[1] < 2:
            return {'message': 'Not enough numeric columns for correlation analysis'}
        
        # Compute correlation matrix
        corr_matrix = numeric_df.corr()
        
        # Find strong correlations
        strong_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.5:  # Threshold for strong correlation
                    strong_correlations.append({
                        'var1': corr_matrix.columns[i],
                        'var2': corr_matrix.columns[j],
                        'correlation': float(corr_val)
                    })
        
        return {
            'correlation_matrix': corr_matrix.to_dict(),
            'strong_correlations': strong_correlations
        }
    
    def _clustering_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform K-means clustering"""
        numeric_df = df.select_dtypes(include=[np.number]).dropna()
        
        if numeric_df.shape[1] < 1 or numeric_df.shape[0] < 10:
            return {'message': 'Not enough data for clustering'}
        
        # Limit data size for performance
        if len(numeric_df) > 1000:
            numeric_df = numeric_df.sample(1000, random_state=42)
        
        # Scale data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(numeric_df)
        
        # Try different numbers of clusters
        best_k = 3
        best_score = -1
        
        for k in range(2, min(6, len(scaled_data) // 10)):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(scaled_data)
            
            if len(set(labels)) > 1:
                score = silhouette_score(scaled_data, labels)
                if score > best_score:
                    best_score = score
                    best_k = k
        
        # Final clustering with best k
        kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(scaled_data)
        
        return {
            'optimal_clusters': best_k,
            'silhouette_score': float(best_score),
            'cluster_sizes': {int(i): int(np.sum(labels == i)) for i in range(best_k)},
            'cluster_centers': kmeans.cluster_centers_.tolist()
        }
    
    def _outlier_detection(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect outliers using IQR and Z-score methods"""
        outliers = {}
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) < 4:
                continue
            
            # IQR method
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            iqr_outliers = series[(series < lower_bound) | (series > upper_bound)]
            
            # Z-score method
            z_scores = np.abs(scipy_stats.zscore(series))
            z_outliers = series[z_scores > 3]
            
            outliers[col] = {
                'iqr_count': int(len(iqr_outliers)),
                'zscore_count': int(len(z_outliers)),
                'iqr_bounds': (float(lower_bound), float(upper_bound)),
                'outlier_values': float(len(iqr_outliers)) / len(series) * 100
            }
        
        return outliers
    
    def _regression_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform regression analysis"""
        numeric_df = df.select_dtypes(include=[np.number]).dropna()
        
        if numeric_df.shape[1] < 2:
            return {'message': 'Not enough numeric columns for regression'}
        
        # Use first column as target, others as features
        target_col = numeric_df.columns[0]
        feature_cols = numeric_df.columns[1:]
        
        if len(feature_cols) == 0:
            return {'message': 'Not enough features for regression'}
        
        X = numeric_df[feature_cols].values
        y = numeric_df[target_col].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Fit model
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Predictions
        y_pred = model.predict(X_test)
        
        return {
            'target': target_col,
            'features': list(feature_cols),
            'coefficients': {col: float(coef) for col, coef in zip(feature_cols, model.coef_)},
            'intercept': float(model.intercept_),
            'r2_score': float(r2_score(y_test, y_pred)),
            'mse': float(mean_squared_error(y_test, y_pred)),
            'mae': float(mean_absolute_error(y_test, y_pred))
        }
    
    def _classification_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform classification analysis"""
        # Find a suitable categorical column for classification
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        if len(categorical_cols) == 0:
            return {'message': 'No categorical columns for classification'}
        
        # Use first categorical column as target
        target_col = categorical_cols[0]
        
        # Get numeric features
        numeric_df = df.select_dtypes(include=[np.number]).dropna()
        
        if numeric_df.shape[1] < 1 or numeric_df.shape[0] < 20:
            return {'message': 'Not enough data for classification'}
        
        # Limit data
        if len(numeric_df) > 1000:
            sample_idx = np.random.choice(len(numeric_df), 1000, replace=False)
            numeric_df = numeric_df.iloc[sample_idx]
            target_series = df[target_col].iloc[sample_idx]
        else:
            target_series = df[target_col]
        
        # Encode target
        le = LabelEncoder()
        y = le.fit_transform(target_series)
        
        # Check if we have enough classes
        if len(np.unique(y)) < 2:
            return {'message': 'Not enough class diversity for classification'}
        
        X = numeric_df.values
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Fit model
        model = DecisionTreeClassifier(max_depth=5, random_state=42)
        model.fit(X_train, y_train)
        
        # Predictions
        y_pred = model.predict(X_test)
        
        return {
            'target': target_col,
            'target_classes': list(le.classes_),
            'accuracy': float(accuracy_score(y_test, y_pred)),
            'feature_importance': {
                col: float(imp) 
                for col, imp in zip(numeric_df.columns, model.feature_importances_)
            }
        }
    
    # Individual analysis methods for specific analysis types
    
    def correlation_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Public method for correlation analysis"""
        return self._correlation_analysis(df)
    
    def clustering_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Public method for clustering analysis"""
        return self._clustering_analysis(df)
    
    def regression_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Public method for regression analysis"""
        return self._regression_analysis(df)
    
    def outlier_detection(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Public method for outlier detection"""
        return self._outlier_detection(df)