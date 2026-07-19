import discord
from sqlalchemy import select

from src.config import CANAL_PAINEL_RECRUTAMENTO_ID, LOGO_PATH, CANAIS, GUILD_ID
from src.database.connection import async_session
from src.database.models import PainelPostado
from src.panels.recrutamento_panel import PainelRecrutamentoLayout
from src.panels.avaliacao_panel import PainelAvaliacaoLayout
from src.panels.whitelist_panel import PainelWhitelistLayout 

async def garantir_painel_whitelist(bot: discord.Client, interaction: discord.Interaction):
    async with async_session() as session:
        resultado = await session.execute(
            select(PainelPostado).where(PainelPostado.nome_painel == "whitelist")
        )
        registro = resultado.scalar_one_or_none()
        
        canal = bot.get_channel(CANAIS["WHITELIST_CANAL_ID"])
        if canal is None:
            print("Canal de WhiteList não foi encontrado ou definido.")
            return

        if registro is not None:    # ---> Caso já tenha sido postado, não duplicar.
            return
        
        # 🔥 CORREÇÃO: Obtém o guild do bot ou do interaction
        if interaction and interaction.guild:
            guild = interaction.guild
        else:
            # Se não tem interaction, pega do bot
            guild = bot.get_guild(GUILD_ID)  # Use seu GUILD_ID da config
            
        if guild is None:
            print("❌ Guild não encontrada!")
            return
        
        # 🔥 CORREÇÃO: Passa o guild, não o interaction
        mensagem = await canal.send(view=PainelWhitelistLayout(guild))

        novo_registro = PainelPostado(
            nome_painel="whitelist",
            canal_id=canal.id,
            message_id=mensagem.id,
        )
        session.add(novo_registro)
        await session.commit()


async def garantir_painel_recrutamento(bot: discord.Client):
    async with async_session() as session:
        resultado = await session.execute(
            select(PainelPostado).where(PainelPostado.nome_painel == "recrutamento")
        )
        registro = resultado.scalar_one_or_none()

        if registro is not None:
            # já foi postado antes, não duplica
            return

        canal = bot.get_channel(CANAL_PAINEL_RECRUTAMENTO_ID)
        if canal is None:
            print("Canal do painel de recrutamento não encontrado. Confira CANAL_PAINEL_RECRUTAMENTO_ID.")
            return

        arquivo = discord.File(LOGO_PATH, filename="logo.png")
        mensagem = await canal.send(view=PainelRecrutamentoLayout(), file=arquivo)

        novo_registro = PainelPostado(
            nome_painel="recrutamento",
            canal_id=canal.id,
            message_id=mensagem.id,
        )
        session.add(novo_registro)
        await session.commit()


async def garantir_painel_avaliacao(bot: discord.Client):
    async with async_session() as session:
        resultado = await session.execute(
            select(PainelPostado).where(PainelPostado.nome_painel == "avaliacao")
        )
        registro = resultado.scalar_one_or_none()
        if registro is not None:
            return

        canal = bot.get_channel(CANAIS["AVALIACAO"])
        if canal is None:
            print("Canal de Avaliação não encontrado. Confira CANAIS['AVALIACAO'].")
            return

        arquivo = discord.File(LOGO_PATH, filename="logo.png")
        mensagem = await canal.send(view=PainelAvaliacaoLayout(), file=arquivo)

        session.add(PainelPostado(
            nome_painel="avaliacao", 
            canal_id=canal.id, 
            message_id=mensagem.id)
        )
        await session.commit()