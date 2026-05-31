import hashlib
import hmac
import datetime
from typing import Dict


class AWSAuth:
    @staticmethod
    def sign(
        method: str,
        uri: str,
        headers: Dict[str, str],
        body: str,
        access_key: str,
        secret_key: str,
        region: str,
        service: str,
    ) -> Dict[str, str]:
        now = datetime.datetime.utcnow()
        amz_date = now.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = now.strftime("%Y%m%d")

        headers["host"] = headers.get("host", "")
        headers["x-amz-date"] = amz_date

        sorted_h = sorted((k.lower(), v.strip()) for k, v in headers.items())
        canonical_headers = "".join(f"{k}:{v}\n" for k, v in sorted_h)
        signed_headers = ";".join(k for k, v in sorted_h)

        payload_hash = hashlib.sha256(body.encode()).hexdigest()
        canonical_request = "\n".join(
            [method.upper(), uri, "", canonical_headers, signed_headers, payload_hash]
        )

        credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
        string_to_sign = (
            f"AWS4-HMAC-SHA256\n{amz_date}\n{credential_scope}\n"
            f"{hashlib.sha256(canonical_request.encode()).hexdigest()}"
        )

        def _sign(key, msg):
            return hmac.new(key, msg.encode(), hashlib.sha256).digest()

        k_date = _sign(("AWS4" + secret_key).encode(), date_stamp)
        k_region = _sign(k_date, region)
        k_service = _sign(k_region, service)
        k_signing = _sign(k_service, "aws4_request")
        signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()

        headers["Authorization"] = (
            f"AWS4-HMAC-SHA256 Credential={access_key}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, Signature={signature}"
        )
        return headers
