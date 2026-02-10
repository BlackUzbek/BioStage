from backend.application.auth_service import AuthService


def test_verify_admin_success() -> None:
    service = AuthService()
    assert service.verify_admin("admin", "admin123") is True
