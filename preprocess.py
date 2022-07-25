import sys
import os
from nipype import Workflow, Node, Function
import nipype.pipeline.engine as pe          # pypeline engine
import nipype.interfaces.fsl as fsl          # fsl
from os.path import abspath
import nipype.interfaces.utility as util     # utility
from nibabel import load
import click


# @click.command()
# @click.argument("func", type=click.Path())
# @click.argument("struct", type=click.Path())
# @click.argument("outfile", type=click.Path())

def prep(func,struct,outfile):
    
    #Check/create working path
    if not os.path.exists(outfile):
        os.mkdir(outfile)
    outfile = outfile + "/prep" 
    if not os.path.exists(outfile):
        os.mkdir(outfile)
    
    preproc = pe.Workflow(name='preproc')
    inputnode = pe.Node(interface=util.IdentityInterface(fields=['func','struct',]),
                    name='inputspec')
    # inputnode.inputs.func = abspath('/Users/xinyi/Desktop/data/subject/sub01.nii')
    # inputnode.inputs.struct = abspath('/Users/xinyi/Desktop/data/subject/struct.nii')
    inputnode.inputs.func = abspath(func)
    inputnode.inputs.struct = abspath(struct)

    # Convert img to fload format. 
    # In case of multiple inputs, here we use a mapnode to convert everyrun
    img2float = pe.MapNode(interface=fsl.ImageMaths(out_data_type='float',
                                                    op_string='',
                                                    suffix='_dtype'),
                                                    iterfield=['in_file'],
                                                    name='img2float')

    preproc.connect(inputnode, 'func', img2float, 'in_file')

    motion_correct = pe.MapNode(interface=fsl.MCFLIRT(save_mats=True,
                                                    save_plots=True),
                                                    name='realign',
                                                    iterfield=['in_file'])

    plot_motion = pe.Node(interface=fsl.PlotMotionParams(in_source='fsl'),
                                                    name='plot_motion',
                                                    iterfield=['in_file'])
    plot_motion.iterables = ('plot_type', ['rotations', 'translations'])

    # Extract the middle volume of the first run as the reference
    extract_ref = pe.Node(interface=fsl.ExtractROI(t_size=1),
                                                    name='extractref')

    preproc.connect(img2float,('out_file', pickfirst), extract_ref, 'in_file')
    preproc.connect(inputnode, ('func', getmiddlevolume), extract_ref, 't_min')

    # Datasink - creates output folder for important outputs
    from nipype.interfaces.io import SelectFiles, DataSink

    # experiment_dir = '/Users/xinyi/Desktop/data/subject'
    # output_dir = '/Users/xinyi/Desktop/data/subject/datasink/prep0711'

    datasink = Node(DataSink(base_directory=outfile),
                    name="datasink")


    preproc.connect([(extract_ref,motion_correct,[('roi_file','ref_file')]),
                 (inputnode,motion_correct,[('func','in_file')]),
                 (motion_correct,plot_motion,[('par_file','in_file')]),
                 (motion_correct,datasink,[('out_file','motion.@res')]),
                 (plot_motion,datasink,[('out_file','motion.@fig')])])
    eg = preproc.run()
    preproc.write_graph(dotfilename= outfile + "/gragh.dot",graph2use='orig')




# Define a function to pick file
# used when the input is a list of files
def pickfirst(files):
    if isinstance(files, list):
        return files[0]
    else:
        return files

# Define a function to return the 1 based index of the middle volume
def getmiddlevolume(func):
    from nibabel import load
    funcfile = func
    if isinstance(func, list):
        funcfile = func[0]
    _, _, _, timepoints = load(funcfile).shape
    return int(timepoints / 2) - 1

# if __name__ == '__main__':
#     prep()