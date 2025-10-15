"""
Results Display Component - Display analysis results
"""
import streamlit as st
from typing import Dict, Any
import json


def render_results_display(results: Dict[str, Any]):
    """
    Render analysis results
    
    Args:
        results: Analysis results dictionary
    """
    if not results:
        st.info("👆 Enter a URL above to start analyzing")
        return
    
    # Header
    st.success("✅ Analysis Complete!")
    
    # Metadata Section
    st.subheader("📄 Page Information")
    metadata = results.get('metadata', {})
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Title", metadata.get('title', 'N/A'))
    with col2:
        st.metric("Processing Time", f"{results.get('processing_time', 0):.2f}s")
    
    if metadata.get('description'):
        st.write("**Description:**", metadata.get('description'))
    
    # Content Summary Section
    st.subheader("📊 Content Analysis")
    summary = results.get('content_summary', {})
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Word Count", summary.get('word_count', 0))
    with col2:
        st.metric("Sentences", summary.get('sentence_count', 0))
    with col3:
        st.metric("Paragraphs", summary.get('paragraph_count', 0))
    with col4:
        st.metric("Reading Time", f"{summary.get('reading_time', 0)} min")
    
    # AI Analysis Section
    if results.get('analysis'):
        st.subheader("🤖 AI-Powered Analysis")
        analysis = results['analysis']
        
        # Summary
        if analysis.get('summary'):
            st.write("**Summary:**")
            st.info(analysis['summary'])
        
        # Key Points
        if analysis.get('key_points'):
            st.write("**Key Points:**")
            for idx, point in enumerate(analysis['key_points'], 1):
                st.write(f"{idx}. {point}")
        
        # Sentiment & Topics
        col1, col2 = st.columns(2)
        with col1:
            sentiment = analysis.get('sentiment', 'unknown')
            sentiment_emoji = {
                'positive': '😊',
                'negative': '😞',
                'neutral': '😐'
            }.get(sentiment.lower(), '🤔')
            st.metric("Sentiment", f"{sentiment_emoji} {sentiment.capitalize()}")
        
        with col2:
            st.write("**Topics:**")
            topics = analysis.get('topics', [])
            if topics:
                st.write(", ".join(topics))
            else:
                st.write("None detected")
    
    # Detailed Report Section
    st.subheader("📋 Detailed Report")
    report = results.get('report', {})
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Content Analysis", "Structure", "Raw Data"])
    
    with tab1:
        if report.get('content_analysis'):
            content_analysis = report['content_analysis']
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Readability Score", 
                         f"{content_analysis.get('readability_score', 0):.1f}/100")
                st.write("**Keywords:**")
                keywords = content_analysis.get('keywords', [])
                if keywords:
                    st.write(", ".join(keywords[:10]))
            
            with col2:
                st.metric("Avg Word Length", 
                         f"{content_analysis.get('avg_word_length', 0):.1f}")
                st.metric("Avg Sentence Length", 
                         f"{content_analysis.get('avg_sentence_length', 0):.1f}")
    
    with tab2:
        if report.get('structure_analysis'):
            structure = report['structure_analysis']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Links", structure.get('links_count', 0))
            with col2:
                st.metric("Images", structure.get('images_count', 0))
            with col3:
                has_forms = "✅ Yes" if structure.get('has_forms') else "❌ No"
                st.metric("Has Forms", has_forms)
            
            # Headings
            headings = structure.get('headings', [])
            if headings:
                st.write("**Page Headings:**")
                for heading in headings[:10]:
                    level = heading.get('level', 1)
                    text = heading.get('text', '')
                    st.write(f"{'  ' * (level-1)}H{level}: {text}")
    
    with tab3:
        st.json(results, expanded=False)


def render_error_display(error: str):
    """
    Render error message
    
    Args:
        error: Error message
    """
    st.error(f"❌ Analysis Failed: {error}")
    
    with st.expander("Troubleshooting Tips"):
        st.write("""
        - Ensure the URL is valid and accessible
        - Check if the website allows scraping (robots.txt)
        - Verify your internet connection
        - Try a different URL
        - Check if the website requires authentication
        """)
