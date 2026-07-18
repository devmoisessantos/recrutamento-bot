import discord
from src.config import LOGO_PATH
from src.panels.selecionar_candidato import SelecionarCandidatoView
from src.utils.error_handling import LoggingViewMixin
class PainelRecrutamentoLayout(LoggingViewMixin, discord.ui.LayoutView):
    action_row = discord.ui.ActionRow()

    container = discord.ui.Container(
        # ────────────────────────────────────────────────
        # Section (Título + descrição + Thumbnail)
        # ────────────────────────────────────────────────
        discord.ui.Section(
            "# 📋 Painel de Recrutamento",
            (
                "Este painel é destinado exclusivamente aos recrutadores autorizados.\n\n"
                "Ao iniciar o processo, o sistema registrará automaticamente todas as alterações "
                "de cargos e manterá o histórico do candidato."
            ),
            accessory=discord.ui.Thumbnail("attachment://logo.png"),
        ),

        # ────────────────────────────────────────────────
        # Separator
        # ────────────────────────────────────────────────
        discord.ui.Separator(
            spacing=discord.SeparatorSpacing.large
        ),

        # ────────────────────────────────────────────────
        # TextDisplay
        # ────────────────────────────────────────────────
        discord.ui.TextDisplay(
            "## 📌 Antes de iniciar\n\n"
            "✅ O candidato deve possuir o cargo **Visitante**.\n"
            "✅ A WhiteList deve estar aprovada.\n"
            "✅ Tenha o **ID do Discord** do candidato em mãos.\n"
            "✅ Certifique-se de que o candidato está presente na call de recrutamento."
        ),

        # ────────────────────────────────────────────────
        # Separator
        # ────────────────────────────────────────────────
        discord.ui.Separator(
            spacing=discord.SeparatorSpacing.large
        ),

        # ────────────────────────────────────────────────
        # ActionRow
        # ────────────────────────────────────────────────
        action_row,

        # ────────────────────────────────────────────────
        # MediaGallery
        # ────────────────────────────────────────────────
        # discord.ui.MediaGallery(
        #     discord.MediaGalleryItem(
        #        media="attachment://banner.png"
        #    )
        # ),

        accent_color=discord.Color.brand_red(),
    )


    def __init__(self):
        super().__init__(timeout=None)  # persistente

    @action_row.button(
        label="Iniciar Recrutamento",
        style=discord.ButtonStyle.success,
        emoji="📋",
        custom_id="painel:iniciar_recrutamento",
    )

    async def iniciar_recrutamento(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Selecione o candidato:",
            view=SelecionarCandidatoView(recrutador=interaction.user),
            ephemeral=True,
        )

    @action_row.button(
        label="Liberar Avaliação",
        style=discord.ButtonStyle.danger,
        emoji="🔓",
        custom_id="painel:liberar_avaliacao",
    )
    async def liberar_avaliacao(self, interaction: discord.Interaction, button: discord.ui.Button):
        from src.services.liberacao_service import liberar_avaliacao_click
        await liberar_avaliacao_click(interaction)