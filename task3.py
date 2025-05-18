#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import re
import yaml
import os
from typing import Tuple, Optional, Dict, Any, List
from dotenv import load_dotenv
from functools import lru_cache
import logging
from rapidfuzz import fuzz, process

# Configuration setup
load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
CONFIG_PATH = os.getenv('CONFIG_PATH', 'config/mappings.yaml')
MIN_CONFIDENCE = float(os.getenv('MIN_CONFIDENCE', 0.7))
API_VERSION = os.getenv('API_VERSION', 'v1')

def load_config() -> Tuple[Dict[str, Any], Dict[str, str]]:
    """Load configuration from YAML file with enhanced error handling"""
    try:
        with open(CONFIG_PATH) as f:
            mappings = yaml.safe_load(f)
            return (
                mappings.get('functions', {}),
                mappings.get('seniority', {}),
                mappings.get('aliases', {})
            )
    except FileNotFoundError:
        logger.warning(f"Config file not found at {CONFIG_PATH}, using defaults")
        return get_default_mappings()
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML config: {e}")
        return get_default_mappings()

def get_default_mappings() -> Tuple[Dict[str, Any], Dict[str, str]]:
    """Return default mappings if config file isn't found"""
    return (
        {  # FUNCTION_HIERARCHY
            "Marketing": {
                "growth": "Growth",
                "brand": "Brand Management",
                "paid media": "Performance Marketing",
                "content": "Content Marketing",
                "digital": "Digital Marketing"
            },
            "Sales": {
                "account": "Account Management",
                "business development": "Business Development",
                "sales development": "Sales Development"
            },
            "Engineering": {
                "frontend": "Frontend Development",
                "backend": "Backend Development",
                "fullstack": "Full Stack Development"
            }
        },
        {  # SENIORITY_KEYWORDS
            "intern": "Entry",
            "junior": "Entry",
            "associate": "Entry",
            "analyst": "Entry",
            "specialist": "Mid-Level",
            "manager": "Manager",
            "director": "Director",
            "vp": "VP",
            "chief": "C-Level",
            "cmo": "C-Level",
            "cto": "C-Level",
            "head": "Director",
            "lead": "Manager",
            "sr": "Senior",
            "senior": "Senior"
        },
        {  # TITLE_ALIASES
            "dev": "developer",
            "eng": "engineer",
            "mgr": "manager"
        }
    )

# Load configurations
FUNCTION_HIERARCHY, SENIORITY_KEYWORDS, TITLE_ALIASES = load_config()

@lru_cache(maxsize=1024)
def normalize_title(title: str) -> str:
    """
    Normalize job title by:
    1. Converting to lowercase
    2. Expanding known aliases
    3. Removing special characters
    """
    title = title.lower()
    # Replace known aliases
    for alias, expansion in TITLE_ALIASES.items():
        title = title.replace(alias, expansion)
    # Remove special characters
    title = re.sub(r'[^a-zA-Z0-9\s]', '', title)
    return title.strip()

def fuzzy_match(title: str, choices: List[str], min_score: int = 70) -> Optional[Tuple[str, float]]:
    """Perform fuzzy matching using rapidfuzz"""
    result = process.extractOne(title, choices, scorer=fuzz.token_set_ratio)
    if result and result[1] >= min_score:
        return result
    return None

def match_with_confidence(title: str, keywords: Dict[str, Any], is_function: bool = False) -> Tuple[Optional[str], float]:
    """
    Enhanced matching with:
    - Exact matching
    - Fuzzy matching
    - Partial matching
    - Hierarchy awareness
    """
    normalized_title = normalize_title(title)
    matches = []
    
    if is_function:
        # First try exact matches in hierarchy
        for func, subfuncs in keywords.items():
            for key, value in subfuncs.items():
                if re.search(rf'\b{key}\b', normalized_title):
                    matches.append((func, value, 1.0))
        
        # Then try fuzzy matches
        if not matches:
            all_subfuncs = [k for sub in keywords.values() for k in sub.keys()]
            if fuzzy_match_result := fuzzy_match(normalized_title, all_subfuncs):
                matched_key, score = fuzzy_match_result
                for func, subfuncs in keywords.items():
                    if matched_key in subfuncs:
                        confidence = score / 100
                        matches.append((func, subfuncs[matched_key], confidence))
    else:
        # Seniority matching
        for key, value in keywords.items():
            if re.search(rf'\b{key}\b', normalized_title):
                matches.append((value, 1.0))
        
        # Fuzzy match fallback
        if not matches:
            if fuzzy_match_result := fuzzy_match(normalized_title, list(keywords.keys())):
                matched_key, score = fuzzy_match_result
                confidence = score / 100
                matches.append((keywords[matched_key], confidence))
    
    # Return best match
    if matches:
        if is_function:
            # Sort by confidence and return the best function match
            matches.sort(key=lambda x: x[2], reverse=True)
            return (matches[0][0], matches[0][1]), matches[0][2]
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[0]
    
    return (None, None) if is_function else (None, 0.0)

@app.route(f'/{API_VERSION}/categorise', methods=['POST'])
@limiter.limit("5 per second")
def categorise_job_title():
    """
    Enhanced categorization endpoint with:
    - Better error handling
    - Input validation
    - Rate limiting
    - Versioning
    """
    if not request.is_json:
        return jsonify({
            "error": "Missing JSON in request",
            "solution": "Set Content-Type to application/json and provide a JSON body",
            "status": "error",
            "version": API_VERSION
        }), 400

    data = request.get_json()
    title = data.get('title', '').strip()
    
    if not title:
        return jsonify({
            "error": "Missing or empty 'title' field",
            "solution": "Provide a job title in the format: {\"title\": \"Your Job Title\"}",
            "status": "error",
            "version": API_VERSION
        }), 400

    logger.info(f"Categorizing job title: {title}")
    
    # Match function and sub-function
    (function, sub_function), func_conf = match_with_confidence(
        title, FUNCTION_HIERARCHY, is_function=True
    )
    
    # Match seniority
    seniority, seniority_conf = match_with_confidence(title, SENIORITY_KEYWORDS)
    
    # Calculate overall confidence
    confidence = (func_conf + seniority_conf) / 2
    matched = confidence >= MIN_CONFIDENCE
    
    # Generate warnings if needed
    warnings = []
    if not function:
        warnings.append("Could not determine function")
    if not seniority:
        warnings.append("Could not determine seniority")
    
    result = {
        "function": function,
        "sub_function": sub_function,
        "seniority": seniority,
        "confidence": round(confidence, 2),
        "matched": matched,
        "warnings": warnings,
        "original_title": title,
        "status": "success",
        "version": API_VERSION
    }
    
    return jsonify(result)

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        "status": "healthy",
        "version": API_VERSION,
        "config_loaded": bool(FUNCTION_HIERARCHY)
    })

@app.route('/')
def index():
    """Enhanced API homepage with versioning"""
    return jsonify({
        "message": "Job Categorization API",
        "version": API_VERSION,
        "documentation": f"/{API_VERSION}/docs",  # Would link to Swagger if implemented
        "endpoints": {
            "categorize_job": {
                "method": "POST",
                "path": f"/{API_VERSION}/categorise",
                "description": "Categorize job titles into function and seniority",
                "example_request": {"title": "Senior Growth Manager"},
                "example_response": {
                    "function": "Marketing",
                    "sub_function": "Growth",
                    "seniority": "Senior",
                    "confidence": 1.0,
                    "matched": True
                }
            },
            "health_check": {
                "method": "GET",
                "path": "/health",
                "description": "Service health check"
            }
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)