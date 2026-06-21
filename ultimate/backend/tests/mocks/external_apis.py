import respx
from httpx import Response

def setup_meta_graph_mock(router: respx.MockRouter):
    """
    Mock interception layer utilizing 'respx'.
    Traps all outgoing HTTP calls to Meta's Graph API, explicitly returning predefined 
    success structures or heavy rate-limiting states to verify system stability 
    under massive scale without executing external networking overhead.
    """
    
    # 1. Trapping Success: Mocking a standard successful token exchange or lead extraction
    router.get(
        url__regex=r"https://graph\.facebook\.com/v[0-9.]+/oauth/access_token"
    ).mock(return_value=Response(200, json={"access_token": "mock_sys_token_9x1"}))

    # 2. Trapping Massive High-Traffic Spikes: Rate Limiting State Injection
    router.get(
        url__regex=r"https://graph\.facebook\.com/v[0-9.]+/.*rate_limit_simulation.*"
    ).mock(return_value=Response(429, json={
        "error": {
            "message": "Application request limit reached",
            "type": "OAuthException",
            "code": 4,
            "error_subcode": 3262000
        }
    }))
    
    # 3. Trapping Production Lead Structures: Standard Lead Gen Array format
    router.get(
        url__regex=r"https://graph\.facebook\.com/v[0-9.]+/.*"
    ).mock(return_value=Response(200, json={
        "data": [
            {
                "id": "ld_meta_10203",
                "field_data": [
                    {"name": "full_name", "values": ["Testing Mock"]},
                    {"name": "phone_number", "values": ["+971501112222"]}
                ]
            }
        ]
    }))

def setup_property_portal_mocks(router: respx.MockRouter):
    """
    Trap verification callbacks to regional UAE property portal APIs (if applicable).
    """
    router.post(
        url__regex=r"https://api\.propertyfinder\.ae/.*"
    ).mock(return_value=Response(202, json={"status": "Acknowledged"}))
