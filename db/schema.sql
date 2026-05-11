-- =============================================================
-- EasyFriend - Schema DDL
-- Scrabgadun - Grupo 5 | Mackenzie | Engenharia de Software
-- M3-01: Criação de todas as tabelas do banco de dados
-- =============================================================

-- Garante que o script pode ser rodado múltiplas vezes sem erro
-- (útil durante desenvolvimento)

-- =============================================================
-- TABELA: usuarios
-- Armazena todos os usuários do app EasyFriend.
-- Colunas idioma, pais_origem, lat e lon são usadas pelo
-- padrão Strategy no RadarService (BuscaPorIdioma,
-- BuscaPorPaisOrigem, BuscaPorProximidade).
-- =============================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id          SERIAL PRIMARY KEY,
    nome        VARCHAR(100)        NOT NULL,
    email       VARCHAR(255)        NOT NULL UNIQUE,
    senha_hash  VARCHAR(255)        NOT NULL,
    idioma      VARCHAR(50)         NOT NULL,           -- ex: "pt", "en", "es"
    pais_origem VARCHAR(100)        NOT NULL,           -- ex: "Brasil", "Venezuela"
    lat         DOUBLE PRECISION    NOT NULL DEFAULT 0, -- latitude GPS
    lon         DOUBLE PRECISION    NOT NULL DEFAULT 0, -- longitude GPS
    created_at  TIMESTAMP           NOT NULL DEFAULT NOW()
);

-- =============================================================
-- TABELA: matches
-- Gerado pelo RadarService quando dois usuários se conectam.
-- O padrão Observer dispara PushNotifier e EmailNotifier
-- assim que um match é inserido aqui.
-- =============================================================
CREATE TABLE IF NOT EXISTS matches (
    id            SERIAL PRIMARY KEY,
    usuario_id_1  INTEGER     NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    usuario_id_2  INTEGER     NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    status        VARCHAR(20) NOT NULL DEFAULT 'pendente', -- pendente | aceito | recusado
    created_at    TIMESTAMP   NOT NULL DEFAULT NOW(),

    -- Garante que não existam dois matches duplicados entre o mesmo par
    CONSTRAINT uq_match_par UNIQUE (usuario_id_1, usuario_id_2),
    -- Garante que um usuário não faça match consigo mesmo
    CONSTRAINT chk_match_diferente CHECK (usuario_id_1 <> usuario_id_2)
);

-- =============================================================
-- TABELA: eventos
-- Eventos da Agenda Cultural.
-- A coluna tipo é usada pelo padrão Strategy (BuscaPorTipoEvento)
-- e idioma por BuscaPorIdioma dentro do AgendaService.
-- =============================================================
CREATE TABLE IF NOT EXISTS eventos (
    id          SERIAL PRIMARY KEY,
    titulo      VARCHAR(200)        NOT NULL,
    tipo        VARCHAR(100)        NOT NULL,           -- ex: "gastronomia", "musica", "arte"
    idioma      VARCHAR(50)         NOT NULL,           -- idioma principal do evento
    lat         DOUBLE PRECISION    NOT NULL DEFAULT 0, -- localização do evento
    lon         DOUBLE PRECISION    NOT NULL DEFAULT 0,
    data_evento TIMESTAMP           NOT NULL,
    created_at  TIMESTAMP           NOT NULL DEFAULT NOW()
);

-- =============================================================
-- TABELA: mensagens
-- Mensagens trocadas no chat entre usuários.
-- O padrão Observer no ChatService dispara ao inserir aqui.
-- =============================================================
CREATE TABLE IF NOT EXISTS mensagens (
    id              SERIAL PRIMARY KEY,
    remetente_id    INTEGER     NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    destinatario_id INTEGER     NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    conteudo        TEXT        NOT NULL,
    created_at      TIMESTAMP   NOT NULL DEFAULT NOW(),

    -- Garante que um usuário não mande mensagem para si mesmo
    CONSTRAINT chk_msg_diferente CHECK (remetente_id <> destinatario_id)
);

-- =============================================================
-- TABELA: apadrinhamentos
-- Sistema de mentoria entre usuários (padrinho -> afilhado).
-- O Observer é acionado no PATCH /{id}/aceitar (M4-03).
-- =============================================================
CREATE TABLE IF NOT EXISTS apadrinhamentos (
    id          SERIAL PRIMARY KEY,
    padrinho_id INTEGER     NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    afilhado_id INTEGER     NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    status      VARCHAR(20) NOT NULL DEFAULT 'pendente', -- pendente | aceito | recusado
    created_at  TIMESTAMP   NOT NULL DEFAULT NOW(),

    -- Garante que não existam duas solicitações duplicadas
    CONSTRAINT uq_apadrinhamento_par UNIQUE (padrinho_id, afilhado_id),
    -- Garante que um usuário não apadrinhe a si mesmo
    CONSTRAINT chk_apadrinhamento_diferente CHECK (padrinho_id <> afilhado_id)
);

-- =============================================================
-- ÍNDICES DE PERFORMANCE (M3-05 antecipado)
-- Colunas consultadas frequentemente pelo padrão Strategy.
-- =============================================================

-- Buscas por proximidade (BuscaPorProximidade)
CREATE INDEX IF NOT EXISTS idx_usuarios_lat  ON usuarios(lat);
CREATE INDEX IF NOT EXISTS idx_usuarios_lon  ON usuarios(lon);

-- Buscas por idioma (BuscaPorIdioma)
CREATE INDEX IF NOT EXISTS idx_usuarios_idioma ON usuarios(idioma);

-- Buscas por país de origem (BuscaPorPaisOrigem)
CREATE INDEX IF NOT EXISTS idx_usuarios_pais_origem ON usuarios(pais_origem);

-- Buscas de eventos por tipo e idioma (BuscaPorTipoEvento / BuscaPorIdioma)
CREATE INDEX IF NOT EXISTS idx_eventos_tipo   ON eventos(tipo);
CREATE INDEX IF NOT EXISTS idx_eventos_idioma ON eventos(idioma);

-- Buscas de mensagens por conversa
CREATE INDEX IF NOT EXISTS idx_mensagens_remetente    ON mensagens(remetente_id);
CREATE INDEX IF NOT EXISTS idx_mensagens_destinatario ON mensagens(destinatario_id);
