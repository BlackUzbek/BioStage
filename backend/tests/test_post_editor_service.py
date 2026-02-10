from datetime import datetime

from backend.application.post_editor_service import PostEditorService
from backend.domain.schemas import ChannelDTO


def test_apply_hyperlink_bold() -> None:
    service = PostEditorService()
    channel = ChannelDTO(
        id=1,
        user_id=1,
        channel_id="-100123",
        link="https://example.com",
        style="bold",
        target_text="BioStage",
        is_active=True,
        created_at=datetime.now(),
    )

    result = service.apply("Welcome to BioStage community", channel)

    assert "<b><a href=\"https://example.com\">BioStage</a></b>" in result
