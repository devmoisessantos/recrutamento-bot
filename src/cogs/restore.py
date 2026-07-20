import discord
from discord import app_commands
from discord.ext import commands

import config
from core.backup_manager import BackupManager
from core.restore_manager import RestoreManager
from core.logger import BackupLogger
from utils.permissions import is_authorized
from utils.views import ConfirmView


class RestoreCog(commands.Cog):
    restore_group = app_commands.Group(
        name="restore", description="Restaurar estrutura do servidor a partir de um backup"
    )

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bm = BackupManager()
        self.rm = RestoreManager()
        self.logger = BackupLogger(config.LOG_CHANNEL_NAME)

    async def _load_target_backup(self, interaction: discord.Interaction, arquivo: str):
        filename = arquivo or self.bm.latest_backup_filename(interaction.guild.id)
        if not filename:
            return None, None
        backup = self.bm.load_backup(interaction.guild.id, filename)
        return backup, filename

    async def _confirm(self, interaction: discord.Interaction, texto: str) -> bool:
        view = ConfirmView(author_id=interaction.user.id, timeout=config.CONFIRMATION_TIMEOUT)
        await interaction.followup.send(texto, view=view, ephemeral=True)
        await view.wait()
        return bool(view.value)

    def _safety_backup(self, guild: discord.Guild, author: str):
        backup = self.bm.create_backup(guild, created_by=f"Auto (antes de restore por {author})")
        self.bm.save_backup(backup)

    @restore_group.command(name="cargos", description="Restaura apenas os cargos do backup")
    @app_commands.describe(arquivo="Nome do arquivo de backup (deixe vazio para usar o mais recente)")
    @is_authorized()
    async def cargos(self, interaction: discord.Interaction, arquivo: str = None):
        await interaction.response.defer(thinking=True, ephemeral=True)
        backup, filename = await self._load_target_backup(interaction, arquivo)
        if not backup:
            await interaction.followup.send("Nenhum backup encontrado.")
            return

        preview = await self.rm.restore_roles(interaction.guild, backup, dry_run=True)
        texto = f"**Prévia da restauração de cargos** (`{filename}`):\n" + "\n".join(preview[:15])
        if not await self._confirm(interaction, texto):
            return

        self._safety_backup(interaction.guild, str(interaction.user))
        report = await self.rm.restore_roles(interaction.guild, backup, dry_run=False)

        await interaction.followup.send("✅ Cargos restaurados. Veja detalhes no canal de logs.", ephemeral=True)
        await self.logger.log(
            interaction.guild, "🛡️ Restauração de cargos", "\n".join(report),
            discord.Color.gold(), author=str(interaction.user),
        )

    @restore_group.command(name="canais", description="Restaura categorias e canais do backup")
    @app_commands.describe(arquivo="Nome do arquivo de backup (deixe vazio para usar o mais recente)")
    @is_authorized()
    async def canais(self, interaction: discord.Interaction, arquivo: str = None):
        await interaction.response.defer(thinking=True, ephemeral=True)
        backup, filename = await self._load_target_backup(interaction, arquivo)
        if not backup:
            await interaction.followup.send("Nenhum backup encontrado.")
            return

        preview_cat = await self.rm.restore_categories(interaction.guild, backup, dry_run=True)
        preview_ch = await self.rm.restore_channels(interaction.guild, backup, dry_run=True)
        texto = f"**Prévia** (`{filename}`):\n" + "\n".join((preview_cat + preview_ch)[:15])
        if not await self._confirm(interaction, texto):
            return

        self._safety_backup(interaction.guild, str(interaction.user))
        report_cat = await self.rm.restore_categories(interaction.guild, backup, dry_run=False)
        report_ch = await self.rm.restore_channels(interaction.guild, backup, dry_run=False)
        full_report = report_cat + report_ch

        await interaction.followup.send("✅ Canais/categorias restaurados. Veja detalhes no canal de logs.", ephemeral=True)
        await self.logger.log(
            interaction.guild, "🛡️ Restauração de canais", "\n".join(full_report),
            discord.Color.gold(), author=str(interaction.user),
        )

    @restore_group.command(name="membros", description="Restaura cargos/apelidos de membros que ainda estão no servidor")
    @app_commands.describe(arquivo="Nome do arquivo de backup (deixe vazio para usar o mais recente)")
    @is_authorized()
    async def membros(self, interaction: discord.Interaction, arquivo: str = None):
        await interaction.response.defer(thinking=True, ephemeral=True)
        backup, filename = await self._load_target_backup(interaction, arquivo)
        if not backup:
            await interaction.followup.send("Nenhum backup encontrado.")
            return

        preview = await self.rm.restore_member_roles(interaction.guild, backup, dry_run=True)
        texto = (
            f"**Prévia** (`{filename}`) — membros que saíram do servidor não podem ser restaurados "
            "(o Discord não permite bots re-adicionarem pessoas):\n" + "\n".join(preview[:15])
        )
        if not await self._confirm(interaction, texto):
            return

        self._safety_backup(interaction.guild, str(interaction.user))
        report = await self.rm.restore_member_roles(interaction.guild, backup, dry_run=False)

        await interaction.followup.send("✅ Membros restaurados. Veja detalhes no canal de logs.", ephemeral=True)
        await self.logger.log(
            interaction.guild, "🛡️ Restauração de membros", "\n".join(report),
            discord.Color.gold(), author=str(interaction.user),
        )

    @restore_group.command(name="tudo", description="Restaura cargos, categorias e canais do backup")
    @app_commands.describe(arquivo="Nome do arquivo de backup (deixe vazio para usar o mais recente)")
    @is_authorized()
    async def tudo(self, interaction: discord.Interaction, arquivo: str = None):
        await interaction.response.defer(thinking=True, ephemeral=True)
        backup, filename = await self._load_target_backup(interaction, arquivo)
        if not backup:
            await interaction.followup.send("Nenhum backup encontrado.")
            return

        texto = (
            f"⚠️ **Você está prestes a restaurar TUDO a partir de** `{filename}`.\n"
            "Isso inclui cargos, categorias e canais. Um backup de segurança será criado antes.\n"
            "Tem certeza?"
        )
        if not await self._confirm(interaction, texto):
            return

        self._safety_backup(interaction.guild, str(interaction.user))
        result = await self.rm.restore_all(interaction.guild, backup, dry_run=False)
        full_report = result["roles"] + result["categories"] + result["channels"]

        await interaction.followup.send(
            "✅ Restauração completa finalizada. Veja o log detalhado no canal de logs.", ephemeral=True
        )
        await self.logger.log(
            interaction.guild, "🛡️ Restauração completa", "\n".join(full_report),
            discord.Color.gold(), author=str(interaction.user),
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(RestoreCog(bot))
