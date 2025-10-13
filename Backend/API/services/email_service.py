import os
from typing import Optional

from azure.communication.email import EmailClient


AZURE_EMAIL_CONNECTION_STRING = os.getenv("AZURE_COMMUNICATION_EMAIL_CONNECTION_STRING", "")
AZURE_EMAIL_SENDER = os.getenv("AZURE_EMAIL_SENDER", "")


def _get_client() -> Optional[EmailClient]:
    if not AZURE_EMAIL_CONNECTION_STRING:
        return None
    try:
        return EmailClient.from_connection_string(AZURE_EMAIL_CONNECTION_STRING)
    except Exception:
        return None


def send_unlock_email(to_address: str, unlock_url: str) -> bool:
    """Send an account unlock email with Azure Communication Services.

    Returns True if the email was sent (or at least enqueued) successfully, False otherwise.
    """
    client = _get_client()
    if client is None or not AZURE_EMAIL_SENDER:
        # Email not configured; treat as no-op success to avoid blocking the flow in dev
        return False

    subject = "Desbloqueo de cuenta - XNFL Fantasy"
    plain_text = (
        "Has solicitado desbloquear tu cuenta. "
        f"Haz clic en el siguiente enlace para continuar: {unlock_url}\n\n"
        
        "Si no realizaste esta solicitud, puedes ignorar este mensaje."
    )
    html = f"""
    <html>
      <body>
        <p>Has solicitado <strong>desbloquear tu cuenta</strong>.</p>
        <p>Pulsa el siguiente botón para activar tu cuenta nuevamente:</p>
        <p>
          <a href="{unlock_url}" style="display:inline-block;padding:10px 16px;background:#2563eb;color:#fff;border-radius:6px;text-decoration:none">
            Desbloquear cuenta
          </a>
        </p>
        <p>Este link es válido por los próximos 5 minutos. \n"
        <p>Si no realizaste esta solicitud, puedes ignorar este mensaje.</p>
      </body>
    </html>
    """

    message = {
        "content": {
            "subject": subject,
            "plainText": plain_text,
            "html": html,
        },
        "recipients": {
            "to": [
                {"address": to_address},
            ]
        },
        "senderAddress": AZURE_EMAIL_SENDER,
    }

    try:
        poller = client.begin_send(message)
        _ = poller.result()  # wait for send completion
        return True
    except Exception:
        # Swallow and report failure; upstream may still report generic success
        return False
