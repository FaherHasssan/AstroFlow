from app.schemas.lead import WebhookPayloadSchema

class LeadParserService:
    """
    Polymorphic parser engine explicitly crafted to intercept unstructured property lead formats
    (Property Finder, Bayut, Meta) and pipeline them through stringent Pydantic v2 validation constraints.
    """

    @staticmethod
    def parse_and_normalize(payload_source: str, raw_webhook: dict) -> dict:
        """
        Translates provider webhooks and enforces pristine international E.164 telephone configurations.
        Raises ValueError (via Pydantic) if the incoming payload is unsalvageable or missing mandatory telemetry keys.
        """
        
        # The Pydantic v2 execution layer instantly coerces types and triggers regex engine validations
        validated_schema = WebhookPayloadSchema(
            source=payload_source,
            raw_data=raw_webhook
        )
        
        return {
            "customer_name": validated_schema.customer_name or "Unknown Client",
            "target_phone_number": validated_schema.phone_number,
            "raw_webhook_payload": raw_webhook
        }
