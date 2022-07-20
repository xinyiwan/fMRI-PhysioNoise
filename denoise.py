from operator import imod
import click
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from os import mkdir, getcwd, path
import nilearn
from nilearn.glm.first_level import make_first_level_design_matrix
from nilearn.plotting import plot_design_matrix
from nilearn.image import mean_img
from nilearn.glm.first_level import FirstLevelModel
from nilearn.plotting import plot_contrast_matrix
import nibabel as nib
from nilearn import plotting
import argparse


# @click.command()
# @click.argument("infile", type=click.Path())
# @click.argument("outfile", type=click.Path())
# @click.argument("t_scan", type=click.Path())
# @click.argument("regressors", type=click.Path())


def denoise(infile, outfile, t_scan, regressors):


    '''This function uses regressros from biosignal to remove noise from fMRI data

    Parameters
    -------------------------------------------------------------------------
    inFile:                 Full path to fMRI data file (nii)

    outDir:                 Full path to output directory

    regressors:             Full path to a csv file of regressors

    tag:                    Array for the scanning time


    
    Output: 
    -------------------------------------------------------------------------

    residual.nii.gz:        Denoised fMRI data

    design_matrix.png:      Img of designed matrix

    contrasts.png:          Img of contrasts

    zstas_i.nii.gz:         Z value of noise components


    '''

    # Define the directory
    # residual = os.path.join(outDir,'residual.nii.gz')
    # inFile = os.path.join(inFile,"")
    # regressors = os.path.join(regressors,"")
    # outDir = os.path.join(outDir,"")

    # inFile = sys.argv[1]
    # outDir = sys.argv[2]
    # regressors = sys.argv[3]

    # write directory
    if not os.path.exists(outfile):
        mkdir(outfile)
    
    outDir = outfile + "/results"
    if not os.path.exists(outDir):
        mkdir(outDir)

    print('Computation will be performed in directory: %s' %outDir)

    # Define the calculated regressors
    reg = pd.read_csv(regressors)
    add_reg_names = []
    
    index = len(reg.columns)
    for i in range(index):
        add_reg_names.append('L%s'%i)
    
    # input the time of scanning
    # with open(t_scan) as file_name:
    #     frame_times = np.loadtxt(file_name)
    frame_times = t_scan

    # Define the empty tasks conditions
    conditions = []
    duration = []
    onsets = []

    events = pd.DataFrame({'trial_type': conditions, 'onset': onsets,
                       'duration': duration})
    

    # Design the 1st level analysis
    hrf_model = 'glover'
    X1 = make_first_level_design_matrix(
        frame_times, events, drift_model=None,
        add_regs=reg, add_reg_names=add_reg_names, hrf_model=hrf_model)

    
    fig, (ax1) = plt.subplots(figsize=(10, 6), nrows=1, ncols=1)
    plot_design_matrix(X1, ax=ax1)
    ax1.set_title('Nuisance-related design matrix', fontsize=12)
    fig.savefig(outDir + '/design_matrix.png')


    # Build the 1st level model
    fmri_glm = FirstLevelModel(
                           minimize_memory=False)
    # Get the number of components and constant(residual)
    n_columns = X1.shape[1]
    mean = mean_img(infile)
    
    # Build contrasts for each noise component
    contrasts = np.zeros([index,index+1])
    for i in range(index):
        contrasts[i,i] = 1

    ax2 = plot_contrast_matrix(contrasts, design_matrix=X1)
    ax2.figure.savefig(outDir + '/contrasts.png')

    # Fit with GLM model
    fmri_glm = fmri_glm.fit(infile, design_matrices=X1)

    # Save the nii image of statistical value of each noise component
    for i in range(index):
        z_img = fmri_glm.compute_contrast(contrasts[i], 
                         output_type='z_score')
        nib.save(z_img, os.path.join(outDir,"zstat_%s.nii.gz"%i))
        # Plot the contrasts
        plotting.plot_stat_map(
            z_img,
            bg_img=mean, threshold=3, 
            title="zsta_component_%s"%i,
            output_file = os.path.join(outDir,"zstat_cont_%s.png"%i))
    # Save the residual data for the further use

    nib.save(fmri_glm.residuals[0],os.path.join(outDir,"residual.nii.gz"))
    return fmri_glm.residuals[0]


# if __name__ == '__main__':
#     denoise()