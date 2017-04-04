#!/bin/bash

print_help()
{
	echo 
	echo "./$0 <CASE> <FSDIR> <PREFIX> <FWHM> <ODIR> <ICO>"
	echo 
}

#########################################################################
# input handling
if [ $# -lt 5 ]
then	
	echo "Not enough arguments"
	print_help
	exit
fi
CASE=${1}
FSDIR=${2}
FWHM=${3}
ODIR=${4}
ICO=${5}
#########################################################################


FSUB=`basename ${FSDIR}`
SUBJECTS_DIR=`dirname ${FSDIR}`

mri_surf2surf \
	--s ${FSUB} \
	--sval ${SUBJECTS_DIR}/${FSUB}/surf/lh.thickness \
	--trgsubject fsaverage${ICO} \
	--tval ${ODIR}/${CASE}_lh2fsaverage${ICO}_${FWHM}.mgh \
	--fwhm-src ${FWHM} \
	--hemi lh \
	--cortex \
	--noreshape
			
mri_surf2surf \
	--s ${FSUB} \
	--sval ${SUBJECTS_DIR}/${FSUB}/surf/rh.thickness \
	--trgsubject fsaverage${ICO} \
	--tval ${ODIR}/${CASE}_rh2fsaverage${ICO}_${FWHM}.mgh \
	--fwhm-src ${FWHM} \
	--hemi rh \
	--cortex \
	--noreshape

