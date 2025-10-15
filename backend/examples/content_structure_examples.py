"""
Content Structure Analyzer - Usage Examples

Demonstrates how to use the content structure analysis components.
"""

import sys
from pathlib import Path
import json

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from src.analyzers.content_structure_analyzer import ContentStructureAnalyzer


def example_1_basic_html_analysis():
    """Example 1: Basic HTML document analysis"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic HTML Document Analysis")
    print("="*70)
    
    analyzer = ContentStructureAnalyzer()
    
    html = """
    <html>
        <body>
            <h1>Complete Guide to Machine Learning</h1>
            
            <h2>Introduction</h2>
            <p>Machine learning is transforming technology across industries.</p>
            
            <h2>Core Concepts</h2>
            <p>Understanding algorithms and data preprocessing is crucial.</p>
            
            <h3>Supervised Learning</h3>
            <p>Classification and regression are key techniques.</p>
            
            <h3>Unsupervised Learning</h3>
            <p>Clustering and dimensionality reduction methods.</p>
            
            <h2>Conclusion</h2>
            <p>Machine learning continues to evolve rapidly.</p>
        </body>
    </html>
    """
    
    result = analyzer.analyze(html)
    
    print(f"\n📊 DOCUMENT STRUCTURE:")
    print(f"  Title: {result['outline']['title']}")
    print(f"  Total Headings: {result['outline']['total_headings']}")
    print(f"  Hierarchy Depth: {result['outline']['hierarchy_depth']}")
    
    print(f"\n📑 HEADING DISTRIBUTION:")
    for level, count in result['outline']['heading_distribution'].items():
        if count > 0:
            print(f"  H{level}: {count} heading(s)")
    
    print(f"\n📄 SECTIONS:")
    for i, section in enumerate(result['outline']['sections'], 1):
        heading_text = section['heading']['text'] if section['heading'] else 'No heading'
        print(f"  {i}. {heading_text} ({section['type']}) - {section['word_count']} words")
    
    print(f"\n🔑 TOP KEY PHRASES:")
    for i, phrase in enumerate(result['key_phrases'][:5], 1):
        print(f"  {i}. '{phrase['phrase']}' ({phrase['type']}) - score: {phrase['score']:.2f}")


def example_2_blog_post_analysis():
    """Example 2: Blog post structure analysis"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Blog Post Analysis")
    print("="*70)
    
    analyzer = ContentStructureAnalyzer(
        extract_key_phrases=True,
        classify_content_type=True
    )
    
    html = """
    <article>
        <h1>The Future of Artificial Intelligence</h1>
        <div class="meta">
            <time datetime="2024-01-15">Posted on January 15, 2024</time>
            <span class="author">by Dr. Sarah Johnson</span>
        </div>
        
        <h2>Introduction</h2>
        <p>
            Artificial intelligence and machine learning are revolutionizing 
            how we interact with technology. Deep learning neural networks 
            enable unprecedented capabilities.
        </p>
        
        <h2>Current Trends</h2>
        <p>
            Natural language processing has made significant advances. 
            Computer vision applications continue to expand across industries.
        </p>
        
        <h3>Enterprise Applications</h3>
        <p>
            Businesses are adopting AI for automation, analytics, and 
            customer experience enhancement.
        </p>
        
        <h3>Research Developments</h3>
        <p>
            Academic institutions are pushing boundaries in reinforcement 
            learning and generative models.
        </p>
        
        <h2>Conclusion</h2>
        <p>
            The future of artificial intelligence holds immense potential 
            for transforming society and industry.
        </p>
    </article>
    """
    
    result = analyzer.analyze(html)
    
    print(f"\n🎯 CONTENT TYPE:")
    print(f"  Primary: {result['content_type']['primary_type']}")
    print(f"  Confidence: {result['content_type']['confidence']:.2%}")
    if result['content_type']['secondary_types']:
        print(f"  Secondary: {', '.join(result['content_type']['secondary_types'])}")
    
    print(f"\n📖 DOCUMENT OUTLINE:")
    toc = analyzer.generate_table_of_contents(result['outline'])
    print(toc)
    
    print(f"\n🔑 KEY PHRASES (Top 10):")
    for i, phrase in enumerate(result['key_phrases'][:10], 1):
        print(f"  {i:2}. '{phrase['phrase']}' "
              f"(freq: {phrase['frequency']}, score: {phrase['score']:.1f})")
    
    print(f"\n📊 METADATA:")
    for key, value in result['metadata'].items():
        print(f"  {key}: {value}")


def example_3_technical_documentation():
    """Example 3: Technical documentation analysis"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Technical Documentation Analysis")
    print("="*70)
    
    analyzer = ContentStructureAnalyzer()
    
    html = """
    <div class="documentation">
        <h1>API Reference Guide</h1>
        
        <h2>Installation</h2>
        <pre><code>pip install mypackage</code></pre>
        <p>Install the package using pip or conda.</p>
        
        <h2>Quick Start</h2>
        <p>Import the main class and initialize:</p>
        <code>from mypackage import MainClass</code>
        
        <h2>API Methods</h2>
        <p>Core functionality and method signatures.</p>
        
        <h3>getData()</h3>
        <p>Retrieve data from the API endpoint.</p>
        <p>Parameters: url, headers, timeout</p>
        
        <h3>processData()</h3>
        <p>Process and transform the retrieved data.</p>
        <p>Returns: Processed data object</p>
        
        <h2>Examples</h2>
        <p>See usage examples in the examples directory.</p>
    </div>
    """
    
    result = analyzer.analyze(html)
    
    print(f"\n📚 DOCUMENTATION STRUCTURE:")
    print(f"  Title: {result['outline']['title']}")
    print(f"  Sections: {result['metadata']['total_sections']}")
    print(f"  Content Type: {result['content_type']['primary_type']}")
    
    print(f"\n🌲 HEADING HIERARCHY:")
    for heading in result['outline']['headings']:
        if heading['level'] <= 2:  # Show top-level headings
            indent = "  " * (heading['level'] - 1)
            print(f"{indent}{'▸' if heading['level'] == 2 else '●'} {heading['text']}")
    
    print(f"\n📝 SECTION BREAKDOWN:")
    for section in result['outline']['sections']:
        if section['heading']:
            print(f"\n  Section: {section['heading']['text']}")
            print(f"    Type: {section['type']}")
            print(f"    Words: {section['word_count']}")
            print(f"    Subsections: {len(section['subsections'])}")


def example_4_markdown_analysis():
    """Example 4: Markdown document analysis"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Markdown Document Analysis")
    print("="*70)
    
    analyzer = ContentStructureAnalyzer()
    
    markdown = """
# Project README

## Overview
This project implements a machine learning pipeline for data analysis.

## Features
- Data preprocessing and cleaning
- Model training and evaluation
- Result visualization

### Data Processing
Handles various data formats including CSV, JSON, and SQL databases.

### Model Training
Supports multiple algorithms:
- Random Forest
- Gradient Boosting
- Neural Networks

## Installation
Install dependencies using pip:
```bash
pip install -r requirements.txt
```

## Usage
Run the main script with your data file:
```bash
python main.py --data data.csv
```

## Contributing
Contributions are welcome! Please read CONTRIBUTING.md first.

## License
MIT License - see LICENSE file for details.
    """
    
    result = analyzer.analyze(markdown, content_format='markdown')
    
    print(f"\n📄 MARKDOWN STRUCTURE:")
    print(f"  Format: {result['format']}")
    print(f"  Title: {result['outline']['title']}")
    print(f"  Total Headings: {result['outline']['total_headings']}")
    
    print(f"\n📑 SECTION TYPES:")
    section_types = {}
    for section in result['outline']['sections']:
        section_type = section['type']
        section_types[section_type] = section_types.get(section_type, 0) + 1
    
    for section_type, count in section_types.items():
        print(f"  {section_type}: {count}")
    
    print(f"\n🔍 KEY TOPICS:")
    for i, phrase in enumerate(result['key_phrases'][:8], 1):
        if phrase['type'] in ['bigram', 'trigram']:
            print(f"  • {phrase['phrase']}")


def example_5_academic_paper_structure():
    """Example 5: Academic paper structure analysis"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Academic Paper Structure Analysis")
    print("="*70)
    
    analyzer = ContentStructureAnalyzer()
    
    html = """
    <article class="paper">
        <h1>Deep Learning for Natural Language Understanding</h1>
        
        <section id="abstract">
            <h2>Abstract</h2>
            <p>
                This paper presents a novel approach to natural language 
                understanding using transformer-based architectures. We 
                demonstrate significant improvements over baseline methods.
            </p>
        </section>
        
        <section id="introduction">
            <h2>Introduction</h2>
            <p>
                Natural language processing has seen remarkable progress 
                with the advent of deep learning models (Smith et al., 2023).
            </p>
        </section>
        
        <section id="methodology">
            <h2>Methodology</h2>
            <p>
                Our approach combines attention mechanisms with hierarchical 
                encoding to capture semantic relationships.
            </p>
            
            <h3>Model Architecture</h3>
            <p>The model consists of encoder and decoder components.</p>
            
            <h3>Training Procedure</h3>
            <p>We train using Adam optimizer with learning rate scheduling.</p>
        </section>
        
        <section id="results">
            <h2>Results</h2>
            <p>
                Our model achieves state-of-the-art performance on benchmark 
                datasets with 94.5% accuracy.
            </p>
        </section>
        
        <section id="discussion">
            <h2>Discussion</h2>
            <p>
                The results demonstrate the effectiveness of our approach 
                for semantic understanding tasks.
            </p>
        </section>
        
        <section id="conclusion">
            <h2>Conclusion</h2>
            <p>
                We have presented a novel architecture that advances the 
                state of natural language understanding.
            </p>
        </section>
        
        <section id="references">
            <h2>References</h2>
            <p>[1] Smith, J. et al. (2023). Deep Learning Methods...</p>
        </section>
    </article>
    """
    
    result = analyzer.analyze(html)
    
    print(f"\n📄 PAPER STRUCTURE:")
    print(f"  Title: {result['outline']['title']}")
    print(f"  Content Type: {result['content_type']['primary_type']}")
    
    print(f"\n📚 STANDARD SECTIONS DETECTED:")
    expected_sections = ['abstract', 'introduction', 'methodology', 'results', 
                        'discussion', 'conclusion', 'references']
    detected_sections = [s['type'] for s in result['outline']['sections']]
    
    for expected in expected_sections:
        status = "✓" if expected in detected_sections else "✗"
        print(f"  {status} {expected.capitalize()}")
    
    print(f"\n🏗️ HIERARCHY:")
    for heading in result['outline']['headings']:
        indent = "  " * (heading['level'] - 1)
        marker = "▸" if heading['level'] > 1 else "●"
        print(f"{indent}{marker} {heading['text']}")
    
    print(f"\n🔬 RESEARCH KEYWORDS:")
    research_phrases = [p for p in result['key_phrases'] 
                       if p['type'] in ['bigram', 'trigram']][:5]
    for phrase in research_phrases:
        print(f"  • {phrase['phrase']}")


def example_6_content_type_comparison():
    """Example 6: Comparing different content types"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Content Type Comparison")
    print("="*70)
    
    analyzer = ContentStructureAnalyzer(classify_content_type=True)
    
    samples = {
        'Blog Post': """
            <article>
                <time>2024-01-01</time>
                <h1>My Travel Adventures</h1>
                <p>Posted by John Doe</p>
                <p>This weekend I visited amazing places...</p>
            </article>
        """,
        'Product Page': """
            <div class="product">
                <h1>Premium Laptop</h1>
                <div class="price">$1,299.99</div>
                <button>Add to Cart</button>
                <p>Buy now and get free shipping!</p>
            </div>
        """,
        'News Article': """
            <article>
                <h1>Breaking: Major Discovery Announced</h1>
                <p>UPDATED: Scientists reported today...</p>
                <div class="byline">By Staff Reporter</div>
            </article>
        """,
        'Technical Docs': """
            <div>
                <h1>API Documentation</h1>
                <code>function getData(params)</code>
                <p>This method accepts parameters and returns data.</p>
            </div>
        """
    }
    
    print(f"\n📊 CONTENT TYPE DETECTION RESULTS:\n")
    print(f"{'Content':<20} {'Detected Type':<20} {'Confidence':<12} {'Score'}")
    print("-" * 70)
    
    for name, html in samples.items():
        result = analyzer.analyze(html)
        ct = result['content_type']
        score = ct['scores'].get(ct['primary_type'], 0)
        
        print(f"{name:<20} {ct['primary_type']:<20} {ct['confidence']:>10.1%} {score:>10.1f}")


def example_7_hierarchy_visualization():
    """Example 7: Visualizing document hierarchy"""
    print("\n" + "="*70)
    print("EXAMPLE 7: Document Hierarchy Visualization")
    print("="*70)
    
    analyzer = ContentStructureAnalyzer()
    
    html = """
    <h1>Software Engineering Handbook</h1>
    <h2>Part 1: Fundamentals</h2>
    <h3>Chapter 1: Programming Basics</h3>
    <h4>Variables and Data Types</h4>
    <h4>Control Structures</h4>
    <h3>Chapter 2: Object-Oriented Programming</h3>
    <h4>Classes and Objects</h4>
    <h4>Inheritance</h4>
    <h4>Polymorphism</h4>
    <h2>Part 2: Advanced Topics</h2>
    <h3>Chapter 3: Design Patterns</h3>
    <h4>Creational Patterns</h4>
    <h4>Structural Patterns</h4>
    <h3>Chapter 4: Testing</h3>
    <h4>Unit Testing</h4>
    <h4>Integration Testing</h4>
    """
    
    result = analyzer.analyze(html)
    
    print(f"\n🌲 DOCUMENT HIERARCHY TREE:\n")
    
    def print_tree(headings, level=0):
        for heading in headings:
            indent = "│   " * level
            connector = "├── " if level > 0 else ""
            print(f"{indent}{connector}H{heading['level']}: {heading['text']}")
            if heading.get('children'):
                print_tree(heading['children'], level + 1)
    
    # Get root headings
    root_headings = [h for h in result['outline']['headings'] 
                    if h['level'] == 1]
    print_tree(root_headings)
    
    print(f"\n📊 HIERARCHY STATISTICS:")
    print(f"  Maximum Depth: {result['outline']['hierarchy_depth']}")
    print(f"  Total Headings: {result['outline']['total_headings']}")
    print(f"\n  Distribution by Level:")
    for level, count in sorted(result['outline']['heading_distribution'].items()):
        if count > 0:
            bar = "█" * count
            print(f"    H{level}: {bar} ({count})")


def example_8_complete_analysis_report():
    """Example 8: Generate complete analysis report"""
    print("\n" + "="*70)
    print("EXAMPLE 8: Complete Analysis Report")
    print("="*70)
    
    analyzer = ContentStructureAnalyzer(
        extract_key_phrases=True,
        max_key_phrases=15,
        classify_content_type=True
    )
    
    html = """
    <article>
        <h1>Building Scalable Web Applications</h1>
        
        <h2>Introduction</h2>
        <p>
            Modern web applications require careful architectural planning.
            Microservices architecture has become increasingly popular for
            building scalable, maintainable systems.
        </p>
        
        <h2>Architecture Patterns</h2>
        <p>
            Several architecture patterns enable scalability including
            microservices, serverless, and event-driven architectures.
        </p>
        
        <h3>Microservices</h3>
        <p>
            Breaking applications into small, independent services improves
            scalability and maintainability. Docker containers facilitate
            microservice deployment.
        </p>
        
        <h3>Serverless Computing</h3>
        <p>
            Cloud providers offer serverless platforms that automatically
            scale based on demand. AWS Lambda and Azure Functions are
            popular choices.
        </p>
        
        <h2>Database Strategies</h2>
        <p>
            Choosing the right database is crucial. NoSQL databases like
            MongoDB offer flexibility, while PostgreSQL provides robust
            relational features.
        </p>
        
        <h3>SQL vs NoSQL</h3>
        <p>
            Understanding the tradeoffs between SQL and NoSQL databases
            helps make informed architectural decisions.
        </p>
        
        <h2>Conclusion</h2>
        <p>
            Building scalable applications requires understanding architecture
            patterns, database choices, and deployment strategies.
        </p>
    </article>
    """
    
    result = analyzer.analyze(html)
    
    print(f"\n" + "="*70)
    print("COMPREHENSIVE STRUCTURE ANALYSIS REPORT")
    print("="*70)
    
    print(f"\n1. DOCUMENT OVERVIEW")
    print(f"   ├─ Title: {result['outline']['title']}")
    print(f"   ├─ Content Type: {result['content_type']['primary_type'].replace('_', ' ').title()}")
    print(f"   ├─ Confidence: {result['content_type']['confidence']:.1%}")
    print(f"   └─ Format: {result['format'].upper()}")
    
    print(f"\n2. STRUCTURAL METRICS")
    print(f"   ├─ Total Headings: {result['metadata']['total_headings']}")
    print(f"   ├─ Total Sections: {result['metadata']['total_sections']}")
    print(f"   ├─ Hierarchy Depth: {result['outline']['hierarchy_depth']}")
    print(f"   ├─ Avg Section Length: {result['metadata']['avg_section_length']:.0f} words")
    print(f"   └─ Clear Structure: {'Yes' if result['metadata']['has_clear_structure'] else 'No'}")
    
    print(f"\n3. HEADING DISTRIBUTION")
    for level in range(1, 7):
        count = result['outline']['heading_distribution'][level]
        if count > 0:
            print(f"   ├─ H{level}: {count} {'heading' if count == 1 else 'headings'}")
    
    print(f"\n4. DOCUMENT OUTLINE")
    toc = analyzer.generate_table_of_contents(result['outline'])
    for line in toc.split('\n')[2:]:  # Skip title
        if line.strip():
            print(f"   {line}")
    
    print(f"\n5. KEY TOPICS & PHRASES")
    print(f"   Top {min(10, len(result['key_phrases']))} phrases:")
    for i, phrase in enumerate(result['key_phrases'][:10], 1):
        print(f"   {i:2}. {phrase['phrase']:<30} "
              f"[{phrase['type']:<7}] score: {phrase['score']:>5.1f}")
    
    print(f"\n6. SECTION ANALYSIS")
    for i, section in enumerate(result['outline']['sections'][:5], 1):
        heading_text = section['heading']['text'] if section['heading'] else 'Untitled'
        print(f"   Section {i}: {heading_text}")
        print(f"   ├─ Type: {section['type']}")
        print(f"   ├─ Words: {section['word_count']}")
        print(f"   └─ Subsections: {len(section['subsections'])}")
        if i < len(result['outline']['sections'][:5]):
            print(f"   │")
    
    print(f"\n" + "="*70)
    print("END OF REPORT")
    print("="*70)


def run_all_examples():
    """Run all examples"""
    print("\n" + "="*70)
    print("CONTENT STRUCTURE ANALYZER - USAGE EXAMPLES")
    print("="*70)
    
    examples = [
        example_1_basic_html_analysis,
        example_2_blog_post_analysis,
        example_3_technical_documentation,
        example_4_markdown_analysis,
        example_5_academic_paper_structure,
        example_6_content_type_comparison,
        example_7_hierarchy_visualization,
        example_8_complete_analysis_report
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\nError in {example.__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("ALL EXAMPLES COMPLETED")
    print("="*70 + "\n")


if __name__ == "__main__":
    run_all_examples()
