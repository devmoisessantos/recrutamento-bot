import discord
from datetime import datetime, timezone


async def log_cargo(guild: discord.Guild, canal_id: int, *, candidato: discord.Member,
                     executor: discord.abc.User, acao: str, cargo: str, extra: str = ""):
    canal = guild.get_channel(canal_id)
    if canal is None:
        return

    texto = (
        f"**{acao}**\n"
        f"Membro: {candidato.mention} (`{candidato.id}`)\n"
        f"Cargo: {cargo}\n"
        f"Executor: {executor.mention}\n"
        f"Data: <t:{int(datetime.now(timezone.utc).timestamp())}:F>"
    )
    if extra:
        texto += f"\n{extra}"

    await canal.send(texto)