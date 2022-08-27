import pandas as pd

# The data used in this project comes from https://www.kaggle.com/datasets/martinellis/nhl-game-data

#first read player info. this has the player id number
player_info = pd.read_csv("player_info.csv")
#create a column with full name for easier lookup
player_info['name'] = (player_info['firstName'])+" "+(player_info['lastName'])
# read games table into pandas
games = pd.read_csv("kaggle_play_data/game.csv")
# read plays table into pandas
plays = pd.read_csv("kaggle_play_data/game_plays.csv")
# read player specific plays info into pandas
game_plays_players = pd.read_csv("kaggle_play_data/game_plays_players.csv")
#all games of the 2019-2020 season
games_2020 = games[games['season']==20192020].drop_duplicates()
#isolate regular season games
regular_season_2020 = games_2020[games_2020['type']=='R']
#isolate game ids
game_ids = regular_season_2020['game_id'].tolist()
#store list of player ids for every goalie that played in 2019-2020
goalie_ids = player_info[player_info['primaryPosition']=="G"]['player_id'].drop_duplicates().tolist()
#store counts in dictionary of dictionaries 
goalie_stats = {}
#fill dictionary with template dictionaries for shots by position and hand
for g in goalie_ids:
    goalie_stats[g]= {'shots_by_position':{'LW':{'L':0,'R':0},'C':{'L':0,'R':0},'RW':{'L':0,'R':0},'D':{'L':0,'R':0}},'goals_by_position':{'LW':{'L':0,'R':0},'C':{'L':0,'R':0},'RW':{'L':0,'R':0},'D':{'L':0,'R':0}}}
                        
# keep track of which shot and goal events have missing data                     
shots_missing_data = []
goals_missing_data = [] 

# function will take a play_id. Will be applied to a series of play_ids
def tally_shots(play_id):
    play = game_plays_players[game_plays_players['play_id']==play_id]
    #get id of shooter
    shooter = play[play['playerType']=='Shooter'].drop_duplicates()

    if shooter.empty:
        shots_missing_data.append(play_id)
        return

    shooter_id = shooter['player_id'].iloc[0]
    #look up shooter_id in player_info and get hand and primary position
    shooter_bio = player_info[player_info['player_id']==shooter_id].drop_duplicates()
    shooter_hand = shooter_bio['shootsCatches'].iloc[0]
    shooter_position = shooter_bio['primaryPosition'].iloc[0]
    goalie = play[play['playerType']=='Goalie'].drop_duplicates()

    if goalie.empty:
        shots_missing_data.append(play_id)
        return
    goalie_id = goalie['player_id'].iloc[0]
    try:
        goalie_stats[goalie_id]['shots_by_position'][shooter_position][shooter_hand]+=1
    except:
        shots_missing_data.append(play_id)
        return
    

def tally_goals(play_id):
    play = game_plays_players[game_plays_players['play_id']==play_id]
    #get id of scorer
    scorer = play[play['playerType']=='Scorer'].drop_duplicates()

    if scorer.empty:
        goals_missing_data.append(play_id)
        return
    
    scorer_id = scorer['player_id'].iloc[0]
    #look up scorer_id in player_info and get hand and primary position
    scorer_bio = player_info[player_info['player_id']==scorer_id].drop_duplicates()
    scorer_hand = scorer_bio['shootsCatches'].iloc[0]
    scorer_position = scorer_bio['primaryPosition'].iloc[0]
    goalie = play[play['playerType']=='Goalie'].drop_duplicates()

    if goalie.empty:
        goals_missing_data.append(play_id)
        return
    goalie_id = goalie['player_id'].iloc[0]
    try:
        goalie_stats[goalie_id]['goals_by_position'][scorer_position][scorer_hand]+=1
    except:
        goals_missing_data.append(play_id)
        return
    

def tally_game(game_id):
    #look up all plays in the game
    plays_in_game = plays[plays['game_id']==game_id].drop_duplicates()
    #isolate shots
    shots = plays_in_game[plays_in_game['event']=='Shot']
    shot_ids = shots['play_id']
    #isolate goals
    goals = plays_in_game[plays_in_game['event']=='Goal']
    goal_ids = goals['play_id']
    #tally shots
    shot_ids.apply(tally_shots)
    #tally goals
    goal_ids.apply(tally_goals)
    print(str(game_id)+' tallied')


for game in game_ids:
    tally_game(game)
    

def convert_to_list(goalie):
    #goalie is a dictionary from goalie_stats
    stats_list = []
    for key in goalie['shots_by_position']:
        stats_list.append(goalie['shots_by_position'][key]['L'])
        stats_list.append(goalie['shots_by_position'][key]['R'])
    for key in goalie['goals_by_position']:
        stats_list.append(goalie['goals_by_position'][key]['L'])
        stats_list.append(goalie['goals_by_position'][key]['R'])
    return stats_list


goalie_stats_listed = {}

for goalie in goalie_stats:
    goalie_stats_listed[goalie] = convert_to_list(goalie_stats[goalie])

df = pd.DataFrame.from_dict(goalie_stats_listed, orient='index',
                       columns=['SLWL','SLWR','SCL','SCR','SRWL','SRWR','SDL','SDR','GLWL','GLWR','GCL','GCR','GRWL','GRWR','GDL','GDR']
                           )


#get hand goalie catches with
ids = df.index.tolist()
goalie_catches = []

for i in ids:
    p = player_info[player_info['player_id']==int(i)]
    goalie_catches.append(p['shootsCatches'].iloc[0])
    
# append goalie catches hand to the dataframe
df['Goalie_Catches'] = goalie_catches
    

#calculate and add columns for saves,goals,total shots, and save percentage
df['Saved_Shots_Total'] = df.iloc[:,0:8].sum(axis=1)
df['Goals_Total'] = df.iloc[:,8:-1].sum(axis=1)
df['Shots_Total'] = df['Saved_Shots_Total'] + df['Goals_Total']
df['SV%'] = df['Saved_Shots_Total'] / (df['Goals_Total']+df['Saved_Shots_Total']) 

#calculate and add columns for sv% against all lefties and all righties
df['SV%_Left'] = (df['SLWL']+df['SCL']+df['SRWL']+df['SDL']) / (df['SLWL']+df['SCL']+df['SRWL']+df['SDL'] + df['GLWL']+df['GCL']+df['GRWL']+df['GDL'])  
df['SV%_Right'] = (df['SLWR']+df['SCR']+df['SRWR']+df['SDR']) / (df['SLWR']+df['SCR']+df['SRWR']+df['SDR'] + df['GLWR']+df['GCR']+df['GRWR']+df['GDR'])

#calculate and add columns for left wing
df['SV%_LeftWing_Total'] = (df['SLWL']+df['SLWR'])/(df['SLWL']+df['SLWR']+df['GLWL']+df['GLWR'])
df['SV%_LeftWing_Left'] = (df['SLWL'])/(df['SLWL']+df['GLWL'])
df['SV%_LeftWing_Right'] = (df['SLWR'])/(df['SLWR']+df['GLWR'])

#calculate and add columns for center
df['SV%_Center_Total'] = (df['SCL']+df['SCR'])/ (df['SCL']+df['SCR']+df['GCL']+df['GCR'])
df['SV%_Center_Left'] = (df['SCL'])/(df['SCL']+df['GCL'])
df['SV%_Center_Right'] = (df['SCR'])/(df['SCR']+df['GCR'])

#calculate and add columns for right wing
df['SV%_RightWing_Total'] = (df['SRWL']+df['SRWR'])/(df['SRWL']+df['SRWR']+df['GRWL']+df['GRWR'])
df['SV%_RightWing_Left'] = (df['SRWL']) / (df['SRWL']+df['GRWL'])
df['SV%_RightWing_Right'] = (df['SRWR']) / (df['SRWR']+df['GRWR'])

#calculate and add columns for defence
df['SV%_Defense_Total'] = (df['SDL']+df['SDR'])/(df['SDL']+df['SDR']+df['GDL']+df['GDR'])
df['SV%_Defense_Left'] = (df['SDL'])/(df['SDL']+df['GDL'])
df['SV%_Defense_Right'] = (df['SDR'])/(df['SDR']+df['GDR'])

#get ids from index and add as column
ids = df.index.tolist()
count = 0
for i in ids:
    ids[count] = int(i)
    count+=1
df['player_id'] = ids


def id_to_name(id):
    p = player_info[player_info['player_id']==id]
    name = p.iloc[0,12]
    return name

df['player_id'].tolist()
df['player_name'] = df['player_id'].apply(id_to_name)
df = df.dropna()

#save to csv for visualizing in Dash
df.to_csv('goalie_stats.csv')