#!/usr/bin/env python
#
# Test cases for tournament.py

from tournament import *


def testDeleteMatches():
    deleteMatches()
    print "1. Old matches can be deleted."


def testDelete():
    deleteMatches()
    deletePlayers()
    print "2. Player records can be deleted."


def testCount():
    deleteMatches()
    deletePlayers()
    c = countPlayers()
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "3. After deleting, countPlayers() returns zero."


def testRegister():
    deleteMatches()
    deletePlayers()
    tourney_id = createTournament("Swiss Spectacular")
    registerPlayer(tourney_id, "Chandra Nalaar")
    c = countPlayers(tourney_id)
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1.")
    print "4. After registering a player, countPlayers() returns 1."


def testRegisterCountDelete():
    # deleteMatches()
    # deletePlayers()
    deleteTournaments()
    tourney_id = createTournament("Swiss Spectacular")
    registerPlayer(tourney_id, "Markov Chaney")
    registerPlayer(tourney_id, "Joe Malik")
    registerPlayer(tourney_id, "Mao Tsu-hsi")
    registerPlayer(tourney_id, "Atlanta Hope")
    c = countPlayers(tourney_id)
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    deletePlayers()
    c = countPlayers()
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def testStandingsBeforeMatches():
    # deleteMatches()
    # deletePlayers()
    deleteTournaments()
    tourney_id = createTournament("Swiss Spectacular")
    registerPlayer(tourney_id, "Melpomene Murray")
    registerPlayer(tourney_id, "Randy Schwartz")
    standings = playerStandings(tourney_id)
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 5:
        raise ValueError("Each playerStandings row should have five columns.")
    [(id1, name1, wins1, matches1, OMWs1), (id2, name2, wins2, matches2, OMWs2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played.")
    print "6. Newly registered players appear in the standings with no matches."


def testReportMatches():
    # deleteMatches()
    # deletePlayers()
    deleteTournaments()
    tourney_id = createTournament("Swiss Spectacular")
    registerPlayer(tourney_id, "Bruno Walton")
    registerPlayer(tourney_id, "Boots O'Neal")
    registerPlayer(tourney_id, "Cathy Burton")
    registerPlayer(tourney_id, "Diane Grant")
    standings = playerStandings(tourney_id)
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(tourney_id, id1, id2)
    reportMatch(tourney_id, id3, id4)
    standings = playerStandings(tourney_id)
    for (i, n, w, m, o) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError(
                "Each match loser should have zero wins recorded.")
    print "7. After a match, players have updated standings."


def testPairings():
    # deleteMatches()
    # deletePlayers()
    deleteTournaments()
    tourney_id = createTournament("Swiss Spectacular")
    registerPlayer(tourney_id, "Twilight Sparkle")
    registerPlayer(tourney_id, "Fluttershy")
    registerPlayer(tourney_id, "Applejack")
    registerPlayer(tourney_id, "Pinkie Pie")
    standings = playerStandings(tourney_id)
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(tourney_id, id1, id2)
    reportMatch(tourney_id, id3, id4)
    pairings = swissPairings(tourney_id)
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "8. After one match, players with one win are paired."


def testNoRematches():
    deleteTournaments()
    tourney_id = createTournament("Flintstones Tourney")
    fred_id = registerPlayer(tourney_id, "Fred Flintstone")
    barney_id = registerPlayer(tourney_id, "Barney Rubble")
    wilma_id = registerPlayer(tourney_id, "Wilma Flintstone")
    betty_id = registerPlayer(tourney_id, "Betty Rubble")
    reportMatch(tourney_id, fred_id, barney_id)
    reportMatch(tourney_id, fred_id, barney_id)
    reportMatch(tourney_id, fred_id, barney_id)
    reportMatch(tourney_id, barney_id, fred_id)
    reportMatch(tourney_id, barney_id, fred_id)
    reportMatch(tourney_id, wilma_id, betty_id)
    # Fred 3W, Barney 2W, Wilma 1W, Betty 0W
    # Since Fred and Barney have played, Fred should play Wilma and
    # Barney should play Betty
    pairings = swissPairings(tourney_id)
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([fred_id, wilma_id]),
                        frozenset([barney_id, betty_id])])
    actual_pairs = set([frozenset([pid1, pid2]),
                        frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "Players should not rematch. Standing are incorrect.")
    print "9. Rematches between players are prevented."


def testBye():
    deleteTournaments()
    tourney_id = createTournament("Flintstones Tourney")
    registerPlayer(tourney_id, "Fred Flintstone")
    registerPlayer(tourney_id, "Barney Rubble")
    registerPlayer(tourney_id, "Wilma Flintstone")
    registerPlayer(tourney_id, "Betty Rubble")
    registerPlayer(tourney_id, "Pebbles Flinstone")
    pairings = swissPairings(tourney_id)
    if len(pairings) != 2:
        raise ValueError(
            "For five players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    # Play a round according to the pairings
    reportMatch(tourney_id, pid1, pid2)
    reportMatch(tourney_id, pid3, pid4)
    standings = playerStandings(tourney_id)
    number_of_byes = 0
    # Check to see that each player has played one match and count the
    # numer of byes
    for player in standings:
        if player[3] != 1:
            raise ValueError(
                "Each player should have played one match after the first round.")
        if hasBye(tourney_id, player[0]):
            number_of_byes += 1
    if number_of_byes != 1:
        raise ValueError(
                "One player should have a bye after the first round.")
    print "10. After one round of five players, each player has played one", \
        "match and one player has a bye."


def testOpponentMatchWins():
    deleteTournaments()
    tourney_id = createTournament("Flintstones Tourney")
    fred_id = registerPlayer(tourney_id, "Fred Flintstone")
    barney_id = registerPlayer(tourney_id, "Barney Rubble")
    wilma_id = registerPlayer(tourney_id, "Wilma Flintstone")
    pebbles_id = registerPlayer(tourney_id, "Pebbles Flintstone")
    bambam_id = registerPlayer(tourney_id, "Bam Bam Rubble")
    reportMatch(tourney_id, fred_id, barney_id)
    reportMatch(tourney_id, fred_id, barney_id)
    reportMatch(tourney_id, fred_id, barney_id)
    reportMatch(tourney_id, barney_id, fred_id)
    reportMatch(tourney_id, barney_id, fred_id)
    reportMatch(tourney_id, fred_id, wilma_id)
    reportMatch(tourney_id, barney_id, pebbles_id)
    reportMatch(tourney_id, fred_id, bambam_id)
    reportMatch(tourney_id, barney_id, bambam_id)
    # Fred 5W, Barney 4W, Wilma 0W, Pebbles 0W, Bam Bam 0W
    # Bam Bam 9 OMW, Wilma 5 OMW, Pebbles 4 OMW
    standings = playerStandings(tourney_id)
    (id1, id2, id3, id4, id5) = (row[0] for row in standings)
    correct_order = (fred_id, barney_id, bambam_id, wilma_id, pebbles_id)
    actual_order = (id1, id2, id3, id4, id5)
    if correct_order != actual_order:
        raise ValueError(
            "Player standings have not obeyed Opponent Match Win rules.")
    print "11. Opponent Match Win rules have been observed in standings."


def testMultipleTournaments():
    deleteTournaments()
    # Flinstones tourney
    flinstones_tourney_id = createTournament("Flintstones Tourney")
    fred_id = registerPlayer(flinstones_tourney_id, "Fred Flintstone")
    barney_id = registerPlayer(flinstones_tourney_id, "Barney Rubble")
    wilma_id = registerPlayer(flinstones_tourney_id, "Wilma Flintstone")
    betty_id = registerPlayer(flinstones_tourney_id, "Betty Rubble")
    pebbles_id = registerPlayer(flinstones_tourney_id, "Pebbles Flintstone")
    bambam_id = registerPlayer(flinstones_tourney_id, "Bam Bam Rubble")
    # Space Ghost tourney
    space_ghost_tourney_id = createTournament("Space Ghost Tourney")
    space_ghost_id = registerPlayer(space_ghost_tourney_id, "Space Ghost")
    zorak_id = registerPlayer(space_ghost_tourney_id, "Zorak")
    brak_id = registerPlayer(space_ghost_tourney_id, "Brak")
    moltar_id = registerPlayer(space_ghost_tourney_id, "Moltar")
    # Player counts
    flinstones_count = countPlayers(flinstones_tourney_id)
    space_ghost_count = countPlayers(space_ghost_tourney_id)
    # Standings
    flintstones_standings = playerStandings(flinstones_tourney_id)
    space_ghost_standings = playerStandings(space_ghost_tourney_id)
    # Check that the counts are correct
    if flinstones_count != 6:
        raise ValueError(
            "After registering six players, countPlayers should be 6.")
    if space_ghost_count != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    # Check to see that the players in each tourney are correct
    [fid1, fid2, fid3, fid4, fid5, fid6] = [row[0] for row in flintstones_standings]
    flinstones_correct_players = set([fred_id, barney_id, wilma_id,
                                      betty_id, pebbles_id, bambam_id])
    flinstones_actual_players = set([fid1, fid2, fid3, fid4, fid5, fid6])
    [sgid1, sgid2, sgid3, sgid4] = [row[0] for row in space_ghost_standings]
    space_ghost_correct_players = set([space_ghost_id, zorak_id,
                                       brak_id, moltar_id])
    space_ghost_actual_players = set([sgid1, sgid2, sgid3, sgid4])
    if flinstones_correct_players != flinstones_actual_players:
        raise ValueError("Players in the Flintstones standings are incorrect.")
    if space_ghost_correct_players != space_ghost_actual_players:
        raise ValueError("Players in the Space Ghost standings are incorrect.")
    print "12. Multiple tournaments can be stored simultaneously."


if __name__ == '__main__':
    testDeleteMatches()
    testDelete()
    testCount()
    testRegister()
    testRegisterCountDelete()
    testStandingsBeforeMatches()
    testReportMatches()
    testPairings()
    testNoRematches()
    testBye()
    testOpponentMatchWins()
    testMultipleTournaments()
    print "Success!  All tests pass!"
