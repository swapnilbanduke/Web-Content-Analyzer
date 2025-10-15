"""
Advanced Streamlit Web Interface for Content Analysis Platform

Features:
- Single URL and batch processing
- Real-time progress tracking
- Advanced visualizations and charts
- Export to PDF, JSON, CSV
- Analysis history management
- Theme customization
- Responsive design
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from pathlib import Path
import asyncio
import json
import csv
import io
from typing import List, Dict, Any, Optional
import sys
from dataclasses import asdict

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ai import create_ai_analysis_service, AnalysisConfig
from src.scrapers import WebScraper, ScraperConfig, ContentExtractor
from src.reports import (
    ReportGenerator, 
    ReportConfig, 
    ReportFormat, 
    ReportTheme
)


# Page configuration
st.set_page_config(
    page_title="Content Analysis Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea22 0%, #764ba222 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #667eea44;
        margin: 0.5rem 0;
    }
    .score-excellent {
        color: #10b981;
        font-weight: 700;
    }
    .score-good {
        color: #3b82f6;
        font-weight: 700;
    }
    .score-fair {
        color: #f59e0b;
        font-weight: 700;
    }
    .score-poor {
        color: #ef4444;
        font-weight: 700;
    }
    .stAlert {
        border-radius: 8px;
    }
    .batch-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .history-item {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = None
    if 'batch_results' not in st.session_state:
        st.session_state.batch_results = []
    if 'api_keys_configured' not in st.session_state:
        st.session_state.api_keys_configured = False


def get_score_class(score: float) -> str:
    """Get CSS class for score display"""
    if score >= 0.8:
        return "score-excellent"
    elif score >= 0.6:
        return "score-good"
    elif score >= 0.4:
        return "score-fair"
    else:
        return "score-poor"


def create_gauge_chart(value: float, title: str, max_value: float = 100) -> go.Figure:
    """Create a gauge chart for scores"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20}},
        delta={'reference': max_value * 0.7},
        gauge={
            'axis': {'range': [None, max_value], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, max_value * 0.4], 'color': '#fee2e2'},
                {'range': [max_value * 0.4, max_value * 0.7], 'color': '#fef3c7'},
                {'range': [max_value * 0.7, max_value], 'color': '#d1fae5'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.9
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor="white",
        font={'color': "darkblue", 'family': "Arial"}
    )
    
    return fig


def create_sentiment_chart(sentiment_data: Dict[str, float]) -> go.Figure:
    """Create sentiment distribution chart"""
    labels = list(sentiment_data.keys())
    values = list(sentiment_data.values())
    
    colors = {
        'positive': '#10b981',
        'neutral': '#6b7280',
        'negative': '#ef4444'
    }
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker=dict(colors=[colors.get(label.lower(), '#3b82f6') for label in labels])
    )])
    
    fig.update_layout(
        title="Sentiment Distribution",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig


def create_topics_chart(topics: List[Dict[str, Any]]) -> go.Figure:
    """Create topics relevance chart"""
    if not topics:
        return None
    
    # Take top 10 topics
    top_topics = sorted(topics, key=lambda x: getattr(x, 'relevance_score', 0), reverse=True)[:10]
    
    names = [getattr(t, 'name', 'Unknown') for t in top_topics]
    relevance = [getattr(t, 'relevance_score', 0) * 100 for t in top_topics]
    
    fig = go.Figure(data=[go.Bar(
        x=relevance,
        y=names,
        orientation='h',
        marker=dict(
            color=relevance,
            colorscale='Viridis',
            showscale=True
        )
    )])
    
    fig.update_layout(
        title="Top Topics by Relevance",
        xaxis_title="Relevance (%)",
        yaxis_title="Topic",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig


def create_seo_radar_chart(seo_scores: Dict[str, float]) -> go.Figure:
    """Create SEO breakdown radar chart"""
    categories = list(seo_scores.keys())
    values = [score * 100 for score in seo_scores.values()]
    
    # Close the polygon
    categories_plot = categories + [categories[0]]
    values_plot = values + [values[0]]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values_plot,
        theta=categories_plot,
        fill='toself',
        fillcolor='rgba(102, 126, 234, 0.3)',
        line=dict(color='rgb(102, 126, 234)', width=2)
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        title="SEO Score Breakdown",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig


def create_readability_comparison(readability_data: Dict[str, Any]) -> go.Figure:
    """Create readability metrics comparison"""
    formulas = readability_data.get('formulas', {})
    
    if not formulas:
        return None
    
    names = []
    scores = []
    
    for name, data in formulas.items():
        if isinstance(data, dict) and 'score' in data:
            names.append(name.replace('_', ' ').title())
            scores.append(data['score'])
    
    if not names:
        return None
    
    fig = go.Figure(data=[go.Bar(
        x=names,
        y=scores,
        marker=dict(
            color=scores,
            colorscale='RdYlGn',
            showscale=True
        ),
        text=scores,
        textposition='outside'
    )])
    
    fig.update_layout(
        title="Readability Formulas Comparison",
        xaxis_title="Formula",
        yaxis_title="Score",
        height=400,
        margin=dict(l=20, r=20, t=40, b=40)
    )
    
    return fig


async def analyze_url(
    url: str,
    ai_provider: str,
    ai_model: str,
    analyze_seo: bool = True,
    analyze_sentiment: bool = True,
    analyze_readability: bool = True,
    extract_topics: bool = True,
    include_competitive: bool = False,
    competitor_urls: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Analyze a single URL"""
    try:
        # Scrape content
        config = ScraperConfig()
        scraper = WebScraper(
            timeout=config.timeout,
            max_retries=config.max_retries,
            max_content_size=config.max_content_size,
            respect_robots_txt=config.respect_robots_txt
        )
        scraped_content = await scraper.scrape_url(url)
        
        # Check if scraping was successful
        if not scraped_content.html_content:
            return {
                'success': False,
                'url': url,
                'error': 'Failed to fetch content from URL. The page may be blocking scrapers or the URL is invalid.'
            }
        
        # Extract content and metadata
        content_extractor = ContentExtractor()
        extracted_data = content_extractor.extract(
            html=scraped_content.html_content,
            base_url=url
        )
        
        # Validate extracted content
        if not extracted_data.processed_text or len(extracted_data.processed_text.strip()) == 0:
            return {
                'success': False,
                'url': url,
                'error': 'No meaningful text content found on the page. The page may be heavily JavaScript-based, empty, or inaccessible.'
            }
        
        if extracted_data.word_count < 10:
            return {
                'success': False,
                'url': url,
                'error': f'Insufficient content found (only {extracted_data.word_count} words). The page may require JavaScript or have minimal text.'
            }
        
        # Configure analysis
        config = AnalysisConfig(
            summarize=True,
            analyze_sentiment=analyze_sentiment,
            extract_topics=extract_topics,
            analyze_seo=analyze_seo,
            score_readability=analyze_readability,
            analyze_competitive=include_competitive
        )
        
        # Create AI service
        ai_service = await create_ai_analysis_service(
            provider=ai_provider.lower(),
            model=ai_model
        )
        
        # Scrape competitor URLs if competitive analysis is enabled
        competitor_context = None
        if include_competitive and competitor_urls and len(competitor_urls) > 0:
            competitor_contents = []
            for comp_url in competitor_urls[:3]:  # Limit to 3 competitors
                try:
                    comp_scraped = await scraper.scrape_url(comp_url)
                    if comp_scraped.html_content:
                        comp_data = content_extractor.extract(
                            html=comp_scraped.html_content,
                            base_url=comp_url
                        )
                        if comp_data.processed_text and comp_data.word_count > 50:
                            competitor_contents.append({
                                'url': comp_url,
                                'title': comp_data.metadata.title or 'Competitor',
                                'content': comp_data.processed_text[:2000],  # Limit to 2000 chars
                                'word_count': comp_data.word_count
                            })
                except:
                    continue
            
            # Build competitor context string
            if competitor_contents:
                context_parts = [f"Competitor Analysis ({len(competitor_contents)} competitors):\n"]
                for i, comp in enumerate(competitor_contents, 1):
                    context_parts.append(f"\nCompetitor {i}: {comp['title']} ({comp['url']})")
                    context_parts.append(f"Word Count: {comp['word_count']}")
                    context_parts.append(f"Content Preview:\n{comp['content'][:500]}...\n")
                competitor_context = "\n".join(context_parts)
        
        # Perform analysis
        analysis_result = await ai_service.analyze(
            content=extracted_data.processed_text,
            title=extracted_data.metadata.title or "Untitled",
            meta_description=extracted_data.metadata.description,
            url=url,
            headings=extracted_data.headings,
            competitor_context=competitor_context,
            config=config
        )
        
        return {
            'success': True,
            'url': url,
            'title': extracted_data.metadata.title or "Untitled",
            'analysis': analysis_result,
            'timestamp': datetime.now().isoformat(),
            'word_count': extracted_data.word_count,
            'processing_time': analysis_result.total_processing_time_ms
        }
        
    except Exception as e:
        # Provide more detailed error messages
        error_msg = str(e)
        if 'validation error' in error_msg.lower():
            error_msg = 'Content extraction failed: The page content is empty or invalid. Try a different URL.'
        elif 'timeout' in error_msg.lower():
            error_msg = 'Request timeout: The page took too long to load. Try again or use a different URL.'
        elif 'connection' in error_msg.lower():
            error_msg = 'Connection error: Unable to reach the URL. Check the URL and your internet connection.'
        
        return {
            'success': False,
            'url': url,
            'error': error_msg
        }


async def batch_analyze_urls(
    urls: List[str],
    ai_provider: str,
    ai_model: str,
    analyze_seo: bool = True,
    analyze_sentiment: bool = True,
    analyze_readability: bool = True,
    extract_topics: bool = True,
    progress_callback=None
) -> List[Dict[str, Any]]:
    """Analyze multiple URLs in batch"""
    results = []
    total = len(urls)
    
    for idx, url in enumerate(urls, 1):
        if progress_callback:
            progress_callback(idx, total, url)
        
        result = await analyze_url(
            url, 
            ai_provider, 
            ai_model,
            analyze_seo=analyze_seo,
            analyze_sentiment=analyze_sentiment,
            analyze_readability=analyze_readability,
            extract_topics=extract_topics
        )
        results.append(result)
    
    return results


def export_to_csv(results: List[Dict[str, Any]]) -> bytes:
    """Export analysis results to CSV"""
    output = io.StringIO()
    
    # Define CSV structure
    fieldnames = [
        'URL', 'Title', 'Status', 'Quality Score', 'SEO Score',
        'Readability Score', 'Sentiment Score', 'Word Count',
        'Processing Time (ms)', 'Timestamp', 'Error'
    ]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for result in results:
        if result.get('success'):
            analysis = result.get('analysis')
            row = {
                'URL': result.get('url', ''),
                'Title': result.get('title', ''),
                'Status': 'Success',
                'Quality Score': f"{analysis.overall_quality_score:.2f}%",
                'SEO Score': f"{analysis.seo.score.overall_score:.2f}%" if analysis.seo else 'N/A',
                'Readability Score': f"{analysis.readability.overall_score:.2f}%" if analysis.readability else 'N/A',
                'Sentiment Score': f"{analysis.sentiment.sentiment.score:.2f}" if analysis.sentiment else 'N/A',
                'Word Count': result.get('word_count', 0),
                'Processing Time (ms)': result.get('processing_time', 0),
                'Timestamp': result.get('timestamp', ''),
                'Error': ''
            }
        else:
            row = {
                'URL': result.get('url', ''),
                'Title': '',
                'Status': 'Failed',
                'Quality Score': '',
                'SEO Score': '',
                'Readability Score': '',
                'Sentiment Score': '',
                'Word Count': '',
                'Processing Time (ms)': '',
                'Timestamp': result.get('timestamp', datetime.now().isoformat()),
                'Error': result.get('error', 'Unknown error')
            }
        
        writer.writerow(row)
    
    return output.getvalue().encode('utf-8')


def export_to_json(results: List[Dict[str, Any]]) -> bytes:
    """Export analysis results to JSON"""
    
    def convert_to_serializable(obj):
        """Convert non-serializable objects to serializable format"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [convert_to_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return convert_to_serializable(obj.__dict__)
        else:
            return obj
    
    # Convert to JSON-serializable format
    export_data = []
    
    for result in results:
        if result.get('success'):
            analysis = result.get('analysis')
            
            # Convert analysis result to dict and handle datetime
            export_item = {
                'url': result.get('url'),
                'title': result.get('title'),
                'timestamp': result.get('timestamp'),
                'word_count': result.get('word_count'),
                'processing_time_ms': result.get('processing_time'),
                'overall_quality_score': analysis.overall_quality_score,
                'summary': convert_to_serializable(asdict(analysis.summary)) if analysis.summary else None,
                'sentiment': convert_to_serializable(asdict(analysis.sentiment)) if analysis.sentiment else None,
                'topics': convert_to_serializable(asdict(analysis.topics)) if analysis.topics else None,
                'seo': convert_to_serializable(asdict(analysis.seo)) if analysis.seo else None,
                'readability': convert_to_serializable(asdict(analysis.readability)) if analysis.readability else None,
                'competitive': convert_to_serializable(asdict(analysis.competitive)) if analysis.competitive else None
            }
        else:
            export_item = {
                'url': result.get('url'),
                'error': result.get('error'),
                'timestamp': result.get('timestamp', datetime.now().isoformat())
            }
        
        export_data.append(export_item)
    
    return json.dumps(export_data, indent=2, default=str).encode('utf-8')


async def generate_pdf_report(result: Dict[str, Any], theme: str = 'professional') -> bytes:
    """Generate PDF report for a single analysis"""
    if not result.get('success'):
        return None
    
    analysis = result.get('analysis')
    
    # Configure report
    theme_map = {
        'professional': ReportTheme.PROFESSIONAL,
        'modern': ReportTheme.MODERN,
        'minimal': ReportTheme.MINIMAL,
        'colorful': ReportTheme.COLORFUL
    }
    
    config = ReportConfig(
        format=ReportFormat.PDF,
        theme=theme_map.get(theme.lower(), ReportTheme.PROFESSIONAL),
        include_charts=True,
        include_recommendations=True,
        company_name="Content Analysis Platform",
        page_breaks=True
    )
    
    # Generate report
    generator = ReportGenerator(config)
    report = await generator.generate_report(
        analysis_result=analysis,
        title=result.get('title', 'Content Analysis'),
        url=result.get('url')
    )
    
    return report.content


def render_sidebar():
    """Render sidebar configuration"""
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # API Configuration
        with st.expander("🔑 API Settings", expanded=True):
            ai_provider = st.selectbox(
                "AI Provider",
                ["OpenAI", "Anthropic"],
                help="Select your preferred AI provider"
            )
            
            if ai_provider == "OpenAI":
                default_model = "gpt-4-turbo-preview"
                models = ["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo"]
            else:
                default_model = "claude-3-opus-20240229"
                models = [
                    "claude-3-opus-20240229",
                    "claude-3-sonnet-20240229",
                    "claude-3-haiku-20240307"
                ]
            
            ai_model = st.selectbox("Model", models, index=0)
            
            api_key = st.text_input(
                "API Key",
                type="password",
                help="Enter your API key"
            )
            
            if api_key:
                import os
                if ai_provider == "OpenAI":
                    os.environ["OPENAI_API_KEY"] = api_key
                else:
                    os.environ["ANTHROPIC_API_KEY"] = api_key
                st.session_state.api_keys_configured = True
                st.success("✅ API key configured")
            else:
                st.warning("⚠️ Please enter your API key")
        
        # Analysis Options
        with st.expander("📊 Analysis Options", expanded=True):
            analyze_seo = st.checkbox(
                "SEO Analysis",
                value=True,
                help="Analyze SEO performance, keywords, and optimization opportunities"
            )
            
            analyze_sentiment = st.checkbox(
                "Sentiment Analysis",
                value=True,
                help="Analyze content sentiment and emotional tone"
            )
            
            analyze_readability = st.checkbox(
                "Readability Analysis",
                value=True,
                help="Score content readability and complexity"
            )
            
            extract_topics = st.checkbox(
                "Topic Extraction",
                value=True,
                help="Extract main topics and themes from content"
            )
            
            include_competitive = st.checkbox(
                "Include Competitive Analysis",
                value=False,
                help="Compare with competitor URLs"
            )
            
            competitor_urls = []
            if include_competitive:
                competitor_input = st.text_area(
                    "Competitor URLs (one per line)",
                    height=100
                )
                if competitor_input:
                    competitor_urls = [url.strip() for url in competitor_input.split('\n') if url.strip()]
        
        # Report Theme
        with st.expander("🎨 Report Theme"):
            report_theme = st.selectbox(
                "Theme",
                ["Professional", "Modern", "Minimal", "Colorful"],
                help="Select report visual theme"
            )
        
        st.markdown("---")
        
        # Statistics
        st.markdown("### 📈 Statistics")
        total_analyses = len(st.session_state.analysis_history)
        st.metric("Total Analyses", total_analyses)
        
        if st.session_state.batch_results:
            st.metric("Batch Results", len(st.session_state.batch_results))
        
        return {
            'ai_provider': ai_provider,
            'ai_model': ai_model,
            'analyze_seo': analyze_seo,
            'analyze_sentiment': analyze_sentiment,
            'analyze_readability': analyze_readability,
            'extract_topics': extract_topics,
            'include_competitive': include_competitive,
            'competitor_urls': competitor_urls,
            'report_theme': report_theme
        }


def render_single_analysis_tab(config: Dict[str, Any]):
    """Render single URL analysis tab"""
    st.markdown("### 🔍 Single URL Analysis")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        url = st.text_input(
            "Enter URL to analyze",
            placeholder="https://example.com/article",
            help="Enter the full URL including https://"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_button = st.button("🚀 Analyze", type="primary", use_container_width=True)
    
    if analyze_button and url:
        if not st.session_state.api_keys_configured:
            st.error("❌ Please configure your API key in the sidebar")
            return
        
        with st.spinner(f"Analyzing {url}..."):
            # Run analysis
            result = asyncio.run(analyze_url(
                url=url,
                ai_provider=config['ai_provider'],
                ai_model=config['ai_model'],
                analyze_seo=config.get('analyze_seo', True),
                analyze_sentiment=config.get('analyze_sentiment', True),
                analyze_readability=config.get('analyze_readability', True),
                extract_topics=config.get('extract_topics', True),
                include_competitive=config['include_competitive'],
                competitor_urls=config['competitor_urls']
            ))
            
            # Save to session state
            st.session_state.current_analysis = result
            st.session_state.analysis_history.insert(0, result)
            
            # Keep only last 50 analyses
            st.session_state.analysis_history = st.session_state.analysis_history[:50]
        
        st.rerun()
    
    # Display current analysis
    if st.session_state.current_analysis:
        display_analysis_results(st.session_state.current_analysis, config)


def render_batch_analysis_tab(config: Dict[str, Any]):
    """Render batch URL analysis tab"""
    st.markdown("### 📋 Batch URL Analysis")
    
    st.info("💡 Enter multiple URLs to analyze them in batch. Results will be available for export.")
    
    urls_input = st.text_area(
        "Enter URLs (one per line)",
        height=200,
        placeholder="https://example.com/article1\nhttps://example.com/article2\nhttps://example.com/article3"
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        process_button = st.button("⚡ Process Batch", type="primary", use_container_width=True)
    
    with col2:
        clear_button = st.button("🗑️ Clear Results", use_container_width=True)
    
    if clear_button:
        st.session_state.batch_results = []
        st.rerun()
    
    if process_button and urls_input:
        if not st.session_state.api_keys_configured:
            st.error("❌ Please configure your API key in the sidebar")
            return
        
        urls = [url.strip() for url in urls_input.split('\n') if url.strip()]
        
        if not urls:
            st.warning("⚠️ Please enter at least one URL")
            return
        
        st.markdown(f"**Processing {len(urls)} URLs...**")
        
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(current, total, url):
            progress = current / total
            progress_bar.progress(progress)
            status_text.text(f"Processing {current}/{total}: {url}")
        
        # Run batch analysis
        results = asyncio.run(batch_analyze_urls(
            urls=urls,
            ai_provider=config['ai_provider'],
            ai_model=config['ai_model'],
            analyze_seo=config.get('analyze_seo', True),
            analyze_sentiment=config.get('analyze_sentiment', True),
            analyze_readability=config.get('analyze_readability', True),
            extract_topics=config.get('extract_topics', True),
            progress_callback=update_progress
        ))
        
        st.session_state.batch_results = results
        
        # Add to history
        for result in results:
            st.session_state.analysis_history.insert(0, result)
        
        st.session_state.analysis_history = st.session_state.analysis_history[:100]
        
        status_text.text("✅ Batch processing complete!")
        st.rerun()
    
    # Display batch results
    if st.session_state.batch_results:
        display_batch_results(st.session_state.batch_results, config)


def display_analysis_results(result: Dict[str, Any], config: Dict[str, Any]):
    """Display detailed analysis results"""
    if not result.get('success'):
        st.error(f"❌ Analysis failed: {result.get('error')}")
        return
    
    analysis = result.get('analysis')
    
    # Header
    st.markdown("---")
    st.markdown(f"## 📄 {result.get('title', 'Analysis Results')}")
    st.markdown(f"**URL:** {result.get('url')}")
    
    # Quick Stats
    col1, col2, col3, col4 = st.columns(4)
    
    quality_score = analysis.overall_quality_score
    with col1:
        st.metric(
            "Quality Score",
            f"{quality_score:.1f}%",
            delta=f"{quality_score - 70:.1f}% vs target"
        )
    
    with col2:
        if analysis.seo:
            seo_score = analysis.seo.score.overall_score
            st.metric("SEO Score", f"{seo_score:.1f}%")
    
    with col3:
        if analysis.readability:
            read_score = analysis.readability.overall_score
            st.metric("Readability", f"{read_score:.1f}%")
    
    with col4:
        st.metric("Word Count", f"{result.get('word_count', 0):,}")
    
    # Tabs for different sections
    tab_list = [
        "📊 Overview",
        "📝 Summary",
        "💭 Sentiment",
        "🏷️ Topics",
        "🔍 SEO",
        "📖 Readability",
        "🎯 Recommendations"
    ]
    
    # Add competitive tab if competitive analysis is present
    if analysis.competitive:
        tab_list.insert(6, "🏆 Competitive")
    
    tabs = st.tabs(tab_list)
    
    # Overview Tab
    with tabs[0]:
        render_overview_tab(analysis)
    
    # Summary Tab
    with tabs[1]:
        render_summary_tab(analysis)
    
    # Sentiment Tab
    with tabs[2]:
        render_sentiment_tab(analysis)
    
    # Topics Tab
    with tabs[3]:
        render_topics_tab(analysis)
    
    # SEO Tab
    with tabs[4]:
        render_seo_tab(analysis)
    
    # Readability Tab
    with tabs[5]:
        render_readability_tab(analysis)
    
    # Competitive Tab (if available)
    tab_index = 6
    if analysis.competitive:
        with tabs[tab_index]:
            render_competitive_tab(analysis)
        tab_index += 1
    
    # Recommendations Tab
    with tabs[tab_index]:
        render_recommendations_tab(analysis)
    
    # Export Options
    st.markdown("---")
    st.markdown("### 📥 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Export HTML Report", use_container_width=True):
            with st.spinner("Generating HTML report..."):
                html_report = asyncio.run(generate_html_report(result, config['report_theme']))
                if html_report:
                    st.download_button(
                        "⬇️ Download HTML",
                        data=html_report,
                        file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                        mime="text/html",
                        use_container_width=True
                    )
    
    with col2:
        if st.button("📑 Export PDF Report", use_container_width=True):
            with st.spinner("Generating PDF report..."):
                pdf_report = asyncio.run(generate_pdf_report(result, config['report_theme']))
                if pdf_report:
                    # Check if this is an HTML fallback (PDF library not installed)
                    if pdf_report.startswith(b'<!DOCTYPE html>') or pdf_report.startswith(b'<html>'):
                        # PDF library not available - show HTML with print instructions
                        st.warning("⚠️ PDF generation libraries not installed")
                        st.info("""
                        **Alternative Options:**
                        1. Click 'Export HTML Report' below and print to PDF from your browser (Ctrl+P)
                        2. Install PDF library: `pip install xhtml2pdf` (Windows) or `pip install weasyprint` (Linux/Mac)
                        3. Use the HTML report directly
                        """)
                        st.download_button(
                            "⬇️ Download HTML Instructions",
                            data=pdf_report,
                            file_name=f"pdf_instructions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                            mime="text/html",
                            use_container_width=True
                        )
                    else:
                        # Actual PDF generated - show success with library info
                        st.success("✅ PDF generated successfully using xhtml2pdf!")
                        st.download_button(
                            "⬇️ Download PDF",
                            data=pdf_report,
                            file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
    
    with col3:
        if st.button("📊 Export JSON Data", use_container_width=True):
            json_data = export_to_json([result])
            st.download_button(
                "⬇️ Download JSON",
                data=json_data,
                file_name=f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )


def display_batch_results(results: List[Dict[str, Any]], config: Dict[str, Any]):
    """Display batch analysis results"""
    st.markdown("---")
    st.markdown("## 📊 Batch Results")
    
    # Summary statistics
    total = len(results)
    successful = sum(1 for r in results if r.get('success'))
    failed = total - successful
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total URLs", total)
    col2.metric("Successful", successful, delta=f"{successful/total*100:.1f}%")
    col3.metric("Failed", failed)
    
    # Results table
    st.markdown("### 📋 Results Summary")
    
    table_data = []
    for result in results:
        if result.get('success'):
            analysis = result.get('analysis')
            table_data.append({
                'URL': result.get('url', '')[:50] + '...' if len(result.get('url', '')) > 50 else result.get('url', ''),
                'Title': result.get('title', '')[:40] + '...' if len(result.get('title', '')) > 40 else result.get('title', ''),
                'Quality': f"{analysis.overall_quality_score:.1f}%",
                'SEO': f"{analysis.seo.score.overall_score:.1f}%" if analysis.seo else 'N/A',
                'Readability': f"{analysis.readability.overall_score:.1f}%" if analysis.readability else 'N/A',
                'Words': result.get('word_count', 0),
                'Status': '✅ Success'
            })
        else:
            table_data.append({
                'URL': result.get('url', '')[:50] + '...' if len(result.get('url', '')) > 50 else result.get('url', ''),
                'Title': '',
                'Quality': '',
                'SEO': '',
                'Readability': '',
                'Words': '',
                'Status': f"❌ {result.get('error', 'Failed')[:30]}"
            })
    
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Export options
    st.markdown("### 📥 Export Batch Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv_data = export_to_csv(results)
        st.download_button(
            "📊 Download CSV",
            data=csv_data,
            file_name=f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        json_data = export_to_json(results)
        st.download_button(
            "📄 Download JSON",
            data=json_data,
            file_name=f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col3:
        st.button("📧 Email Results", use_container_width=True, disabled=True, help="Coming soon!")


def render_overview_tab(analysis):
    """Render overview tab with gauges"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Quality gauge
        quality_chart = create_gauge_chart(
            analysis.overall_quality_score,
            "Overall Quality Score"
        )
        st.plotly_chart(quality_chart, use_container_width=True)
    
    with col2:
        # SEO gauge
        if analysis.seo:
            seo_chart = create_gauge_chart(
                analysis.seo.score.overall_score,
                "SEO Score"
            )
            st.plotly_chart(seo_chart, use_container_width=True)
    
    # Processing info
    st.markdown("### ℹ️ Analysis Information")
    info_col1, info_col2, info_col3 = st.columns(3)
    
    with info_col1:
        st.metric("Analyzers Run", len(analysis.analyzers_run))
    
    with info_col2:
        st.metric("Processing Time", f"{analysis.total_processing_time_ms:.0f}ms")
    
    with info_col3:
        st.metric("Total Cost", f"${analysis.total_llm_cost:.4f}")


def render_summary_tab(analysis):
    """Render summary tab"""
    if not analysis.summary:
        st.info("No summary analysis available")
        return
    
    summary = analysis.summary
    
    st.markdown("### 📝 Content Summary")
    
    # Summary lengths
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Short Summary**")
        if summary.short_summary:
            st.info(summary.short_summary.text)
    
    with col2:
        st.markdown("**Medium Summary**")
        if summary.medium_summary:
            st.info(summary.medium_summary.text)
    
    with col3:
        st.markdown("**Long Summary**")
        if summary.long_summary:
            st.info(summary.long_summary.text)
    
    # Main takeaway
    if summary.main_takeaway:
        st.markdown("### 🎯 Main Takeaway")
        st.success(summary.main_takeaway)
    
    # Key points
    st.markdown("### 📌 Key Points")
    for point in summary.key_points:
        importance = point.importance if hasattr(point, 'importance') else 0.5
        emoji = "🔴" if importance > 0.8 else "🟡" if importance > 0.5 else "🟢"
        point_text = point.point if hasattr(point, 'point') else str(point)
        st.markdown(f"{emoji} {point_text} *(Importance: {importance:.0%})*")


def render_sentiment_tab(analysis):
    """Render sentiment tab"""
    if not analysis.sentiment:
        st.info("No sentiment analysis available")
        return
    
    sentiment = analysis.sentiment
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Sentiment score
        score = sentiment.sentiment.score
        st.markdown(f"### Sentiment Score")
        st.markdown(f"<h1 class='{get_score_class((score+1)/2)}'>{score:+.2f}</h1>", unsafe_allow_html=True)
        
        st.markdown(f"**Confidence:** {sentiment.sentiment.confidence:.0%}")
        
        # Tone
        st.markdown("### 🎭 Tone")
        st.markdown(f"**Primary:** {sentiment.tone.primary_tone}")
        if sentiment.tone.secondary_tones:
            st.markdown(f"**Secondary:** {', '.join([str(t) for t in sentiment.tone.secondary_tones])}")
    
    with col2:
        # Sentiment distribution
        sentiment_dist = {
            'Positive': sentiment.sentiment.positive_ratio,
            'Neutral': sentiment.sentiment.neutral_ratio,
            'Negative': sentiment.sentiment.negative_ratio
        }
        chart = create_sentiment_chart(sentiment_dist)
        st.plotly_chart(chart, use_container_width=True)
    
    # Emotions
    if sentiment.emotions:
        st.markdown("### 😊 Emotional Content")
        cols = st.columns(4)
        for idx, emotion_obj in enumerate(sentiment.emotions):
            with cols[idx % 4]:
                emotion_name = emotion_obj.emotion if hasattr(emotion_obj, 'emotion') else str(emotion_obj)
                emotion_intensity = emotion_obj.intensity if hasattr(emotion_obj, 'intensity') else 0
                st.metric(str(emotion_name).title(), f"{emotion_intensity:.0%}")


def render_topics_tab(analysis):
    """Render topics tab"""
    if not analysis.topics:
        st.info("No topics analysis available")
        return
    
    topics_data = analysis.topics
    
    # Topics chart
    if topics_data.main_topics:
        chart = create_topics_chart(topics_data.main_topics)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
    
    # Themes
    st.markdown("### 🎨 Themes")
    if topics_data.themes:
        for theme in topics_data.themes:
            theme_name = getattr(theme, 'name', 'Unknown Theme')
            theme_desc = getattr(theme, 'description', '')
            st.markdown(f"• **{theme_name}**: {theme_desc}")
    
    # Entities
    st.markdown("### 🏢 Named Entities")
    if topics_data.named_entities:
        entity_cols = st.columns(3)
        for idx, entity in enumerate(topics_data.named_entities[:12]):
            with entity_cols[idx % 3]:
                entity_text = getattr(entity, 'text', 'Unknown')
                entity_type = getattr(entity, 'entity_type', 'Unknown')
                entity_confidence = getattr(entity, 'confidence', 0)
                st.markdown(f"**{entity_text}**")
                st.caption(f"Type: {entity_type} | Confidence: {entity_confidence:.0%}")


def render_seo_tab(analysis):
    """Render SEO tab"""
    if not analysis.seo:
        st.info("💡 No SEO analysis available. Enable SEO analysis in the sidebar options.")
        return
    
    seo = analysis.seo
    
    # Overall SEO Score
    st.markdown("### 📊 SEO Performance")
    overall_score = seo.score.overall_score
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        score_color = "🟢" if overall_score >= 80 else "🟡" if overall_score >= 60 else "🔴"
        st.metric("Overall SEO Score", f"{score_color} {overall_score:.1f}%")
    with col2:
        st.metric("Keyword Score", f"{seo.score.keyword_score:.1f}%")
    with col3:
        st.metric("Content Score", f"{seo.score.content_score:.1f}%")
    with col4:
        st.metric("Meta Score", f"{seo.score.metadata_score:.1f}%")
    
    # SEO radar chart
    st.markdown("### 🎯 SEO Breakdown")
    seo_scores = {
        'Content': seo.score.content_score,
        'Technical': seo.score.technical_score,
        'Keywords': seo.score.keyword_score,
        'Structure': seo.score.structure_score,
        'Links': seo.score.link_score,
        'Meta': seo.score.metadata_score
    }
    
    chart = create_seo_radar_chart(seo_scores)
    st.plotly_chart(chart, use_container_width=True)
    
    # Primary Keywords
    st.markdown("### 🔑 Primary Keywords")
    if seo.primary_keywords:
        keyword_df = pd.DataFrame([
            {
                'Keyword': kw.keyword,
                'Frequency': kw.frequency,
                'Density': f"{kw.density:.2f}%",
                'Prominence': f"{kw.prominence:.0%}",
                'In Title': "✅" if kw.in_title else "❌",
                'In Headings': "✅" if kw.in_headings else "❌",
                'Optimal': "✅" if kw.is_optimal else "⚠️"
            }
            for kw in seo.primary_keywords[:10]
        ])
        st.dataframe(keyword_df, use_container_width=True, hide_index=True)
    else:
        st.info("No primary keywords identified")
    
    # Meta Tags Analysis
    if seo.meta_tags:
        st.markdown("### 📝 Meta Tags")
        col1, col2 = st.columns(2)
        
        with col1:
            title_status = "✅" if seo.meta_tags.title_optimal else "⚠️"
            st.markdown(f"**Title Tag:** {title_status} {seo.meta_tags.title_length} characters")
            if not seo.meta_tags.title_optimal:
                st.caption("💡 Optimal length: 50-60 characters")
        
        with col2:
            desc_status = "✅" if seo.meta_tags.description_optimal else "⚠️"
            st.markdown(f"**Meta Description:** {desc_status} {seo.meta_tags.description_length} characters")
            if not seo.meta_tags.description_optimal:
                st.caption("💡 Optimal length: 150-160 characters")
        
        # Social media tags
        if seo.meta_tags.og_tags_present:
            st.success("✅ Open Graph tags present")
        else:
            st.warning("⚠️ Open Graph tags missing")
        
        if seo.meta_tags.twitter_tags_present:
            st.success("✅ Twitter Card tags present")
        else:
            st.warning("⚠️ Twitter Card tags missing")
    
    # Content Structure
    if seo.content_structure:
        st.markdown("### 📐 Content Structure")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Headings", seo.content_structure.total_headings)
        with col2:
            st.metric("Paragraphs", seo.content_structure.paragraph_count)
        with col3:
            st.metric("Word Count", seo.content_structure.word_count)
    
    # Issues
    if seo.issues:
        st.markdown("### ⚠️ SEO Issues & Recommendations")
        
        # Group by priority
        critical_issues = [i for i in seo.issues if i.priority == "critical"]
        high_issues = [i for i in seo.issues if i.priority == "high"]
        medium_issues = [i for i in seo.issues if i.priority == "medium"]
        
        if critical_issues:
            st.markdown("#### 🔴 Critical Issues")
            for issue in critical_issues:
                with st.expander(f"🔴 {issue.category}: {issue.title}"):
                    st.write(issue.description)
                    if issue.recommendation:
                        st.info(f"💡 **Fix:** {issue.recommendation}")
        
        if high_issues:
            st.markdown("#### 🟡 High Priority")
            for issue in high_issues:
                with st.expander(f"🟡 {issue.category}: {issue.title}"):
                    st.write(issue.description)
                    if issue.recommendation:
                        st.info(f"💡 **Fix:** {issue.recommendation}")
        
        if medium_issues:
            st.markdown("#### 🔵 Medium Priority")
            for issue in medium_issues:
                with st.expander(f"🔵 {issue.category}: {issue.title}"):
                    st.write(issue.description)
                    if issue.recommendation:
                        st.info(f"💡 **Fix:** {issue.recommendation}")
    else:
        st.success("✅ No major SEO issues detected!")
    
    # Recommendations
    if seo.recommendations:
        st.markdown("### 💡 Recommendations")
        for i, rec in enumerate(seo.recommendations, 1):
            st.markdown(f"{i}. {rec}")
    
    # Opportunities
    if seo.opportunities:
        st.markdown("### 🚀 Growth Opportunities")
        for i, opp in enumerate(seo.opportunities, 1):
            st.markdown(f"{i}. {opp}")


def render_readability_tab(analysis):
    """Render readability tab"""
    if not analysis.readability:
        st.info("No readability analysis available")
        return
    
    readability = analysis.readability
    
    # Readability comparison
    chart = create_readability_comparison(readability.__dict__)
    if chart:
        st.plotly_chart(chart, use_container_width=True)
    
    # Grade level
    st.markdown("### 📚 Reading Level")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        reading_level = readability.readability_metrics.reading_level if readability.readability_metrics else "N/A"
        st.metric("Reading Level", str(reading_level))
    
    with col2:
        st.metric("Target Audience", readability.target_audience_grade)
    
    with col3:
        st.metric("Overall Score", f"{readability.overall_score:.0f}%")
    
    # Improvements
    if readability.improvements:
        st.markdown("### 💡 Improvement Suggestions")
        for suggestion in readability.improvements:
            suggestion_text = suggestion.suggestion if hasattr(suggestion, 'suggestion') else str(suggestion)
            st.markdown(f"• {suggestion_text}")


def render_competitive_tab(analysis):
    """Render competitive analysis tab with side-by-side comparisons"""
    if not analysis.competitive:
        st.info("💡 **Enable Competitive Analysis** to compare your content with competitors.\n\n"
                "Go to sidebar → 📊 Analysis Options → Check 'Include Competitive Analysis' → Add competitor URLs")
        return
    
    competitive = analysis.competitive
    
    # Header with gradient
    st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <h2 style='color: white; margin: 0;'>🏆 Competitive Intelligence Dashboard</h2>
            <p style='color: #f0f0f0; margin: 5px 0 0 0;'>Comprehensive analysis of your competitive positioning</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Performance Scorecard
    st.markdown("### 📊 Performance Scorecard")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        score = competitive.overall_competitive_score
        color = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔴"
        st.metric("Competitive Score", f"{score:.1f}/100", delta=f"{color}")
    
    with col2:
        if competitive.content_depth:
            depth_score = competitive.content_depth.depth_score
            st.metric("Content Depth", f"{depth_score:.1f}/10", 
                     delta="Strong" if depth_score >= 7 else "Moderate" if depth_score >= 5 else "Weak")
    
    with col3:
        if competitive.style_differentiation:
            uniqueness = competitive.style_differentiation.tone_uniqueness * 100
            st.metric("Style Uniqueness", f"{uniqueness:.0f}%",
                     delta="Distinctive" if uniqueness >= 70 else "Generic")
    
    with col4:
        gap_count = len(competitive.content_gaps) if competitive.content_gaps else 0
        high_priority = sum(1 for g in (competitive.content_gaps or []) if g.priority.value == "high")
        st.metric("Content Gaps", gap_count, delta=f"{high_priority} High Priority" if high_priority else "No Critical Gaps")
    
    st.markdown("---")
    
    # Content Gaps - Side by Side with Priority Grouping
    if competitive.content_gaps:
        st.markdown("### 🎯 Content Gap Analysis")
        st.markdown("*Identify opportunities to strengthen your content against competitors*")
        
        # Group by priority
        high_priority = [g for g in competitive.content_gaps if g.priority.value == "high"]
        medium_priority = [g for g in competitive.content_gaps if g.priority.value == "medium"]
        low_priority = [g for g in competitive.content_gaps if g.priority.value == "low"]
        
        # High Priority Gaps
        if high_priority:
            st.markdown("#### 🔴 High Priority Gaps (Immediate Action Required)")
            for i in range(0, len(high_priority), 2):
                cols = st.columns(2)
                for j, col in enumerate(cols):
                    if i + j < len(high_priority):
                        gap = high_priority[i + j]
                        with col:
                            st.markdown(f"""
                                <div style='background: #fee2e2; padding: 15px; border-radius: 8px; 
                                            border-left: 4px solid #dc2626; margin-bottom: 10px;'>
                                    <h4 style='margin-top: 0; color: #991b1b;'>🔴 {gap.topic}</h4>
                                    <p><strong>Gap:</strong> {gap.description}</p>
                                    <p><strong>Impact:</strong> {gap.potential_impact}</p>
                                    <p><strong>Action:</strong> {gap.suggested_action}</p>
                                    <p><strong>Keywords:</strong> {', '.join(gap.keywords) if gap.keywords else 'N/A'}</p>
                                </div>
                            """, unsafe_allow_html=True)
        
        # Medium Priority Gaps
        if medium_priority:
            st.markdown("#### 🟡 Medium Priority Gaps (Plan to Address)")
            for i in range(0, len(medium_priority), 2):
                cols = st.columns(2)
                for j, col in enumerate(cols):
                    if i + j < len(medium_priority):
                        gap = medium_priority[i + j]
                        with col:
                            st.markdown(f"""
                                <div style='background: #fef3c7; padding: 15px; border-radius: 8px; 
                                            border-left: 4px solid #f59e0b; margin-bottom: 10px;'>
                                    <h4 style='margin-top: 0; color: #92400e;'>🟡 {gap.topic}</h4>
                                    <p><strong>Gap:</strong> {gap.description}</p>
                                    <p><strong>Impact:</strong> {gap.potential_impact}</p>
                                    <p><strong>Action:</strong> {gap.suggested_action}</p>
                                    <p><strong>Keywords:</strong> {', '.join(gap.keywords) if gap.keywords else 'N/A'}</p>
                                </div>
                            """, unsafe_allow_html=True)
        
        # Low Priority Gaps
        if low_priority:
            st.markdown("#### 🟢 Low Priority Gaps (Nice to Have)")
            for i in range(0, len(low_priority), 2):
                cols = st.columns(2)
                for j, col in enumerate(cols):
                    if i + j < len(low_priority):
                        gap = low_priority[i + j]
                        with col:
                            st.markdown(f"""
                                <div style='background: #d1fae5; padding: 15px; border-radius: 8px; 
                                            border-left: 4px solid #10b981; margin-bottom: 10px;'>
                                    <h4 style='margin-top: 0; color: #065f46;'>🟢 {gap.topic}</h4>
                                    <p><strong>Gap:</strong> {gap.description}</p>
                                    <p><strong>Impact:</strong> {gap.potential_impact}</p>
                                    <p><strong>Action:</strong> {gap.suggested_action}</p>
                                    <p><strong>Keywords:</strong> {', '.join(gap.keywords) if gap.keywords else 'N/A'}</p>
                                </div>
                            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Unique Value Propositions - Side by Side
    if competitive.unique_value_propositions:
        st.markdown("### 💎 Your Unique Value Propositions")
        st.markdown("*What makes your content stand out from competitors*")
        
        # Group by strength
        strong = [uvp for uvp in competitive.unique_value_propositions if uvp.strength.value == "strong"]
        moderate = [uvp for uvp in competitive.unique_value_propositions if uvp.strength.value == "moderate"]
        weak = [uvp for uvp in competitive.unique_value_propositions if uvp.strength.value == "weak"]
        
        # Strong UVPs
        if strong:
            st.markdown("#### 🟢 Strong Differentiators (Leverage These!)")
            for i in range(0, len(strong), 2):
                cols = st.columns(2)
                for j, col in enumerate(cols):
                    if i + j < len(strong):
                        uvp = strong[i + j]
                        with col:
                            points_html = "".join([f"<li>{point}</li>" for point in uvp.supporting_points]) if uvp.supporting_points else ""
                            st.markdown(f"""
                                <div style='background: #d1fae5; padding: 15px; border-radius: 8px; 
                                            border-left: 4px solid #10b981; margin-bottom: 10px;'>
                                    <h4 style='margin-top: 0; color: #065f46;'>🟢 {uvp.aspect}</h4>
                                    <p><strong>Why it matters:</strong> {uvp.description}</p>
                                    {f"<p><strong>Evidence:</strong></p><ul>{points_html}</ul>" if points_html else ""}
                                </div>
                            """, unsafe_allow_html=True)
        
        # Moderate UVPs
        if moderate:
            st.markdown("#### 🟡 Moderate Differentiators (Can Be Strengthened)")
            for i in range(0, len(moderate), 2):
                cols = st.columns(2)
                for j, col in enumerate(cols):
                    if i + j < len(moderate):
                        uvp = moderate[i + j]
                        with col:
                            points_html = "".join([f"<li>{point}</li>" for point in uvp.supporting_points]) if uvp.supporting_points else ""
                            st.markdown(f"""
                                <div style='background: #fef3c7; padding: 15px; border-radius: 8px; 
                                            border-left: 4px solid #f59e0b; margin-bottom: 10px;'>
                                    <h4 style='margin-top: 0; color: #92400e;'>🟡 {uvp.aspect}</h4>
                                    <p><strong>Why it matters:</strong> {uvp.description}</p>
                                    {f"<p><strong>Evidence:</strong></p><ul>{points_html}</ul>" if points_html else ""}
                                </div>
                            """, unsafe_allow_html=True)
        
        # Weak UVPs
        if weak:
            st.markdown("#### 🔴 Weak Differentiators (Needs Development)")
            for i in range(0, len(weak), 2):
                cols = st.columns(2)
                for j, col in enumerate(cols):
                    if i + j < len(weak):
                        uvp = weak[i + j]
                        with col:
                            points_html = "".join([f"<li>{point}</li>" for point in uvp.supporting_points]) if uvp.supporting_points else ""
                            st.markdown(f"""
                                <div style='background: #fee2e2; padding: 15px; border-radius: 8px; 
                                            border-left: 4px solid #dc2626; margin-bottom: 10px;'>
                                    <h4 style='margin-top: 0; color: #991b1b;'>🔴 {uvp.aspect}</h4>
                                    <p><strong>Why it matters:</strong> {uvp.description}</p>
                                    {f"<p><strong>Evidence:</strong></p><ul>{points_html}</ul>" if points_html else ""}
                                </div>
                            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Competitive Advantages - Side by Side
    if competitive.competitive_advantages:
        st.markdown("### 💪 Competitive Advantages Analysis")
        st.markdown("*Where you outperform competitors and how to leverage it*")
        
        for i in range(0, len(competitive.competitive_advantages), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j < len(competitive.competitive_advantages):
                    adv = competitive.competitive_advantages[i + j]
                    strength_color_map = {
                        "strong": ("#d1fae5", "#10b981", "#065f46", "🟢"),
                        "moderate": ("#fef3c7", "#f59e0b", "#92400e", "🟡"),
                        "weak": ("#fee2e2", "#dc2626", "#991b1b", "🔴")
                    }
                    bg_color, border_color, text_color, icon = strength_color_map.get(adv.strength.value, ("#f3f4f6", "#9ca3af", "#374151", "⚪"))
                    
                    with col:
                        evidence_html = "".join([f"<li>{ev}</li>" for ev in adv.evidence]) if adv.evidence else ""
                        st.markdown(f"""
                            <div style='background: {bg_color}; padding: 15px; border-radius: 8px; 
                                        border-left: 4px solid {border_color}; margin-bottom: 10px;'>
                                <h4 style='margin-top: 0; color: {text_color};'>{icon} {adv.category.replace('_', ' ').title()}</h4>
                                <p><strong>Advantage:</strong> {adv.advantage}</p>
                                {f"<p><strong>Evidence:</strong></p><ul>{evidence_html}</ul>" if evidence_html else ""}
                                {f"<p><strong>💡 How to Leverage:</strong> {adv.how_to_leverage}</p>" if adv.how_to_leverage else ""}
                            </div>
                        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Market Position & Content Depth - Side by Side
    col1, col2 = st.columns(2)
    
    with col1:
        if competitive.market_position:
            st.markdown("### 📊 Market Positioning Insights")
            market = competitive.market_position
            
            st.markdown(f"""
                <div style='background: #dbeafe; padding: 15px; border-radius: 8px; 
                            border-left: 4px solid #3b82f6;'>
                    <p><strong>🎯 Positioning:</strong> {market.positioning_statement}</p>
                    <p><strong>👥 Audience Fit:</strong> {market.target_audience_alignment}</p>
                    {f"<p><strong>🏰 Competitive Moat:</strong> {market.competitive_moat}</p>" if market.competitive_moat else ""}
                    {f"<p><strong>📍 Market Segment:</strong> {market.market_segment}</p>" if market.market_segment else ""}
                </div>
            """, unsafe_allow_html=True)
            
            if market.differentiation_factors:
                st.markdown("**🔑 Key Differentiators:**")
                for factor in market.differentiation_factors:
                    st.markdown(f"• {factor}")
    
    with col2:
        if competitive.content_depth:
            st.markdown("### 📚 Content Depth Comparison")
            depth = competitive.content_depth
            
            # Progress bar for topic coverage
            coverage_color = "#10b981" if depth.topic_coverage >= 80 else "#f59e0b" if depth.topic_coverage >= 60 else "#dc2626"
            
            st.markdown(f"""
                <div style='background: #f3f4f6; padding: 15px; border-radius: 8px;'>
                    <p><strong>Comprehensiveness:</strong> <span style='color: #3b82f6; font-weight: bold;'>{depth.comprehensiveness.title()}</span></p>
                    <p><strong>Detail Level:</strong> <span style='color: #3b82f6; font-weight: bold;'>{depth.detail_level.title()}</span></p>
                    <p><strong>Topic Coverage:</strong></p>
                    <div style='background: #e5e7eb; border-radius: 10px; height: 20px; overflow: hidden;'>
                        <div style='background: {coverage_color}; width: {depth.topic_coverage}%; height: 100%; 
                                    display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 12px;'>
                            {depth.topic_coverage:.0f}%
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                if depth.areas_of_strength:
                    st.markdown("**✅ Strengths:**")
                    for strength in depth.areas_of_strength[:3]:
                        st.markdown(f"• {strength}")
            
            with col_b:
                if depth.areas_needing_expansion:
                    st.markdown("**📈 Expand:**")
                    for area in depth.areas_needing_expansion[:3]:
                        st.markdown(f"• {area}")
    
    st.markdown("---")
    
    # Opportunities & Threats - Side by Side with Better Design
    st.markdown("### ✨ SWOT Analysis Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        if competitive.opportunities:
            st.markdown("""
                <div style='background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); 
                            padding: 20px; border-radius: 10px; min-height: 200px;'>
                    <h4 style='color: #065f46; margin-top: 0;'>✨ Opportunities to Seize</h4>
                </div>
            """, unsafe_allow_html=True)
            for i, opp in enumerate(competitive.opportunities, 1):
                st.markdown(f"**{i}.** {opp}")
        else:
            st.markdown("""
                <div style='background: #f3f4f6; padding: 20px; border-radius: 10px; min-height: 200px;'>
                    <h4 style='color: #6b7280; margin-top: 0;'>✨ Opportunities</h4>
                    <p>No specific opportunities identified</p>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if competitive.threats:
            st.markdown("""
                <div style='background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); 
                            padding: 20px; border-radius: 10px; min-height: 200px;'>
                    <h4 style='color: #991b1b; margin-top: 0;'>⚠️ Threats to Monitor</h4>
                </div>
            """, unsafe_allow_html=True)
            for i, threat in enumerate(competitive.threats, 1):
                st.markdown(f"**{i}.** {threat}")
        else:
            st.markdown("""
                <div style='background: #f3f4f6; padding: 20px; border-radius: 10px; min-height: 200px;'>
                    <h4 style='color: #6b7280; margin-top: 0;'>⚠️ Threats</h4>
                    <p>No significant threats identified</p>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Strategic Recommendations
    if competitive.recommendations:
        st.markdown("### 💡 Strategic Action Plan")
        st.markdown("*Prioritized recommendations to improve competitive position*")
        
        for i, rec in enumerate(competitive.recommendations, 1):
            priority_badge = "🔴 CRITICAL" if i <= 2 else "🟡 HIGH" if i <= 4 else "🟢 MEDIUM"
            st.markdown(f"""
                <div style='background: #f9fafb; padding: 12px; border-radius: 6px; 
                            margin-bottom: 8px; border-left: 3px solid #3b82f6;'>
                    <p style='margin: 0;'><strong>{i}.</strong> {rec} <span style='float: right; font-size: 0.85em;'>{priority_badge}</span></p>
                </div>
            """, unsafe_allow_html=True)


def render_recommendations_tab(analysis):
    """Render recommendations tab"""
    all_recommendations = []
    
    # Collect from all sources
    if analysis.seo and analysis.seo.recommendations:
        all_recommendations.extend([
            {'source': 'SEO', 'priority': 'high', 'text': rec}
            for rec in analysis.seo.recommendations
        ])
    
    if analysis.readability and analysis.readability.improvements:
        all_recommendations.extend([
            {'source': 'Readability', 'priority': getattr(rec, 'priority', 'medium'), 'text': getattr(rec, 'suggestion', str(rec))}
            for rec in analysis.readability.improvements
        ])
    
    if analysis.competitive and analysis.competitive.recommendations:
        all_recommendations.extend([
            {'source': 'Competitive', 'priority': 'high', 'text': rec}
            for rec in analysis.competitive.recommendations
        ])
    
    if not all_recommendations:
        st.info("No recommendations available")
        return
    
    # Display by priority
    st.markdown("### 🎯 Priority Actions")
    
    for rec in all_recommendations:
        priority = rec.get('priority', 'medium')
        color = "red" if priority == 'high' else "orange" if priority == 'medium' else "blue"
        
        st.markdown(f"""
        <div class="metric-card">
            <strong style="color: {color};">[{priority.upper()}]</strong> 
            <strong>{rec.get('source')}</strong>: {rec.get('text')}
        </div>
        """, unsafe_allow_html=True)


async def generate_html_report(result: Dict[str, Any], theme: str) -> bytes:
    """Generate HTML report"""
    if not result.get('success'):
        return None
    
    theme_map = {
        'professional': ReportTheme.PROFESSIONAL,
        'modern': ReportTheme.MODERN,
        'minimal': ReportTheme.MINIMAL,
        'colorful': ReportTheme.COLORFUL
    }
    
    config = ReportConfig(
        format=ReportFormat.HTML,
        theme=theme_map.get(theme.lower(), ReportTheme.PROFESSIONAL),
        include_charts=True,
        include_recommendations=True,
        company_name="Content Analysis Platform"
    )
    
    generator = ReportGenerator(config)
    report = await generator.generate_report(
        analysis_result=result.get('analysis'),
        title=result.get('title', 'Content Analysis'),
        url=result.get('url')
    )
    
    return report.content.encode('utf-8')


def render_history_tab():
    """Render analysis history tab"""
    st.markdown("### 📚 Analysis History")
    
    if not st.session_state.analysis_history:
        st.info("No analysis history yet. Start analyzing URLs to build your history!")
        return
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_status = st.selectbox("Status", ["All", "Success", "Failed"])
    
    with col2:
        filter_days = st.selectbox("Time Period", ["All Time", "Last 24h", "Last 7d", "Last 30d"])
    
    with col3:
        if st.button("🗑️ Clear History"):
            st.session_state.analysis_history = []
            st.rerun()
    
    # Filter history
    filtered_history = st.session_state.analysis_history.copy()
    
    if filter_status != "All":
        success_filter = filter_status == "Success"
        filtered_history = [h for h in filtered_history if h.get('success') == success_filter]
    
    if filter_days != "All Time":
        days_map = {"Last 24h": 1, "Last 7d": 7, "Last 30d": 30}
        days = days_map.get(filter_days, 365)
        cutoff = datetime.now() - timedelta(days=days)
        filtered_history = [
            h for h in filtered_history
            if datetime.fromisoformat(h.get('timestamp', '')) > cutoff
        ]
    
    # Display history
    st.markdown(f"**Showing {len(filtered_history)} of {len(st.session_state.analysis_history)} analyses**")
    
    for idx, item in enumerate(filtered_history[:20]):  # Show last 20
        with st.container():
            st.markdown(f"""
            <div class="history-item">
                <strong>{item.get('title', 'Untitled')}</strong><br>
                <small>{item.get('url', '')}</small><br>
                <small>📅 {item.get('timestamp', '')[:16]}</small>
                {'<span style="color: green;">✅ Success</span>' if item.get('success') else '<span style="color: red;">❌ Failed</span>'}
            </div>
            """, unsafe_allow_html=True)
            
            if item.get('success') and st.button(f"View #{idx}", key=f"view_{idx}"):
                st.session_state.current_analysis = item
                st.rerun()


def main():
    """Main application"""
    init_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">📊 Content Analysis Platform</h1>', unsafe_allow_html=True)
    st.markdown("**Professional web content analysis powered by AI**")
    
    # Sidebar configuration
    config = render_sidebar()
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs([
        "🔍 Single Analysis",
        "📋 Batch Processing",
        "📚 History"
    ])
    
    with tab1:
        render_single_analysis_tab(config)
    
    with tab2:
        render_batch_analysis_tab(config)
    
    with tab3:
        render_history_tab()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #666;">
            <small>Content Analysis Platform v1.0 | Built with Streamlit | 
            Powered by OpenAI & Anthropic</small>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
