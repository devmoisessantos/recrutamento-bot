import re
import discord

from src.config import CARGOS, CANAIS
from src.utils.logger import log_mudanca_cargo
from src.utils.log_container import LogContainerView


def _aplicar_apelido(candidato: discord.Member, id_fivem: str) -> str:
    """Monta o apelido no formato 'Username | idFivem', respeitando o limite de 32 caracteres."""
    nome_base = candidato.name
    nome_capitalizado = nome_base[:1].upper() + nome_base[1:]
    sufixo = f" | {id_fivem}"
    limite_nome = 32 - len(sufixo)
    return f"{nome_capitalizado[:limite_nome]}{sufixo}"


def _formatar_telefone(telefone: str) -> str:
    """Remove qualquer caractere não-numérico e insere o traço no formato XXX-XXX."""
    apenas_numeros = re.sub(r"\D", "", telefone)
    if len(apenas_numeros) == 6:
        return f"{apenas_numeros[:3]}-{apenas_numeros[3:]}"
    return telefone  # formato inesperado, mantém como foi digitado


async def processar_whitelist(interaction: discord.Interaction, *, nome: str, sobrenome: str,
                               idade: str, telefone: str, id_fivem: str):
    await interaction.response.defer(ephemeral=True)

    candidato = interaction.user
    guild = interaction.guild
    cargo_visitante = guild.get_role(CARGOS["Visitantes"])

    if cargo_visitante in candidato.roles:
        await interaction.followup.send(
            "❌ Você já realizou a Whitelist anteriormente.", ephemeral=True
        )
        return

    if not idade.isdigit():
        await interaction.followup.send(
            "❌ Idade inválida. Digite apenas números.", ephemeral=True
        )
        return

    if not id_fivem.isdigit() or len(id_fivem) > 6:
        await interaction.followup.send(
            "❌ Identificador (ID FiveM) inválido. Deve conter no máximo 6 dígitos numéricos.",
            ephemeral=True,
        )
        return

    telefone_formatado = _formatar_telefone(telefone)
    novo_apelido = _aplicar_apelido(candidato, id_fivem)

    await candidato.add_roles(cargo_visitante, reason="Whitelist concluída")

    apelido_aplicado = True
    try:
        await candidato.edit(nick=novo_apelido)
    except discord.Forbidden:
        apelido_aplicado = False

    await log_mudanca_cargo(
        guild, candidato=candidato, executor=guild.me,
        cargos_adicionados=[cargo_visitante.mention],
    )

    await _enviar_log_whitelist(
        guild, candidato=candidato, nome=nome, sobrenome=sobrenome,
        idade=idade, telefone=telefone_formatado, id_fivem=id_fivem,
        cargo_visitante=cargo_visitante, apelido=novo_apelido,
        apelido_aplicado=apelido_aplicado,
    )

    await interaction.followup.send(
        "✅ Whitelist concluída com sucesso! Seu acesso foi liberado.", ephemeral=True
    )

async def _enviar_log_whitelist(guild: discord.Guild, *, candidato: discord.Member, nome: str,
                                 sobrenome: str, idade: str, telefone: str, id_fivem: str,
                                 cargo_visitante: discord.Role, apelido: str,
                                 apelido_aplicado: bool):
    canal = guild.get_channel(CANAIS["LOG_WHITELIST"])
    if canal is None:
        return

    linhas = (
        f"➜ **Usuário:** {candidato.mention} (`{candidato.id}`)\n"
        f"➜ **Nome:** `{nome}`\n"
        f"➜ **Sobrenome:** `{sobrenome}`\n"
        f"➜ **Idade:** `{idade}`\n"
        f"➜ **Telefone:** `{telefone}`\n"
        f"➜ **Identificador:** `{id_fivem}`\n"
        f"➜ **Cargos adicionados:** {cargo_visitante.mention} (`{cargo_visitante.id}`)\n"
        f"➜ **Nome base (USERNAME):** `{candidato.name}`\n"
        f"➜ **Apelido aplicado:** `{apelido}`"
    )

    if not apelido_aplicado:
        linhas += f"\n- **Não foi possível redefinir o apelido para** `{candidato.name}` ❌"

    view = LogContainerView(
        titulo="✅ Sistema de Liberação - Sucesso",
        linhas=linhas,
        guild=guild,
        cor=discord.Color.green(),
        avatar_url=candidato.display_avatar.url,
    )
    await canal.send(view=view)