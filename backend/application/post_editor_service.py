from backend.domain.schemas import SettingsDTO


class PostEditorService:
    @staticmethod
    def render_hyperlink(target_text: str, link: str, style: str) -> str:
        base = f'<a href="{link}">{target_text}</a>'
        if style == "bold":
            return f"<b>{base}</b>"
        if style == "italic":
            return f"<i>{base}</i>"
        return base

    def apply(self, text: str, settings: SettingsDTO) -> str:
        replacement = self.render_hyperlink(settings.target_text, settings.link, settings.style)
        return text.replace(settings.target_text, replacement, 1)
