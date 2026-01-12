"""
邮件发送工具
支持 Resend API 和 SMTP
"""
import smtplib
import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, html_body: str):
    """发送邮件
    
    优先使用 Resend API，如果未配置则使用 SMTP
    """
    # 从环境变量获取配置
    resend_api_key = os.getenv("RESEND_API_KEY", "")
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("DEFAULT_EMAIL_ACCOUNT") or os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("DEFAULT_EMAIL_PASSWORD") or os.getenv("SMTP_PASSWORD", "")
    from_email = os.getenv("FROM_EMAIL", smtp_user or "noreply@travelgpt.com")
    
    last_error = None
    
    # 尝试使用 Resend API
    if resend_api_key and resend_api_key != "":
        try:
            import resend
            resend.api_key = resend_api_key
            
            params = {
                "from": from_email,
                "to": [to_email],
                "subject": subject,
                "html": html_body
            }
            
            resend.Emails.send(params)
            logger.info(f"Email sent via Resend to {to_email}")
            return
            
        except Exception as e:
            logger.error(f"Resend email failed: {str(e)}")
            last_error = e
            # 继续尝试 SMTP
    
    # 使用 SMTP
    if smtp_host and smtp_user and smtp_password:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = smtp_user
            msg['To'] = to_email
            
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 根据端口选择 SSL 或 TLS
            if smtp_port == 465:
                # 使用 SSL 连接
                server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30)
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
                server.quit()
            else:
                # 使用 TLS 连接
                with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_password)
                    server.send_message(msg)
            
            logger.info(f"Email sent via SMTP to {to_email} (from {smtp_user})")
            return
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP认证失败: {str(e)}\n提示：Gmail用户需要使用'应用专用密码'而不是普通密码"
            logger.error(error_msg)
            raise ValueError(error_msg) from e
        except (smtplib.SMTPConnectError, ConnectionError, TimeoutError) as e:
            error_msg = f"SMTP连接失败: {str(e)}\n提示：请检查网络连接、防火墙设置和SMTP服务器地址"
            logger.error(error_msg)
            raise ValueError(error_msg) from e
        except Exception as e:
            last_error = e
            error_msg = f"SMTP邮件发送失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e
    
    # 未配置邮件服务
    error_msg = "未配置邮件服务。请配置以下之一：\n1. RESEND_API_KEY\n2. SMTP_HOST + DEFAULT_EMAIL_ACCOUNT + DEFAULT_EMAIL_PASSWORD"
    logger.error(error_msg)
    if last_error:
        raise Exception(f"{error_msg}\n最后尝试的错误: {str(last_error)}") from last_error
    else:
        raise ValueError(error_msg)
