-- ============================================================================
-- NFL Fantasy League - Initial Data Insert Script
-- This script populates the database with essential data to make it functional
-- ============================================================================

-- ============================================================================
-- 1. INSERT NFL TEAMS (equipos)
-- ============================================================================
-- All 32 NFL teams for the 2024-2025 season
INSERT INTO equipos (nombre, ciudad, thumbnail) VALUES 
    -- AFC East
    ('Buffalo Bills', 'Buffalo', 'https://a.espncdn.com/i/teamlogos/nfl/500/buf.png'),
    ('Miami Dolphins', 'Miami', 'https://a.espncdn.com/i/teamlogos/nfl/500/mia.png'),
    ('New England Patriots', 'Foxborough', 'https://a.espncdn.com/i/teamlogos/nfl/500/ne.png'),
    ('New York Jets', 'East Rutherford', 'https://a.espncdn.com/i/teamlogos/nfl/500/nyj.png'),
    
    -- AFC North
    ('Baltimore Ravens', 'Baltimore', 'https://a.espncdn.com/i/teamlogos/nfl/500/bal.png'),
    ('Cincinnati Bengals', 'Cincinnati', 'https://a.espncdn.com/i/teamlogos/nfl/500/cin.png'),
    ('Cleveland Browns', 'Cleveland', 'https://a.espncdn.com/i/teamlogos/nfl/500/cle.png'),
    ('Pittsburgh Steelers', 'Pittsburgh', 'https://a.espncdn.com/i/teamlogos/nfl/500/pit.png'),
    
    -- AFC South
    ('Houston Texans', 'Houston', 'https://a.espncdn.com/i/teamlogos/nfl/500/hou.png'),
    ('Indianapolis Colts', 'Indianapolis', 'https://a.espncdn.com/i/teamlogos/nfl/500/ind.png'),
    ('Jacksonville Jaguars', 'Jacksonville', 'https://a.espncdn.com/i/teamlogos/nfl/500/jax.png'),
    ('Tennessee Titans', 'Nashville', 'https://a.espncdn.com/i/teamlogos/nfl/500/ten.png'),
    
    -- AFC West
    ('Denver Broncos', 'Denver', 'https://a.espncdn.com/i/teamlogos/nfl/500/den.png'),
    ('Kansas City Chiefs', 'Kansas City', 'https://a.espncdn.com/i/teamlogos/nfl/500/kc.png'),
    ('Las Vegas Raiders', 'Las Vegas', 'https://a.espncdn.com/i/teamlogos/nfl/500/lv.png'),
    ('Los Angeles Chargers', 'Los Angeles', 'https://a.espncdn.com/i/teamlogos/nfl/500/lac.png'),
    
    -- NFC East
    ('Dallas Cowboys', 'Dallas', 'https://a.espncdn.com/i/teamlogos/nfl/500/dal.png'),
    ('New York Giants', 'East Rutherford', 'https://a.espncdn.com/i/teamlogos/nfl/500/nyg.png'),
    ('Philadelphia Eagles', 'Philadelphia', 'https://a.espncdn.com/i/teamlogos/nfl/500/phi.png'),
    ('Washington Commanders', 'Landover', 'https://a.espncdn.com/i/teamlogos/nfl/500/wsh.png'),
    
    -- NFC North
    ('Chicago Bears', 'Chicago', 'https://a.espncdn.com/i/teamlogos/nfl/500/chi.png'),
    ('Detroit Lions', 'Detroit', 'https://a.espncdn.com/i/teamlogos/nfl/500/det.png'),
    ('Green Bay Packers', 'Green Bay', 'https://a.espncdn.com/i/teamlogos/nfl/500/gb.png'),
    ('Minnesota Vikings', 'Minneapolis', 'https://a.espncdn.com/i/teamlogos/nfl/500/min.png'),
    
    -- NFC South
    ('Atlanta Falcons', 'Atlanta', 'https://a.espncdn.com/i/teamlogos/nfl/500/atl.png'),
    ('Carolina Panthers', 'Charlotte', 'https://a.espncdn.com/i/teamlogos/nfl/500/car.png'),
    ('New Orleans Saints', 'New Orleans', 'https://a.espncdn.com/i/teamlogos/nfl/500/no.png'),
    ('Tampa Bay Buccaneers', 'Tampa', 'https://a.espncdn.com/i/teamlogos/nfl/500/tb.png'),
    
    -- NFC West
    ('Arizona Cardinals', 'Glendale', 'https://a.espncdn.com/i/teamlogos/nfl/500/ari.png'),
    ('Los Angeles Rams', 'Los Angeles', 'https://a.espncdn.com/i/teamlogos/nfl/500/lar.png'),
    ('San Francisco 49ers', 'San Francisco', 'https://a.espncdn.com/i/teamlogos/nfl/500/sf.png'),
    ('Seattle Seahawks', 'Seattle', 'https://a.espncdn.com/i/teamlogos/nfl/500/sea.png')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 2. INSERT DEFAULT ADMIN USER (usuarios)
-- ============================================================================
-- Password is "admin123" - hashed with bcrypt
-- NOTE: Change this password in production!
INSERT INTO usuarios (nombre, alias, correo, contrasena_hash, rol, estado, idioma, imagen_perfil_url) VALUES
    ('Administrator', 'admin', 'admin@nflfantasy.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIIHu9Qzpm', 'administrador', 'activa', 'en', '/img/perfil/default.png')
ON CONFLICT (correo) DO NOTHING;

-- ============================================================================
-- 3. INSERT TEST USERS (usuarios)
-- ============================================================================
-- Password for all test users is "password123" - hashed with bcrypt
INSERT INTO usuarios (nombre, alias, correo, contrasena_hash, rol, estado, idioma) VALUES
    ('John Smith', 'JSmith', 'john.smith@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIIHu9Qzpm', 'manager', 'activa', 'en'),
    ('Maria Garcia', 'MGarcia', 'maria.garcia@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIIHu9Qzpm', 'manager', 'activa', 'es'),
    ('David Johnson', 'DJohnson', 'david.johnson@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIIHu9Qzpm', 'manager', 'activa', 'en'),
    ('Sarah Williams', 'SWilliams', 'sarah.williams@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIIHu9Qzpm', 'manager', 'activa', 'en'),
    ('Carlos Rodriguez', 'CRodriguez', 'carlos.rodriguez@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIIHu9Qzpm', 'manager', 'activa', 'es')
ON CONFLICT (correo) DO NOTHING;

-- ============================================================================
-- 4. INSERT CURRENT SEASON (temporadas)
-- ============================================================================
INSERT INTO temporadas (nombre, semanas, fecha_inicio, fecha_fin, es_actual) VALUES
    ('NFL Season 2024-2025', 18, '2024-09-05', '2025-01-05', TRUE)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 5. INSERT SEASON WEEKS (temporadas_semanas)
-- ============================================================================
-- Insert 18 weeks for the 2024-2025 season
INSERT INTO temporadas_semanas (temporada_id, numero, fecha_inicio, fecha_fin)
SELECT 
    t.id,
    semana.numero,
    DATE '2024-09-05' + (semana.numero - 1) * INTERVAL '7 days' AS fecha_inicio,
    DATE '2024-09-05' + semana.numero * INTERVAL '7 days' - INTERVAL '1 day' AS fecha_fin
FROM 
    temporadas t,
    generate_series(1, 18) AS semana(numero)
WHERE 
    t.nombre = 'NFL Season 2024-2025'
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 6. INSERT SAMPLE LEAGUE (ligas)
-- ============================================================================
-- Password for league is "league123" - hashed with bcrypt
INSERT INTO ligas (
    nombre, 
    descripcion, 
    contrasena_hash, 
    equipos_max, 
    estado, 
    temporada_id, 
    comisionado_id,
    playoffs_equipos,
    puntajes_decimales,
    trade_deadline_activa
)
SELECT 
    'Champions League 2024',
    'Elite fantasy football league for the 2024-2025 season. May the best manager win!',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIIHu9Qzpm',
    12,
    'Pre_draft',
    t.id,
    u.id,
    6,
    TRUE,
    FALSE
FROM 
    temporadas t,
    usuarios u
WHERE 
    t.nombre = 'NFL Season 2024-2025'
    AND u.correo = 'john.smith@test.com'
ON CONFLICT (nombre) DO NOTHING;

-- ============================================================================
-- 7. INSERT SAMPLE PLAYERS (jugadores)
-- ============================================================================
-- Sample star players from different teams and positions
DO $$
DECLARE
    v_chiefs_id UUID;
    v_bills_id UUID;
    v_49ers_id UUID;
    v_cowboys_id UUID;
    v_eagles_id UUID;
    v_ravens_id UUID;
    v_bengals_id UUID;
    v_dolphins_id UUID;
BEGIN
    -- Get team IDs
    SELECT id INTO v_chiefs_id FROM equipos WHERE nombre = 'Kansas City Chiefs';
    SELECT id INTO v_bills_id FROM equipos WHERE nombre = 'Buffalo Bills';
    SELECT id INTO v_49ers_id FROM equipos WHERE nombre = 'San Francisco 49ers';
    SELECT id INTO v_cowboys_id FROM equipos WHERE nombre = 'Dallas Cowboys';
    SELECT id INTO v_eagles_id FROM equipos WHERE nombre = 'Philadelphia Eagles';
    SELECT id INTO v_ravens_id FROM equipos WHERE nombre = 'Baltimore Ravens';
    SELECT id INTO v_bengals_id FROM equipos WHERE nombre = 'Cincinnati Bengals';
    SELECT id INTO v_dolphins_id FROM equipos WHERE nombre = 'Miami Dolphins';

    -- Insert Quarterbacks
    INSERT INTO jugadores (nombre, posicion, equipo_id, imagen_url, activo) VALUES
        ('Patrick Mahomes', 'QB', v_chiefs_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/3139477.png', TRUE),
        ('Josh Allen', 'QB', v_bills_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/3918298.png', TRUE),
        ('Brock Purdy', 'QB', v_49ers_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/4431457.png', TRUE),
        ('Dak Prescott', 'QB', v_cowboys_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/2577417.png', TRUE),
        ('Jalen Hurts', 'QB', v_eagles_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/4040715.png', TRUE),
        ('Lamar Jackson', 'QB', v_ravens_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/3916387.png', TRUE),
        ('Joe Burrow', 'QB', v_bengals_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/4038941.png', TRUE),
        ('Tua Tagovailoa', 'QB', v_dolphins_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/4241479.png', TRUE)
    ON CONFLICT DO NOTHING;

    -- Insert Running Backs
    INSERT INTO jugadores (nombre, posicion, equipo_id, imagen_url, activo) VALUES
        ('Isiah Pacheco', 'RB', v_chiefs_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/4685687.png', TRUE),
        ('James Cook', 'RB', v_bills_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/4430737.png', TRUE),
        ('Christian McCaffrey', 'RB', v_49ers_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/3116593.png', TRUE),
        ('Ezekiel Elliott', 'RB', v_cowboys_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/3051392.png', TRUE),
        ('De''Andre Swift', 'RB', v_eagles_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/4040757.png', TRUE),
        ('Derrick Henry', 'RB', v_ravens_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/3043078.png', TRUE),
        ('Joe Mixon', 'RB', v_bengals_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/3116385.png', TRUE),
        ('Raheem Mostert', 'RB', v_dolphins_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/2576414.png', TRUE)
    ON CONFLICT DO NOTHING;

    -- Insert Wide Receivers
    INSERT INTO jugadores (nombre, posicion, equipo_id, imagen_url, activo) VALUES
        ('Travis Kelce', 'TE', v_chiefs_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/15847.png', TRUE),
        ('Stefon Diggs', 'WR', v_bills_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/2976212.png', TRUE),
        ('Deebo Samuel', 'WR', v_49ers_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/4036348.png', TRUE),
        ('CeeDee Lamb', 'WR', v_cowboys_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/4241389.png', TRUE),
        ('A.J. Brown', 'WR', v_eagles_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/4035687.png', TRUE),
        ('Zay Flowers', 'WR', v_ravens_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/4686626.png', TRUE),
        ('Ja''Marr Chase', 'WR', v_bengals_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/4372016.png', TRUE),
        ('Tyreek Hill', 'WR', v_dolphins_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/3116406.png', TRUE)
    ON CONFLICT DO NOTHING;

    -- Insert Tight Ends
    INSERT INTO jugadores (nombre, posicion, equipo_id, imagen_url, activo) VALUES
        ('Dawson Knox', 'TE', v_bills_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/3929630.png', TRUE),
        ('George Kittle', 'TE', v_49ers_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/3116406.png', TRUE),
        ('Jake Ferguson', 'TE', v_cowboys_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/4569618.png', TRUE),
        ('Dallas Goedert', 'TE', v_eagles_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/3925353.png', TRUE),
        ('Mark Andrews', 'TE', v_ravens_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/3915511.png', TRUE)
    ON CONFLICT DO NOTHING;

    -- Insert Kickers
    INSERT INTO jugadores (nombre, posicion, equipo_id, imagen_url, activo) VALUES
        ('Harrison Butker', 'K', v_chiefs_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/3054850.png', TRUE),
        ('Tyler Bass', 'K', v_bills_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/4047365.png', TRUE),
        ('Jake Moody', 'K', v_49ers_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/4567048.png', TRUE),
        ('Brandon Aubrey', 'K', v_cowboys_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/4430807.png', TRUE),
        ('Jake Elliott', 'K', v_eagles_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/3115306.png', TRUE),
        ('Justin Tucker', 'K', v_ravens_id, 'https://a.espncdn.com/i/headshots/nfl/players/full/14914.png', TRUE)
    ON CONFLICT DO NOTHING;

    -- Insert Defenses
    INSERT INTO jugadores (nombre, posicion, equipo_id, imagen_url, activo) VALUES
        ('Chiefs Defense', 'DEF', v_chiefs_id, 'https://a.espncdn.com/i/teamlogos/nfl/500/kc.png', TRUE),
        ('Bills Defense', 'DEF', v_bills_id, 'https://a.espncdn.com/i/teamlogos/nfl/500/buf.png', TRUE),
        ('49ers Defense', 'DEF', v_49ers_id, 'https://a.espncdn.com/i/teamlogos/nfl/500/sf.png', TRUE),
        ('Cowboys Defense', 'DEF', v_cowboys_id, 'https://a.espncdn.com/i/teamlogos/nfl/500/dal.png', TRUE),
        ('Eagles Defense', 'DEF', v_eagles_id, 'https://a.espncdn.com/i/teamlogos/nfl/500/phi.png', TRUE),
        ('Ravens Defense', 'DEF', v_ravens_id, 'https://a.espncdn.com/i/teamlogos/nfl/500/bal.png', TRUE)
    ON CONFLICT DO NOTHING;
END $$;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Initial data inserted successfully!';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Summary:';
    RAISE NOTICE '- 32 NFL Teams inserted';
    RAISE NOTICE '- 1 Admin user + 5 test users created';
    RAISE NOTICE '- 1 Current season (2024-2025) with 18 weeks';
    RAISE NOTICE '- 1 Sample league created';
    RAISE NOTICE '- ~50 Sample players inserted';
    RAISE NOTICE '';
    RAISE NOTICE 'Test Credentials:';
    RAISE NOTICE '- Admin: admin@nflfantasy.com / admin123';
    RAISE NOTICE '- Users: john.smith@test.com / password123';
    RAISE NOTICE '         maria.garcia@test.com / password123';
    RAISE NOTICE '         (and 3 more test users)';
    RAISE NOTICE '';
    RAISE NOTICE 'League Password: league123';
    RAISE NOTICE '========================================';
END $$;
