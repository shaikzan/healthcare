import os
import logging
import re
from urllib.parse import urlparse

# In a real app, we would use NLP libraries like NLTK or spaCy,
# but for this demo, we'll keep it simple with keyword matching

# List of trusted health domains
TRUSTED_DOMAINS = [
    'who.int',
    'cdc.gov',
    'nih.gov',
    'mayoclinic.org',
    'healthline.com',
    'webmd.com',
    'medlineplus.gov',
    'hopkinsmedicine.org',
    'clevelandclinic.org',
    'health.harvard.edu'
]

# Keywords commonly found in false health claims
FALSE_CLAIM_KEYWORDS = [
    'miracle cure',
    'secret remedy',
    'doctors hate this',
    'they don\'t want you to know',
    'big pharma hides',
    'cancer cure suppressed',
    'incredible breakthrough',
    'revolutionary treatment',
    'ancient remedy',
    'toxic',
    'chemical free',
    'natural cure',
    'proven by research'
]

def verify_health_info(text, file=None):
    """
    Verify health information based on text content or uploaded file
    
    In a real application, this would use sophisticated NLP and image recognition,
    but for this demo we use simple heuristics
    """
    result = {
        'verified': False,
        'is_reliable': False,
        'confidence': 0,
        'message': '',
        'details': []
    }
    
    # Handle empty input
    if not text and not file:
        result['message'] = 'Please provide text or upload a file to verify.'
        return result
    
    # Mark as verified (the process was completed)
    result['verified'] = True
    
    # Check if it's a URL
    is_url = False
    domain = None
    if text:
        try:
            parsed = urlparse(text)
            if parsed.scheme and parsed.netloc:
                is_url = True
                domain = parsed.netloc
                if domain.startswith('www.'):
                    domain = domain[4:]
        except:
            pass
    
    # Check against trusted domains
    if is_url and domain:
        if domain in TRUSTED_DOMAINS:
            result['is_reliable'] = True
            result['confidence'] = 0.9
            result['message'] = f"This content is from {domain}, which is a trusted health information source."
            result['details'].append(f"Domain {domain} is on our list of trusted health information providers.")
            return result
    
    # Check for false claim keywords
    false_claim_count = 0
    if text:
        text_lower = text.lower()
        for keyword in FALSE_CLAIM_KEYWORDS:
            if keyword.lower() in text_lower:
                false_claim_count += 1
                result['details'].append(f"Found potentially misleading phrase: '{keyword}'")
    
    # Make a simple determination based on our checks
    if false_claim_count > 0:
        result['is_reliable'] = False
        result['confidence'] = min(0.3 + (false_claim_count * 0.1), 0.9)
        result['message'] = "This content contains language commonly found in misleading health claims."
    else:
        # If we got here, we don't have strong evidence either way
        if is_url and domain:
            result['message'] = f"This content is from {domain}, which is not in our database of verified health sources."
            result['is_reliable'] = False
            result['confidence'] = 0.6
        else:
            result['message'] = "We don't have enough information to verify this content definitively."
            result['is_reliable'] = None
            result['confidence'] = 0.5
            result['details'].append("For more accurate verification, please provide a link to the original source.")
    
    # If file was uploaded (in a real app, we'd do image processing or OCR here)
    if file:
        result['details'].append("File analysis is limited in this demo version. For a complete verification, please include the text content or source URL.")
    
    return result
