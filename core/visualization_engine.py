"""
DataSense AI - Visualization Engine
Creates charts and visualizations using Matplotlib
"""

import numpy as np
import pandas as pd
from typing import Optional
import matplotlib
matplotlib.use('QtAgg')  # Use Qt backend
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class VisualizationEngine:
    """Engine for creating data visualizations"""
    
    # Color palette
    COLORS = [
        '#1E3A5F', '#2D5A87', '#00D4AA', '#38A169', '#D69E2E',
        '#E53E3E', '#9F7AEA', '#ED8936', '#48BB78', '#4299E1'
    ]
    
    def __init__(self):
        self.current_chart: Optional[FigureCanvasQTAgg] = None
    
    def create_chart(self, df: pd.DataFrame, chart_type: str) -> FigureCanvasQTAgg:
        """Create a chart of the specified type"""
        chart_type = chart_type.lower()
        
        if 'line' in chart_type:
            return self._create_line_chart(df)
        elif 'bar' in chart_type:
            return self._create_bar_chart(df)
        elif 'scatter' in chart_type:
            return self._create_scatter_chart(df)
        elif 'histogram' in chart_type:
            return self._create_histogram(df)
        elif 'pie' in chart_type:
            return self._create_pie_chart(df)
        elif 'box' in chart_type:
            return self._create_box_plot(df)
        else:
            raise ValueError(f"Unknown chart type: {chart_type}")
    
    def _create_figure(self) -> tuple:
        """Create a figure and canvas"""
        fig = Figure(figsize=(10, 6), facecolor='white')
        canvas = FigureCanvasQTAgg(fig)
        return fig, canvas
    
    def _create_line_chart(self, df: pd.DataFrame) -> FigureCanvasQTAgg:
        """Create a line chart"""
        fig, canvas = self._create_figure()
        ax = fig.add_subplot(111)
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            ax.text(0.5, 0.5, 'No numeric data available', 
                   ha='center', va='center', transform=ax.transAxes)
            return canvas
        
        # Plot each numeric column
        for i, col in enumerate(numeric_cols[:5]):  # Limit to 5 columns
            ax.plot(df.index, df[col], label=col, 
                   color=self.COLORS[i % len(self.COLORS)], linewidth=2)
        
        ax.set_xlabel('Index', fontsize=12)
        ax.set_ylabel('Value', fontsize=12)
        ax.set_title('Line Chart', fontsize=14, fontweight='bold')
        ax.legend(loc='best', framealpha=0.9)
        ax.grid(True, alpha=0.3)
        
        fig.tight_layout()
        return canvas
    
    def _create_bar_chart(self, df: pd.DataFrame) -> FigureCanvasQTAgg:
        """Create a bar chart"""
        fig, canvas = self._create_figure()
        ax = fig.add_subplot(111)
        
        # Use first categorical column for grouping if available
        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            ax.text(0.5, 0.5, 'No numeric data available', 
                   ha='center', va='center', transform=ax.transAxes)
            return canvas
        
        # Get first numeric column
        col = numeric_cols[0]
        
        if len(cat_cols) > 0:
            # Group by categorical column
            grouped = df.groupby(cat_cols[0])[col].mean().head(10)
            ax.bar(range(len(grouped)), grouped.values, color=self.COLORS[1])
            ax.set_xticks(range(len(grouped)))
            ax.set_xticklabels(grouped.index, rotation=45, ha='right')
            ax.set_xlabel(cat_cols[0], fontsize=12)
        else:
            # Use index
            sample = df[col].head(20)
            ax.bar(range(len(sample)), sample.values, color=self.COLORS[1])
            ax.set_xticks(range(len(sample)))
            ax.set_xlabel('Index', fontsize=12)
        
        ax.set_ylabel(col, fontsize=12)
        ax.set_title(f'Bar Chart - {col}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        fig.tight_layout()
        return canvas
    
    def _create_scatter_chart(self, df: pd.DataFrame) -> FigureCanvasQTAgg:
        """Create a scatter plot"""
        fig, canvas = self._create_figure()
        ax = fig.add_subplot(111)
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            ax.text(0.5, 0.5, 'Need at least 2 numeric columns for scatter plot', 
                   ha='center', va='center', transform=ax.transAxes)
            return canvas
        
        # Use first two numeric columns
        x_col = numeric_cols[0]
        y_col = numeric_cols[1]
        
        # Drop NaN values
        plot_data = df[[x_col, y_col]].dropna()
        
        ax.scatter(plot_data[x_col], plot_data[y_col], 
                  alpha=0.6, c=self.COLORS[2], edgecolors='white', s=50)
        
        ax.set_xlabel(x_col, fontsize=12)
        ax.set_ylabel(y_col, fontsize=12)
        ax.set_title(f'Scatter Plot: {x_col} vs {y_col}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Add correlation
        corr = plot_data[x_col].corr(plot_data[y_col])
        ax.text(0.05, 0.95, f'Correlation: {corr:.3f}', 
               transform=ax.transAxes, fontsize=10,
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        fig.tight_layout()
        return canvas
    
    def _create_histogram(self, df: pd.DataFrame) -> FigureCanvasQTAgg:
        """Create a histogram"""
        fig, canvas = self._create_figure()
        ax = fig.add_subplot(111)
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            ax.text(0.5, 0.5, 'No numeric data available', 
                   ha='center', va='center', transform=ax.transAxes)
            return canvas
        
        # Use first numeric column
        col = numeric_cols[0]
        data = df[col].dropna()
        
        ax.hist(data, bins=30, color=self.COLORS[3], edgecolor='white', alpha=0.8)
        
        ax.set_xlabel(col, fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_title(f'Histogram - {col}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add statistics
        mean_val = data.mean()
        median_val = data.median()
        ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.2f}')
        ax.axvline(median_val, color='green', linestyle='--', linewidth=2, label=f'Median: {median_val:.2f}')
        ax.legend()
        
        fig.tight_layout()
        return canvas
    
    def _create_pie_chart(self, df: pd.DataFrame) -> FigureCanvasQTAgg:
        """Create a pie chart"""
        fig, canvas = self._create_figure()
        ax = fig.add_subplot(111)
        
        # Find categorical column with reasonable number of categories
        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        
        if len(cat_cols) == 0:
            ax.text(0.5, 0.5, 'No categorical data available for pie chart', 
                   ha='center', va='center', transform=ax.transAxes)
            return canvas
        
        # Use first categorical column
        col = cat_cols[0]
        value_counts = df[col].value_counts().head(8)
        
        if len(value_counts) < 2:
            ax.text(0.5, 0.5, 'Not enough categories for pie chart', 
                   ha='center', va='center', transform=ax.transAxes)
            return canvas
        
        colors = self.COLORS[:len(value_counts)]
        wedges, texts, autotexts = ax.pie(
            value_counts.values, 
            labels=value_counts.index,
            autopct='%1.1f%%',
            colors=colors,
            explode=[0.02] * len(value_counts)
        )
        
        ax.set_title(f'Pie Chart - {col}', fontsize=14, fontweight='bold')
        
        fig.tight_layout()
        return canvas
    
    def _create_box_plot(self, df: pd.DataFrame) -> FigureCanvasQTAgg:
        """Create a box plot"""
        fig, canvas = self._create_figure()
        ax = fig.add_subplot(111)
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            ax.text(0.5, 0.5, 'No numeric data available', 
                   ha='center', va='center', transform=ax.transAxes)
            return canvas
        
        # Use first few numeric columns
        cols = numeric_cols[:5]
        data_to_plot = [df[col].dropna().values for col in cols]
        
        bp = ax.boxplot(data_to_plot, labels=cols, patch_artist=True)
        
        # Color the boxes
        for patch, color in zip(bp['boxes'], self.COLORS[:len(cols)]):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_xlabel('Columns', fontsize=12)
        ax.set_ylabel('Value', fontsize=12)
        ax.set_title('Box Plot', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        fig.tight_layout()
        return canvas