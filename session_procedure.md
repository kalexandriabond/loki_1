

before entering scanner on laptop: 

`conda activate psychopy`

`cd ~/Desktop/loki_1/experimental_scripts/`

`python perceptual_criterion.py`

`python reward_criterion.py`

login to coax lab mac

`source activate psypy2.7`

inside scanner: 

`python luminance_range.py`

`python greeblified_decisions_loki1.py` x 5 runs with calibration and validation at beginning of each run

  * calibrate (c) 
  * validate  (v)
  * record (o) 

after end of session: 

`git add */data/subject*/`

`git commit -m ‘add data for s 8xx session x’ `

`git push`

check for physio + BOLD + structural data on flywheel 
check that behavioral data is uploaded to repo and complete

at end of each week of sessions:

* calculate earnings for the week
* ask participant to complete:
w9 + HSRP form + electronic funds transfer form
* email forms with IRB approval letter to Tisha
* get email endorsement of forms from participant in lieu of physical signature

