import discord
import datetime


class BackupLogger:
    """Envia logs detalhados para um canal de texto do servidor (ex: #backup-logs)."""

    def __init__(self, log_channel_name: str):
        self.log_channel_name = log_channel_name

    def _find_log_channel(self, guild: discord.Guild):
        return discord.utils.get(guild.text_channels, name=self.log_channel_name)

    async def log(
        self,
        guild: discord.Guild,
        title: str,
        description: str,
        color: discord.Color = discord.Color.blurple(),
        author: str = None,
    ):
        channel = self._find_log_channel(guild)
        embed = discord.Embed(
            title=title,
            description=(description or "Sem detalhes.")[:4000],
            color=color,
            timestamp=datetime.datetime.utcnow(),
        )
        if author:
            embed.set_footer(text=f"Executado por {author}")

        if channel:
            try:
                await channel.send(embed=embed)
            except discord.Forbidden:
                print(f"[AVISO] Sem permissão para enviar no canal #{self.log_channel_name}")
        else:
            print(f"[AVISO] Canal de log '#{self.log_channel_name}' não encontrado em {guild.name}")

        print(f"[LOG] {title}: {description[:200] if description else ''}")
