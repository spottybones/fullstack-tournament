#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import itertools
import random


class Player():
    """Object representation of a Player

    Attributes:
     - id
     - name
     - wins: matches won
     - played: matches played
    """
    def __init__(self, id, name, wins=0, played=0):
        self.id             = id
        self.name           = name
        self.wins           = wins
        self.played         = played

    def __str__(self):
        return("{x.name} ({x.wins} / {x.played})".format(x=self))


class DB:
    def __init__(self, db_con_str="dbname=tournament"):
        """
        Creates a database connection with the connection string provided
        :param str db_con_str: Contains the database connection string, with
           a default value when no argument is passed to the parameter
        """
        self.conn = psycopg2.connect(db_con_str)

    def cursor(self):
        """
        Returns the current cursor of the database
        """
        return self.conn.cursor()

    def execute(self, sql_query, and_close=False):
        """
        Executes SQL Queries
        :param tuple sql_query: A one or two element tuple; the first element is
            required and contains a string with the SQL query option; the second
            is optional and contains parameters to be substituted, after
            sanitation, if specified in the query
        :param bool and_close: If true, closes the database connection after
            executing and commiting the SQL query
        """
        cursor = self.cursor()
        cursor.execute(*sql_query)
        if and_close:
            self.conn.commit()
            self.close()
        return {"conn": self.conn, "cursor": cursor if not and_close else None}

    def close(self):
        """
        Closes the current database connection
        """
        self.conn.close()


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    DB().execute(('delete from matches',), True)


def deletePlayers():
    """Remove all the player records from the database."""
    DB().execute(('delete from players',), True)


def countPlayers():
    """Returns the number of players currently registered."""
    conn = DB().execute(('select count(*) from players',))
    player_count = conn['cursor'].fetchone()
    conn['cursor'].close()
    return player_count[0]


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    DB().execute(('insert into players (name) values (%(name)s)',
                  {'name': name}), True)


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = DB().execute(('select * from standings',))
    standings = conn['cursor'].fetchall()
    conn['cursor'].close()
    return standings


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    DB().execute(('insert into matches values (%(winner)s, %(loser)s)',
                  {'winner': winner, 'loser': loser}), True)


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    # Load a list of matches played in previous rounds. This list will be used
    # to check each pairing proposed for the current round to prevent rematches.
    conn = DB().execute(('select * from matches',))
    matches = conn['cursor'].fetchall()
    conn['cursor'].close()
    previously_matched = []
    for winner_id, loser_id in matches:
        previously_matched.append(set([winner_id, loser_id]))

    # To generate pairings get the list of players from the playerStandings()
    # function and split them into groups based on the number of wins. The list
    # of players in each group is then shuffled randomly and pairings are
    # attempted in order, skipping any pairs that have already played. If a pair
    # is skipped the group is reshuffled and pairing is attempted again.

    def by_wins(player):
        # Utility function used by itertools.groupby to generate lists of
        # Players grouped by number of wins.
        return player.wins

    def next_pair(players):
        # An iterator that will return pairs of elements from a list
        # in order. If returns an empty list of passed a list with an odd
        # number of elements
        if len(players) % 2:
            yield []
        else:
            i = 0
            while i < len(players):
                yield players[i:i + 2]
                i += 2

    # Generate a list of Player objects from the list returned by
    # playerStandings().
    players = [Player(*args)
               for args in playerStandings()]

    round_pairings = []
    for group in itertools.groupby(players, by_wins):
        # Iterate through groups created based on number of player wins
        group_players = [group_player for group_player in group[1]]
        while True:
            # shuffle the groups players and start pulling pairs to match up
            random.shuffle(group_players)
            group_pairings = []
            for player1, player2 in next_pair(group_players):
                if set([player1.id, player2.id]) not in previously_matched:
                    # If the pair hasn't played before, add them to the list of
                    # group pairings and get the next pair.
                    group_pairings.append((player1.id, player1.name,
                                           player2.id, player2.name))

            if len(group_pairings) == len(group_players) / 2:
                # If every group player has been successfully matched, add the
                # group pairings to the round pairings and go to the next group.
                # Otherwise we'll reshuffle the group players and attempt
                # another pairing.
                round_pairings = round_pairings + group_pairings
                break

    return round_pairings
