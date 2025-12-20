import base64
import logging

import dkim
from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend

logger = logging.getLogger(__name__)


class DKIMEmailBackend(EmailBackend):
    def send_messages(self, email_messages):
        for message in email_messages:
            # Prepare DKIM headers
            dkim_selector = b"your_selector"  # Replace with your actual selector
            dkim_domain = b"barodybroject.com"  # Replace with your actual domain
            dkim_private_key_base64 = settings.DKIM_PRIVATE_KEY

            try:
                # Decode the base64 private key
                dkim_private_key_bytes = base64.b64decode(dkim_private_key_base64)
                dkim_private_key = (
                    b"-----BEGIN RSA PRIVATE KEY-----\n"
                    + dkim_private_key_bytes
                    + b"\n-----END RSA PRIVATE KEY-----"
                )

                # Sign the email
                signature = dkim.sign(
                    message=message.message().as_bytes(),
                    selector=dkim_selector,
                    domain=dkim_domain,
                    privkey=dkim_private_key,
                    include_headers=[
                        b"from",
                        b"to",
                        b"subject",
                        b"date",
                        b"message-id",
                    ],
                )

                # Add signature to the email headers
                signature_value = signature[len("DKIM-Signature: ") :].decode()
                # Remove all types of newlines and excessive whitespace
                signature_value = "".join(signature_value.splitlines())
                message.extra_headers["DKIM-Signature"] = signature_value
            except Exception as e:
                logger.warning("DKIM signing failed: %s", e)
        return super().send_messages(email_messages)
