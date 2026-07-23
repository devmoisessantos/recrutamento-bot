import discord

from src.services.gerenciar_cargos_service import (
    determinar_escopos, listar_cargos_do_escopo, adicionar_cargo, remover_cargo,
)
from src.utils.error_handling import LoggingViewMixin


class GerenciarCargosView(LoggingViewMixin, discord.ui.LayoutView):
    def __init__(self, membro_executor: discord.Member):
        super().__init__(timeout=180)

        escopos = determinar_escopos(membro_executor)
        self.nomes_cargos = []
        for escopo in escopos:
            for nome in listar_cargos_do_escopo(escopo):
                if nome not in self.nomes_cargos:
                    self.nomes_cargos.append(nome)

        self.candidato_selecionado: discord.Member | None = None
        self.cargo_selecionado: str | None = None

        self._montar_componentes()

    def _montar_componentes(self):
        select_membro = discord.ui.UserSelect(placeholder="1. Selecione o membro")
        select_membro.callback = self._selecionar_membro

        select_cargo = discord.ui.Select(
            placeholder="2. Selecione o cargo",
            options=[discord.SelectOption(label=nome, value=nome) for nome in self.nomes_cargos],
        )
        select_cargo.callback = self._selecionar_cargo

        botao_adicionar = discord.ui.Button(label="Adicionar Cargo", style=discord.ButtonStyle.success)
        botao_adicionar.callback = self._adicionar

        botao_remover = discord.ui.Button(label="Remover Cargo", style=discord.ButtonStyle.danger)
        botao_remover.callback = self._remover

        row_membro = discord.ui.ActionRow()
        row_membro.add_item(select_membro)

        row_cargo = discord.ui.ActionRow()
        row_cargo.add_item(select_cargo)

        row_botoes = discord.ui.ActionRow()
        row_botoes.add_item(botao_adicionar)
        row_botoes.add_item(botao_remover)

        resumo_membro = self.candidato_selecionado.mention if self.candidato_selecionado else "*nenhum*"
        resumo_cargo = self.cargo_selecionado if self.cargo_selecionado else "*nenhum*"

        container = discord.ui.Container(
            discord.ui.TextDisplay("# 🛠️ Gerenciamento de Cargos"),
            discord.ui.TextDisplay(
                f"- **Membro selecionado:** {resumo_membro}\n"
                f"- **Cargo selecionado:** {resumo_cargo}"
            ),
            discord.ui.Separator(spacing=discord.SeparatorSpacing.small),
            row_membro,
            row_cargo,
            row_botoes,
            accent_color=discord.Color.blurple(),
        )

        # Se já existir um container montado antes, remove pra evitar duplicar
        if hasattr(self, "container"):
            self.remove_item(self.container)

        self.container = container
        self.add_item(self.container)

    async def _selecionar_membro(self, interaction: discord.Interaction):
        self.candidato_selecionado = interaction.data["values"][0]
        self.candidato_selecionado = interaction.guild.get_member(int(self.candidato_selecionado))
        self._montar_componentes()
        await interaction.response.edit_message(view=self)

    async def _selecionar_cargo(self, interaction: discord.Interaction):
        self.cargo_selecionado = interaction.data["values"][0]
        self._montar_componentes()
        await interaction.response.edit_message(view=self)

    async def _validar_selecoes(self, interaction: discord.Interaction) -> bool:
        if self.candidato_selecionado is None or self.cargo_selecionado is None:
            await interaction.response.send_message(
                "❌ Selecione um membro e um cargo antes de continuar.", ephemeral=True
            )
            return False
        return True

    async def _adicionar(self, interaction: discord.Interaction):
        if not await self._validar_selecoes(interaction):
            return
        await interaction.response.defer(ephemeral=True)
        await adicionar_cargo(interaction, self.candidato_selecionado, self.cargo_selecionado)

    async def _remover(self, interaction: discord.Interaction):
        if not await self._validar_selecoes(interaction):
            return
        await interaction.response.defer(ephemeral=True)
        await remover_cargo(interaction, self.candidato_selecionado, self.cargo_selecionado)