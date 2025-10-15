"""
Text Processing Pipeline - Usage Examples

This file contains practical examples of using the text processing pipeline.
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from src.processors.text_processor import TextProcessor


def example_1_basic_html_processing():
    """Example 1: Basic HTML content processing"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic HTML Processing")
    print("="*70)
    
    processor = TextProcessor()
    
    html = """
    <html>
        <head>
            <title>Sample Article</title>
            <script>alert('This will be removed');</script>
            <style>.class { color: red; }</style>
        </head>
        <body>
            <h1>Welcome to Text Processing</h1>
            <p>This is the first paragraph with some <strong>important</strong> information.</p>
            <p>This is the second paragraph with a <a href="http://example.com">link</a>.</p>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
                <li>Item 3</li>
            </ul>
        </body>
    </html>
    """
    
    result = processor.process(html, is_html=True)
    
    print(f"\nOriginal length: {result['original_length']} chars")
    print(f"Processed length: {result['processed_length']} chars")
    print(f"\nProcessed text:\n{result['processed_text'][:200]}...")
    print(f"\nStatistics:")
    print(f"  - Words: {result['word_count']}")
    print(f"  - Sentences: {result['sentence_count']}")
    print(f"  - Paragraphs: {result['paragraph_count']}")
    print(f"  - Reading time: {result['reading_time']:.1f} minutes")
    print(f"  - Language: {result['language']['language']} (confidence: {result['language']['confidence']:.2f})")


def example_2_multilingual_detection():
    """Example 2: Language detection across multiple languages"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Multilingual Language Detection")
    print("="*70)
    
    processor = TextProcessor(detect_language=True)
    
    samples = {
        'English': "The quick brown fox jumps over the lazy dog. This is a sample text in English.",
        'Spanish': "El rápido zorro marrón salta sobre el perro perezoso. Este es un texto de muestra en español.",
        'French': "Le renard brun rapide saute par-dessus le chien paresseux. C'est un exemple de texte en français.",
        'German': "Der schnelle braune Fuchs springt über den faulen Hund. Dies ist ein Beispieltext auf Deutsch.",
        'Italian': "La volpe marrone veloce salta sopra il cane pigro. Questo è un testo di esempio in italiano.",
        'Portuguese': "A rápida raposa marrom pula sobre o cachorro preguiçoso. Este é um texto de amostra em português."
    }
    
    print("\nLanguage Detection Results:")
    print("-" * 70)
    
    for language, text in samples.items():
        result = processor.process(text, is_html=False)
        detected = result['language']['language'].upper()
        confidence = result['language']['confidence']
        print(f"{language:12} -> Detected: {detected:2} | Confidence: {confidence:.2f}")


def example_3_text_normalization():
    """Example 3: Text normalization and cleaning"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Text Normalization")
    print("="*70)
    
    processor = TextProcessor(
        clean_html=False,
        normalize_text=True,
        handle_special_chars=True
    )
    
    messy_text = """
    Hello    World!    This  has    excessive    whitespace.
    
    
    
    Too   many   newlines   above.
    
    "Smart quotes" and 'single quotes' everywhere.
    Em—dash and en–dash mixed in.
    
    Emails like test@example.com should be handled.
    URLs like https://example.com too.
    
    Some emojis: 😀 🎉 ✨
    """
    
    result = processor.process(messy_text, is_html=False)
    
    print("\nOriginal text:")
    print(messy_text[:200])
    print("\nNormalized text:")
    print(result['processed_text'][:200])
    print(f"\nSteps applied: {', '.join(result['steps_applied'])}")


def example_4_summarization_prep():
    """Example 4: Content preparation for summarization"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Summarization Preparation")
    print("="*70)
    
    processor = TextProcessor(prepare_summary=True)
    
    article = """
    Artificial Intelligence is transforming the modern world. 
    Machine learning algorithms can now process vast amounts of data in seconds.
    This technology has applications in healthcare, finance, and transportation.
    
    Deep learning, a subset of machine learning, uses neural networks with multiple layers.
    These networks can recognize patterns in data that humans might miss.
    The potential benefits are enormous, but there are also risks to consider.
    
    Privacy concerns are one major issue with AI systems.
    Bias in training data can lead to unfair outcomes.
    Transparency and accountability are crucial for responsible AI development.
    Researchers and policymakers must work together to address these challenges.
    
    The future of AI looks promising with continued innovation.
    New breakthroughs are happening every day in laboratories around the world.
    However, we must remain vigilant about the ethical implications.
    The technology we create today will shape society for generations to come.
    """
    
    result = processor.process(article, is_html=False)
    
    print(f"\nContent Statistics:")
    print(f"  - Total sentences: {len(result['summary_data']['sentences'])}")
    print(f"  - Total paragraphs: {len(result['summary_data']['paragraphs'])}")
    print(f"  - Key sentences: {len(result['summary_data']['key_sentences'])}")
    
    print(f"\nReadability Metrics:")
    metrics = result['summary_data']['metrics']
    print(f"  - Flesch Reading Ease: {metrics['flesch_reading_ease']:.1f}")
    print(f"  - Avg. sentence length: {metrics['avg_sentence_length']:.1f} words")
    print(f"  - Avg. word length: {metrics['avg_word_length']:.1f} chars")
    print(f"  - Total syllables: {metrics['total_syllables']}")
    
    print(f"\nTop 3 Key Sentences:")
    for i, sentence in enumerate(result['summary_data']['key_sentences'][:3], 1):
        print(f"\n{i}. [{sentence['score']:.3f}] {sentence['text']}")


def example_5_batch_processing():
    """Example 5: Batch processing multiple documents"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Batch Processing")
    print("="*70)
    
    processor = TextProcessor()
    
    documents = [
        "<p>First document about technology and innovation.</p>",
        "<p>Second document discussing environmental issues.</p>",
        "<p>Third document covering economic trends.</p>",
        "<p>Fourth document exploring social media impact.</p>",
        "<p>Fifth document analyzing political developments.</p>"
    ]
    
    results = processor.process_batch(documents, is_html=True)
    
    print(f"\nProcessed {len(results)} documents:")
    print("-" * 70)
    
    for i, result in enumerate(results, 1):
        print(f"\nDocument {i}:")
        print(f"  Text: {result['processed_text'][:50]}...")
        print(f"  Words: {result['word_count']}")
        print(f"  Language: {result['language']['language']}")


def example_6_custom_configuration():
    """Example 6: Custom pipeline configuration"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Custom Pipeline Configuration")
    print("="*70)
    
    # Configuration 1: Aggressive cleaning
    processor_aggressive = TextProcessor(
        clean_html=True,
        normalize_text=True,
        handle_special_chars=True,
        html_cleaner={
            'preserve_structure': False,
            'remove_links': True,
            'remove_images': True
        },
        char_handler={
            'unicode_form': 'NFKC',
            'remove_emojis': True,
            'ascii_only': True
        }
    )
    
    # Configuration 2: Minimal processing
    processor_minimal = TextProcessor(
        clean_html=True,
        normalize_text=False,
        handle_special_chars=False,
        detect_language=False,
        prepare_summary=False
    )
    
    html = "<p>Hello 😀 World! Visit <a href='http://example.com'>our site</a>.</p>"
    
    result_aggressive = processor_aggressive.process(html, is_html=True)
    result_minimal = processor_minimal.process(html, is_html=True)
    
    print("\nAggressive cleaning:")
    print(f"  Text: '{result_aggressive['processed_text']}'")
    print(f"  Steps: {result_aggressive['steps_applied']}")
    
    print("\nMinimal processing:")
    print(f"  Text: '{result_minimal['processed_text']}'")
    print(f"  Steps: {result_minimal['steps_applied']}")


def example_7_keyword_extraction():
    """Example 7: Keyword extraction"""
    print("\n" + "="*70)
    print("EXAMPLE 7: Keyword Extraction")
    print("="*70)
    
    processor = TextProcessor()
    
    article = """
    Machine learning and artificial intelligence are revolutionizing technology.
    Deep learning algorithms use neural networks to process data.
    Natural language processing enables computers to understand human language.
    Computer vision allows machines to interpret visual information.
    These technologies are transforming industries worldwide.
    Data science combines machine learning with statistical analysis.
    """
    
    result = processor.process(article, is_html=False)
    
    print("\nTop Keywords:")
    for i, (keyword, count) in enumerate(result['keywords'][:10], 1):
        print(f"{i:2}. {keyword:20} ({count} occurrences)")


def example_8_real_world_article():
    """Example 8: Processing a real-world article"""
    print("\n" + "="*70)
    print("EXAMPLE 8: Real-World Article Processing")
    print("="*70)
    
    processor = TextProcessor(
        clean_html=True,
        normalize_text=True,
        handle_special_chars=True,
        detect_language=True,
        prepare_summary=True
    )
    
    article_html = """
    <article>
        <header>
            <h1>The Future of Renewable Energy</h1>
            <p class="byline">By John Smith | Published: March 15, 2024</p>
        </header>
        
        <div class="content">
            <p>
                Renewable energy sources are becoming increasingly important in the fight 
                against climate change. Solar and wind power have seen dramatic cost 
                reductions over the past decade, making them competitive with fossil fuels.
            </p>
            
            <p>
                According to recent studies, renewable energy could supply 80% of the 
                world's electricity by 2050. This transition will require significant 
                investment in grid infrastructure and energy storage solutions.
            </p>
            
            <blockquote>
                "The shift to renewable energy is not just environmentally necessary, 
                it's economically inevitable," says Dr. Sarah Johnson, energy economist.
            </blockquote>
            
            <p>
                Battery technology improvements are crucial for storing intermittent 
                renewable energy. Lithium-ion batteries have become cheaper and more 
                efficient, but new technologies like solid-state batteries show even 
                greater promise.
            </p>
            
            <p>
                Governments worldwide are implementing policies to accelerate the 
                renewable energy transition. Carbon pricing, renewable energy targets, 
                and subsidies for clean technology are becoming more common.
            </p>
        </div>
    </article>
    """
    
    result = processor.process(article_html, is_html=True)
    
    print("\n" + "="*70)
    print("PROCESSING RESULTS")
    print("="*70)
    
    print(f"\n1. BASIC STATISTICS")
    print(f"   - Original length: {result['original_length']:,} characters")
    print(f"   - Processed length: {result['processed_length']:,} characters")
    print(f"   - Reduction: {((result['original_length'] - result['processed_length']) / result['original_length'] * 100):.1f}%")
    
    print(f"\n2. CONTENT METRICS")
    print(f"   - Words: {result['word_count']:,}")
    print(f"   - Sentences: {result['sentence_count']}")
    print(f"   - Paragraphs: {result['paragraph_count']}")
    print(f"   - Reading time: {result['reading_time']:.1f} minutes")
    
    print(f"\n3. LANGUAGE DETECTION")
    print(f"   - Language: {result['language']['language'].upper()}")
    print(f"   - Confidence: {result['language']['confidence']:.2f}")
    print(f"   - Method: {result['language']['method']}")
    
    print(f"\n4. READABILITY")
    print(f"   - Flesch Reading Ease: {result['readability_score']:.1f}")
    score = result['readability_score']
    if score >= 90:
        level = "Very Easy"
    elif score >= 80:
        level = "Easy"
    elif score >= 70:
        level = "Fairly Easy"
    elif score >= 60:
        level = "Standard"
    elif score >= 50:
        level = "Fairly Difficult"
    elif score >= 30:
        level = "Difficult"
    else:
        level = "Very Difficult"
    print(f"   - Reading Level: {level}")
    
    print(f"\n5. TOP KEYWORDS")
    for i, (keyword, count) in enumerate(result['keywords'][:5], 1):
        print(f"   {i}. {keyword} ({count})")
    
    print(f"\n6. KEY SENTENCES (Top 3)")
    for i, sentence in enumerate(result['summary_data']['key_sentences'][:3], 1):
        print(f"\n   {i}. [{sentence['score']:.3f}]")
        print(f"      {sentence['text']}")
    
    print(f"\n7. PROCESSED TEXT (First 300 chars)")
    print(f"   {result['processed_text'][:300]}...")
    
    print(f"\n8. PROCESSING PIPELINE")
    print(f"   Steps applied: {', '.join(result['steps_applied'])}")


def run_all_examples():
    """Run all examples"""
    print("\n" + "="*70)
    print("TEXT PROCESSING PIPELINE - USAGE EXAMPLES")
    print("="*70)
    
    examples = [
        example_1_basic_html_processing,
        example_2_multilingual_detection,
        example_3_text_normalization,
        example_4_summarization_prep,
        example_5_batch_processing,
        example_6_custom_configuration,
        example_7_keyword_extraction,
        example_8_real_world_article
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\nError in {example.__name__}: {e}")
    
    print("\n" + "="*70)
    print("ALL EXAMPLES COMPLETED")
    print("="*70 + "\n")


if __name__ == "__main__":
    run_all_examples()
