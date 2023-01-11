import os
import re
from os import listdir
from os.path import isfile, join
from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename
from tkinter import filedialog
import pandas as pd
from functools import partial
import fnmatch
from scipy.integrate import quad
from scipy.stats import lognorm
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import numpy as np
import typer

app = typer.Typer()

fig, ax = plt.subplots(1, 1)

# code to average all forc files that it finds in a particular directory
def get_file_list(dirbase=""):

    all_files=[]
    all_sizes=[]
    all_elongs=[]

    home = os.path.expanduser('~/Research')

    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing

    #filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
    if dirbase == "":
        dirbase = filedialog.askdirectory(initialdir=home)

    counter=0

    for file in os.listdir(dirbase):
        if file.lower().endswith('.frc'):
            allname = join(dirbase, file)
            # get size and elongation from filename
            elong = re.search(r'_E(.*?)_S', file, re.M | re.S).group(1)
            size = re.search(r'_S(.*?).frc', file, re.M | re.S).group(1)

            all_files.append(allname)
            all_sizes.append(size)
            all_elongs.append(elong)
            counter += 1

    print('{} data files read'.format(counter))

    return all_files, all_sizes, all_elongs, dirbase


# retrun a list of files and grain sizes for a particular elongation value
def get_filtered_file_list(filelist, elong):
    Eelong='E'+elong
    filtered_sizes=[]

    elong_file_list= [s for s in filelist if Eelong in s]
    for file in elong_file_list:
        match = re.search(r'average_E([0-9]{2,3})_S([0-9]{2,3}).frc', file)
        size = size=int(match.group(2))
        print('size = {}'.format(size))
        filtered_sizes.append(size)

    return elong_file_list, filtered_sizes


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
    fo = open(filename, "w")

    # iterate through dataframe rows and write out the field and magnetization columns
    for index, row in df_final.iterrows():
        if index==0:
            stringline= ('{hfield}'+','+'{mag:.5E}').format(hfield=row['field'],mag=row['mean'])
            append_new_line(filename,stringline)
            #print(index, row['field'], row[0])
        field_new=float(row['field'])
        #print(type(field_new))
        if index>0:

            if field_new < field_old:
                stringline =""
                append_new_line(filename, stringline)

            stringline= ('{hfield}'+','+'{mag:.5E}').format(hfield=row['field'],mag=row['mean'])
            append_new_line(filename,stringline)
        field_old = field_new
    stringline = ""
    append_new_line(filename, stringline)
    stringline = "END"
    append_new_line(filename, stringline)
    fo.close()


def get_all_frc(filelist, sizelist, norm_list, norm_file):
    # read in the first column of one file to get the list of field values
    df0= pd.read_csv(filelist[0], sep=',', usecols=[0] , header=None, names=['field'])
    df0.drop(df0.tail(1).index, inplace=True)
    #print(df0)

    # define 'readin' a modifier to read_csv so we can use it with the 'map' utility
    readin = partial(pd.read_csv, sep=',', usecols=[1], header=None, prefix='M')

    df = pd.concat(map((readin), filelist), axis=1)
    df.drop(df.tail(1).index, inplace=True)
    #print(df)
    df.columns=sizelist

    # sort data frame columns to increasing grain size
    df=df.reindex(sorted(df.columns, key=lambda x: float(x)), axis=1)

    #normalize each column df (which only contains values of M) by norm_list value
    # df.to_csv('/Users/williams/Desktop/Before_n.csv')

    for col in df.columns:
        col_index=int(df.columns.get_loc(col))
        print('col = {}, {} df= {}'.format(col,col_index, norm_list[col_index]))
        # max_M= df[col].max()
        df[col]=df[col]*norm_list[col_index]
    # df.to_csv('/Users/williams/Desktop/After_n.csv')

    indx_count=0
    with open(norm_file, 'a+') as f:
        for item in norm_list:
            with open(norm_file, 'a') as f:
                f.write('size = {}, factor = {:10.6f} \n'.format(df.columns[indx_count], item))
            indx_count+=1

    #print(df)


    dfmean=df.mean(axis=1).to_frame()
    dfmean.columns= ['mean']
#    df.columns=filelist


    # define a new data frame with columns of field, M for each frcfile, and average M
    #df_final=pd.concat((df0,df,dfmean), axis=1)

    # define a new data frame with columns of field,  and average M
    df_final=pd.concat((df0, df, dfmean), axis=1)
    #print(df_final)

    return df_final



def read_frcs(dirname,elongation,size):
    all_files=[]
    count=0
    for dirNames, subdirList, fileList in os.walk(dirname):
        if fnmatch.fnmatch(dirNames, elongation) and fnmatch.fnmatch(dirNames, size):
            count+=1
            for fname in fileList:
                if fname.lower().startswith('my') and fname.lower().endswith('.frc'):
                    allname=join(dirNames,fname)
                    all_files.append(allname)
                    ##print('\t%s' % allname)

    #os.chdir(dirname)
    #all_files = [f for f in listdir(dirname) if isfile(join(dirname, f))]
    print('{} data files read'.format(count))
    #print(all_files)


    df0= pd.read_csv(all_files[0], sep=',', usecols=[0] , header=None, names=['field'])
    df0.drop(df0.tail(1).index, inplace=True)
    #print(df0)

    readin = partial(pd.read_csv, sep=',', usecols=[1], header=None, prefix='M')

    df = pd.concat(map((readin), all_files), axis=1)
    df.drop(df.tail(1).index, inplace=True)
    #print(df)


    dfmean=df.mean(axis=1).to_frame()
    dfmean.columns= ['mean']
    df.columns=all_files

    df_final=pd.concat((df0,df,dfmean), axis=1)
    return df_final



def check_frcs(dirname,elongation,size):
    all_files=[]
    count=0
    for dirNames, subdirList, fileList in os.walk(dirname):
        if fnmatch.fnmatch(dirNames, elongation) and fnmatch.fnmatch(dirNames, size):
            for fname in fileList:
                if fname.lower().startswith('my') and fname.lower().endswith('.frc'):
                    count+=1
                    allname=join(dirNames,fname)
                    all_files.append(allname)
                    #print('\t%s' % allname)
    badcount=0
    for file in all_files:
        linecount=len(open(file).readlines())
        #if linecount != 81003:
        if linecount != 5253:
            badcount+=1
            #print('{} lines in file{}'.format(linecount, file))
    print('{} files found for {}, {} with {} bad files'.format(count, elongation.replace('*',''),size.replace('*',''), badcount))





def lognorm_dist_elongs(geometric_mean_size, shape ,elong_list):
    r"""
    Creates a lognormal distribution with medium value = size, and standard deviation = size/3.
    :return: a scipy lognormal object.
    """
    #variance = deviation**2
    #variance = (mean_size / 3) ** 2
    #scale = mean_size / (variance / (mean_size ** 2) + 1) ** .5


    scale=geometric_mean_size


    nd = lognorm(shape, loc=0, scale=scale).pdf
    norm_list_elong=[]
    nulist = [int(i) for i in elong_list]
    #min and max sizes of partciles in file list
    elong_min=min(nulist)
    elong_max=max(nulist)

    # the min and max size over which we will integrate
    min_elong=0
    max_elong=500
    #put size list in order
    elongs_in_order = sorted(nulist)
    print(nulist)
    print('elongs in order')
    print(elongs_in_order)

    #intgrate from min_size to max_size to get normalization factor
    res_norm, err = quad(nd, min_elong, max_elong)

    for elong in elongs_in_order:
        list_index=elongs_in_order.index(int(elong))
        if list_index == elongs_in_order.index(elong_min):
            xmin=0
        else:
            xmin = (float(elongs_in_order[list_index]) + float(elongs_in_order[list_index -1]))/2
        if list_index == elongs_in_order.index(elong_max):
            xmax = max_elong
        else:
            xmax = (float(elongs_in_order[list_index]) + float(elongs_in_order[list_index + 1]))/2
        #integrate over corect interval for each given grain sizeat centre of interval
        res, err = quad(nd, xmin, xmax)

        norm_list_elong.append(res/res_norm)
    # for x in range(len(elongs_in_order)):
    #     print('elong, norm {} {}'.format(elongs_in_order[x], norm_list_elong[x]/res_norm ))
    #     print('sum of norm = {}'.format(sum(norm_list_elong)/res_norm))

    return norm_list_elong

def lognorm_dist(geometric_mean_size, shape ,size_list):
    r"""
    Creates a lognormal distribution with medium value = size, and standard deviation = size/3.
    :return: a scipy lognormal object.
    """
    #variance = deviation**2
    #variance = (mean_size / 3) ** 2
    #scale = mean_size / (variance / (mean_size ** 2) + 1) ** .5


    scale=geometric_mean_size


    nd = lognorm(shape, loc=0, scale=scale).pdf
    norm_list=[]
    print(size_list)
    nulist = [int(i) for i in size_list]
    #min and max sizes of partciles in file list
    size_min=min(nulist)
    size_max=max(nulist)

    # the min and max size over which we will integrate
    min_size=0
    max_size=500
    #put size list in order
    size_in_order = sorted(nulist)
    print(nulist)
    print(size_in_order)

    #intgrate from min_size to max_size to get normalization factor
    res_norm, err = quad(nd, min_size, max_size)

    for size in size_in_order:
        list_index=size_in_order.index(int(size))
        if list_index == size_in_order.index(size_min):
            #xmin = (size_in_order[list_index] - min_size) / 2
            xmin=0
        else:
            xmin = (float(size_in_order[list_index]) + float(size_in_order[list_index -1]))/2
        if list_index == size_in_order.index(size_max):
            xmax = max_size
        else:
            xmax = (float(size_in_order[list_index]) + float(size_in_order[list_index + 1]))/2
        #integrate over corect interval for each given grain sizeat centre of interval
        res, err = quad(nd, xmin, xmax)

        norm_list.append(res/res_norm)

    return norm_list

def plt_lognorm_dist(geometric_mean_size, shape, ax_norm, fig_norm, pltfile):
    r"""
    Creates a lognormal distribution with medium value = size, and standard deviation = size/3.
    :return: a scipy lognormal object.
    """


    scale=geometric_mean_size


    nd = lognorm(shape, loc=0, scale=scale).pdf

    x = np.linspace(0.1, 500, 100)
    ax_norm.plot(x,nd(x), label = str(geometric_mean_size))
    plt.xlabel(r'$Grain Size\, (\mathrm{nm})$', fontsize='xx-large')
    plt.ylabel(r'$Pdf $', fontsize='xx-large', rotation='vertical')
    major=100
    minor=10
    majorLocator = MultipleLocator(major)
    majorFormatter = FormatStrFormatter('%d')
    minorLocator = MultipleLocator(minor)
    ax_norm.xaxis.set_major_locator(majorLocator)
    ax_norm.xaxis.set_major_formatter(majorFormatter)
    ax_norm.xaxis.set_minor_locator(minorLocator)
    plt.xticks(rotation=45)


    plt.yticks(rotation=45)
    plt.subplots_adjust(bottom=0.2)
    plt.subplots_adjust(left=0.2)
    title=('Geometric mean = {} nm,  Shape = {}'.format(scale, shape))
    #ax_norm.legend(loc='upper right', title='geomatric mean')






# def get_frc_from_distribution(all_frc):
#     # define lognormal distribution

@app.command()
def app_main(dirbase:str=""):
    all_files,all_sizes, all_elongs, dirbase =get_file_list(dirbase)
    all_elongs=list(set(all_elongs))
    int_elongs= sorted([int(i) for i in all_elongs])
    str_elongs = [str(i).zfill(3) for i in int_elongs]
#    print(str_elongs)

    #mean_size = 300
    mean_size_list=[40,60,80,100,120,150,200,300]
    shape = 1.0
    elong_shape= 1.0

    norm_file = dirbase + '/../SizeDistributions/Normalization_factors.txt'
    f =open(norm_file, 'w')
    f.close()
    fig_norm, ax_norm = plt.subplots()
    pltfile = dirbase + '/../SizeDistributions/Elongs_LonNorm_GM' + '_Shape' + str(shape) + '.pdf'

    #geometric_mean_elong_list = [1]
    geometric_mean_elong_list = [1, 20, 40, 60, 100, 150, 200, 250, 300, 400]


# dont need this outer for loop for grain size distributions with single elongation
    for geometric_mean_elong in geometric_mean_elong_list:
        GME = str(geometric_mean_elong).zfill(3)
        norm_list_elongs=lognorm_dist_elongs(geometric_mean_elong, elong_shape, int_elongs)

        for mean_size in mean_size_list:

            plt_lognorm_dist(mean_size, shape, ax_norm, fig_norm, pltfile)


        # ################################################################################################################
        # #this next block is for writing frc files per specified grain size distribution and for each available elongation
        # ################################################################################################################
        #
        # for elong in str_elongs:
        #     filtered_file_list, sizes_for_elong= get_filtered_file_list(all_files,elong)
        #     with open(norm_file,'a') as f:
        #         f.write('Lognorm mean size = {}, shape = {}, elongation ={} \n'.format(mean_size,shape,elong))
        #     # print(filtered_file_list)
        #     # print(sizes_for_elong)
        #     norm_list = lognorm_dist(mean_size, shape, sizes_for_elong)
        #     # print(norm_list)
        #
        #     df_all_frc = get_all_frc(filtered_file_list,sizes_for_elong,norm_list,norm_file)
        #
        #     #dist_frc = get_frc_from_distribution(all_frc)
        #     outfile= dirbase+'/../SizeDistributions/E'+elong + 'LonNorm_GM'+str(mean_size)+'_Shape'+str(shape)+'.frc'
        #     print('outfile = {}'.format(outfile))
        #
        #
        #     write_frc(outfile, df_all_frc)
        # ###############################################################################################################
        # ###############################################################################################################


        # ################################################################################################################
        # # this next block is for writing frc files per specified grain size distribution and for a elongation distribution
        # ################################################################################################################
            elong_index=0
            df_elong_dist=pd.DataFrame(columns=['field','elong_dist'])

            for elong in str_elongs:
                filtered_file_list, sizes_for_elong= get_filtered_file_list(all_files,elong)
                with open(norm_file,'a') as f:
                    f.write('Lognorm mean size = {}, shape = {}, elongation ={} \n'.format(mean_size,shape,elong))
                # print(filtered_file_list)
                # print(sizes_for_elong)
                norm_list = lognorm_dist(mean_size, shape, sizes_for_elong)
                # print(norm_list)

                df_all_frc = get_all_frc(filtered_file_list,sizes_for_elong,norm_list,norm_file)
                #print('elong index = {},  norm = {}'.format(elong_index, norm_list_elongs[elong_index]))
                if elong_index==0:
                    print('set column to zero')
                    df_elong_dist['field']=df_all_frc['field']
                    df_elong_dist['mean']=0

                #dist_frc = get_frc_from_distribution(all_frc)
                # outfile= dirbase+'/../TESTpdfs/E'+elong + 'LonNorm_GM'+str(mean_size)+'_Shape'+str(shape)+'.frc'
                # print('outfile = {}'.format(outfile))

                df_elong_dist['mean']=df_elong_dist['mean']+df_all_frc['mean']*norm_list_elongs[elong_index]
                elong_index+=1
            outfile= dirbase+'/../ElongSizeDistributions/DistrE'+ GME + 'LonNorm_GM'+str(mean_size)+'_Shape'+str(shape)+'.frc'
            print('outfile = {}'.format(outfile))
            write_frc(outfile, df_elong_dist)
        # ################################################################################################################
        # ################################################################################################################


    title = ('Lognormal distributions with Shape Factor {}'.format(shape))

    ax_norm.legend(loc = 'upper right', title='Geometric mean (nm)')
    plt.title(title)
    #fig_norm.savefig(pltfile)





if __name__ == '__main__':
    main()
