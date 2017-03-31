__author__ = 'kanaan'


import os
from variables.subject_list import *


def thick2surf(population, fsdir):
    for subject in population:

        os.system('sh /scr/sambesi1/workspace/Projects/Tourettome/thick2surf.sh %s %s %s %s %s'
                  %(subject,
                    os.path.join(fsdir, subject),
                    '20',  # FWHM
                    os.path.join(fsdir, 'CT'),
                    '5'  # FSAVERAGE5
                    ))



thick2surf(tourettome_subjects,
           tourettome_freesurfer)