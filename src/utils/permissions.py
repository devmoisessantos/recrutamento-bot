import discord
from discord import app_commands
from src.config import ADMIN_ROLE_NAMES


def is_authorized():
    """Permite o comando apenas para Administradores ou membros com um dos cargos configurados."""

    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.user.guild_permissions.administrator:
            return True

        member_role_names = {r.name for r in interaction.user.roles}
        if member_role_names.intersection(ADMIN_ROLE_NAMES):
            return True

        await interaction.response.send_message(
            "❌ Você não tem permissão para usar este comando. "
            "É necessário ser Administrador ou ter um dos cargos autorizados.",
            ephemeral=True,
        )
        return False

    return app_commands.check(predicate)
