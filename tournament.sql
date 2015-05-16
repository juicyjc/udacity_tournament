-- Table definitions for the tournament project.

-- Drop the database if it exists
DROP DATABASE tournament;

-- Create the database
CREATE DATABASE tournament;

-- Connect to the DB
\c tournament;

-- Create the players table
CREATE TABLE Players (
	id serial primary key,
	name text
);

-- Insert a record for 'Bye'
INSERT INTO Players (id, name) VALUES (0, 'Bye');

-- Create the tournament table
CREATE TABLE Tournaments (
    id serial primary key,
    name text
);

-- Create the tournaments-players table
CREATE TABLE Tournaments_Players (
    tournament_id integer references Tournaments(id),
    player_id integer references Players(id),
    primary key (tournament_id, player_id)
);

-- Create the matches table
CREATE TABLE Matches (
	id serial primary key,
    tournament_id integer references Tournaments(id),
	winner integer references Players(id),
	loser integer references Players(id)
);

-- Create a view that returns tournament_id, id, name, wins, and losses for each player
CREATE VIEW v_WinsAndLosses AS
    SELECT w.tournament_id, w.id, w.name, w.wins, l.losses
    FROM (
        SELECT tp1.tournament_id, p1.id, p1.name, COUNT(m1.winner) AS wins
        FROM ((Players p1 LEFT JOIN Tournaments_Players tp1 ON p1.id = tp1.player_id)
        LEFT JOIN Matches m1 ON p1.id = m1.winner)
        GROUP BY tp1.tournament_id, p1.id, p1.name
    ) w
    INNER JOIN (
        SELECT tp2.tournament_id, p2.id, p2.name, COUNT(m2.loser) AS losses
        FROM ((Players p2 LEFT JOIN Tournaments_Players tp2 ON p2.id = tp2.player_id)
        LEFT JOIN Matches m2 ON p2.id = m2.loser)
        GROUP BY tp2.tournament_id, p2.id, p2.name
    ) l
    ON w.id = l.id
    WHERE w.id <> 0
    ORDER BY w.wins DESC;
