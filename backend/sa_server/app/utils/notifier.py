import smtplib
from email.message import EmailMessage

async def send_email_notification(subject: str, content: str):
    """
    发送邮件通知
    """
    print("📧 发送邮件通知")
    sender = "your_email@example.com"
    recipient = "admin@example.com"
    password = "your_email_password"

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(content)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
    except Exception as e:
        print(f"❌ 发送邮件通知失败：{e}")