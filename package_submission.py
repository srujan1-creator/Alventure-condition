import os
import zipfile
import pandas as pd

ALLOWED_ACTIONS = {"notify", "digest", "mute"}
ALLOWED_TYPES = {"personal", "urgent", "event", "payment", "business_update", "promotion", "greeting", "forward", "spam", "scam", "unknown"}

def validate_output(csv_path="output.csv"):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Output file {csv_path} does not exist!")

    df = pd.read_csv(csv_path)
    expected_cols = ["message_id", "action", "message_type", "reason", "confidence", "evidence_message_ids"]
    
    if list(df.columns) != expected_cols:
        raise ValueError(f"Columns mismatch! Expected {expected_cols}, got {list(df.columns)}")

    for idx, row in df.iterrows():
        action = str(row["action"]).strip().lower()
        m_type = str(row["message_type"]).strip().lower()
        conf = float(row["confidence"])
        ev = str(row["evidence_message_ids"]).strip()

        if action not in ALLOWED_ACTIONS:
            raise ValueError(f"Row {idx}: Invalid action '{action}'. Must be one of {ALLOWED_ACTIONS}")
        if m_type not in ALLOWED_TYPES:
            raise ValueError(f"Row {idx}: Invalid message_type '{m_type}'. Must be one of {ALLOWED_TYPES}")
        if not (0.0 <= conf <= 1.0):
            raise ValueError(f"Row {idx}: Confidence {conf} out of range [0.0, 1.0]")
        if not ev:
            raise ValueError(f"Row {idx}: evidence_message_ids cannot be empty. Use 'none' if empty.")

    print(f"[Validator] '{csv_path}' PASSED all schema & value validations ({len(df)} rows)!")
    return True

def package(zip_filename="code.zip"):
    validate_output("output.csv")

    files_to_zip = []
    
    # Add root scripts & files
    for root_file in ["run_pipeline.py", "package_submission.py", "README.md"]:
        if os.path.exists(root_file):
            files_to_zip.append(root_file)

    # Add directories: src/, tests/
    for folder in ["src", "tests"]:
        if os.path.exists(folder):
            for r, d, files in os.walk(folder):
                for f in files:
                    if not f.endswith(".pyc") and "__pycache__" not in r:
                        files_to_zip.append(os.path.join(r, f))

    print(f"[Packager] Creating '{zip_filename}' containing {len(files_to_zip)} source files...")
    
    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zf:
        for fpath in files_to_zip:
            zf.write(fpath, arcname=fpath)

    print(f"[Packager] Successfully created '{zip_filename}' ({os.path.getsize(zip_filename)} bytes)!")

if __name__ == "__main__":
    package()
