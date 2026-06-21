from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
import re

class WebhookPayloadSchema(BaseModel):
    """
    Robust Pydantic v2 data verification schema.
    Polymorphically absorbs untyped raw dictionaries and normalizes them.
    """
    source: str = Field(..., description="Lead origin identifier: propertyfinder, bayut, or meta")
    raw_data: Dict[str, Any] = Field(..., description="Unstructured webhook payload from the provider")
    
    # Standardized extraction fields (calculated post-validation)
    customer_name: Optional[str] = None
    phone_number: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def extract_polymorphic_fields(cls, data: Any) -> Any:
        """
        Translates heavily fragmented property portal inputs into normalized attributes.
        """
        if isinstance(data, dict):
            raw = data.get('raw_data', {})
            source = str(data.get('source', '')).lower()
            
            if source == "propertyfinder":
                data['customer_name'] = raw.get('client', {}).get('name')
                data['phone_number'] = raw.get('client', {}).get('phone')
            elif source == "bayut":
                data['customer_name'] = raw.get('CustomerName')
                data['phone_number'] = raw.get('CustomerPhone')
            elif source == "meta":
                field_data = raw.get('field_data', [])
                for field in field_data:
                    if field.get('name') == 'full_name':
                        data['customer_name'] = field.get('values', [None])[0]
                    if field.get('name') == 'phone_number':
                        data['phone_number'] = field.get('values', [None])[0]
                        
        return data

    @field_validator('phone_number')
    @classmethod
    def normalize_uae_cellular(cls, v: Optional[str]) -> str:
        """
        Specifically optimized regex engine for UAE cellular standardizations.
        Forces pristine international E.164 formats on input.
        """
        if not v:
            raise ValueError("Phone number is structurally required by the schema.")
        
        # Strip absolutely all non-numeric chars
        cleaned = re.sub(r'\D', '', v)
        
        # UAE Formats: Convert local strings uniformly to international 9715x
        if re.match(r'^05\d{8}$', cleaned):
            return f"+971{cleaned[1:]}"
        elif re.match(r'^5\d{8}$', cleaned):
            return f"+971{cleaned}"
        elif re.match(r'^9715\d{8}$', cleaned):
            return f"+{cleaned}"
        elif re.match(r'^009715\d{8}$', cleaned):
            return f"+{cleaned[2:]}"
        
        # Fallback to appending '+' assuming it's a valid international dial string
        return f"+{cleaned}"
