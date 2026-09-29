"""
DataSense AI - Insight Generator
Generates natural language insights from analysis results
"""

from typing import Dict, Any, List


class InsightGenerator:
    """Generates human-readable insights from analysis results"""
    
    def generate_insights(self, results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate insights from analysis results"""
        insights = []
        
        # 1. Data Overview
        if 'patterns' in results:
            patterns = results['patterns']
            if patterns:
                insight = self._generate_data_overview(patterns)
                insights.append(insight)
        
        # 2. Correlations
        if 'correlations' in results:
            correlations = results['correlations']
            if correlations and 'strong_correlations' in correlations:
                corr_insights = self._generate_correlation_insights(correlations)
                insights.extend(corr_insights)
        
        # 3. Clustering
        if 'clustering' in results:
            clustering = results['clustering']
            if clustering and 'optimal_clusters' in clustering:
                cluster_insight = self._generate_clustering_insight(clustering)
                insights.append(cluster_insight)
        
        # 4. Outliers
        if 'outliers' in results:
            outliers = results['outliers']
            if outliers and isinstance(outliers, dict):
                outlier_insights = self._generate_outlier_insights(outliers)
                insights.extend(outlier_insights)
        
        # 5. Regression
        if 'regression' in results:
            regression = results['regression']
            if regression and 'r2_score' in regression:
                reg_insight = self._generate_regression_insight(regression)
                insights.append(reg_insight)
        
        # 6. Classification
        if 'classification' in results:
            classification = results['classification']
            if classification and 'accuracy' in classification:
                class_insight = self._generate_classification_insight(classification)
                insights.append(class_insight)
        
        return insights
    
    def _generate_data_overview(self, patterns: Dict) -> Dict[str, str]:
        """Generate data overview insight"""
        if not patterns:
            return {
                'title': 'Data Overview',
                'content': 'No patterns detected in the data.',
                'type': 'info'
            }
        
        # Calculate average statistics
        means = [p.get('mean', 0) for p in patterns.values() if 'mean' in p]
        stds = [p.get('std', 0) for p in patterns.values() if 'std' in p]
        
        if means:
            avg_mean = sum(means) / len(means)
            avg_std = sum(stds) / len(stds) if stds else 0
            
            content = f"Analysis of {len(patterns)} numeric variables shows an average value of {avg_mean:.2f} with typical variation of {avg_std:.2f}. "
            
            # Add skewness info
            skewed_right = sum(1 for p in patterns.values() if p.get('skewness', 0) > 0.5)
            skewed_left = sum(1 for p in patterns.values() if p.get('skewness', 0) < -0.5)
            
            if skewed_right > 0:
                content += f"{skewed_right} variable(s) show right-skewed distribution. "
            if skewed_left > 0:
                content += f"{skewed_left} variable(s) show left-skewed distribution. "
            
            return {
                'title': 'Data Overview',
                'content': content.strip(),
                'type': 'info'
            }
        
        return {
            'title': 'Data Overview',
            'content': f'Found {len(patterns)} numeric variables in the dataset.',
            'type': 'info'
        }
    
    def _generate_correlation_insights(self, correlations: Dict) -> List[Dict[str, str]]:
        """Generate correlation insights"""
        insights = []
        
        strong_corrs = correlations.get('strong_correlations', [])
        
        if not strong_corrs:
            insights.append({
                'title': 'Correlation Analysis',
                'content': 'No strong correlations found between variables (all correlations below 0.5).',
                'type': 'info'
            })
            return insights
        
        # Top positive correlation
        positive = [c for c in strong_corrs if c['correlation'] > 0]
        negative = [c for c in strong_corrs if c['correlation'] < 0]
        
        if positive:
            top_pos = max(positive, key=lambda x: x['correlation'])
            insights.append({
                'title': 'Strong Positive Correlation',
                'content': f"Variables '{top_pos['var1']}' and '{top_pos['var2']}' show strong positive correlation ({top_pos['correlation']:.2f}). When one increases, the other tends to increase as well.",
                'type': 'info'
            })
        
        if negative:
            top_neg = min(negative, key=lambda x: x['correlation'])
            insights.append({
                'title': 'Strong Negative Correlation',
                'content': f"Variables '{top_neg['var1']}' and '{top_neg['var2']}' show strong negative correlation ({top_neg['correlation']:.2f}). When one increases, the other tends to decrease.",
                'type': 'warning'
            })
        
        if len(strong_corrs) > 2:
            insights.append({
                'title': 'Multiple Correlations',
                'content': f"Found {len(strong_corrs)} pairs of strongly correlated variables. This suggests potential redundancy that could be addressed through feature selection.",
                'type': 'info'
            })
        
        return insights
    
    def _generate_clustering_insight(self, clustering: Dict) -> Dict[str, str]:
        """Generate clustering insight"""
        n_clusters = clustering.get('optimal_clusters', 0)
        silhouette = clustering.get('silhouette_score', 0)
        cluster_sizes = clustering.get('cluster_sizes', {})
        
        if n_clusters == 0:
            return {
                'title': 'Clustering Analysis',
                'content': 'Unable to perform clustering on this data.',
                'type': 'warning'
            }
        
        content = f"Data naturally groups into {n_clusters} distinct clusters (silhouette score: {silhouette:.2f}). "
        
        # Describe cluster sizes
        sizes = list(cluster_sizes.values())
        if sizes:
            avg_size = sum(sizes) / len(sizes)
            content += f"Cluster sizes range from {min(sizes)} to {max(sizes)} observations (average: {avg_size:.0f}). "
        
        if silhouette > 0.5:
            content += "The clustering is well-defined with clear separation between groups."
        elif silhouette > 0.25:
            content += "The clustering shows moderate separation between groups."
        else:
            content += "The clusters have some overlap, suggesting the groups may not be fully distinct."
        
        return {
            'title': 'Clustering Analysis',
            'content': content.strip(),
            'type': 'info'
        }
    
    def _generate_outlier_insights(self, outliers: Dict) -> List[Dict[str, str]]:
        """Generate outlier insights"""
        insights = []
        
        # Find columns with most outliers
        outlier_cols = []
        for col, data in outliers.items():
            if isinstance(data, dict) and 'outlier_values' in data:
                pct = data['outlier_values']
                if pct > 0:
                    outlier_cols.append((col, pct))
        
        if not outlier_cols:
            insights.append({
                'title': 'Outlier Detection',
                'content': 'No significant outliers detected in the dataset.',
                'type': 'info'
            })
            return insights
        
        # Sort by percentage
        outlier_cols.sort(key=lambda x: x[1], reverse=True)
        
        # Top outlier column
        top_col, top_pct = outlier_cols[0]
        insights.append({
            'title': 'Outliers Detected',
            'content': f"Column '{top_col}' contains {top_pct:.1f}% outlier values. This may indicate data quality issues or genuine anomalies worth investigating.",
            'type': 'warning'
        })
        
        # Multiple outlier columns
        if len(outlier_cols) > 1:
            insights.append({
                'title': 'Multiple Outlier Columns',
                'content': f"{len(outlier_cols)} columns contain outlier values. Consider reviewing these for data cleaning or further investigation.",
                'type': 'info'
            })
        
        return insights
    
    def _generate_regression_insight(self, regression: Dict) -> Dict[str, str]:
        """Generate regression insight"""
        r2 = regression.get('r2_score', 0)
        target = regression.get('target', 'unknown')
        features = regression.get('features', [])
        
        if r2 < 0:
            return {
                'title': 'Regression Analysis',
                'content': 'Unable to perform regression analysis on this data.',
                'type': 'warning'
            }
        
        content = f"Linear regression model for predicting '{target}' from {len(features)} features achieves R² = {r2:.3f}. "
        
        if r2 > 0.7:
            content += "This indicates a strong predictive relationship - the model explains most of the variance in the target variable."
        elif r2 > 0.4:
            content += "This indicates a moderate predictive relationship. The model captures some patterns but significant unexplained variation remains."
        else:
            content += "This indicates a weak predictive relationship. The features have limited ability to predict the target variable."
        
        # Add coefficient info
        coeffs = regression.get('coefficients', {})
        if coeffs:
            top_feature = max(coeffs.items(), key=lambda x: abs(x[1]))
            content += f" The most influential predictor is '{top_feature[0]}' (coefficient: {top_feature[1]:.3f})."
        
        return {
            'title': 'Regression Analysis',
            'content': content.strip(),
            'type': 'info'
        }
    
    def _generate_classification_insight(self, classification: Dict) -> Dict[str, str]:
        """Generate classification insight"""
        accuracy = classification.get('accuracy', 0)
        target = classification.get('target', 'unknown')
        classes = classification.get('target_classes', [])
        
        if accuracy < 0:
            return {
                'title': 'Classification Analysis',
                'content': 'Unable to perform classification on this data.',
                'type': 'warning'
            }
        
        content = f"Decision tree classifier for '{target}' achieves {accuracy*100:.1f}% accuracy. "
        
        if accuracy > 0.9:
            content += "The model shows excellent classification ability with high accuracy."
        elif accuracy > 0.7:
            content += "The model shows good classification ability with room for improvement."
        elif accuracy > 0.5:
            content += "The model shows moderate classification ability, better than random but not highly reliable."
        else:
            content += "The model shows limited classification ability. Consider using more features or different algorithms."
        
        # Add class info
        if classes:
            content += f" The target has {len(classes)} classes: {', '.join(str(c) for c in classes[:5])}."
            if len(classes) > 5:
                content += f" and {len(classes) - 5} more."
        
        return {
            'title': 'Classification Analysis',
            'content': content.strip(),
            'type': 'info'
        }