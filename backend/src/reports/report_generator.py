"""
Report Generation Service

Creates professional HTML/PDF reports from AI analysis results with:
- Executive summary
- Detailed analysis sections
- Visual data representations (charts, graphs)
- Actionable recommendations
- Competitive benchmarking
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import base64
from io import BytesIO

# Import AI analysis results
import sys
sys.path.append('..')

from ..ai.ai_analysis_service import ComprehensiveAnalysisResult


class ReportFormat(str, Enum):
    """Report output formats"""
    HTML = "html"
    PDF = "pdf"
    JSON = "json"
    MARKDOWN = "markdown"


class ReportTheme(str, Enum):
    """Visual themes for reports"""
    PROFESSIONAL = "professional"  # Blue/gray corporate
    MODERN = "modern"  # Purple/teal contemporary
    MINIMAL = "minimal"  # Black/white clean
    COLORFUL = "colorful"  # Multi-color vibrant


class ChartType(str, Enum):
    """Chart types for visualizations"""
    BAR = "bar"
    PIE = "pie"
    LINE = "line"
    RADAR = "radar"
    GAUGE = "gauge"
    DONUT = "donut"


@dataclass
class ReportConfig:
    """Configuration for report generation"""
    format: ReportFormat = ReportFormat.HTML
    theme: ReportTheme = ReportTheme.PROFESSIONAL
    include_charts: bool = True
    include_recommendations: bool = True
    include_competitive: bool = True
    include_raw_data: bool = False
    page_breaks: bool = True  # For PDF
    logo_url: Optional[str] = None
    company_name: Optional[str] = None
    watermark: Optional[str] = None


@dataclass
class VisualizationData:
    """Data for creating visualizations"""
    chart_type: ChartType
    title: str
    data: Dict[str, Any]
    labels: List[str] = field(default_factory=list)
    values: List[float] = field(default_factory=list)
    colors: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class ReportSection:
    """A section in the report"""
    title: str
    content: str
    level: int = 2  # Heading level (h2, h3, etc.)
    visualizations: List[VisualizationData] = field(default_factory=list)
    subsections: List['ReportSection'] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutiveSummary:
    """Executive summary for the report"""
    overview: str
    key_findings: List[str] = field(default_factory=list)
    quick_stats: Dict[str, Any] = field(default_factory=dict)
    recommendation_count: int = 0
    priority_actions: List[str] = field(default_factory=list)


@dataclass
class GeneratedReport:
    """Complete generated report"""
    content: str  # HTML, PDF bytes, JSON, or Markdown
    format: ReportFormat
    metadata: Dict[str, Any] = field(default_factory=dict)
    file_size_bytes: int = 0
    generation_time_ms: float = 0.0
    sections_count: int = 0


class ReportGenerator:
    """
    Professional report generator for AI analysis results.
    
    Features:
    - Multiple output formats (HTML, PDF, JSON, Markdown)
    - Visual themes
    - Charts and visualizations
    - Executive summaries
    - Actionable recommendations
    - Competitive benchmarking
    """
    
    def __init__(self, config: Optional[ReportConfig] = None):
        """
        Initialize report generator.
        
        Args:
            config: Report configuration
        """
        self.config = config or ReportConfig()
        self._theme_colors = self._get_theme_colors()
    
    async def generate_report(
        self,
        analysis_result: ComprehensiveAnalysisResult,
        title: str = "Content Analysis Report",
        url: Optional[str] = None,
        config: Optional[ReportConfig] = None
    ) -> GeneratedReport:
        """
        Generate comprehensive report from analysis results.
        
        Args:
            analysis_result: AI analysis results
            title: Report title
            url: Analyzed URL
            config: Override configuration
            
        Returns:
            GeneratedReport with content and metadata
        """
        start_time = datetime.now()
        config = config or self.config
        
        # Generate executive summary
        exec_summary = self._generate_executive_summary(analysis_result)
        
        # Create report sections
        sections = []
        
        # 1. Overview section
        sections.append(self._create_overview_section(
            analysis_result, url, exec_summary
        ))
        
        # 2. Summary section
        if analysis_result.summary:
            sections.append(self._create_summary_section(analysis_result.summary))
        
        # 3. Sentiment & Tone section
        if analysis_result.sentiment:
            sections.append(self._create_sentiment_section(analysis_result.sentiment))
        
        # 4. Topics & Themes section
        if analysis_result.topics:
            sections.append(self._create_topics_section(analysis_result.topics))
        
        # 5. SEO Analysis section
        if analysis_result.seo:
            sections.append(self._create_seo_section(analysis_result.seo))
        
        # 6. Readability section
        if analysis_result.readability:
            sections.append(self._create_readability_section(analysis_result.readability))
        
        # 7. Competitive Analysis section
        if analysis_result.competitive and config.include_competitive:
            sections.append(self._create_competitive_section(analysis_result.competitive))
        
        # 8. Recommendations section
        if config.include_recommendations:
            sections.append(self._create_recommendations_section(
                analysis_result, exec_summary
            ))
        
        # Generate report in requested format
        if config.format == ReportFormat.HTML:
            content = self._generate_html_report(
                title, exec_summary, sections, analysis_result, config
            )
        elif config.format == ReportFormat.PDF:
            content = await self._generate_pdf_report(
                title, exec_summary, sections, analysis_result, config
            )
        elif config.format == ReportFormat.JSON:
            content = self._generate_json_report(
                title, exec_summary, sections, analysis_result
            )
        elif config.format == ReportFormat.MARKDOWN:
            content = self._generate_markdown_report(
                title, exec_summary, sections, analysis_result
            )
        else:
            raise ValueError(f"Unsupported format: {config.format}")
        
        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds() * 1000
        
        return GeneratedReport(
            content=content,
            format=config.format,
            metadata={
                'title': title,
                'url': url,
                'generated_at': datetime.now().isoformat(),
                'theme': config.theme.value,
                'sections': len(sections),
                'total_cost': analysis_result.total_llm_cost,
                'analyzers_run': analysis_result.analyzers_run
            },
            file_size_bytes=len(content) if isinstance(content, (str, bytes)) else 0,
            generation_time_ms=generation_time,
            sections_count=len(sections)
        )
    
    def _generate_executive_summary(
        self,
        result: ComprehensiveAnalysisResult
    ) -> ExecutiveSummary:
        """Generate executive summary from results"""
        
        # Overview (use provided executive summary or create one)
        overview = result.executive_summary or "Comprehensive content analysis completed."
        
        # Key findings (use provided insights)
        key_findings = result.key_insights[:5] if result.key_insights else []
        
        # Quick stats
        quick_stats = {
            'Overall Quality': f"{result.overall_quality_score:.0f}/100",
            'Analyzers Run': len(result.analyzers_run),
            'Processing Time': f"{result.total_processing_time_ms/1000:.1f}s",
            'Analysis Cost': f"${result.total_llm_cost:.4f}"
        }
        
        # Add specific scores
        if result.seo:
            quick_stats['SEO Score'] = f"{result.seo.score.overall_score:.0f}/100"
        if result.readability:
            quick_stats['Readability'] = f"Grade {result.readability.readability_metrics.average_grade_level:.1f}"
        if result.sentiment:
            quick_stats['Sentiment'] = f"{result.sentiment.sentiment.score:+.2f}"
        
        # Priority actions (use provided action items)
        priority_actions = result.action_items[:5] if result.action_items else []
        
        return ExecutiveSummary(
            overview=overview,
            key_findings=key_findings,
            quick_stats=quick_stats,
            recommendation_count=len(result.action_items) if result.action_items else 0,
            priority_actions=priority_actions
        )
    
    def _create_overview_section(
        self,
        result: ComprehensiveAnalysisResult,
        url: Optional[str],
        exec_summary: ExecutiveSummary
    ) -> ReportSection:
        """Create overview section"""
        
        content = f"""
<div class="overview-box">
    <p class="overview-text">{exec_summary.overview}</p>
</div>

<div class="stats-grid">
"""
        
        for stat_name, stat_value in exec_summary.quick_stats.items():
            content += f"""
    <div class="stat-card">
        <div class="stat-label">{stat_name}</div>
        <div class="stat-value">{stat_value}</div>
    </div>
"""
        
        content += "</div>"
        
        if url:
            content += f"""
<div class="meta-info">
    <strong>Analyzed URL:</strong> <a href="{url}" target="_blank">{url}</a><br>
    <strong>Analysis Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
</div>
"""
        
        # Add quality score visualization
        visualizations = []
        if result.overall_quality_score:
            visualizations.append(VisualizationData(
                chart_type=ChartType.GAUGE,
                title="Overall Content Quality",
                data={'score': result.overall_quality_score},
                description=f"Overall quality score: {result.overall_quality_score:.0f}/100"
            ))
        
        return ReportSection(
            title="Executive Summary",
            content=content,
            level=2,
            visualizations=visualizations
        )
    
    def _create_summary_section(self, summary_result) -> ReportSection:
        """Create content summary section"""
        
        content = f"""
<div class="summary-content">
    <h3>Short Summary</h3>
    <p class="summary-text">{summary_result.short_summary.text}</p>
    
    <h3>Main Takeaway</h3>
    <p class="highlight-box">{summary_result.main_takeaway}</p>
    
    <h3>Key Points</h3>
    <ul class="key-points-list">
"""
        
        for point in summary_result.key_points[:7]:
            importance_badge = "high" if point.importance > 0.7 else "medium" if point.importance > 0.4 else "low"
            content += f"""
        <li class="key-point">
            <span class="importance-badge {importance_badge}">{point.importance:.1f}</span>
            <span class="point-text">{point.point}</span>
            {f'<span class="point-category">({point.category})</span>' if point.category else ''}
        </li>
"""
        
        content += """
    </ul>
</div>
"""
        
        # Add reading time visualization
        visualizations = []
        if summary_result.medium_summary:
            reading_time = summary_result.medium_summary.reading_time_seconds / 60  # Convert seconds to minutes
            visualizations.append(VisualizationData(
                chart_type=ChartType.BAR,
                title="Content Metrics",
                data={
                    'reading_time': reading_time,
                    'word_counts': {
                        'short': summary_result.short_summary.word_count,
                        'medium': summary_result.medium_summary.word_count,
                        'long': summary_result.long_summary.word_count if summary_result.long_summary else 0
                    }
                },
                labels=['Short', 'Medium', 'Long'],
                values=[
                    summary_result.short_summary.word_count,
                    summary_result.medium_summary.word_count,
                    summary_result.long_summary.word_count if summary_result.long_summary else 0
                ],
                description=f"Estimated reading time: {reading_time:.1f} minutes"
            ))
        
        return ReportSection(
            title="Content Summary",
            content=content,
            level=2,
            visualizations=visualizations
        )
    
    def _create_sentiment_section(self, sentiment_result) -> ReportSection:
        """Create sentiment analysis section"""
        
        sentiment = sentiment_result.sentiment
        tone = sentiment_result.tone
        
        # Sentiment color
        sent_color = self._get_sentiment_color(sentiment.score)
        
        content = f"""
<div class="sentiment-overview">
    <div class="sentiment-score" style="color: {sent_color}">
        <h3>Sentiment Score</h3>
        <div class="score-display">{sentiment.score:+.2f}</div>
        <div class="score-label">{sentiment.polarity.value.replace('_', ' ').title()}</div>
    </div>
    
    <div class="tone-info">
        <h3>Tone Analysis</h3>
        <p><strong>Primary Tone:</strong> {tone.primary_tone.value.title()}</p>
        <p><strong>Formality:</strong> {tone.formality_level:.0%}</p>
        <p><strong>Professionalism:</strong> {tone.professionalism_score:.0%}</p>
        {'<p><strong>Secondary Tones:</strong> ' + ', '.join(t.value for t in tone.secondary_tones[:3]) + '</p>' if tone.secondary_tones else ''}
    </div>
</div>

<div class="sentiment-details">
    <h3>Sentiment Breakdown</h3>
    <div class="sentiment-bars">
        <div class="sent-bar">
            <span>Positive:</span>
            <div class="bar-container">
                <div class="bar positive" style="width: {sentiment.positive_ratio*100}%"></div>
            </div>
            <span>{sentiment.positive_ratio:.0%}</span>
        </div>
        <div class="sent-bar">
            <span>Neutral:</span>
            <div class="bar-container">
                <div class="bar neutral" style="width: {sentiment.neutral_ratio*100}%"></div>
            </div>
            <span>{sentiment.neutral_ratio:.0%}</span>
        </div>
        <div class="sent-bar">
            <span>Negative:</span>
            <div class="bar-container">
                <div class="bar negative" style="width: {sentiment.negative_ratio*100}%"></div>
            </div>
            <span>{sentiment.negative_ratio:.0%}</span>
        </div>
    </div>
</div>
"""
        
        # Add emotions if available
        if sentiment_result.emotions:
            content += """
<div class="emotions-section">
    <h3>Emotional Content</h3>
    <div class="emotions-grid">
"""
            for emotion in sentiment_result.emotions[:5]:
                content += f"""
        <div class="emotion-card">
            <div class="emotion-name">{emotion.emotion.value.title()}</div>
            <div class="emotion-intensity">
                <div class="intensity-bar" style="width: {emotion.intensity*100}%"></div>
            </div>
            <div class="emotion-value">{emotion.intensity:.0%}</div>
        </div>
"""
            content += """
    </div>
</div>
"""
        
        # Visualizations
        visualizations = []
        
        # Sentiment pie chart
        visualizations.append(VisualizationData(
            chart_type=ChartType.PIE,
            title="Sentiment Distribution",
            data={
                'positive': sentiment.positive_ratio,
                'neutral': sentiment.neutral_ratio,
                'negative': sentiment.negative_ratio
            },
            labels=['Positive', 'Neutral', 'Negative'],
            values=[sentiment.positive_ratio, sentiment.neutral_ratio, sentiment.negative_ratio],
            colors=['#10b981', '#6b7280', '#ef4444']
        ))
        
        # Emotions radar chart
        if sentiment_result.emotions:
            visualizations.append(VisualizationData(
                chart_type=ChartType.RADAR,
                title="Emotional Profile",
                data={
                    'emotions': {e.emotion.value: e.intensity for e in sentiment_result.emotions[:8]}
                },
                labels=[e.emotion.value.title() for e in sentiment_result.emotions[:8]],
                values=[e.intensity for e in sentiment_result.emotions[:8]]
            ))
        
        return ReportSection(
            title="Sentiment & Tone Analysis",
            content=content,
            level=2,
            visualizations=visualizations
        )
    
    def _create_topics_section(self, topics_result) -> ReportSection:
        """Create topics and themes section"""
        
        content = """
<div class="topics-overview">
    <h3>Main Topics</h3>
    <div class="topics-list">
"""
        
        for topic in topics_result.main_topics[:10]:
            relevance_width = topic.relevance_score * 100
            content += f"""
        <div class="topic-item">
            <div class="topic-header">
                <span class="topic-name">{topic.name}</span>
                <span class="topic-score">{topic.relevance_score:.1%}</span>
            </div>
            <div class="relevance-bar">
                <div class="bar-fill" style="width: {relevance_width}%"></div>
            </div>
            <p class="topic-description">{topic.description}</p>
            {f'<div class="topic-keywords">Keywords: {", ".join(topic.keywords[:5])}</div>' if topic.keywords else ''}
        </div>
"""
        
        content += """
    </div>
</div>
"""
        
        # Themes
        if topics_result.themes:
            content += """
<div class="themes-section">
    <h3>Themes</h3>
    <div class="themes-grid">
"""
            for theme in topics_result.themes:
                content += f"""
        <div class="theme-card">
            <h4>{theme.name}</h4>
            <p>{theme.description}</p>
            <div class="theme-confidence">Confidence: {theme.confidence:.0%}</div>
        </div>
"""
            content += """
    </div>
</div>
"""
        
        # Named Entities
        if topics_result.named_entities:
            content += """
<div class="entities-section">
    <h3>Named Entities</h3>
    <div class="entities-list">
"""
            for entity in topics_result.named_entities[:15]:
                content += f"""
        <span class="entity-tag {entity.entity_type.value}">{entity.text}</span>
"""
            content += """
    </div>
</div>
"""
        
        # Visualizations
        visualizations = []
        
        # Topics bar chart
        if topics_result.main_topics:
            visualizations.append(VisualizationData(
                chart_type=ChartType.BAR,
                title="Topic Relevance",
                data={
                    'topics': {t.name: t.relevance_score for t in topics_result.main_topics[:8]}
                },
                labels=[t.name for t in topics_result.main_topics[:8]],
                values=[t.relevance_score for t in topics_result.main_topics[:8]]
            ))
        
        return ReportSection(
            title="Topics & Themes",
            content=content,
            level=2,
            visualizations=visualizations
        )
    
    def _create_seo_section(self, seo_result) -> ReportSection:
        """Create SEO analysis section"""
        
        score = seo_result.score
        
        content = f"""
<div class="seo-overview">
    <div class="seo-score-display">
        <h3>Overall SEO Score</h3>
        <div class="big-score" style="color: {self._get_score_color(score.overall_score)}">
            {score.overall_score:.0f}/100
        </div>
    </div>
    
    <div class="seo-subscores">
        <div class="subscore-item">
            <span>Content</span>
            <div class="score-bar">
                <div class="bar-fill" style="width: {score.content_score}%"></div>
            </div>
            <span>{score.content_score:.0f}</span>
        </div>
        <div class="subscore-item">
            <span>Technical</span>
            <div class="score-bar">
                <div class="bar-fill" style="width: {score.technical_score}%"></div>
            </div>
            <span>{score.technical_score:.0f}</span>
        </div>
        <div class="subscore-item">
            <span>Keywords</span>
            <div class="score-bar">
                <div class="bar-fill" style="width: {score.keyword_score}%"></div>
            </div>
            <span>{score.keyword_score:.0f}</span>
        </div>
        <div class="subscore-item">
            <span>Structure</span>
            <div class="score-bar">
                <div class="bar-fill" style="width: {score.structure_score}%"></div>
            </div>
            <span>{score.structure_score:.0f}</span>
        </div>
    </div>
</div>
"""
        
        # Keywords
        if seo_result.primary_keywords:
            content += """
<div class="keywords-section">
    <h3>Primary Keywords</h3>
    <table class="keyword-table">
        <thead>
            <tr>
                <th>Keyword</th>
                <th>Density</th>
                <th>Title</th>
                <th>Headings</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
"""
            for kw in seo_result.primary_keywords[:10]:
                status = "✓ Optimal" if kw.is_optimal else "⚠ Needs work"
                status_class = "optimal" if kw.is_optimal else "needs-work"
                content += f"""
            <tr>
                <td>{kw.keyword}</td>
                <td>{kw.density:.1f}%</td>
                <td>{'✓' if kw.in_title else '✗'}</td>
                <td>{'✓' if kw.in_headings else '✗'}</td>
                <td class="{status_class}">{status}</td>
            </tr>
"""
            content += """
        </tbody>
    </table>
</div>
"""
        
        # Issues
        if seo_result.issues:
            content += """
<div class="seo-issues">
    <h3>Issues & Recommendations</h3>
"""
            for issue in seo_result.issues[:10]:
                priority_class = f"priority-{issue.priority.value}"
                content += f"""
    <div class="issue-card {priority_class}">
        <div class="issue-header">
            <span class="issue-priority">{issue.priority.value.upper()}</span>
            <span class="issue-category">{issue.category}</span>
        </div>
        <div class="issue-content">
            <p class="issue-text">{issue.issue}</p>
            <p class="issue-recommendation"><strong>Recommendation:</strong> {issue.recommendation}</p>
        </div>
    </div>
"""
            content += """
</div>
"""
        
        # Visualizations
        visualizations = []
        
        # SEO score breakdown
        visualizations.append(VisualizationData(
            chart_type=ChartType.RADAR,
            title="SEO Score Breakdown",
            data={
                'content': score.content_score,
                'technical': score.technical_score,
                'keywords': score.keyword_score,
                'metadata': score.metadata_score,
                'structure': score.structure_score,
                'links': score.link_score
            },
            labels=['Content', 'Technical', 'Keywords', 'Metadata', 'Structure', 'Links'],
            values=[
                score.content_score,
                score.technical_score,
                score.keyword_score,
                score.metadata_score,
                score.structure_score,
                score.link_score
            ]
        ))
        
        return ReportSection(
            title="SEO Analysis",
            content=content,
            level=2,
            visualizations=visualizations
        )
    
    def _create_readability_section(self, read_result) -> ReportSection:
        """Create readability analysis section"""
        
        metrics = read_result.readability_metrics
        accessibility = read_result.accessibility
        
        content = f"""
<div class="readability-overview">
    <div class="reading-level">
        <h3>Reading Level</h3>
        <div class="level-badge {metrics.reading_level.value}">
            {metrics.reading_level.value.replace('_', ' ').title()}
        </div>
        <div class="grade-level">Grade {metrics.average_grade_level:.1f}</div>
    </div>
    
    <div class="readability-scores">
        <h3>Readability Metrics</h3>
        <div class="metric-item">
            <span>Flesch Reading Ease:</span>
            <span>{metrics.flesch_reading_ease:.0f}/100</span>
        </div>
        <div class="metric-item">
            <span>Flesch-Kincaid Grade:</span>
            <span>{metrics.flesch_kincaid_grade:.1f}</span>
        </div>
        <div class="metric-item">
            <span>SMOG Index:</span>
            <span>{metrics.smog_index:.1f}</span>
        </div>
        <div class="metric-item">
            <span>Gunning Fog:</span>
            <span>{metrics.gunning_fog_index:.1f}</span>
        </div>
    </div>
</div>

<div class="text-complexity">
    <h3>Text Complexity</h3>
    <div class="complexity-grid">
        <div class="complexity-stat">
            <div class="stat-label">Avg Words/Sentence</div>
            <div class="stat-value">{read_result.text_complexity.avg_words_per_sentence:.1f}</div>
        </div>
        <div class="complexity-stat">
            <div class="stat-label">Complex Words</div>
            <div class="stat-value">{read_result.text_complexity.complex_words_percentage:.1f}%</div>
        </div>
        <div class="complexity-stat">
            <div class="stat-label">Long Sentences</div>
            <div class="stat-value">{read_result.text_complexity.long_sentences_percentage:.1f}%</div>
        </div>
        <div class="complexity-stat">
            <div class="stat-label">Reading Time</div>
            <div class="stat-value">{read_result.estimated_reading_time_minutes:.1f} min</div>
        </div>
    </div>
</div>

<div class="accessibility-section">
    <h3>Accessibility (WCAG)</h3>
    <div class="wcag-level">
        <span class="level-badge level-{accessibility.level.value.lower()}">{accessibility.level.value}</span>
        <span class="level-score">Score: {accessibility.score:.0f}/100</span>
    </div>
</div>
"""
        
        # Improvements
        if read_result.improvements:
            content += """
<div class="improvements-section">
    <h3>Suggested Improvements</h3>
"""
            for improvement in read_result.improvements[:5]:
                content += f"""
    <div class="improvement-card priority-{improvement.priority}">
        <div class="improvement-type">{improvement.type.title()}</div>
        <p class="improvement-issue">{improvement.issue}</p>
        <div class="improvement-example">
            <strong>Before:</strong> {improvement.example[:100]}...
        </div>
        <div class="improvement-suggestion">
            <strong>Better:</strong> {improvement.suggestion[:100]}...
        </div>
    </div>
"""
            content += """
</div>
"""
        
        # Visualizations
        visualizations = []
        
        # Grade levels comparison
        visualizations.append(VisualizationData(
            chart_type=ChartType.BAR,
            title="Grade Level Comparison",
            data={
                'flesch_kincaid': metrics.flesch_kincaid_grade,
                'smog': metrics.smog_index,
                'gunning_fog': metrics.gunning_fog_index,
                'coleman_liau': metrics.coleman_liau_index,
                'ari': metrics.automated_readability_index
            },
            labels=['FK Grade', 'SMOG', 'Gunning Fog', 'Coleman-Liau', 'ARI'],
            values=[
                metrics.flesch_kincaid_grade,
                metrics.smog_index,
                metrics.gunning_fog_index,
                metrics.coleman_liau_index,
                metrics.automated_readability_index
            ]
        ))
        
        return ReportSection(
            title="Readability Analysis",
            content=content,
            level=2,
            visualizations=visualizations
        )
    
    def _create_competitive_section(self, comp_result) -> ReportSection:
        """Create competitive analysis section"""
        
        content = f"""
<div class="competitive-overview">
    <h3>Competitive Position</h3>
    <div class="competitive-score">
        <div class="big-score" style="color: {self._get_score_color(comp_result.overall_competitive_score)}">
            {comp_result.overall_competitive_score:.0f}/100
        </div>
        <p>Overall Competitive Strength</p>
    </div>
</div>
"""
        
        # Content Gaps
        if comp_result.content_gaps:
            content += """
<div class="content-gaps">
    <h3>Content Gaps</h3>
"""
            for gap in comp_result.content_gaps:
                priority_class = f"priority-{gap.priority.value}"
                content += f"""
    <div class="gap-card {priority_class}">
        <div class="gap-header">
            <h4>{gap.topic}</h4>
            <span class="gap-priority">{gap.priority.value.upper()}</span>
        </div>
        <p class="gap-description">{gap.description}</p>
        <p class="gap-impact"><strong>Impact:</strong> {gap.potential_impact}</p>
        <p class="gap-action"><strong>Action:</strong> {gap.suggested_action}</p>
    </div>
"""
            content += """
</div>
"""
        
        # UVPs
        if comp_result.unique_value_propositions:
            content += """
<div class="uvps-section">
    <h3>Unique Value Propositions</h3>
"""
            for uvp in comp_result.unique_value_propositions:
                strength_class = uvp.strength.value
                content += f"""
    <div class="uvp-card strength-{strength_class}">
        <h4>{uvp.aspect}</h4>
        <p>{uvp.description}</p>
        <div class="uvp-strength">Strength: {uvp.strength.value.title()}</div>
    </div>
"""
            content += """
</div>
"""
        
        # Competitive Advantages
        if comp_result.competitive_advantages:
            content += """
<div class="advantages-section">
    <h3>Competitive Advantages</h3>
"""
            for adv in comp_result.competitive_advantages:
                content += f"""
    <div class="advantage-card">
        <div class="adv-category">{adv.category.replace('_', ' ').title()}</div>
        <p class="adv-text">{adv.advantage}</p>
        <p class="adv-leverage"><strong>How to Leverage:</strong> {adv.how_to_leverage}</p>
    </div>
"""
            content += """
</div>
"""
        
        # Visualizations
        visualizations = []
        
        # Content depth
        if comp_result.content_depth:
            visualizations.append(VisualizationData(
                chart_type=ChartType.GAUGE,
                title="Content Depth",
                data={'score': comp_result.content_depth.depth_score, 'max': 10},
                description=f"Depth: {comp_result.content_depth.comprehensiveness}"
            ))
        
        return ReportSection(
            title="Competitive Analysis",
            content=content,
            level=2,
            visualizations=visualizations
        )
    
    def _create_recommendations_section(
        self,
        result: ComprehensiveAnalysisResult,
        exec_summary: ExecutiveSummary
    ) -> ReportSection:
        """Create recommendations section"""
        
        content = """
<div class="recommendations-overview">
    <h3>Priority Actions</h3>
    <div class="priority-actions">
"""
        
        for i, action in enumerate(exec_summary.priority_actions, 1):
            content += f"""
        <div class="action-item">
            <div class="action-number">{i}</div>
            <div class="action-text">{action}</div>
        </div>
"""
        
        content += """
    </div>
</div>
"""
        
        # Collect all recommendations
        all_recommendations = []
        
        if result.seo and result.seo.recommendations:
            all_recommendations.extend([
                ('SEO', rec) for rec in result.seo.recommendations
            ])
        
        if result.readability and result.readability.improvements:
            all_recommendations.extend([
                ('Readability', imp.suggestion) for imp in result.readability.improvements[:3]
            ])
        
        if result.sentiment and result.sentiment.recommendations:
            all_recommendations.extend([
                ('Tone & Sentiment', rec) for rec in result.sentiment.recommendations
            ])
        
        if result.competitive and result.competitive.recommendations:
            all_recommendations.extend([
                ('Competitive', rec) for rec in result.competitive.recommendations
            ])
        
        if all_recommendations:
            content += """
<div class="all-recommendations">
    <h3>Detailed Recommendations</h3>
"""
            for category, rec in all_recommendations[:15]:
                content += f"""
    <div class="recommendation-item">
        <span class="rec-category">{category}</span>
        <span class="rec-text">{rec}</span>
    </div>
"""
            content += """
</div>
"""
        
        return ReportSection(
            title="Recommendations & Action Plan",
            content=content,
            level=2
        )
    
    def _get_theme_colors(self) -> Dict[str, str]:
        """Get color scheme for current theme"""
        
        themes = {
            ReportTheme.PROFESSIONAL: {
                'primary': '#1e40af',
                'secondary': '#3b82f6',
                'accent': '#60a5fa',
                'success': '#10b981',
                'warning': '#f59e0b',
                'danger': '#ef4444',
                'text': '#1f2937',
                'background': '#ffffff'
            },
            ReportTheme.MODERN: {
                'primary': '#7c3aed',
                'secondary': '#a78bfa',
                'accent': '#06b6d4',
                'success': '#10b981',
                'warning': '#f59e0b',
                'danger': '#ef4444',
                'text': '#0f172a',
                'background': '#f8fafc'
            },
            ReportTheme.MINIMAL: {
                'primary': '#000000',
                'secondary': '#374151',
                'accent': '#6b7280',
                'success': '#059669',
                'warning': '#d97706',
                'danger': '#dc2626',
                'text': '#111827',
                'background': '#ffffff'
            },
            ReportTheme.COLORFUL: {
                'primary': '#ec4899',
                'secondary': '#8b5cf6',
                'accent': '#06b6d4',
                'success': '#10b981',
                'warning': '#f59e0b',
                'danger': '#ef4444',
                'text': '#1f2937',
                'background': '#fef3c7'
            }
        }
        
        return themes.get(self.config.theme, themes[ReportTheme.PROFESSIONAL])
    
    def _get_sentiment_color(self, score: float) -> str:
        """Get color based on sentiment score"""
        if score > 0.5:
            return '#10b981'  # Green
        elif score > 0:
            return '#60a5fa'  # Light blue
        elif score > -0.5:
            return '#f59e0b'  # Orange
        else:
            return '#ef4444'  # Red
    
    def _get_score_color(self, score: float) -> str:
        """Get color based on score (0-100)"""
        if score >= 80:
            return '#10b981'  # Green
        elif score >= 60:
            return '#60a5fa'  # Blue
        elif score >= 40:
            return '#f59e0b'  # Orange
        else:
            return '#ef4444'  # Red
    
    def _generate_html_report(
        self,
        title: str,
        exec_summary: ExecutiveSummary,
        sections: List[ReportSection],
        result: ComprehensiveAnalysisResult,
        config: ReportConfig
    ) -> str:
        """Generate HTML report"""
        
        from .html_template import HTMLReportTemplate
        
        template = HTMLReportTemplate(config)
        metadata = {
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_cost': result.total_llm_cost,
            'processing_time_ms': result.total_processing_time_ms
        }
        
        return template.generate(title, exec_summary, sections, metadata)
    
    async def _generate_pdf_report(
        self,
        title: str,
        exec_summary: ExecutiveSummary,
        sections: List[ReportSection],
        result: ComprehensiveAnalysisResult,
        config: ReportConfig
    ) -> bytes:
        """Generate PDF report"""
        
        from .pdf_generator import PDFGenerator
        from .html_template import HTMLReportTemplate
        
        # Generate HTML specifically for PDF (no external fonts)
        template = HTMLReportTemplate(config, for_pdf=True)
        metadata = {
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_cost': result.total_llm_cost,
            'processing_time_ms': result.total_processing_time_ms
        }
        html_content = template.generate(title, exec_summary, sections, metadata)
        
        # Convert to PDF
        pdf_gen = PDFGenerator()
        html_content = pdf_gen.optimize_for_pdf(html_content)
        pdf_bytes = await pdf_gen.generate_pdf(html_content)
        
        return pdf_bytes
    
    def _generate_json_report(
        self,
        title: str,
        exec_summary: ExecutiveSummary,
        sections: List[ReportSection],
        result: ComprehensiveAnalysisResult
    ) -> str:
        """Generate JSON report"""
        
        report_data = {
            'title': title,
            'generated_at': datetime.now().isoformat(),
            'executive_summary': {
                'overview': exec_summary.overview,
                'key_findings': exec_summary.key_findings,
                'quick_stats': exec_summary.quick_stats,
                'priority_actions': exec_summary.priority_actions
            },
            'analysis_results': {
                'overall_quality_score': result.overall_quality_score,
                'total_cost': result.total_llm_cost,
                'processing_time_ms': result.total_processing_time_ms,
                'analyzers_run': result.analyzers_run
            },
            'sections': [
                {
                    'title': section.title,
                    'level': section.level,
                    'has_visualizations': len(section.visualizations) > 0
                }
                for section in sections
            ]
        }
        
        return json.dumps(report_data, indent=2)
    
    def _generate_markdown_report(
        self,
        title: str,
        exec_summary: ExecutiveSummary,
        sections: List[ReportSection],
        result: ComprehensiveAnalysisResult
    ) -> str:
        """Generate Markdown report"""
        
        md = f"""# {title}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

{exec_summary.overview}

### Quick Stats

"""
        
        for stat_name, stat_value in exec_summary.quick_stats.items():
            md += f"- **{stat_name}:** {stat_value}\n"
        
        md += "\n### Key Findings\n\n"
        for finding in exec_summary.key_findings:
            md += f"- {finding}\n"
        
        md += "\n### Priority Actions\n\n"
        for i, action in enumerate(exec_summary.priority_actions, 1):
            md += f"{i}. {action}\n"
        
        md += "\n---\n\n"
        
        for section in sections:
            md += f"\n## {section.title}\n\n"
            # Strip HTML tags for markdown
            import re
            clean_content = re.sub(r'<[^>]+>', '', section.content)
            md += clean_content + "\n\n"
        
        return md
