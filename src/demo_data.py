import pandas as pd
from pathlib import Path

def generate_demo_bookings(count=8, start="2026-06-01"):
    """Generate demo bookings with fixed check-in at 16:00 and check-out at 12:00 noon."""
    base = pd.Timestamp(start)
    names = ["Li Ming", "Wang Wei", "Zhang Hui", "Chen Jie", "Liu Yang", "Zhao Lin", "Sun Yu", "Xu Ning"]
    rows = []
    for i in range(count):
        # Each stay starts 2 days apart at 16:00 (4 PM)
        checkin = base + pd.Timedelta(days=i * 2)
        checkin = checkin.replace(hour=16, minute=0, second=0)
        
        # Check-out at 12:00 noon the next day
        checkout = checkin + pd.Timedelta(days=1)
        checkout = checkout.replace(hour=12, minute=0, second=0)
        
        # Some guests may have earlier check-in (e.g., 14:00) or late check-out (e.g., 14:00)
        if i % 3 == 1:  # Earlier check-in
            checkin = checkin.replace(hour=14, minute=0, second=0)
        if i % 3 == 2:  # Late check-out
            checkout = checkout.replace(hour=14, minute=0, second=0)
        
        rows.append({
            "姓名": names[i % len(names)] + f" {i+1}",
            "入住时间": checkin.strftime("%Y-%m-%d %H:%M:%S"),
            "退房时间": checkout.strftime("%Y-%m-%d %H:%M:%S"),
            "电话号码": f"+485000000{i+1:02d}",
            "有无车库": "Yes" if i % 2 else "No",
        })
    return pd.DataFrame(rows)

def save_demo_csv(path):
    df = generate_demo_bookings()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return df