import re

from src.config import PREFIXOS_NICKNAME


ABERTURAS = "[⟦【〔"
FECHAMENTOS = "]⟧】〕"


def remover_prefixo_existente(nome: str) -> str:
    """Remove qualquer prefixo entre colchetes (de qualquer estilo) do início do nome."""
    nome = nome.strip()
    if not nome or nome[0] not in ABERTURAS:
        return nome

    for i, char in enumerate(nome):
        if char in FECHAMENTOS:
            return nome[i + 1:].strip()

    return nome  # não achou fechamento, retorna sem mexer

def aplicar_prefixo(nome_atual: str, cargo: str) -> str:
    """Remove prefixo antigo (se houver) e aplica o novo prefixo do cargo,
    truncando o nome para nunca ultrapassar 32 caracteres no total."""
    prefixo = PREFIXOS_NICKNAME.get(cargo)
    if prefixo is None:
        return nome_atual[:32]

    nome_sem_prefixo = remover_prefixo_existente(nome_atual)
    prefixo_completo = f"{prefixo} "
    limite_nome = 32 - len(prefixo_completo)

    return f"{prefixo_completo}{nome_sem_prefixo[:limite_nome]}"
