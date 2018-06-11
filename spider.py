# This file generated by GenerateAutoSpider
from dax import AutoSpider

name = 'FS6'

exe_lang = 'bash'

inputs = [
    ("t1_nifti", "FILE", "T1 NIFTI image(s)", ""),
    ("brainmask", "FILE", "Edited brainmask image file", "F"),
    ("control", "FILE", "Edited control points file", "F"),
    ("wm", "FILE", "Edited wm image file", "F"),
    ("aseg", "FILE", "Edited aseg image file", "F")]

outputs = [
    ("stats.txt", "FILE", "STATS", "FreeSurfer stats"),
    ("report.pdf", "FILE", "PDF", "QA report"),
    ("Subjects/*", "DIR", "DATA", "Output of FreeSurfer recon-all")
]

code = r"""#!/bin/bash

# Make directories
mkdir ${temp_dir}/Subjects

# Freesurfer Setup
export FREESURFER_HOME=/opt/freesurfer
source $$FREESURFER_HOME/SetUpFreeSurfer.sh

# Run FreeSurfer init
inputs=${t1_nifti}
inputs=$${inputs//,/\ -i }
recon-all \
-sd ${temp_dir}/Subjects \
-s ${assessor_label} \
-i $$inputs

# Add FreeSurfer edits if any
if [[ "${brainmask}" && "${brainmask}" != "None" ]]; then
   echo "Copying brainmask"
   cp "${brainmask}" ${temp_dir}/Subjects/${assessor_label}/mri/brainmask.mgz
fi

if [[ "${wm}" && "${wm}" != "None" ]]; then
   echo "Copying wm"
   cp "${wm}" ${temp_dir}/Subjects/${assessor_label}/mri/wm.mgz
fi

if [[ "${aseg}" && "${aseg}" != "None" ]]; then
   echo "Copying aseg"
   cp "${aseg}" ${temp_dir}/Subjects/${assessor_label}/mri/aseg.mgz
fi

if [[ "${control}" && "${control}" != "None" ]]; then
   echo "Copying control"
   mkdir -p ${temp_dir}/Subjects/${assessor_label}/tmp/
   cp "${control}" ${temp_dir}/Subjects/${assessor_label}/tmp/control.dat
fi
   
# Run the recon including hippo subfields
export WRITE_POSTERIORS=1
recon-all \
-sd ${temp_dir}/Subjects \
-s ${assessor_label} \
-all \
-qcache \
-hippocampal-subfields-T1

# Unlink average brains so they don't get uploaded
if [ -e ${temp_dir}/Subjects/fsaverage ]; then
    unlink ${temp_dir}/Subjects/fsaverage
fi
if [ -e ${temp_dir}/Subjects/lh.EC_average ]; then
    unlink ${temp_dir}/Subjects/lh.EC_average
fi
if [ -e ${temp_dir}/Subjects/rh.EC_average ]; then
    unlink ${temp_dir}/Subjects/rh.EC_average
fi

# Create QA PDFs
cd ${temp_dir}/Subjects/${assessor_label} && \
xvfb-run -e xvfb.err -f xvfb.auth --wait=5 -a \
--server-args "-screen 0 1920x1080x24" \
make_screenshots.sh

mv ${temp_dir}/Subjects/${assessor_label}/all.pdf ${temp_dir}/report.pdf

# Create stats file
export SUBJECTS_DIR=${temp_dir}/Subjects
python -c "from recon_stats import Subject;\
s = Subject('${assessor_label}');s.get_measures();\
s.write('${temp_dir}/stats.txt')"
"""

if __name__ == '__main__':
    spider = AutoSpider(
        name,
        inputs,
        outputs,
        code,
        exe_lang=exe_lang,
    )

    spider.go()
