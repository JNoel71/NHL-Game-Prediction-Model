import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import log_loss, accuracy_score, make_scorer, roc_auc_score, f1_score
from sklearn.model_selection import cross_val_score, cross_val_predict
from sklearn.feature_selection import SelectPercentile, mutual_info_classif
from sklearn.model_selection import RandomizedSearchCV
import numpy as np

def removeEarlyGames(df,games=20):
    """Remove the first x games for each team in a season.
    
    Parameters:
        df(Dataframe) - the dataframe containing all games.
        games(Int) - the number of games to remove.
    
    Returns:
        df(Dataframe) - the dataframe with the given number of games removed."""
    
    #get all team names
    teams = df.Home_Team.unique()

    #get all seasons
    seasons = df.season.unique()

    #where the games that will be removed are stored
    gamesToRemove = set()

    for i in seasons:
        #get the games from a given season
        season = df[df["season"] == i].sort_values("Game_Id")
        for j in teams:
            #get the teams first x games
            earlyGames = season[(season["Away_Team"] == j) | (season["Home_Team"] == j)].head(games)
            gameList = earlyGames.Game_Id.unique()
            gamesToRemove.update(gameList)
    
    #remove games from the dataframe
    df = df[~df.Game_Id.isin(list(gamesToRemove))]

    return df

def UseOnlyEarlyGames(df,games=20):
    """Retrieve only the first x games for each team in a season.
    
    Parameters:
        df(Dataframe) - the dataframe containing all games.
        games(Int) - the number of games to retrieve.
    
    Returns:
        df(Dataframe) - the dataframe the retrieved games."""
    
    #get all team names
    teams = df.Home_Team.unique()

    #get all seasons
    seasons = df.season.unique()

    #where the games that will be removed are stored
    gamesToRemove = set()

    for i in seasons:
        #get the games from a given season
        season = df[df["season"] == i].sort_values("Game_Id")
        for j in teams:
            #get the teams first x games
            earlyGames = season[(season["Away_Team"] == j) | (season["Home_Team"] == j)].head(games)
            gameList = earlyGames.Game_Id.unique()
            gamesToRemove.update(gameList)
    
    #remove games from the dataframe
    df = df[df.Game_Id.isin(list(gamesToRemove))]

    return df

def UseOnlyMidGames(df,games=42):
    """Retrieve only the middle x games for each team in a season.
    
    Parameters:
        df(Dataframe) - the dataframe containing all games.
        games(Int) - the number of games to retrieve.
    
    Returns:
        df(Dataframe) - the dataframe the retrieved games."""
    
    #get all team names
    teams = df.Home_Team.unique()

    #get all seasons
    seasons = df.season.unique()

    #remove games from the dataframe
    df = removeEarlyGames(df)

    gamesToRemove = set()
    
    for i in seasons:
        #get the games from a given season
        season = df[df["season"] == i].sort_values("Game_Id")
        for j in teams:
            #get the teams first x games
            earlyGames = season[(season["Away_Team"] == j) | (season["Home_Team"] == j)].head(games)
            gameList = earlyGames.Game_Id.unique()
            gamesToRemove.update(gameList)
    
    #remove games from the dataframe
    df = df[df.Game_Id.isin(list(gamesToRemove))]

    return df

def UseOnlyLateGames(df):
    """Retrieve only late games for each team in a season.
    
    Parameters:
        df(Dataframe) - the dataframe containing all games.
    
    Returns:
        df(Dataframe) - the dataframe the retrieved games."""
    
    #get the early and mid games
    earlyGames = UseOnlyEarlyGames(df)
    midGames = UseOnlyMidGames(df)

    #remove early and mid games from the data
    df = df[~df.Game_Id.isin(earlyGames.Game_Id.unique())]
    df = df[~df.Game_Id.isin(midGames.Game_Id.unique())]

    return df

def parameterTuning(classifier,trainX,trainY):
    """Use RandomizedSearchCV to tune the parameters of an ExtraTreesClassifier.

    Parameters:
        classifier(ExtraTreesClassifier) - an ExtraTreesClassifier instance.
        trainX(Dataframe) - the training features.
        trainY(Dataframe) - the training targets.

    Returns:
        search.best_params_(Dict) - the best parameters found by the search
    """

    #the parameter grid to search
    params = {
        'n_estimators': range(50,750,25),
        'max_features': range(1,trainX.shape[1],1),
        'min_samples_leaf': range(1,100,1),
        'min_samples_split': range(2,100,1),
        'random_state':[42]
    }

    #create a log loss scorer
    logLoss = make_scorer(score_func=log_loss, greater_is_better=False)

    #create the randomized search and fit the model
    tuner = RandomizedSearchCV(classifier,params,cv=10,scoring=logLoss,n_iter=200,random_state=42)
    search = tuner.fit(trainX,trainY)

    return search.best_params_

def chooseModel(season,model):
    """Create the given model and predict the given season

    Parameters:
        season(Int) - the season to predict.
        model(String) - the model to be created (Early, Mid, Late).

    Returns:
        proba(List) - a list of probabilities from the model.
        preds(List) - a list of outcomes predicted by the model.
        testingY(List) - a list that contains the actual outcome from the model
    """
    #read in the csv
    df = pd.read_csv("Dataframes/CombinedFrame.csv")

    #create training data
    trainingFrame = df[(df['season'] < season)]

    #select games based off model
    if model == 'Early':
        trainingFrame = UseOnlyEarlyGames(trainingFrame)
    elif model == 'Mid':
        trainingFrame = UseOnlyMidGames(trainingFrame)
    elif model == 'Late':
        trainingFrame = UseOnlyLateGames(trainingFrame)
    else:
        print("Error: use either 'Early', 'Mid', or 'Late' for model parameter.")
        return
    
    #remove OT games, drop unneeded columns, and replace NaNs/Inf
    trainingFrame = trainingFrame[trainingFrame['RegOrOT'] != 'OT']
    trainingFrame = trainingFrame.drop(['Game_Id','RegOrOT','Away_Team','Home_Team','season','isPlayoff'], axis=1) 
    trainingFrame.replace([np.inf, -np.inf], np.nan, inplace=True)
    trainingFrame = trainingFrame.fillna(0)

    #separate x and y for the training set
    trainingX = trainingFrame[trainingFrame.columns.difference(['Outcome'])]
    trainingY = trainingFrame['Outcome'].astype('int32')

    #create the model
    classifier = ExtraTreesClassifier(random_state=42)

    #perform feature selection
    selector = SelectPercentile(score_func=mutual_info_classif,percentile=10).fit(trainingX,trainingY)

    #adjust the training features
    trainingX = selector.transform(trainingX)

    #select parameters selected from runTests based off model
    if model == 'Early':
        params = {'random_state': 42, 'n_estimators': 250, 'min_samples_split': 61, 'min_samples_leaf': 11, 'max_features': 48}
    elif model == 'Mid':
        params = {'random_state': 42, 'n_estimators': 75, 'min_samples_split': 94, 'min_samples_leaf': 31, 'max_features': 13}
    elif model == 'Late':
        params = {'random_state': 42, 'n_estimators': 350, 'min_samples_split': 31, 'min_samples_leaf': 87, 'max_features': 32}

    #create model
    classifier = ExtraTreesClassifier(**params)

    #get cross validation results
    cvProbs = cross_val_predict(classifier,trainingX,trainingY,cv=10,method='predict_proba')
    
    #create testing data
    testingFrame = df[df['season'] == season]

    #select games based off model
    if model == 'Early':
        testingFrame = UseOnlyEarlyGames(testingFrame)
    elif model == 'Mid':
        testingFrame = UseOnlyMidGames(testingFrame)
    elif model == 'Late':
        testingFrame = UseOnlyLateGames(testingFrame)
    
    #drop unneeded columns and replace NaNs/Inf
    testingFrame = testingFrame.drop(['Game_Id','RegOrOT','Away_Team','Home_Team','season','isPlayoff'], axis=1) 
    testingFrame.replace([np.inf, -np.inf], np.nan, inplace=True)
    testingFrame = testingFrame.fillna(0)

    #separate x and y for the training set
    testingX = testingFrame[testingFrame.columns.difference(['Outcome'])]
    testingY = testingFrame['Outcome'].astype('int32')

    #adjust testing features
    testingX = selector.transform(testingX)

    #fit model
    classifier.fit(trainingX,trainingY)

    #score model
    proba = classifier.predict_proba(testingX)
    preds = classifier.predict(testingX)

    return list(proba), list(preds), list(testingY), list(cvProbs[:, 1]), list(trainingY)

def runTests(season,state):
    """Run hyperparameter tuning and select features.

    Parameters:
        season(Int) - the season to predict.
        model(String) - the model to be created (Early, Mid, Late).
    """
    #read in the data
    df = pd.read_csv("Dataframes/CombinedFrame.csv")

    #create training data
    trainingFrame = df[(df['season'] < season)]

    #determine which games to use given the model string
    print(state)
    if state == 'Early':
        trainingFrame = UseOnlyEarlyGames(trainingFrame)
    elif state == 'Mid':
        trainingFrame = UseOnlyMidGames(trainingFrame)
    elif state == 'Late':
        trainingFrame = UseOnlyLateGames(trainingFrame)
    else:
        print("Error: use either 'Early', 'Mid', or 'Late' for model parameter.")
        return

    #remove OT games, drop unneeded columns, and replace NaNs/Inf
    trainingFrame = trainingFrame[trainingFrame['RegOrOT'] != 'OT']
    trainingFrame = trainingFrame.drop(['Game_Id','RegOrOT','Away_Team','Home_Team','season','isPlayoff'], axis=1) 
    trainingFrame.replace([np.inf, -np.inf], np.nan, inplace=True)
    trainingFrame = trainingFrame.fillna(0)

    #separate x and y for the training set
    trainingX = trainingFrame[trainingFrame.columns.difference(['Outcome'])]
    trainingY = trainingFrame['Outcome'].astype('int32')

    #create the model
    classifier = ExtraTreesClassifier(random_state=42)
    
    #perform feature selection
    selector = SelectPercentile(score_func=mutual_info_classif,percentile=10).fit(trainingX,trainingY)
    
    #adjust the training features
    trainingX = selector.transform(trainingX)

    #tune parameters
    params = parameterTuning(classifier,trainingX,trainingY)
    print(params)

    #set classifier parameters
    classifier = ExtraTreesClassifier(**params)

    print(state + " Cross Validation Scores:")

    #iterate through the scoring metrics
    scoring = ['accuracy','neg_log_loss','roc_auc','f1']
    for i in scoring:
        cv = cross_val_score(classifier,trainingX,trainingY,cv=10,scoring=i)
        print(i + ": " + str(cv.mean()))

    print("")

    #create testing data
    testingFrame = df[df['season'] == season]

    #determine which games to use given the model string
    if state == 'Early':
        testingFrame = UseOnlyEarlyGames(testingFrame)
    elif state == 'Mid':
        testingFrame = UseOnlyMidGames(testingFrame)
    elif state == 'Late':
        testingFrame = UseOnlyLateGames(testingFrame)

    #drop unneeded columns and replace NaNs/Inf
    testingFrame = testingFrame.drop(['Game_Id','RegOrOT','Away_Team','Home_Team','season','isPlayoff'], axis=1) 
    testingFrame.replace([np.inf, -np.inf], np.nan, inplace=True)
    testingFrame = testingFrame.fillna(0)

    #separate x and y for the training set
    testingX = testingFrame[testingFrame.columns.difference(['Outcome'])]
    testingY = testingFrame['Outcome'].astype('int32')

    #adjust testing features
    testingX = selector.transform(testingX)

    #fit model
    classifier.fit(trainingX,trainingY)

    #score model
    proba = classifier.predict_proba(testingX)
    preds = classifier.predict(testingX)

    print("Testing " + state + " " + str(season) + " season")
    print("Accuracy: " + str(accuracy_score(testingY,preds)))
    print("Log Loss: " + str(log_loss(testingY,proba)))
    print("AUC: " + str(roc_auc_score(testingY,preds)))
    print("F1-Score: " + str(f1_score(testingY,preds)))
    print("")

def main(season):
    """Create all three models and output performance.

    Parameters:
        season(Int) - the season to predict.
    """

    #where cross validation results are stored
    cvAcc =[]
    cvLL = []
    cvAUC = []
    cvF1 = []

    #where test results are stored
    testAcc =[]
    testLL = []
    testAUC = []
    testF1 = []

    for i in range(10):
        #create the three models
        earlyProba, earlyPreds, earlyOutcomes, earlyCVProba, earlyCVOutcomes = chooseModel(season,'Early')
        midProba, midPreds, midOutcomes, midCVProba, midCVOutcomes  = chooseModel(season,'Mid')
        lateProba, latePreds, lateOutcomes, lateCVProba, lateCVOutcomes  = chooseModel(season,'Late')

        #join probabilites, predictions, and outcomes together
        cvProba = earlyCVProba + midCVProba + lateCVProba
        cvPreds = [np.round(x) for x in cvProba]
        cvOutcomes = earlyCVOutcomes + midCVOutcomes + lateCVOutcomes
        totalProba = earlyProba + midProba + lateProba
        totalPreds = earlyPreds + midPreds + latePreds
        totalOutcomes = earlyOutcomes + midOutcomes + lateOutcomes

        #add estimations to lists
        cvAcc.append(accuracy_score(cvOutcomes,cvPreds))
        cvLL.append(log_loss(cvOutcomes,cvProba))
        cvAUC.append(roc_auc_score(cvOutcomes,cvPreds))
        cvF1.append(f1_score(cvOutcomes,cvPreds))

        testAcc.append(accuracy_score(totalOutcomes,totalPreds))
        testLL.append(log_loss(totalOutcomes,totalProba))
        testAUC.append(roc_auc_score(totalOutcomes,totalPreds))
        testF1.append(f1_score(totalOutcomes,totalPreds))

    #output metrics
    print("Cross Validation Results")
    print("Accuracy: " + str(sum(cvAcc)/len(cvAcc)))
    print("Log Loss: " + str(sum(cvLL)/len(cvLL)))
    print("AUC: " + str(sum(cvAUC)/len(cvAUC)))
    print("F1-Score: " + str(sum(cvF1)/len(cvF1)))
    print(" ")
    print("Testing " + str(season) + " season")
    print("Accuracy: " + str(sum(testAcc)/len(testAcc)))
    print("Log Loss: " + str(sum(testLL)/len(testLL)))
    print("AUC: " + str(sum(testAUC)/len(testAUC)))
    print("F1-Score: " + str(sum(testF1)/len(testF1)))

#these methods select hyperparameters 
#runTests(2021,'Early')
#runTests(2021,'Mid')
#runTests(2021,'Late')
    
#predict outcomes
main(2021)
