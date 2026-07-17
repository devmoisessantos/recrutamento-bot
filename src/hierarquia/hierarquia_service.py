import discord
from sqlalchemy import select

from src.config import CARGOS, CARGOS_HIERARQUIA, CANAIS
from src.database.connection import async_session
from src.database.models import MensagemHierarquia
from src.hierarquia.builder import montar_card_cargo


def calcular_membros_por_cargo(guild: discord.Guild) -> dict[int, list[discord.Member]]:
    cargos_ordenados = [guild.get_role(CARGOS[nome]) for nome in CARGOS_HIERARQUIA]
    cargos_ordenados = [c for c in cargos_ordenados if c is not None]

    resultado: dict[int, list[discord.Member]] = {cargo.id: [] for cargo in cargos_ordenados}

    for membro in guild.members:
        cargos_que_possui = [c for c in cargos_ordenados if c in membro.roles]
        if not cargos_que_possui:
            continue
        cargo_mais_alto = max(cargos_que_possui, key=lambda c: c.position)
        resultado[cargo_mais_alto.id].append(membro)

    return resultado


async def atualizar_hierarquia(guild: discord.Guild):
    canal = guild.get_channel(CANAIS["HIERARQUIA_SUL"])
    if canal is None:
        print("Canal de hierarquia não encontrado. Confira CANAIS['HIERARQUIA_SUL'].")
        return

    membros_por_cargo = calcular_membros_por_cargo(guild)

    for nome_cargo in CARGOS_HIERARQUIA:
        cargo = guild.get_role(CARGOS[nome_cargo])
        if cargo is None:
            continue  # cargo foi apagado do servidor, pula

        membros = membros_por_cargo.get(cargo.id, [])
        card = montar_card_cargo(cargo, membros)

        async with async_session() as session:
            resultado = await session.execute(
                select(MensagemHierarquia).where(MensagemHierarquia.cargo_id == cargo.id)
            )
            registro = resultado.scalar_one_or_none()

            if registro is not None:
                try:
                    mensagem = await canal.fetch_message(registro.message_id)
                    await mensagem.edit(view=_embrulhar_em_view(card))
                    continue  # sucesso, vai pro próximo cargo
                except discord.NotFound:
                    pass  # mensagem foi apagada manualmente, vamos criar uma nova abaixo

            # Cria uma mensagem nova (primeira vez, ou porque a antiga sumiu)
            nova_mensagem = await canal.send(view=_embrulhar_em_view(card))

            if registro is not None:
                registro.canal_id = canal.id
                registro.message_id = nova_mensagem.id
            else:
                session.add(MensagemHierarquia(
                    cargo_id=cargo.id, canal_id=canal.id, message_id=nova_mensagem.id
                ))

            await session.commit()


def _embrulhar_em_view(container: discord.ui.Container) -> discord.ui.LayoutView:
    """Container sozinho não pode ser enviado direto — precisa estar dentro de uma LayoutView."""
    view = discord.ui.LayoutView(timeout=None)
    view.add_item(container)
    return view