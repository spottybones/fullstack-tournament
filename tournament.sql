-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- ensure we're connected to the 'tournament' database
\c tournament;

-- create the 'players' table
DROP TABLE IF EXISTS players CASCADE;
create table players (
  id SERIAL PRIMARY KEY,
  name text
);

-- create the 'matches' table
DROP TABLE IF EXISTS matches CASCADE;
CREATE TABLE matches (
  winner int REFERENCES players (id),
  loser int REFERENCES players (id),
  PRIMARY KEY (winner, loser),
  UNIQUE (loser, winner)
);

-- create the standings view
DROP VIEW IF EXISTS standings;
CREATE VIEW standings AS
SELECT p.id, p.name, SUM(COALESCE(r.win, 0)) AS wins, SUM(COALESCE(r.match, 0)) AS matches
FROM players p LEFT JOIN
 (
  SELECT winner AS player_id, 1 AS win, 1 AS match FROM matches
  UNION ALL
  SELECT loser AS player_id, 0 AS win, 1 AS match FROM matches
) AS r
ON p.id = r.player_id
GROUP BY p.id, p.name
ORDER BY wins DESC
;
