from tqdm import tqdm
import numpy as np
import pandas as pd

# Enable tqdm for pandas apply
tqdm.pandas()

def find_closest_players_and_ballcarrier_indicator(row, tracking_df):
    # Filter tracking_df for the same game, play, frame
    same_frame = tracking_df[(tracking_df['gameId'] == row['gameId']) &
                             (tracking_df['playId'] == row['playId']) &
                             (tracking_df['frameId'] == row['frameId'])]

    # Find the club of the tackler
    tackler_club = same_frame[same_frame['nflId'] == row['tacklerId']]['club'].iloc[0]

    # Filter for defenders and offensive players, excluding the tackler
    defenders = same_frame[(same_frame['club'] == tackler_club) & (same_frame['nflId'] != row['tacklerId'])]
    offensive = same_frame[(same_frame['club'] != tackler_club)]

    # Calculate distances for defenders and offensive players
    defender_distances = np.sqrt((defenders['x'] - row['x_tackler'])**2 + (defenders['y'] - row['y_tackler'])**2)
    offensive_distances = np.sqrt((offensive['x'] - row['x_tackler'])**2 + (offensive['y'] - row['y_tackler'])**2)

    # Get the three smallest distances for both groups and corresponding nflIds
    closest_defenders = defender_distances.nsmallest(3)
    closest_offensive = offensive_distances.nsmallest(3)

    # Get nflIds of closest players
    closest_defender_ids = defenders.loc[closest_defenders.index]['nflId'].tolist()
    closest_offensive_ids = offensive.loc[closest_offensive.index]['nflId'].tolist()

    # Check if ballCarrier is among the three closest offensive players
    ballcarrier_indicator = 1 if row['ballCarrierId'] in closest_offensive_ids else 0

    # Return the distances and the indicator
    return closest_defenders.tolist() + closest_offensive.tolist() + [ballcarrier_indicator]

def main():
    # Load data
    x = pd.read_pickle('./data/x.pkl')
    df_tracking_new = pd.read_pickle('./data/tracking_new.pkl')

    # Apply the function and add new columns
    results = x.progress_apply(lambda row: find_closest_players_and_ballcarrier_indicator(row, df_tracking_new), axis=1)
    x[['closest_defender_1', 'closest_defender_2', 'closest_defender_3', 
       'closest_offensive_1', 'closest_offensive_2', 'closest_offensive_3', 
       'ballcarrier_closest_indicator']] = pd.DataFrame(results.tolist(), index=x.index)

    # Save the updated dataframe
    x.to_pickle('./x_updated.pkl')

if __name__ == "__main__":
    main()
