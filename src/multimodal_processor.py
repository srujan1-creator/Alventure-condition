import re

class MultimodalProcessor:
    """
    MultimodalProcessor standardizes text, image OCR/descriptions, and voice note transcripts
    into a unified semantic representation with rich feature signals.
    """
    URGENT_KEYWORDS = {"urgent", "asap", "immediately", "emergency", "otp", "code", "verification", "deadline", "meeting", "due today", "critical"}
    PAYMENT_KEYWORDS = {"bill", "payment", "invoice", "fee", "pay", "upi", "qr", "amount due", "due date", "rent", "maintenance"}
    SCAM_KEYWORDS = {"lottery", "won", "claim now", "gift card", "bank blocked", "account suspended", "verify details", "free money", "cashback claim", "click link", "bit.ly", "prize"}
    GREETING_KEYWORDS = {"good morning", "good evening", "happy sunday", "have a nice day", "blessed day", "hello family", "good night"}
    PROMO_KEYWORDS = {"sale", "discount", "off", "coupon", "promo", "deal", "limited time", "buy 1 get 1", "shop now"}

    def __init__(self, data_loader):
        self.data_loader = data_loader

    def process_message(self, msg_row):
        """
        Combines text, image OCR/description, and voice note transcripts into a single unified textual representation.
        Also extracts specific modal flags.
        """
        text = str(msg_row.get("message_text", "")).strip()
        media_type = str(msg_row.get("media_type", "")).strip().lower()
        media_id = str(msg_row.get("media_id", "")).strip()
        
        extracted_text = text
        image_meta = {}
        voice_meta = {}

        if media_type == "image" and media_id in self.data_loader.images_dict:
            image_meta = self.data_loader.images_dict[media_id]
            ocr = str(image_meta.get("ocr_text", "")).strip()
            desc = str(image_meta.get("image_description", "")).strip()
            if ocr:
                extracted_text += f" [IMAGE_OCR: {ocr}]"
            if desc:
                extracted_text += f" [IMAGE_DESC: {desc}]"

        elif media_type == "voice" and media_id in self.data_loader.voice_notes_dict:
            voice_meta = self.data_loader.voice_notes_dict[media_id]
            transcript = str(voice_meta.get("transcript", "")).strip()
            if transcript:
                extracted_text += f" [VOICE_TRANSCRIPT: {transcript}]"

        text_lower = extracted_text.lower()

        # Feature signals
        is_urgent_text = any(k in text_lower for k in self.URGENT_KEYWORDS)
        is_payment_text = any(k in text_lower for k in self.PAYMENT_KEYWORDS)
        is_scam_text = any(k in text_lower for k in self.SCAM_KEYWORDS)
        is_greeting_text = any(k in text_lower for k in self.GREETING_KEYWORDS)
        is_promo_text = any(k in text_lower for k in self.PROMO_KEYWORDS)
        
        user_id = str(msg_row.get("user_id", ""))
        has_direct_mention = False
        if user_id and f"@{user_id}" in text_lower or "@here" in text_lower or "@all" in text_lower:
            has_direct_mention = True

        return {
            "unified_text": extracted_text,
            "media_type": media_type,
            "media_id": media_id,
            "is_urgent_text": is_urgent_text,
            "is_payment_text": is_payment_text,
            "is_scam_text": is_scam_text,
            "is_greeting_text": is_greeting_text,
            "is_promo_text": is_promo_text,
            "has_direct_mention": has_direct_mention,
            "text_length": len(extracted_text)
        }
