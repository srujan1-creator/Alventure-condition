import os
import csv
import random
from datetime import datetime, timedelta

def ensure_dataset_exists(dataset_dir="dataset", force=False):
    """
    Checks if dataset/messages.csv exists. If not (or force=True), creates synthetic dataset files.
    """
    os.makedirs(dataset_dir, exist_ok=True)
    media_dir = os.path.join(dataset_dir, "media")
    os.makedirs(media_dir, exist_ok=True)
    
    messages_path = os.path.join(dataset_dir, "messages.csv")
    if os.path.exists(messages_path) and not force and os.path.getsize(messages_path) > 50:
        print(f"[Dataset] Using existing dataset at {dataset_dir}/")
        return

    print(f"[Dataset] Generating synthetic dataset in {dataset_dir}/...")
    
    random.seed(42)

    # 1. Users
    users = []
    for i in range(1, 101):
        u_id = f"user_{i:03d}"
        q_start = random.choice(["22:00", "23:00", "21:30", "00:00", None])
        q_end = random.choice(["07:00", "08:00", "06:30", "08:30", None]) if q_start else None
        users.append({
            "user_id": u_id,
            "quiet_hours_start": q_start or "",
            "quiet_hours_end": q_end or "",
            "recent_opens": random.randint(10, 150),
            "recent_replies": random.randint(5, 80),
            "recent_dismissals": random.randint(2, 50),
            "recent_reports": random.randint(0, 5)
        })

    with open(os.path.join(dataset_dir, "users.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=users[0].keys())
        writer.writeheader()
        writer.writerows(users)

    # 2. Groups
    groups = []
    group_types = ["family", "society", "work", "school", "friends", "interest"]
    for g in range(1, 21):
        g_id = f"group_{g:03d}"
        g_type = random.choice(group_types)
        admin_count = random.randint(1, 3)
        admins = [f"user_{random.randint(1, 100):03d}" for _ in range(admin_count)]
        groups.append({
            "group_id": g_id,
            "group_name": f"{g_type.capitalize()} Group {g}",
            "group_type": g_type,
            "member_count": random.randint(5, 50),
            "admin_user_ids": ";".join(admins),
            "recent_activity_level": random.choice(["high", "medium", "low"])
        })

    with open(os.path.join(dataset_dir, "groups.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=groups[0].keys())
        writer.writeheader()
        writer.writerows(groups)

    # 3. Group Members
    group_members = []
    for g in groups:
        member_users = random.sample(users, random.randint(5, 15))
        admins = g["admin_user_ids"].split(";")
        for u in member_users:
            is_admin = u["user_id"] in admins
            group_members.append({
                "group_id": g["group_id"],
                "user_id": u["user_id"],
                "role": "admin" if is_admin else "member",
                "activity_level": random.choice(["active", "passive", "lurker"]),
                "read_rate": round(random.uniform(0.2, 0.95), 2),
                "reply_rate": round(random.uniform(0.05, 0.70), 2),
                "dismissal_rate": round(random.uniform(0.05, 0.50), 2),
                "is_muted": random.choice([True, False, False, False])
            })

    with open(os.path.join(dataset_dir, "group_members.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=group_members[0].keys())
        writer.writeheader()
        writer.writerows(group_members)

    # 4. Business Accounts
    businesses = []
    brand_names = [
        ("Zomato", True, "zomato.com"), ("Amazon", True, "amazon.com"),
        ("Uber", True, "uber.com"), ("Swiggy", True, "swiggy.in"),
        ("HDFC Bank", True, "hdfcbank.com"), ("State Bank", True, "sbi.co.in"),
        ("Flash Sales LLC", False, "cheapdeals-scam.xyz"), ("Crypto Winners", False, "lottery-win.info"),
        ("Local Bakery", False, "localbakery.com"), ("Quick Loans", False, "fastcash-now.biz")
    ]
    for b_idx, (b_name, is_v, domain) in enumerate(brand_names, start=1):
        b_id = f"biz_{b_idx:03d}"
        businesses.append({
            "business_id": b_id,
            "brand_name": b_name,
            "is_verified": is_v,
            "sender_domain": domain,
            "account_age_days": random.randint(10, 2000) if is_v else random.randint(1, 40),
            "report_count": random.randint(0, 2) if is_v else random.randint(15, 250)
        })

    with open(os.path.join(dataset_dir, "business_accounts.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=businesses[0].keys())
        writer.writeheader()
        writer.writerows(businesses)

    # 5. User Business History
    user_biz_history = []
    for u in users:
        sampled_biz = random.sample(businesses, random.randint(1, 4))
        for b in sampled_biz:
            opt_in = random.choice([True, False]) if b["is_verified"] else False
            opt_out = not opt_in if random.choice([True, False]) else False
            user_biz_history.append({
                "user_id": u["user_id"],
                "business_id": b["business_id"],
                "has_recent_order": random.choice([True, False, False]),
                "has_recent_booking": random.choice([True, False, False]),
                "has_recent_payment": random.choice([True, False, False]),
                "opt_in_status": opt_in,
                "opt_out_status": opt_out
            })

    with open(os.path.join(dataset_dir, "user_business_history.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=user_biz_history[0].keys())
        writer.writeheader()
        writer.writerows(user_biz_history)

    # 6. Images & Voice Notes metadata
    images = [
        {"image_id": "img_001", "file_path": "media/poster_sale.png", "ocr_text": "50% OFF FLASH SALE! Use code SAVE50", "image_description": "Promotional poster offering 50% discount"},
        {"image_id": "img_002", "file_path": "media/payment_qr.png", "ocr_text": "Scan UPI QR Code to pay maintenance bill Rs 2500", "image_description": "UPI Payment QR code screenshot for bill payment"},
        {"image_id": "img_003", "file_path": "media/event_invite.jpg", "ocr_text": "Annual Society Meeting Sunday 5 PM at Club House", "image_description": "Notice poster for upcoming society meeting"},
        {"image_id": "img_004", "file_path": "media/scam_winner.png", "ocr_text": "CONGRATULATIONS YOU WON 10 LAKHS! Click bit.ly/claim-prize now", "image_description": "Scam lottery winner screenshot with external link"},
    ]
    with open(os.path.join(dataset_dir, "images.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=images[0].keys())
        writer.writeheader()
        writer.writerows(images)

    voice_notes = [
        {"voice_note_id": "vn_001", "file_path": "media/voice_urgent.aac", "transcript": "Hey, please send me the project file urgently before 6 PM meeting.", "duration_seconds": 12},
        {"voice_note_id": "vn_002", "file_path": "media/voice_greeting.aac", "transcript": "Good morning family! Hope everyone has a blessed Sunday.", "duration_seconds": 25},
        {"voice_note_id": "vn_003", "file_path": "media/voice_scam.aac", "transcript": "Your bank account will be blocked today unless you call 9876543210 immediately.", "duration_seconds": 18},
    ]
    with open(os.path.join(dataset_dir, "voice_notes.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=voice_notes[0].keys())
        writer.writeheader()
        writer.writerows(voice_notes)

    # 7. Historical Messages & Events
    msg_history = []
    msg_events = []
    now = datetime.now()
    
    for h in range(1, 201):
        h_id = f"hist_msg_{h:04d}"
        u = random.choice(users)
        conv_type = random.choice(["personal", "group", "business"])
        g_id = random.choice(groups)["group_id"] if conv_type == "group" else ""
        b_id = random.choice(businesses)["business_id"] if conv_type == "business" else ""
        s_user = random.choice(users)["user_id"] if conv_type != "business" else ""
        cat = random.choice(["personal", "urgent", "event", "payment", "business_update", "promotion", "greeting", "forward", "spam", "scam"])
        
        created = (now - timedelta(days=random.randint(1, 30), hours=random.randint(1, 20))).isoformat()
        
        msg_history.append({
            "message_id": h_id,
            "user_id": u["user_id"],
            "sender_user_id": s_user,
            "business_id": b_id,
            "group_id": g_id,
            "created_at": created,
            "message_text": f"Historical message {h} for {cat} context",
            "media_type": "",
            "media_id": "",
            "category": cat
        })
        
        # Event reactions
        evt_type = random.choice(["opened", "replied", "dismissed", "muted", "reported"])
        msg_events.append({
            "message_id": h_id,
            "user_id": u["user_id"],
            "event_type": evt_type,
            "event_timestamp": (datetime.fromisoformat(created) + timedelta(minutes=random.randint(1, 120))).isoformat()
        })

    with open(os.path.join(dataset_dir, "message_history.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=msg_history[0].keys())
        writer.writeheader()
        writer.writerows(msg_history)

    with open(os.path.join(dataset_dir, "message_events.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=msg_events[0].keys())
        writer.writeheader()
        writer.writerows(msg_events)

    # 8. Daily Notification Summary
    daily_summaries = []
    for u in users[:30]:
        for d_offset in range(1, 8):
            d_str = (now - timedelta(days=d_offset)).strftime("%Y-%m-%d")
            recv = random.randint(20, 150)
            notif = int(recv * random.uniform(0.1, 0.3))
            dig = int(recv * random.uniform(0.2, 0.5))
            mut = recv - notif - dig
            daily_summaries.append({
                "user_id": u["user_id"],
                "date": d_str,
                "total_received": recv,
                "total_notified": notif,
                "total_digested": dig,
                "total_muted": mut
            })

    with open(os.path.join(dataset_dir, "daily_notification_summary.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=daily_summaries[0].keys())
        writer.writeheader()
        writer.writerows(daily_summaries)

    # 9. Incoming Messages (messages.csv) & Sample Messages (sample_messages.csv)
    sample_templates = [
        # (text, media_type, media_id, conv_type, is_scam, is_urgent, category, expected_action, reason, evidence_hist_idx)
        ("URGENT OTP: Your verification code is 948201. Do not share with anyone.", "", "", "personal", False, True, "urgent", "notify", "Critical time-sensitive security authentication OTP", 0),
        ("Hey @user_001, can you send the slide deck before 5pm meeting?", "", "", "group", False, True, "personal", "notify", "Direct user mention requiring urgent work item reply", 1),
        ("Your Swiggy order #84920 has been picked up by delivery partner.", "", "", "business", False, False, "business_update", "notify", "Active user order status update from verified business", 2),
        ("CONGRATULATIONS! You won $50,000 lottery! Click http://scam-win.xyz to claim now!", "", "", "personal", True, False, "scam", "mute", "Phishing link scam detected from unknown sender", 3),
        ("50% OFF Flash Sale on shoes! Use code SHOE50 today only!", "image", "img_001", "business", False, False, "promotion", "digest", "Marketing promo poster; added to daily digest", 4),
        ("Please pay monthly maintenance fee of Rs 2500 by 10th August.", "image", "img_002", "group", False, False, "payment", "digest", "Society bill payment reminder; routed to digest", 5),
        ("Voice Note Audio Message", "voice", "vn_001", "personal", False, True, "urgent", "notify", "Voice message requesting urgent project file transmission", 6),
        ("Your account will be suspended in 1 hour unless you verify details here: http://phish-bank.biz", "voice", "vn_003", "personal", True, False, "scam", "mute", "Fraudulent bank suspension voice scam", 7),
        ("Good morning everyone! Have a nice weekend!", "", "", "group", False, False, "greeting", "mute", "Low-priority routine group greeting", 8),
        ("Forwarded many times: Drink lemon tea to cure all viruses!", "", "", "group", False, False, "forward", "mute", "Highly forwarded unverified viral chain message", 9)
    ]

    incoming_messages = []
    sample_messages = []

    for i in range(1, 61):
        m_id = f"msg_{i:04d}"
        tpl = sample_templates[(i - 1) % len(sample_templates)]
        u_id = f"user_{(i % 50) + 1:03d}"
        conv_type = tpl[3]
        g_id = f"group_{((i % 10) + 1):03d}" if conv_type == "group" else ""
        b_id = f"biz_{((i % 8) + 1):03d}" if conv_type == "business" else ""
        s_user = f"user_{(((i + 5) % 50) + 1):03d}" if conv_type != "business" else ""
        created_at = (now - timedelta(minutes=i * 15)).isoformat()
        fwd_count = random.randint(5, 25) if tpl[6] == "forward" else random.randint(0, 1)

        row_dict = {
            "message_id": m_id,
            "user_id": u_id,
            "conversation_type": conv_type,
            "group_id": g_id,
            "business_id": b_id,
            "sender_user_id": s_user,
            "created_at": created_at,
            "message_text": tpl[0],
            "media_type": tpl[1],
            "media_id": tpl[2],
            "forwarded_count": fwd_count
        }
        incoming_messages.append(row_dict)

        if i <= 10:
            sample_row = dict(row_dict)
            sample_row.update({
                "action": tpl[7],
                "message_type": tpl[6],
                "reason": tpl[8],
                "confidence": round(random.uniform(0.88, 0.98), 2),
                "evidence_message_ids": f"hist_msg_{tpl[9]+1:04d}" if tpl[9] < len(msg_history) else "none"
            })
            sample_messages.append(sample_row)

    with open(messages_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=incoming_messages[0].keys())
        writer.writeheader()
        writer.writerows(incoming_messages)

    with open(os.path.join(dataset_dir, "sample_messages.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=sample_messages[0].keys())
        writer.writeheader()
        writer.writerows(sample_messages)

    # 10. Blank output.csv template
    with open(os.path.join(dataset_dir, "output.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["message_id", "action", "message_type", "reason", "confidence", "evidence_message_ids"])

    print(f"[Dataset] Successfully generated 12 dataset CSV files in '{dataset_dir}/'!")

if __name__ == "__main__":
    ensure_dataset_exists(force=True)
