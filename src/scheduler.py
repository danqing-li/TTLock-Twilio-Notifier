def due_tasks(df, now):
    return {
        "whatsapp": df[df["whatsapp_send_at"] <= now].copy(),
        "sms": df[df["sms_send_at"] <= now].copy(),
    }

def dispatch_due(df, now, whatsapp_sender, sms_sender):
    due = due_tasks(df, now)
    results = []
    for _, row in due["whatsapp"].iterrows():
        results.append(whatsapp_sender.send(row["电话号码"], row["whatsapp_message"], row["whatsapp_send_at"]))
    for _, row in due["sms"].iterrows():
        results.append(sms_sender.send(row["电话号码"], row["sms_message"], row["sms_send_at"]))
    return results