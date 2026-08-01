import os
import pandas as pd

class DataLoader:
    """
    DataLoader loads and indexes all WhatsApp context tables from the dataset directory.
    """
    def __init__(self, dataset_dir="dataset"):
        self.dataset_dir = dataset_dir
        self.users_df = None
        self.groups_df = None
        self.group_members_df = None
        self.business_accounts_df = None
        self.user_business_history_df = None
        self.message_history_df = None
        self.message_events_df = None
        self.images_df = None
        self.voice_notes_df = None
        self.daily_summary_df = None
        
        # Indexed lookups for O(1) performance
        self.users_dict = {}
        self.groups_dict = {}
        self.group_members_dict = {} # (group_id, user_id) -> row
        self.business_dict = {}
        self.user_biz_history_dict = {} # (user_id, business_id) -> row
        self.images_dict = {}
        self.voice_notes_dict = {}
        
        self.load_all()

    def _safe_read_csv(self, filename):
        path = os.path.join(self.dataset_dir, filename)
        if os.path.exists(path) and os.path.getsize(path) > 0:
            try:
                return pd.read_csv(path).fillna("")
            except Exception as e:
                print(f"[DataLoader] Warning loading {filename}: {e}")
                return pd.DataFrame()
        return pd.DataFrame()

    def load_all(self):
        print(f"[DataLoader] Loading dataset tables from '{self.dataset_dir}'...")
        self.users_df = self._safe_read_csv("users.csv")
        self.groups_df = self._safe_read_csv("groups.csv")
        self.group_members_df = self._safe_read_csv("group_members.csv")
        self.business_accounts_df = self._safe_read_csv("business_accounts.csv")
        self.user_business_history_df = self._safe_read_csv("user_business_history.csv")
        self.message_history_df = self._safe_read_csv("message_history.csv")
        self.message_events_df = self._safe_read_csv("message_events.csv")
        self.images_df = self._safe_read_csv("images.csv")
        self.voice_notes_df = self._safe_read_csv("voice_notes.csv")
        self.daily_summary_df = self._safe_read_csv("daily_notification_summary.csv")

        self.build_indices()

    def build_indices(self):
        # Index users
        if not self.users_df.empty and 'user_id' in self.users_df.columns:
            for _, row in self.users_df.iterrows():
                self.users_dict[str(row['user_id'])] = row.to_dict()

        # Index groups
        if not self.groups_df.empty and 'group_id' in self.groups_df.columns:
            for _, row in self.groups_df.iterrows():
                self.groups_dict[str(row['group_id'])] = row.to_dict()

        # Index group members
        if not self.group_members_df.empty and 'group_id' in self.group_members_df.columns:
            for _, row in self.group_members_df.iterrows():
                key = (str(row['group_id']), str(row['user_id']))
                self.group_members_dict[key] = row.to_dict()

        # Index business accounts
        if not self.business_accounts_df.empty and 'business_id' in self.business_accounts_df.columns:
            for _, row in self.business_accounts_df.iterrows():
                self.business_dict[str(row['business_id'])] = row.to_dict()

        # Index user business history
        if not self.user_business_history_df.empty and 'user_id' in self.user_business_history_df.columns:
            for _, row in self.user_business_history_df.iterrows():
                key = (str(row['user_id']), str(row['business_id']))
                self.user_biz_history_dict[key] = row.to_dict()

        # Index images
        if not self.images_df.empty and 'image_id' in self.images_df.columns:
            for _, row in self.images_df.iterrows():
                self.images_dict[str(row['image_id'])] = row.to_dict()

        # Index voice notes
        if not self.voice_notes_df.empty and 'voice_note_id' in self.voice_notes_df.columns:
            for _, row in self.voice_notes_df.iterrows():
                self.voice_notes_dict[str(row['voice_note_id'])] = row.to_dict()

        print(f"[DataLoader] Indexed {len(self.users_dict)} users, {len(self.groups_dict)} groups, {len(self.business_dict)} businesses.")

    def get_messages_to_route(self):
        return self._safe_read_csv("messages.csv")

    def get_sample_messages(self):
        return self._safe_read_csv("sample_messages.csv")
