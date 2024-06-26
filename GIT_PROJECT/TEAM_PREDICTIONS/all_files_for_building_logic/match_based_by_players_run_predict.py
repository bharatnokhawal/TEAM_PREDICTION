import pandas as pd

# Load data into DataFrames
df = pd.read_csv('transformed_match_data.csv')
cricket_data = pd.read_csv('IPl Ball-by-Ball 2008-2023.csv')

# Define functions to calculate performance against a specific team and player
def performance_against_team(player_name, team_name, df):
    player_team_data = df[(df['player'] == player_name) & (df['against_team'] == team_name)]
    matches_played = player_team_data['match_id'].nunique()

    total_runs = player_team_data['run_scored'].sum()
    total_wickets = player_team_data['wicket'].sum()
    total_4s = player_team_data['4s'].sum()
    total_6s = player_team_data['6s'].sum()
    total_50s = player_team_data['50s'].sum()
    total_100s = player_team_data['100s'].sum()
    
    return {
        'matches_played': matches_played,
        'total_runs': total_runs,
        'total_wickets': total_wickets,
        'total_4s': total_4s,
        'total_6s': total_6s,
        'total_50s': total_50s,
        'total_100s': total_100s
    }

def performance_against_player(batsman, bowler, cricket_data):
    filtered_data = cricket_data[(cricket_data['batsman'] == batsman) & (cricket_data['bowler'] == bowler)]
    total_runs = filtered_data['batsman_runs'].sum()
    total_wickets = filtered_data[filtered_data['is_wicket'] == 1].shape[0]
    
    return {
        'total_runs': total_runs,
        'total_wickets': total_wickets
    }

def calculate_fantasy_points(player_performance, Batsman_points, Bowling_points, Fielding_points):
    fantasy_points = (
        player_performance['total_runs'] * Batsman_points['Run'] +
        player_performance['total_4s'] * Batsman_points['bFour'] +
        player_performance['total_6s'] * Batsman_points['bSix'] +
        player_performance['total_50s'] * Batsman_points['Half_century'] +
        player_performance['total_100s'] * Batsman_points['Century'] +
        player_performance['total_wickets'] * Bowling_points['Wicket']
    )
    
    # Assuming some dummy values for fielding points
    total_catches = player_performance.get('catches', 0)
    total_stumpings = player_performance.get('stumpings', 0)
    total_runouts = player_performance.get('runouts', 0)

    fantasy_points += (
        total_catches * Fielding_points['Catch'] +
        total_stumpings * Fielding_points['Stumping'] +
        total_runouts * Fielding_points['RunOutD']  # Assuming direct runouts
    )
    
    return fantasy_points

# Define points system
Batsman_points = {
    'Run': 1, 'bFour': 1, 'bSix': 2, '30Runs': 4,
    'Half_century': 8, 'Century': 16, 'Duck': -2, '170sr': 6,
    '150sr': 4, '130sr': 2, '70sr': -2, '60sr': -4, '50sr': -6
}

Bowling_points = {
    'Wicket': 25, 'LBW_Bowled': 8, '3W': 4, '4W': 8,
    '5W': 16, 'Maiden': 12, '5rpo': 6, '6rpo': 4, '7rpo': 2, '10rpo': -2,
    '11rpo': -4, '12rpo': -6
}

Fielding_points = {
    'Catch': 8, '3Cath': 4, 'Stumping': 12, 'RunOutD': 12,
    'RunOutInd': 6
}

# Aggregate performance metrics for each player in one team against the other team
def aggregate_performance_metrics(team, opponent_team, team_name, opponent_team_name, df, cricket_data):
    player_performances = []

    for player in team:
        team_performance = performance_against_team(player, opponent_team_name, df)
        
        # Performance against each player in the opponent team
        total_opponent_performance = {'total_runs': 0, 'total_wickets': 0}
        for opponent in opponent_team:
            player_vs_opponent = performance_against_player(player, opponent, cricket_data)
            total_opponent_performance['total_runs'] += player_vs_opponent['total_runs']
            total_opponent_performance['total_wickets'] += player_vs_opponent['total_wickets']

        # Aggregate performance
        aggregated_performance = {
            'total_runs': team_performance['total_runs'] + total_opponent_performance['total_runs'],
            'total_wickets': team_performance['total_wickets'] + total_opponent_performance['total_wickets'],
            'total_4s': team_performance['total_4s'],
            'total_6s': team_performance['total_6s'],
            'total_50s': team_performance['total_50s'],
            'total_100s': team_performance['total_100s']
        }
        
        fantasy_points = calculate_fantasy_points(aggregated_performance, Batsman_points, Bowling_points, Fielding_points)
        player_performances.append((fantasy_points, player))
        
    return player_performances

# Define the teams and their names
csk = ['MS Dhoni', 'Shaik Rasheed', 'Shivam Dube', 'RD Gaikwad', 'DL Chahar', 'RA Jadeja', 'AM Rahane', 'M Theekshana', 'TU Deshpande', 'Simarjeet Singh', 'MM Ali']
csk_name = 'Chennai Super Kings'
gt = ['Rashid Khan', 'Shubman Gill', 'Mohammed Shami', 'WP Saha', 'DA Miller', 'V Shankar', 'MS Wade', 'J Yadav', 'KS Williamson', 'R Sai Kishore', 'MM Sharma']
gt_name = 'Gujarat Titans'

# Aggregate performance metrics for CSK players against GT players
csk_performances = aggregate_performance_metrics(csk, gt, csk_name, gt_name, df, cricket_data)

# Aggregate performance metrics for GT players against CSK players
gt_performances = aggregate_performance_metrics(gt, csk, gt_name, csk_name, df, cricket_data)

# Combine and sort performances
combined_performances = csk_performances + gt_performances
combined_performances.sort(reverse=True, key=lambda x: x[0])

# Get the top 11 players
top_11_players = combined_performances[:11]

# Print top 11 players based on fantasy points
print("Top 11 players based on fantasy points:")
for points, player in top_11_players:
    print(f"Player name :- {player}..... Fantasy Points: {points:.2f}")
