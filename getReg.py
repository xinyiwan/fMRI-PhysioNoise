from random import sample
from sre_parse import State
from sympy import im
import click
from http.client import ImproperConnectionState
import imp
from matplotlib.pyplot import show
import pandas as pd 
import math
import sys
import numpy as np
import os
import heartpy as hp
import matplotlib.pyplot as plt
import neurokit2 as nk


# @click.command()
# @click.argument("txtpath",type=click.Path())
# @click.argument("workdir",type=click.Path())
# @click.argument('tr')
# @click.argument('order')
# @click.argument('samplerate',type=click.INT)

def getregressors(txtpath, workdir, tr, order, samplerate):

    # Creat/check working path
    if not os.path.exists(workdir):
        os.mkdir(workdir)

    workdir = workdir + "/physio"
    
    if not os.path.exists(workdir):
        os.mkdir(workdir)

    # Open the txt file
    with open(txtpath, "r+") as f:
        d = f.readlines()

    # Remove the head infos 
    for i in np.arange(11):
        d.pop(0)
    
    # Split values into colums
    dataset = []
    for str in d:
        row = str.split("\t")
        if row[0] == '':
            break
        dataset.append([float(i) for i in row[:3]])
    
    # Give names to colums
    import pandas as pd 
    df = pd.DataFrame(dataset)
    df.columns = ['ppg','respiration','mri']
    tag, n_scan = pulse_detect(df['mri'], workdir, tr)
    df = df.astype('float')

    # Limit the length of t_scan by comparing the ends
    r_end = int(tag[n_scan-1]) + 3*int(float(tr))*10000
    if r_end <= len(df['mri']):
        df = df[0:r_end]

    # Analyze respiration
    rsp = nk.rsp_process(df['respiration'],samplerate,method="biosppy")
    rsp_info = rsp[0]
    phase = rsp_info['RSP_Phase']
    phase_c = pd.DataFrame(phase)
    phase_c.to_csv(workdir + '/rsp_phase.csv', index = None)
    # get phase value of respiration and cardiac
    
    resp_phase = getphase_res(df, tag, phase, workdir)
    card_phase = getphase_ppg(df['ppg'],tag, workdir)

    # Calculate and Define the size of regressors
    m = int(order)
    regressors = []
    for i in range(n_scan):
        t_reg = []
        for j in range(m):
            unit = [math.cos((j+1) * resp_phase[i]), math.sin((j+1) * resp_phase[i]), math.cos((j+1) * card_phase[i]), math.sin((j+1) * card_phase[i])]
            # if j == 0 :
            #     unit2 = [math.cos((j+1) * card_phase[i]) * math.cos((j+1) * resp_phase[i]),
            #              math.sin((j+1) * card_phase[i]) * math.cos((j+1) * resp_phase[i]),
            #              math.cos((j+1) * card_phase[i]) * math.sin((j+1) * resp_phase[i]),
            #              math.sin((j+1) * card_phase[i]) * math.sin((j+1) * resp_phase[i])]
            #     t_reg = np.concatenate((t_reg,unit,unit2))
            # else:
            #     t_reg = np.concatenate((t_reg,unit))
            t_reg = np.concatenate((t_reg,unit))
        regressors.append(t_reg)
    regressors = pd.DataFrame(regressors)
    regressors.to_csv(workdir + '/regressors.csv', index = None)
    return tag


def pulse_detect(mri, workdir,tr):
    # Get the time stamp of each MRI volume by checking the pulse value
    # tag contains all the t_scan
    t_scan = mri.astype(float)
    pulse = t_scan[t_scan[:] > 3.1]
    index_p = pulse.index
    tag = []
    tag.append(index_p[0])
    ref = index_p[0]

    for i in np.arange(len(index_p)):
        if i == len(index_p) - 1:
            break

        if index_p[i+1] -  ref > 50:
            tag.append(index_p[i+1])
            ref = index_p[i+1]
    n_scan = len(tag)  

    # Invoke the next line 
    # when using the middle time of scanning to be the frame time
    tag = [x+int(tr*5000) for x in tag]

    df = pd.DataFrame(tag)
    df.to_csv(workdir + '/mri_pulse.csv', index = None)
    return tag, n_scan


def getphase_ppg(ppg, t_scan, workdir):
    # Use heartpy to detect peaks
    working_data, measures = hp.process(ppg, 10000.0)

    #plot with different title
    fig = hp.plotter(working_data, measures, title='Heart Beat Detection on Noisy Signal', show = False)
    # fig.plt.savefig(workdir + "/heartbet.png")

    peak = working_data.get("peaklist")
    phase_ppg = []

    for p in t_scan:
        idx = find_left(peak,p)
        t1 = peak[idx]
        t2 = peak[idx+1]
        res = 2*math.pi*(p-t1)/(t2-t1)
        # print(t1,t2,p,p-t1,t2-t1,res)
        phase_ppg.append(res)
    
    return phase_ppg


def getphase_res(df, t_scan, phase, workdir):
    df = np.asarray(df)
    resp = np.zeros([len(df),2])
    resp[:,0] = df[:,1]

    # Mark the unreliable data segments
    resp[:,1] = np.where(resp[:,0] > 0.04, False, True)

    # Get the max and min value of respiration data
    max_value = np.max(resp[np.where(resp[:,1] == True),0])
    min_value = np.min(resp[np.where(resp[:,1] == True),0])
    range = max_value - min_value

    # Normalize the respiration data
    f = lambda x: (x-min_value)/(range)
    resp_norm = f(resp[np.where(resp[:,1] == True),0])
    hist = np.histogram(resp_norm, bins =100)

    num = len(hist[0])
    x = np.arange(num)
    # hist[0]

    # Plot and Save the histogram of respiration
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(15, 5))
    plt.bar(x, height = hist[0], )
    fig.savefig(workdir + '/respiration_histogram.png')

    # Find the MRI pulse in the histogram and get the value
    hist = np.asarray(hist)

    # Calculate the value of each scan before regressors calculation
    val = []
    for i in t_scan:
        amp = resp[i,0]
        amp_norm = f(amp)
        val.append(phase_value(hist,amp_norm) * find_phase(phase, i) * math.pi)
    val_c = pd.DataFrame(val)
    val_c.to_csv(workdir + '/rsp_phase_final_value.csv', index = None)
    return val


## Define the function that find the left amplitude
def find_left(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    if array[idx] > value:
        return idx-1
    else:
        return idx


## Define the function that calculate the value from histogram A/(A + B)
def phase_value(hist, amp_norm):
    idx = find_left(hist[1],amp_norm)
    num = len(hist[0])
    A = 0
    sum = 0
    for i in np.arange(num):
        if i <= idx:
            A = A + hist[0][i]
        sum = sum + hist[0][i]
    return A/sum


# array is the raw respiration signal
# value is the scanning time
def find_phase(phase,value):

    # state 1 means inhall
    state = phase[value]
    if state == 1:
        return 1
    else:
        return -1


# if __name__ == '__main__':
#     getregressors()