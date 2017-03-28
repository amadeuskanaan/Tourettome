__author__ = 'kanaan.. 25.03.2017'

import os

# os.system('python 000_get_data.py       && '
#           'python 001_preproc_anat.py   && '
#           'python 003_kelly_kapowski.py && '
#           'python 004_preproc_func.py   && '
#           'python 005_transform.py      && '
#           'python 006_denoise.py           ')


def run_tourettome_pipeline():
    os.system('start /wait python 003_kelly_kapowski.py')
    os.system('start /wait python 004_preproc_func.py')

run_tourettome_pipeline()