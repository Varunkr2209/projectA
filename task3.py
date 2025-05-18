#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from concurrent.futures import ThreadPoolExecutor
import re
import yaml
import os
from typing import Tuple, Optional, Dict, Any, List
from dotenv import load_dotenv
from functools import lru_cache
import logging
from logging.config import dictConfig
from rapidfuzz import fuzz, process
import time
from pydantic_settings import BaseSettings
from pydantic import ValidationError

# --------------------------
# Configuration Setup
# --------------------------

# Load environment variables
load_dotenv()

# Configure logging
dictConfig({
    'version': 1,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'fmt': '%(asctime)s %(levelname)s %(name)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
            'stream': 'ext://sys.stdout'
        }
    },
    'root': {
        'level': os.getenv('LOG_LEVEL', 'INFO'),
        'handlers': ['console']
    }
})

logger = logging.getLogger(__name__)

# --------------------------
# Settings Class
# --------------------------

class Settings(BaseSettings):
    """Application configuration settings."""
    config_path: str = os.getenv('CONFIG_PATH', 'config/mappings.yaml')
    min_confidence: float = float(os.getenv('MIN_CONFIDENCE', 0.7))
    api_version: str = os.getenv('API_VERSION', 'v1')
    max_titles_per_request: int = int(os.getenv('MAX_TITLES_PER_REQUEST', 100))
    cache_timeout: int = int(os.getenv('CACHE_TIMEOUT', 300))
    debug: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    port: int = int(os.getenv('PORT', 8000))

# Load settings
try:
    settings = Settings()
except ValidationError as e:
    logger.error(f"Configuration error: {e}")
    raise

# --------------------------
# Flask Application Setup
# --------------------------

app = Flask(__name__)
CORS(app)

# Custom error handler for 500 errors
@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"Internal server error: {str(e)}", exc_info=True)
    return jsonify({
        "status": "error",
        "message": "Internal server error",
        "error": str(e),
        "version": settings.api_version
    }), 500

# Custom error handler for 404 errors
@app.errorhandler(404)
def not_found_error(e):
    return jsonify({
        "status": "error",
        "message": "Endpoint not found",
        "version": settings.api_version
    }), 404

# Custom error handler for 405 errors
@app.errorhandler(405)
def method_not_allowed_error(e):
    return jsonify({
        "status": "error",
        "message": "Method not allowed",
        "version": settings.api_version
    }), 405

# Security headers middleware
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    # Ensure JSON content type for error responses
    if response.status_code >= 400:
        response.headers['Content-Type'] = 'application/json'
    return response

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# Caching configuration
cache = Cache(config={
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': settings.cache_timeout
})
cache.init_app(app)

# Thread pool for async processing
executor = ThreadPoolExecutor(max_workers=4)

# --------------------------
# Configuration Loading
# --------------------------

def load_config() -> Tuple[Dict[str, Any], Dict[str, str], Dict[str, str]]:
    """Load configuration from YAML file with error handling."""
    try:
        with open(settings.config_path) as f:
            mappings = yaml.safe_load(f)
            return (
                mappings.get('functions', {}),
                mappings.get('seniority', {}),
                mappings.get('aliases', {})
            )
    except FileNotFoundError:
        logger.warning(f"Config file not found at {settings.config_path}, using defaults")
        return get_default_mappings()
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML config: {e}")
        return get_default_mappings()

def get_default_mappings() -> Tuple[Dict[str, Any], Dict[str, str], Dict[str, str]]:
    """Return default mappings if config file isn't found."""
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
                "fullstack": "Full Stack Development",
                "software": "Software Engineering"
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

# --------------------------
# Title Processing Functions
# --------------------------

@lru_cache(maxsize=1024)
def normalize_title(title: str) -> str:
    """
    Normalize job title by:
    1. Converting to lowercase
    2. Expanding aliases
    3. Removing special characters
    """
    title = title.lower()
    for alias, expansion in TITLE_ALIASES.items():
        title = title.replace(alias, expansion)
    title = re.sub(r'[^a-zA-Z0-9\s]', '', title)
    return title.strip()

def fuzzy_match(title: str, choices: List[str], min_score: int = 70) -> Optional[Tuple[str, float]]:
    """Perform fuzzy matching using rapidfuzz."""
    result = process.extractOne(title, choices, scorer=fuzz.token_set_ratio)
    if result and result[1] >= min_score:
        return result
    return None

def match_with_confidence(title: str, keywords: Dict[str, Any], is_function: bool = False) -> Tuple[Optional[str], float]:
    """
    Enhanced matching with confidence score.
    
    Args:
        title: Job title to match
        keywords: Dictionary of keywords to match against
        is_function: Whether we're matching functions or seniority
        
    Returns:
        Tuple of (matched_value, confidence_score)
    """
    normalized_title = normalize_title(title)
    matches = []
    
    if is_function:
        # Exact matches in hierarchy
        for func, subfuncs in keywords.items():
            for key, value in subfuncs.items():
                if re.search(rf'\b{key}\b', normalized_title):
                    matches.append((func, value, 1.0))
        
        # Fuzzy matches fallback
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
            matches.sort(key=lambda x: x[2], reverse=True)
            return (matches[0][0], matches[0][1]), matches[0][2]
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[0]
    
    # Always return a properly structured tuple, even when no match is found
    if is_function:
        return ((None, None), 0.0)  # Return ((function, sub_function), confidence)
    else:
        return (None, 0.0)  # Return (seniority, confidence)

@cache.memoize()
def process_title(title: str) -> Dict[str, Any]:
    """Process a single job title and return categorization results."""
    logger.info("Processing job title", extra={"title": title})
    start_time = time.time()
    
    (function, sub_function), func_conf = match_with_confidence(title, FUNCTION_HIERARCHY, is_function=True)
    seniority, seniority_conf = match_with_confidence(title, SENIORITY_KEYWORDS)
    
    confidence = (func_conf + seniority_conf) / 2
    matched = confidence >= settings.min_confidence
    
    warnings = []
    if not function:
        warnings.append("Could not determine function")
    if not seniority:
        warnings.append("Could not determine seniority")
    
    processing_time = round((time.time() - start_time) * 1000, 2)
    
    result = {
        "function": function,
        "sub_function": sub_function,
        "seniority": seniority,
        "confidence": round(confidence, 2),
        "matched": matched,
        "warnings": warnings,
        "original_title": title,
        "processing_time_ms": processing_time
    }
    
    logger.info("Title processed", extra={"result": result})
    return result

def process_title_wrapper(title: str) -> Dict[str, Any]:
    """Wrapper for executor to handle exceptions."""
    try:
        return process_title(title)
    except Exception as e:
        logger.error(f"Error processing title {title}: {str(e)}")
        return {
            "original_title": title,
            "error": str(e),
            "matched": False
        }

# --------------------------
# API Endpoints
# --------------------------

@app.route(f'/{settings.api_version}/categorise', methods=['POST'])
@limiter.limit("5 per second")
def categorise_job_titles():
    """Categorize one or multiple job titles."""
    if not request.is_json:
        logger.warning("Request without JSON payload")
        return jsonify({
            "error": "Missing JSON in request",
            "solution": "Set Content-Type to application/json and provide a JSON body",
            "status": "error",
            "version": settings.api_version
        }), 400

    data = request.get_json()
    titles = []
    
    # Handle both single title and multiple titles input
    if 'title' in data:
        title = data['title'].strip()
        if title:
            titles.append(title)
    elif 'titles' in data:
        if not isinstance(data['titles'], list):
            logger.warning("Invalid titles format", extra={"titles": data.get('titles')})
            return jsonify({
                "error": "Invalid format for 'titles' field",
                "solution": "Provide an array of titles like: {\"titles\": [\"Title1\", \"Title2\"]}",
                "status": "error",
                "version": settings.api_version
            }), 400
        titles = [t.strip() for t in data['titles'] if t.strip()]
    else:
        logger.warning("Missing title/titles field")
        return jsonify({
            "error": "Missing 'title' or 'titles' field",
            "solution": "Provide either a single title or an array of titles",
            "status": "error",
            "version": settings.api_version
        }), 400

    if not titles:
        logger.warning("Empty titles list received")
        return jsonify({
            "error": "No valid titles provided",
            "solution": "Provide at least one non-empty job title",
            "status": "error",
            "version": settings.api_version
        }), 400

    if len(titles) > settings.max_titles_per_request:
        logger.warning("Too many titles in request", extra={"count": len(titles)})
        return jsonify({
            "error": f"Too many titles in one request (max {settings.max_titles_per_request})",
            "solution": f"Split your request into batches of {settings.max_titles_per_request} titles or less",
            "status": "error",
            "version": settings.api_version
        }), 400

    # Process all titles (async for large batches)
    try:
        if len(titles) > 10:
            logger.info("Processing large batch asynchronously", extra={"count": len(titles)})
            futures = [executor.submit(process_title_wrapper, title) for title in titles]
            results = [future.result() for future in futures]
        else:
            results = [process_title(title) for title in titles]
        
        logger.info("Batch processing complete", extra={"count": len(results)})
        return jsonify({
            "results": results,
            "count": len(results),
            "status": "success",
            "version": settings.api_version
        })
    except Exception as e:
        logger.error(f"Error processing batch: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Error processing titles",
            "error": str(e),
            "version": settings.api_version
        }), 500

@app.route('/health')
def health_check():
    """Basic health check endpoint."""
    return jsonify({
        "status": "healthy",
        "version": settings.api_version,
        "timestamp": time.time()
    })

@app.route('/ready')
def readiness_check():
    """Readiness check including dependencies."""
    checks = {
        "config_loaded": bool(FUNCTION_HIERARCHY),
        "cache_working": True,  # Could add actual cache test
        "executor_ready": True
    }
    status = "ready" if all(checks.values()) else "degraded"
    
    return jsonify({
        "status": status,
        "checks": checks,
        "version": settings.api_version
    })

@app.route('/')
def index():
    """API documentation."""
    return jsonify({
        "service": "Job Title Categorization API",
        "version": settings.api_version,
        "endpoints": {
            "categorize": {
                "method": "POST",
                "path": f"/{settings.api_version}/categorise",
                "description": "Categorize job titles",
                "limits": "5 requests per second"
            },
            "health": {
                "method": "GET",
                "path": "/health",
                "description": "Basic service health check"
            },
            "ready": {
                "method": "GET",
                "path": "/ready",
                "description": "Service readiness check"
            }
        },
        "config": {
            "max_titles_per_request": settings.max_titles_per_request,
            "min_confidence": settings.min_confidence,
            "cache_timeout_seconds": settings.cache_timeout
        }
    })

@app.route('/reload-config', methods=['POST'])
def reload_config():
    """Reload configuration without restarting."""
    global FUNCTION_HIERARCHY, SENIORITY_KEYWORDS, TITLE_ALIASES
    try:
        FUNCTION_HIERARCHY, SENIORITY_KEYWORDS, TITLE_ALIASES = load_config()
        logger.info("Configuration reloaded successfully")
        return jsonify({
            "status": "success",
            "message": "Configuration reloaded",
            "config_path": settings.config_path
        })
    except Exception as e:
        logger.error("Failed to reload config", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# --------------------------
# Main Execution
# --------------------------

if __name__ == '__main__':
    app.config['PROPAGATE_EXCEPTIONS'] = True  # Ensure exceptions propagate for JSON responses
    logger.info(f"Starting server on port {settings.port} (debug={settings.debug})")
    app.run(host='0.0.0.0', port=settings.port, debug=settings.debug)