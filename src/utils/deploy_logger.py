"""
Utilitário de logs para deploy.
Basta importar e chamar as funções para ver tudo colorido no console.
"""

import datetime
from typing import Any


# Cores ANSI para o terminal
class Cores:
    """Códigos de cor para deixar o console mais legível."""
    VERDE = "\033[92m"
    VERMELHO = "\033[91m"
    AMARELO = "\033[93m"
    AZUL = "\033[94m"
    CIANO = "\033[96m"
    MAGENTA = "\033[95m"
    CINZA = "\033[90m"
    BRANCO = "\033[97m"
    NEGRITO = "\033[1m"
    RESET = "\033[0m"


def _horario_atual() -> str:
    """Retorna o horário atual formatado: [HH:MM:SS]"""
    return datetime.datetime.now().strftime("%H:%M:%S")


def _formatar(msg: str, cor: str, emoji: str = "") -> str:
    """Aplica cor e emoji a uma mensagem."""
    hora = _horario_atual()
    return f"{Cores.CINZA}[{hora}]{Cores.RESET} {emoji} {cor}{msg}{Cores.RESET}"


def info(mensagem: str):
    """Log informativo (azul). Use para ações normais em andamento."""
    print(_formatar(mensagem, Cores.AZUL, "ℹ️"))


def sucesso(mensagem: str):
    """Log de sucesso (verde). Use quando algo terminar bem."""
    print(_formatar(mensagem, Cores.VERDE, "✅"))


def erro(mensagem: str):
    """Log de erro (vermelho). Use quando algo falhar."""
    print(_formatar(mensagem, Cores.VERMELHO, "❌"))


def aviso(mensagem: str):
    """Log de aviso (amarelo). Use para alertas não críticos."""
    print(_formatar(mensagem, Cores.AMARELO, "⚠️"))


def destaque(mensagem: str):
    """Log de destaque (magenta). Use para títulos ou marcos importantes."""
    print(_formatar(mensagem, Cores.MAGENTA + Cores.NEGRITO, "🔷"))


def etapa(numero: int, total: int, descricao: str):
    """
    Mostra o progresso de uma etapa.
    Ex: [1/5] Carregando cogs...
    """
    print(_formatar(f"[{numero}/{total}] {descricao}", Cores.CIANO, "📌"))


def separador(titulo: str = ""):
    """
    Imprime uma linha separadora com título opcional.
    Ex: ═══════ INÍCIO DO DEPLOY ═══════
    """
    if titulo:
        linha = f"═══ {titulo} ═══"
        print(f"\n{Cores.MAGENTA}{Cores.NEGRITO}{linha}{Cores.RESET}")
    else:
        print(f"{Cores.CINZA}{'─' * 60}{Cores.RESET}")


def inicio_deploy():
    """Marca o início do deploy com uma linha destacada."""
    separador("INÍCIO DO DEPLOY")


def fim_deploy():
    """Marca o fim do deploy com uma linha destacada."""
    separador("DEPLOY CONCLUÍDO")
    print()  # linha em branco no final


def resumo_erro(comando: str, erro: Any):
    """
    Exibe um resumo formatado de erro.
    Use dentro de try/except para mostrar o que falhou.
    """
    print(_formatar(f"Erro em '{comando}'", Cores.VERMELHO, "💥"))
    print(f"  {Cores.VERMELHO}{type(erro).__name__}: {erro}{Cores.RESET}")