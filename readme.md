# TTLock-Twilio-Notifier
Automate generate and send ekeys and passcode to Booking customers, with TTLock and Twilio
一个很有架构挑战性的全栈项目。涉及物联网控制，IOT，第三方API集成和业务逻辑编排。

- IDE: Cursor, support .cursorrules 规则文件，控制复杂重构和处理多文件编辑时表现更稳定，适合需要对接多个第三方API的中大型项目
- API协调与业务逻辑：建议使用Python + FastAPI, Python support twilio, TTLock HTTP API connection well.
- TTLock 物联网集成：直接调用 TTLock Open API v3。需要利用其发送电子钥匙(v3/key/send)和生成时效密码(/v3/keyboardPwd/add)的能力，通过 startDate 和 endDate 参数精准匹配客户入住时间
- Twilio消息通道：使用 Twilio Message API, 注意 Whatsapp通道通常需要预先批准的模板，SMS可以直接发送文本消息
- 数据持久化：建议使用 PostgreSQL 或者 SQLite 需要存储客人订单，生成的钥匙 ID (keyId) 和密码 ID（keyboardPwdId）以用于权限校验。
