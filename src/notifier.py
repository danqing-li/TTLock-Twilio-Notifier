def build_whatsapp_message(row):
    return (
        f"你好 {row['姓名']}，你的入住时间是 {row['入住时间']:%Y-%m-%d %H:%M}。"
        f" 车库：{row['有无车库']}。"
        f" 门锁码将于入住前生效。"
    )

def build_sms_message(row):
    return (
        f"{row['姓名']}，提醒你将于 {row['入住时间']:%Y-%m-%d %H:%M} 入住。"
        f" 门锁码：{row['keyboardPwd']}。"
    )

class WhatsAppSenderMock:
    def send(self, to, message, send_at):
        return {"channel": "whatsapp", "to": to, "send_at": send_at, "message": message, "status": "queued"}

class SMSSenderMock:
    def send(self, to, message, send_at):
        return {"channel": "sms", "to": to, "send_at": send_at, "message": message, "status": "queued"}