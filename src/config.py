import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
DATABASE_URL = os.getenv("DATABASE_URL")
# preencha com o ID do canal onde o painel vai ficar
CANAL_PAINEL_RECRUTAMENTO_ID = 1486369071590281326
LOGO_PATH = "assets/logo.png"

BACKUP_DIR = os.getenv("BACKUP_DIR", "data/backups")
MAX_BACKUPS_PER_GUILD = int(os.getenv("MAX_BACKUPS_PER_GUILD", 10))
AUTO_BACKUP_INTERVAL_HOURS = int(os.getenv("AUTO_BACKUP_INTERVAL_HOURS", 24))
LOG_CHANNEL_NAME = os.getenv("LOG_CHANNEL_NAME", "backup-logs")
ADMIN_ROLE_NAMES = [
    r.strip() for r in os.getenv("ADMIN_ROLE_NAMES", "Admin,Fundador").split(",") if r.strip()
]
CONFIRMATION_TIMEOUT = int(os.getenv("CONFIRMATION_TIMEOUT", 30))

if not DISCORD_TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN não definido. Crie um arquivo .env baseado em .env.example."
    )


# IDs dos cargos
CARGOS = {

    "Visitantes": 1486368796758507590,
    "ESTUDANTE": 1486368795739291690,
    "PROVA": 1486368794795573308,
    "Aprovado": 1522576790445621301,
    "HP S・Valley": 1486368783835725955,
    "🔰・Enfermeiro (a)": 1486368782585954405,
    "🚑・Paramédico": 1522567683269333012,
    "🥼・Doutor": 1486368765330591754,
    "🩺・Psicólogo": 1486368764059451503,
    "✈️・Recrutador": 1486368762369282179,
    "🚑・Instrutor Resgate": 1506834191126630521,
    "🥼・Instrutor": 1486368762872594534,
    "👑・Responsável Doutor・🥼": 1486368760536240340,
    "👑・Responsável Psicólogo・🧠": 1486368759227613235,
    "👑・Responsável Instrutor・🎓": 1486368758363586592,
    "👑・Responsável Recrutamento・🎯": 1486368757440970803,
    "👑・Responsável Destaque・👑": 1496398147642069063,
    "🛡️・【 GATE 】CMS  ·  Valley": 1515898748763508907,
    "⚔️・【 GATE 】GUARDIÃO": 1515670358261497906,
    "⚔️・【 GATE 】OPERADOR": 1515670175125475469,
    "🛡️・【 GATE 】CAPITÃO": 1515670028999983175,
    "🛡️・【 GATE 】COORDENADOR・TÁTICO": 1515669916785836144,
    "👑・【 GATE 】SUBCOMANDANTE・TÁTICO": 1515669807293403217,
    "👑・【 GATE 】COMANDANTE・TÁTICO": 1515669491038818415,
    "👑・SUPERVISOR": 1522581678072004649,
    "👑・VICE DIRETOR": 1522581475118289036,
    "👑・DIRETOR": 1486368748502781983,
    "🔍・COORDENADOR": 1486368746678386688,
    "👑 |  VICE DIRETOR GERAL": 1486368745252192256,
    "👑 |  DIRETOR GERAL": 1486368744195227780,
    "👑 | RESPONSÁVEL GERAL": 1425163342611349574,
    "Responsavel HP": 1325206480541978643,
    "Supervisor NW": 1325206480558882829

}

CARGOS_HIERARQUIA = [

    "Responsavel HP",
    "👑 | RESPONSÁVEL GERAL",
    "👑 |  DIRETOR GERAL",
    "👑 |  VICE DIRETOR GERAL",
    "🔍・COORDENADOR",
    "👑・Responsável Instrutor・🎓",
    "👑・Responsável Recrutamento・🎯",
    "👑・Responsável Psicólogo・🧠",
    "👑・Responsável Doutor・🥼",
    "👑・DIRETOR",
    "👑・VICE DIRETOR",
    "👑・SUPERVISOR",
    "🥼・Instrutor",
    "🚑・Instrutor Resgate",
    "✈️・Recrutador",
    "🩺・Psicólogo",
    "🥼・Doutor",
    "🚑・Paramédico",
    "🔰・Enfermeiro (a)",
]

CARGOS_EXCLUIR_HIERARQUIA = [
    "🛡️・【 GATE 】CMS  ·  Valley",
]

HIERARQUIA_GATE = [

    "👑・【 GATE 】COMANDANTE・TÁTICO",
    "👑・【 GATE 】SUBCOMANDANTE・TÁTICO",
    "🛡️・【 GATE 】COORDENADOR・TÁTICO",
    "🛡️・【 GATE 】CAPITÃO",
    "⚔️・【 GATE 】OPERADOR",
    "⚔️・【 GATE 】GUARDIÃO"
]


# Hierarquia: define quem pode conceder cargos a algum usuário.
HIERARQUIA_CONCESSAO = {

    "Visitantes": None,
    "ESTUDANTE": "✈️・Recrutador",
    "PROVA": "✈️・Recrutador",
    "Aprovado": "✈️・Recrutador",
    "HP S・Valley": None,
    "🔰・Enfermeiro (a)": "✈️・Recrutador",
    "🚑・Paramédico": "✈️・Recrutador",
    "🥼・Doutor": "👑・DIRETOR",
    "🩺・Psicólogo": "👑・DIRETOR",
    "✈️・Recrutador": "👑・DIRETOR",
    "🚑・Instrutor Resgate": "👑・DIRETOR",
    "🥼・Instrutor": "👑・DIRETOR",
    "👑・Responsável Doutor・🥼": "👑 |  VICE DIRETOR GERAL",
    "👑・Responsável Psicólogo・🧠": "👑 |  VICE DIRETOR GERAL",
    "👑・Responsável Instrutor・🎓": "👑 |  VICE DIRETOR GERAL",
    "👑・Responsável Recrutamento・🎯": "👑 |  VICE DIRETOR GERAL",
    "👑・Responsável Destaque・👑": "👑 |  DIRETOR GERAL",
    "⚔️・【 GATE 】GUARDIÃO": "🛡️・【 GATE 】COORDENADOR・TÁTICO",
    "⚔️・【 GATE 】OPERADOR": "🛡️・【 GATE 】COORDENADOR・TÁTICO",
    "🛡️・【 GATE 】CAPITÃO": "🛡️・【 GATE 】COORDENADOR・TÁTICO",
    "🛡️・【 GATE 】COORDENADOR・TÁTICO": "👑・【 GATE 】SUBCOMANDANTE・TÁTICO",
    "👑・【 GATE 】SUBCOMANDANTE・TÁTICO": "👑・【 GATE 】COMANDANTE・TÁTICO",
    "👑・【 GATE 】COMANDANTE・TÁTICO": "👑 | RESPONSÁVEL GERAL",
    "👑・SUPERVISOR": "👑・DIRETOR",
    "👑・VICE DIRETOR": "👑 |  VICE DIRETOR GERAL",
    "👑・DIRETOR": "👑 |  VICE DIRETOR GERAL",
    "🔍・COORDENADOR": "👑 |  VICE DIRETOR GERAL",
    "👑 |  VICE DIRETOR GERAL": "👑 |  DIRETOR GERAL",
    "👑 |  DIRETOR GERAL": "👑 | RESPONSÁVEL GERAL",
    "👑 | RESPONSÁVEL GERAL": "Responsavel HP",
    "Responsavel HP": "Supervisor NW"

}

TOTAL_PERGUNTAS_PROVA = 11
COOLDOWN_REPROVACAO_HORAS = 24
TEMPO_LIMITE_PROVA_MINUTOS = 60
NOTA_MINIMA_APROVACAO = 70

CANAIS = {
    "MANAGE_ROLE_CHANNEL_ID": 1529960097130741801,
    "WHITELIST_CANAL_ID": 1528299364970266657,
    "HIERARQUIA_SUL": 1487250788391583745,
    "MATERIAL_ESTUDO": 1486369061507043348,
    "AVALIACAO": 1486369066091282623,
    "APROVAR_REPROVAR": 1526595318974517340,
    "RECRUTAMENTOS": 1486369074341613638,
    "LOG_WHITELIST": 1528352488028246137,
    "LOG_RECRUTAMENTOS": 1486369287139754014,
    "LOG_APROVACOES": 1526596056274567299,
    "LOG_REPROVACOES": 1526596314744492134,
    "LOG_CARGOS": 1526596799509561404,
    "LOG_ERROS": 1526596982066380990
}

PREFIXOS_NICKNAME = {
    "🔰・Enfermeiro (a)": "[ ENF ]",
    "🚑・Paramédico": "[ PAR ]",
    "🩺・Psicólogo": "[ PSI ]",
    "✈️・Recrutador": "[ REC ]",
    "🥼・Instrutor": "[ INS ]",
    "👑・VICE DIRETOR": "[ V・DIR ]",
    "👑・DIRETOR": "[ DIR ]",
    "🔍・COORDENADOR": "[ COR ]",
    "👑 |  VICE DIRETOR GERAL": "[V.DIR.G]",
    "👑 |  DIRETOR GERAL": "⟦DIR · G⟧",
    "👑 | RESPONSÁVEL GERAL": "⟦RESP · G⟧"
}

ESCOPOS_GERENCIAMENTO = {
    "dono": {
        "cargos_autorizados": [
            "Responsavel HP",
        ],
        "cargos_gerenciaveis": [
            "👑 | RESPONSÁVEL GERAL",
            "👑 |  DIRETOR GERAL",
            "👑 |  VICE DIRETOR GERAL",
            "👑・【 GATE 】COMANDANTE・TÁTICO",
            "👑・【 GATE 】SUBCOMANDANTE・TÁTICO",
            "🛡️・【 GATE 】COORDENADOR・TÁTICO",
            "🛡️・【 GATE 】CAPITÃO",
            "⚔️・【 GATE 】OPERADOR",
            "⚔️・【 GATE 】GUARDIÃO",
            "🛡️・【 GATE 】CMS  ·  Valley",            
            "🔍・COORDENADOR",
            "👑・Responsável Instrutor・🎓",
            "👑・Responsável Recrutamento・🎯",
            "👑・Responsável Psicólogo・🧠",
            "👑・Responsável Doutor・🥼",
            "👑・DIRETOR",
            "👑・VICE DIRETOR",
            "👑・SUPERVISOR",
            "🥼・Instrutor",
            "🚑・Instrutor Resgate",
            "✈️・Recrutador",
            "🩺・Psicólogo",
            "🥼・Doutor",
            "🚑・Paramédico",
            "🔰・Enfermeiro (a)",
        ],
    },
    "gate": {
        "cargos_autorizados": [
            "👑・【 GATE 】COMANDANTE・TÁTICO",
            "👑・【 GATE 】SUBCOMANDANTE・TÁTICO",
        ],
        "cargos_gerenciaveis": [
            "🛡️・【 GATE 】COORDENADOR・TÁTICO",
            "🛡️・【 GATE 】CAPITÃO",
            "⚔️・【 GATE 】OPERADOR",
            "⚔️・【 GATE 】GUARDIÃO",
            "🛡️・【 GATE 】CMS  ·  Valley",
        ],
    },
    "diretoria": {
        "cargos_autorizados": [
            "🔍・COORDENADOR",
            "👑・DIRETOR",
            "👑・VICE DIRETOR",
            "👑・SUPERVISOR"
        ],
        "cargos_gerenciaveis": {
            "🔍・COORDENADOR": [
                "👑・DIRETOR",
                "👑・VICE DIRETOR",
                "👑・SUPERVISOR",
                "🥼・Instrutor",
                "🚑・Instrutor Resgate",
                "✈️・Recrutador",
                "🩺・Psicólogo",
                "🥼・Doutor",
                "🚑・Paramédico",
                "🔰・Enfermeiro (a)"
            ],
            "👑・DIRETOR": [
                "👑・VICE DIRETOR",
                "👑・SUPERVISOR",
                "🥼・Instrutor",
                "🚑・Instrutor Resgate",
                "✈️・Recrutador",
                "🩺・Psicólogo",
                "🥼・Doutor",
                "🚑・Paramédico",
                "🔰・Enfermeiro (a)"
            ],
            "👑・VICE DIRETOR": [
                "👑・SUPERVISOR",
                "🥼・Instrutor",
                "🚑・Instrutor Resgate",
                "✈️・Recrutador",
                "🩺・Psicólogo",
                "🥼・Doutor",
                "🚑・Paramédico",
                "🔰・Enfermeiro (a)"
            ],
            "👑・SUPERVISOR": [
                "🥼・Instrutor",
                "🚑・Instrutor Resgate",
                "✈️・Recrutador",
                "🩺・Psicólogo",
                "🥼・Doutor",
                "🚑・Paramédico",
                "🔰・Enfermeiro (a)"
            ]
        },
    },
    "geral": {
        "cargos_autorizados": [
            "👑 | RESPONSÁVEL GERAL",
            "👑 |  DIRETOR GERAL",
            "👑 |  VICE DIRETOR GERAL"
        ],
        "cargos_gerenciaveis": {
            "👑 | RESPONSÁVEL GERAL": [
                "👑 |  DIRETOR GERAL",
                "👑 |  VICE DIRETOR GERAL",
                "👑・【 GATE 】COMANDANTE・TÁTICO",
                "👑・【 GATE 】SUBCOMANDANTE・TÁTICO",
                "🛡️・【 GATE 】COORDENADOR・TÁTICO",
                "🛡️・【 GATE 】CAPITÃO",
                "⚔️・【 GATE 】OPERADOR",
                "⚔️・【 GATE 】GUARDIÃO",
                "🛡️・【 GATE 】CMS  ·  Valley",            
                "🔍・COORDENADOR",
                "👑・Responsável Instrutor・🎓",
                "👑・Responsável Recrutamento・🎯",
                "👑・Responsável Psicólogo・🧠",
                "👑・Responsável Doutor・🥼",
                "👑・DIRETOR",
                "👑・VICE DIRETOR",
                "👑・SUPERVISOR",
                "🥼・Instrutor",
                "🚑・Instrutor Resgate",
                "✈️・Recrutador",
                "🩺・Psicólogo",
                "🥼・Doutor",
                "🚑・Paramédico",
                "🔰・Enfermeiro (a)"

            ],
            "👑 |  DIRETOR GERAL": [
                "👑 |  VICE DIRETOR GERAL",
                "👑・【 GATE 】COMANDANTE・TÁTICO",
                "👑・【 GATE 】SUBCOMANDANTE・TÁTICO",
                "🛡️・【 GATE 】COORDENADOR・TÁTICO",
                "🛡️・【 GATE 】CAPITÃO",
                "⚔️・【 GATE 】OPERADOR",
                "⚔️・【 GATE 】GUARDIÃO",
                "🛡️・【 GATE 】CMS  ·  Valley",            
                "🔍・COORDENADOR",
                "👑・Responsável Instrutor・🎓",
                "👑・Responsável Recrutamento・🎯",
                "👑・Responsável Psicólogo・🧠",
                "👑・Responsável Doutor・🥼",
                "👑・DIRETOR",
                "👑・VICE DIRETOR",
                "👑・SUPERVISOR",
                "🥼・Instrutor",
                "🚑・Instrutor Resgate",
                "✈️・Recrutador",
                "🩺・Psicólogo",
                "🥼・Doutor",
                "🚑・Paramédico",
                "🔰・Enfermeiro (a)"
            ],
            "👑 |  VICE DIRETOR GERAL": [
                "👑・【 GATE 】COMANDANTE・TÁTICO",
                "👑・【 GATE 】SUBCOMANDANTE・TÁTICO",
                "🛡️・【 GATE 】COORDENADOR・TÁTICO",
                "🛡️・【 GATE 】CAPITÃO",
                "⚔️・【 GATE 】OPERADOR",
                "⚔️・【 GATE 】GUARDIÃO",
                "🛡️・【 GATE 】CMS  ·  Valley",            
                "🔍・COORDENADOR",
                "👑・Responsável Instrutor・🎓",
                "👑・Responsável Recrutamento・🎯",
                "👑・Responsável Psicólogo・🧠",
                "👑・Responsável Doutor・🥼",
                "👑・DIRETOR",
                "👑・VICE DIRETOR",
                "👑・SUPERVISOR",
                "🥼・Instrutor",
                "🚑・Instrutor Resgate",
                "✈️・Recrutador",
                "🩺・Psicólogo",
                "🥼・Doutor",
                "🚑・Paramédico",
                "🔰・Enfermeiro (a)"
            ],
        },
    },
}


LIMITE_REMOCOES_SUSPEITAS = 5
# 1,5 minutos — mude só este número se quiser ajustar no futuro
JANELA_TEMPO_SUSPEITA_SEGUNDOS = 90
