import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation
from matplotlib import rc
import pandas as pd
from functools import partial

WEEK_START = 1
WEEK_END = 9

class NflPlayAnimator():
    def __init__(self):
        self.gameId_dict = {} # dict with gameId as key and week as value for caching

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
        df = df.query('gameId==@gameId & playId==@playId')
            
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
    
        # plot a line plot for marking the field lines with black color
        plt.plot([10, 10, 20, 20, 30, 30, 40, 40, 50, 50, 60, 60, 70, 70, 80,
                  80, 90, 90, 100, 100, 110, 110, 120, 0, 0, 120, 120],
                 [0, 53.3, 53.3, 0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 
                  0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 53.3, 0, 0, 53.3],
                 color='black', zorder = 0)
    
        # create the end-zones with a lighter shade of blue
        left_end_zone = patches.Rectangle((0, 0), 10, 53.3, facecolor='lightblue', alpha=0.2, zorder=0)
        right_end_zone = patches.Rectangle((110, 0), 120, 53.3, facecolor='lightblue', alpha=0.2, zorder=0)
    
        # add the patches to the subplot
        ax.add_patch(left_end_zone)
        ax.add_patch(right_end_zone)
    
        # set the limits of x-axis and y-axis
        plt.xlim(0, 120)
        plt.ylim(-5, 58.3)
    
        # remove the axis values from the plot
        plt.axis('off')
    
        # plot the numbers (yard lines) with black color
        for x in range(20, 110, 10):
            number = x
            if x > 50:
                number = 120 - x
    
            plt.text(x, 5, str(number - 10),
                     horizontalalignment='center',
                     fontsize=20,
                     color='black')
    
            plt.text(x - 0.6, 53.3 - 5, str(number - 10),
                     horizontalalignment='center',
                     fontsize=20,
                     color='black',
                     rotation=180)
    
        # make ground markings with black color
        for x in range(11, 110):
            ax.plot([x, x], [0.4, 0.7], color='black', zorder = 0)
            ax.plot([x, x], [53.0, 52.5], color='black', zorder = 0)
            ax.plot([x, x], [22.91, 23.57], color='black', zorder = 0)
            ax.plot([x, x], [29.73, 30.39], color='black', zorder = 0)
        
        return fig, ax

    def _plot_players(self, df, dots_t1, dots_t2, ball, t1, t2, frame):
        # Update dots for team 1
        df_qry = df.query("frameId==@frame & club==@t1")
        x_coords = df_qry.x.tolist()
        y_coords = df_qry.y.tolist()
        dots_t1.set_data(x_coords, y_coords)

        # Update dots for team 2
        df_qry = df.query("frameId==@frame & club==@t2")
        x_coords = df_qry.x.tolist()
        y_coords = df_qry.y.tolist()
        dots_t2.set_data(x_coords, y_coords)
        
        # Update dots for the football
        df_qry = df.query("frameId==@frame & club=='football'")
        x_coords = df_qry.x.tolist()
        y_coords = df_qry.y.tolist()
        ball.set_data(x_coords, y_coords)
        return dots_t1, dots_t2, ball
    
    def animate_play(self, gameId, playId, interval=100):
        plt.ioff()
        fig, ax = self._create_football_field()

        df = self.load_play_data(gameId, playId)

        n_frames = len(df.frameId.unique())
        teams = [team for team in df.club.unique() if team != 'football']
        t1, t2 = teams[0], teams[1]
        
        dots_t1, = plt.plot([], [], 'bo')
        dots_t2, = plt.plot([], [], 'ro')
        ball, = plt.plot([], [], c='brown', marker='D')

        rc('animation', html='html5')
        anim = FuncAnimation(
            fig, 
            func=partial(
                self._plot_players, 
                df, 
                dots_t1, 
                dots_t2, 
                ball,
                t1, t2), 
            frames=n_frames, 
            interval=interval, 
            blit=True)

        plt.ion()

        return anim