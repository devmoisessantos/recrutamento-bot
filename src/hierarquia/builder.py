import discord
from datetime import datetime, timezone


def montar_card_cargo(cargo: discord.Role, membros: list[discord.Member]) -> discord.ui.Container:
    if membros:
        linhas = "\n".join(f"- {membro.mention}" for membro in membros)
    else:
        linhas = "*Nenhum membro possui este cargo no momento.*"

    agora = int(datetime.now(timezone.utc).timestamp())
    rodape_texto = f"-# Atualizado automaticamente • <t:{agora}:f>"

    return discord.ui.Container(
        discord.ui.TextDisplay(f"# {cargo.name} - [{len(membros)} membros]"),
        discord.ui.Separator(spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(linhas),
        discord.ui.Separator(spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(rodape_texto),
        accent_color=cargo.color if cargo.color.value != 0 else discord.Color.blurple(),
    )