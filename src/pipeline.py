from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

from .demo_data import save_demo_csv
from .mock_builder import load_booking_csv, build_mock_records, save_mock_csv
from .ttlock_real_client import TTLockClient
from .twilio_sender import TwilioSender
from .notifier import build_whatsapp_message, build_sms_message, WhatsAppSenderMock, SMSSenderMock


def now_ms():
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def ensure_columns(df):
    required = [
        "姓名",
        "入住时间",
        "退房时间",
        "电话号码",
        "有无车库",
        "lockId",
        "keyId",
        "keyName",
        "startDate",
        "endDate",
        "keyboardPwdVersion",
        "keyboardPwd",
        "passcode",
        "ekey",
        "whatsapp_send_at",
        "sms_send_at",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")


def attach_messages(df):
    df = df.copy()
    df["whatsapp_message"] = df.apply(build_whatsapp_message, axis=1)
    df["sms_message"] = df.apply(build_sms_message, axis=1)
    return df


def attach_ttlock_real(df, ttlock_client: TTLockClient):
    df = df.copy()
    ekey_payloads = []
    passcode_payloads = []

    for _, row in df.iterrows():
        ekey_payload = ttlock_client.get_ekey(int(row["keyId"]))
        passcode_payload = ttlock_client.get_passcode(int(row["keyId"]))

        ekey_payloads.append(ekey_payload)
        passcode_payloads.append(passcode_payload)

    df["ekey_payload"] = ekey_payloads
    df["passcode_payload"] = passcode_payloads
    return df


def _normalize_value(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None
    return text


def create_ttlock_from_record(ttlock_client: TTLockClient, row):
    ekey_result = None
    ekey_value = _normalize_value(row.get("ekey"))
    if ekey_value:
        ekey_result = ttlock_client.create_ekey(
            lock_id=int(row["lockId"]),
            start_date=int(row["startDate"]),
            end_date=int(row["endDate"]),
            ekey=ekey_value,
            remarks=str(row.get("keyName", "")),
        )

    keyboard_pwd = _normalize_value(row.get("keyboardPwd")) or _normalize_value(row.get("passcode"))
    passcode_result = ttlock_client.create_passcode(
        lock_id=int(row["lockId"]),
        keyboard_pwd_name=str(row["keyName"]),
        keyboard_pwd=keyboard_pwd,
        start_date=int(row["startDate"]),
        end_date=int(row["endDate"]),
    )

    return {
        "ekey_result": ekey_result,
        "passcode_result": passcode_result,
    }


def sync_ttlock(df, use_real_ttlock=False):
    if not use_real_ttlock:
        return df

    client = TTLockClient.from_env()
    df = df.copy()

    ekey_results = []
    passcode_results = []

    for _, row in df.iterrows():
        try:
            result = create_ttlock_from_record(client, row)
            ekey_result = result["ekey_result"]
            passcode_result = result["passcode_result"]

            if ekey_result and isinstance(ekey_result, dict) and ekey_result.get("keyId"):
                ekey_result = client.get_ekey(int(ekey_result["keyId"]))

            if passcode_result and isinstance(passcode_result, dict) and passcode_result.get("keyboardPwdId"):
                passcode_result = client.get_passcode(int(passcode_result["keyboardPwdId"]))

        except Exception as e:
            ekey_result = None
            passcode_result = {"error": str(e), "姓名": row["姓名"]}

        ekey_results.append(ekey_result)
        passcode_results.append(passcode_result)

    df["ekey_result"] = ekey_results
    df["passcode_result"] = passcode_results
    return df


# def due_rows(df, current_dt=None):
#     if current_dt is None:
#         current_dt = pd.Timestamp.utcnow()
#     if not isinstance(current_dt, pd.Timestamp):
#         current_dt = pd.Timestamp(current_dt)

#     whatsapp_due = df[df["whatsapp_send_at"] <= current_dt].copy()
#     sms_due = df[df["sms_send_at"] <= current_dt].copy()
#     return whatsapp_due, sms_due

def due_rows(df, current_dt=None):
    if current_dt is None:
        current_dt = pd.Timestamp.now(tz="UTC")
    else:
        current_dt = pd.Timestamp(current_dt)
        if current_dt.tzinfo is None:
            current_dt = current_dt.tz_localize("UTC")
        else:
            current_dt = current_dt.tz_convert("UTC")

    df = df.copy()
    for col in ["whatsapp_send_at", "sms_send_at", "入住时间", "退房时间"]:
        df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")

    whatsapp_due = df[df["whatsapp_send_at"] <= current_dt].copy()
    sms_due = df[df["sms_send_at"] <= current_dt].copy()
    return whatsapp_due, sms_due

def send_notifications(df, use_real_twilio=False, current_dt=None):
    whatsapp_due, sms_due = due_rows(df, current_dt=current_dt)

    if use_real_twilio:
        sender = TwilioSender()
        whatsapp_sender = sender.send_whatsapp
        sms_sender = sender.send_sms
    else:
        whatsapp_mock = WhatsAppSenderMock()
        sms_mock = SMSSenderMock()
        whatsapp_sender = whatsapp_mock.send
        sms_sender = sms_mock.send

    results = []

    for _, row in whatsapp_due.iterrows():
        results.append(
            whatsapp_sender(
                row["电话号码"],
                row["whatsapp_message"],
                row["whatsapp_send_at"],
            )
        )

    for _, row in sms_due.iterrows():
        results.append(
            sms_sender(
                row["电话号码"],
                row["sms_message"],
                row["sms_send_at"],
            )
        )

    return results


def run_pipeline(
    data_dir="data",
    use_demo_csv=True,
    use_real_ttlock=False,
    use_real_twilio=False,
    current_dt=None,
):
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    demo_csv = data_dir / "booking_customers_demo.csv"
    mock_csv = data_dir / "booking_ttlock_message_mock.csv"

    if use_demo_csv or not demo_csv.exists():
        save_demo_csv(demo_csv)

    booking_df = load_booking_csv(demo_csv)
    mock_df = build_mock_records(booking_df)
    mock_df = attach_messages(mock_df)

    if use_real_ttlock:
        mock_df = sync_ttlock(mock_df, use_real_ttlock=True)

    save_mock_csv(mock_df, mock_csv)

    notification_results = send_notifications(
        mock_df,
        use_real_twilio=use_real_twilio,
        current_dt=current_dt,
    )
    print("The result of len(mock_df) is ", len(mock_df))
    return {
        "demo_csv": str(demo_csv),
        "mock_csv": str(mock_csv),
        "rows": len(mock_df),
        "notifications": notification_results,
    }


if __name__ == "__main__":
    # All mock, mock TTLock, mock Twilio
    # result = run_pipeline(
    #     data_dir="data",
    #     use_demo_csv=True,
    #     use_real_ttlock=False,
    #     use_real_twilio=False,
    # )
    # print(result)

    # Real TTLock, mock Twilio
    result = run_pipeline(
        data_dir="data",
        use_demo_csv=False,
        use_real_ttlock=True,
        use_real_twilio=False,
    )

    # # Real TTLock, real Twilio
    # result = run_pipeline(
    #     data_dir="data",
    #     use_demo_csv=False,
    #     use_real_ttlock=True,
    #     use_real_twilio=False,
    # )

    # # Real TTLock, real Twilio, with current_dt in the past to trigger notifications
    # result = run_pipeline(
    #     data_dir="data",
    #     use_demo_csv=False,
    #     use_real_ttlock=True,
    #     use_real_twilio=True,
    # )