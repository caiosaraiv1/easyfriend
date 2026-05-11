-- =============================================================
-- EasyFriend - Seed de Dados para Demo
-- Scrabgadun - Grupo 5 | Mackenzie | Engenharia de Software
-- M3-02: 10 usuários, 5 eventos, 3 matches
-- =============================================================

-- Limpa os dados anteriores (mantém a estrutura das tabelas)
-- A ordem importa por causa das foreign keys
TRUNCATE TABLE apadrinhamentos RESTART IDENTITY CASCADE;
TRUNCATE TABLE mensagens       RESTART IDENTITY CASCADE;
TRUNCATE TABLE matches         RESTART IDENTITY CASCADE;
TRUNCATE TABLE eventos         RESTART IDENTITY CASCADE;
TRUNCATE TABLE usuarios        RESTART IDENTITY CASCADE;

-- =============================================================
-- USUÁRIOS (10 usuários de diferentes países e idiomas)
-- Senhas são todas "senha123" (hash fictício para demo)
-- lat/lon aproximadas de São Paulo e região
-- =============================================================
INSERT INTO usuarios (nome, email, senha_hash, idioma, pais_origem, lat, lon) VALUES
-- Brasileiros
('Carlos Silva',      'carlos@email.com',   'hash_senha123', 'pt', 'Brasil',     -23.5505, -46.6333),
('Ana Souza',         'ana@email.com',       'hash_senha123', 'pt', 'Brasil',     -23.5600, -46.6500),

-- Venezuelanos
('Maria Gonzalez',    'maria@email.com',     'hash_senha123', 'es', 'Venezuela',  -23.5450, -46.6200),
('Pedro Ramirez',     'pedro@email.com',     'hash_senha123', 'es', 'Venezuela',  -23.5700, -46.6400),

-- Haitianos
('Jean Baptiste',     'jean@email.com',      'hash_senha123', 'fr', 'Haiti',      -23.5300, -46.6100),
('Marie Claire',      'marie@email.com',     'hash_senha123', 'fr', 'Haiti',      -23.5550, -46.6450),

-- Bolivianos
('Luis Mamani',       'luis@email.com',      'hash_senha123', 'es', 'Bolivia',    -23.5800, -46.6600),
('Rosa Quispe',       'rosa@email.com',      'hash_senha123', 'es', 'Bolivia',    -23.5650, -46.6350),

-- Angolanos
('Diogo Ferreira',    'diogo@email.com',     'hash_senha123', 'pt', 'Angola',     -23.5400, -46.6250),

-- Sírio
('Amir Hassan',       'amir@email.com',      'hash_senha123', 'ar', 'Siria',      -23.5750, -46.6550);

-- =============================================================
-- EVENTOS (5 eventos da Agenda Cultural)
-- Variados por tipo e idioma para testar BuscaPorTipoEvento
-- e BuscaPorIdioma do padrão Strategy
-- =============================================================
INSERT INTO eventos (titulo, tipo, idioma, lat, lon, data_evento) VALUES
(
    'Festa Junina do Centro Cultural',
    'gastronomia',
    'pt',
    -23.5505, -46.6333,
    NOW() + INTERVAL '7 days'
),
(
    'Show de Música Latina',
    'musica',
    'es',
    -23.5600, -46.6500,
    NOW() + INTERVAL '10 days'
),
(
    'Exposição de Arte Haitiana',
    'arte',
    'fr',
    -23.5450, -46.6200,
    NOW() + INTERVAL '14 days'
),
(
    'Aula de Português para Migrantes',
    'educacao',
    'pt',
    -23.5700, -46.6400,
    NOW() + INTERVAL '3 days'
),
(
    'Festival Gastronômico Internacional',
    'gastronomia',
    'pt',
    -23.5300, -46.6100,
    NOW() + INTERVAL '20 days'
);

-- =============================================================
-- MATCHES (3 matches entre usuários)
-- Esses matches simulam o que o RadarService gera,
-- acionando o padrão Observer (PushNotifier, EmailNotifier)
-- =============================================================
INSERT INTO matches (usuario_id_1, usuario_id_2, status) VALUES
(1, 3, 'aceito'),   -- Carlos (BR/pt) <-> Maria (Venezuela/es)
(2, 5, 'aceito'),   -- Ana (BR/pt)    <-> Jean (Haiti/fr)
(4, 7, 'pendente'); -- Pedro (Venezuela/es) <-> Luis (Bolivia/es)

-- =============================================================
-- MENSAGENS (algumas mensagens de exemplo no chat)
-- Simula o ChatService que aciona o Observer ao receber msg
-- =============================================================
INSERT INTO mensagens (remetente_id, destinatario_id, conteudo) VALUES
(1, 3, 'Olá Maria, tudo bem? Vi que estamos próximos no radar!'),
(3, 1, 'Hola Carlos! Sí, todo bien. Que bueno conocerte.'),
(2, 5, 'Oi Jean, bem-vindo ao Brasil! Posso te ajudar com algo?'),
(5, 2, 'Merci Ana! Je cherche un cours de portugais.');

-- =============================================================
-- APADRINHAMENTOS (1 exemplo de solicitação de mentoria)
-- =============================================================
INSERT INTO apadrinhamentos (padrinho_id, afilhado_id, status) VALUES
(1, 5, 'aceito'),   -- Carlos apadrinha Jean
(2, 3, 'pendente'); -- Ana solicitou apadrinhar Maria

-- =============================================================
-- FIM DO SEED
-- =============================================================
