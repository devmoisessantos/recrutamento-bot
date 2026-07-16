import json
import discord
from datetime import datetime, timezone
from sqlalchemy import select


from src.config import CARGOS, CANAIS, TOTAL_PERGUNTAS_PROVA, NOTA_MINIMA_APROVACAO
from src.database.connection import async_session
from src.database.models import Recrutamento, Pergunta, RespostaProva
from src.utils.logger import log_cargo
from src.utils.error_handling import LoggingViewMixin
from src.panels.aprovacao_panel import AprovacaoView

async def iniciar_avaliacao(interaction: discord.Interaction):
    candidato = interaction.user
    guild = interaction.guild

    async with async_session() as session:
        resultado = await session.execute(
            select(Recrutamento).where(
                Recrutamento.discord_id_candidato == candidato.id,
                Recrutamento.status == "ESTUDANDO",
            )
        )
        recrutamento = resultado.scalar_one_or_none()

        if recrutamento is None:
            await interaction.response.send_message(
                "❌ Você não possui um recrutamento ativo em fase de estudo.", ephemeral=True
            )
            return

        if recrutamento.formulario_aberto:
            await interaction.response.send_message(
                "❌ Sua avaliação já foi iniciada anteriormente e não pode ser reaberta. "
                "Caso tenha ocorrido um erro, procure um recrutador.",
                ephemeral=True,
            )
            return

        recrutamento.formulario_aberto = True
        recrutamento.status = "EM_PROVA"
        recrutamento.pergunta_atual = 0
        recrutamento.data_inicio_prova = datetime.utcnow()  # antes: datetime.now(timezone.utc)
        await session.commit()

    # Troca de cargo: Estudante -> Prova
    cargo_estudante = guild.get_role(CARGOS["ESTUDANTE"])
    cargo_prova = guild.get_role(CARGOS["PROVA"])
    await candidato.remove_roles(cargo_estudante, reason="Iniciou avaliação")
    await candidato.add_roles(cargo_prova, reason="Iniciou avaliação")

    # única resposta à interação
    await interaction.response.send_message(
        "# 📝┃📋・PROVA — CENTRO MÉDICO SUL VALLEY\n"
        "> Leia com atenção. Algumas questões exigem interpretação.\n"
        "> Responda corretamente às questões abaixo.\n"
        "> Cada pergunta possui apenas 1 alternativa correta.\n\n"
        "Avaliação iniciada! Você tem **1 hora** para concluir.",
        ephemeral=True,
    )
    await enviar_pergunta(interaction, numero=1)

async def enviar_pergunta(interaction: discord.Interaction, numero: int):
    async with async_session() as session:
        resultado = await session.execute(select(Pergunta).where(Pergunta.ordem == numero))
        pergunta = resultado.scalar_one_or_none()

    view = PerguntaView(numero=numero, pergunta=pergunta)
    conteudo = f"## 📝 Pergunta {numero}/{TOTAL_PERGUNTAS_PROVA}\n\n{pergunta.enunciado}"

    if interaction.response.is_done():
        await interaction.edit_original_response(content=conteudo, view=view)
    else:
        await interaction.response.send_message(conteudo, view=view, ephemeral=True)


class PerguntaView(LoggingViewMixin, discord.ui.View):
    def __init__(self, numero: int, pergunta: Pergunta):
        super().__init__(timeout=None)
        self.numero = numero
        self.pergunta = pergunta

        opcoes = json.loads(pergunta.opcoes)
        letras = ["A", "B", "C", "D"]

        select = discord.ui.Select(
            placeholder="Escolha uma resposta...",
            options=[
                discord.SelectOption(label=f"{letras[i]}) {texto}", value=letras[i])
                for i, texto in enumerate(opcoes)
            ],
        )
        select.callback = self.responder
        self.add_item(select)


    async def responder(self, interaction: discord.Interaction):
        resposta = interaction.data["values"][0]
        correta = resposta == self.pergunta.resposta_correta

        async with async_session() as session:
            resultado = await session.execute(
                select(Recrutamento).where(
                    Recrutamento.discord_id_candidato == interaction.user.id,
                    Recrutamento.status == "EM_PROVA",
                )
            )
            recrutamento = resultado.scalar_one_or_none()

            session.add(RespostaProva(
                recrutamento_id=recrutamento.id,
                numero_pergunta=self.numero,
                resposta_escolhida=resposta,
                correta=correta,
            ))
            recrutamento.pergunta_atual = self.numero
            await session.commit()

        if self.numero >= TOTAL_PERGUNTAS_PROVA:
            await mostrar_botao_enviar(interaction)
        else:
            await enviar_pergunta(interaction, numero=self.numero + 1)


async def mostrar_botao_enviar(interaction: discord.Interaction):
    view = discord.ui.View(timeout=None)
    botao = discord.ui.Button(label="Enviar Questionário", style=discord.ButtonStyle.success)

    async def enviar_callback(inter: discord.Interaction):
        await finalizar_avaliacao(inter)

    botao.callback = enviar_callback
    view.add_item(botao)

    await interaction.response.edit_message(
        content="Você respondeu todas as perguntas. Clique abaixo para enviar sua avaliação.",
        view=view,
    )


async def finalizar_avaliacao(interaction: discord.Interaction):
    candidato = interaction.user
    guild = interaction.guild

    async with async_session() as session:
        resultado = await session.execute(
            select(Recrutamento).where(
                Recrutamento.discord_id_candidato == candidato.id,
                Recrutamento.status == "EM_PROVA",
            )
        )
        recrutamento = resultado.scalar_one()

        resultado_respostas = await session.execute(
            select(RespostaProva).where(RespostaProva.recrutamento_id == recrutamento.id)
        )
        respostas = resultado_respostas.scalars().all()

        acertos = sum(1 for r in respostas if r.correta)
        percentual = round((acertos / TOTAL_PERGUNTAS_PROVA) * 100, 1)

        recrutamento.acertos = acertos
        recrutamento.nota_percentual = percentual
        recrutamento.status = "AGUARDANDO_DECISAO"
        await session.commit()

        respostas_erradas_ids = [r.numero_pergunta for r in respostas if not r.correta]

        # Monta o detalhe de cada pergunta errada (enunciado, resposta dada, resposta correta)
        detalhes_erros = []
        for resposta in respostas:
            if resposta.correta:
                continue

            resultado_pergunta = await session.execute(
                select(Pergunta).where(Pergunta.ordem == resposta.numero_pergunta)
            )
            pergunta = resultado_pergunta.scalar_one()
            opcoes = json.loads(pergunta.opcoes)
            letras = ["A", "B", "C", "D"]

            texto_resposta_dada = opcoes[letras.index(resposta.resposta_escolhida)]
            texto_resposta_correta = opcoes[letras.index(pergunta.resposta_correta)]

            detalhes_erros.append({
                "numero": resposta.numero_pergunta,
                "enunciado": pergunta.enunciado,
                "resposta_dada": texto_resposta_dada,
                "resposta_correta": texto_resposta_correta,
            })

    await interaction.response.edit_message(
        content=f"✅ Avaliação enviada! Você acertou {acertos}/{TOTAL_PERGUNTAS_PROVA} ({percentual}%). "
                f"Aguarde a decisão do recrutador.",
        view=None,
    )

    canal = guild.get_channel(CANAIS["APROVAR_REPROVAR"])
    status_emoji = "✅ Apto para aprovação" if percentual >= NOTA_MINIMA_APROVACAO else "❌ Abaixo da nota mínima"
    cor = discord.Color.green() if percentual >= NOTA_MINIMA_APROVACAO else discord.Color.red()

    await canal.send(view=AprovacaoView(
        candidato=candidato, 
        recrutamento_id=recrutamento.id,
        nota=percentual, 
        acertos=acertos, 
        total=TOTAL_PERGUNTAS_PROVA,
        respostas_erradas=respostas_erradas_ids, 
        detalhes_erros=detalhes_erros,
        status_emoji=status_emoji, 
        guild=guild, 
        cor=cor,
    ))