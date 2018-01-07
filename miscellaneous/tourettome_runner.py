__author__ = 'kanaan.. 25.03.2017'

import os

# os.system('python 000_check_raw_data.py       && '
#           'python 001_anat_preproc.py   && '
#           'python 003_kelly_kapowski.py && '
#           'python 003_func_preproc.py   && '
#           'python 004_transform.py      && '
#           'python 005_func_denoise.py           ')


def run_tourettome_pipeline():
    os.system('start /wait python 003_kelly_kapowski.py')
    os.system('start /wait python 003_func_preproc.py')

run_tourettome_pipeline()