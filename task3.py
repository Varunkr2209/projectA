#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import yaml
from typing import Tuple, Optional, Dict, Any

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

# Load mappings from external YAML file (fallback to defaults if not found)
try:
    with open('config/mappings.yaml') as f:
        mappings = yaml.safe_load(f)
        FUNCTION_HIERARCHY = mappings['functions']
        SENIORITY_KEYWORDS = mappings['seniority']
except FileNotFoundError:
    # Default mappings if config file isn't found
    FUNCTION_HIERARCHY = {
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
    }

    SENIORITY_KEYWORDS = {
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
    }

def match_with_confidence(title: str, keywords: Dict[str, Any], is_function: bool = False) -> Tuple[Optional[str], float]:
    """
    Match job title with keywords and return the best match with confidence score.
    
    Args:
        title: Job title to match against
        keywords: Dictionary of keywords to match
        is_function: Whether we're matching functions (special handling)
    
    Returns:
        Tuple of (matched_value, confidence_score)
    """
    title = title.lower()
    matches = []
    
    # For function matching, we need to handle the hierarchy
    if is_function:
        for func, subfuncs in keywords.items():
            for key, value in subfuncs.items():
                if re.search(rf'\b{key}\b', title):
                    matches.append((func, value, 1.0))  # Full confidence
    
    # For seniority matching (flat structure)
    else:
        for key, value in keywords.items():
            if re.search(rf'\b{key}\b', title):
                matches.append((value, 1.0))  # Full confidence
    
    # If no exact matches, try partial matches with lower confidence
    if not matches and is_function:
        for func, subfuncs in keywords.items():
            for key, value in subfuncs.items():
                if key in title:
                    matches.append((func, value, 0.7))  # Partial confidence
    
    elif not matches:
        for key, value in keywords.items():
            if key in title:
                matches.append((value, 0.7))  # Partial confidence
    
    # Return the highest confidence match
    if matches:
        if is_function:
            # For functions, we want to return both function and sub-function
            return (matches[0][0], matches[0][1]), matches[0][2]
        return matches[0]
    return (None, None) if is_function else (None, 0.0)

@app.route('/categorise', methods=['POST'])
def categorise_job_title():
    """
    Categorize a job title into function, sub-function, and seniority.
    
    Request:
        POST /categorise
        Content-Type: application/json
        {"title": "Senior Growth Manager"}
    
    Response:
        {
            "function": "Marketing",
            "sub_function": "Growth",
            "seniority": "Senior",
            "confidence": 1.0,
            "matched": true,
            "warnings": []
        }
    """
    if not request.is_json:
        return jsonify({
            "error": "Missing JSON in request",
            "solution": "Set Content-Type to application/json and provide a JSON body"
        }), 400

    data = request.get_json()
    title = data.get('title', '').strip()
    
    if not title:
        return jsonify({
            "error": "Missing or empty 'title' field",
            "solution": "Provide a job title in the format: {\"title\": \"Your Job Title\"}"
        }), 400

    title_lower = title.lower()
    
    # Match function and sub-function
    (function, sub_function), func_conf = match_with_confidence(
        title_lower, FUNCTION_HIERARCHY, is_function=True
    )
    
    # Match seniority
    seniority, seniority_conf = match_with_confidence(title_lower, SENIORITY_KEYWORDS)
    
    # Calculate overall confidence
    confidence = (func_conf + seniority_conf) / 2
    matched = confidence > 0.7
    
    # Generate warnings if needed
    warnings = []
    if not matched:
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
        "original_title": title  # Echo back the original for reference
    }
    
    return jsonify(result)

@app.route('/')
def index():
    """API Homepage"""
    return jsonify({
        "message": "Job Categorization API",
        "endpoints": {
            "categorize_job": {
                "method": "POST",
                "path": "/categorise",
                "description": "Categorize job titles into function and seniority",
                "example_request": {"title": "Senior Growth Manager"},
                "example_response": {
                    "function": "Marketing",
                    "sub_function": "Growth",
                    "seniority": "Senior",
                    "confidence": 1.0,
                    "matched": True
                }
            }
        }
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": {
            "categorize_job": "POST /categorise"
        }
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({
        "error": "Method not allowed",
        "solution": "This endpoint only accepts POST requests"
    }), 405

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
