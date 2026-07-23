import discord

from src.config import CARGOS, CANAIS, ESCOPOS_GERENCIAMENTO, JANELA_TEMPO_SUSPEITA_SEGUNDOS
from src.utils.logger import log_mudanca_cargo
from src.utils.log_container import LogContainerView
from src.utils.rate_limiter import registrar_remocao


def _cargo_permitido_para_executor(executor: discord.Member, nome_cargo: str) -> bool:
    """
    Verifica se o executor pode gerenciar um cargo específico.
    Percorre todos os escopos do executor e confere se o cargo está
    na lista de gerenciáveis de algum deles.
    """
    escopos_do_executor = determinar_escopos(executor)

    for escopo in escopos_do_executor:
        cargos_que_pode_gerenciar = listar_cargos_do_escopo(escopo, executor)
        if nome_cargo in cargos_que_pode_gerenciar:
            return True

    return False


def determinar_escopos(membro: discord.Member) -> list[str]:
    """
    Retorna as chaves de ESCOPOS_GERENCIAMENTO que esse membro está autorizado a usar.
    Ex: se o membro tem o cargo '👑・DIRETOR', retorna ['diretoria'].
    """
    escopos_do_membro = []

    for chave_escopo, config_escopo in ESCOPOS_GERENCIAMENTO.items():
        # Pega os IDs dos cargos autorizados para este escopo
        ids_autorizados_no_escopo = {
            CARGOS[nome_do_cargo]
            for nome_do_cargo in config_escopo["cargos_autorizados"]
        }

        # Verifica se o membro possui algum desses cargos
        membro_tem_acesso = any(
            cargo_do_membro.id in ids_autorizados_no_escopo
            for cargo_do_membro in membro.roles
        )

        if membro_tem_acesso:
            escopos_do_membro.append(chave_escopo)

    return escopos_do_membro


def listar_cargos_do_escopo(escopo: str, membro_executor: discord.Member) -> list[str]:
    """
    Retorna os nomes dos cargos que o membro pode gerenciar DENTRO de um escopo.

    - Se o escopo tem 'cargos_gerenciaveis' como LISTA (ex: 'dono', 'gate'):
      o membro pode gerenciar todos, retorna a lista inteira.

    - Se o escopo tem 'cargos_gerenciaveis' como DICIONÁRIO (ex: 'diretoria', 'geral'):
      cada chave é um cargo que pode gerenciar outros. Precisamos achar qual dessas
      chaves o membro executor possui, e retornar APENAS a lista daquele cargo.
    """
    config_escopo = ESCOPOS_GERENCIAMENTO[escopo]
    cargos_gerenciaveis = config_escopo["cargos_gerenciaveis"]

    # ---------------------------------------------------------------
    # CASO 1: 'cargos_gerenciaveis' é None
    # Significa "todos os cargos de todos os outros escopos".
    # Junta tudo e retorna.
    # ---------------------------------------------------------------
    if cargos_gerenciaveis is None:
        todos_os_cargos = []
        for outro_escopo in ESCOPOS_GERENCIAMENTO.values():
            candidatos = outro_escopo["cargos_gerenciaveis"]
            if candidatos is not None:
                # Se for dict, pega os valores (as listas) e achata
                if isinstance(candidatos, dict):
                    for lista_de_cargos in candidatos.values():
                        todos_os_cargos.extend(lista_de_cargos)
                # Se for lista, estende direto
                elif isinstance(candidatos, list):
                    todos_os_cargos.extend(candidatos)
        return todos_os_cargos

    # ---------------------------------------------------------------
    # CASO 2: 'cargos_gerenciaveis' é uma LISTA
    # O membro pode gerenciar todos os cargos da lista.
    # Ex: escopos 'dono' e 'gate'
    # ---------------------------------------------------------------
    if isinstance(cargos_gerenciaveis, list):
        return cargos_gerenciaveis

    # ---------------------------------------------------------------
    # CASO 3: 'cargos_gerenciaveis' é um DICIONÁRIO
    # As chaves são cargos que podem gerenciar, os valores são listas
    # de cargos gerenciáveis. Precisamos descobrir qual chave o membro
    # executor possui, e retornar APENAS a lista daquela chave.
    # Ex: escopos 'diretoria' e 'geral'
    # ---------------------------------------------------------------
    if isinstance(cargos_gerenciaveis, dict):
        # Pega os IDs dos cargos do membro executor
        ids_dos_cargos_do_membro = {cargo.id for cargo in membro_executor.roles}

        for nome_do_cargo_gerenciador, lista_de_gerenciaveis in cargos_gerenciaveis.items():
            id_do_cargo_gerenciador = CARGOS.get(nome_do_cargo_gerenciador)

            # Se o membro possui este cargo gerenciador, retorna a lista dele
            if id_do_cargo_gerenciador and id_do_cargo_gerenciador in ids_dos_cargos_do_membro:
                return lista_de_gerenciaveis

        # Se o membro não possui nenhum cargo gerenciador deste escopo,
        # retorna lista vazia (não pode gerenciar nada)
        return []

    # Fallback: se não for None, lista ou dict, retorna vazio por segurança
    return []


async def adicionar_cargo(interaction: discord.Interaction, candidato: discord.Member, nome_cargo: str):
    """
    Adiciona um cargo ao candidato.
    Verifica permissão do executor, impede auto-atribuição e cargo duplicado.
    """
    guild = interaction.guild
    executor = interaction.user

    # Valida se o executor pode gerenciar este cargo
    if not _cargo_permitido_para_executor(executor, nome_cargo):
        await interaction.followup.send("❌ Você não tem permissão para gerenciar esse cargo.", ephemeral=True)
        return

    # Impede que o executor atribua cargos a si mesmo
    if candidato.id == executor.id:
        await interaction.followup.send("❌ Você não pode atribuir cargos a si mesmo.", ephemeral=True)
        return

    # Busca o cargo pelo ID no servidor
    cargo = guild.get_role(CARGOS[nome_cargo])

    # Verifica se o candidato já possui o cargo
    if cargo in candidato.roles:
        await interaction.followup.send(f"❌ {candidato.mention} já possui o cargo {cargo.mention}.", ephemeral=True)
        return

    # Adiciona o cargo e registra no log
    await candidato.add_roles(cargo, reason=f"Adicionado via `/gerenciar_cargos` por {executor}")
    await log_mudanca_cargo(guild, candidato=candidato, executor=executor, cargos_adicionados=[cargo.mention])

    await interaction.followup.send(f"✅ Cargo {cargo.mention} adicionado a {candidato.mention}.", ephemeral=True)


async def remover_cargo(interaction: discord.Interaction, candidato: discord.Member, nome_cargo: str):
    """
    Remove um cargo do candidato.
    Verifica permissão do executor, impede auto-remoção e cargo inexistente.
    Também monitora remoções suspeitas (muitas em pouco tempo).
    """
    guild = interaction.guild
    executor = interaction.user

    # Valida se o executor pode gerenciar este cargo
    if not _cargo_permitido_para_executor(executor, nome_cargo):
        await interaction.followup.send("❌ Você não tem permissão para gerenciar esse cargo.", ephemeral=True)
        return

    # Impede que o executor remova cargos de si mesmo
    if candidato.id == executor.id:
        await interaction.followup.send("❌ Você não pode remover cargos de si mesmo.", ephemeral=True)
        return

    # Busca o cargo pelo ID no servidor
    cargo = guild.get_role(CARGOS[nome_cargo])

    # Verifica se o candidato realmente possui o cargo
    if cargo not in candidato.roles:
        await interaction.followup.send(f"❌ {candidato.mention} não possui o cargo {cargo.mention}.", ephemeral=True)
        return

    # Remove o cargo e registra no log
    await candidato.remove_roles(cargo, reason=f"Removido via `/gerenciar_cargos` por {executor}")
    await log_mudanca_cargo(guild, candidato=candidato, executor=executor, cargos_removidos=[cargo.mention])

    # Registra a remoção no controlador de frequência (anti-abuso)
    remocoes_recentes = registrar_remocao(executor.id, candidato.id, cargo.id, nome_cargo)

    # Se houve atividade suspeita, reverte as remoções e notifica
    if remocoes_recentes is not None:
        await _reverter_remocoes_suspeitas(guild, executor, remocoes_recentes)
        await interaction.followup.send(
            "⚠️ Você está fazendo isso rápido demais. As remoções recentes foram revertidas "
            "e essa atividade foi registrada no log de cargos.",
            ephemeral=True,
        )
        return

    await interaction.followup.send(f"✅ Cargo {cargo.mention} removido de {candidato.mention}.", ephemeral=True)


async def _reverter_remocoes_suspeitas(
    guild: discord.Guild,
    executor: discord.Member,
    remocoes: list[tuple[float, int, int, str]]
):
    """
    Reverte remoções feitas rapidamente (possível ataque/erro).
    Para cada remoção na lista, devolve o cargo ao membro se ele não o tiver mais.
    Envia um relatório detalhado no canal de log de cargos.
    """
    linhas_do_relatorio = []

    for _, id_do_candidato, id_do_cargo, _nome_do_cargo in remocoes:
        candidato = guild.get_member(id_do_candidato)
        cargo = guild.get_role(id_do_cargo)

        # Se o membro ou cargo não existem mais, pula
        if candidato is None or cargo is None:
            continue

        # Se o cargo já foi removido, devolve
        if cargo not in candidato.roles:
            await candidato.add_roles(cargo, reason="Reversão automática - atividade suspeita detectada")

        linhas_do_relatorio.append(f"- {candidato.mention}: {cargo.mention} restaurado")

    # Busca o canal de log
    canal_de_log = guild.get_channel(CANAIS["LOG_CARGOS"])
    if canal_de_log is None:
        return

    # Monta o texto do relatório
    texto_do_relatorio = (
        f"- **Executor:** {executor.mention} (`{executor.id}`)\n"
        f"- **Motivo:** {len(remocoes)} remoções de cargo em menos de {JANELA_TEMPO_SUSPEITA_SEGUNDOS}s\n\n"
        + "\n".join(linhas_do_relatorio)
    )

    # Cria a view com o container de log
    view_de_log = LogContainerView(
        titulo="⚠️ Atividade Suspeita Detectada",
        linhas=texto_do_relatorio,
        guild=guild,
        cor=discord.Color.orange(),
        avatar_url=executor.display_avatar.url,
    )

    await canal_de_log.send(view=view_de_log)