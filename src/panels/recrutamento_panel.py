import discord
from src.config import LOGO_PATH
from src.panels.selecionar_candidato import SelecionarCandidatoView

class PainelRecrutamentoLayout(discord.ui.LayoutView):
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

class PainelRecrutamentoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # timeout=None = view persistente, nunca expira

    @discord.ui.button(
        label="Iniciar Recrutamento", 
        style=discord.ButtonStyle.green, 
        custom_id="painel:iniciar_recrutamento"
    )

    @discord.ui.button(
        label="Liberar Prova", 
        style=discord.ButtonStyle.blurple, 
        custom_id="painel:liberar_prova"
    )
    async def liberar_prova(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Use `/liberar-prova @membro`.", ephemeral=True
        )

    @discord.ui.button(label="Aprovar", style=discord.ButtonStyle.success, custom_id="painel:aprovar")
    async def aprovar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Use `/aprovar @membro`.", ephemeral=True
        )

    @discord.ui.button(label="Reprovar", style=discord.ButtonStyle.danger, custom_id="painel:reprovar")
    async def reprovar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Use `/reprovar @membro`.", ephemeral=True
        )
