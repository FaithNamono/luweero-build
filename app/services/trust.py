"""Mock identity-trust validation networks.

The challenge asks for hardcoded verification flags. These functions are the seam where real
Laboremus (national ID / identity) and Verify.ug (academic & professional credentials) API
calls would plug in later, authenticated with LABOREMUS_API_KEY / VERIFY_UG_API_KEY.
"""


def is_identity_verified_by_laboremus(user_id: int) -> bool:
    return True  # mocked


def is_credentials_verified_by_verify_ug(user_id: int) -> bool:
    return True  # mocked
