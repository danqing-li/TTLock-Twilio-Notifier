from src.demo_data import generate_demo_bookings
from src.mock_builder import build_mock_records
from src.ttlock_client import TTLockMockClient
from src.notifier import build_whatsapp_message, build_sms_message
from src.scheduler import due_tasks
import pandas as pd

def test_demo_rows():
    df = generate_demo_bookings(3)
    assert len(df) == 3
    assert list(df.columns) == ["姓名", "入住时间", "退房时间", "电话号码", "有无车库"]

def test_mock_fields():
    df = generate_demo_bookings(2)
    df["入住时间"] = pd.to_datetime(df["入住时间"])
    df["退房时间"] = pd.to_datetime(df["退房时间"])
    mock = build_mock_records(df)
    for col in ["startDate", "endDate", "keyboardPwd", "passcode", "whatsapp_send_at", "sms_send_at"]:
        assert col in mock.columns

def test_ttlock_mock():
    df = generate_demo_bookings(1)
    df["入住时间"] = pd.to_datetime(df["入住时间"])
    df["退房时间"] = pd.to_datetime(df["退房时间"])
    row = build_mock_records(df).iloc[0]
    client = TTLockMockClient()
    ekey = client.create_ekey(row)
    pwd = client.create_passcode(row)
    assert ekey["lockId"] == 3215
    assert pwd["keyboardPwd"] == row["keyboardPwd"]

def test_messages_and_schedule():
    df = generate_demo_bookings(1)
    df["入住时间"] = pd.to_datetime(df["入住时间"])
    df["退房时间"] = pd.to_datetime(df["退房时间"])
    mock = build_mock_records(df)
    mock["whatsapp_message"] = mock.apply(build_whatsapp_message, axis=1)
    mock["sms_message"] = mock.apply(build_sms_message, axis=1)
    now = mock.iloc[0]["sms_send_at"] + pd.Timedelta(minutes=1)
    due = due_tasks(mock, now)
    assert len(due["sms"]) == 1
    assert len(due["whatsapp"]) == 1