import pandas as pd

def combine(lst,cross):
    """Add a set of dataframes together in a list.

    Parameters:
        lst(List) - a list of integers that represent number of games used to assess quality in the retrieved files.
        cross(Bool) - should cross or nocross files be retrieved.

    Returns:
        dfs(List) - a list of dataframes to be joined together.
    """
    #where dataframes will be stored
    dfs = []

    #determine how the file name ends
    if cross:
        end = 'Cross'
    else:
        end = 'NoCross'

    #iterate through files and add the to the list of dataframes
    for i in lst:
        df = pd.read_csv("DataFrames/" + str(i) + end + ".csv")
        keep_same = {'Game_Id', 'RegOrOT','season','Away_Team','Home_Team','Outcome','isPlayoff'}
        df.columns = ['{}{}'.format(c, '' if c in keep_same else ' ' + str(i)) for c in df.columns]
        dfs.append(df)
    
    return dfs

#where all frames will be stored, and the game intervals used in the datasets
dfs = []
lst = [5,10,20,40,82]

#combine nocross and cross dataframes
noCross = combine(lst,False)
cross =  combine(lst,True)

#put all dataframes in one list
dfs.extend(noCross)
dfs.extend(cross)

#set index and join all frames into one based off index
dfs = [df.set_index(['Game_Id','RegOrOT','season','Away_Team','Home_Team','Outcome','isPlayoff']) for df in dfs]
combined = pd.concat(dfs, axis=1)
print(combined.columns)
combined.to_csv("DataFrames/CombinedFrame.csv",index=True)
