# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 15:45:01 2021

This script is to plot an accumulative histogram of fluorescent intensity from all brain regions per animal.

In the working directory, save this script and make subfolders of each animal (subfolder name by animal ID (e.g. M988)) to save original image files (z-stack) of eYFP (e.g. file name: M988_BLA_eYFP.tif) and Syp-mCherry (e.g. file name: M988_BLA_mCherry.tif) from all downstream regions.

*** Please modify the lists of animal ID (in line 20), brain regions (in line 21), and fluorophore (in line 22).***

During analysis, the animal ID and brain region will be written in console to show the status of analysis. If you don't want, make line 37 (print(id, region)) as comment.

@author: Anes JU
"""

import numpy as np
import matplotlib.pyplot as plt
from skimage import io
from os import path

# Please define animal ID, brain regions and fluorophore
animal_id = ['M988','M989','F992']
brain_regions = ['ICa','ICp','ContraICa','ContraICp','PrL','IL','AcbC','LAcbSh','BLA','CeM','CeL','LHp']
fluorophore = 'mCherry'

directory = path.dirname(path.abspath(__file__))

# Open each folder
for id in animal_id:    
    for region in brain_regions:
        image_name = r'%s\%s\%s_%s_%s.tif'%(directory, id, id, region, fluorophore)
        image_array = io.imread(image_name)
        image_array_std = image_array/4095 # Standardization
        
        image = image_array_std.flatten()
        
        print(id, region) # Check the analysis status in console
    
    X = np.sort(image)
    F = np.array(range(4095))/float(4095)
    n, bins, patches = plt.hist(X, F, density=True, histtype='step', cumulative=True, label=id)
    plt.legend(bbox_to_anchor=(1.04,1), loc="upper left")

plt.title('Cumulative step histograms')
plt.xlabel('Standardized fluorescence intensity')
plt.ylabel('Likelihood occurence')
plt.savefig('%s_distplot.svg'%(fluorophore), format = 'svg') 
plt.show()