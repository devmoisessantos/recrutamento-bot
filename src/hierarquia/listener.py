# src/listeners/hierarquia_listener.py
import asyncio
import discord
from discord.ext import commands

from src.hierarquia.hierarquia_service import atualizar_hierarquia


class HierarquiaListener(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Variáveis para controlar o "debounce"
        self._atualizacao_pendente = False
        self._task = None
        self.DELAY_SEGUNDOS = 5  # 5 segundos - você pode ajustar pra 10, 30, etc

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        # Filtro: só reage se os cargos mudaram
        if set(before.roles) == set(after.roles):
            return
        
        # Se já tem uma atualização agendada, cancela e agenda de novo
        if self._task and not self._task.done():
            self._task.cancel()
        
        # Agenda a atualização com delay
        self._task = asyncio.create_task(self._atualizar_com_delay(after.guild))
    
    async def _atualizar_com_delay(self, guild: discord.Guild):
        try:
            # Espera o delay
            await asyncio.sleep(self.DELAY_SEGUNDOS)
            # Se chegou aqui sem ser cancelado, executa
            await atualizar_hierarquia(guild)
            print(f"✅ Hierarquia atualizada automaticamente (após mudança de cargo)")
        except asyncio.CancelledError:
            # A tarefa foi cancelada porque outra mudança ocorreu
            print("⏸️ Atualização cancelada - nova mudança detectada")
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(HierarquiaListener(bot))