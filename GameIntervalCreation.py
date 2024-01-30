import pandas as pd
import numpy as np

def getIndividualStat(statName,team,df,avg=False):
    """Calculate the summed total of a given stat for a given team.
    
    Parameters:
        statName(String) - the name of the stat to be found.
        team(String) - the abbrieviation of the desired team.
        df(DataFrame) - the available game data.
        avg(Bool) - whether or not to calculate the average.
    
    Returns:
        totalFor(Float) - the sum or average of the stat for the team.
        totalAgainst(Float) - the sum or average of the stat againsst the team.
    """

    #create the dfs for the away and home games
    dfAway = df[(df["Away_Team"] == team)]
    dfHome = df[(df["Home_Team"] == team)]

    #create the strings
    awayString = "Away_" + statName
    homeString = "Home_" + statName

    #get the data for away games
    awayStatFor = list(dfAway[awayString].values)
    awayStatAgainst = list(dfAway[homeString].values)
    awayDates = list(dfAway['Date'])

    #get the data for home games
    homeStatFor = list(dfHome[homeString].values)
    homeStatAgainst = list(dfHome[awayString].values)
    homeDates = list(dfHome['Date'])

    #complete dataframe
    d = {'Date': awayDates + homeDates, 'For': awayStatFor + homeStatFor, 'Against': awayStatAgainst + homeStatAgainst}
    completeDF = pd.DataFrame(d)
    completeDF['Date'] = pd.to_datetime(completeDF['Date'],format='%Y-%m-%d')
    completeDF.sort_values(by='Date',inplace = True)

    #determine if we are calculating the sum or average
    match avg:
        case False:
            #get totals
            totalFor = (sum(awayStatFor) + sum(homeStatFor))
            totalAgainst = (sum(awayStatAgainst) + sum(homeStatAgainst))
            return totalFor, totalAgainst
        case True:
            #linearly weight values when calculating average
            if (completeDF.shape[0]) > 0:
                increment = 1/completeDF.shape[0]
                weightedStatFor = []
                weightedStatAgainst = []
                counter = 0
                for row in completeDF.itertuples():
                    weightedStatFor.append(row.For*(increment*(counter+1)))
                    weightedStatAgainst.append(row.Against*(increment*(counter+1)))

                totalFor = sum(weightedStatFor)
                totalAgainst = sum(weightedStatAgainst)
            else:
                totalFor = 0
                totalAgainst = 0 

            return totalFor, totalAgainst

def getWinsLoses(team,df):
    """Calculate the number of wins and loses for a team.
    
    Parameters:
        team(String) - the abbrieviation of the desired team.
        df(DataFrame) - the available game data.
    
    Returns:
        wins(Int) - the number of games the team won.
        loses(Int) - the number of games the team lost.
    """
    wins = df[df['Winner'] == team].shape[0]
    loses = df[df['Winner'] != team].shape[0]
    
    return [wins,loses]

def calculateCORSI(shotAttemptsFor,shotAttemptsAgainst,average=False):
    """Calculate the CORSI, given shot attempts.
    
    Parameters:
        shotAttemptsFor(Int) - the number of shot attempts for.
        shotAttemptsAgainst(Int) - the number of shot attempts against.
        average(Bool) - if the calculate should be the average or the sum.
    
    Returns:
        CORSI(Float) - the average or sum for the CORSI
    """
    match average:
        case False:
            return shotAttemptsFor - shotAttemptsAgainst
        case True:
            #account for divided by zero errors
            return (shotAttemptsAgainst + shotAttemptsFor) and (shotAttemptsFor/(shotAttemptsAgainst + shotAttemptsFor)) or 0
            
def collectDataForTeam(team,df,gameWindow):
    """Collect all the stats for a certain team before a game.
    
    Parameters:
        team(String) - the abbrieviation of the desired team.
        df(DataFrame) - the available game data.
        gameWindow(Int) - the number of recent games to use.
    
    Returns:
        totals(List) - a list with all the statistics to be added to the main dataframe.
    """
    #only select required games
    df = df[(df["Away_Team"] == team) | (df["Home_Team"] == team)].tail(gameWindow)
    
    #list where the items to be placed in a row are stored
    totals = []

    #collect stats
    goals = getIndividualStat("Score",team,df)
    goalsAvg = getIndividualStat("Score",team,df,True)
    goals5v5 = getIndividualStat("Score5v5",team,df)
    goals5v5Avg = getIndividualStat("Score5v5",team,df,True)
    goalsClose5v5 = getIndividualStat("ScoreClose5v5",team,df)
    goalsClose5v5Avg = getIndividualStat("ScoreClose5v5",team,df,True)
    shots = getIndividualStat("Shots",team,df)
    shotsAvg = getIndividualStat("Shots",team,df,True)
    shotAttempts = getIndividualStat("Shot_Attempts",team,df)
    shotAttempts5v5 = getIndividualStat("Shot_Attempts5v5",team,df)
    shotAttemptsClose5v5 = getIndividualStat("Shot_AttemptsClose5v5",team,df)
    faceOffs = getIndividualStat("FO",team,df)
    hits = getIndividualStat("Hits",team,df)
    hitsAvg = getIndividualStat("Hits",team,df,True)
    pims = getIndividualStat("PIM",team,df)
    pimsAvg = getIndividualStat("PIM",team,df,True)
    blocks = getIndividualStat("Blocks",team,df)
    blocksAvg = getIndividualStat("Blocks",team,df,True)
    giveAways = getIndividualStat("Give",team,df)
    giveAwaysAvg = getIndividualStat("Give",team,df,True)
    takeAways = getIndividualStat("Take",team,df)
    takeAwaysAvg = getIndividualStat("Take",team,df,True)
    PPO = getIndividualStat("PPO",team,df)
    PPG = getIndividualStat("PPG",team,df)

    #get XG
    xg = getIndividualStat("xG",team,df)
    xgAvg = getIndividualStat("xG",team,df,True)
    xg5v5 = getIndividualStat("xG5v5",team,df)
    xg5v5Avg = getIndividualStat("xG5v5",team,df,True)
    xg5v5Close = getIndividualStat("xGClose5v5",team,df)
    xg5v5CloseAvg = getIndividualStat("xGClose5v5",team,df,True)

    #get wins and loses
    winsLoses = getWinsLoses(team,df)

    #calculate shooting percentage
    shootRate = shots[0] and (goals[0]/shots[0]) or 0
    
    #calculate save percentage
    saveRate = shots[1] and (1 - (goals[1]/shots[1])) or 0

    #calculate shooting percentage
    shootPer = (shots[0]+goals[0]) and (goals[0]/(shots[0]+goals[0])) or 0
    
    #calculate save percentage
    savePer = (shots[1]+goals[1]) and (1 - (goals[1]/(shots[1]+goals[1]))) or 0

    #PowerPlay Percentage
    PPPer = PPO[0] and (PPG[0]/PPO[0]) or 0

    #PenaltyKill Percentage
    PKPer = PPO[1] and (PPG[1]/PPO[1]) or 0

    #calculate the PDO
    PDOPer = shootPer + savePer
    
    #calculate CORSI
    shotAttemptsFor = shotAttempts[0]
    shotAttemptsAgainst = shotAttempts[1]
    CORSISum = calculateCORSI(shotAttemptsFor,shotAttemptsAgainst)
    CORSIAvg = calculateCORSI(shotAttemptsFor,shotAttemptsAgainst,True)

    #calculate CORSI for 5v5
    shotAttemptsFor5v5 = shotAttempts5v5[0]
    shotAttemptsAgainst5v5 = shotAttempts5v5[1]
    CORSI5v5Sum = calculateCORSI(shotAttemptsFor5v5,shotAttemptsAgainst5v5)
    CORSI5v5Avg = calculateCORSI(shotAttemptsFor5v5,shotAttemptsAgainst5v5,True)

    #calculate CORSI for 5v5 close situations
    shotAttemptsFor5v5Close = shotAttemptsClose5v5[0]
    shotAttemptsAgainst5v5Close = shotAttemptsClose5v5[1]
    CORSI5v5CloseSum = calculateCORSI(shotAttemptsFor5v5Close,shotAttemptsAgainst5v5Close)
    CORSI5v5CloseAvg = calculateCORSI(shotAttemptsFor5v5Close,shotAttemptsAgainst5v5Close,True)

    #calculate faceoff percentage
    FOPer = (faceOffs[0] + faceOffs[1]) and (faceOffs[0]/(faceOffs[0] + faceOffs[1])) or 0

    #calculate xG share
    xGPer = (xg[0] + xg[1]) and (xg[0]/(xg[0] + xg[1])) or 0
    
    #the totals
    totals = totals + [winsLoses[0],winsLoses[1],goals[0],goals[1],goalsAvg[0],goalsAvg[1],goals5v5[0],goals5v5[1],
            goals5v5Avg[0],goals5v5Avg[1],goalsClose5v5[0],goalsClose5v5[1],goalsClose5v5Avg[0],goalsClose5v5Avg[1],
            shots[0],shots[1],shotsAvg[0],shotsAvg[1],CORSISum,CORSIAvg,CORSI5v5Sum,CORSI5v5Avg,
            CORSI5v5CloseSum,CORSI5v5CloseAvg,FOPer,hits[0],hits[1],hitsAvg[0],hitsAvg[1],pims[0],pims[1],pimsAvg[0],pimsAvg[1],
            blocks[0],blocks[1],blocksAvg[0],blocksAvg[1],giveAways[0],giveAways[1],giveAwaysAvg[0],giveAwaysAvg[1],
            takeAways[0],takeAways[1],takeAwaysAvg[0],takeAwaysAvg[1],xg[0],xg[1],xgAvg[0],xgAvg[1],xg5v5[0],xg5v5[1],
            xg5v5Avg[0],xg5v5Avg[1],xg5v5Close[0],xg5v5Close[1],xg5v5CloseAvg[0],xg5v5CloseAvg[1],PPPer,PKPer,shootRate,saveRate,
            shootPer,savePer,PDOPer,xGPer]

    return totals
    
def createFrame(df,dfOut,gameWindow,cross):
    """Create the dataframe of games.
    
    Parameters:
        df(DataFrame) - the available game data.
        dfOut(DataFrame) - the empty dataframe that each game will be added to.
        gameWindow(Int) - the number of recent games to use.
        cross(Bool) - should games from previous seasons be used?
    
    Returns:
        dfOut(DataFrame) - the filled dataframe that contains all games.
    """
    #iterate through all games
    for i in df.Game_Id.unique():
        #home and away teams as well as the season
        away = df[df['Game_Id'] == i].Away_Team.unique()[0]
        home = df[df['Game_Id'] == i].Home_Team.unique()[0]
        season = df[df['Game_Id'] == i].season.unique()[0]
        date = df[df['Game_Id'] == i].Date.unique()[0]
        regOrOT = df[df['Game_Id'] == i].RegOrOT.unique()[0]
        playoff = df[df['Game_Id'] == i].isPlayoffs.unique()[0]

        #determine if the home or away team won
        if df[df['Game_Id'] == i]['Winner'].values[0] == df[df['Game_Id'] == i]['Home_Team'].values[0]:
            outcome = 1
        elif df[df['Game_Id'] == i]['Winner'].values[0] == df[df['Game_Id'] == i]['Away_Team'].values[0]:
            outcome = 0

        #determine if data can cross over between seasons
        if cross:
            gameData = df[(df["Date"] < date)]
        else:
            gameData = df[(df["Date"] < date) & (df["season"] == season)]

        #get away data for away teams
        awayTeamData = collectDataForTeam(away,gameData,gameWindow)

        #get home data
        homeTeamData = collectDataForTeam(home,gameData,gameWindow)

        #begin the row with the game, away team and home team ids.
        lst = [i,regOrOT,away,home,season,playoff]

        #represent features as home_value - away_value
        for j in range(len(awayTeamData)):
            lst.append(homeTeamData[j] - awayTeamData[j])
        
        #add the outcome
        lst.append(outcome)
        
        #add the row to the dataframe
        dfOut.loc[len(dfOut)] = lst

    return dfOut

def main(cross,lst):
    """Main method which calls other methods to create game instances.

    Parameters:
        cross(Bool) - should data be taken from previous seasons?
        lst(List if Ints) - list of integers representing the previous number of games used in instance creation.
    """
    #read in database
    data = pd.read_csv('Database/NHLData.csv')

    #fill infs and NaNs with 0
    data.replace([np.inf, -np.inf], np.nan, inplace=True)
    data = data.fillna(0)

    #convert the data column and sort by it
    data['Date'] = pd.to_datetime(data['Date'],format='%Y-%m-%d')
    data.sort_values(by='Date',inplace = True)

    #base columns
    baseCols = ["Game_Id",
                "RegOrOT",
                "Away_Team",
                "Home_Team",
                "season",
                "isPlayoff",
                "Wins",
                "Loses",
                "Goals",
                "GoalsAgainst",
                "GoalsAvg",
                "GoalsAgainstAvg",
                "Goals5v5",
                "GoalsAgainst5v5",
                "Goals5v5Avg",
                "GoalsAgainst5v5Avg",
                "GoalsClose5v5",
                "GoalsAgainstClose5v5",
                "GoalsClose5v5Avg",
                "GoalsAgainstClose5v5Avg",
                "Shots",
                "ShotsAgainst",
                "ShotsAvg",
                "ShotsAgainstAvg",
                "CORSI",
                "CORSIAvg",
                "CORSI5v5",
                "CORSI5v5Avg",
                "CORSIClose5v5",
                "CORSIClose5v5Avg",
                "FO",
                "Hits",
                "HitsAgainst",
                "HitsAvg",
                "HitsAgainstAvg",
                "PIMS",
                "PIMSAgainst",
                "PIMSAvg",
                "PIMSAgainstAvg",
                "Blocks",
                "BlocksAgainst",
                "BlocksAvg",
                "BlocksAgainstAvg",
                "Give",
                "GiveAgainst",
                "GiveAvg",
                "GiveAgainstAvg",
                "Take",
                "TakeAgainst",
                "TakeAvg",
                "TakeAgainstAvg",
                "XGFor",
                "XGAgainst",
                "XGForAvg",
                "XGAgainstAvg",
                "XGFor5v5",
                "XGAgainst5v5",
                "XGFor5v5Avg",
                "XGAgainst5v5Avg",
                "XGFor5v5Close",
                "XGAgainst5v5Close",
                "XGFor5v5CloseAvg",
                "XGAgainst5v5CloseAvg",
                "PP%",
                "PK%",
                "shRate",
                "svRate",
                "sh%",
                "sv%",
                "PDO%",
                "xG%",
                "Outcome"]

    #create dataframe
    trainDF = pd.DataFrame(columns=baseCols)

    #iterate through the number of games to be used
    for i in lst:

        #print progress
        if cross:
            print("Creating " + str(i) + " Games with Cross")
        else:
            print("Creating " + str(i) + " Games with No Cross")

        #fill the dataframe
        newDF = createFrame(data.copy(),trainDF.copy(),i,cross)

        #create csv
        if cross:
            newDF.to_csv("DataFrames/" + str(i) + "Cross.csv",index=False)
        else:
            newDF.to_csv("DataFrames/" + str(i) + "NoCross.csv",index=False)

main(False,[5,10,20,40,82])
main(True,[5,10,20,40,82])
 
