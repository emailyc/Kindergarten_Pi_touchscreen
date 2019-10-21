#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 15:58:08 2019

@author: chung
"""
import numpy as np;
import random, os;
from psychopy import core, visual, event, gui, data;
#from psychopy.tools.monitorunittools import posToPix;
from psychopy.tools.filetools import fromFile, toFile;
from typing import NewType;
from itertools import count;
import traceback
import logging


try:  # try to get a previous parameters file
    expInfo = fromFile('lastParams.pickle');
except:  # if not there then use a default set
    expInfo = {'experimenter':'chung', 'school': 'cuhk', 'participant':0};
expInfo['dateStr'] = data.getDateStr();  # add the current time

# present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='English vocab-image classification', fixed=['dateStr']);
if dlg.OK:
    #toFile('lastParams.pickle', expInfo)  # save params to file for next time
    pass;
else:
    core.quit();  # the user hit cancel so exit
    
# make a text file to save data
fileName = expInfo['experimenter'] + "_" + expInfo['school'] + "_" + str(expInfo['participant']) + "_" + expInfo['dateStr'] + "_" ;
dataDirectory = "data"
dataFile = open(os.path.join(dataDirectory, fileName + "dataFile" + '.csv'), 'w');  # a simple text file with 'comma-separated-values'
dataFile.write('trial,imageName,targetName,correct,trialFlip,globalFlip\n');

#Some global constants
width_pix = 800;
height_pix = 480;
frame_per_sec = 60;

#A global count of number of frames since the beginning of the very first trial
global_flip_count = count(1);


def checkSize(image: visual.ImageStim) -> bool:
    """ Returns whether the image is within certain dimention (in pixel).

    Parameters:
        image (visual.ImageStim):A visual.ImageStim object with image path defined.

    Returns:
        bool:Whether the image attached to the visual.ImageStim is within certain size (in pixel).   

    """
    
    try:
        if (image.size[0] > 360) or (image.size[1] > 300):
            return True;
        else:
            return False
    except TypeError as e:
        print(e);
        dataFile.write("could check image dimention" + "\n" );
        staircase.saveAsText(os.path.join(dataDirectory, fileName + "staircaseFile" + "_error"), delim = ",");
        myDlg = gui.Dlg(title='Error Checking Image Dimention');
        myDlg.addText('either image path not yet assigned or image cannot be found');
        ok_data = myDlg.show();  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # or if ok_data is not None
            print(ok_data)
        else:
            print('user cancelled')
        core.quit();    
               

def myFlip(window: visual.Window) -> None:
    """ Flip the window and increast the gobal fram count by 1.

    Parameters:
        window (visual.Window):A visual.Window object to be flipped.

    Returns:
        global_frames (int):Number of frames passed since inception of experiment.   

    """
    
    global_frames = next(global_flip_count);
    window.flip();
    return global_frames

# Create a window
win = visual.Window([width_pix, height_pix], monitor="pi7inch", fullscr=0);
mouse = event.Mouse(visible = True, win = win);

#load image
dog_path = os.path.join(os.getcwd(), r"dogs-cats-images/dog vs cat/dataset/test_set/dogs");
cat_path = os.path.join(os.getcwd(), r"dogs-cats-images/dog vs cat/dataset/test_set/cats");

#os.path.join(os.getcwd(), dog_path)

# Create a stimulus for a certain window
Instruction = visual.TextStim(win, units = "pix", pos=(400.0, 200.0));
Stim_Left = visual.ImageStim(win, units = "pix", pos=(-200.0, 0.0));
Stim_Right = visual.ImageStim(win, units = "pix", pos=(200.0, 0.0));

# Create a stimulus for feedback message
Feedback = visual.TextStim(win, text="empty", units = "pix", pos=(400, 0.0));

#fixation
Fixation = visual.GratingStim(win, color=-1, colorSpace='rgb', 
                              tex=None, mask='cross', size=0.1);

                              

staircase = data.StairHandler(startVal = 10.0,
                          stepType = 'db', stepSizes=1,#[8,4,4,2],
                          nUp=1, nDown=1,  # will home in on the 80% threshold
                          nTrials=1);


for trial in range(10):

    
    #randomly choose a dog image
    dog_file_name = random.choice(os.listdir(dog_path))
    dog_image = os.path.join(dog_path, dog_file_name);
    #randomly choose a cat image
    cat_file_name = random.choice(os.listdir(cat_path))
    cat_image = os.path.join(cat_path, cat_file_name);
    animal_images = {"cat": cat_image, "dog": dog_image};
    
    #randomly pick correct answer
    choice = random.choice(["cat", "dog"]);
    target_animal_name = choice;
    target_animal_path = animal_images[choice];
    
    #update instruction
    Instruction.text = "Click the " + target_animal_name + "!";
    
    #randomlyt assign image position
    animal_keys = list(animal_images.keys());
    random.shuffle(animal_keys);
    left_image_animal = animal_keys[0];
    left_image_path = animal_images[left_image_animal];
    right_image_animal = animal_keys[1];
    right_image_path = animal_images[right_image_animal];
    
    #update stimulus
    Stim_Left.image, Stim_Left.name = left_image_path, left_image_animal;
    Stim_Right.image, Stim_Right.name = right_image_path, right_image_animal;
        
    try:
        #resize stimulus
        while checkSize(Stim_Left):
            Stim_Left.size = Stim_Left.size * 0.9;
        
        while checkSize(Stim_Right):
            Stim_Right.size = Stim_Right.size * 0.9;
        
        
        # Pause 5 s, so you get a chance to see it!
        #event.waitKeys()
        
            
        #Use refresh rate to time response time
        trial_flip_count = count(1);
        
        # get response
        thisResp = None;
        while thisResp == None:
    
            # Draw the stimulus to the window. We always draw at the back buffer of the window.
            Fixation.draw();
            Stim_Left.draw();
            Stim_Right.draw();
            Instruction.draw();
            
            #update the number of frame passed
            trial_frames = next(trial_flip_count);
            
            # Flip window to update stimulus.
            global_frames = myFlip(win);
            
            if mouse.isPressedIn(Stim_Left):
                if (Stim_Left.name == target_animal_name):
                    Feedback.text = "Correct!";
                    thisResp = 1;
                else:    
                    Feedback.text = "Incorrect!";
                    thisResp = -1;
            if mouse.isPressedIn(Stim_Right):
                if (Stim_Right.name == target_animal_name):
                    Feedback.text = "Correct!";
                    thisResp = 1;
                else:    
                    Feedback.text = "Incorrect!";
                    thisResp = -1;
        
            event.clearEvents();  # clear other (eg mouse) events - they clog the buffer
        
        # add the data to the staircase so it can calculate the next level
        #staircase.addData(thisResp);
        dataToPrint = f"{str(trial)},{os.path.basename(target_animal_path)},{target_animal_name},{str(thisResp)},{str(trial_frames)},{str(global_frames)}\n"
        print(dataToPrint)
        dataFile.write(dataToPrint );
        
        #show feedback
        for _ in range(frame_per_sec):           
            Feedback.draw();
            myFlip(win);  
            
    except Exception as e:
        # Logs the error appropriately.
        logging.error(traceback.format_exc())
        
        # Close the window
        win.close();
        
        # Close PsychoPy
        core.quit();
            

# staircase has ended
dataFile.close();
#staircase.saveAsText(os.path.join(dataDirectory, fileName + "staircaseFile"), delim = ",");  # special python binary file to save all the info

        
# Close the window
win.close();

# Close PsychoPy
core.quit();
    