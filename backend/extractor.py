import re
from typing import Dict, List, Any

# Enhanced regex patterns for intelligence extraction
UPI_PATTERNS = [
    r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}",
    r"[a-zA-Z0-9.\-_]+@[\w.-]+",
    r"\b[\w.-]+@[\w.-]+\.[a-zA-Z]{2,}\b"
]

PHONE_PATTERNS = [
    r"\+91[6-9]\d{9}",
    r"\+?\d{10,15}",
    r"\b\d{10}\b",
    r"\+91[-\s]?\d{5}[-\s]?\d{5}"
]

URL_PATTERNS = [
    r"https?://[^\s]+",
    r"www\.[^\s]+",
    r"[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}[^\s]*"
]

BANK_ACCOUNT_PATTERNS = [
    r"\b\d{10,18}\b",
    r"\b[A-Z]{4}\d{7,15}\b",
    r"account\s*#?\s*[:\-]?\s*\d+",
    r"a/c\s*[:\-]?\s*\d+"
]

CARD_PATTERNS = [
    r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
    r"\b\d{13,19}\b",
    r"card\s*#?\s*[:\-]?\s*\d+"
]

def extract_upi_ids(text: str) -> List[str]:
    """Extract UPI IDs from text"""
    upi_ids = []
    for pattern in UPI_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        upi_ids.extend(matches)
    return list(set(upi_ids))  # Remove duplicates

def extract_phone_numbers(text: str) -> List[str]:
    """Extract phone numbers from text"""
    phone_numbers = []
    for pattern in PHONE_PATTERNS:
        matches = re.findall(pattern, text)
        phone_numbers.extend(matches)
    return list(set(phone_numbers))

def extract_urls(text: str) -> List[str]:
    """Extract URLs from text"""
    urls = []
    for pattern in URL_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        urls.extend(matches)
    return list(set(urls))

def extract_bank_accounts(text: str) -> List[str]:
    """Extract bank account numbers from text"""
    accounts = []
    for pattern in BANK_ACCOUNT_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        accounts.extend(matches)
    return list(set(accounts))

def extract_card_numbers(text: str) -> List[str]:
    """Extract card numbers from text"""
    cards = []
    for pattern in CARD_PATTERNS:
        matches = re.findall(pattern, text)
        cards.extend(matches)
    return list(set(cards))

def extract_suspicious_keywords(text: str) -> List[str]:
    """Extract suspicious keywords from text"""
    suspicious_words = [
        "urgent", "immediate", "verify", "confirm", "suspended",
        "blocked", "freeze", "expire", "limited", "exclusive",
        "prize", "winner", "lottery", "bonus", "reward",
        "click", "download", "install", "update", "payment",
        "required", "deposit", "transfer", "otp", "cvv", "pin"
    ]
    
    found_keywords = []
    text_lower = text.lower()
    
    for word in suspicious_words:
        if word in text_lower:
            found_keywords.append(word)
    
    return list(set(found_keywords))

def extract_intelligence(text: str, existing_intel: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """
    Comprehensive intelligence extraction from text
    """
    # Extract all types of intelligence
    upi_ids = extract_upi_ids(text)
    phone_numbers = extract_phone_numbers(text)
    urls = extract_urls(text)
    bank_accounts = extract_bank_accounts(text)
    card_numbers = extract_card_numbers(text)
    suspicious_keywords = extract_suspicious_keywords(text)
    
    # Update existing intelligence without duplicates
    existing_intel["upiIds"].extend([uid for uid in upi_ids if uid not in existing_intel["upiIds"]])
    existing_intel["phoneNumbers"].extend([pn for pn in phone_numbers if pn not in existing_intel["phoneNumbers"]])
    existing_intel["phishingLinks"].extend([url for url in urls if url not in existing_intel["phishingLinks"]])
    existing_intel["bankAccounts"].extend([ba for ba in bank_accounts if ba not in existing_intel["bankAccounts"]])
    existing_intel["suspiciousKeywords"].extend([kw for kw in suspicious_keywords if kw not in existing_intel["suspiciousKeywords"]])
    
    return existing_intel

# Backward compatibility function
def extract(text: str, intel: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Legacy function for backward compatibility"""
    return extract_intelligence(text, intel)
