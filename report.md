## Introduction

- fMRI origin
- noise origin
- Why denoise
- purpose

Physiological noise is one of the significant motion artefacts in functional magnetic resonance imaging(fMRI). fMRI uses magnetic imaging to measure brain activity by measuring changes in local oxygenation of blood, which in turn reflects the amount of local brain activity.[1] However, physiological pulsations related to cardiac pulsation and respiration would perturb blood-oxygen level contrast(BOLD). First, respiration is inevitable. During data aquisition, even the perfect subject could not avoid chest movement from breathing, which would result in head motion in the magnetic field. So the MR images are likely to be distorted by respiration in a way. Second, cardiac pulsation could directly influence the BOLD signal especially in the region with large blood vessels. For example, cerebrospinal fluid(CSF) flow is modulated by both the cardiac and respiratory cycles, resulting in additional signal changes.[2] 

(The introversial idea about denoising physiological noise. Example, resting state) 

Purpose:

The main purpose of this research is to provide a robust tool in denoising physiological artefacts, which will give back a 'cleaned' data for the furthur use.


## Background

- GLM model of neural signal. Basis.
- Role of physiological signal
- Difficulty in denoise (global..)
- Existing methods for denoising


## Materials and Method

- Overview
- Data & Software
- Modules(Divide into modules that are meaningful to the resulst)
- Modelling the noise
- Noise correction and visualization
- Model assessment

## Results and discussion

- The problem about removing interesting signal as well
- Global noise reduction( Choose only WM or CSF that are less influenced by the )

### Reference

[1] handbook

[2] The role of physiological
