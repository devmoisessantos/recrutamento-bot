import discord
from datetime import datetime, timezone
from sqlalchemy import select

from src.config import CARGOS, CANAIS
from src.database.connection import async_session
from src.database.models import Usuario, Recrutamento
from src.utils.logger import log_cargo
from src.utils.nickname import aplicar_prefixo


def possui_cargo_recrutador_ou_superior(membro: discord.Member) -> bool:
    ids_permitidos = {
        CARGOS["✈️・Recrutador"], CARGOS["🥼・Instrutor"], CARGOS["Supervisor"],
        CARGOS["Vice Diretor"], CARGOS["👑・DIRETOR"], CARGOS["Vice Diretor Geral"],
        CARGOS["Diretor Geral"], CARGOS["👑 Responsável Geral"],
    }
    return any(cargo.id in ids_permitidos for cargo in membro.roles)


class AprovacaoView(discord.ui.View):
    def __init__(self, candidato_id: int, recrutamento_id: int):
        super().__init__(timeout=None)
        self.candidato_id = candidato_id
        self.recrutamento_id = recrutamento_id

    @discord.ui.button(label="Aprovar", style=discord.ButtonStyle.success, custom_id="aprovacao:aprovar")
    async def aprovar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not possui_cargo_recrutador_ou_superior(interaction.user):
            await interaction.response.send_message(
                "❌ Você não possui permissão para aprovar candidatos.", ephemeral=True
            )
            return

        candidato = interaction.guild.get_member(self.candidato_id)
        if candidato is None:
            await interaction.response.send_message("❌ Membro não encontrado no servidor.", ephemeral=True)
            return

        view_cargo = EscolherCargoView(
            candidato_id=self.candidato_id,
            recrutamento_id=self.recrutamento_id,
            aprovador=interaction.user,
            mensagem_original=interaction.message,  # <-- guarda a mensagem com os botões Aprovar/Reprovar
        )
        await interaction.response.send_message(
            f"Escolha o cargo inicial para {candidato.mention}:", view=view_cargo, ephemeral=True
        )


    

        
        # ... resto igual ...

        


    @discord.ui.button(label="Reprovar", style=discord.ButtonStyle.danger, custom_id="aprovacao:reprovar")
    async def reprovar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not possui_cargo_recrutador_ou_superior(interaction.user):
            await interaction.response.send_message(
                "❌ Você não possui permissão para reprovar candidatos.", ephemeral=True
            )
            return

        await interaction.response.defer()  # <-- adicionar aqui

        guild = interaction.guild
        candidato = guild.get_member(self.candidato_id)
        if candidato is None:
            await interaction.response.send_message("❌ Membro não encontrado no servidor.", ephemeral=True)
            return

        cargo_estudante = guild.get_role(CARGOS["ESTUDANTE"])
        cargo_prova = guild.get_role(CARGOS["PROVA"])

        cargos_para_remover = [c for c in [cargo_estudante, cargo_prova] if c in candidato.roles]
        if cargos_para_remover:
            await candidato.remove_roles(*cargos_para_remover, reason=f"Reprovado por {interaction.user}")

        async with async_session() as session:
            resultado = await session.execute(
                select(Recrutamento).where(Recrutamento.id == self.recrutamento_id)
            )
            recrutamento = resultado.scalar_one()
            recrutamento.status = "REPROVADO"
            recrutamento.data_fim = datetime.now(timezone.utc)

            resultado_usuario = await session.execute(
                select(Usuario).where(Usuario.discord_id == self.candidato_id)
            )
            usuario = resultado_usuario.scalar_one()
            usuario.status = "VISITANTE"
            usuario.data_ultima_reprovacao = datetime.now(timezone.utc)

            await session.commit()

        await log_cargo(
            guild, CANAIS["LOG_REPROVACOES"],
            candidato=candidato, executor=interaction.user,
            acao="❌ Candidato Reprovado",
            cargo="Estudante/Prova removidos",
            extra=f"Nota: {recrutamento.nota_percentual}% | Pode tentar novamente em 24h",
        )

        await interaction.edit_original_response(  # <-- trocar de response.edit_message
            content=f"❌ {candidato.mention} foi reprovado por {interaction.user.mention}.",
            view=None,
        )


class EscolherCargoView(discord.ui.View):
    def __init__(self, candidato_id: int, recrutamento_id: int, aprovador: discord.Member,
                 mensagem_original: discord.Message):
        super().__init__(timeout=60)
        self.candidato_id = candidato_id
        self.recrutamento_id = recrutamento_id
        self.aprovador = aprovador
        self.mensagem_original = mensagem_original

    @discord.ui.select(
        placeholder="Selecione o cargo inicial",
        options=[
            discord.SelectOption(label="Enfermeiro(a)", value="🔰・Enfermeiro (a)"),
            discord.SelectOption(label="Paramédico", value="🚑・Paramédico"),
        ],
    )

    async def escolher(self, interaction: discord.Interaction, item: discord.ui.Select):
        await interaction.response.defer()  # confirma a interação imediatamente

        cargo_escolhido = item.values[0]
        guild = interaction.guild
        candidato = guild.get_member(self.candidato_id)

        cargo_estudante = guild.get_role(CARGOS["ESTUDANTE"])
        cargo_prova = guild.get_role(CARGOS["PROVA"])
        cargo_hp = guild.get_role(CARGOS["HP S・Valley"])
        cargo_aprovado = guild.get_role(CARGOS["Aprovado"])
        cargo_visitante = guild.get_role(CARGOS["Visitantes"])
        cargo_final = guild.get_role(CARGOS[cargo_escolhido])

        cargos_remover = [c for c in [cargo_estudante, cargo_prova, cargo_visitante] if c in candidato.roles]
        if cargos_remover:
            await candidato.remove_roles(*cargos_remover, reason=f"Aprovado por {self.aprovador}")

        await candidato.add_roles(cargo_hp, cargo_aprovado, cargo_final, reason=f"Aprovado por {self.aprovador}")
        # ... dentro de escolher()
        novo_nickname = aplicar_prefixo(candidato.display_name, cargo_escolhido)
        try:
            await candidato.edit(nick=novo_nickname)
        except discord.Forbidden:
            pass  # bot pode não ter permissão de editar nick de membros com cargo mais alto


        async with async_session() as session:
            resultado = await session.execute(
                select(Recrutamento).where(Recrutamento.id == self.recrutamento_id)
            )
            recrutamento = resultado.scalar_one()
            recrutamento.status = "APROVADO"
            recrutamento.cargo_final = cargo_escolhido
            recrutamento.data_fim = datetime.now(timezone.utc)

            resultado_usuario = await session.execute(
                select(Usuario).where(Usuario.discord_id == self.candidato_id)
            )
            usuario = resultado_usuario.scalar_one()
            usuario.status = "APROVADO"
            usuario.ja_foi_aprovado = True

            await session.commit()

        await log_cargo(
            guild, CANAIS["LOG_APROVACOES"],
            candidato=candidato, executor=self.aprovador,
            acao="✅ Candidato Aprovado",
            cargo=f"HP S Valley, Aprovado, {cargo_escolhido}",
            extra=f"Nota: {recrutamento.nota_percentual}%",
        )

        await interaction.edit_original_response(
            content=f"✅ {candidato.mention} aprovado como **{cargo_escolhido}** por {self.aprovador.mention}.",
            view=None,
        )

        await self.mensagem_original.edit(
            content=self.mensagem_original.content + f"\n\n✅ **Aprovado como {cargo_escolhido}** por {self.aprovador.mention}",
            view=None,
        )