import os 
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
DATABASE_URL = os.getenv("DATABASE_URL")

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
    "⚔️・【 GATE 】GUARDIÃO": 1515670358261497906,
    "⚔️・【 GATE 】OPERADOR": 1515670175125475469,    
    "🛡️・【 GATE 】CAPITÃO": 1515670028999983175,
    "🛡️・【 GATE 】COORDENADOR・TÁTICO": 1515669916785836144,   
    "👑・【 GATE 】SUBCOMANDANTE・TÁTICO": 1515669807293403217,
    "👑・【 GATE 】 COMANDANTE・TÁTICO": 1515669491038818415,
    "Supervisor": 1522581678072004649,  
    "Vice Diretor": 1522581475118289036,  
    "👑・DIRETOR": 1486368748502781983,  
    "🔍・Corregedoria": 1486368746678386688,
    "Vice Diretor Geral": 1486368745252192256,  
    "Diretor Geral": 1486368744195227780,
    "👑 Responsável Geral": 1425163342611349574,  
    "Responsavel HP": 1325206480541978643, 
    "Supervisor NW": 1325206480558882829

}

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
    "👑・Responsável Doutor・🥼": "Vice Diretor Geral",
    "👑・Responsável Psicólogo・🧠": "Vice Diretor Geral",
    "👑・Responsável Instrutor・🎓": "Vice Diretor Geral",
    "👑・Responsável Recrutamento・🎯": "Vice Diretor Geral",
    "👑・Responsável Destaque・👑": "Diretor Geral",
    "⚔️・【 GATE 】GUARDIÃO": "🛡️・【 GATE 】COORDENADOR・TÁTICO",
    "⚔️・【 GATE 】OPERADOR": "🛡️・【 GATE 】COORDENADOR・TÁTICO",    
    "🛡️・【 GATE 】CAPITÃO": "🛡️・【 GATE 】COORDENADOR・TÁTICO",
    "🛡️・【 GATE 】COORDENADOR・TÁTICO": "👑・【 GATE 】SUBCOMANDANTE・TÁTICO",   
    "👑・【 GATE 】SUBCOMANDANTE・TÁTICO": "👑・【 GATE 】 COMANDANTE・TÁTICO",
    "👑・【 GATE 】 COMANDANTE・TÁTICO": "👑 Responsável Geral",
    "Supervisor": "👑・DIRETOR",  
    "Vice Diretor": "Vice Diretor Geral",  
    "👑・DIRETOR": "Vice Diretor Geral",  
    "🔍・Corregedoria": "Vice Diretor Geral",
    "Vice Diretor Geral": "Diretor Geral",  
    "Diretor Geral": "👑 Responsável Geral",
    "👑 Responsável Geral": "Responsavel HP",  
    "Responsavel HP": "Supervisor NW"

}
   
COOLDOWN_REPROVACAO_HORAS = 24
TEMPO_LIMITE_PROVA_MINUTOS = 60
NOTA_MINIMA_APROVACAO = 70
    