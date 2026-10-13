import re
import spacy

# Load SpaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Technical terms mapping to prevent token destruction
TECH_MAPPINGS = {
    r'\bc\+\+(?!\w)': 'cplusplus',
    r'\bc#(?!\w)': 'csharp',
    r'(?<!\w)\.net\b': 'dotnet',
    r'\bnode\.js\b': 'nodejs',
    r'\breact\.js\b': 'reactjs',
    r'\bvue\.js\b': 'vuejs',
    r'\bnext\.js\b': 'nextjs',
    r'\bexpress\.js\b': 'expressjs',
    r'\bangular\.js\b': 'angularjs',
    r'\bci\/cd\b': 'cicd',
    r'\btcp\/ip\b': 'tcpip',
    r'\brest\s*api[s]?\b': 'restapi',
    r'\brestful\b': 'restapi',
    r'\bscikit-learn\b': 'scikitlearn',
    r'\bpower\s*bi\b': 'powerbi',
    r'\bgit\s*hub\b': 'github'
}

def preprocess_text(text):
    """
    Clean, preserve technical terms, and lemmatize text while eliminating noise.
    """
    if not text:
        return ""
        
    text = text.lower()
    
    # Preserve technical keywords before stripping punctuation
    for pattern, replacement in TECH_MAPPINGS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
    # Remove URL links and emails
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
    text = re.sub(r'\S+@\S+', ' ', text)
    
    # Remove non-alphanumeric except spaces
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    doc = nlp(text)
    # Lemmatize and exclude stopwords and short noise tokens
    tokens = [
        token.lemma_ for token in doc 
        if not token.is_stop and not token.is_punct and len(token.lemma_.strip()) > 1
    ]
    return " ".join(tokens)