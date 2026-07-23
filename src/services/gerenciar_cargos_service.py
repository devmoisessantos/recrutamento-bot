import discord

from src.config import CARGOS, CANAIS, ESCOPOS_GERENCIAMENTO, JANELA_TEMPO_SUSPEITA_SEGUNDOS
from src.utils.logger import log_mudanca_cargo
from src.utils.log_container import LogContainerView
from src.utils.rate_limiter import registrar_remocao

def _cargo_permitido_para_executor(executor: discord.Member, nome_cargo: str) -> bool:
    escopos = determinar_escopos(executor)
    for escopo in escopos:
        if nome_cargo in listar_cargos_do_escopo(escopo):
            return True
    return False


def determinar_escopos(membro: discord.Member) -> list[str]:
    """Retorna as chaves de ESCOPOS_GERENCIAMENTO que esse membro está autorizado a usar."""
    escopos = []
    for chave, config_escopo in ESCOPOS_GERENCIAMENTO.items():
        ids_autorizados = {CARGOS[nome] for nome in config_escopo["cargos_autorizados"]}
        if any(cargo.id in ids_autorizados for cargo in membro.roles):
            escopos.append(chave)
    return escopos


def listar_cargos_do_escopo(escopo: str, membro: discord.Member = None) -> list[str]:
    """Nomes de cargo gerenciáveis dentro de um escopo."""
    config_escopo = ESCOPOS_GERENCIAMENTO[escopo]
    cargos_gerenciaveis = config_escopo["cargos_gerenciaveis"]
    
    # Se for uma lista, retorna diretamente
    if isinstance(cargos_gerenciaveis, list):
        return cargos_gerenciaveis
    
    # Se for um dicionário, precisa filtrar baseado no cargo do membro
    if isinstance(cargos_gerenciaveis, dict) and membro:
        nomes_cargos_membro = [cargo.name for cargo in membro.roles]
        
        # Encontra qual cargo do membro tem permissão no dicionário
        for cargo_autorizado, cargos_permitidos in cargos_gerenciaveis.items():
            if cargo_autorizado in nomes_cargos_membro:
                return cargos_permitidos
        
        # Se nenhum cargo específico for encontrado, retorna lista vazia
        return []
    
    # Fallback: se for None ou não for lista nem dict
    return []

async def adicionar_cargo(interaction: discord.Interaction, candidato: discord.Member, nome_cargo: str):
    guild = interaction.guild
    executor = interaction.user

    if not _cargo_permitido_para_executor(executor, nome_cargo):
        await interaction.followup.send("❌ Você não tem permissão para gerenciar esse cargo.", ephemeral=True)
        return

    if candidato.id == executor.id:
        await interaction.followup.send("❌ Você não pode atribuir cargos a si mesmo.", ephemeral=True)
        return

    cargo = guild.get_role(CARGOS[nome_cargo])
    if cargo in candidato.roles:
        await interaction.followup.send(f"❌ {candidato.mention} já possui o cargo {cargo.mention}.", ephemeral=True)
        return

    await candidato.add_roles(cargo, reason=f"Adicionado via `/gerenciar_cargos` por {executor}")
    await log_mudanca_cargo(guild, candidato=candidato, executor=executor, cargos_adicionados=[cargo.mention])

    await interaction.followup.send(f"✅ Cargo {cargo.mention} adicionado a {candidato.mention}.", ephemeral=True)


async def remover_cargo(interaction: discord.Interaction, candidato: discord.Member, nome_cargo: str):
    guild = interaction.guild
    executor = interaction.user

    if not _cargo_permitido_para_executor(executor, nome_cargo):
        await interaction.followup.send("❌ Você não tem permissão para gerenciar esse cargo.", ephemeral=True)
        return

    if candidato.id == executor.id:
        await interaction.followup.send("❌ Você não pode remover cargos de si mesmo.", ephemeral=True)
        return

    cargo = guild.get_role(CARGOS[nome_cargo])
    if cargo not in candidato.roles:
        await interaction.followup.send(f"❌ {candidato.mention} não possui o cargo {cargo.mention}.", ephemeral=True)
        return

    await candidato.remove_roles(cargo, reason=f"Removido via `/gerenciar_cargos` por {executor}")
    await log_mudanca_cargo(guild, candidato=candidato, executor=executor, cargos_removidos=[cargo.mention])

    recentes = registrar_remocao(executor.id, candidato.id, cargo.id, nome_cargo)

    if recentes is not None:
        await _reverter_remocoes_suspeitas(guild, executor, recentes)
        await interaction.followup.send(
            "⚠️ Você está fazendo isso rápido demais. As remoções recentes foram revertidas "
            "e essa atividade foi registrada no log de cargos.",
            ephemeral=True,
        )
        return

    await interaction.followup.send(f"✅ Cargo {cargo.mention} removido de {candidato.mention}.", ephemeral=True)


async def _reverter_remocoes_suspeitas(guild: discord.Guild, executor: discord.Member,
                                        remocoes: list[tuple[float, int, int, str]]):
    linhas = []

    for _, candidato_id, cargo_id, _nome_cargo in remocoes:
        candidato = guild.get_member(candidato_id)
        cargo = guild.get_role(cargo_id)
        if candidato is None or cargo is None:
            continue

        if cargo not in candidato.roles:
            await candidato.add_roles(cargo, reason="Reversão automática - atividade suspeita detectada")

        linhas.append(f"- {candidato.mention}: {cargo.mention} restaurado")

    canal = guild.get_channel(CANAIS["LOG_CARGOS"])
    if canal is None:
        return


    texto = (
        f"- **Executor:** {executor.mention} (`{executor.id}`)\n"
        f"- **Motivo:** {len(remocoes)} remoções de cargo em menos de {JANELA_TEMPO_SUSPEITA_SEGUNDOS}s\n\n"
        + "\n".join(linhas)
    )

    view = LogContainerView(
        titulo="⚠️ Atividade Suspeita Detectada",
        linhas=texto,
        guild=guild,
        cor=discord.Color.orange(),
        avatar_url=executor.display_avatar.url,
    )
    await canal.send(view=view)