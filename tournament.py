#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
from itertools import combinations

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    db = connect()
    c = db.cursor()
    c.execute('delete from matches')
    db.commit()
    db.close()


def deletePlayers():
    """Remove all the player records from the database."""
    db = connect()
    c = db.cursor()
    c.execute('delete from players')
    db.commit()
    db.close()


def countPlayers():
    """Returns the number of players currently registered."""
    db = connect()
    c = db.cursor()
    c.execute('select count(*) from players')
    count = c.fetchone()[0]
    db.close()
    return count


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    db = connect()
    c = db.cursor()
    c.execute('insert into players (name) values (%(name)s)',
              {'name': name})
    db.commit()
    db.close()


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
    db = connect()
    c = db.cursor()
    c.execute('select * from standings')
    standings = c.fetchall()
    db.close()
    return standings


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    db = connect()
    c = db.cursor()
    c.execute('insert into matches values (%(winner)s, %(loser)s)',
              {'winner': winner, 'loser': loser})
    db.commit()
    db.close()


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

    # Load a list of matches already played. this list will be used to check
    # each pairing generated to see if it's been already played.
    db = connect()
    c = db.cursor()
    c.execute('select * from matches')
    already_matched = []
    for winner_id, loser_id in c.fetchall():
        already_matched.append(set([winner_id, loser_id]))
    db.close()

    # To generate pairings get the list of players from the playerStandings()
    # function and compare pairs by pulling two players from the list and
    # checking to see if they have already played. If not they are added to the
    # list of pairings to be returned. It they have played before then player2
    # is put on a stack and will be called for a future pairing.
    matched = []
    pairings = []

    # iterate through potential_matches. if the match hasn't already been played
    # add it to both the pairings list and add the set of player IDs to the
    # already_matched list
    for match in combinations(playerStandings(), 2):
        # if these players haven't already played, add them to the pairings list
        # and the already_matched list.
        match_set = set([match[0][0], match[1][0]])
        if match_set in already_matched:
            continue
        elif match[0][0] in matched:
            continue
        elif match[0][1] in matched:
            continue
        else:
            pairings.append((match[0][0], match[0][1], match[1][0], match[1][1]))
            matched += [match[0][0], match[1][0]]

    return pairings
