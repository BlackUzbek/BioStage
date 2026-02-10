from backend.application.post_editor_service import PostEditorService
from backend.domain.schemas import SettingsDTO


def test_apply_hyperlink_bold() -> None:
    service = PostEditorService()
    settings = SettingsDTO(link="https://example.com", style="bold", target_text="BioStage", channel_id="-100")

    result = service.apply("Welcome to BioStage community", settings)

    assert "<b><a href=\"https://example.com\">BioStage</a></b>" in result
