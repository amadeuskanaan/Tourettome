import nipype.pipeline.engine as pe
import nipype.interfaces.utility as util


def calc_friston_twenty_four(in_file):
    """
    Method to calculate friston twenty four parameters

    Parameters
    ----------
    in_file: string
        input movement parameters file from motion correction

    Returns
    -------
    new_file: string
        output 1D file containing 24 parameter values

    """

    import numpy as np
    import os

    new_data = None

    data = np.genfromtxt(in_file)

    data_squared = data ** 2

    new_data = np.concatenate((data, data_squared), axis=1)

    data_roll = np.roll(data, 1, axis=0)

    data_roll[0] = 0

    new_data = np.concatenate((new_data, data_roll), axis=1)

    data_roll_squared = data_roll ** 2

    new_data = np.concatenate((new_data, data_roll_squared), axis=1)

    new_file = os.path.join(os.getcwd(), 'fristons_twenty_four.1D')
    np.savetxt(new_file, new_data, fmt='%0.8f', delimiter=' ')

    return new_file



def set_frames_ex(in_file, threshold,
                  frames_before=1, frames_after=2):
    """
    Method to calculate Number of frames that would be censored
    ("scrubbed") by removing the offending time frames
    (i.e., those exceeding FD threshold), the preceding frame,
    and the two subsequent frames

    Parameters
    ----------
    in_file : a string
        framewise displacement(FD) file path
    threshold : a float
         scrubbing threshold value set in configuration file
    frames_before : an integer
        number of frames preceding the offending time frame
        by default value is 1
    frames_after : an integer
        number of frames following the offending time frame
        by default value is 2

    Returns
    -------
    out_file : string
        path to file containing offending time frames
    """

    import os
    import numpy as np
    from numpy import loadtxt

    out_file = os.path.join(os.getcwd(), 'frames_ex.1D')
    data = loadtxt(in_file)
    #masking zeroth timepoint value as 0, since the mean displacment value for
    #zeroth timepoint cannot be calculated, as there is no timepoint before it
    data[0] = 0

    extra_indices = []

    indices = [i[0] for i in (np.argwhere(data >= threshold)).tolist()]
    #print "initial indices-->", indices

    for i in indices:

        #remove preceding frames
        if i > 0 :
            count = 1
            while count <= frames_before:
                extra_indices.append(i-count)
                count+=1

        #remove following frames
        count = 1
        while count <= frames_after:
            extra_indices.append(i+count)
            count+=1

    indices = list(set(indices) | set(extra_indices))
    indices.sort()

    f = open(out_file, 'a')

    #print "indices preceding and following -->", \
    #      set(extra_indices)
    #print "final indices -->", indices
    for idx in indices:
        f.write('%s,' % int(idx))

    f.close()

    return out_file


def calculate_FD_Power(in_file):
    """
    Method to calculate Framewise Displacement (FD) calculations
    (Power et al., 2012)

    Parameters
    ----------
    in_file : string
        movement parameters vector file path

    Returns
    -------
    out_file : string
        Frame-wise displacement mat
        file path

    """

    import os
    import numpy as np

    out_file = os.path.join(os.getcwd(), 'FD.1D')

    lines = open(in_file, 'r').readlines()
    rows = [[float(x) for x in line.split()] for line in lines]
    cols = np.array([list(col) for col in zip(*rows)])

    translations = np.transpose(np.abs(np.diff(cols[3:6, :])))
    rotations = np.transpose(np.abs(np.diff(cols[0:3, :])))

    FD_power = np.sum(translations, axis = 1) + (50*3.141/180)*np.sum(rotations, axis =1)

    #FD is zero for the first time point
    FD_power = np.insert(FD_power, 0, 0)

    print 'FD-Power=', np.mean(FD_power)
    print 'FD-Max='  , np.max(FD_power)

    np.savetxt(out_file, FD_power)

    return out_file


def calculate_FD_J(in_file):

    '''
    @ Krsna
    May 2013
    compute
    1) Jenkinson FD from 3dvolreg's *.affmat12.1D file from -1Dmatrix_save option

    input: subject ID, rest_number, name of 6 parameter motion correction file (an output of 3dvolreg)
    output: FD_J.1D file
    Assumptions:    1) subject is available in BASE_DIR
    2) 3dvolreg is already performed and the 1D motion parameter and 1D_matrix file file is present in sub?/rest_? called as --->'lfo_mc_affmat.1D'

    '''

    import numpy as np
    import os
    import sys
    import math

    """
    Method to calculate Framewise Displacement (FD) calculations
    (Jenkinson et al., 2002)

    Parameters; in_file : string
    Returns; out_file : string
    NOTE: infile should have one 3dvolreg affine matrix in one row - NOT the motion parameters

    """

    out_file = os.path.join(os.getcwd(), 'FD_J.1D')

    f = open(out_file, 'w')
    #print in_file
    pm_ = np.genfromtxt(in_file)

    pm = np.zeros((pm_.shape[0],pm_.shape[1]+4))
    pm[:,:12]=pm_
    pm[:,12:]=[0.0, 0.0, 0.0, 1.0]

    flag = 0

    #The default radius (as in FSL) of a sphere represents the brain
    rmax = 80.0

    #rigid body transformation matrix
    T_rb_prev = np.matrix(np.eye(4))

    for i in range(0, pm.shape[0]):
	T_rb = np.matrix(pm[i].reshape(4,4)) # making use of the fact that the order of aff12 matrix is "row-by-row"

	if flag == 0:
            flag = 1
            # first timepoint
            print >> f, 0
        else:
            M = np.dot(T_rb, T_rb_prev.I) - np.eye(4)
            A = M[0:3, 0:3]
            b = M[0:3, 3]

            FD_J = math.sqrt((rmax*rmax/5)*np.trace(np.dot(A.T, A)) + np.dot(b.T, b))
            print >> f, '%.8f'%FD_J

        T_rb_prev = T_rb

    f.close()

    return out_file




    """
    Method to calculate Framewise Displacement (FD) calculations
    (Jenkinson et al., 2002)

    Parameters
    ----------
    in_file : string
        movement parameters vector file path

    Returns
    -------
    out_file : string
        Frame -wise displalcement mat
        file path

    """

    '''
    import os
    import numpy as np
    import math

    out_file = os.path.join(os.getcwd(), 'FD_jenkinson.1D')

    f = open(out_file, 'w')

    pm = np.loadtxt(in_file)

    flag = 0

    #The default radius (as in FSL) of a sphere represents the brain
    rmax = 80.0

    #rigid body transformation matrix
    T_rb_prev = np.matrix(np.eye(4))

    for i in range(0, pm.shape[0]):

        t1 = np.matrix([[1,0,0,pm[i][0]], [0,1,0, pm[i][1]], [0,0,1,pm[i][2]], [0,0,0,1]] )
        t2 = np.matrix([[1,0,0,0], [0, math.cos(pm[i][3]), math.sin(pm[i][3]),0], [0, - math.sin(pm[i][3]), math.cos(pm[i][3]), 0], [0,0,0,1]])
        t3 = np.matrix([[math.cos(pm[i][4]), 0, math.sin(pm[i][4]),0], [0,1,0,0], [-math.sin(pm[i][4]), 0, math.cos(pm[i][4]), 0], [0,0,0,1]])
        t4 = np.matrix([[math.cos(pm[i][5]), math.sin(pm[i][5]), 0, 0], [-math.sin(pm[i][5]), math.cos(pm[i][5]), 0, 0], [0,0,1,0], [0,0,0,1]])
        T_rb  = np.dot(np.dot(t1,t2), np.dot(t3,t4))

        if flag == 0:
            flag = 1
            # first timepoint
            print >> f, 0
        else:
            M = np.dot(T_rb, T_rb_prev.I) - np.eye(4)
            A = M[0:3, 0:3]
            b = M[0:3, 3]

            FD_J = math.sqrt((rmax*rmax/5)*np.trace(np.dot(A.T, A)) + np.dot(b.T, b))
            print >> f, '%.4f'%FD_J

        T_rb_prev = T_rb

    f.close()

    return out_file
    '''


def set_frames_in(in_file, threshold, exclude_list):

    """
     Method to Calculate  the frames that are left
     after censoring for scrubbing.

     Parameters
     ----------
     in_file : string
        framewise displacement(FD) file path
     threshold : float
        scrubbing thereshold set in configuration file
     exclude_list : string
        path of file containing sensored timepoints

     Returns
     -------
     out_file : string
        path of file containing remaining uncensored timepoints
    """

    import os
    import numpy as np
    from numpy import loadtxt

    out_file = os.path.join(os.getcwd(), 'frames_in.1D')

    data = loadtxt(in_file)
    #masking zeroth timepoint value as 0, since the mean displacment value for
    #zeroth timepoint cannot be calculated, as there is no timepoint before it
    data[0] = 0

    indices = [i[0] for i in (np.argwhere(data < threshold)).tolist()]

    indx = []
    f = open(exclude_list, 'r')
    line = f.readline()
    if line:
        line = line.strip(',')
        indx = map(int, line.split(","))
    f.close()
    print indx

    if indx:
        indices = list(set(indices) - set(indx))

    f = open(out_file, 'a')

    for idx in indices:
        f.write('%s,' % int(idx))

    f.close()

    return out_file


def gen_motion_parameters(subject_id, scan_id, movement_parameters, max_displacement):
    """
    Method to calculate all the movement parameters

    Parameters
    ----------
    subject_id : string
        subject name or id
    scan_id : string
        scan name or id
    max_displacement : string
        path of file with maximum displacement (in mm) for brain voxels in each volume
    movement_parameters : string
        path of 1D file containing six movement/motion parameters(3 Translation,
        3 Rotations) in different columns (roll pitch yaw dS  dL  dP)

    Returns
    -------
    out_file : string
        path to csv file contianing various motion parameters

    """

    import os
    import numpy as np
    import re

    out_file = os.path.join(os.getcwd(), 'motion_parameters.txt')

    f = open(out_file, 'w')
    #f.write(str(os.getcwd()))   ### work
    print >>f, "Subject,Scan,Mean_Relative_RMS_Displacement," \
        "Max_Relative_RMS_Displacement,Movements_gt_threshold,"\
        "Mean_Relative_Mean_Rotation,Mean_Relative_Maxdisp,Max_Relative_Maxdisp," \
        "Max_Abs_Maxdisp,Max Relative_Roll,Max_Relative_Pitch," \
        "Max_Relative_Yaw,Max_Relative_dS-I,Max_Relative_dL-R," \
        "Max_Relative_dP-A,Mean_Relative_Roll,Mean_Relative_Pitch,Mean_Relative_Yaw," \
        "Mean_Relative_dS-I,Mean_Relative_dL-R,Mean_Relative_dP-A,Max_Abs_Roll," \
        "Max_Abs_Pitch,Max_Abs_Yaw,Max_Abs_dS-I,Max_Abs_dL-R,Max_Abs_dP-A," \
        "Mean_Abs_Roll,Mean_Abs_Pitch,Mean_Abs_Yaw,Mean_Abs_dS-I,Mean_Abs_dL-R,Mean_Abs_dP-A"


    f.write("%s," % (subject_id))
    f.write("%s," % (scan_id))

    arr = np.genfromtxt(movement_parameters)
    arr = arr.T

    ##Relative RMS of translation
    rms = np.sqrt(arr[3]*arr[3] + arr[4]*arr[4] + arr[5]*arr[5])
    diff = np.diff(rms)
    MEANrms = np.mean(abs(diff))
    f.write("%.3f," % (MEANrms))

    #Max Relative RMS Displacement
    MAXrms = np.max(abs(diff))
    f.write("%.3f," % (MAXrms))

    ##NUMBER OF relative RMS movements >0.1mm
    NUMmove = np.sum(abs(diff) > 0.1)
    f.write("%.3f," % (NUMmove))

    ##Mean of mean relative rotation (params 1-3)
    MEANrot = np.mean(np.abs(np.diff((abs(arr[0])+ abs(arr[1])+ abs(arr[2]))/3 ) ) )
    f.write("%.3f," % (MEANrot))

    file = open(max_displacement, 'r')
    lines = file.readlines()
    file.close()
    list1 = []

    #remove any other information aother than matrix from
    #max displacement file. afni adds infomration to the file
    for l in lines:
        if re.match("^\d+?\.\d+?$", l.strip()):
            list1.append(float(l.strip()))

    arr2 = np.array(list1, dtype='float')

    #Mean Relative Maxdisp
    mean = np.mean(np.diff(arr2))
    f.write("%.3f," % (mean))

    #Max Relative Maxdisp
    relMAX = np.max(abs(np.diff(arr2)))
    f.write("%.3f," % (relMAX))

    #Max Abs Maxdisp
    MAX= np.max(arr2)
    f.write("%.3f," %(MAX))

    #Max Relative Roll,Max Relative Pitch,
    #Max Relative Yaw,Max Relative dS-I,
    #Max Relative dL-R,Max Relative dP-A
    for i in range(6):
        f.write("%.6f," %(np.max(abs(np.diff(arr[i])))))

    #Mean Relative Roll,Mean Relative Pitch,
    #Mean Relative Yaw,Mean Relative dS-I,
    #Mean Relative dL-R,Mean Relative dP-A
    for i in range(6):
        f.write("%.6f," %(np.mean(np.diff(arr[i]))))

    #Max Abs Roll,Max Abs Pitch,Max Abs Yaw,
    #Max Abs dS-I,Max Abs dL-R,Max Abs dP-A
    for i in range(6):
        f.write("%.6f," %(np.max(abs(arr[i]))))

    #Mean Abs Roll,Mean Abs Pitch,Mean Abs Yaw,
    #Mean Abs dS-I,Mean Abs dL-R,Mean Abs dP-A
    for i in range(6):
        f.write("%.6f," %(np.mean(abs(arr[i]))))

    f.close()
    return out_file


def gen_power_parameters(subject_id, scan_id, FDP_1D, FDJ_1D, DVARS, \
                             threshold = 1.0):

    """
    Method to generate Power parameters for scrubbing

    Parameters
    ----------
    subject_id : string
        subject name or id
    scan_id : string
        scan name or id
    FD_ID: string
        framewise displacement(FD as per power et al., 2012) file path
    FDJ_ID: string
        framewise displacement(FD as per jenkinson et al., 2002) file path
    threshold : float
        scrubbing threshold set in the configuration
        by default the value is set to 1.0
    DVARS : string
        path to numpy file containing DVARS

    Returns
    -------
    out_file : string (csv file)
        path to csv file containing all the pow parameters
    """

    import os
    import numpy as np
    from numpy import loadtxt

    powersFD_data = loadtxt(FDP_1D)
    jenkFD_data = loadtxt(FDJ_1D)

    #Mean (across time/frames) of the absolute values
    #for Framewise Displacement (FD)
    meanFD_Power  = np.mean(powersFD_data)

    #Mean FD Jenkinson
    meanFD_Jenkinson = np.mean(jenkFD_data)

    #Number of frames (time points) where movement
    #(FD) exceeded threshold
    numFD = float(jenkFD_data[jenkFD_data > threshold].size)

    #Root mean square (RMS; across time/frames)
    #of the absolute values for FD
    rmsFD = np.sqrt(np.mean(jenkFD_data))

    #Mean of the top quartile of FD is $FDquartile
    quat=int(len(jenkFD_data)/4)
    FDquartile=np.mean(np.sort(jenkFD_data)[::-1][:quat])

    ##NUMBER OF FRAMES >threshold FD as percentage of total num frames
    count = np.float(jenkFD_data[jenkFD_data>threshold].size)
    percentFD = (count*100/(len(jenkFD_data)+1))

    #Mean DVARS
    meanDVARS = np.mean(np.load(DVARS))


    out_file = os.path.join(os.getcwd(), 'pow_params.txt')

    with open(out_file,'w') as f:

        print >>f, "Subject,Scan,MeanFD_Power,MeanFD_Jenkinson," \
        "NumFD_greater_than_%.2f,rootMeanSquareFD,FDquartile(top1/4thFD)," \
        "PercentFD_greater_than_%.2f,MeanDVARS" % (threshold,threshold)

        f.write("%s," % subject_id)
        f.write("%s," % scan_id)
        f.write('%.4f,' % meanFD_Power)
        f.write('%.4f,' % meanFD_Jenkinson)
        f.write('%.4f,' % numFD)
        f.write('%.4f,' % rmsFD)
        f.write('%.4f,' % FDquartile)
        f.write('%.4f,' % percentFD)
        f.write('%.4f' % meanDVARS)
    return out_file


def calculate_DVARS(rest, mask):
    """
    Method to calculate DVARS as per
    power's method

    Parameters
    ----------
    rest : string (nifti file)
        path to motion correct functional data
    mask : string (nifti file)
        path to brain only mask for functional data

    Returns
    -------
    out_file : string (numpy mat file)
        path to file containing  array of DVARS
        calculation for each voxel
    """

    import numpy as np
    import nibabel as nib
    import os

    out_file = os.path.join(os.getcwd(), 'DVARS.npy')

    rest_data = nib.load(rest).get_data().astype(np.float32)
    mask_data = nib.load(mask).get_data().astype('bool')

    #square of relative intensity value for each voxel across
    #every timepoint
    data = np.square(np.diff(rest_data, axis = 3))
    #applying mask, getting the data in the brain only
    data = data[mask_data]
    #square root and mean across all timepoints inside mask
    DVARS = np.sqrt(np.mean(data, axis=0))


    np.save(out_file, DVARS)

    return out_file


