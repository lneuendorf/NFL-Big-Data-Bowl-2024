from tqdm import tqdm
import numpy as np
import pandas as pd

# Enable tqdm for pandas apply
tqdm.pandas()

def num_offensive_players_between_tackler_and_ballCarrier(row, tracking_df):
    same_frame = tracking_df[(tracking_df['gameId'] == row['gameId']) &
                             (tracking_df['playId'] == row['playId']) &
                             (tracking_df['frameId'] == row['frameId'])]

    ballCarrier_club = same_frame[same_frame['nflId'] == row['ballCarrierId']]['club'].iloc[0]
    x_tackler, y_tackler, x_ballCarrier, y_ballCarrier = row['x_tackler'], row['y_tackler'], \
                                                         row['x_ballCarrier'], row['y_ballCarrier']

    # Bounding box with extra 2 yards in y direction
    xmin, xmax = min(x_tackler, x_ballCarrier), max(x_tackler, x_ballCarrier)
    ymin, ymax = min(y_tackler, y_ballCarrier) - 2, max(y_tackler, y_ballCarrier) + 2


    # Filter offensive players, excluding the ballCarrier
    offensive = same_frame[(same_frame['club'] == ballCarrier_club) & (same_frame['nflId'] != row['ballCarrierId'])]

    # Filter to offensive players inside bounding box created by tackler, ballcarrier coordinates
    num_players = offensive[(offensive['x'] >= xmin) & (offensive['x'] <= xmax) & 
                            (offensive['y'] <= ymax) & (offensive['y'] >= ymin)].shape[0]

    return num_players

def main():
    # Load data
    x = pd.read_pickle('./data/x.pkl')
    df_tracking_new = pd.read_pickle('./data/tracking_new.pkl')

    # Apply the function and add new columns
    results = x.progress_apply(lambda row: num_offensive_players_between_tackler_and_ballCarrier(
        row, df_tracking_new), axis=1)
    x['num_off_player_between'] = results.tolist()

    # Save the updated dataframe
    x.to_pickle('./x_updated_num_o_players.pkl')

if __name__ == "__main__":
    main()
