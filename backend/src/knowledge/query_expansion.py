"""
Query Expansion - Enhance search queries for better retrieval

Implements multiple query expansion techniques:
- Synonym expansion
- Conceptual expansion using LLM
- N-gram generation
- Spell correction
- Related terms extraction
"""

from typing import List, Dict, Set, Optional, Any
from dataclasses import dataclass
import logging
import re
from collections import Counter

logger = logging.getLogger(__name__)


@dataclass
class ExpandedQuery:
    """Expanded query with additional terms"""
    original: str
    expanded_terms: List[str]
    synonyms: List[str]
    related_concepts: List[str]
    corrected_terms: List[str]
    weights: Dict[str, float]  # Term weights for relevance
    
    def get_all_terms(self) -> List[str]:
        """Get all unique terms including original"""
        all_terms = [self.original] + self.expanded_terms + self.synonyms + self.related_concepts
        return list(set(all_terms))
    
    def get_weighted_terms(self) -> Dict[str, float]:
        """Get all terms with their weights"""
        terms = {}
        # Original query has highest weight
        for word in self.original.split():
            terms[word] = 1.0
        
        # Other terms have lower weights
        for term in self.expanded_terms:
            terms[term] = self.weights.get(term, 0.8)
        
        for term in self.synonyms:
            terms[term] = self.weights.get(term, 0.7)
        
        for term in self.related_concepts:
            terms[term] = self.weights.get(term, 0.6)
        
        return terms


class QueryExpander:
    """
    Advanced query expansion engine.
    
    Features:
    - Multi-strategy expansion (synonyms, concepts, spelling)
    - LLM-powered semantic expansion
    - Configurable expansion strategies
    - Query rewriting
    """
    
    def __init__(
        self,
        use_synonyms: bool = True,
        use_concepts: bool = True,
        use_spelling: bool = True,
        max_expansions: int = 10
    ):
        """
        Initialize query expander.
        
        Args:
            use_synonyms: Enable synonym expansion
            use_concepts: Enable conceptual expansion
            use_spelling: Enable spelling correction
            max_expansions: Maximum number of expansion terms
        """
        self.use_synonyms = use_synonyms
        self.use_concepts = use_concepts
        self.use_spelling = use_spelling
        self.max_expansions = max_expansions
        
        # Built-in synonym dictionary (can be extended)
        self.synonym_dict = self._build_synonym_dict()
        
        # Common tech/business domain expansions
        self.domain_expansions = self._build_domain_expansions()
        
        logger.info("QueryExpander initialized")
    
    def _build_synonym_dict(self) -> Dict[str, List[str]]:
        """Build a dictionary of common synonyms"""
        return {
            # Technical terms
            'ai': ['artificial intelligence', 'machine learning', 'ml', 'deep learning'],
            'ml': ['machine learning', 'ai', 'artificial intelligence'],
            'api': ['application programming interface', 'interface', 'endpoint'],
            'database': ['db', 'data store', 'datastore', 'storage'],
            'server': ['backend', 'host', 'node'],
            'client': ['frontend', 'user interface', 'ui'],
            
            # Business terms
            'revenue': ['income', 'earnings', 'sales'],
            'profit': ['earnings', 'gain', 'margin'],
            'customer': ['client', 'user', 'consumer'],
            'product': ['service', 'offering', 'solution'],
            
            # Action verbs
            'analyze': ['examine', 'study', 'evaluate', 'assess'],
            'improve': ['enhance', 'optimize', 'boost', 'upgrade'],
            'create': ['build', 'develop', 'generate', 'produce'],
            'search': ['find', 'lookup', 'query', 'retrieve'],
            
            # General terms
            'good': ['excellent', 'great', 'quality', 'positive'],
            'bad': ['poor', 'negative', 'low-quality'],
            'fast': ['quick', 'rapid', 'speedy', 'swift'],
            'slow': ['sluggish', 'delayed', 'lagging'],
        }
    
    def _build_domain_expansions(self) -> Dict[str, List[str]]:
        """Build domain-specific concept expansions"""
        return {
            'seo': ['search engine optimization', 'ranking', 'keywords', 'meta tags', 'backlinks'],
            'marketing': ['advertising', 'promotion', 'campaigns', 'branding', 'outreach'],
            'analytics': ['metrics', 'data analysis', 'statistics', 'insights', 'reporting'],
            'security': ['authentication', 'authorization', 'encryption', 'protection', 'privacy'],
            'performance': ['speed', 'optimization', 'efficiency', 'scalability', 'latency'],
            'ux': ['user experience', 'usability', 'interface', 'design', 'interaction'],
            'content': ['text', 'article', 'blog', 'documentation', 'copy'],
        }
    
    async def expand(self, query: str) -> ExpandedQuery:
        """
        Expand a search query using multiple strategies.
        
        Args:
            query: Original search query
            
        Returns:
            ExpandedQuery with additional terms
        """
        query = query.lower().strip()
        
        expanded_terms = []
        synonyms = []
        related_concepts = []
        corrected_terms = []
        weights = {}
        
        # Extract query terms
        query_terms = self._extract_terms(query)
        
        # 1. Synonym expansion
        if self.use_synonyms:
            for term in query_terms:
                if term in self.synonym_dict:
                    term_synonyms = self.synonym_dict[term][:3]  # Limit per term
                    synonyms.extend(term_synonyms)
                    for syn in term_synonyms:
                        weights[syn] = 0.7
        
        # 2. Domain concept expansion
        if self.use_concepts:
            for term in query_terms:
                if term in self.domain_expansions:
                    concepts = self.domain_expansions[term][:3]
                    related_concepts.extend(concepts)
                    for concept in concepts:
                        weights[concept] = 0.6
        
        # 3. N-gram expansion (bi-grams)
        bigrams = self._extract_ngrams(query, n=2)
        expanded_terms.extend(bigrams)
        for bg in bigrams:
            weights[bg] = 0.8
        
        # 4. Spelling correction (basic)
        if self.use_spelling:
            for term in query_terms:
                corrected = self._spell_correct(term)
                if corrected != term:
                    corrected_terms.append(corrected)
                    weights[corrected] = 0.9
        
        # 5. Word variations (plurals, tenses)
        variations = self._generate_variations(query_terms)
        expanded_terms.extend(variations)
        for var in variations:
            weights[var] = 0.75
        
        # Limit total expansions
        all_expansions = expanded_terms + synonyms + related_concepts
        if len(all_expansions) > self.max_expansions:
            # Keep highest weighted terms
            scored = [(term, weights.get(term, 0.5)) for term in all_expansions]
            scored.sort(key=lambda x: x[1], reverse=True)
            all_expansions = [term for term, _ in scored[:self.max_expansions]]
        
        return ExpandedQuery(
            original=query,
            expanded_terms=expanded_terms[:self.max_expansions // 3],
            synonyms=synonyms[:self.max_expansions // 3],
            related_concepts=related_concepts[:self.max_expansions // 3],
            corrected_terms=corrected_terms,
            weights=weights
        )
    
    async def expand_with_llm(
        self,
        query: str,
        llm_service: Optional[Any] = None,
        context: Optional[str] = None
    ) -> ExpandedQuery:
        """
        Expand query using LLM for semantic understanding.
        
        Args:
            query: Original query
            llm_service: LLM service for generation
            context: Optional context for better expansion
            
        Returns:
            ExpandedQuery with LLM-generated terms
        """
        # First, do standard expansion
        expanded = await self.expand(query)
        
        # If LLM service is available, get semantic expansions
        if llm_service:
            try:
                prompt = self._build_expansion_prompt(query, context)
                llm_expansions = await llm_service.generate(
                    prompt,
                    max_tokens=100,
                    temperature=0.3
                )
                
                # Parse LLM response
                llm_terms = self._parse_llm_expansions(llm_expansions)
                
                # Add to related concepts
                expanded.related_concepts.extend(llm_terms[:5])
                for term in llm_terms:
                    expanded.weights[term] = 0.65
                    
            except Exception as e:
                logger.error(f"LLM expansion failed: {e}")
        
        return expanded
    
    def _build_expansion_prompt(self, query: str, context: Optional[str]) -> str:
        """Build prompt for LLM query expansion"""
        prompt = f"""Given the search query: "{query}"

Generate 5 related search terms or phrases that would help find relevant content.
Focus on:
- Synonyms and related concepts
- Common variations
- Domain-specific terminology

"""
        if context:
            prompt += f"\nContext: {context}\n"
        
        prompt += "\nReturn only the terms, one per line, without numbering or explanations."
        
        return prompt
    
    def _parse_llm_expansions(self, llm_response: str) -> List[str]:
        """Parse LLM-generated expansion terms"""
        lines = llm_response.strip().split('\n')
        terms = []
        
        for line in lines:
            # Clean up the line
            line = line.strip()
            # Remove numbering, bullets, etc.
            line = re.sub(r'^[\d\.\-\*\+]+\s*', '', line)
            if line and len(line.split()) <= 5:  # Reasonable term length
                terms.append(line.lower())
        
        return terms
    
    def _extract_terms(self, query: str) -> List[str]:
        """Extract meaningful terms from query"""
        # Remove punctuation and split
        query = re.sub(r'[^\w\s]', ' ', query)
        terms = query.lower().split()
        
        # Remove stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                      'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'be', 'been'}
        terms = [t for t in terms if t not in stop_words and len(t) > 2]
        
        return terms
    
    def _extract_ngrams(self, text: str, n: int = 2) -> List[str]:
        """Extract n-grams from text"""
        words = text.split()
        ngrams = []
        
        for i in range(len(words) - n + 1):
            ngram = ' '.join(words[i:i+n])
            ngrams.append(ngram)
        
        return ngrams
    
    def _spell_correct(self, term: str) -> str:
        """Basic spelling correction (can be enhanced with external library)"""
        # Common tech typos
        corrections = {
            'machien': 'machine',
            'learing': 'learning',
            'analize': 'analyze',
            'databse': 'database',
            'serach': 'search',
            'optimze': 'optimize',
            'performace': 'performance',
        }
        
        return corrections.get(term, term)
    
    def _generate_variations(self, terms: List[str]) -> List[str]:
        """Generate word variations (plurals, etc.)"""
        variations = []
        
        for term in terms:
            # Add plural if not already plural
            if not term.endswith('s'):
                variations.append(term + 's')
            
            # Add singular if plural
            if term.endswith('s') and len(term) > 3:
                variations.append(term[:-1])
            
            # Add -ing form for verbs
            if len(term) > 3 and not term.endswith('ing'):
                if term.endswith('e'):
                    variations.append(term[:-1] + 'ing')
                else:
                    variations.append(term + 'ing')
        
        return variations
    
    def get_expanded_query_string(self, expanded: ExpandedQuery, strategy: str = 'weighted') -> str:
        """
        Convert expanded query to search string.
        
        Args:
            expanded: ExpandedQuery object
            strategy: 'simple', 'weighted', or 'boolean'
            
        Returns:
            Formatted query string
        """
        if strategy == 'simple':
            # Just concatenate all terms
            all_terms = expanded.get_all_terms()
            return ' '.join(all_terms)
        
        elif strategy == 'weighted':
            # Include weights (for systems that support it)
            weighted = expanded.get_weighted_terms()
            # Format: term^weight
            return ' '.join([f"{term}^{weight:.2f}" for term, weight in weighted.items()])
        
        elif strategy == 'boolean':
            # Boolean query with OR
            original_terms = expanded.original.split()
            other_terms = (expanded.expanded_terms + expanded.synonyms + 
                          expanded.related_concepts)
            
            if not other_terms:
                return expanded.original
            
            # Original terms are required (AND), expansions are optional (OR)
            required = ' AND '.join(original_terms)
            optional = ' OR '.join(other_terms[:5])
            return f"({required}) OR ({optional})"
        
        else:
            return expanded.original


class SemanticQueryRewriter:
    """
    Rewrite queries for better semantic understanding.
    
    Handles:
    - Question to statement conversion
    - Query normalization
    - Intent detection
    """
    
    def __init__(self):
        self.question_patterns = [
            (r'^what is (.+)', r'\1 definition explanation'),
            (r'^how to (.+)', r'\1 tutorial guide steps'),
            (r'^why (.+)', r'\1 reason explanation'),
            (r'^when (.+)', r'\1 timing schedule'),
            (r'^where (.+)', r'\1 location place'),
            (r'^who (.+)', r'\1 person author'),
        ]
    
    def rewrite(self, query: str) -> str:
        """
        Rewrite query for better retrieval.
        
        Args:
            query: Original query
            
        Returns:
            Rewritten query
        """
        query = query.lower().strip()
        
        # Convert questions to statements
        for pattern, replacement in self.question_patterns:
            if re.match(pattern, query):
                query = re.sub(pattern, replacement, query)
                break
        
        # Remove question marks
        query = query.replace('?', '')
        
        # Normalize whitespace
        query = ' '.join(query.split())
        
        return query
    
    def detect_intent(self, query: str) -> str:
        """
        Detect query intent.
        
        Returns:
            Intent type: 'informational', 'navigational', 'transactional'
        """
        query = query.lower()
        
        # Transactional keywords
        if any(word in query for word in ['buy', 'purchase', 'order', 'download', 'install']):
            return 'transactional'
        
        # Navigational keywords
        if any(word in query for word in ['login', 'sign in', 'homepage', 'website']):
            return 'navigational'
        
        # Default to informational
        return 'informational'
