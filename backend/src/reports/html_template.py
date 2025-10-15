"""
HTML Report Template Generator

Creates professional HTML reports with embedded CSS and JavaScript
for charts and visualizations.
"""

import json
from typing import Dict, List, Optional
from ..reports.report_generator import (
    ReportSection,
    ExecutiveSummary,
    ReportConfig,
    ReportTheme,
    VisualizationData,
    ChartType
)


class HTMLReportTemplate:
    """Generates professional HTML reports with styling and charts"""
    
    def __init__(self, config: ReportConfig, for_pdf: bool = False):
        self.config = config
        self.colors = self._get_theme_colors()
        self.theme_name = config.theme.value if hasattr(config.theme, 'value') else str(config.theme)
        self.for_pdf = for_pdf  # Flag to disable external fonts for PDF generation
    
    def generate(
        self,
        title: str,
        exec_summary: ExecutiveSummary,
        sections: List[ReportSection],
        metadata: Dict
    ) -> str:
        """Generate complete HTML report"""
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {self._generate_styles()}
    {self._generate_chart_scripts()}
</head>
<body>
    <div class="report-container">
        {self._generate_header(title, metadata)}
        {self._generate_executive_summary(exec_summary)}
        {self._generate_sections(sections)}
        {self._generate_footer(metadata)}
    </div>
    {self._generate_chart_initializations(sections)}
</body>
</html>"""
        
        return html
    
    def _generate_header(self, title: str, metadata: Dict) -> str:
        """Generate report header"""
        
        logo_html = ""
        if self.config.logo_url:
            logo_html = f'<img src="{self.config.logo_url}" alt="Logo" class="logo">'
        
        company_html = ""
        if self.config.company_name:
            company_html = f'<div class="company-name">{self.config.company_name}</div>'
        
        return f"""
    <header class="report-header">
        <div class="header-content">
            {logo_html}
            <div class="header-text">
                <h1 class="report-title">{title}</h1>
                {company_html}
                <div class="report-date">{metadata.get('generated_at', '')}</div>
            </div>
        </div>
    </header>"""
    
    def _generate_executive_summary(self, exec_summary: ExecutiveSummary) -> str:
        """Generate executive summary HTML"""
        
        stats_html = ""
        for stat_name, stat_value in exec_summary.quick_stats.items():
            stats_html += f"""
                <div class="stat-card">
                    <div class="stat-label">{stat_name}</div>
                    <div class="stat-value">{stat_value}</div>
                </div>"""
        
        findings_html = ""
        for finding in exec_summary.key_findings:
            findings_html += f"<li>{finding}</li>"
        
        actions_html = ""
        for i, action in enumerate(exec_summary.priority_actions, 1):
            actions_html += f"""
                <div class="action-item">
                    <div class="action-number">{i}</div>
                    <div class="action-text">{action}</div>
                </div>"""
        
        return f"""
    <section class="executive-summary">
        <h2>Executive Summary</h2>
        <div class="overview-box">
            <p>{exec_summary.overview}</p>
        </div>
        
        <div class="stats-grid">
            {stats_html}
        </div>
        
        <div class="findings-section">
            <h3>Key Findings</h3>
            <ul class="findings-list">
                {findings_html}
            </ul>
        </div>
        
        <div class="actions-section">
            <h3>Priority Actions</h3>
            <div class="priority-actions">
                {actions_html}
            </div>
        </div>
    </section>"""
    
    def _generate_sections(self, sections: List[ReportSection]) -> str:
        """Generate all report sections"""
        
        sections_html = ""
        for section in sections:
            sections_html += self._generate_section(section)
        
        return sections_html
    
    def _generate_section(self, section: ReportSection) -> str:
        """Generate a single report section"""
        
        # Generate visualizations
        viz_html = ""
        if self.config.include_charts and section.visualizations:
            viz_html = '<div class="visualizations-grid">'
            for i, viz in enumerate(section.visualizations):
                chart_id = f"chart_{section.title.replace(' ', '_')}_{i}"
                viz_html += f"""
                <div class="chart-container">
                    <h4>{viz.title}</h4>
                    <canvas id="{chart_id}" class="chart-canvas"></canvas>
                    {f'<p class="chart-description">{viz.description}</p>' if viz.description else ''}
                </div>"""
            viz_html += '</div>'
        
        # Generate subsections
        subsections_html = ""
        for subsection in section.subsections:
            subsections_html += self._generate_section(subsection)
        
        page_break = ' class="page-break"' if self.config.page_breaks else ''
        
        return f"""
    <section{page_break}>
        <h{section.level}>{section.title}</h{section.level}>
        <div class="section-content">
            {section.content}
        </div>
        {viz_html}
        {subsections_html}
    </section>"""
    
    def _generate_footer(self, metadata: Dict) -> str:
        """Generate report footer"""
        
        watermark_html = ""
        if self.config.watermark:
            watermark_html = f'<div class="watermark">{self.config.watermark}</div>'
        
        return f"""
    <footer class="report-footer">
        {watermark_html}
        <div class="footer-info">
            <p>Generated on {metadata.get('generated_at', '')}</p>
            <p>Analysis Cost: ${metadata.get('total_cost', 0):.4f} | Processing Time: {metadata.get('processing_time_ms', 0)/1000:.1f}s</p>
        </div>
    </footer>"""
    
    def _generate_styles(self) -> str:
        """Generate embedded CSS styles with theme-specific customizations"""
        
        # Add Google Fonts for Modern and Colorful themes (only for web view, not PDF)
        google_fonts = ""
        if not self.for_pdf:
            if self.theme_name == "modern":
                google_fonts = '<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">'
            elif self.theme_name == "colorful":
                google_fonts = '<link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@300;500;700&display=swap" rel="stylesheet">'
            elif self.theme_name == "professional":
                google_fonts = '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">'
        
        return f"""
    {google_fonts}
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: {self.colors.get('font', '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif')};
            line-height: 1.6;
            color: {self.colors['text']};
            background: {self.colors['background']};
        }}
        
        .report-container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        
        /* Header */
        .report-header {{
            background: linear-gradient(135deg, {self.colors['primary']}, {self.colors['secondary']});
            color: white;
            padding: 40px;
            border-radius: {self.colors.get('border_radius', '12px')};
            margin-bottom: 40px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .header-content {{
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        
        .logo {{
            max-width: 100px;
            height: auto;
        }}
        
        .report-title {{
            font-size: 2.5em;
            font-weight: {self.colors.get('heading_weight', '700')};
            margin-bottom: 10px;
        }}
        
        .company-name {{
            font-size: 1.2em;
            opacity: 0.9;
            margin-bottom: 5px;
        }}
        
        .report-date {{
            font-size: 0.9em;
            opacity: 0.8;
        }}
        
        /* Executive Summary */
        .executive-summary {{
            background: {self.colors.get('card_bg', 'white')};
            padding: 30px;
            border-radius: {self.colors.get('border_radius', '12px')};
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            border: 1px solid {self.colors.get('border', '#e5e7eb')};
        }}
        
        .executive-summary h2 {{
            color: {self.colors['primary']};
            font-size: 2em;
            font-weight: {self.colors.get('heading_weight', '700')};
            margin-bottom: 20px;
            border-bottom: 3px solid {self.colors['accent']};
            padding-bottom: 10px;
        }}
        
        .overview-box {{
            background: {self.colors.get('background', '#f9fafb')};
            border-left: 4px solid {self.colors['primary']};
            padding: 20px;
            margin: 20px 0;
            font-size: 1.1em;
            line-height: 1.8;
            border-radius: {self.colors.get('border_radius', '8px')};
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, {self.colors['primary']}, {self.colors['secondary']});
            color: white;
            padding: 25px;
            border-radius: {self.colors.get('border_radius', '8px')};
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 8px;
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: 700;
        }}
        
        .findings-list {{
            list-style: none;
            padding: 0;
        }}
        
        .findings-list li {{
            padding: 12px 20px;
            margin: 10px 0;
            background: {self.colors.get('card_bg', 'white')};
            border-left: 4px solid {self.colors['success']};
            border-radius: {self.colors.get('border_radius', '4px')};
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        
        .priority-actions {{
            margin-top: 20px;
        }}
        
        .action-item {{
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 15px;
            margin: 10px 0;
            background: {self.colors.get('card_bg', 'white')};
            border: 2px solid {self.colors['accent']};
            border-radius: {self.colors.get('border_radius', '8px')};
            transition: transform 0.2s;
        }}
        
        .action-item:hover {{
            transform: translateX(5px);
        }}
        
        .action-number {{
            background: {self.colors['primary']};
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.2em;
            flex-shrink: 0;
        }}
        
        .action-text {{
            flex: 1;
        }}
        
        /* Sections */
        section {{
            background: {self.colors.get('card_bg', 'white')};
            padding: 30px;
            margin-bottom: 30px;
            border-radius: {self.colors.get('border_radius', '12px')};
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border: 1px solid {self.colors.get('border', '#e5e7eb')};
        }}
        
        section h2 {{
            color: {self.colors['primary']};
            font-size: 2em;
            font-weight: {self.colors.get('heading_weight', '700')};
            margin-bottom: 20px;
            border-bottom: 3px solid {self.colors['accent']};
            padding-bottom: 10px;
        }}
        
        section h3 {{
            color: {self.colors['secondary']};
            font-size: 1.5em;
            font-weight: {self.colors.get('heading_weight', '700')};
            margin: 25px 0 15px 0;
        }}
        
        section h4 {{
            color: {self.colors['text']};
            font-size: 1.2em;
            margin: 20px 0 10px 0;
        }}
        
        .section-content {{
            margin: 20px 0;
        }}
        
        /* Visualizations */
        .visualizations-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin: 30px 0;
        }}
        
        .chart-container {{
            background: {self.colors['background']};
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
        }}
        
        .chart-container h4 {{
            text-align: center;
            margin-bottom: 15px;
            color: {self.colors['primary']};
        }}
        
        .chart-canvas {{
            max-width: 100%;
            height: 300px !important;
        }}
        
        .chart-description {{
            text-align: center;
            margin-top: 10px;
            font-size: 0.9em;
            color: #6b7280;
        }}
        
        /* Scores and Metrics */
        .big-score {{
            font-size: 4em;
            font-weight: 700;
            text-align: center;
            margin: 20px 0;
        }}
        
        .score-bar {{
            background: #e5e7eb;
            height: 25px;
            border-radius: 12px;
            overflow: hidden;
            position: relative;
        }}
        
        .bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, {self.colors['primary']}, {self.colors['accent']});
            transition: width 0.3s ease;
        }}
        
        /* Tables */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        table th {{
            background: {self.colors['primary']};
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        
        table td {{
            padding: 12px;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        table tr:hover {{
            background: {self.colors['background']};
        }}
        
        /* Cards */
        .issue-card, .gap-card, .uvp-card, .advantage-card {{
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            border-left: 4px solid {self.colors['primary']};
            background: {self.colors['background']};
        }}
        
        .priority-critical {{
            border-left-color: {self.colors['danger']};
        }}
        
        .priority-high {{
            border-left-color: {self.colors['warning']};
        }}
        
        .priority-medium {{
            border-left-color: {self.colors['accent']};
        }}
        
        .priority-low {{
            border-left-color: {self.colors['success']};
        }}
        
        /* Badges */
        .importance-badge, .entity-tag, .level-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
            margin-right: 8px;
        }}
        
        .importance-badge.high {{
            background: {self.colors['danger']};
            color: white;
        }}
        
        .importance-badge.medium {{
            background: {self.colors['warning']};
            color: white;
        }}
        
        .importance-badge.low {{
            background: {self.colors['success']};
            color: white;
        }}
        
        /* Footer */
        .report-footer {{
            margin-top: 40px;
            padding: 30px;
            background: #f9fafb;
            border-radius: 12px;
            text-align: center;
            color: #6b7280;
        }}
        
        .watermark {{
            font-size: 0.9em;
            opacity: 0.7;
            margin-bottom: 10px;
        }}
        
        /* Print Styles */
        @media print {{
            .page-break {{
                page-break-before: always;
            }}
            
            .report-container {{
                max-width: 100%;
            }}
            
            section {{
                box-shadow: none;
            }}
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .report-title {{
                font-size: 1.8em;
            }}
            
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
            
            .visualizations-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>"""
    
    def _generate_chart_scripts(self) -> str:
        """Generate Chart.js library and helper functions"""
        
        return """
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script>
        // Chart.js configuration
        Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        Chart.defaults.font.size = 12;
        
        // Helper function to create charts
        function createChart(canvasId, type, data, options = {}) {
            const ctx = document.getElementById(canvasId);
            if (!ctx) return;
            
            new Chart(ctx, {
                type: type,
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    ...options
                }
            });
        }
    </script>"""
    
    def _generate_chart_initializations(self, sections: List[ReportSection]) -> str:
        """Generate JavaScript to initialize all charts"""
        
        script = "\n    <script>\n        document.addEventListener('DOMContentLoaded', function() {"
        
        chart_index = 0
        for section in sections:
            for i, viz in enumerate(section.visualizations):
                chart_id = f"chart_{section.title.replace(' ', '_')}_{i}"
                chart_js = self._generate_chart_config(chart_id, viz, chart_index)
                script += f"\n            {chart_js}"
                chart_index += 1
        
        script += "\n        });\n    </script>"
        
        return script
    
    def _generate_chart_config(
        self,
        chart_id: str,
        viz: VisualizationData,
        index: int
    ) -> str:
        """Generate Chart.js configuration for a visualization"""
        
        # Default colors
        colors = viz.colors if viz.colors else [
            '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899'
        ]
        
        if viz.chart_type == ChartType.GAUGE:
            # Gauge chart (using doughnut)
            score = viz.data.get('score', 0)
            max_score = viz.data.get('max', 100)
            percentage = (score / max_score) * 100
            
            return f"""
            createChart('{chart_id}', 'doughnut', {{
                labels: ['Score', 'Remaining'],
                datasets: [{{
                    data: [{score:.1f}, {max_score - score:.1f}],
                    backgroundColor: ['{self._get_score_color(percentage)}', '#e5e7eb'],
                    borderWidth: 0
                }}]
            }}, {{
                cutout: '70%',
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{ enabled: false }}
                }}
            }});"""
        
        elif viz.chart_type == ChartType.BAR:
            labels_json = json.dumps(viz.labels)
            values_json = json.dumps(viz.values)
            
            return f"""
            createChart('{chart_id}', 'bar', {{
                labels: {labels_json},
                datasets: [{{
                    data: {values_json},
                    backgroundColor: '{colors[0]}',
                    borderRadius: 6
                }}]
            }}, {{
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{ beginAtZero: true }}
                }}
            }});"""
        
        elif viz.chart_type == ChartType.PIE or viz.chart_type == ChartType.DONUT:
            labels_json = json.dumps(viz.labels)
            values_json = json.dumps(viz.values)
            colors_json = json.dumps(colors[:len(viz.values)])
            cutout = '50%' if viz.chart_type == ChartType.DONUT else '0%'
            
            return f"""
            createChart('{chart_id}', 'doughnut', {{
                labels: {labels_json},
                datasets: [{{
                    data: {values_json},
                    backgroundColor: {colors_json},
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }}]
            }}, {{
                cutout: '{cutout}',
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{ padding: 15, usePointStyle: true }}
                    }}
                }}
            }});"""
        
        elif viz.chart_type == ChartType.RADAR:
            labels_json = json.dumps(viz.labels)
            values_json = json.dumps(viz.values)
            
            return f"""
            createChart('{chart_id}', 'radar', {{
                labels: {labels_json},
                datasets: [{{
                    data: {values_json},
                    backgroundColor: 'rgba(59, 130, 246, 0.2)',
                    borderColor: '{colors[0]}',
                    borderWidth: 2,
                    pointBackgroundColor: '{colors[0]}',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '{colors[0]}'
                }}]
            }}, {{
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    r: {{
                        beginAtZero: true,
                        max: 100
                    }}
                }}
            }});"""
        
        elif viz.chart_type == ChartType.LINE:
            labels_json = json.dumps(viz.labels)
            values_json = json.dumps(viz.values)
            
            return f"""
            createChart('{chart_id}', 'line', {{
                labels: {labels_json},
                datasets: [{{
                    data: {values_json},
                    borderColor: '{colors[0]}',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4,
                    fill: true
                }}]
            }}, {{
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{ beginAtZero: true }}
                }}
            }});"""
        
        return ""
    
    def _get_score_color(self, score: float) -> str:
        """Get color based on score"""
        if score >= 80:
            return '#10b981'
        elif score >= 60:
            return '#3b82f6'
        elif score >= 40:
            return '#f59e0b'
        else:
            return '#ef4444'
    
    def _get_theme_colors(self) -> Dict[str, str]:
        """Get color scheme for current theme with enhanced distinctiveness"""
        
        themes = {
            ReportTheme.PROFESSIONAL: {
                'primary': '#1e40af',      # Deep blue
                'secondary': '#3b82f6',    # Bright blue  
                'accent': '#60a5fa',       # Light blue
                'success': '#10b981',      # Green
                'warning': '#f59e0b',      # Orange
                'danger': '#ef4444',       # Red
                'text': '#1f2937',         # Dark gray
                'background': '#f9fafb',   # Very light gray
                'card_bg': '#ffffff',      # White cards
                'border': '#e5e7eb',       # Light border
                'font': "'Inter', 'Segoe UI', system-ui, sans-serif",
                'heading_weight': 'bold',  # Changed from '700' for PDF compatibility
                'border_radius': '8px'
            },
            ReportTheme.MODERN: {
                'primary': '#7c3aed',      # Purple
                'secondary': '#a78bfa',    # Light purple
                'accent': '#06b6d4',       # Cyan
                'success': '#10b981',      # Green
                'warning': '#f59e0b',      # Orange
                'danger': '#f43f5e',       # Pink-red
                'text': '#0f172a',         # Very dark blue
                'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',  # Gradient background
                'card_bg': '#ffffff',      # White cards with shadow
                'border': '#c4b5fd',       # Purple border
                'font': "'Poppins', 'Arial', sans-serif",
                'heading_weight': 'bold',  # Changed from '600' for PDF compatibility
                'border_radius': '16px'
            },
            ReportTheme.MINIMAL: {
                'primary': '#000000',      # Black
                'secondary': '#374151',    # Dark gray
                'accent': '#6b7280',       # Medium gray
                'success': '#059669',      # Dark green
                'warning': '#d97706',      # Dark orange
                'danger': '#dc2626',       # Dark red
                'text': '#111827',         # Almost black
                'background': '#ffffff',   # Pure white
                'card_bg': '#fafafa',      # Off-white cards
                'border': '#e5e7eb',       # Very light gray border
                'font': "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif",
                'heading_weight': 'normal',   # Changed from '300' for PDF compatibility
                'border_radius': '0px'     # Sharp corners
            },
            ReportTheme.COLORFUL: {
                'primary': '#ec4899',      # Pink
                'secondary': '#8b5cf6',    # Purple
                'accent': '#06b6d4',       # Cyan
                'success': '#10b981',      # Green
                'warning': '#f59e0b',      # Orange
                'danger': '#ef4444',       # Red
                'text': '#1f2937',         # Dark gray
                'background': 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',  # Warm gradient
                'card_bg': '#ffffff',      # White cards
                'border': '#fbbf24',       # Golden border
                'font': "'Quicksand', 'Comic Sans MS', cursive",
                'heading_weight': 'bold',  # Changed from '700' for PDF compatibility
                'border_radius': '20px'    # Very rounded
            }
        }
        
        return themes.get(self.config.theme, themes[ReportTheme.PROFESSIONAL])
