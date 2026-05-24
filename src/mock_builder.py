import pandas as pd
from .config import LOCK_ID, BUFFER_BEFORE, BUFFER_AFTER, CHECKIN_NOTICE, SMS_NOTICE

def load_booking_csv(path):
    df = pd.read_csv(path)
    df["入住时间"] = pd.to_datetime(df["入住时间"])
    df["退房时间"] = pd.to_datetime(df["退房时间"])
    return df

def build_mock_records(df):
    rows = []
    for i, row in df.reset_index(drop=True).iterrows():
        ci = row["入住时间"]
        co = row["退房时间"]
        rows.append({
            "姓名": row["姓名"],
            "入住时间": ci,
            "退房时间": co,
            "电话号码": row["电话号码"],
            "有无车库": row["有无车库"],
            "lockId": LOCK_ID,
            "keyId": 1000 + i,
            "keyName": f"stay-{row['姓名']}",
            "startDate": int((ci - BUFFER_BEFORE).timestamp() * 1000),
            "endDate": int((co + BUFFER_AFTER).timestamp() * 1000),
            "keyboardPwdVersion": 4,
            "keyboardPwd": f"{100000 + i:06d}",
            "passcode": f"{80000000 + i:08d}",
            "ekey": f"ekey_{1000 + i}",
            "whatsapp_send_at": ci - CHECKIN_NOTICE,
            "sms_send_at": ci - SMS_NOTICE,
        })
    return pd.DataFrame(rows)

def save_mock_csv(df, path):
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return df