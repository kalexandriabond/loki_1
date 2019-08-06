**TODO before we start data collection**

@ariaaay @kmbond

1) ~~verify that training and test sets of greebles are separated and consistent across our experiments (again, to be sure)~~
2) run through each of our tasks to make sure nothing conflicts with the other (?) {seems fine}
3) make sure that there are the same visuals (window size, greeble size, luminance/contrast issues). {create a dict for the luminance and contrast values as a separate config file} 
4) ~~collate current subject list (IDs)~~
5) recruit remainder of subjects (3)
6) ~~method for coordinating the scheduling of sessions {shared google calendar, can just use calpendo}~~
7) test physio. data collection
8) ~~settle on a numbering convention for sessions (perceptual session is 1? my RL sessions being 2-10, last perc. session is 11?) {one-based indexing}~~
9) ~~develop a procedure for the overall experiment (when to do the criterion tasks, when to do the perceptual tasks, etc.) {update old nb}~~
_ _ _

@kmbond

+ figure out session order for each person for RL task (just random, add the sequence for each person in csv)
+ find best angle for LC using probabilistic LC atlas (right now doing AC/PC, more oblique?)
+ confirm run length for behavioral task < scan run
+ ~~test Eyelink data collection at new position~~
+ confirm 1:1 mapping between position of button press and visual selection (add box to selection and confirm left button press corresponds to left visual selection)
+ ~~ask John to trim the head case for subject 1 (and check for subject 2)~~
+ ~~decide if it's even worth recruiting subject 2? 4 weeks left~~
+ analyze my own pilot data (neuroimaging + behavior)
+ ask Javi when to do the RL task sessions
+ phase encoding issue with flywheel (error). collected both encoding versions. 

+ John: Also, I can’t quite remember from looking at your program today, but after the last screen of instructions you should time out to a fixation cross that the subject can look at before the scan starts. You don’t want instructions still displayed and the fixation to be cued by the MRI trigger because that increases the chance the subject will be moving their eyes during the reference scans collected before the first trigger is sent. During the reference scan is the most important time when the subject should remain still and not move their eyes so they should have a fixation during that period. 

  + Issue for my exp. too? Problem is that the fixation point is the point total. 
