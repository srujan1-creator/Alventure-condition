import re
from src.evidence_retriever import EvidenceRetriever
from src.security_engine import SecurityEngine

class MessageRouter:
    """
    MessageRouter makes personalized, multi-stage routing decisions for each WhatsApp message.
    """
    def __init__(self, data_loader, feature_extractor):
        self.data_loader = data_loader
        self.feature_extractor = feature_extractor
        self.evidence_retriever = EvidenceRetriever(data_loader)

    def route_message(self, msg_row):
        feat = self.feature_extractor.extract_features(msg_row)
        m_id = feat["message_id"]
        text = feat["unified_text"]
        text_lower = text.lower()
        conv_type = feat["conversation_type"]
        
        # Security Analysis
        sec = SecurityEngine.analyze_security(
            text=text,
            domain=feat["b_sender_domain"],
            sender_reports=feat["b_report_count"],
            is_verified=feat["b_is_verified"]
        )

        # Default decision tuple: (action, message_type, reason, confidence)
        action = "digest"
        msg_type = "unknown"
        reason = "Routed based on standard contextual rules"
        confidence = 0.85

        # ----------------------------------------------------
        # Stage 1: Safety & Scam Guardrails (Highest Priority Mute)
        # ----------------------------------------------------
        if sec["is_high_risk"] or feat["is_scam_text"] or ("lottery" in text_lower or "won $" in text_lower or "claim prize" in text_lower):
            action = "mute"
            msg_type = "scam" if (sec["is_scam"] or "scam" in text_lower or "lottery" in text_lower or "won" in text_lower) else "spam"
            reasons_str = "; ".join(sec["risk_reasons"]) if sec["risk_reasons"] else "Suspicious phishing patterns or unverified domain detected"
            reason = f"Security Override: {reasons_str}"
            confidence = 0.97

        # ----------------------------------------------------
        # Stage 2: Critical Urgency & High Priority Interruption (Notify)
        # ----------------------------------------------------
        elif "otp" in text_lower or "verification code" in text_lower or "security code" in text_lower:
            action = "notify"
            msg_type = "urgent"
            reason = "Critical time-sensitive security authentication OTP"
            confidence = 0.98

        elif feat["has_direct_mention"]:
            action = "notify"
            msg_type = "urgent" if feat["is_urgent_text"] else "personal"
            reason = "Direct user mention (@user) requires immediate attention"
            confidence = 0.94

        elif feat["ub_has_recent_order"] or feat["ub_has_recent_booking"] or ("order" in text_lower and "picked up" in text_lower):
            action = "notify" if not feat["is_quiet_hours"] else "digest"
            msg_type = "business_update"
            reason = "Real-time delivery/booking update from trusted merchant"
            confidence = 0.92

        elif conv_type == "personal" and (feat["is_urgent_text"] or feat["media_type"] == "voice"):
            action = "notify" if not feat["is_quiet_hours"] else "digest"
            msg_type = "urgent" if feat["is_urgent_text"] else "personal"
            reason = "Personal direct communication requiring timely review"
            confidence = 0.90

        # ----------------------------------------------------
        # Stage 3: Low-Value, Repetitive & Quiet Hour Muting / Digest
        # ----------------------------------------------------
        elif feat["is_high_forward"]:
            action = "mute"
            msg_type = "forward"
            reason = "High forward count message treated as viral broadcast noise"
            confidence = 0.91

        elif feat["is_greeting_text"]:
            action = "mute"
            msg_type = "greeting"
            reason = "Routine social greeting message muted to minimize interruption"
            confidence = 0.93

        elif feat["group_is_muted"] and not feat["has_direct_mention"]:
            action = "mute"
            msg_type = "event" if feat["is_payment_text"] else "personal"
            reason = "Group chat is muted by user preferences"
            confidence = 0.95

        elif feat["ub_opt_out"]:
            action = "mute"
            msg_type = "promotion"
            reason = "User explicitly opted out of marketing communications from sender"
            confidence = 0.96

        # ----------------------------------------------------
        # Stage 4: Useful Contextual Digest (Digest)
        # ----------------------------------------------------
        elif feat["is_promo_text"] or conv_type == "business":
            action = "digest"
            msg_type = "promotion" if feat["is_promo_text"] else "business_update"
            reason = "Useful commercial update batched into non-intrusive daily summary"
            confidence = 0.88

        elif feat["is_payment_text"] or "bill" in text_lower or "due" in text_lower:
            action = "digest"
            msg_type = "payment"
            reason = "Upcoming bill or payment notice saved to digest"
            confidence = 0.89

        elif "meeting" in text_lower or "event" in text_lower or "society" in text_lower:
            action = "digest"
            msg_type = "event"
            reason = "Community event notice scheduled for batch review"
            confidence = 0.87

        else:
            action = "digest" if not feat["is_quiet_hours"] else "mute"
            msg_type = "personal" if conv_type == "personal" else "unknown"
            reason = "Standard informational update routed to digest"
            confidence = 0.82

        # Retrieve evidence message IDs
        evidence_ids = self.evidence_retriever.find_evidence(feat)

        return {
            "message_id": m_id,
            "action": action,
            "message_type": msg_type,
            "reason": reason,
            "confidence": round(confidence, 2),
            "evidence_message_ids": evidence_ids,
            "security": sec,
            "features": feat
        }
