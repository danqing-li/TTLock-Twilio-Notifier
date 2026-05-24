class TTLockMockClient:
    def __init__(self, lock_id=3215):
        self.lock_id = lock_id

    def create_ekey(self, record):
        return {
            "keyId": int(record["keyId"]),
            "lockId": int(record["lockId"]),
            "startDate": int(record["startDate"]),
            "endDate": int(record["endDate"]),
            "remarks": f"mock for {record['姓名']}",
            "keyRight": 1,
            "keyboardPwdVersion": int(record.get("keyboardPwdVersion", 4)),
            "remoteEnable": 1,
        }

    def create_passcode(self, record):
        return {
            "keyboardPwdId": int(record["keyId"]),
            "lockId": int(record["lockId"]),
            "keyboardPwd": str(record["keyboardPwd"]),
            "keyboardPwdName": f"pwd-{record['姓名']}",
            "keyboardPwdVersion": int(record.get("keyboardPwdVersion", 4)),
            "keyboardPwdType": 3,
            "startDate": int(record["startDate"]),
            "endDate": int(record["endDate"]),
            "isCustom": 1,
            "status": 1,
        }