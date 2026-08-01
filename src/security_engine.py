import re
import urllib.parse

class SecurityEngine:
    """
    SecurityEngine provides enterprise-grade safety checks:
    - Phishing link detection
    - Domain spoofing & suspicious TLD analysis
    - Brand spoofing detection
    - High report rate sender quarantine
    """
    SUSPICIOUS_TLDS = {".xyz", ".biz", ".top", ".click", ".win", ".info", ".online", ".site", ".tk", ".ml", ".ga", ".cf", ".gq"}
    TRUSTED_DOMAINS = {"zomato.com", "swiggy.in", "amazon.com", "uber.com", "hdfcbank.com", "sbi.co.in", "whatsapp.com", "google.com"}
    KNOWN_BRANDS = ["zomato", "swiggy", "amazon", "uber", "hdfc", "sbi", "paytm", "phonepe", "bank"]

    @classmethod
    def analyze_security(cls, text, domain="", sender_reports=0, is_verified=True):
        text_lower = str(text).lower()
        domain_lower = str(domain).lower()
        
        is_scam = False
        is_suspicious_domain = False
        is_brand_spoof = False
        risk_score = 0.0
        risk_reasons = []

        # 1. Suspicious TLD check
        if any(domain_lower.endswith(tld) for tld in cls.SUSPICIOUS_TLDS):
            is_suspicious_domain = True
            risk_score += 0.6
            risk_reasons.append(f"Unverified suspicious domain TLD: {domain_lower}")

        # 2. Phishing link patterns
        links = re.findall(r'https?://[^\s]+', text_lower)
        for link in links:
            parsed = urllib.parse.urlparse(link)
            netloc = parsed.netloc.lower()
            if any(netloc.endswith(tld) for tld in cls.SUSPICIOUS_TLDS) or "bit.ly" in netloc or "tinyurl" in netloc:
                is_scam = True
                risk_score += 0.7
                risk_reasons.append(f"Shortened or unverified link detected: {netloc}")

        # 3. Brand spoofing check
        for brand in cls.KNOWN_BRANDS:
            if brand in text_lower:
                if not is_verified and domain_lower and not any(td in domain_lower for td in cls.TRUSTED_DOMAINS):
                    is_brand_spoof = True
                    risk_score += 0.8
                    risk_reasons.append(f"Unverified sender claiming brand identity '{brand}' from domain '{domain_lower}'")

        # 4. Report history threshold
        if sender_reports >= 10:
            risk_score += 0.5
            risk_reasons.append(f"Sender has high historical report count ({sender_reports} reports)")

        # 5. Financial scam keywords
        scam_phrases = ["lottery won", "claim 50000", "account suspended", "bank blocked", "call immediately", "urgent transfer", "wire money"]
        for phrase in scam_phrases:
            if phrase in text_lower:
                is_scam = True
                risk_score += 0.75
                risk_reasons.append(f"Phishing/Scam keyword pattern matched: '{phrase}'")

        is_high_risk = risk_score >= 0.50 or is_scam or is_brand_spoof

        return {
            "is_high_risk": is_high_risk,
            "is_scam": is_scam,
            "is_suspicious_domain": is_suspicious_domain,
            "is_brand_spoof": is_brand_spoof,
            "risk_score": min(round(risk_score, 2), 1.0),
            "risk_reasons": risk_reasons
        }
