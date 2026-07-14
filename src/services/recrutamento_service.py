import discord
from datetime import datetime, timezone

from sqlalchemy import select

from src.config import CARGOS, CANAIS

from src.utils.logger import log_cargo

from src.database.connection import async_session
from src.database.models import Usuario, Recrutamento


async def validar_e_iniciar_recrutamento(
    interaction: discord.Interaction,
    candidato: discord.Member,
    recrutador: discord.Member,
):
    guild = interaction.guild
    cargo_visitante = guild.get_role(CARGOS["Visitantes"])
    cargo_estudante = guild.get_role(CARGOS["ESTUDANTE"])
    cargo_hp = guild.get_role(CARGOS["HP S・Valley"])
    cargo_aprovado = guild.get_role(CARGOS["Aprovado"])

    # Validações do fluxo
    if cargo_visitante not in candidato.roles:
        await interaction.response.send_message(
            "❌ Este membro não possui o cargo Visitante (não concluiu a WhiteList).",
            ephemeral=True,
        )
        return

    if cargo_hp in candidato.roles or cargo_aprovado in candidato.roles:
        await interaction.response.send_message(
            "❌ Este membro já foi aprovado anteriormente.", ephemeral=True
        )
        return

    async with async_session() as session:
        resultado = await session.execute(
            select(Usuario).where(Usuario.discord_id == candidato.id)
        )
        usuario = resultado.scalar_one_or_none()

        if usuario is None:
            usuario = Usuario(discord_id=candidato.id, nickname_atual=candidato.display_name)
            session.add(usuario)

        # Checa cooldown de 24h após reprovação
        if usuario.data_ultima_reprovacao:
            tempo_passado = datetime.now(timezone.utc) - usuario.data_ultima_reprovacao
            if tempo_passado.total_seconds() < 24 * 3600:
                horas_restantes = 24 - (tempo_passado.total_seconds() / 3600)
                await interaction.response.send_message(
                    f"❌ Este candidato precisa aguardar mais {horas_restantes:.1f}h para tentar novamente.",
                    ephemeral=True,
                )
                return

        # Checa se já está em recrutamento ativo
        resultado_recrutamento = await session.execute(
            select(Recrutamento).where(
                Recrutamento.discord_id_candidato == candidato.id,
                Recrutamento.status.in_(["ESTUDANDO", "EM_PROVA"]),
            )
        )
        recrutamento_ativo = resultado_recrutamento.scalar_one_or_none()

        if recrutamento_ativo is not None:
            await interaction.response.send_message(
                "❌ Este candidato já está em processo de recrutamento com outro recrutador.",
                ephemeral=True,
            )
            return

        # Tudo certo: cria o recrutamento
        novo_recrutamento = Recrutamento(
            discord_id_candidato=candidato.id,
            discord_id_recrutador=recrutador.id,
            status="ESTUDANDO",
        )
        session.add(novo_recrutamento)
        usuario.status = "ESTUDANTE"
        await session.commit()

    # Aplica o cargo
    await candidato.add_roles(cargo_estudante, reason=f"Recrutamento iniciado por {recrutador}")

    await interaction.response.send_message(
    f"## ✅ Recrutamento Iniciado\n\n"
    f"👤 **Candidato:** {candidato.mention}\n"
    f"📚 **Cargo aplicado:** `Estudante`\n\n"
    "O candidato já pode iniciar os estudos.",
    ephemeral=True,
)

    # Log (canal de logs - vamos formalizar isso no próximo passo)
    canal_log = guild.get_channel(CANAIS["LOG_RECRUTAMENTOS"])  # substituir pelo ID do canal de logs de recrutamentos
    if canal_log:
        await canal_log.send(
            f"📥 **Recrutamento iniciado**\n"
            f"Candidato: {candidato.mention} (`{candidato.id}`)\n"
            f"Recrutador: {recrutador.mention}\n"
            f"Data: <t:{int(datetime.now(timezone.utc).timestamp())}:F>"
        )




# ... (dentro da função, no lugar do log antigo)
    await log_cargo(
        guild,
        CANAIS["LOG_RECRUTAMENTOS"],
        candidato=candidato,
        executor=recrutador,
        acao="📥 Novo Recrutamento",
        cargo="Estudante",
    )