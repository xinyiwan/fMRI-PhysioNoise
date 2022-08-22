import imp
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
from nilearn.maskers import NiftiSpheresMasker
from nilearn.reporting import get_clusters_table


# @click.command()
# @click.argument("infile", type=click.Path())
# @click.argument("outfile", type=click.Path())
# @click.argument("t_scan", type=click.Path())
# @click.argument("regressors", type=click.Path())


def denoise(infile, outfile, t_scan, regressors,tr):


    '''This function uses regressros from biosignal to remove noise from fMRI data

    Parameters
    -------------------------------------------------------------------------
    inFile:                 Full path to fMRI data file (nii)

    outDir:                 Full path to output directory

    t_scan:                 Array for the scanning time


    regressors:             Full path to a csv file of regressors

    
    Output: 
    -------------------------------------------------------------------------

    residual.nii.gz:        Denoised fMRI data

    design_matrix.png:      Img of designed matrix

    contrasts.png:          Img of contrasts

    zstas_i.nii.gz:         Z value of noise components


    '''

    # write directory
    if not os.path.exists(outfile):
        mkdir(outfile)
    
    outDir = outfile + "/Denoise"
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
    frame_times = t_scan
    # frame_times = frame_times[1:]

    # with open(t_scan) as file_name:
    #     frame_times = np.loadtxt(file_name)
    # frame_times = frame_times[1:]

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

    # drop the constant in matrix
    X1.pop(X1.columns[-1]) 


    
    fig, (ax1) = plt.subplots(figsize=(10, 8), nrows=1, ncols=1)
    plot_design_matrix(X1, ax=ax1)
    ax1.set_title('Nuisance-related design matrix', fontsize=12)
    fig.savefig(outDir + '/design_matrix.png')


    # Build the 1st level model
    fmri_glm = FirstLevelModel(t_r = tr, minimize_memory=False, signal_scaling = False)

    # Get the number of components and constant(residual)
    n_columns = X1.shape[1]
    mean = mean_img(infile)
    
    # Build contrasts for each noise component
    contrasts = np.zeros([index,index])
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
        # nib.save(z_img, os.path.join(outDir,"zstat_%s.nii.gz"%i))
        # Plot the contrasts
        plotting.plot_stat_map(
            z_img,
            bg_img=mean, threshold=2, 
            title="zsta_component_%s"%i,
            draw_cross=False,
            output_file = os.path.join(outDir,"zstat_cont_%s.png"%i))
    # Save the residual data for the further use

    nib.save(fmri_glm.residuals[0],os.path.join(outDir,"residual.nii.gz"))

    ## ANALYSIS
    table = get_clusters_table(z_img, stat_threshold=2,
                           cluster_threshold=None).set_index('Cluster ID', drop=True)
    # get the 8 largest clusters' max x, y, and z coordinates
    n_clusters = len(table.head())
    coords = table.loc[range(1,n_clusters+1), ['X', 'Y', 'Z']].values

    # extract time series from each coordinate
    masker = NiftiSpheresMasker(coords)
    real_timeseries = masker.fit_transform(infile)
    predicted_timeseries = masker.fit_transform(fmri_glm.predicted[0])
    corrected_timeseries = masker.fit_transform(fmri_glm.residuals[0])

    # colors for each of the clusters
    colors = ['blue', 'navy', 'purple', 'magenta', 'olive']
    # plot the time series and corresponding locations
    fig1, axs1 = plt.subplots(3, n_clusters)
    for i in range(0, n_clusters):
        # plotting time series
        # axs1[0, i].set_title('Cluster peak {}\n'.format(coords[i]))
        axs1[0, i].plot(real_timeseries[:, i], c=colors[i], lw=2)
        axs1[0, i].plot(corrected_timeseries[:, i], c='r', ls='--', lw=2)
        axs1[0, i].plot(predicted_timeseries[:, i], c='g', ls='--', lw=2)
        axs1[0, i].set_xlabel('Time')
        axs1[0, i].set_ylabel('Signal intensity', labelpad=0)

        # plotting image below the time series
        roi_img = plotting.plot_stat_map(
            z_img, cut_coords=[coords[i][2]], threshold=2, figure=fig1,
            axes=axs1[1, i], display_mode='z', colorbar=False, bg_img=mean)
        roi_img.add_markers([coords[i]], colors[i], 300)

        # plotting frequency specturm
        frequency, power_spectrum = make_specturm(predicted_timeseries[:, i],tr)
        axs1[2, i].plot(frequency, power_spectrum)

    fig1.set_size_inches(24, 14)
    fig1.savefig(os.path.join(outDir,"5Clusters_effect.png"))



def make_specturm(data,tr):
    sampling_rate = 1/tr
    fourier_transform = np.fft.rfft(data)
    abs_fourier_transform = np.abs(fourier_transform)
    power_spectrum = np.square(abs_fourier_transform)
    frequency = np.linspace(0, sampling_rate/2, len(power_spectrum))

    return frequency,power_spectrum

# if __name__ == '__main__':
#     denoise()