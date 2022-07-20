# fMRI-PhysioNoise

## Purpose

PhysioNoise is a tool for physiological noise correction of fMRI. The core model of this tool is based on the noise model from RETROICOR (Glover et al. 2000), including cardiac and respiration caused noise in fMRI image. 

The main idea of PhysioNoise is to build a GLM with noise as main components. Noise components come from RETROICOR noise model and are used as regressors in GLM. The residual of GLM will be the corrected fMRI data for furthur use.
