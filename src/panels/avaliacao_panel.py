import discord

from src.config import LOGO_PATH
from src.utils.error_handling import LoggingViewMixin


class PainelAvaliacaoLayout(LoggingViewMixin, discord.ui.LayoutView):
    action_row = discord.ui.ActionRow()

    container = discord.ui.Container(
        discord.ui.Section(
            "# 📝 Avaliação de Recrutamento",
            (
                "Clique no botão abaixo para iniciar sua avaliação.\n\n"
                "Você terá **11 perguntas de múltipla escolha** e **1 hora** para concluir.\n"
                "⚠️ A avaliação só pode ser iniciada **uma única vez**."

            ),
            accessory=discord.ui.Thumbnail("attachment://logo.png"),
        ),
        discord.ui.Separator(spacing=discord.SeparatorSpacing.large),
        action_row,
        accent_color=discord.Color.gold(),
    )

    def __init__(self):
        super().__init__(timeout=None)

    @action_row.button(
        label="Iniciar Avaliação",
        style=discord.ButtonStyle.green,
        custom_id="painel:iniciar_avaliacao",
    )
    async def iniciar_avaliacao(self, interaction: discord.Interaction, button: discord.ui.Button):
        from src.services.avaliacao_service import iniciar_avaliacao
        await iniciar_avaliacao(interaction)


