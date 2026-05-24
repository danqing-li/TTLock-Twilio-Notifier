from pathlib import Path
from .demo_data import save_demo_csv
from .mock_builder import load_booking_csv, build_mock_records, save_mock_csv
from .ttlock_client import TTLockMockClient
from .notifier import build_whatsapp_message, build_sms_message

def run_pipeline(data_dir="data"):
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    demo_path = data_dir / "booking_customers_demo.csv"
    mock_path = data_dir / "booking_ttlock_message_mock.csv"
    demo_df = save_demo_csv(demo_path)
    booking_df = load_booking_csv(demo_path)
    mock_df = build_mock_records(booking_df)
    client = TTLockMockClient()
    mock_df["ekey_payload"] = mock_df.apply(lambda r: client.create_ekey(r), axis=1)
    mock_df["passcode_payload"] = mock_df.apply(lambda r: client.create_passcode(r), axis=1)
    mock_df["whatsapp_message"] = mock_df.apply(build_whatsapp_message, axis=1)
    mock_df["sms_message"] = mock_df.apply(build_sms_message, axis=1)
    save_mock_csv(mock_df, mock_path)
    return demo_df, mock_df

if __name__ == "__main__":
    run_pipeline()