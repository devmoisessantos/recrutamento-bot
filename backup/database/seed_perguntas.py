import asyncio
import json
from sqlalchemy import select, func

from src.database.connection import async_session, init_db
from src.database.models import Pergunta



PERGUNTAS = [
    ("Para que serve o comando \"Toggle\" (F7)?",
     ["Guardar veículos", "Praticar ações ilegais", "Entrar e sair de serviço"], "C"),
    ("Sobre o uso do uniforme e toggle:",
     ["Pode usar uniforme fora de serviço se estiver sem cometer crimes",
      "O uniforme só deve ser usado com toggle ligado e em serviço",
      "O toggle é opcional durante o expediente"], "B"),
    ("Um enfermeiro decide sair do hospital uniformizado para ajudar na rua. Isso é:",
     ["Permitido em emergências", "Permitido com autorização",
      "Proibido, enfermeiros atuam apenas no hospital"], "C"),
    ("Se o paciente recusar a cobrança, você deve NEGAR atendimento?",
     ["Sim, não sou obrigado", "Talvez, se eu não conhecer a pessoa",
      "Apenas em atendimento externo"], "C"),
    ("Você saiu do hospital rapidamente para resolver algo fora e esqueceu o toggle ligado. O correto seria:",
     ["Manter ligado pois foi rápido", "Desligar o toggle antes de sair do hospital",
      "Ignorar, pois não afeta o serviço"], "B"),
    ("O que NÃO é permitido durante o serviço?",
     ["Atender pacientes", "Ficar ausente farmando salário", "Usar rádio"], "B"),
    ("Qual o valor correto de reanimação no hospital?",
     ["5.000", "8.000", "10.000"], "B"),
    ("O que acontece na 3ª advertência?",
     ["Após 2 advertências ocorre exoneração", "3ª advertência resulta em exoneração",
      "Advertências são apenas avisos sem punição"], "B"),
    ("Você sendo membro do HP, pode se envolver com outras organizações (ilegais) durante o serviço?",
     ["Sim, se não for pego", "Não, é totalmente proibido", "Depende da situação"], "B"),
    ("Durante atendimento interno, qual conduta é obrigatória?",
     ["Permanecer na rádio 12 e, se possível, na call do hospital",
      "Usar qualquer rádio disponível", "Não é necessário comunicação"], "A"),
    ("Ao prosseguir, você confirma que leu e concorda com todas as regras do HP?",
     ["Estou ciente e concordo com todas as regras", "Não concordo"], "A"),
]


async def seed():
    await init_db()
    async with async_session() as session:
        for i, (enunciado, opcoes, correta) in enumerate(PERGUNTAS, start=1):
            session.add(Pergunta(
                ordem=i,
                enunciado=enunciado,
                opcoes=json.dumps(opcoes, ensure_ascii=False),
                resposta_correta=correta,
            ))
        await session.commit()
    print("As 11 Perguntas foram inseridas com sucesso.")




async def seed_perguntas_se_vazio():
    async with async_session() as session:
        resultado = await session.execute(select(func.count()).select_from(Pergunta))
        total = resultado.scalar_one()

        if total > 0:
            return  # já tem perguntas, não faz nada

        for i, (enunciado, opcoes, correta) in enumerate(PERGUNTAS, start=1):
            session.add(Pergunta(
                ordem=i,
                enunciado=enunciado,
                opcoes=json.dumps(opcoes, ensure_ascii=False),
                resposta_correta=correta,
            ))
        await session.commit()
        print(f"{len(PERGUNTAS)} perguntas inseridas automaticamente (tabela estava vazia).")


if __name__ == "__main__":
    asyncio.run(seed())