import discord 
import traceback
import logging
from discord.ext import commands

from src.panels.avaliacao_panel import PainelAvaliacaoLayout
from src.panels.recrutamento_panel import PainelRecrutamentoLayout
from src.panels.whitelist_panel import PainelWhitelistLayout
from src.database.connection import init_db
from src.database.seed_perguntas import seed_perguntas_se_vazio

from src.config import DISCORD_TOKEN, GUILD_ID, CANAIS
from src.panels.setup_paineis import garantir_painel_recrutamento, garantir_painel_avaliacao, garantir_painel_whitelist

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("recrutamento-bot")

intents = discord.Intents.default()
intents.members = True

class RecrutamentoBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Carregar extensões (cogs)
        await self.load_extension("src.cogs.recrutar")
        await self.load_extension("src.cogs.liberar_prova")
        await self.load_extension("src.cogs.aprovar")
        await self.load_extension("src.cogs.reprovar")
        await self.load_extension("src.cogs.whitelist")
        await self.load_extension("src.cogs.hierarquia")
        await self.load_extension("src.hierarquia.listener")

        guild_object = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild_object)
        await self.tree.sync(guild=guild_object)
        logger.info(f"Comandos de barra sincronizados com o servidor (ID: {GUILD_ID})")

        await init_db()
        await seed_perguntas_se_vazio()

        # Inicializa como None - serão criados no on_ready
        self.painel_recrutamento_view = None
        self.painel_avaliacao_view = None
        self.painel_whitelist_view = None


        @self.tree.error
        async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
            guild = interaction.guild
            canal = guild.get_channel(CANAIS["LOG_ERROS"]) if guild else None
            tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))[-1200:]

            if canal:
                await canal.send(
                    f"⚠️ **Erro em Slash Command**\n"
                    f"Comando: `/{interaction.command.name if interaction.command else '?'}`\n"
                    f"Usuário: {interaction.user.mention}\n"
                    f"```py\n{tb}\n```"
                )
                
    async def on_ready(self):
        logger.info(f"Bot conectado como {self.user} (ID: {self.user.id})")
        guild = self.get_guild(int(GUILD_ID))


        if guild:
            logger.info(f"Conectado ao servidor: {guild.name} (ID: {guild.id})")
        else:
            logger.warning("Não foi possível encontrar o servidor com o ID fornecido.")


        # 🔥 PRIMEIRO: Cria os painéis
        self.painel_recrutamento_view = PainelRecrutamentoLayout()
        self.painel_avaliacao_view = PainelAvaliacaoLayout()
        self.painel_whitelist_view = PainelWhitelistLayout(guild)

        # 🔥 DEPOIS: Adiciona as views persistentes
        self.add_view(self.painel_recrutamento_view)
        self.add_view(self.painel_avaliacao_view)
        self.add_view(self.painel_whitelist_view)

        # 🔥 POR ÚLTIMO: Garante que os painéis estão nos canais corretos
        await garantir_painel_recrutamento(self)
        await garantir_painel_avaliacao(self)
        await garantir_painel_whitelist(self)


bot = RecrutamentoBot()

def run():
    bot.run(DISCORD_TOKEN)
    



