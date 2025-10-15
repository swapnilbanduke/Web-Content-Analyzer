"""
Quick SEO Test - Run from backend/src directory
Tests if SEO analysis is properly configured
"""
import sys
import os

# Check imports
print("Testing imports...")
try:
    from models.data_models import Metadata
    print("✅ Metadata model imported")
    
    from ai.seo_analyzer import SEOAnalyzer, SEOAnalysisResult, SEOScore
    print("✅ SEO Analyzer imported")
    
    from ai.ai_analysis_service import AIAnalysisConfig
    print("✅ AIAnalysisConfig imported")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test Metadata with keywords as string (simulate the bug)
print("\nTesting Metadata with keywords conversion...")
try:
    # Test 1: Keywords as comma-separated string (old way - should fail)
    try:
        metadata1 = Metadata(
            title="Test",
            keywords="keyword1,keyword2,keyword3"  # String
        )
        print("❌ Metadata accepted string keywords (bug not fixed)")
    except Exception as e:
        print(f"✅ Metadata correctly rejects string keywords: {type(e).__name__}")
    
    # Test 2: Keywords as list (correct way)
    metadata2 = Metadata(
        title="Test",
        keywords=["keyword1", "keyword2", "keyword3"]  # List
    )
    print(f"✅ Metadata accepts list keywords: {metadata2.keywords}")
    
    # Test 3: Keywords as empty list (default)
    metadata3 = Metadata(title="Test")
    print(f"✅ Metadata defaults to empty list: {metadata3.keywords}")
    
except Exception as e:
    print(f"❌ Metadata test error: {e}")
    import traceback
    traceback.print_exc()

# Test SEO configuration
print("\nTesting SEO Analysis Configuration...")
try:
    config = AIAnalysisConfig(
        summarize=True,
        analyze_sentiment=True,
        extract_topics=True,
        analyze_seo=True,  # This should enable SEO
        score_readability=True,
        analyze_competitive=False
    )
    print(f"✅ AIAnalysisConfig created with analyze_seo={config.analyze_seo}")
    
except Exception as e:
    print(f"❌ Config error: {e}")

# Test SEO data structures
print("\nTesting SEO Data Structures...")
try:
    # Test SEOScore
    from ai.seo_analyzer import SEOScore
    score = SEOScore(
        overall_score=85.5,
        content_score=90.0,
        technical_score=80.0,
        keyword_score=85.0,
        metadata_score=88.0,
        structure_score=82.0,
        link_score=78.0
    )
    print(f"✅ SEOScore created: overall={score.overall_score}")
    
    # Verify nested access pattern
    print(f"   - Content score: {score.content_score}")
    print(f"   - Technical score: {score.technical_score}")
    print(f"   - Keyword score: {score.keyword_score}")
    
except Exception as e:
    print(f"❌ SEO structure error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("SEO CONFIGURATION TEST COMPLETE")
print("="*80)
print("\nNext steps:")
print("1. Open http://localhost:8537 in your browser")
print("2. Expand '📊 Analysis Options' in sidebar")
print("3. Ensure 'SEO Analysis' checkbox is ✅ CHECKED")
print("4. Enter URL: https://blog.reedsy.com/short-stories/")
print("5. Click '🚀 Analyze'")
print("6. Navigate to '🔍 SEO' tab")
