# NHL Pre-game Prediction Model
## Overview
This is a Python repo that contains a machine learning model which uses data from the NHL API to determine the likelihood of each team winning a given regular season NHL game before it takes place.

- **DatabaseCreationNHL.py** - this script uses the play-by-play data found in the raw data folder to summarize what took place in each given game.
- **GameIntervalCreation.py** - this script creates the instances to be predicted. In other words for each game in the dataset, it gathers information from previous games to assess the quality of each team in the match. This file has the ability to create features based on the number of games requested for team assessment (i.e. how many previous games should be used to judge team quality?) and whether or not the previous games can cross over into the previous season.
- **makeCombinedDataset.py** - this script takes multiple csvs created by GameIntervalCreation and joins them on their unique game IDs thus making a single dataset with over 600 features.
- **ModelCreation.py** - this script reads the combined dataset and using the 2010-2020 NHL seasons, performs feature selection and hyperparameter tuning before predicting game outcomes in the 2021 NHL season.

## How it Works
### Basic Approach
Rather than attempting to predict the whole NHL with a single model, I decided to split the season into early, middle, and late stages. The early stage is the first 20 games for each team, the middle being the middling 42 games, and the late stage being the last 20 games given a typical 82-game season. Therefore, this approach is made up of three separate models (early, middle, and late) which all work together to predict the complete NHL season. 

To better utilize this approach I used multiple game windows for feature engineering, specifically, I used the last 5, 10, 20, 40, and 82 games. This means that for each of these game windows, I created an entire feature set within which features were engineered only using the last "x" number of games for each team. For each game window, I also created one feature set that made use of cross-over and one that did not. When I refer to cross-over I am referring to whether the game window can retrieve games from the previous season or not. Features were averaged linearly similar to how MoneyPuck.com creates its model, you can read more about that here: https://moneypuck.com/about.htm. 

Lastly, features were represented as the home value for the performance indicator minus the away value for the performance indicator. These halved the total number of features in the feature set while allowing me to focus on relative team strength. A paper written by Gianni Pischedda inspired this feature representation, you can read the paper here: https://www.researchgate.net/publication/284457066_Predicting_NHL_Match_Outcomes_with_ML_Models.

### The Data
The model is built on data from the NHL's API, which is spatiotemporal data that records events that took place throughout games. This includes information about when the event took place, its location on the ice, and the teams/players that were involved in the play. I retrieved the data from the NHL API using a Python module named hockey_scraper which was developed by Harry Shomer and you can read about it here: https://github.com/HarryShomer/Hockey-Scraper.

I also included expected goals (xG) data from my own model which you can read about in this repo: https://github.com/JNoel71/NHL-Expected-Goals-xG-Model.

### Model Features
As was already mentioned there are over 600 features in the main dataset so rather than listing features I will outline which performance indicators appear in the feature set.

1) Wins
2) Loses
3) Goals
4) Shots
5) CORSI
6) Faceoffs
7) Hits
8) Penalty Minutes
9) Blocks
10) Giveaways
11) Takeaways
12) Expected Goals (xG)
13) Power-play %
14) Penalty-kill %
15) Shooting %
16) Save %
17) PDO %
18) Shooting Ratio
19) Save Ratio

### Feature Selection
Due to the large number of features available feature selection was performed using SelectBestPercentile from the sklearn library. This function selects the features that rank in the given percentile based on a given scoring function. For this dataset, the function selected features that ranked in the 5th percentile per the mutual information scoring function.

### Extremely Randomized Trees (ExtraTreesClassifier)
An extremely randomized trees model was imported from sklearn and was selected due to the large number of features in the dataset and the power of the model compared to more traditional approaches such as logistic regression. While random forest would have also been a suitable choice extremely randomized trees were chosen due to the computational speed advantage over random forest.

### Hyperparameter Tuning
Hyperparameters were chosen using 250 iterations of a randomized search with cross-validation (RandomizedSearchCV). The parameter grid used can be seen in the ModelCreation.py file. The objective of the search was to minimize the log loss of the model.

## Performance
### Overall Performance

Due to the large number of features, selecting a given percentile can result in different features being chosen between runs. Therefore, the results below are averages seen over 10 separate runs.

#### 10-Fold Cross-Validation (2010-2020)
The table below shows the model performance over 10-fold stratified cross-validation for the seasons of 2010-2020.

|   Metric   | Score  |
| ---------- | ------ |
|  Log Loss  | 0.6660 |
|  Accuracy  | 0.5907 |
|    AUC     | 0.5689 |
|  F1-Score  | 0.6751 |

#### Test Season (2021)
The table below shows the model performance for the left-out testing set which was all regular season games from the 2021 NHL season.

|   Metric   | Score  |
| ---------- | ------ |
|  Log Loss  | 0.6526 |
|  Accuracy  | 0.6320 |
|    AUC     | 0.6224 |
|  F1-Score  | 0.6871 |
