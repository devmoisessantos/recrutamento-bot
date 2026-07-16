import discord
from datetime import datetime, timezone
from src.config import CANAIS
from src.utils.log_container import LogContainerView


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



async def log_mudanca_cargo(guild: discord.Guild, *, candidato: discord.Member,
                             executor: discord.abc.User,
                             cargos_adicionados: list[str] | None = None,
                             cargos_removidos: list[str] | None = None):
    """Auditoria bruta: toda vez que um cargo é adicionado/removido pelo bot."""
    canal = guild.get_channel(CANAIS["LOG_CARGOS"])
    if canal is None:
        return

    partes = [f"- **Membro:** {candidato.mention} (`{candidato.id}`)"]
    if cargos_adicionados:
        partes.append(f"- **Adicionados:** {', '.join(cargos_adicionados)}")
    if cargos_removidos:
        partes.append(f"- **Removidos:** {', '.join(cargos_removidos)}")
    partes.append(f"- **Executor:** {executor.mention}")

    view = LogContainerView(
        titulo="🔧 Alteração de Cargo(s)",
        linhas="\n".join(partes),
        guild=guild,
        cor=discord.Color.blurple(),
        avatar_url=candidato.display_avatar.url,
    )
    await canal.send(view=view)


async def log_decisao(guild: discord.Guild, canal_id: int, *, titulo: str, candidato: discord.Member,
                       executor: discord.abc.User, cargo: str, extra: str = "",
                       cor: discord.Color = discord.Color.blurple()):
    """Log padronizado para aprovações/reprovações, em Container."""
    canal = guild.get_channel(canal_id)
    if canal is None:
        return

    linhas = (
        f"- **Membro:** {candidato.mention} (`{candidato.id}`)\n"
        f"- **Cargo:** {cargo}\n"
        f"- **Executor:** {executor.mention}"
    )
    if extra:
        linhas += f"\n- {extra}"

    view = LogContainerView(titulo=titulo, linhas=linhas, guild=guild, cor=cor,
                             avatar_url=candidato.display_avatar.url)
    await canal.send(view=view)