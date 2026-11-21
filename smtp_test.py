import smtplib
import sys
from email.message import EmailMessage
from email.utils import parseaddr

from vrn_processing.env_loader import get_env, load_env_file


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def main() -> int:
    load_env_file()
    sender_email = get_env("SENDER_EMAIL")
    sender_password = get_env("SENDER_PASSWORD")

    if not sender_email or not sender_password:
        print("Missing SENDER_EMAIL or SENDER_PASSWORD in the environment or .env file.")
        return 1

    recipient_input = input("Recipient email address: ").strip()
    _, recipient = parseaddr(recipient_input)
    if not recipient or recipient != recipient_input or any(char in recipient for char in ",;"):
        print("Enter exactly one valid recipient email address.")
        return 1

    message = EmailMessage()
    message["From"] = sender_email
    message["To"] = recipient
    message["Subject"] = "SMTP connection test"
    message.set_content("This is a test email to verify SMTP authentication and delivery.")

    stage = "connecting"
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=20) as server:
            stage = "starting TLS"
            server.starttls()
            server.ehlo()

            stage = "authenticating"
            server.login(sender_email, sender_password)
            print("SMTP authentication succeeded.")

            stage = "sending"
            server.send_message(message, from_addr=sender_email, to_addrs=[recipient])

        print(f"Test email sent to {recipient}.")
        return 0
    except smtplib.SMTPAuthenticationError as exc:
        print(f"SMTP authentication failed (code {exc.smtp_code}): {exc.smtp_error!r}")
    except smtplib.SMTPResponseException as exc:
        print(f"SMTP error while {stage} (code {exc.smtp_code}): {exc.smtp_error!r}")
    except (smtplib.SMTPException, OSError) as exc:
        print(f"SMTP error while {stage}: {exc}")

    return 1


if __name__ == "__main__":
    sys.exit(main())
