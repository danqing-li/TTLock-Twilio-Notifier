import pandas as pd
from pathlib import Path

def generate_demo_bookings(count=8, start="2026-06-01 15:00:00"):
    base = pd.Timestamp(start)
    names = ["Li Ming", "Wang Wei", "Zhang Hui", "Chen Jie", "Liu Yang", "Zhao Lin", "Sun Yu", "Xu Ning"]
    rows = []
    for i in range(count):
        checkin = base + pd.Timedelta(days=i * 2, hours=i % 3)
        checkout = checkin + pd.Timedelta(days=2 + i % 3)
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