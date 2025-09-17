import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class ChartGenerator:
    def __init__(self):
        self.chart_types = {
            'pie': self._create_pie_chart,
            'bar': self._create_bar_chart,
            'line': self._create_line_chart,
            'scatter': self._create_scatter_chart,
            'histogram': self._create_histogram
        }
    
    def generate_charts(self, data: List[Dict[str, Any]], query_type: str = "custom") -> List[Dict[str, Any]]:
        """Generate appropriate charts based on data structure and content"""
        if not data:
            return []
        
        try:
            df = pd.DataFrame(data)
            charts = []
            
            # Auto-detect chart types based on data
            chart_suggestions = self._analyze_data_for_charts(df, query_type)
            
            for chart_type, config in chart_suggestions.items():
                try:
                    chart = self._create_chart(df, chart_type, config)
                    if chart and chart.get('figure_json'):  # Only add charts with JSON
                        charts.append(chart)
                except Exception as e:
                    logger.error(f"Error creating {chart_type} chart: {e}")
                    continue
            
            return charts
            
        except Exception as e:
            logger.error(f"Error generating charts: {e}")
            return []
    
    def _analyze_data_for_charts(self, df: pd.DataFrame, query_type: str) -> Dict[str, Dict[str, Any]]:
        """Analyze data to suggest appropriate chart types"""
        suggestions = {}
        
        # Get column info
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # 1. Status/Category Distribution (Pie Chart)
        if any(col in df.columns for col in ['status', 'channel', 'type', 'category']):
            status_col = next((col for col in ['status', 'channel', 'type', 'category'] if col in df.columns), None)
            if status_col and df[status_col].nunique() <= 10:  # Limit for readability
                value_counts = df[status_col].value_counts()
                suggestions['pie'] = {
                    'column': status_col,
                    'title': f'{status_col.title()} Distribution',
                    'values': {
                        'names': value_counts.index.tolist(),
                        'values': value_counts.values.tolist()
                    }
                }
        
        # 2. Budget/Financial Analysis (Bar Chart)
        if 'budget' in df.columns:
            suggestions['bar'] = {
                'column': 'budget',
                'title': 'Budget Analysis',
                'x': 'name' if 'name' in df.columns else 'campaign_id',
                'y': 'budget'
            }
        
        # 3. Performance Metrics (Bar Chart)
        if any(col in df.columns for col in ['CTR', 'CVR', 'conversions']):
            perf_col = next((col for col in ['CTR', 'CVR', 'conversions'] if col in df.columns), None)
            if perf_col:
                suggestions['bar'] = {
                    'column': perf_col,
                    'title': f'{perf_col} Performance',
                    'x': 'campaign_id' if 'campaign_id' in df.columns else df.index,
                    'y': perf_col
                }
        
        # 4. Time Series (Line Chart)
        if 'date' in df.columns or any('date' in col.lower() for col in df.columns):
            date_col = 'date' if 'date' in df.columns else next((col for col in df.columns if 'date' in col.lower()), None)
            if date_col and len(df) > 1:
                suggestions['line'] = {
                    'column': date_col,
                    'title': 'Performance Over Time',
                    'x': date_col,
                    'y': 'CTR' if 'CTR' in df.columns else numeric_cols[0] if numeric_cols else None
                }
        
        # 5. Budget vs Performance (Scatter Plot)
        if 'budget' in df.columns and any(col in df.columns for col in ['CTR', 'CVR', 'conversions']):
            perf_col = next((col for col in ['CTR', 'CVR', 'conversions'] if col in df.columns), None)
            if perf_col:
                suggestions['scatter'] = {
                    'x': 'budget',
                    'y': perf_col,
                    'title': f'Budget vs {perf_col}',
                    'color': 'channel' if 'channel' in df.columns else None
                }
        
        # 6. Distribution Analysis (Histogram)
        if numeric_cols and len(df) > 5:
            suggestions['histogram'] = {
                'column': numeric_cols[0],
                'title': f'{numeric_cols[0]} Distribution'
            }
        
        return suggestions
    
    def _create_chart(self, df: pd.DataFrame, chart_type: str, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a specific chart type"""
        if chart_type not in self.chart_types:
            return None
        
        try:
            fig = self.chart_types[chart_type](df, config)
            if fig:
                # Convert Plotly figure to JSON-serializable format
                fig_json = fig.to_json()
                return {
                    'type': chart_type,
                    'title': config.get('title', f'{chart_type.title()} Chart'),
                    'figure_json': fig_json,
                    'config': config
                }
        except Exception as e:
            logger.error(f"Error creating {chart_type} chart: {e}")
            return None
    
    def _create_pie_chart(self, df: pd.DataFrame, config: Dict[str, Any]) -> Optional[go.Figure]:
        """Create pie chart"""
        try:
            column = config['column']
            values = config['values']
            
            # Handle both old pandas Series format and new dict format
            if isinstance(values, dict) and 'names' in values and 'values' in values:
                # New format: already converted to lists
                values_list = values['values']
                names_list = values['names']
            else:
                # Old format: pandas Series - convert to lists
                values_list = values.values.tolist() if hasattr(values, 'values') else values
                names_list = values.index.tolist() if hasattr(values, 'index') else list(range(len(values_list)))
            
            fig = px.pie(
                values=values_list,
                names=names_list,
                title=config['title']
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            return fig
        except Exception as e:
            logger.error(f"Error creating pie chart: {e}")
            return None
    
    def _create_bar_chart(self, df: pd.DataFrame, config: Dict[str, Any]) -> Optional[go.Figure]:
        """Create bar chart"""
        try:
            x_col = config.get('x', df.index)
            y_col = config.get('y')
            
            if y_col and y_col in df.columns:
                fig = px.bar(
                    df,
                    x=x_col,
                    y=y_col,
                    title=config['title']
                )
                fig.update_xaxes(tickangle=45)
                return fig
            else:
                # Create count-based bar chart
                column = config['column']
                value_counts = df[column].value_counts()
                
                # Convert pandas Series to lists for JSON serialization
                x_values = value_counts.index.tolist()
                y_values = value_counts.values.tolist()
                
                fig = px.bar(
                    x=x_values,
                    y=y_values,
                    title=config['title']
                )
                fig.update_xaxes(tickangle=45)
                return fig
        except Exception as e:
            logger.error(f"Error creating bar chart: {e}")
            return None
    
    def _create_line_chart(self, df: pd.DataFrame, config: Dict[str, Any]) -> Optional[go.Figure]:
        """Create line chart"""
        try:
            x_col = config['x']
            y_col = config['y']
            
            if y_col and y_col in df.columns:
                # Sort by x column for proper line chart
                df_sorted = df.sort_values(x_col)
                fig = px.line(
                    df_sorted,
                    x=x_col,
                    y=y_col,
                    title=config['title']
                )
                return fig
        except Exception as e:
            logger.error(f"Error creating line chart: {e}")
            return None
    
    def _create_scatter_chart(self, df: pd.DataFrame, config: Dict[str, Any]) -> Optional[go.Figure]:
        """Create scatter plot"""
        try:
            x_col = config['x']
            y_col = config['y']
            color_col = config.get('color')
            
            fig = px.scatter(
                df,
                x=x_col,
                y=y_col,
                color=color_col,
                title=config['title']
            )
            return fig
        except Exception as e:
            logger.error(f"Error creating scatter chart: {e}")
            return None
    
    def _create_histogram(self, df: pd.DataFrame, config: Dict[str, Any]) -> Optional[go.Figure]:
        """Create histogram"""
        try:
            column = config['column']
            
            fig = px.histogram(
                df,
                x=column,
                title=config['title']
            )
            return fig
        except Exception as e:
            logger.error(f"Error creating histogram: {e}")
            return None
