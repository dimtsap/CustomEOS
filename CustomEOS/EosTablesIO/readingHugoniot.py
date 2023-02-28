import pandas as pd
import matplotlib.pyplot as plt
import os
plt.style.use('ggplot')


def read_hugoniot(filename):
    """Read a hugoniot table formatted by the Hyades hugoniot function

    Args:
        filename (string): filename of hugoniot to be read

    Returns:
        df (Pandas.DataFrame): Pandas DataFrame with each column as a variable in the hugoniot
    """
    
    with open(filename) as f:
        lines = f.readlines()
    variables = lines[3].split()  # the fourth line of the hugoniot table is the variable headers
    # The variable headers should be Rho, Pres, Enrgy, Temp, Up, Us
    df = pd.read_csv(filename, names=variables, skiprows=4, sep='  ', engine='python')

    # density is already in g/cc
    df['Up'] *= 1e-5  # convert cm/s to km/s = um/ns
    df['Us'] *= 1e-5  # convert cm/s to km/s = um/ns
    df['Pres'] *= 1e-10  # convert dynes/cm^2 to GPa
    df['Temp'] *= (11605 * 1000)  # convert KeV to Kelvin
    df['Enrgy'] *= 1e-7  # converts erg to Joules, NOT SURE ENRGY IS IN ERGS

    return df


def plot_hugoniot(filename, mode='all'):
    """Neatly plot some of the most important variables on the Hugoniot

    Args:
        filename (string): name of the hugoniot file output from the Hyades Hugoniot function 
        mode (string, optional): Which variables to plot. Options are 1, 2, 3, or all. Defaults to all. 
        
    Returns:
        fig (matplotlib figure), ax (matplotlib axis): figure and axis of the plot
    """
    df = read_hugoniot(filename)
    if (mode == 'all') or (mode == ''):
        fig, ax = plt.subplots(1, 3, figsize=(12, 4))
        fig.suptitle(f'Hugoniot Visualization of {os.path.split(filename)[1]}')

        df.plot('Up', 'Us', color='red', ax=ax[0], legend=False)
        ax[0].set(xlabel='Particle Velocity (km/s)', ylabel='Shock Velocity (km/s)', aspect='equal')
        ax[0].set_title('Up v. Us', color='red', fontsize='medium', fontweight='bold')

        df.plot('Pres', 'Temp', color='blue', ax=ax[1], legend=False)
        ax[1].set(xlabel='Pressure (GPa)', ylabel='Temperature (K)')
        ax[1].set_title('Pres v. Temp', color='blue', fontsize='medium', fontweight='bold')

        df.plot('Rho', 'Pres', color='green', ax=ax[2], legend=False)
        ax[2].set(xlabel='Density (g/cc)', ylabel='Pressure (GPa)')
        ax[2].set_title('Rho v. Pres', color='green', fontsize='medium', fontweight='bold')

        for axis in ax:
            # Conditionally format tick labels to use scientific notation if they're > 1000
            # just a cosmetic fix to save space on the triple plot
            axis.ticklabel_format(axis='both', style='scientific', scilimits=(0, 3))

    elif mode in ('1', '2', '3'):
        fig, ax = plt.subplots(figsize=(6, 4))
        if mode == '1':
            x = 'Up'
            y = 'Us'
            x_label = 'Particle Velocity (km/s)'
            y_label = 'Shock Velocity (km/s)'
        if mode == '2':
            x = 'Pres'
            y = 'Temp'
            x_label = 'Pressure (GPa)'
            y_label = 'Temperature (K)'
        if mode == '3':
            x = 'Rho'
            y = 'Pres'
            x_label = 'Density (g/cc)'
            y_label = 'Pressure (GPa)'
        df.plot(x, y, xlabel=x_label, ylabel=y_label, legend=False, ax=ax)
        ax.set_title(f'Hugoniot of {os.path.split(filename)[1]}')
        ax.ticklabel_format(axis='both', style='scientific', scilimits=(0, 3))
    else:
        raise Exception(f'{mode!r} is not a valid selection.\n'
                        f'Options are Up/Us [1], Pres/Temp [2], Rho/Pres [3], or all [all]')

    return fig, ax


if __name__ == '__main__':
    filename = 'data/hugoniot/hugoniot_Fe_182.dat'
    mode = 'all'
    # filename = input('Enter Hugoniot Filename: ')
    # mode = input('Select variables to plot - Up/Us [1], Pres/Temp [2], Rho/Pres [3], or all [all]: ')
    fig, ax = plot_hugoniot(filename, mode=mode)
    plt.show()

