import time

from src.config import LIMITE_REMOCOES_SUSPEITAS, JANELA_TEMPO_SUSPEITA_SEGUNDOS

# Estrutura em memória (não precisa ir pro banco — é só um "cache de curto prazo"):
# {executor_id: [(timestamp, candidato_id, cargo_id, nome_cargo), ...]}
_historico_remocoes: dict[int, list[tuple[float, int, int, str]]] = {}


def registrar_remocao(executor_id: int, candidato_id: int, cargo_id: int, nome_cargo: str):
    """Registra uma remoção de cargo. Se o executor ultrapassar o limite dentro da janela
    de tempo, retorna a lista de remoções recentes (para reverter); caso contrário, None."""
    agora = time.monotonic()
    historico = _historico_remocoes.setdefault(executor_id, [])

    # Descarta entradas fora da janela de tempo antes de contar
    historico[:] = [entrada for entrada in historico if agora - entrada[0] <= JANELA_TEMPO_SUSPEITA_SEGUNDOS]

    historico.append((agora, candidato_id, cargo_id, nome_cargo))

    if len(historico) >= LIMITE_REMOCOES_SUSPEITAS:
        recentes = list(historico)
        historico.clear()  # zera o contador desse executor depois do bloqueio
        return recentes

    return None