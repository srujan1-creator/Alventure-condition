import pandas as pd
from sklearn.metrics import classification_report, accuracy_score

class SystemEvaluator:
    """
    SystemEvaluator benchmarks predictions against ground truth sample messages.
    """
    def __init__(self, data_loader):
        self.data_loader = data_loader

    def evaluate_on_sample(self, router_engine):
        sample_df = self.data_loader.get_sample_messages()
        if sample_df.empty or 'action' not in sample_df.columns:
            print("[Evaluator] No sample ground truth labels available for evaluation.")
            return

        y_true_action = []
        y_pred_action = []
        y_true_type = []
        y_pred_type = []

        print(f"[Evaluator] Evaluating router performance on {len(sample_df)} sample messages...")

        for _, row in sample_df.iterrows():
            pred = router_engine.route_message(row)
            
            y_true_action.append(str(row['action']).strip().lower())
            y_pred_action.append(str(pred['action']).strip().lower())
            
            y_true_type.append(str(row['message_type']).strip().lower())
            y_pred_type.append(str(pred['message_type']).strip().lower())

        acc_action = accuracy_score(y_true_action, y_pred_action)
        acc_type = accuracy_score(y_true_type, y_pred_type)

        print(f"=== Evaluation Benchmark Results ===")
        print(f"Action Accuracy: {acc_action:.4f}")
        print(f"Message Type Accuracy: {acc_type:.4f}")
        print("\nAction Classification Report:")
        print(classification_report(y_true_action, y_pred_action, zero_division=0))

        return {
            "action_accuracy": acc_action,
            "type_accuracy": acc_type
        }
