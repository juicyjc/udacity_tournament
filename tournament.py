#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import bleach
import utils


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def createTournament(name):
    """Add a tournament to the database.

    Args:
      name:  the name of the tournemant

    Returns:
      id_of_new_row:  the id of the newly created tournament
    """
    DB = connect()
    c = DB.cursor()
    c.execute(
        "INSERT INTO Tournaments (name) VALUES (%s) RETURNING id;",
        (bleach.clean(name),))
    id_of_new_row = c.fetchone()[0]
    c.execute(
        """INSERT INTO Tournaments_Players (tournament_id, player_id)
        VALUES (%s, 0);""", (id_of_new_row,))
    DB.commit()
    DB.close()
    return id_of_new_row


def deleteTournaments():
    """Remove all the matches, players, and tournaments from the database."""
    DB = connect()
    c = DB.cursor()
    query = "DELETE FROM Matches;"
    c.execute(query)
    query = "DELETE FROM Tournaments_Players;"
    c.execute(query)
    query = "DELETE FROM Players WHERE id <> 0;"
    c.execute(query)
    query = "DELETE FROM Tournaments;"
    c.execute(query)
    DB.commit()
    DB.close()


def deleteMatches(tournament_id=0):
    """Remove all the match records for a tournament from the database.

    Args:
      tournament_id (optional):  the id of the tournament to delete matches
        from. Pass 0 or leave blank to delete all matches in the DB.
    """
    DB = connect()
    c = DB.cursor()
    if tournament_id == 0:
        query = "DELETE FROM Matches;"
    else:
        query = "DELETE FROM Matches WHERE tournament_id = %s;",
        (tournament_id,)
    c.execute(query)
    DB.commit()
    DB.close()


def deletePlayers():
    """Remove all the player records from the database except for 'Bye'."""
    DB = connect()
    c = DB.cursor()
    query = "DELETE FROM Tournaments_Players;"
    c.execute(query)
    query = "DELETE FROM Players WHERE id <> 0;"
    c.execute(query)
    DB.commit()
    DB.close()


def countPlayers(tournament_id=0):
    """Returns the number of players currently registered.

    Args:
      tournament_id (optional):  the id of the tournament in which to count
        players. Pass 0 or leave blank to count all players in the DB.

    Returns:
      number_of_players:  the player count
    """
    DB = connect()
    c = DB.cursor()
    if tournament_id == 0:
        c.execute("SELECT COUNT(id) as num FROM Players WHERE id <> 0;")
    else:
        c.execute(
            """SELECT COUNT(player_id) as num FROM Tournaments_Players
            WHERE tournament_id = %s AND player_id <> 0;""", (tournament_id,))
    row = c.fetchone()
    number_of_players = row[0]
    DB.close()
    return number_of_players


def registerPlayer(tournament_id, name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      tournament_id:  the id of the tournament that the player will be
        registered in
      name:  the player's full name (need not be unique).

    Returns:
      id_of_new_row:  the id of the newly created player
    """
    DB = connect()
    c = DB.cursor()
    c.execute(
        "INSERT INTO Players (name) VALUES (%s) RETURNING id;",
        (bleach.clean(name),))
    id_of_new_row = c.fetchone()[0]
    c.execute(
        """INSERT INTO Tournaments_Players (tournament_id, player_id)
        VALUES (%s, %s);""", (tournament_id, id_of_new_row))
    DB.commit()
    DB.close()
    return id_of_new_row


def playerStandings(tournament_id):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a
    player tied for first place if there is currently a tie.

    Args:
      tournament_id:  the id of the tournament to get standings for

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches, OMWs):
        id:  the player's unique id (assigned by the database)
        name:  the player's full name (as registered)
        wins:  the number of matches the player has won
        matches:  the number of matches the player has played
        opponent match wins:  the number of matches the player's opponents have
          won
    """
    DB = connect()
    c = DB.cursor()
    c.execute("""SELECT id, name, wins, wins + losses AS matches
       FROM v_WinsAndLosses WHERE tournament_id = %s;""", (tournament_id,))
    rows = c.fetchall()
    standings = [(row[0], str(row[1]), row[2], row[3],
                 getOpponentMatchWins(tournament_id, row[0])) for row in rows]
    DB.close()
    # Sort the tuple by wins and opponent match wins
    results = sorted(standings, key=lambda element: (-element[2], -element[4]))
    return results


def reportMatch(tournament_id, winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      tournament_id:  the id of the tournament to add the match to
      winner:  the id of the player who won
      loser:  the id of the player who lost
    """
    DB = connect()
    c = DB.cursor()
    c.execute(
        """INSERT INTO Matches (tournament_id, winner, loser)
        VALUES (%s, %s, %s);""", (tournament_id, winner, loser))
    DB.commit()
    DB.close()


def numberOfMatchesPlayed(tournament_id, player1_id, player2_id):
    """Returns the number of matches two players have played.

    Args:
      tournament_id:  the id of the tournament to check for matches
      player1_id:  the id of player1
      player2_id:  the id of player2

    Returns:
      number_played:  the number of matches played between the two players
    """
    DB = connect()
    c = DB.cursor()
    c.execute("""SELECT id FROM Matches
            WHERE (winner = %s OR winner = %s)
            AND (loser = %s OR loser = %s)
            AND tournament_id = %s;""",
              (player1_id, player2_id, player1_id, player2_id, tournament_id))
    number_played = c.rowcount
    DB.close()
    return number_played


def havePlayedBefore(tournament_id, player1_id, player2_id):
    """Returns true/false if players have played before.

    Args:
      tournament_id:  the id of the tournament to check for matches
      player1_id:  the id of player1
      player2_id:  the id of player2

    Returns:
      have_played:  boolean - whether or not playes have played before
    """
    number_played = numberOfMatchesPlayed(tournament_id, player1_id, player2_id)
    if number_played == 0:
        return False
    else:
        return True


def hasBye(tournament_id, player_id):
    """ Returns true/false if player has had a 'Bye'.

    Args:
      tournament_id:  the id of the tournament to check for a bye
      player_id:  the id of the player

    Returns:
      has_bye:  boolean - whether or not the player has had a 'Bye'
    """

    DB = connect()
    c = DB.cursor()
    c.execute("""SELECT id FROM Matches WHERE winner = %s
              AND loser = 0 AND tournament_id = %s;""",
              (player_id, tournament_id))
    has_bye = True if c.rowcount > 0 else False
    DB.close()
    return has_bye


def getOpponentMatchWins(tournament_id, player_id):
    """ Returns the total number of wins of all of a player's opponents.

    Args:
      tournament_id:  the id of the tournament to check
      player_id:  the id of the player

    Returns:
      opponent_match_wins:  the total number of wins of a player's opponents
    """
    DB = connect()
    c = DB.cursor()
    # Get all matches the player has played
    c.execute("""SELECT winner, loser FROM Matches
              WHERE (winner = %s OR loser = %s) AND tournament_id = %s;""",
              (player_id, player_id, tournament_id))
    rows = c.fetchall()
    # Loop through the result set and create a list of opponents
    if len(rows) > 0:
        opponents = []
        for row in rows:
            if row[0] == player_id:
                opponents.append(row[1])
            else:
                opponents.append(row[0])
        # Get the total number of wins for the players in the list
        c.execute("""SELECT COUNT(winner) FROM Matches
                  WHERE tournament_id = %s AND winner IN %s;""",
                  (tournament_id, tuple(opponents)))
        result = c.fetchone()
        opponent_match_wins = result[0]
    else:
        opponent_match_wins = 0
    DB.close()
    return opponent_match_wins


def swissPairings(tournament_id):
    """Returns a list of pairs of players for the next round of a match.

    Each player appears once in the pairings. If there is an odd number of
    players then a player who has not had one will get a bye. Each player is
    paired with another player with an equal or nearly-equal win record, that
    is, a player adjacent to him or her in the standings.

    Args:
      tournament_id:  the id of the tournament to pair

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1:  the first player's unique id
        name1:  the first player's name
        id2:  the second player's unique id
        name2:  the second player's name
    """
    standings = playerStandings(tournament_id)
    # If we have an odd number of players, loop through
    if len(standings) % 2 == 1:
        for player in standings:
            player_id = player[0]
            # And give the first player who has not already had one a 'Bye'
            if not hasBye(tournament_id, player_id):
                reportMatch(tournament_id, player_id, 0)
                # Remove the player from the list
                standings = utils.tuple_without(standings, player)
                break
    # Create a list of tuples to return
    pairings = []
    # Loop over standings while it's populated
    while len(standings) > 0:
        # Put the first player in a variable and remove him from standings
        first_player = standings[0]
        standings = utils.tuple_without(standings, standings[0])
        # Iterate through the standings minus the first player
        for player in standings:
            #  If the first player has not played the current player
            if not havePlayedBefore(tournament_id, first_player[0], player[0]):
                # Then we have our pair. Add them to the list.
                pairings.append([first_player[0], str(first_player[1]),
                                player[0], str(player[1])])
                # And delete the current player from standings.
                standings = utils.tuple_without(standings, player)
                break
    return pairings
