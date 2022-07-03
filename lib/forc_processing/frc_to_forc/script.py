# FORCPy  Wyn Williams 2021 based on original code of Miguel A. Valdez G. 2020

# Press ⌃R to execute
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

from argparse import ArgumentParser
import numpy as np
import scipy.linalg
from scipy.interpolate import interp2d
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.cm import RdBu_r
import pandas as pd
import re
import os
from os.path import isfile, join
from tkinter import Tk
from tkinter import filedialog

def get_file_list():

    all_files = []
    home = os.path.expanduser('~')
    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    dirbase = filedialog.askdirectory(initialdir=home)
    counter = 0
    for file in os.listdir(dirbase):
        if file.lower().endswith('.frc'):
            allname = join(dirbase, file)
            all_files.append(allname)
            counter += 1

    print('{} data files read'.format(counter))
    print(all_files)
    return all_files

def read_onecol_frc(filename):

    # Used to read a single column of Magnetization values in otherwise generic FORC format (assumed Bmin, Bmax, Bstep)
    df0 = pd.read_csv(filename, sep=',', header=None, names=['M'])
    df0['field']= np.nan
    #df0.drop(df0.tail(1).index, inplace=True)
    oldval=float(df0.iloc[-1,0])
    arraysize=0
    for idx in reversed(df0.index):
        newval=float(df0.loc[idx,'M'])
        diffval=newval-oldval
        if diffval>0:
            #print('Array size = {}'.format(arraysize))
            break
        oldval = newval
        arraysize += 1
    fieldlist = []
    # The assumed max min and step in mT
    vals=np.arange(2400, -2401, -30)
    for x in vals:
        y=x-1
        val1=np.arange(x,2401, 30)
        fieldlist.extend(val1)

    count=0
    for index, row in df0.iterrows():
        df0.at[count,'field']=fieldlist[count]
        count+=1

    #df0['field'] = df0['field'].apply(int)
    df0=df0[['field','M']]

    #print(df0)
    #print('length of list = {}'.format(len(fieldlist)))
    #print('length of frame = {}'.format(len(df0.index)))
    return df0


def read_frc(filename):
    # Reads a two-column generic FORC file of field and magnetisation pairs
    field=[]
    print('filename = {}'.format(filename))
    # grab the file into panda dataframe and chop of the last line (contains 'END')
    df0= pd.read_csv(filename, sep=',', header=None, names=['field', 'M'])
    df0.drop(df0.tail(1).index, inplace=True)

    #find the major loop dimension (.i.e.list of field values)
    oldval=float(df0.iloc[-1,0])
    arraysize=0
    for idx in reversed(df0.index):
        newval=float(df0.loc[idx,'field'])
        diffval=newval-oldval
        if diffval>0:
            #print('Array size = {}'.format(arraysize))
            break
        oldval=newval
        arraysize+=1
        field.append(float(df0.loc[idx,'field']))

    #print('Array size = {}'.format(arraysize))
    # create an numpy square array of teh correct size for data, and fill with zeros
    myFORC = np.zeros((arraysize, arraysize))

    # Iterate though dataframe and populate numpy array
    oldval=float(df0.iloc[0,0])
    row_number=-1
    col_number=arraysize
    for idx in (df0.index):
        #get list of 'M' values until new - old 'field' difference is negative
        newval=float(df0.loc[idx,'field'])
        M=float(df0.loc[idx,'M'])
        diffval=newval-oldval
        #print(diffval)
        if diffval<0.00001:
            col_number=(arraysize-row_number-2)
            row_number += 1
            myFORC[row_number,col_number]=M
            oldval = newval
        else:
            col_number += 1
            myFORC[row_number, col_number] = M
            oldval=newval

    #normalize array
    #abs_max = np.amax(np.abs(myFORC))
    #myFORC=myFORC/abs_max

    return myFORC, field

def append_new_line(file_name, text_to_append):
    """Append given text as a new line at the end of file"""
    # Open the file in append & read mode ('a+')
    with open(file_name, "a+") as file_object:
        # Move read cursor to the start of file.
        file_object.seek(0)
        # If file is not empty then append '\n'
        data = file_object.read(100)
        if len(data) > 0:
            file_object.write("\n")
        # Append text at the end of file
        file_object.write(text_to_append)

def write_frc(filename, df_final):
    # write the FORC data held in dataframe to <filename> in generic format (can be read by FORCinel)

    fo = open(filename, "w")
    #for index, row in df_final.head(10).iterrows():
    for index, row in df_final.iterrows():
        #print(row['field'],row['B.M'])
        #exit()
        if index==0:
            stringline= ('{hfield}'+','+'{mag:.5E}').format(hfield=row['field'],mag=row['M'])
            append_new_line(filename,stringline)
            #print(index, row[0], row[5])
        field_new=float(row[0])
        #print(type(field_new))
        if index>0:

            if field_new < field_old:
                stringline =""
                append_new_line(filename, stringline)

            stringline= ('{hfield}'+','+'{mag:.5E}').format(hfield=row['field'],mag=row['M'])
            append_new_line(filename,stringline)
        field_old = field_new
    stringline = ""
    append_new_line(filename, stringline)
    stringline = "END"
    append_new_line(filename, stringline)
    fo.close()


def get_array_size(filename):
    # a routine just to return the dimension of the FORC major loop
    linecount=0
    arraysize=0
    textfile = open(filename)
    lines = textfile.readlines()
    oldval=10.
    for line in reversed(lines):
        linecount+=1
        linetuple=tuple(line.split(','))
        x=linetuple[0]

        try:
            x = float(x)
        except:
            pass
        else:
            diffval=oldval-x
            if diffval <= 0.:
                textfile.close()
                return arraysize
            arraysize+=1
            oldval=x



def plot_curves(m, B, major, minor):
    def anti_diagonal(m):
        return np.fliplr(m).diagonal()

    fig, ax = plt.subplots()

    plt.plot(B, anti_diagonal(m)[::-1], color='tomato')

    for i in range(len(m)):
        plt.plot(B[len(m) - i:], m[i, len(m) - i:], color='k', lw=0.5)

    majorLocator = MultipleLocator(major)
    majorFormatter = FormatStrFormatter('%d')
    minorLocator = MultipleLocator(minor)
    ax.xaxis.set_major_locator(majorLocator)
    ax.xaxis.set_major_formatter(majorFormatter)
    ax.xaxis.set_minor_locator(minorLocator)
    plt.xticks(rotation=45)

    plt.ylim(-1., 1.)
    majorLocator = MultipleLocator(0.25)
    majorFormatter = FormatStrFormatter('%.2f')
    minorLocator = MultipleLocator(0.05)
    ax.yaxis.set_major_locator(majorLocator)
    ax.yaxis.set_major_formatter(majorFormatter)
    ax.yaxis.set_minor_locator(minorLocator)

    plt.xlabel(r'$B\,(\mathrm{mT})$', fontsize='xx-large')
    plt.ylabel(r'$m$  ', fontsize='xx-large', rotation='horizontal')


    plt.tight_layout()
    return fig, ax


def forc_distribution(m, Bb, Ba, sf):
    def in_grid(i, j, sf, n):
        grid = []
        for k in range(i - sf, i + sf + 1):
            for l in range(j - sf, j + sf + 1):
                if in_triangle(k, l, n) and in_square(k, l, n):
                    grid.append((k, l))
        return tuple(grid)

    def in_triangle(i, j, n):
        return j >= (n - 1) - i

    def in_square(i, j, n):
        return i <= n - 1 and j <= n - 1

    rho = np.zeros_like(m)
    for i in range(len(m)):
        for j in range(len(m) - i, len(m)):
            grid = in_grid(i, j, sf, len(m))
            data = []
            for indices in grid:
                data.append(
                    np.array([Bb[indices[0]][indices[1]], Ba[indices[0]][indices[1]], m[indices[0]][indices[1]]]))
            data = np.array(data)
            A = np.c_[np.ones(data.shape[0]), data[:, :2], np.prod(data[:, :2], axis=1), data[:, :2] ** 2]
            C, _, _, _ = scipy.linalg.lstsq(A, data[:, 2])
            rho[i][j] = -C[3] / 2.0

    return rho/np.max(rho)


def plot_forc_distribution(
        Bb, Ba, rho,
        xlim, ylim,
        major, minor,
        shiftedCMap,
        anotate,
        contour_start=0.1, contour_end=1.1, contour_step=0.3):

    # Normalizing the distribution
    rhomin = np.min(rho)

    for i in range(len(rho)):
        for j in range(len(rho[0])):
            if rho[i][j] < 0.:
                rho[i][j] /= -rhomin

    Bc, Bu = np.meshgrid(np.linspace(0., np.max(Bb), 2 * len(Bb)), np.linspace(np.max(Bb), np.min(Bb), 2 * len(Bb)))

    # Interpolator function
    I = interp2d(Bb[0], Ba[:, 0], rho, kind='cubic', fill_value=np.NaN)

    F = np.zeros_like(Bc)

    for i in range(len(Bc)):
        for j in range(len(Bc)):
            F[i, j] = I(Bu[i, j] + Bc[i, j], Bu[i, j] - Bc[i, j])

    # Plot
    fig, ax = plt.subplots()

    # Contour levels
    levels = np.arange(contour_start, contour_end, contour_step)
    levels = np.concatenate((-1.0 * levels[::-1], levels))

    figure = plt.contourf(Bc, Bu, F, levels=levels, cmap=shiftedCMap, extend=None)
    contours = plt.contour(Bc, Bu, F, levels=levels, colors='k', linewidths=0.2, extend='both')

    # Display parameters
    plt.plot([0., np.max(Bb)], [0., 0.], color='black', linewidth=0.5, linestyle='--')

    plt.xlabel(r'$B_c\, (\mathrm{mT})$', fontsize='xx-large')
    plt.ylabel(r'$B_u\, (\mathrm{mT})$', fontsize='xx-large', rotation='vertical')

    plt.xlim(xlim[0], xlim[1])
    plt.ylim(ylim[0], ylim[1])

    majorLocator = MultipleLocator(major)
    majorFormatter = FormatStrFormatter('%d')
    minorLocator = MultipleLocator(minor)
    ax.xaxis.set_major_locator(majorLocator)
    ax.xaxis.set_major_formatter(majorFormatter)
    ax.xaxis.set_minor_locator(minorLocator)
    plt.xticks(rotation=45)

    majorLocator = MultipleLocator(major)
    majorFormatter = FormatStrFormatter('%d')
    minorLocator = MultipleLocator(minor)
    ax.yaxis.set_major_locator(majorLocator)
    ax.yaxis.set_major_formatter(majorFormatter)
    ax.yaxis.set_minor_locator(minorLocator)

    # Add colorbar
    clb = plt.colorbar(figure)
    clb.add_lines(contours)
    clb.set_ticks(levels)

    labels = [r'-1.0 ($\times${:5.3f})'.format(round(abs(rhomin), 3))]
    labels += ['{:4.1f}'.format(l) for l in levels[1:]]
    clb.set_ticklabels(labels)
    clb.ax.set_title(r'$\rho$', y=1.01)

    ax.set_aspect('equal')
    x=.04
    y=.85
    for names in anotate:
        plt.figtext(x,y, names)
        y-=.03
    plt.tight_layout()
    return fig, ax


def shiftedColorMap(cmap, start=0, midpoint=0.5, stop=1.0, name='shiftedcmap'):
    '''
    Function to offset the "center" of a colormap. Useful for
    data with a negative min and positive max and you want the
    middle of the colormap's dynamic range to be at zero

    Input
    -----
      cmap : The matplotlib colormap to be altered
      start : Offset from lowest point in the colormap's range.
          Defaults to 0.0 (no lower ofset). Should be between
          0.0 and `midpoint`.
      midpoint : The new center of the colormap. Defaults to
          0.5 (no shift). Should be between 0.0 and 1.0. In
          general, this should be  1 - vmax/(vmax + abs(vmin))
          For example if your data range from -15.0 to +5.0 and
          you want the center of the colormap at 0.0, `midpoint`
          should be set to  1 - 5/(5 + 15)) or 0.75
      stop : Offset from highets point in the colormap's range.
          Defaults to 1.0 (no upper ofset). Should be between
          `midpoint` and 1.0.
    '''
    cdict = {
        'red': [],
        'green': [],
        'blue': [],
        'alpha': []
    }

    # regular index to compute the colors
    reg_index = np.linspace(start, stop, 257)

    # shifted index to match the data
    shift_index = np.hstack([
        np.linspace(0.0, midpoint, 128, endpoint=False),
        np.linspace(midpoint, 1.0, 129, endpoint=True)
    ])

    for ri, si in zip(reg_index, shift_index):
        r, g, b, a = cmap(ri)

        cdict['red'].append((si, r, r))
        cdict['green'].append((si, g, g))
        cdict['blue'].append((si, b, b))
        cdict['alpha'].append((si, a, a))

    newcmap = LinearSegmentedColormap(name, cdict)
    plt.register_cmap(cmap=newcmap)

    return newcmap


def main():

    # Parse arguments
    ap = ArgumentParser(description=
    '''
    Calculate the FORC distribution and plot
    '''
    )
    ap.add_argument('infile',
        type=str,
        help=
          'The magnetisation file "*.frc" file',
    )
    ap.add_argument('outfile',
        type= str,
        help=
          'The output pdf file',
    )
    ap.add_argument('-l', '--loop', nargs=3,
        type= int,
        help=
          'The hysteresis half-loop parameters (units=mT)',
    )
    ap.add_argument('--sf',
        type= int,
        help=
          'The forc distribution smoothing factor',
    )
    ap.add_argument('--xlim', nargs= 2,
        type= float,
        help=
          'The xlim plot parameters',
    )
    ap.add_argument('--ylim', nargs= 2,
        type= float,
        help=
          'The xlim plot parameters',
    )
    ap.add_argument('--minor',
        type= float,
        help=
          'The minor ticks forc plot parameter',
    )
    ap.add_argument('--major',
        type= float,
        help=
          'The major ticks forc plot parameters',
    )
    ap.add_argument('--cminor',
        type= float,
        help=
          'The minor ticks curves plot parameter',
    )
    ap.add_argument('--cmajor',
        type= float,
        help=
          'The major ticks curves plot parameters',
    )
    ap.add_argument('--contour-start',
        type= float,
        default=0.1,
        help=
          'The countour levels start value'
    )
    ap.add_argument('--contour-end',
        type= float,
        default=1.1,
        help=
          'The contour levels end value',
    )
    ap.add_argument('--contour-step',
        type= float,
        default=0.3,
        help=
          'The contour levels step value'
    )
    ap.add_argument('--annotations',
        type= str,
        default= "",
        help=
          '\'__\' separated list of annotations'
    )

    args = ap.parse_args()

    shiftedCMap = shiftedColorMap(RdBu_r, midpoint=(0.5))

    # Read generic FORC format
    mforc, Bfield = read_frc(args.infile)
    Bfield= [i*1000 for i in Bfield]
    Bfield.reverse()
    start=max(Bfield)
    end=min(Bfield)

    # process annotations here
    if args.annotations is not None:
        annotate = [ann.strip() for ann in args.annotations.split('__')]
    else:
        annotate = []

    # The applied field
    if not Bfield:
        print("Bfield not set")
        # Loop parameters
        start, end, step = args.loop
        Bfield = np.arange(end, start+abs(step), abs(step))

    # Calculate forc distribution
    Bb, Ba = np.meshgrid(Bfield, Bfield[::-1])
    rho = forc_distribution(mforc, Bb, Ba, args.sf)

    # Plot the forc distribution
    output_string ='test'
    fig, ax = plot_forc_distribution(
        Bb, Ba, rho,
        args.xlim, args.ylim,
        args.major, args.minor,
        shiftedCMap, annotate,
        contour_start=args.contour_start,
        contour_end=args.contour_end,
        contour_step=args.contour_step)
    fig.savefig(args.outfile); plt.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

