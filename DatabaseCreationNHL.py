import pandas as pd

def createTrainingFrame(lst):
    """Create a dataframe from a list of csv file names.

    Parameters:
        lst(list) - a list of strings which correspond to the files the frame will be comprised of.

    Returns:
        trainingFrame - a dataframe with all information from the games.
    """
    #where each individual frame is stored for concatenation
    frames = []

    #iterate through the list of csvs
    for i in lst:
        #read in the csv
        season = pd.read_csv(i)

        #denote playoff games
        season['isPlayoffs'] = season.apply(lambda x: 1 if x['Game_Id'] >= 30000  else 0, axis = 1)

        #create a unique Game_Id by adding the year the game took place to the current Game_Id string
        seasonString = i[17:21]
        season['Game_Id'] = seasonString + season['Game_Id'].astype(str)
        season = season.iloc[:,1:] #remove the index column

        #add the frame to the list of frames
        frames.append(season)

    #concatenate the frame together then sort by the Game_Id
    trainingFrame = pd.concat(frames)
    trainingFrame['Game_Id'] = trainingFrame['Game_Id'].astype(int)

    return trainingFrame

def RecordEnding(away,home,df):
    """Count the goals that were scored by each team and how the game ended.

    Parameters:
        away(string) - the string name of the away team.
        home(string) - the string name of the home team.

    Returns:
        [ending,winner] - how the game ended (REG or OT), and who won.
    """
    #keep track of if the game ended in regular time
    ending = 'REG'

    #game end event
    endingStats = df[(df['Event'] == 'GEND')]

    #account for missing GEND event
    if endingStats['Period'].values.size == 0:
        endingStats = df[(df['Event'] == 'PEND')]
        endingStats = endingStats.sort_values('Period')
        endingStats = endingStats.tail(-(endingStats.shape[0] - 1))

    #record the type of ending     
    if endingStats['Period'].iloc[0] > 3:
        ending = 'OT'
    
    #count the goals
    awayGoals = endingStats['Away_Score'].iloc[0]
    homeGoals = endingStats['Home_Score'].iloc[0]
    
    #determine the winner of the game
    if awayGoals > homeGoals:
        winner = away
    elif homeGoals > awayGoals:
        winner = home
    else:
        winner = 'ERROR'
        
    return ending, winner

def countGoals(away,home,df,v5=False,close=False):
    """Count the goals in a game for both teams.

    Parameters:
        away(string) - the string name of the away team.
        home(string) - the string name of the home team.
        df(dataframe) - the pandas dataframe that contains all data.
        v5(Bool) - denotes if the calculation should be for 5v5 or all strengths.
        close(Bool) - denotes if the calculates should only be in close game situations.

    Returns:
        [awayGoals,homeGoals] - the number of goals for the away and home team as a list.
    """
    #if we're only looking at 5v5 situations
    if v5:
        df = df[df['Strength'] == '5x5']

    #if we're only looking at 'close' situations
    if close:
        df = df[(((df['Period'] == 1) | (df['Period'] == 2)) & (df['Score_Diff'] <= 1))|(((df['Period'] == 3) | (df['Period'] == 4)) & (df['Score_Diff'] == 0))]
    
    #make sure that shootout goals are not included in regular season
    df = df[((df['Period'] < 5) & (df['isPlayoffs'] == 0)) | (df['isPlayoffs'] == 1)]
    
    #count goals for both teams
    awayGoals = df[(df['Event'] == 'GOAL') & (df['Ev_Team'] == away)].shape[0]
    homeGoals = df[(df['Event'] == 'GOAL') & (df['Ev_Team'] == home)].shape[0]

    return [awayGoals, homeGoals]

def countShots(away,home,df,v5=False,close=False):
    """Count the shots that took place in a game for both teams.

    Parameters:
        away(string) - the string name of the away team.
        home(string) - the string name of the home team.
        df(dataframe) - the pandas dataframe that contains all data.
        v5(Bool) - denotes if the calculation should be for 5v5 or all strengths.
        close(Bool) - denotes if the calculates should only be in close game situations.

    Returns:
        [awayShots,homeShots] - the number of shots for the away and home team as a list.
    """
    #if we're only looking at 5v5 situations
    if v5:
        df = df[df['Strength'] == '5x5']

    #if we're only looking at 'close' situations
    if close:
        df = df[(((df['Period'] == 1) | (df['Period'] == 2)) & (df['Score_Diff'] <= 1))|(((df['Period'] == 3) | (df['Period'] == 4)) & (df['Score_Diff'] == 0))]
    
    #make sure that shootout shots are not included in regular season
    df = df[((df['Period'] < 5) & (df['isPlayoffs'] == 0)) | (df['isPlayoffs'] == 1)]
    
    #count the away and home shots
    awayShots = df[(df['Ev_Team'] == away) & ((df['Event'] == 'SHOT'))].shape[0]
    homeShots = df[(df['Ev_Team'] == home) & (df['Event'] == 'SHOT')].shape[0]
        
    return [awayShots,homeShots]

def countShotAttempts(away,home,df,v5=False,close=False):
    """Count the shot attempts that took place in a game for both teams.

    Parameters:
        away(string) - the string name of the away team.
        home(string) - the string name of the home team.
        df(dataframe) - the pandas dataframe that contains all data.
        v5(Bool) - denotes if the calculation should be for 5v5 or all strengths.
        close(Bool) - denotes if the calculates should only be in close game situations.

    Returns:
        [awayShotAttempts,homeAttempts] - the number of shot attempts for the away and home team as a list.
    """

    #if we're only looking at 5v5 situations
    if v5:
        df = df[df['Strength'] == '5x5']

    #if we're only looking at 'close' situations
    if close:
        df = df[(((df['Period'] == 1) | (df['Period'] == 2)) & (df['Score_Diff'] <= 1))|(((df['Period'] == 3) | (df['Period'] == 4)) & (df['Score_Diff'] == 0))]

    #make sure that shootout shots are not included in regular season
    df = df[((df['Period'] < 5) & (df['isPlayoffs'] == 0)) | (df['isPlayoffs'] == 1)]
        
    #count the away and home shot attempts
    awayShotAttempts = df[(df['Ev_Team'] == away) & ((df['Event'] == 'SHOT') |
                                                     (df['Event'] == 'MISS') |
                                                     (df['Event'] == 'GOAL') |
                                                     (df['Event'] == 'BLOCK'))].shape[0] 
    homeShotAttempts = df[(df['Ev_Team'] == home) & ((df['Event'] == 'SHOT') |
                                                     (df['Event'] == 'MISS') |
                                                     (df['Event'] == 'GOAL') |
                                                     (df['Event'] == 'BLOCK'))].shape[0]
        
    return [awayShotAttempts, homeShotAttempts]

def countHits(away,home,df):
    """Count the hits that took place in a game for both teams.

    Parameters:
        away(string) - the string name of the away team.
        home(string) - the string name of the home team.
        df(dataframe) - the pandas dataframe that contains all data.

    Returns:
        [awayHits, homeHits] - the number of hits for the away and home team as a list.
    """
    #count away and home hits
    awayHits = df[(df['Ev_Team'] == away) & (df['Event'] == 'HIT')].shape[0]
    homeHits = df[(df['Ev_Team'] == home) & (df['Event'] == 'HIT')].shape[0]
    return [awayHits, homeHits]

def countBlocks(away,home,df,v5=False,close=False):
    """Count the blocks that took place in a game for both teams.

    Parameters:
        away(string) - the string name of the away team.
        home(string) - the string name of the home team.
        df(dataframe) - the pandas dataframe that contains all data.
        v5(Bool) - denotes if the calculation should be for 5v5 or all strengths.
        close(Bool) - denotes if the calculates should only be in close game situations.

    Returns:
        [awayBlocks, homeBlocks] - the number of blocks for the away and home team as a list.
    """
    #if we're only looking at 5v5 situations
    if v5:
        df = df[df['Strength'] == '5x5']

    #if we're only looking at 'close' situations
    if close:
        df = df[(((df['Period'] == 1) | (df['Period'] == 2)) & (df['Score_Diff'] <= 1))|(((df['Period'] == 3) | (df['Period'] == 4)) & (df['Score_Diff'] == 0))]

    #count away and home blocks
    awayBlocks = df[(df['Ev_Team'] == home) & (df['Event'] == 'BLOCK')].shape[0]
    homeBlocks = df[(df['Ev_Team'] == away) & (df['Event'] == 'BLOCK')].shape[0]

    return [awayBlocks, homeBlocks]

def countFaceoffs(away,home,df):
    """Count the faceoff wins for both teams.

    Parameters:
        away(string) - the string name of the away team.
        home(string) - the string name of the home team.
        df(dataframe) - the pandas dataframe that contains all data.

    Returns:
        [awayFO, homeFO] - the number of faceoff wins for the away and home team as a list.
    """
    #count away and home faceoffs
    awayFO = df[(df['Ev_Team'] == away) & (df['Event'] == 'FAC')].shape[0]
    homeFO = df[(df['Ev_Team'] == home) & (df['Event'] == 'FAC')].shape[0]
    return [awayFO, homeFO]

def countGiveAways(away,home,df):
    """Count the giveaways for both teams.

    Parameters:
        away(string) - the string name of the away team.
        home(string) - the string name of the home team.
        df(dataframe) - the pandas dataframe that contains all data.

    Returns:
        [awayGive, homeGive] - the number of giveaways for the away and home team as a list.
    """
    #count away and home giveaways
    awayGive = df[(df['Ev_Team'] == away) & (df['Event'] == 'GIVE')].shape[0]
    homeGive = df[(df['Ev_Team'] == home) & (df['Event'] == 'GIVE')].shape[0]
    return [awayGive, homeGive]

def countTakeAways(away,home,df):
    """Count the takeaways for both teams.

    Parameters:
        away(string) - the string name of the away team.
        home(string) - the string name of the home team.
        df(dataframe) - the pandas dataframe that contains all data.

    Returns:
        [awayTake, homeTake] - the number of takeaways for the away and home team as a list.
    """
    #count away and home takeaways
    awayTake = df[(df['Ev_Team'] == away) & (df['Event'] == 'TAKE')].shape[0]
    homeTake = df[(df['Ev_Team'] == home) & (df['Event'] == 'TAKE')].shape[0]
    return [awayTake, homeTake]

def checkForOffsettingPens(events,otherTeam):
    """Given events determine if the opposing team got an offsetting penalty.

    Parameters:
        events(Dataframe) - a dataframe of events.
        otherTeam(String) - the name of the opposing team

    Returns:
        Bool - was there an offsetting penalty.
    """
    if events[events['Ev_Team'] == otherTeam].shape[0] > 0:
        return True
    else:
        return False
    
def countPenaltyMins(away,home,df):
    """Count penalty minutes for each team.

    Parameters:
        away(string) - the string name of the away team.
        home(string) - the string name of the home team.
        df(Dataframe) - a dataframe of events.

    Returns:
        [awaySum, homeSum, awayPPO, homePPO] - the number of penalty minutes and the number of powerplay opportunities for both teams.
    """
    #get the penalties that took place for both teams
    awayPen = df[(df['Ev_Team'] == away) & (df['Event'] == 'PENL')]
    homePen = df[(df['Ev_Team'] == home) & (df['Event'] == 'PENL')]

    #used to sum the penalty minutes
    awaySum = 0
    homeSum = 0

    #count powerplay opportunities
    awayPPO = 0
    homePPO = 0

    #iterate through the penalties
    for index, pen in awayPen.iterrows():
        #make sure the penalty is not NaN
        if not isinstance(pen['Type'],float):
            
            #find the number of minutes for the penalty in the type string
            mins = pen['Type'][pen['Type'].find("(")+1:pen['Type'].find(" min)")]

            #store the events that took place at the same time
            eventsAtSameTime = df[(df['Time_Elapsed'] == pen['Time_Elapsed']) & (df['Period'] == pen['Period']) & (df['Event'] == 'PENL')]

            #if it is a major, 5 mins
            if (mins == 'maj') or ('maj' in mins): 
                awaySum += 5

                #if there wasn't a fight increment the opportunities
                if 'Fighting' not in pen['Type']:
                    awayPPO += 1

            #if the string is empty, likely penalty shot       
            elif mins == '':
                continue
            
            else:
                #add the minutes
                awaySum += int(mins)

                #ensure there weren't offsetting minors before storing the powerplay opportunity
                if not checkForOffsettingPens(eventsAtSameTime,home):
                    awayPPO += 1
                         
        else:
            #if the penalty is NaN use the event description instead
            mins = pen['Description'][pen['Description'].find("(")+1:pen['Description'].find(" min)")]
            awaySum += int(mins)

            if mins == '':
                continue

            #ensure there weren't offsetting minors before storing the powerplay opportunity
            if not checkForOffsettingPens(eventsAtSameTime,home):
                awayPPO += 1

    #iterate through the penalties
    for index, pen in homePen.iterrows():
        #make sure the penalty is not NaN
        if not isinstance(pen['Type'],float):
            
            #find the number of minutes for the penalty in the type string
            mins = pen['Type'][pen['Type'].find("(")+1:pen['Type'].find(" min)")]

            #store the events that took place at the same time
            eventsAtSameTime = df[(df['Time_Elapsed'] == pen['Time_Elapsed']) & (df['Period'] == pen['Period']) & (df['Event'] == 'PENL')]

            #if it is a major, 5 mins
            if (mins == 'maj') or ('maj' in mins): 
                homeSum += 5

                #if there wasn't a fight increment the opportunities
                if 'Fighting' not in pen['Type']:
                    homePPO += 1

            #if the string is empty, likely penalty shot      
            elif mins == '':
                continue
                
            else:
                #add the minutes
                homeSum += int(mins)

                #ensure there weren't offsetting minors before storing the powerplay opportunity
                if not checkForOffsettingPens(eventsAtSameTime,away):
                    homePPO += 1
        else:
            #if the penalty is NaN use the event description instead
            mins = pen['Description'][pen['Description'].find("(")+1:pen['Description'].find(" min)")]

            if mins == '':
                continue

            homeSum += int(mins)

            #ensure there weren't offsetting minors before storing the powerplay opportunity
            if not checkForOffsettingPens(eventsAtSameTime,away):
                homePPO += 1

    return [awaySum, homeSum, awayPPO, homePPO]
    

def countPPG(away,home,df):
    """Count powerplay goals scored by both teams.

    Parameters:
        away(string) - the string name of the away team.
        home(string) - the string name of the home team.
        df(Dataframe) - a dataframe of events.

    Returns:
        [awayGoals,homeGoals] - the powerplay goals scored for both the home and away team.
    """
    #track the away and home goals
    awayGoals = 0
    homeGoals = 0

    #make sure that shootout shots are not included in regular season
    df = df[((df['Period'] < 5) & (df['isPlayoffs'] == 0)) | (df['isPlayoffs'] == 1)]

    #get all goals that took place outside of shootouts
    goals = df[(df['Event'] == 'GOAL')]

    #iterate through all the goals
    for index, g in goals.iterrows():
        
        #determine the strength of both sides
        strength = g['Strength']
        strength = strength.split('x')

        #if the away team scored
        if g['Ev_Team'] == away:
            #if the away team had more players on the ice than the home team
            if int(strength[1]) > int(strength[0]):
                awayGoals += 1

        #if the home team scored
        elif g['Ev_Team'] == home:
            #if the home team had more players on the ice than the away team
            if int(strength[1]) < int(strength[0]):
                homeGoals += 1
            
    return [awayGoals,homeGoals]

def countXG(away,home,df,v5=False,close=False):
    """Count the expected goals in a game for both teams.

    Parameters:
        away(string) - the string name of the away team.
        home(string) - the string name of the home team.
        df(dataframe) - the pandas dataframe that contains all data.
        v5(Bool) - denotes if the calculation should be for 5v5 or all strengths.
        close(Bool) - denotes if the calculates should only be in close game situations.

    Returns:
        [awayXG, homeXG] - the xG for the away and home team as a list.
    """
    #if we're only looking at 5v5 situations
    if v5:
        df = df[(df['HomePlayers'] == 6) & (df['AwayPlayers'] == 6)]

    #if we're only looking at 'close' situations
    if close:
        df = df[(((df['GameTime'] <= 2400)) & (df['GoalDiff'] <= 1)) | ((df['GameTime'] > 2400) & (df['GoalDiff'] == 0))]

    #calculate xG for both teams
    awayXG = df[(df['Team'] == away)]['xG'].sum()
    homeXG = df[(df['Team'] == home)]['xG'].sum()

    return [awayXG,homeXG]

def main():
    """Main method which creates single game summaries using event data from the NHL."""

    #columns for the output csv
    cols = ['Game_Id','season','Date','isPlayoffs','Winner','RegOrOT','Away_Team','Home_Team','Away_Score','Home_Score','Away_Shots','Home_Shots','Away_Shot_Attempts','Home_Shot_Attempts','Away_CORSI%','Home_CORSI%',
            'Away_Fen%','Home_Fen%','Away_Score5v5','Home_Score5v5','Away_Shots5v5','Home_Shots5v5','Away_Shot_Attempts5v5','Home_Shot_Attempts5v5','Away_CORSI%5v5','Home_CORSI%5v5','Away_Fen%5v5','Home_Fen%5v5',
            'Away_ScoreClose','Home_ScoreClose','Away_ShotsClose','Home_ShotsClose','Away_Shot_AttemptsClose','Home_Shot_AttemptsClose','Away_CORSI%Close','Home_CORSI%Close','Away_Fen%Close','Home_Fen%Close',
            'Away_ScoreClose5v5','Home_ScoreClose5v5','Away_ShotsClose5v5','Home_ShotsClose5v5','Away_Shot_AttemptsClose5v5','Home_Shot_AttemptsClose5v5','Away_CORSI%Close5v5','Home_CORSI%Close5v5','Away_Fen%Close5v5','Home_Fen%Close5v5',
            'Away_Hits','Home_Hits','Away_Blocks','Home_Blocks','Away_Blocks5v5','Home_Blocks5v5','Away_FO','Home_FO','Away_Give','Home_Give','Away_Take','Home_Take','Away_TRatio','Home_TRatio','Away_PIM','Home_PIM','Away_PPO',
            'Home_PPO','Away_PPG','Home_PPG','Away_xG','Home_xG','Away_xG5v5','Home_xG5v5','Away_xGClose','Home_xGClose','Away_xGClose5v5','Home_xGClose5v5','Away_xG%','Home_xG%','Away_xG%5v5','Home_xG%5v5','Away_xG%Close','Home_xG%Close',
            'Away_xG%Close5v5','Home_xG%Close5v5']

    #the final df to store all values
    finalDF = pd.DataFrame(columns=cols)

    #the files that will make up the data
    trainingFiles = ["Raw Data/nhl_pbp_20102011.csv",
                     "Raw Data/nhl_pbp_20112012.csv",
                     "Raw Data/nhl_pbp_20122013.csv",
                     "Raw Data/nhl_pbp_20132014.csv",
                     "Raw Data/nhl_pbp_20142015.csv",
                     "Raw Data/nhl_pbp_20152016.csv",
                     "Raw Data/nhl_pbp_20162017.csv",
                     "Raw Data/nhl_pbp_20172018.csv",
                     "Raw Data/nhl_pbp_20182019.csv",
                     "Raw Data/nhl_pbp_20192020.csv",
                     "Raw Data/nhl_pbp_20202021.csv",
                     "Raw Data/nhl_pbp_20212022.csv"]

    #the trainingframe
    trainingFrame = createTrainingFrame(trainingFiles)
    print(trainingFrame)

    #where the expected goals are stored, remove playoffs, fix game_id to include year
    xg = pd.read_csv("Raw Data/xGData2010-2021.csv")

    #create a scoring difference column to be used in the close calculations
    trainingFrame['Score_Diff'] = (trainingFrame['Away_Score']-trainingFrame['Home_Score']).abs()

    #account for team name change
    xg = xg.replace({'ARI':'PHX',
                     'TBL':'T.B',
                     'SJS':'S.J',
                     'LAK':'L.A',
                     'NJD':'N.J'})
    trainingFrame = trainingFrame.replace({'ARI':'PHX',
                                           'TBL':'T.B',
                                           'SJS':'S.J',
                                           'LAK':'L.A',
                                           'NJD':'N.J'})

    #iterate through all games
    for i in trainingFrame.Game_Id.unique():

        #do not include playoff games
        playoffs = trainingFrame[trainingFrame['Game_Id'] == i].isPlayoffs.unique()[0]
        if playoffs:
            continue

        print("Creating Game: " + str(i))

        #row to store in df
        row = [i,str(i)[0:4],trainingFrame[trainingFrame['Game_Id'] == i].Date.unique()[0],playoffs]

        #home and away
        away = trainingFrame[trainingFrame['Game_Id'] == i].Away_Team.unique()[0]
        home = trainingFrame[trainingFrame['Game_Id'] == i].Home_Team.unique()[0]

        #create a dataframe with only the game in question
        gameFrame = trainingFrame[(trainingFrame['Game_Id'] == i)]
        xgFrame = xg[xg['GameID'] == i]

        #count different statistics
        shots = countShots(away,home,gameFrame)
        shotAttempts = countShotAttempts(away,home,gameFrame)
        goals = countGoals(away,home,gameFrame)
        ending = RecordEnding(away,home,gameFrame)
        hits = countHits(away,home,gameFrame)
        blocks = countBlocks(away,home,gameFrame)
        fo = countFaceoffs(away,home,gameFrame)
        give = countGiveAways(away,home,gameFrame)
        take = countTakeAways(away,home,gameFrame)
        pims = countPenaltyMins(away,home,gameFrame)
        PPG = countPPG(away,home,gameFrame)
        expectedGoals = countXG(away,home,xgFrame)

        #count 5v5 stats
        shots5v5 = countShots(away,home,gameFrame,True)
        shotAttempts5v5 = countShotAttempts(away,home,gameFrame,True)
        goals5v5 = countGoals(away,home,gameFrame,True)
        blocks5v5 = countBlocks(away,home,gameFrame,True)
        expectedGoals5v5 = countXG(away,home,xgFrame,True)

        #count close stats
        shotsClose = countShots(away,home,gameFrame,False,True)
        shotAttemptsClose = countShotAttempts(away,home,gameFrame,False,True)
        goalsClose = countGoals(away,home,gameFrame,False,True)
        blocksClose = countBlocks(away,home,gameFrame,False,True)
        expectedGoalsClose = countXG(away,home,xgFrame,False,True)

        #count 5v5 close stats
        shotsClose5v5 = countShots(away,home,gameFrame,True,True)
        shotAttemptsClose5v5 = countShotAttempts(away,home,gameFrame,True,True)
        goalsClose5v5 = countGoals(away,home,gameFrame,True,True)
        blocksClose5v5 = countBlocks(away,home,gameFrame,True,True)
        expectedGoalsClose5v5 = countXG(away,home,xgFrame,True,True)

        #give take ratios
        if (take[0]+give[0]) == 0:
            awayRatio = 0
        else:
            awayRatio = take[0]/(take[0]+give[0])

        if (take[1]+give[1]) == 0:
            homeRatio = 0
        else:
            homeRatio = take[1]/(take[1]+give[1])

        #account for errors and determine winner
        if ending[1] == 'ERROR':
            if goals[0] > goals[1]:
                row.append(away)
            elif goals[1] > goals[0]:
                row.append(home)
            else:
                row.append('ERROR')
        else:
            row.append(ending[1])

        #append all strength stats
        row.append(ending[0])
        row.append(away)
        row.append(home)
        row.append(goals[0])
        row.append(goals[1])
        row.append(shots[0])
        row.append(shots[1])
        row.append(shotAttempts[0])
        row.append(shotAttempts[1])

        #CORSI all strength
        row.append((shotAttempts[0]/(shotAttempts[0]+shotAttempts[1]))*100)
        row.append((shotAttempts[1]/(shotAttempts[0]+shotAttempts[1]))*100)

        #Fenwick all strength
        row.append(((shotAttempts[0]-blocks[1])/((shotAttempts[0]-blocks[1])+(shotAttempts[1]-blocks[0])))*100)
        row.append(((shotAttempts[1]-blocks[0])/((shotAttempts[0]-blocks[1])+(shotAttempts[1]-blocks[0])))*100)

        #append 5v5 stats
        row.append(goals5v5[0])
        row.append(goals5v5[1])
        row.append(shots5v5[0])
        row.append(shots5v5[1])
        row.append(shotAttempts5v5[0])
        row.append(shotAttempts5v5[1])

        #CORSI 5v5
        row.append((shotAttempts5v5[0]/(shotAttempts5v5[0]+shotAttempts5v5[1]))*100)
        row.append((shotAttempts5v5[1]/(shotAttempts5v5[0]+shotAttempts5v5[1]))*100)

        #Fenwick 5v5
        row.append(((shotAttempts5v5[0]-blocks5v5[1])/((shotAttempts5v5[0]-blocks5v5[1])+(shotAttempts5v5[1]-blocks5v5[0])))*100)
        row.append(((shotAttempts5v5[1]-blocks5v5[0])/((shotAttempts5v5[0]-blocks5v5[1])+(shotAttempts5v5[1]-blocks5v5[0])))*100)

        #append close stats
        row.append(goalsClose[0])
        row.append(goalsClose[1])
        row.append(shotsClose[0])
        row.append(shotsClose[1])
        row.append(shotAttemptsClose[0])
        row.append(shotAttemptsClose[1])

        #CORSI Close
        row.append((shotAttemptsClose[0]/(shotAttemptsClose[0]+shotAttemptsClose[1]))*100)
        row.append((shotAttemptsClose[1]/(shotAttemptsClose[0]+shotAttemptsClose[1]))*100)

        #Fenwick Close
        row.append(((shotAttemptsClose[0]-blocksClose[1])/((shotAttemptsClose[0]-blocksClose[1])+(shotAttemptsClose[1]-blocksClose[0])))*100)
        row.append(((shotAttemptsClose[1]-blocksClose[0])/((shotAttemptsClose[0]-blocksClose[1])+(shotAttemptsClose[1]-blocksClose[0])))*100)

        #append close 5v5 stats
        row.append(goalsClose5v5[0])
        row.append(goalsClose5v5[1])
        row.append(shotsClose5v5[0])
        row.append(shotsClose5v5[1])
        row.append(shotAttemptsClose5v5[0])
        row.append(shotAttemptsClose5v5[1])

        #CORSI Close 5v5
        row.append((shotAttemptsClose5v5[0]/(shotAttemptsClose5v5[0]+shotAttemptsClose5v5[1]))*100)
        row.append((shotAttemptsClose5v5[1]/(shotAttemptsClose5v5[0]+shotAttemptsClose5v5[1]))*100)

        #Fenwick Close
        if (shotAttemptsClose5v5[0]-blocksClose5v5[1])+(shotAttemptsClose5v5[1]-blocksClose5v5[0]) == 0:
            row.append(0)
            row.append(0)
        else:
            row.append(((shotAttemptsClose5v5[0]-blocksClose5v5[1])/((shotAttemptsClose5v5[0]-blocksClose5v5[1])+(shotAttemptsClose5v5[1]-blocksClose5v5[0])))*100)
            row.append(((shotAttemptsClose5v5[1]-blocksClose5v5[0])/((shotAttemptsClose5v5[0]-blocksClose5v5[1])+(shotAttemptsClose5v5[1]-blocksClose5v5[0])))*100)

        #append remaining stats
        row.append(hits[0])
        row.append(hits[1])
        row.append(blocks[0])
        row.append(blocks[1])
        row.append(blocks5v5[0])
        row.append(blocks5v5[1])
        row.append(fo[0])
        row.append(fo[1])
        row.append(give[0])
        row.append(give[1])
        row.append(take[0])
        row.append(take[1])
        row.append(awayRatio)
        row.append(homeRatio)

        #append penalty related stats
        row.append(pims[0])
        row.append(pims[1])
        row.append(pims[2])
        row.append(pims[3])
        row.append(PPG[0])
        row.append(PPG[1])

        #append the expected goals
        row.append(expectedGoals[0])
        row.append(expectedGoals[1])
        row.append(expectedGoals5v5[0])
        row.append(expectedGoals5v5[1])
        row.append(expectedGoalsClose[0])
        row.append(expectedGoalsClose[1])
        row.append(expectedGoalsClose5v5[0])
        row.append(expectedGoalsClose5v5[1])

        #xG percentages
        row.append((expectedGoals[0]/(expectedGoals[0]+expectedGoals[1]))*100)
        row.append((expectedGoals[1]/(expectedGoals[0]+expectedGoals[1]))*100)
        row.append((expectedGoals5v5[0]/(expectedGoals5v5[0]+expectedGoals5v5[1]))*100)
        row.append((expectedGoals5v5[1]/(expectedGoals5v5[0]+expectedGoals5v5[1]))*100)
        row.append((expectedGoalsClose[0]/(expectedGoalsClose[0]+expectedGoalsClose[1]))*100)
        row.append((expectedGoalsClose[1]/(expectedGoalsClose[0]+expectedGoalsClose[1]))*100)
        row.append((expectedGoalsClose5v5[0]/(expectedGoalsClose5v5[0]+expectedGoalsClose5v5[1]))*100)
        row.append((expectedGoalsClose5v5[1]/(expectedGoalsClose5v5[0]+expectedGoalsClose5v5[1]))*100)

        #place the row in the dataframe
        finalDF.loc[len(finalDF)] = row

    #output the data to a csv
    finalDF.to_csv("Database/NHLData.csv",index=False)

main()


