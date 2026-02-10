from backend.domain.schemas import ChannelDTO


class PostEditorService:
    @staticmethod
    def render_hyperlink(target_text: str, link: str, style: str) -> str:
        base = f'<a href="{link}">{target_text}</a>'
        if style == "bold":
            return f"<b>{base}</b>"
        if style == "italic":
            return f"<i>{base}</i>"
        return base

    def apply(self, text: str, channel: ChannelDTO) -> str:
        replacement = self.render_hyperlink(channel.target_text, channel.link, channel.style)
        return text.replace(channel.target_text, replacement, 1)
