import os
import csv
import pandas as pd
from src.dataset_generator import ensure_dataset_exists
from src.data_loader import DataLoader
from src.multimodal_processor import MultimodalProcessor
from src.feature_extractor import FeatureExtractor
from src.router_engine import MessageRouter
from src.evaluator import SystemEvaluator

def run():
    print("==================================================")
    print(" WhatsApp Message Notification Router Pipeline ")
    print("==================================================")

    # Step 1: Ensure dataset directory is ready
    dataset_dir = "dataset"
    ensure_dataset_exists(dataset_dir=dataset_dir, force=False)

    # Step 2: Initialize modules
    data_loader = DataLoader(dataset_dir=dataset_dir)
    multimodal_proc = MultimodalProcessor(data_loader)
    feat_extractor = FeatureExtractor(data_loader, multimodal_proc)
    router = MessageRouter(data_loader, feat_extractor)

    # Step 3: Run benchmark evaluation if sample messages exist
    evaluator = SystemEvaluator(data_loader)
    evaluator.evaluate_on_sample(router)

    # Step 4: Route all incoming messages in dataset/messages.csv
    messages_df = data_loader.get_messages_to_route()
    if messages_df.empty:
        print("[Pipeline] Error: dataset/messages.csv is empty or missing!")
        return

    print(f"\n[Pipeline] Routing {len(messages_df)} incoming messages from dataset/messages.csv...")

    results = []
    for _, row in messages_df.iterrows():
        pred = router.route_message(row)
        results.append(pred)

    results_df = pd.DataFrame(results)
    
    # Required columns in exact order
    required_cols = ["message_id", "action", "message_type", "reason", "confidence", "evidence_message_ids"]
    results_df = results_df[required_cols]

    # Save to dataset/output.csv and root output.csv
    ds_output_path = os.path.join(dataset_dir, "output.csv")
    root_output_path = "output.csv"

    results_df.to_csv(ds_output_path, index=False)
    results_df.to_csv(root_output_path, index=False)

    print(f"[Pipeline] Successfully generated predictions for {len(results_df)} messages!")
    print(f" Saved to: {ds_output_path}")
    print(f" Saved to: {root_output_path}")

    # Summary Statistics
    print("\n--- Action Distribution ---")
    print(results_df['action'].value_counts())
    print("\n--- Message Type Distribution ---")
    print(results_df['message_type'].value_counts())

    # Step 5: Package submission zip
    from package_submission import package
    package()

if __name__ == "__main__":
    run()
