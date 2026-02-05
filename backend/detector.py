import re
from typing import Tuple, List

# Enhanced scam detection patterns
SCAM_KEYWORDS = [
    "blocked", "verify", "urgent", "upi", "account",
    "suspended", "kyc", "click", "bank", "immediately",
    "limited time", "offer expires", "prize", "winner",
    "lottery", "congratulations", "payment required",
    "act now", "don't miss", "exclusive", "bonus",
    "reward", "claim", "expire", "suspend", "freeze",
    "debit card", "credit card", "cvv", "otp", "pin"
]

URGENCY_PATTERNS = [
    r"\burgent\b", r"\bimmediately\b", r"\bright now\b",
    r"\blast chance\b", r"\blimited time\b", r"\btoday only\b"
]

FINANCIAL_PATTERNS = [
    r"\baccount.*block\b", r"\baccount.*suspend\b", r"\bverify.*account\b",
    r"\bpayment.*required\b", r"\bdeposit.*money\b", r"\btransfer.*fund\b"
]

PHISHING_PATTERNS = [
    r"\bclick.*link\b", r"\bdownload.*app\b", r"\binstall.*software\b",
    r"\bupdate.*details\b", r"\bconfirm.*information\b"
]

def calculate_scam_score(text: str) -> Tuple[bool, List[str], float]:
    """
    Advanced scam detection with scoring system
    Returns: (is_scam, detected_keywords, confidence_score)
    """
    text_lower = text.lower()
    detected_keywords = []
    score = 0.0
    
    # Keyword-based scoring
    keyword_hits = [k for k in SCAM_KEYWORDS if k in text_lower]
    detected_keywords.extend(keyword_hits)
    score += len(keyword_hits) * 0.15
    
    # Urgency pattern detection
    for pattern in URGENCY_PATTERNS:
        if re.search(pattern, text_lower):
            score += 0.25
            detected_keywords.append("urgency_tactic")
    
    # Financial threat patterns
    for pattern in FINANCIAL_PATTERNS:
        if re.search(pattern, text_lower):
            score += 0.30
            detected_keywords.append("financial_threat")
    
    # Phishing patterns
    for pattern in PHISHING_PATTERNS:
        if re.search(pattern, text_lower):
            score += 0.20
            detected_keywords.append("phishing_attempt")
    
    # Suspicious URL detection
    if re.search(r'https?://[^\s]+', text):
        score += 0.15
        detected_keywords.append("suspicious_link")
    
    # Phone number detection
    if re.search(r'\+?\d{10,}', text):
        score += 0.10
        detected_keywords.append("phone_number")
    
    # Normalize score to 0-1 range
    confidence_score = min(score, 1.0)
    is_scam = confidence_score >= 0.4  # Threshold for scam detection
    
    return is_scam, detected_keywords, confidence_score

def detect_scam(text: str) -> Tuple[bool, List[str]]:
    """
    Backward compatibility function
    Returns: (is_scam, detected_keywords)
    """
    is_scam, keywords, _ = calculate_scam_score(text)
    return is_scam, keywords
