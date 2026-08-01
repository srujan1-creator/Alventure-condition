from datetime import datetime

class FeatureExtractor:
    """
    FeatureExtractor converts incoming message + context lookups into a structured feature dictionary.
    """
    def __init__(self, data_loader, multimodal_processor):
        self.data_loader = data_loader
        self.multimodal_processor = multimodal_processor

    def _is_time_in_quiet_hours(self, created_at_str, q_start_str, q_end_str):
        if not q_start_str or not q_end_str:
            return False
        try:
            msg_dt = datetime.fromisoformat(str(created_at_str).replace("Z", "+00:00"))
            msg_time = msg_dt.time()
            
            sh, sm = map(int, str(q_start_str).split(":"))
            eh, em = map(int, str(q_end_str).split(":"))
            
            start_time = msg_time.replace(hour=sh, minute=sm, second=0, microsecond=0)
            end_time = msg_time.replace(hour=eh, minute=em, second=0, microsecond=0)
            
            if start_time < end_time:
                return start_time <= msg_time <= end_time
            else: # Overnight quiet hours e.g. 22:00 to 07:00
                return msg_time >= start_time or msg_time <= end_time
        except Exception:
            return False

    def extract_features(self, msg_row):
        u_proc = self.multimodal_processor.process_message(msg_row)
        
        user_id = str(msg_row.get("user_id", ""))
        conv_type = str(msg_row.get("conversation_type", "")).lower()
        group_id = str(msg_row.get("group_id", ""))
        business_id = str(msg_row.get("business_id", ""))
        sender_user_id = str(msg_row.get("sender_user_id", ""))
        created_at = str(msg_row.get("created_at", ""))
        forwarded_count = int(float(msg_row.get("forwarded_count", 0) or 0))

        # 1. User Features
        u_info = self.data_loader.users_dict.get(user_id, {})
        q_start = u_info.get("quiet_hours_start", "")
        q_end = u_info.get("quiet_hours_end", "")
        is_quiet = self._is_time_in_quiet_hours(created_at, q_start, q_end)
        
        user_opens = int(u_info.get("recent_opens", 0) or 0)
        user_replies = int(u_info.get("recent_replies", 0) or 0)
        user_dismissals = int(u_info.get("recent_dismissals", 0) or 0)
        user_reports = int(u_info.get("recent_reports", 0) or 0)

        # 2. Group Features
        g_info = self.groups_dict_get = self.data_loader.groups_dict.get(group_id, {})
        gm_info = self.data_loader.group_members_dict.get((group_id, user_id), {})
        sender_gm_info = self.data_loader.group_members_dict.get((group_id, sender_user_id), {})
        
        group_is_muted = str(gm_info.get("is_muted", "")).lower() in ["true", "1"]
        user_is_group_admin = str(gm_info.get("role", "")).lower() == "admin"
        sender_is_group_admin = str(sender_gm_info.get("role", "")).lower() == "admin"
        g_reply_rate = float(gm_info.get("reply_rate", 0.0) or 0.0)
        g_dismissal_rate = float(gm_info.get("dismissal_rate", 0.0) or 0.0)

        # 3. Business Features
        b_info = self.data_loader.business_dict.get(business_id, {})
        ub_info = self.data_loader.user_biz_history_dict.get((user_id, business_id), {})
        
        b_is_verified = str(b_info.get("is_verified", "")).lower() in ["true", "1"]
        b_sender_domain = str(b_info.get("sender_domain", "")).lower()
        b_report_count = int(b_info.get("report_count", 0) or 0)
        b_age_days = int(b_info.get("account_age_days", 0) or 0)
        
        is_suspicious_domain = any(b_sender_domain.endswith(ext) for ext in [".xyz", ".biz", ".info", ".top", ".click"]) or "scam" in b_sender_domain
        
        ub_has_recent_order = str(ub_info.get("has_recent_order", "")).lower() in ["true", "1"]
        ub_has_recent_booking = str(ub_info.get("has_recent_booking", "")).lower() in ["true", "1"]
        ub_has_recent_payment = str(ub_info.get("has_recent_payment", "")).lower() in ["true", "1"]
        ub_opt_in = str(ub_info.get("opt_in_status", "")).lower() in ["true", "1"]
        ub_opt_out = str(ub_info.get("opt_out_status", "")).lower() in ["true", "1"]

        return {
            "message_id": str(msg_row.get("message_id", "")),
            "user_id": user_id,
            "conversation_type": conv_type,
            "group_id": group_id,
            "business_id": business_id,
            "sender_user_id": sender_user_id,
            "forwarded_count": forwarded_count,
            "is_high_forward": forwarded_count >= 3,
            
            # Multimodal text signals
            "unified_text": u_proc["unified_text"],
            "media_type": u_proc["media_type"],
            "is_urgent_text": u_proc["is_urgent_text"],
            "is_payment_text": u_proc["is_payment_text"],
            "is_scam_text": u_proc["is_scam_text"],
            "is_greeting_text": u_proc["is_greeting_text"],
            "is_promo_text": u_proc["is_promo_text"],
            "has_direct_mention": u_proc["has_direct_mention"],
            
            # User & Quiet Hours
            "is_quiet_hours": is_quiet,
            "user_opens": user_opens,
            "user_replies": user_replies,
            "user_dismissals": user_dismissals,
            "user_reports": user_reports,
            
            # Group Context
            "group_is_muted": group_is_muted,
            "user_is_group_admin": user_is_group_admin,
            "sender_is_group_admin": sender_is_group_admin,
            "g_reply_rate": g_reply_rate,
            "g_dismissal_rate": g_dismissal_rate,
            
            # Business Context
            "b_is_verified": b_is_verified,
            "b_sender_domain": b_sender_domain,
            "b_report_count": b_report_count,
            "b_age_days": b_age_days,
            "is_suspicious_domain": is_suspicious_domain,
            "ub_has_recent_order": ub_has_recent_order,
            "ub_has_recent_booking": ub_has_recent_booking,
            "ub_has_recent_payment": ub_has_recent_payment,
            "ub_opt_in": ub_opt_in,
            "ub_opt_out": ub_opt_out
        }
