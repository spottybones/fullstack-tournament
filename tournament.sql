-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- create a new 'tournament' database, dropping the old one if it exists
DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;

-- ensure we're connected to the 'tournament' database
\c tournament;

-- create the 'players' table
create table players (
  id SERIAL PRIMARY KEY,
  name text
);

-- create the 'matches' table
CREATE TABLE matches (
  winner int REFERENCES players (id),
  loser int REFERENCES players (id),
  PRIMARY KEY (winner, loser),
  UNIQUE (loser, winner)
);

-- create the standings view
CREATE VIEW standings AS
SELECT p.id, p.name,
  COALESCE(w.wins,0) AS wins,
  COALESCE(w.wins,0) + COALESCE(l.losses,0) AS matches
FROM players p
  LEFT JOIN (
    SELECT winner, COUNT(winner) AS wins FROM matches GROUP BY winner
  ) AS w ON p.id = w.winner
  LEFT JOIN (
    SELECT loser, COUNT(loser) AS losses FROM matches GROUP BY loser
  ) AS l ON p.id = l.loser
ORDER BY wins DESC, p.id
;
