-- SQL query to insert NFL teams required for the bulk player creation test
-- Based on teams mentioned in nfl_players_bulk_test_corrected.json

INSERT INTO equipos (nombre, ciudad) VALUES 
    ('Buffalo Bills', 'Buffalo'),
    ('Tennessee Titans', 'Nashville'),
    ('Kansas City Chiefs', 'Kansas City'),
    ('Baltimore Ravens', 'Baltimore'),
    ('Green Bay Packers', 'Green Bay'),
    ('Dallas Cowboys', 'Dallas'),
    ('San Francisco 49ers', 'San Francisco'),
    ('New Orleans Saints', 'New Orleans'),
    ('Los Angeles Rams', 'Los Angeles'),
    ('Las Vegas Raiders', 'Las Vegas'),
    ('Pittsburgh Steelers', 'Pittsburgh'),
    ('Cleveland Browns', 'Cleveland'),
    ('Cincinnati Bengals', 'Cincinnati');