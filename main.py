from multiprocessing.spawn import import_main_path
from operator import imod
from traitlets import default
from denoise import denoise
from preprocess import prep
from getReg import getregressors
import os
import numpy as np
import click

@click.command()
@click.argument('func', type=click.Path())
@click.argument('struc', type=click.Path())
@click.argument('physio', type=click.Path())
@click.argument('outfile', type=click.Path())
@click.argument('tr',type=click.FLOAT)
@click.argument('order')
@click.argument('samplerate', type=click.INT)

def physio_denoise(func, struc, physio, outfile, tr, order, samplerate):

    '''This function executes motion correction of fMRI, regressors calculation and noise removal of fMRI data.
    The working directory is under the base directory.

    Parameters
    -------------------------------------------------------------------------
    func:                   Full path to fMRI data file (nii)

    struc:                  Full path to structural brain data

    workDir:                Raletive path to output directory

    physio:                 Full path to a txt file of physiological noise including 3 columns

    TR:                     TR (in seconds)

    order:                  Int value stands for the orders of noise model

    res_peak:               Full path to a csv file of respiration infomation

    
    Output: 
    -------------------------------------------------------------------------

    residual.nii.gz:        Denoised fMRI data

    design_matrix.png:      Img of designed matrix

    contrasts.png:          Img of contrasts

    zstas_i.nii.gz:         Z value of noise components

    Other variables from the workflow 

    '''
    if not os.path.exists(outfile):
        os.mkdir(outfile)
    
    prep(func, struc, outfile)
    tag = getregressors(physio, outfile, tr, order, samplerate)

    path = os.path.join(outfile,"prep", "motion/_realign0")
    in_file = [f for f in os.listdir(path) if f.endswith('.nii.gz')]
    in_file = os.path.join(path, in_file[0])
    regressors = open(os.path.join(outfile,"physio","regressors.csv"),"r")
    denoise(in_file, outfile, tag, regressors)

if __name__ == '__main__':
    physio_denoise()
