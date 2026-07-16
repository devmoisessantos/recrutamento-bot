import discord
import traceback

from src.config import CANAIS


class LoggingViewMixin:
    async def on_error(self, interaction: discord.Interaction, error: Exception, item):
        guild = interaction.guild
        canal = guild.get_channel(CANAIS["LOG_ERROS"]) if guild else None

        tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        tb_curto = tb[-1200:]  # evita passar do limite de caracteres do Discord

        mensagem = (
            f"⚠️ **Erro em componente**\n"
            f"Usuário: {interaction.user.mention} (`{interaction.user.id}`)\n"
            f"Componente: `{item.__class__.__name__}`\n"
            f"Erro: `{error}`\n"
            f"```py\n{tb_curto}\n```"
        )

        if canal:
            await canal.send(mensagem)

        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Ocorreu um erro inesperado. A equipe foi notificada.", ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "❌ Ocorreu um erro inesperado. A equipe foi notificada.", ephemeral=True
                )
        except discord.HTTPException:
            pass  # interação pode já ter expirado

class LoggingModalMixin:
    async def on_error(self, interaction: discord.Interaction, error: Exception):
        guild = interaction.guild
        canal = guild.get_channel(CANAIS["LOG_ERROS"]) if guild else None
        tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))[-1200:]

        if canal:
            await canal.send(
                f"⚠️ **Erro em Modal**\n"
                f"Modal: `{self.__class__.__name__}`\n"
                f"Usuário: {interaction.user.mention}\n"
                f"```py\n{tb}\n```"
            )

        if not interaction.response.is_done():
            await interaction.response.send_message("❌ Erro inesperado. A equipe foi notificada.", ephemeral=True)