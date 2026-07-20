# Discord Backup Bot — Cidade RP

Bot de backup e restauração para servidores Discord de Roleplay, feito em Python (discord.py 2.x).

## Recursos

- `/backup criar` — backup manual instantâneo
- `/backup listar` — lista backups salvos
- `/backup exportar` — baixa um backup como arquivo `.json`
- `/backup deletar` — remove um backup específico
- Backup automático agendado (intervalo configurável, padrão 24h)
- `/diff` — compara um backup com o estado atual do servidor, sem alterar nada
- `/restore cargos` / `/restore canais` / `/restore membros` / `/restore tudo` — restauração seletiva, sempre com prévia (dry-run) e confirmação por botão
- Backup de segurança automático criado antes de qualquer restauração
- Logs detalhados em um canal `#backup-logs`
- Controle de permissão: só Administradores ou cargos configurados podem usar `/backup` e `/restore`

## O que é salvo no backup

Cargos (nome, cor, permissões, hierarquia), categorias, canais (nome, tópico, permissões, slowmode etc.), emojis, configurações gerais do servidor, e cargos/apelidos dos membros atuais.

**Limitação importante do Discord:** não é possível re-adicionar ao servidor membros que saíram — isso não é permitido pela API para nenhum bot. O `/restore membros` só reaplica cargos/apelidos de quem ainda está no servidor.

## Configuração inicial

1. Crie uma aplicação em https://discord.com/developers/applications
2. Na aba **Bot**, ative os **Privileged Gateway Intents**: `SERVER MEMBERS INTENT`
3. Gere o link de convite em **OAuth2 > URL Generator** com os escopos `bot` e `applications.commands`, e permissões: `Manage Roles`, `Manage Channels`, `Manage Nicknames`, `View Channels`, `Send Messages`, `Attach Files`
4. Copie o token do bot para o arquivo `.env` (baseado em `.env.example`)
5. Crie manualmente um canal de texto chamado `backup-logs` no seu servidor (ou mude `LOG_CHANNEL_NAME` no `.env`)

## Rodando localmente

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # edite com seu token
python bot.py
```

## Hospedagem

**Vercel não é compatível** com este tipo de bot: Vercel roda funções serverless de curta duração, e um bot Discord precisa manter uma conexão WebSocket persistente 24/7.

**Render funciona bem**, mas é preciso:
1. Criar o serviço como **Background Worker** (não "Web Service")
2. Usar um **disco persistente** (veja `render.yaml`, plano pago a partir de poucos dólares/mês) — sem isso, os backups em JSON são apagados a cada novo deploy
3. Configurar a variável `DISCORD_TOKEN` no painel do Render (não vai no `render.yaml` por segurança)

Deploy com o arquivo incluso:
```bash
# No painel do Render: New > Blueprint > conecte o repositório
# Ele vai detectar o render.yaml automaticamente
```

## Estrutura do projeto

```
discord-backup-bot/
├── bot.py                  # entrada principal
├── config.py                # variáveis de ambiente
├── core/
│   ├── backup_manager.py    # criação/salvamento/leitura de backups
│   ├── diff_engine.py       # comparação backup vs atual
│   ├── restore_manager.py   # aplica restaurações (com dry_run)
│   └── logger.py            # logs em canal Discord
├── cogs/
│   ├── backup.py             # /backup ...
│   ├── restore.py            # /restore ...
│   ├── diff.py                # /diff
│   └── status.py              # /status
├── utils/
│   ├── permissions.py        # checagem de cargo/admin
│   └── views.py                # botões de confirmação
├── data/backups/              # arquivos JSON (criado automaticamente)
├── render.yaml
└── requirements.txt
```

## Próximos passos sugeridos

- Restaurar overwrites de permissão por canal/categoria (atualmente só é comparado no `/diff`, não reaplicado no restore — pode ser adicionado)
- Exportar backups automaticamente para um repositório Git privado ou S3, como camada extra de segurança
- Comando `/backup agendar` para o próprio staff ajustar o intervalo sem mexer no `.env`
