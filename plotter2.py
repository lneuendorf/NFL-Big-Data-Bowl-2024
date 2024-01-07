import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation
from matplotlib import rc
import pandas as pd
from functools import partial
import textwrap


WEEK_START = 1
WEEK_END = 9

class NflPlayAnimator():
    def __init__(self):
        self.gameId_dict = {} # dict with gameId as key and week as value for caching
        self.df_pred = pd.read_pickle('data/predictions.pkl')

    def _get_play_description_dict(self, gameId, playId):
        df_plays = pd.read_csv('data/plays.csv')
        cols = ['gameId','playId','ballCarrierId','possessionTeam','preSnapHomeScore','preSnapVisitorScore','ballCarrierDisplayName','playDescription',
                'quarter','down','yardsToGo','possessionTeam','yardlineNumber','absoluteYardlineNumber',
                'defensiveTeam']
        play_info_row = df_plays.query("gameId==@gameId & playId==@playId")
        play_info_dict = {key: next(iter(value.values())) for key, value in play_info_row.to_dict().items()}
        return play_info_dict

    def _populate_gameId_dict(self):
        for week in range(WEEK_START, WEEK_END+1):
            df_gids = pd.read_csv(f'data/tracking_week_{week}.csv', usecols=[0])
            
            if 'gameId' not in df_gids.columns:
                raise Exception("First column of tracking data csv is expected to be 'gameId'")
                
            gameIds = df_gids.gameId.unique()
            for gid in gameIds:
                self.gameId_dict[gid] = week
    
    def load_play_data(self, gameId, playId):
        if len(self.gameId_dict) == 0:
            self._populate_gameId_dict()

        df = pd.read_csv(f'data/tracking_week_{self.gameId_dict[gameId]}.csv')
        df = df.query('gameId==@gameId & playId==@playId').reset_index(drop=True)
            
        return df
        
    def _create_football_field(self):
        """
        Code from: https://www.kaggle.com/code/robikscube/nfl-big-data-bowl-plotting-player-position
        """
        
        # creat a rectangle representing the field with white color
        rect = patches.Rectangle((0, 0), 120, 53.3, facecolor='white', zorder=0)
    
        # creat a subplot to plot our field on
        fig, ax = plt.subplots(1, figsize=(12, 6.33))
    
        # add the rectangle to the plot
        ax.add_patch(rect)
    
        # plot a line plot for marking the field lines with grey color
        plt.plot([10, 10, 20, 20, 30, 30, 40, 40, 50, 50, 60, 60, 70, 70, 80,
                  80, 90, 90, 100, 100, 110, 110, 120, 0, 0, 120, 120],
                 [0, 53.3, 53.3, 0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 
                  0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 53.3, 0, 0, 53.3],
                 color='lightgrey', zorder = 0)
    
        # create the end-zones in white
        left_end_zone = patches.Rectangle((0, 0), 10, 53.3, facecolor='snow', alpha=0.2, zorder=0)
        right_end_zone = patches.Rectangle((110, 0), 120, 53.3, facecolor='snow', alpha=0.2, zorder=0)
    
        # add the patches to the subplot
        ax.add_patch(left_end_zone)
        ax.add_patch(right_end_zone)
    
        # set the limits of x-axis and y-axis
        plt.xlim(0, 120)
        plt.ylim(-5, 58.3)
    
        # remove the axis values from the plot
        plt.axis('off')
    
        # plot the numbers (yard lines) with grey color
        for x in range(20, 110, 10):
            number = x
            if x > 50:
                number = 120 - x
    
            plt.text(x, 5, str(number - 10),
                     horizontalalignment='center',
                     fontsize=20,
                     color='lightgrey',
                     zorder=0)
    
            plt.text(x - 0.6, 53.3 - 5, str(number - 10),
                     horizontalalignment='center',
                     fontsize=20,
                     color='lightgrey',
                     rotation=180,
                     zorder=0)
    
        # make ground markings with grey color
        for x in range(11, 110):
            ax.plot([x, x], [0.4, 0.7], color='lightgrey', zorder = 0)
            ax.plot([x, x], [53.0, 52.5], color='lightgrey', zorder = 0)
            ax.plot([x, x], [22.91, 23.57], color='lightgrey', zorder = 0)
            ax.plot([x, x], [29.73, 30.39], color='lightgrey', zorder = 0)
        
        return fig, ax

    
    def _plot_players(self, df, los, playDir, tacklerId, ballCarrierID, gameId, playId, dots_t1, dots_t2, ball,
                      dots_tackler, dots_ballCarrier, t1, t2, pred_tackle_line, frame):

        updated_artists = []

        ids = [tacklerId,ballCarrierID]

        df_qry = self.df_pred.query('gameId==@gameId & playId==@playId & frameId==@frame & tacklerId==@tacklerId')
        if df_qry.shape[0] > 0:
            pred_playResult = df_qry.pred_playResult.values[0]
            if playDir == "left":
                tackle_line = los - pred_playResult
            else:
                tackle_line = los + pred_playResult
            pred_tackle_line.set_data([tackle_line, tackle_line],[0, 53.3])
            updated_artists.append(pred_tackle_line)
        
        # Update dots for team 1
        df_qry = df.query("frameId==@frame & club==@t1 & nflId not in @ids")
        x_coords = df_qry.x.tolist()
        y_coords = df_qry.y.tolist()
        dots_t1.set_data(x_coords, y_coords)
        updated_artists.append(dots_t1)

        # Update dots for team 2
        df_qry = df.query("frameId==@frame & club==@t2 & nflId not in @ids")
        x_coords = df_qry.x.tolist()
        y_coords = df_qry.y.tolist()
        dots_t2.set_data(x_coords, y_coords)
        updated_artists.append(dots_t2)
        # Update dots for the football
        df_qry = df.query("frameId==@frame & club=='football'")
        x_coords = df_qry.x.tolist()
        y_coords = df_qry.y.tolist()
        ball.set_data(x_coords, y_coords)
        updated_artists.append(ball)

        df_qry = df.query("frameId==@frame & nflId==@tacklerId")
        if df_qry.shape[0] > 0:
            x_coords = df_qry.x.tolist()
            y_coords = df_qry.y.tolist()
            dots_tackler.set_data(x_coords, y_coords)
            updated_artists.append(dots_tackler)

        df_qry = df.query("frameId==@frame & nflId==@ballCarrierID")
        if df_qry.shape[0] > 0:
            x_coords = df_qry.x.tolist()
            y_coords = df_qry.y.tolist()
            dots_ballCarrier.set_data(x_coords, y_coords)
            updated_artists.append(dots_ballCarrier)
        
        return updated_artists
    
    def animate_play(self, gameId, playId, tacklerId, interval=100):
        plt.ioff()
        fig, ax = self._create_football_field()

        df = self.load_play_data(gameId, playId)

        n_frames = len(df.frameId.unique())
        teams = [team for team in df.club.unique() if team != 'football']
        t1, t2 = teams[0], teams[1]

        # Fetch and plot the play description
        df_game = pd.read_csv('data/games.csv').query('gameId==@gameId')
        play_info = self._get_play_description_dict(gameId, playId)
        play_description = f"2022 Week {df_game.week.values[0]}: {df_game.homeTeamAbbr.values[0]} " + \
                           f"{play_info['preSnapHomeScore']} - " + \
                           f"{df_game.visitorTeamAbbr.values[0]} {play_info['preSnapVisitorScore']}\n"
        plt.text(0.5, 1.05, play_description, ha='center', va='center', transform=ax.transAxes, fontsize=20)

        num_suffix = {1:"st",2:"nd",3:"rd",4:"th"}
        play_description = f"({play_info['down']}{num_suffix[play_info['down']]} & {play_info['yardsToGo']})" + \
                           f"(Q{play_info['quarter']}) {play_info['playDescription']}"
        play_description = textwrap.fill(play_description, width=70)
        plt.text(0.5, 1.0, play_description, ha='center', va='center', transform=ax.transAxes, fontsize=12)

        # Make sure t1 is the offensive team
        if t1 != play_info['possessionTeam']:
            t_tmp = t1
            t1 = t2
            t2 = t_tmp

        # Plot line of scrimmage
        playDir = df.playDirection[0]
        yardsToGo = play_info['yardsToGo']
        los = 0
        if yardsToGo > 10:
            if playDir == "left":
                los = play_info['absoluteYardlineNumber'] + (yardsToGo - 10)
            else:
                los = play_info['absoluteYardlineNumber'] - (yardsToGo - 10)
        else:
            los = play_info['absoluteYardlineNumber']
        plt.plot([los, los],[0, 53.3], color='#3253e6', zorder = 1, alpha=0.8, label='Line of Scrimmage')
        
        # Plot first down yardage line
        firstDownNumber = 0
        if df.playDirection[0] == "left":
            firstDownNumber = play_info['absoluteYardlineNumber'] - play_info['yardsToGo']
        else:
            firstDownNumber = play_info['absoluteYardlineNumber'] + play_info['yardsToGo']
            
        plt.plot([firstDownNumber, firstDownNumber],[0, 53.3],
                 color='#FDDA0D', zorder = 1, alpha=0.8, label='First Down Line')

        # Predicted tackle yardline
        pred_tackle_line, = plt.plot([], [], color='green', zorder = 1, label='Predicted Tackle Line')
        
        # plot actual tackle line
        playResult = self.df_pred.query('gameId==@gameId & playId==@playId & tacklerId==@tacklerId').playResult.values[0]
        if playDir == "left":
            tackle_line = los - playResult
        else:
            tackle_line = los + playResult
        plt.plot([tackle_line, tackle_line],[0, 53.3], color='purple', zorder = 1, label='Actual Tackle Line')

        dots_t1, = plt.plot([], [], marker='o', mec='#EE4F4F',mfc='#E88A8A', linestyle='None', alpha=1, markersize=6,zorder=3)
        dots_ballCarrier, = plt.plot([], [], marker='o',mec='black', mfc='#ff0000', linestyle='None', markersize=6,zorder=4)
        
        dots_t2, = plt.plot([], [], marker='o', mec='#525252',mfc='#898989', linestyle='None', alpha=1, markersize=6,zorder=3)
        dots_tackler, = plt.plot([], [], marker='o',mec='black', mfc='black', linestyle='None', markersize=6,zorder=4)
        
        ball, = plt.plot([], [], marker='D', linestyle='None',mec='black', mfc='brown', markersize=4,zorder=5)

        plt.legend(loc='upper right',bbox_to_anchor=(1.10, 1.165))
        
        ballCarrierId = play_info['ballCarrierId']
        
        rc('animation', html='html5')
        anim = FuncAnimation(
            fig, 
            func=partial(
                self._plot_players, 
                df, 
                los,
                playDir,
                tacklerId,
                ballCarrierId,
                gameId, 
                playId,
                dots_t1, 
                dots_t2, 
                ball,
                dots_tackler,
                dots_ballCarrier,
                t1, t2,
                pred_tackle_line), 
            frames=n_frames, 
            interval=interval, 
            blit=True)

        plt.ion()
        return anim