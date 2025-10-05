"""Email notification service"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from models import SmtpConfig, db
from security import decrypt_password


def get_smtp_config():
    """Get SMTP configuration from database"""
    config = SmtpConfig.query.first()
    return config


def send_email(to_email, subject, html_body):
    """
    Send email using SMTP configuration from database

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_body: HTML body content

    Returns:
        tuple: (success: bool, message: str)
    """
    # Get SMTP config from database
    smtp_config = get_smtp_config()

    if not smtp_config or not smtp_config.server:
        print("⚠️  SMTP not configured - email not sent")
        return False, "SMTP not configured"

    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = smtp_config.email_from
        msg['To'] = to_email
        msg['Subject'] = subject

        # Attach HTML body
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)

        # Connect to SMTP server
        if smtp_config.use_ssl:
            server = smtplib.SMTP(smtp_config.server, smtp_config.port)
            server.starttls()
        else:
            server = smtplib.SMTP(smtp_config.server, smtp_config.port)

        # Login if credentials provided
        if smtp_config.login and smtp_config.password:
            # Decrypt password before using
            decrypted_password = decrypt_password(smtp_config.password)
            if not decrypted_password:
                raise Exception("Failed to decrypt SMTP password")
            server.login(smtp_config.login, decrypted_password)

        # Send email
        server.send_message(msg)
        server.quit()

        print(f"✅ Email sent to {to_email}")
        return True, "Email sent successfully"

    except Exception as e:
        error_msg = f"Failed to send email: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg


def send_new_request_email(manager_email, employee_name, request_data):
    """
    Send email to manager about new request

    Args:
        manager_email: Manager's email address
        employee_name: Employee's full name
        request_data: Dictionary with request details (date, time_out, time_return, reason)

    Returns:
        tuple: (success: bool, message: str)
    """
    subject = f"Nowy wniosek od {employee_name}"

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 20px; padding: 40px; box-shadow: 0 10px 40px rgba(0,0,0,0.1);">
            <h2 style="color: #1e293b; margin-bottom: 30px; font-size: 24px;">Nowy wniosek o wyjście</h2>

            <div style="background: #f8fafc; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
                <p style="margin: 10px 0; color: #475569;"><strong style="color: #1e293b;">Pracownik:</strong> {employee_name}</p>
                <p style="margin: 10px 0; color: #475569;"><strong style="color: #1e293b;">Data:</strong> {request_data['date']}</p>
                <p style="margin: 10px 0; color: #475569;"><strong style="color: #1e293b;">Wyjście:</strong> {request_data['time_out']}</p>
                <p style="margin: 10px 0; color: #475569;"><strong style="color: #1e293b;">Powrót:</strong> {request_data['time_return']}</p>
            </div>

            <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; border-radius: 8px; margin-bottom: 30px;">
                <p style="margin: 0; color: #78350f;"><strong>Powód:</strong> {request_data['reason']}</p>
            </div>

            <p style="margin-top: 30px; text-align: center;">
                <a href="http://localhost:5000"
                   style="display: inline-block; padding: 12px 24px; background: linear-gradient(to right, #667eea, #764ba2); color: white; text-decoration: none; border-radius: 8px; font-weight: bold;">
                    Przejdź do aplikacji
                </a>
            </p>

            <p style="margin-top: 30px; text-align: center; color: #94a3b8; font-size: 12px;">
                TimeOff Manager - System zarządzania wnioskami
            </p>
        </div>
    </body>
    </html>
    """

    return send_email(manager_email, subject, html)


def send_decision_email(employee_email, employee_name, request_data, decision, comment=None):
    """
    Send email to employee about manager's decision

    Args:
        employee_email: Employee's email address
        employee_name: Employee's full name
        request_data: Dictionary with request details
        decision: 'zaakceptowany' or 'odrzucony'
        comment: Optional manager comment (required for rejection)

    Returns:
        tuple: (success: bool, message: str)
    """
    if decision == 'zaakceptowany':
        subject = f"✅ Wniosek zaakceptowany - {request_data['date']}"
        color = "#10b981"
        emoji = "✅"
        message = "Twój wniosek został zaakceptowany."
        bg_color = "#d1fae5"
    else:
        subject = f"❌ Wniosek odrzucony - {request_data['date']}"
        color = "#ef4444"
        emoji = "❌"
        message = "Twój wniosek został odrzucony."
        bg_color = "#fee2e2"

    comment_section = ""
    if comment:
        comment_section = f"""
        <div style="background: {bg_color}; border-left: 4px solid {color}; padding: 15px; border-radius: 8px; margin-top: 20px;">
            <p style="margin: 0; color: #1e293b;"><strong>Komentarz managera:</strong> {comment}</p>
        </div>
        """

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 20px; padding: 40px; box-shadow: 0 10px 40px rgba(0,0,0,0.1);">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: {color}; font-size: 48px; margin: 0;">{emoji}</h1>
                <h2 style="color: #1e293b; margin: 10px 0; text-transform: uppercase; font-size: 20px;">Wniosek {decision}</h2>
            </div>

            <div style="background: #f8fafc; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
                <p style="margin: 10px 0; color: #475569;"><strong style="color: #1e293b;">Pracownik:</strong> {employee_name}</p>
                <p style="margin: 10px 0; color: #475569;"><strong style="color: #1e293b;">Data:</strong> {request_data['date']}</p>
                <p style="margin: 10px 0; color: #475569;"><strong style="color: #1e293b;">Wyjście:</strong> {request_data['time_out']}</p>
                <p style="margin: 10px 0; color: #475569;"><strong style="color: #1e293b;">Powrót:</strong> {request_data['time_return']}</p>
            </div>

            {comment_section}

            <p style="margin-top: 30px; text-align: center; color: #94a3b8; font-size: 12px;">
                TimeOff Manager - System zarządzania wnioskami
            </p>
        </div>
    </body>
    </html>
    """

    return send_email(employee_email, subject, html)
