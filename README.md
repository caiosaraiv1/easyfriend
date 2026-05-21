# EasyFriend

Plataforma de conexão entre imigrantes e estrangeiros que facilita a integração social por meio de matching por idioma, proximidade geográfica e país de origem — com agenda cultural, chat e sistema de apadrinhamento.

Desenvolvido pelo **Grupo 5 (Scrabgadun)** — Engenharia de Software · Universidade Presbiteriana Mackenzie.

---

## Visão Geral

O EasyFriend conecta pessoas que chegaram a uma nova cidade ou país a outras com perfis compatíveis, permitindo que encontrem amigos, mentores e eventos culturais próximos. O projeto é composto por uma API REST em Python (FastAPI) e um app iOS nativo em Swift.

---

## Arquitetura

```
easyfriend/
├── app/                  # API REST (Python · FastAPI)
│   ├── main.py
│   ├── database.py
│   ├── models/
│   │   ├── db_models.py          # ORM SQLAlchemy
│   │   └── repositorios_CRUD.py  # Repositórios de acesso ao banco
│   ├── routes/
│   │   ├── auth.py           # Autenticação JWT
│   │   ├── radar.py          # Matching entre usuários
│   │   ├── agenda.py         # Agenda cultural
│   │   ├── chat.py           # Mensagens
│   │   └── apadrinhamento.py # Sistema de mentoria
│   ├── services/
│   │   ├── radar_service.py
│   │   ├── agenda_service.py
│   │   ├── chat_service.py
│   │   └── apadrinhamento_service.py
│   └── patterns/
│       ├── strategy.py   # Padrão Strategy (critérios de busca)
│       └── observer.py   # Padrão Observer (notificações)
├── db/
│   ├── schema.sql        # DDL — criação das tabelas
│   └── seed.sql          # Dados iniciais
├── ios/                  # App iOS (Swift · SwiftUI)
│   └── EasyFriend/
│       ├── Models/
│       ├── Views/
│       ├── ViewModels/
│       └── Services/
├── docker-compose.yml
├── Makefile
└── .env.example
```

---

## Funcionalidades

**Radar (Matching)**
Busca usuários compatíveis com base em critério configurável — idioma, país de origem ou proximidade geográfica. Ao criar um match, o sistema aciona automaticamente os canais de notificação (push, e-mail, badge) via padrão Observer.

**Agenda Cultural**
Lista e filtra eventos próximos ao usuário. O filtro é intercambiável em tempo de execução — por tipo de evento (gastronomia, música, arte) ou por idioma — sem nenhum `if/else` espalhado nos serviços.

**Chat**
Troca de mensagens direta entre dois usuários. Cada mensagem enviada aciona o Observer, gerando notificações nos três canais.

**Apadrinhamento**
Sistema de mentoria onde um usuário experiente (padrinho) pode aceitar a solicitação de um recém-chegado (afilhado). A aceitação também aciona o Observer.

**Autenticação JWT**
Login via `POST /auth/login` retorna um token Bearer com validade de 24 h. O app iOS armazena o token no Keychain e o envia em cada requisição.

---

## Padrões de Projeto

### Strategy — Critérios de Busca

Implementado em `app/patterns/strategy.py`. Permite que o cliente (iOS) troque o filtro de busca sem alterar nenhuma classe existente no servidor.

| Estratégia | Critério |
|---|---|
| `BuscaPorIdioma` | Filtra pelo idioma do usuário ou evento |
| `BuscaPorPaisOrigem` | Filtra pelo país de origem do usuário |
| `BuscaPorProximidade` | Filtra por raio em km usando a fórmula de Haversine |
| `BuscaPorTipoEvento` | Filtra eventos da agenda por categoria |

`BuscaContext` mantém a estratégia ativa e delega a execução — nenhum `if/else` nos services.

### Observer — Sistema de Notificações

Implementado em `app/patterns/observer.py`. Desacopla a geração de eventos dos canais de saída.

| Observer | Comportamento |
|---|---|
| `PushNotifier` | Simula envio APNs/FCM |
| `EmailNotifier` | Simula envio via SendGrid/SES |
| `BadgeNotifier` | Incrementa o contador de não lidas |

Os services `RadarService`, `ChatService` e `ApadrinhamentoService` herdam de `EventoSubject` e chamam `self.notificar(evento)` no momento correto.

---

## Stack

| Camada | Tecnologia |
|---|---|
| API | Python 3.12 · FastAPI · Uvicorn |
| ORM | SQLAlchemy |
| Banco de dados | PostgreSQL 15 |
| Autenticação | JWT (python-jose · passlib/bcrypt) |
| Testes | pytest · httpx |
| Containerização | Docker · Docker Compose |
| App iOS | Swift · SwiftUI |

---

## Pré-requisitos

- Docker e Docker Compose instalados
- (Opcional, para dev local sem Docker) Python 3.12+ e PostgreSQL 15+

---

## Como Rodar

**1. Clone o repositório e configure o ambiente**

```bash
git clone <url-do-repo>
cd easyfriend
cp .env.example .env
# Edite .env com suas credenciais se necessário
```

**2. Suba os containers**

```bash
make up
```

Isso constrói a imagem da API, sobe o banco PostgreSQL, aplica o schema e insere os dados de seed automaticamente.

**3. Verifique se está funcionando**

```bash
curl http://localhost:8000/health
# → {"status":"ok","db":"ok","versao":"0.2.0"}
```

A documentação interativa estará disponível em `http://localhost:8000/docs`.

---

## Comandos Make

| Comando | Descrição |
|---|---|
| `make up` | Build e sobe todos os containers em background |
| `make down` | Para e remove os containers |
| `make logs` | Acompanha os logs em tempo real |
| `make test` | Executa a suite de testes com pytest |
| `make build` | Rebuild completo sem cache |

---

## Variáveis de Ambiente

Copie `.env.example` para `.env` e ajuste os valores:

```env
POSTGRES_USER=easyfriend
POSTGRES_PASSWORD=changeme
POSTGRES_DB=easyfriend_db
DATABASE_URL=postgresql://easyfriend:changeme@db:5432/easyfriend_db

# Chave secreta para assinar tokens JWT — troque em produção
SECRET_KEY=changeme
```

---

## Endpoints Principais

### Auth
| Método | Rota | Descrição |
|---|---|---|
| POST | `/auth/login` | Retorna token JWT |
| GET | `/auth/me` | Dados do usuário autenticado |

### Radar
| Método | Rota | Descrição |
|---|---|---|
| GET | `/radar/matches` | Busca usuários pelo critério (`idioma`, `pais_origem`, `proximidade`) |
| POST | `/radar/matches` | Cria match entre dois usuários |

### Agenda
| Método | Rota | Descrição |
|---|---|---|
| GET | `/agenda/eventos` | Lista eventos filtrados por tipo ou idioma |
| POST | `/agenda/eventos` | Cria novo evento |

### Chat
| Método | Rota | Descrição |
|---|---|---|
| POST | `/chat/mensagens` | Envia mensagem |
| GET | `/chat/mensagens/{id}` | Busca mensagem por ID |
| GET | `/chat/conversa` | Histórico entre dois usuários |

### Apadrinhamento
| Método | Rota | Descrição |
|---|---|---|
| POST | `/apadrinhamento/solicitar` | Cria solicitação de mentoria |
| PATCH | `/apadrinhamento/{id}/aceitar` | Aceita solicitação |

---

## Testes

```bash
# Via Make (recomendado — roda dentro do container)
make test

# Diretamente com pytest (ambiente local)
cd app
pytest -q
```

Os testes cobrem rotas (`tests/test_routes.py`), services (`tests/test_services.py`) e os padrões de projeto (`patterns/test_patterns.py`).

---

## App iOS

O app em SwiftUI consome a API REST e implementa as seguintes telas:

- **LoginScreen** — autenticação e armazenamento do token no Keychain
- **RadarScreen** — mapa com `MapCircle` mostrando usuários por raio de privacidade
- **DetalhesMatchScreen** — perfil do match com opção de iniciar conversa
- **AgendaScreen** — lista de eventos culturais próximos
- **PerfilScreen** — dados do usuário autenticado

Para rodar o app, abra `ios/EasyFriend/EasyFriend.xcodeproj` no Xcode e aponte o `APIClient` para `http://localhost:8000` (ou o IP da sua máquina na rede local).

---

## Banco de Dados

O schema é aplicado automaticamente pelo Docker Compose na primeira inicialização (`db/schema.sql`). As tabelas principais são:

- `usuarios` — perfis com idioma, país de origem e coordenadas GPS
- `matches` — pares de usuários conectados pelo Radar
- `eventos` — agenda cultural com tipo e idioma
- `mensagens` — histórico de chat
- `apadrinhamentos` — vínculos padrinho → afilhado

Índices de performance estão criados sobre as colunas mais consultadas pelas estratégias de busca (`idioma`, `pais_origem`, `lat`, `lon`).
