__author__ = 'kanaan.. 25.03.2017'

import os


os.system('python 000_data_data.py      && '
          'python 001_preproc_anat.py   && '
          'python 003_kelly_kapowski.py && '
          'python 004_preproc_func.py   && '
          'python 005_transform.py         ')

