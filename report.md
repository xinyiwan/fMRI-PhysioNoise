## Introduction

- fMRI origin
- noise origin
- Why denoise
- purpose

Physiological noise is one of the significant artefacts in functional magnetic resonance imaging(fMRI). fMRI uses magnetic imaging to measure brain activity by measuring changes in local oxygenation of blood, which in turn reflects the amount of local brain activity.[1] However, physiological pulsations related to cardiac pulsation and respiration would perturb blood-oxygen level contrast(BOLD) and add nuisance to fMRI data, which are the key challenges in this area. First, respiration is inevitable. During data aquisition, even the perfect subject could not avoid chest movement from breathing, which would result in head motion in the magnetic field. So that the MR images are likely to be distorted by respiration in a way. Second, cardiac pulsation could directly influence the BOLD signal especially in the region with large blood vessels. For example, cerebrospinal fluid(CSF) flow is modulated by both the cardiac and respiratory cycles, resulting in additional signal changes.[2]

The role of physiological noise in fMRI analysis deserves discussion. Some studies prefer not performing a physiological correction on fMRI data because cardiac and respiratory related fluctuations may be correlated with variations in neuronal activity.[2] However, the spatial specificity of functional connectivity has been clearly demonstrated to be influenced by aliased physiological noise.[4] A functional connectivity study by Dagli has shown that removing cardiac fluctuations resulted in a variance reduction of roughly 10–40%, depending on the region being investigated[5]. The sensitivity of these regions near pulsatile vessels could be improved by physiological noise correction. But another unarguable evidence is that heart rate variability is widely used as a measure of emotional arousal and autonomic nervous system activity.[2] All these facts remind us that physiological noise correction shoule be used carefully especially when the key factors in experiments are related to physiological responses.

In this work, we provides a robust model-based tool ___ in denoising physiological artefacts, which will give back a denoised data for further use. The implementation of this tool is based on the model RETROICOR [6]. 

This paper introduces the modules of this tool and explains results in each step from the example subject.


## Background

- GLM model of neural signal. Basis.
- Role of physiological signal
- Difficulty in denoise (global..)
- Existing methods for denoising


The goal of an fMRI data analysis is to analyze each voxel's time series to see whether the BOLD signal changes in response to some manipulation[1]. And the method used for fMRI analysis in detection of signal changes is the general linear model(GLM). GLM, a well-developed tool of linear systems analysis, is used widely to predict the responses of certain systems to a wide variety of inputs.[3]

In this work, our approach to addressing the problem of physiological artefacts is to record heartbeat and respiration signal during scanning, and then to retrospectively remove these effects from the data.[6] GLM model is used as the basis of the denoise tool to build a noise model representing physiological artefact in fMRI images, and the cleaned data is obtained by regressing out physiological components in the model.

The general linear model could be expressed 

Y = Xb + e

In the expression, X is a designed matrix containing linear variables for the model. And Y is explained by the X through weight bete. And bete is the weight for each varaible. The error of this model is estimated by e.

Inheritating the idea of GLM, noise model RETROICOR assumes that the signal coule be expressed by additive noise components with weights. Both cardiac signal and respiration signal are regarded as periodic signals, so that they can be expressed as a low-Fourier series expanded interms of these phases:

(展开式) [1]

In this expression, phy(c) and phy(t) are the phases in the respective cardiac and respiratory cycles. And the order of Fouriour expression is configureable. In this work we used M = 2 as default.


For the calculation of cardiac phase, it is defined as 

公式[2]

Here t1 and t2 is the time for the subsequent R-peak value. So the expression constrains the phase value in the range of 0 to 2pi. Since recorded physiological signals are used as inputs without any preprcossing, so R peak detection will be oprerated before the calculation. 


For the calculation of respiratory phase, depth and states of breathing will be both taken into consideration. It is quite easy to imagine that a deeper breathe is more likely to bring a potential bulk motion of head. And also the phase of respiration will be different from inhaling to exhaling. Therefore, respiratory phase will be defined by both depth and state. State of inhaling or exhaling is more like polarity of phase, and depth is more like the amplitude value. The signal of depth is recorded by a detecting belt wrapping around subject's chest. To get the respiratory amplitude of the given time, a histogram-equalized transfer function is used, which is expressed  as :

(展开式)

First, all the signal values are normalized to the range (0, Rmax). Then a histogram is gained with all normalized values. In the y domain of histogram, the y value is from the normalized data. And in the x domain, the bins of histogram are defined to be 100 bins. If the normalized amplitude from the given time belongs to the nth bin, then the phase value will be calculated by dividing the sum value till nth bin by the sum of 100 bins.

In the end, value from the divisor will multiple by pi and the state value which is expressed as ... in the formula.

During data aquisition of fMRI, BOLD time series have time resolution, which refers to reprtition time or TR. And by now MRI data will be either recorded by multi-slice or single slice at a time, which means the slices constructing the whole brain volumn come from different time during the TR. Therefore, it indicates that one given time stamp could not represent for all slices. However, applying different time stamp for each slice is also not practical. The slices are collected in horizontal direction, and the region of interest for an artefact could be in any shape rather than only scattering on a horizontal slice. To simplify the slice time problem, the middle time stamp in TR is chosen to calculate the physiological phases.


## Materials and Method

- Overview
- Data & Software
- Modules(Divide into modules that are meaningful to the resulst)
- Modelling the noise
- Noise correction and visualization
- Model assessment





## Results and discussion

- Nonlinearity? Limit of GLM model
- The problem about removing interesting signal as well
- Global noise reduction( Choose only WM or CSF that are less influenced by the )
- The noise model explains variance lower than 0.05, but it lost degree of freedom

### Reference

[1] handbook

[2] The role of physiological 

[3] Parametric Analysis of fMRI Data Using Linear Systems Methods

[4] Lowe, M.J., Mock, B.J., Sorenson, J.A., 1998. Functional connectivity in single and multislice echoplanar imaging using resting-state fluctuations. NeuroImage 7, 119–132.

[5] Dagli, M.S., Ingeholm, J.E., Haxby, J.V., 1999. Localization of cardiac-induced signal change in fMRI. NeuroImage 9, 407–415

[6] Gloveretal.,2000
