import re

class EvidenceRetriever:
    """
    EvidenceRetriever locates historical message IDs ('evidence_message_ids')
    that serve as contextual evidence for the routing decision.
    """
    def __init__(self, data_loader):
        self.data_loader = data_loader
        self.history_df = data_loader.message_history_df
        self.events_df = data_loader.message_events_df

    def _token_set(self, text):
        return set(re.findall(r'\w+', str(text).lower()))

    def find_evidence(self, feat_dict, top_k=2):
        if self.history_df.empty or 'user_id' not in self.history_df.columns:
            return "none"

        user_id = feat_dict["user_id"]
        group_id = feat_dict["group_id"]
        business_id = feat_dict["business_id"]
        sender_user_id = feat_dict["sender_user_id"]
        unified_text = feat_dict["unified_text"]
        target_tokens = self._token_set(unified_text)

        # Filter candidate historical messages for this user
        user_hist = self.history_df[self.history_df['user_id'] == user_id]
        if user_hist.empty:
            return "none"

        scored_candidates = []
        for _, row in user_hist.iterrows():
            score = 0.0
            h_id = str(row['message_id'])
            
            # Context match bonus
            if group_id and str(row.get('group_id', '')) == group_id:
                score += 0.4
            if business_id and str(row.get('business_id', '')) == business_id:
                score += 0.4
            if sender_user_id and str(row.get('sender_user_id', '')) == sender_user_id:
                score += 0.5
                
            # Text token similarity (Jaccard)
            h_tokens = self._token_set(row.get('message_text', ''))
            if target_tokens and h_tokens:
                intersection = len(target_tokens.intersection(h_tokens))
                union = len(target_tokens.union(h_tokens))
                jaccard = intersection / float(union)
                score += jaccard * 0.5

            if score > 0.35:
                scored_candidates.append((h_id, score))

        if not scored_candidates:
            return "none"

        # Sort by relevance score descending
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        top_ids = [c[0] for c in scored_candidates[:top_k]]
        return ";".join(top_ids)
