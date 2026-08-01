import os
import unittest
import pandas as pd
from src.dataset_generator import ensure_dataset_exists
from src.data_loader import DataLoader
from src.multimodal_processor import MultimodalProcessor
from src.feature_extractor import FeatureExtractor
from src.router_engine import MessageRouter
from src.evidence_retriever import EvidenceRetriever
from package_submission import validate_output

class TestMessageNotificationRouter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dataset_dir = "dataset"
        ensure_dataset_exists(dataset_dir=cls.dataset_dir, force=False)
        cls.loader = DataLoader(dataset_dir=cls.dataset_dir)
        cls.multi_proc = MultimodalProcessor(cls.loader)
        cls.feat_ext = FeatureExtractor(cls.loader, cls.multi_proc)
        cls.router = MessageRouter(cls.loader, cls.feat_ext)

    def test_01_data_loader_indices(self):
        self.assertGreater(len(self.loader.users_dict), 0)
        self.assertGreater(len(self.loader.groups_dict), 0)
        self.assertGreater(len(self.loader.business_dict), 0)

    def test_02_multimodal_processor(self):
        sample_msg = {
            "message_id": "test_001",
            "user_id": "user_001",
            "message_text": "Check this 50% discount sale",
            "media_type": "image",
            "media_id": "img_001"
        }
        res = self.multi_proc.process_message(sample_msg)
        self.assertTrue(res["is_promo_text"])
        self.assertIn("IMAGE_OCR", res["unified_text"])

    def test_03_scam_routing_mute(self):
        scam_msg = {
            "message_id": "test_scam",
            "user_id": "user_001",
            "conversation_type": "personal",
            "message_text": "CONGRATULATIONS YOU WON $50,000 LOTTERY! Click http://scam-link.xyz to claim!",
            "media_type": "",
            "media_id": "",
            "forwarded_count": 0
        }
        decision = self.router.route_message(scam_msg)
        self.assertEqual(decision["action"], "mute")
        self.assertIn(decision["message_type"], ["scam", "spam"])

    def test_04_urgent_otp_routing_notify(self):
        otp_msg = {
            "message_id": "test_otp",
            "user_id": "user_001",
            "conversation_type": "personal",
            "message_text": "Your login OTP is 729104. Do not share.",
            "media_type": "",
            "media_id": "",
            "forwarded_count": 0
        }
        decision = self.router.route_message(otp_msg)
        self.assertEqual(decision["action"], "notify")
        self.assertEqual(decision["message_type"], "urgent")

    def test_05_evidence_retriever(self):
        retriever = EvidenceRetriever(self.loader)
        feat = {
            "user_id": "user_001",
            "group_id": "group_001",
            "business_id": "",
            "sender_user_id": "user_002",
            "unified_text": "Project presentation slides meeting"
        }
        ev_ids = retriever.find_evidence(feat)
        self.assertIsInstance(ev_ids, str)

if __name__ == "__main__":
    unittest.main()
