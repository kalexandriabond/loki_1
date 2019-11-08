Screen('Preference', 'SkipSyncTests', 1)

%%%   FFA/LOC/PPA LOCALIZER: FFALOCLocal     %%%
%%%                                          %%%   
%%%     modified from localizers from AN & JP%%%
%%%                                          %%%
%%%  11/17/09: Wrote it. (JP)
%%%  2/23/11: Modified from FFALocal.m (JP)
%%%  8/4/11: Changed houses to Scenes. (JP)  
%%%  2/24/12: Modified out2put/bg color (DM)
%%%  6/27/12: Modified fixation at start and filename. Added EBA. General
%%%  updates.
%%%  7/21/17: Updated to System76 keycode and fixed cap issues. (JP)
%%%  8/1/19: Updated to run at Mellon scanner. Removed EBA. (AW)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Initialize %%
clear; clc;
rand('state', sum(clock*100));
%% Get Subject Info %%
prompt={'CoAx ID (e.g. 0999)', 'TR Length (in ms)', 'At Scanner? Yes=1, No=0', ...
    'Order: Order1=1, Order2=0','Session Number (e.g. 01)','Run Number (e.g. 01)',};
def={'','2000','1','1','', ''};
title='SETUP FFA/LOC/PPA/EBA LOCALIZER...';
lineNo=1;
answer=inputdlg(prompt,title,lineNo,def);
SubjID = char(answer(1,:));
TRtime = str2num(char(answer(2,:)));
atscanner = str2num(char(answer(3,:)));
PickCond = str2num(char(answer(4,:)));
sesnumber = str2num(char(answer(5,:)));
runnumber = str2num(char(answer(6,:)));

scanstart = fix(clock);

%% Create SubjData folder if there isn't one already, then assign filenames

% if ~exist('SubjData','dir')
%     mkdir('SubjData');
% end

subj_dir = strcat('../../data/BIDS/sub-', SubjID, '/ses-', num2str(sesnumber), '/func');
if ~exist(subj_dir,'dir')
    mkdir(subj_dir);
end

DataFileName = strcat(subj_dir,'/sub-', SubjID, '_ses-0', num2str(sesnumber), 'task-localizer_run-0', num2str(runnumber), '_events' ,num2str(scanstart(4)), '.txt');
MatFileName = strcat(subj_dir, '/sub-', SubjID, '_ses-0', num2str(sesnumber), 'task-localizer_run-0', num2str(runnumber), '_events' ,num2str(scanstart(4)));

% MatFileName = strcat('SubjData/',SubjID, '_Run',num2str(runnumber), '_FFALOCPPAEBALocal_',num2str(scanstart(4)),num2str(scanstart(5)));


%% PsychToolbox Setup %%
%need this for some of the os x things?
AssertOpenGL;
%choose the display screen (needed if multiple monitors attached)
screenNumber = max(Screen('Screens'));
% Setup Button Box Keys (for BIRC Allegra)
if atscanner
        key1=31; %corr to the Yellow key
        key2=30;
else        
        key1=31;
        key2=30;
end

HideCursor;
% esc_key = KbName('escape'); %this key kills script during the experimet
esc_key = 20;

black=BlackIndex(screenNumber); %bkgd color for the inst will be black
gray=GrayIndex(screenNumber); %bkgd color for experiment will be gray
bkgdColor = gray;
textColor = black;
w=Screen('OpenWindow', screenNumber);
ifi = Screen('GetFlipInterval', w);
slack = ifi / 2;

%get / display screen 
Screen(w,'FillRect', gray);%gray
%always writes to an offscreen buffer window � flip to see changes  made
Screen('Flip', w);
% set font; display text
Screen('TextFont',w, 'Times');
Screen('TextSize',w, 18);
%Screen('TextStyle', w, 0);
DrawFormattedText(w, 'Preloading images...', 'center', 'center', black);
Screen('Flip', w);



%% Load Stimuli %%
load faces;
load objects;
load scramobjects;
load scenes;
% load bodyparts;

%% Setup Fixation Cross %%
fixation_dark=repmat(gray,30,30);
fixation_dark(13:16,:)=0;
fixation_dark(:,13:16)=0;

%% Scan & Experiment Parameters %%
TR = 2.0; 

NumBlocks = 15; %% 3 repetitions of 4 conditions
totalOffBlocks = 12;

TRsPerBlock = 8;
FixTRs = 3;
StimsPerBlock = 16;
trialDuration = 1;
stimPresentationLength = 0.8; %0.75;
BlockLength = TR * TRsPerBlock;
FixLength = TR * FixTRs;
StartFixTime = 12;
EndFixTime = 6;
[junk junk junk NumStims] = size(faces);
ITI = trialDuration - stimPresentationLength; 
TasksPerBlock = 2;


%% Condition Orders
% 1=Faces, 2=Objects, 3=Scenes, 4=Scrambled Objects 5=Bodyparts
if PickCond == 1 
        CondOrder = [1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4];
    else	
        CondOrder = [2, 4, 1, 3, 2, 4, 1, 3, 2, 4, 1, 3];
end	%if stimtype


%% Create matrix for trial order and Shuffle
%trialMatrix = zeros(NumStims,NumBlocks);  
temp = 1:NumStims;
FaceStimOrder = Shuffle(temp);
ObjectStimOrder = Shuffle(temp);
SceneStimOrder = Shuffle(temp);
ScrambledStimOrder = Shuffle(temp);
% BodypartStimOrder = Shuffle(temp);

FaceTrial = 1;
ObjectTrial = 1;
SceneTrial = 1;
ScrambledTrial = 1;
% BodypartTrial = 1;


% for i = 1:NumBlocks
%     trialMatrix(:,i) = temp;
% end;
% trialMatrix = Shuffle(trialMatrix);


%% Create matrix for Task and Shuffle
Matrix = zeros(StimsPerBlock,NumBlocks);  
Matrix(1:TasksPerBlock,:) = 1;
TaskMatrix = Shuffle(Matrix);

%Make sure there are no task trials back to back  (2 tasks per block
%hard-coded)
for i = 1:NumBlocks
    
    taskind = find(TaskMatrix(:,i));
    disttask = diff(taskind); 
    
    while disttask == 1 | TaskMatrix(1,i) == 1
        reshuffle = Shuffle(TaskMatrix(:,i));
        TaskMatrix(:,i) = reshuffle;       
        taskind = find(TaskMatrix(:,i));
        disttask = diff(taskind); 
    end %while  
        
end



%% Setup Datafile %%
datafile = fopen(DataFileName,'wt');
fprintf(datafile,'%s \n','<><><><><><><><>');
fprintf(datafile,'%s \n','FFA/LOC/PPA LOCALIZER');
fprintf(datafile,'%s %s \n','Matlab version ', version);
fprintf(datafile,'%s %s \n','Begin:', datestr(now));
fprintf(datafile,'%s %s \n','SubjID:', SubjID);
fprintf(datafile,'%s %i \n','Run Number:', runnumber);
fprintf(datafile,'%s %f \n','TR:', TR);

fprintf(datafile,'%s %i \n','Total Blocks:', NumBlocks);

%fprintf(datafile,'%s %i \n','Total Number of Volumes acquired (#TR):', totalNumOfTR);
fprintf(datafile,'%s \n','<><><><><><><><>');    

fprintf(datafile,'%s \n','<><><><><><><><>');
fprintf(datafile,'%s %s \n','Script Start :: ', datestr(now));

fprintf(datafile,'%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n', 'Trial No.', 'Block', 'Face(1)/Object(2)/Scenes(3)/Scrambled(4)', 'Trial', 'TR','Stim No.', 'Presentation Time(s)', 'StimEndTime(s)', 'TrialEndTime(s)', 'Response', 'Correct?', 'RT(ms)');
fprintf(datafile,'%s\n','<><><><><><><><>');


%% Show Instructions %%
inst_horzpos=50;
top_vertpos=100;
inst_vertpos=40;
inst_color=textColor;

Screen('FillRect', w, bkgdColor);
Screen('TextFont',w, 'Arial');
Screen('TextSize',w, 24);
%0=normal,1=bold,2=italic,4=underline,8=outline,32=condense,64=extend
%Screen('TextStyle', w);

DrawFormattedText(w, 'Concentrate on dispaly.\nPush button when image repeats.', 'center', 'center', black);
Screen('Flip', w);


% wait 4 seconds before switching to fixation
WaitSecs(4);

Screen('PutImage', w, fixation_dark);
Screen('Flip', w); %show offscreen buffer that has fixation


%% Set Things Up %%
FlushEvents('keyDown');
%stimtype = FirstCond;  %Faces = 1, Object = 0
samediff = 0;
TrialCount = 1;

%% Suppress Keyboard Output to Command Window
ListenChar(2);

%% Wait for Trigger %%  
    if atscanner == 1
        keyCodes(1:256) = 0;
        while keyCodes(34)==0  %34 is keyCode for Mellon Scanner
              [keyPressed, secs, keyCodes] = KbCheck;
        end
    else KbWait
    end
    
    Screen('PutImage', w, fixation_dark);
    Screen('Flip', w); %show offscreen buffer that has fixation


%%% Get Start Time %%%
ExptStartTime = GetSecs;

fprintf(sprintf('\n\n GOT SYNC! EXPERIMENT STARTED!'));

%% Wait For Initial Fixation Time %%
WaitSecs(StartFixTime);

%%%%%%%%%%%%%%%%%%%%%%%
%% MAIN PROGRAM LOOP %%
%%%%%%%%%%%%%%%%%%%%%%%

for block = 1:NumBlocks
   
	for trial = 1:StimsPerBlock
        
		samediff = TaskMatrix(trial, block);

        %% For first stim in the block or a new stim (samediff=0) %%
		if samediff == 0
            %% Get pict from pick %%
            if CondOrder(block) == 1 %faces
                    pick = FaceStimOrder(FaceTrial);
                    pict = faces(:, :, :, pick);
                    FaceTrial = FaceTrial+1;
            elseif CondOrder(block) == 2 %objects
                    pick = ObjectStimOrder(ObjectTrial);
                    pict = objects(:, :, :, pick);
                    ObjectTrial = ObjectTrial+1;
            elseif CondOrder(block) == 3 %scenes	
                    pick = SceneStimOrder(SceneTrial);
                    pict = scenes(:, :, :, pick);
                    SceneTrial = SceneTrial+1;
%             elseif CondOrder(block) == 4 %scrambled objects
            else %scrambled objects
                    pick = ScrambledStimOrder(ScrambledTrial);
                    pict = scramobjects(:, :, :, pick);
                    ScrambledTrial = ScrambledTrial+1;
%             else    %bodyparts
%                     pick = BodypartStimOrder(BodypartTrial);
%                     pict = bodyparts(:, :, :, pick);
%                     BodypartTrial = BodypartTrial+1;                   
            end	%if stimtype
  		end %if stim
            
        %% Copy pict to the window %%
        Screen('PutImage', w, pict);
            
        
	    %% Figure out time for Trial %%
        StimEndTime = ExptStartTime + StartFixTime + ((block-1)*(BlockLength+FixLength)) ...
            + (trial * trialDuration) - ITI - slack;
        TrialEndTime = StimEndTime + ITI;
       
        %% Setup Response Stuff %%
        accuracy = 0;
        rt=0;
        keyCodes(1:256) = 0;       
        
        %% Show Stimulus %%
        trcount= round((GetSecs-ExptStartTime)/2);
        PresTime = Screen('Flip', w);
       
        %% Wait for Button Press %%
        while (GetSecs < StimEndTime)
          if sum(double(keyCodes(key1)))==0
                [keyPressed, secs, keyCodes] = KbCheck;
          end
        end

        %% Show Blank for ITI %%
        Screen(w,'FillRect', gray);
        Screen('Flip', w);
        
        %% Wait for Button Press %%
        while (GetSecs < StimEndTime)
          if sum(double(keyCodes(key1)))==0
                [keyPressed, secs, keyCodes] = KbCheck;
          end
        end
         
        
        %% Figure Correct Key %%
        if keyCodes(key1)
            resp=1; %same
        elseif keyCodes(key2)
            resp=0; %different
        else double(keyCodes(key1))+ double(keyCodes(key2))~=1;
            resp=-1;
        end
                 
        if samediff == 0
            correctkey = -1;
        else
            correctkey = 1;
        end
        
        
        %% Record Response Info %%
        accuracy =(resp==correctkey);
        rt = (secs-PresTime)*1000;

        %% Record end of Trial time %%
        end_time_trial = GetSecs; 
        PresTime=PresTime-ExptStartTime;
        StimEndTime=StimEndTime-ExptStartTime;
        TrialEndTime=TrialEndTime-ExptStartTime;
        %% Record Data in Matrix %%
        ExptRecord(TrialCount,1) = TrialCount;
        ExptRecord(TrialCount,2) = block;
        ExptRecord(TrialCount,3) = CondOrder(block);
        ExptRecord(TrialCount,4) = trial;
        ExptRecord(TrialCount,5) = trcount;
        ExptRecord(TrialCount,6) = pick ;
        ExptRecord(TrialCount,7) = PresTime;
        ExptRecord(TrialCount,8) = StimEndTime;
        ExptRecord(TrialCount,9) = TrialEndTime;
        ExptRecord(TrialCount,10) = resp;
        ExptRecord(TrialCount,11) = accuracy;
        ExptRecord(TrialCount,12) = rt;
        fprintf(datafile,'%d\t%d\t%d\t%d\t%d\t%d\t%5.2f\t%5.2f\t%5.2f\t%d\t%d\t%5.2f\n', TrialCount, block, CondOrder(block), trial, trcount, pick, PresTime, StimEndTime, TrialEndTime, resp, accuracy, rt);
        
        %% Output to Command Window %%
        TimeNow = GetSecs - ExptStartTime;
        tr_indiv_end= round((GetSecs-ExptStartTime)/2);
        fprintf(sprintf('\nBlock:%d  Trial:%d  Stim:%i Response:%i Accuracy:%i TimeNow:%3.2f TR:%i',block,trial,pick,resp,accuracy,TimeNow,tr_indiv_end));
        
        
        %% Update Count of All Trials
        TrialCount = TrialCount + 1;
        
	end	%for stim		
    
    
    %% Show Fixation Between Blocks %%
    Screen('PutImage', w, fixation_dark);
    Screen('Flip', w); %show offscreen buffer that has fixation
	%% Fixation Period Between Blocks %%
    WaitSecs(FixLength);

    
	
end %for block	

WaitSecs(EndFixTime);

ListenChar(0);
Screen('CloseAll');

clear faces;
clear objects;
clear scenes;
clear scramobjects;

save(MatFileName);







































