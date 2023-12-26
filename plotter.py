import matplotlib.pyplot as plt
import matplotlib.patches as patches

def create_football_field(player_x=None, player_y=None):
    # Create a rectangle representing the field with white color
    rect = patches.Rectangle((0, 0), 120, 53.3, facecolor='white', zorder=0)

    # Creating a subplot to plot our field on
    fig, ax = plt.subplots(1, figsize=(12, 6.33))

    # Adding the rectangle to the plot
    ax.add_patch(rect)

    # Plotting a line plot for marking the field lines with black color
    plt.plot([10, 10, 20, 20, 30, 30, 40, 40, 50, 50, 60, 60, 70, 70, 80,
              80, 90, 90, 100, 100, 110, 110, 120, 0, 0, 120, 120],
             [0, 53.3, 53.3, 0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 
              0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 53.3, 0, 0, 53.3],
             color='black', zorder = 0)

    # Creating the end-zones with a lighter shade of blue
    left_end_zone = patches.Rectangle((0, 0), 10, 53.3, facecolor='lightblue', alpha=0.2, zorder=0)
    right_end_zone = patches.Rectangle((110, 0), 120, 53.3, facecolor='lightblue', alpha=0.2, zorder=0)

    # Adding the patches to the subplot
    ax.add_patch(left_end_zone)
    ax.add_patch(right_end_zone)

    # Setting the limits of x-axis and y-axis
    plt.xlim(0, 120)
    plt.ylim(-5, 58.3)

    # Removing the axis values from the plot
    plt.axis('off')

    # Plotting the numbers (yard lines) with black color
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

    # Making ground markings with black color
    for x in range(11, 110):
        ax.plot([x, x], [0.4, 0.7], color='black', zorder = 0)
        ax.plot([x, x], [53.0, 52.5], color='black', zorder = 0)
        ax.plot([x, x], [22.91, 23.57], color='black', zorder = 0)
        ax.plot([x, x], [29.73, 30.39], color='black', zorder = 0)

     # If player locations are provided, plot them on the field
    if player_x and player_y:
        ax.scatter(player_x, player_y, color='red', zorder=1)
    
    # Returning the figure and axis
    return fig, ax

