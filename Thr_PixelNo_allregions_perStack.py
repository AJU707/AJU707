# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 15:45:01 2021

This script is to threshold z-stack images of one fluorophore and count the number of thresholded pixels per z stack.
The numbers of thresholded pixels are normalized to the average number of thresholded pixels from the BLA of each animal.
At the end of this script, you will have a bar plot (+SEM error bar) combined with scatter plot as svg format and an excel file with all data saved.

In the working directory, save this script and make subfolders of each animal (subfolder name by animal ID (e.g. M988)) to save original image files (z-stack) of eYFP (e.g. file name: M988_BLA_eYFP.tif) or Syp-mCherry (e.g. file name: M988_BLA_mCherry.tif) from all downstream regions.

*** Please modify the lists of animal ID (in line 27), brain regions (in line 28), and fluorophore (in line 29).***
*** Please modify 'thr_value' parameter. Put your own threshold value here.***

During analysis, the animal ID and brain region will be written in console to show the status of analysis. If you don't want, make line 70 (print(id,region, i)) as comment.

@author: Anes Ju
"""

import numpy as np
from skimage import io
import pandas as pd
from os import path
from matplotlib import rc
import matplotlib.pyplot as plt
from scipy import stats as stat

# Please define animal ID, brain regions and fluorophore
animal_id = ['M988','M989','F992']
brain_regions = ['ICa','ICp','ContraICa','ContraICp','PrL','IL','AcbC','LAcbSh','BLA','CeM','CeL','LHp']
fluorophore = 'mCherry'

directory = path.dirname(path.abspath(__file__))

data_dict = {}
BLA_dict ={}

# Get the average value from BLA data of each animal and keep it in BLA_dict as a dictionary form
for id in animal_id:
    if 'M' in id:
        thr_value = 0.35
    else:
        thr_value = 0.40
        
    image_name = r'%s\%s\%s_%s_%s.tif'%(directory, id, id, 'BLA', fluorophore)
    image_array = io.imread(image_name)
    image_std = (image_array/4095).flatten()
    image_thr = np.where(image_std > thr_value, 1, 0) # Thresholding       
    BLA_dict[id] = image_thr.sum(axis = None)    
    
# Get the thresholded data from all brain region data of all animal and draw a bar graph (+SEM) combined with scatter plot.
for region in brain_regions:
    a = []
    for id in animal_id:        
            # Set the thresholding value
        if 'M' in id:
            thr_value = 0.35
        else:
            thr_value = 0.40
        
        image_name = r'%s\%s\%s_%s_%s.tif'%(directory, id, id, region, fluorophore)
        image_array = io.imread(image_name)
        image_array_std = image_array/4095 # Standardization
        
        # Read an image per stack and get the number of thresholded pixel per stack
        for i in range(30):
            image = image_array_std[i::]            
            image_thr = np.where(image > thr_value, 1, 0) # Thresholding       
            image_pixel_no = image_thr.sum(axis = None)/BLA_dict[id] # Total number of pixels after thresholding per stack norm. to BLA
            a.append(image_pixel_no)
            print(id,region, i) # To show the status of analysis in console
            
    avg = np.average(a)
    sem_ = stat.sem(a)
    
    regions = list([region for i in range(len(a))])
    plt.bar(region,avg,yerr=sem_,capsize=3, alpha=.5)
    plt.scatter(regions, a, s=0.7)
        
    data_dict[region] = a

plt.xticks(rotation=45)
plt.ylabel('%s intensity norm. to BLA'%(fluorophore))
rc('font', **{'family':'Arial'})
plt.savefig('%s_all stacks.svg'%(fluorophore), format = 'svg')
plt.show()

# Save data to an excel file
df = pd.DataFrame.from_dict(data_dict)
excel_file = '%s_allStacks.xlsx'%(fluorophore)
df_write = pd.ExcelWriter(excel_file, engine='xlsxwriter')
df.to_excel(df_write, sheet_name = 'Sheet1')
df_write.save()