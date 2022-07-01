# Code to average .frc files per elongation and grain size in a
# directory hierarchy. Usually used to produce a .frc data file that
# contains teh averaged forc data from several field directions distributed
# over a sphere
import os
from os import listdir
from os.path import isfile, join
from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename
from tkinter import filedialog
import pandas as pd
from functools import partial
import fnmatch
import typer

app = typer.Typer()


def read_all_filenames(dirbase):
    all_files = []
    count = 0
    print('dirbase= ', dirbase)
    for dirNames, subdirList, fileList in os.walk(dirbase):
        for fname in fileList:
            # next line to read FORC loops  in loop format
            if fname.lower().startswith('my') and fname.lower().endswith('forc.loop'):
                count += 1
                allname = join(dirNames, fname)
                all_files.append(allname)
                ##print('\t%s' % allname)
    print('{} data files read'.format(count))

    return all_files


def calculate_product(row):
    return row[1]*row[4] + row[2]*row[5] + row[3]*row[6]


def get_average_loop(filelist):

    avgDataFrame = pd.read_csv(filelist[0], sep=',',  header=0)
    avgDataFrame['M.H'] = avgDataFrame.apply(calculate_product, axis=1)

    for i in range (1, len(filelist)):
        temppd= pd.read_csv(filelist[i], sep=',',  header=0)
        temppd['M.H'] = temppd.apply(calculate_product, axis=1)
        avgDataFrame = avgDataFrame.add(temppd)
        print('file = {}'.format(filelist[i]))
        print('Number of cols = {}'.format(avgDataFrame.shape[1]))
    df_final = avgDataFrame / len(filelist)

    return df_final


def get_average_frc(filelist):
    headerlist=['field', 'magnetization']
    dtype={'field':float, 'magnetization':float}
    avgDataFrame = pd.read_csv(filelist[0], sep=',', header=None, skip_blank_lines=False, names=None, dtype=dtype,skipfooter=2)

    for i in range (1, len(filelist)):
        temppd= pd.read_csv(filelist[i], sep=',', header=None, skip_blank_lines=False, names=None, dtype=dtype, skipfooter=2)
        avgDataFrame = avgDataFrame.add(temppd)
        print('adding file {}'.format(i))
    df_final = avgDataFrame / len(filelist)

    return df_final


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


def write_frc_from_loop(filename, df_final):
    fo = open(filename, "w")
    for index, row in df_final.iterrows():
        if index==0:
            stringline= ('{hfield}'+','+'{mag:.5E}').format(hfield=row[0],mag=row[10])
            append_new_line(filename,stringline)
        field_new=float(row[0])
        if index>0:

            if field_new < field_old:
                stringline =""
                append_new_line(filename, stringline)

            stringline= ('{hfield}'+','+'{mag:.5E}').format(hfield=row[0],mag=row[10])
            append_new_line(filename,stringline)
        field_old = field_new
    stringline = ""
    append_new_line(filename, stringline)
    stringline = "END"
    append_new_line(filename, stringline)
    fo.close()


def read_frcs(dirname,elongation,size):
    all_files=[]
    count=0
    print('dirname, elongation, size = ', dirname,elongation, size)
    for dirNames, subdirList, fileList in os.walk(dirname):
        if fnmatch.fnmatch(dirNames, elongation) and fnmatch.fnmatch(dirNames, size):

            for fname in fileList:
                if fname.lower().startswith('my') and fname.lower().endswith('.frc'):
                    count += 1
                    allname=join(dirNames,fname)
                    all_files.append(allname)

    print('{} data files read'.format(count))
    print(all_files)

    df0= pd.read_csv(all_files[0], sep=',', usecols=[0] , header=None, names=['field'])
    df0.drop(df0.tail(1).index, inplace=True)

    readin = partial(pd.read_csv, sep=',', usecols=[1], header=None, prefix='M')

    df = pd.concat(map((readin), all_files), axis=1)
    df.drop(df.tail(1).index, inplace=True)

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
                    print(fname)
                    count+=1
                    allname=join(dirNames,fname)
                    all_files.append(allname)
    badcount=0
    for file in all_files:
        linecount=len(open(file).readlines())
        if linecount != 5253:
            badcount += 1
    print('{} files found for {}, {} with {} bad files'.format(count, elongation.replace('*',''),size.replace('*',''), badcount))


@app.command()
def app_main(dirbase:str = "", output_file:str = ""):

    home = os.path.expanduser('~')

    if dirbase == "":
        Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
        dirbase = filedialog.askdirectory(initialdir=home)

    print('dirbase = ', dirbase)

    my_list = read_all_filenames(dirbase)

    # Either read and average data using the .loop files or .frc
    # remember to chose the correct list of files in read_all_filenames
    df_final=get_average_loop(my_list)
    print(df_final)

    if output_file == "":
        outfilefrc= dirbase+ '/average_forcnewloop.frc'
    else:
        outfilefrc = output_file

    write_frc_from_loop(outfilefrc,df_final)
    exit()


def main():
    app()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
