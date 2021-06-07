# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 13:41:56 2021

This script is to threshold the BLA image, make z-projection and save an image file as jpg format. 
In the working directory, save this script and make subfolders of each animal (subfolder name by animal ID (e.g. M988)) to save original image files (z-stack) of eYFP (e.g. file name: M988_BLA_eYFP.tif) or Syp-mCherry (e.g. file name: M988_BLA_mCherry.tif) from all downstream regions.

***Please modify id (Line 18), fluorephore (Line 19) and thresholding value (Line 20). ***

@author: user
"""
import numpy as np
from skimage import io
from os import path
import matplotlib.pyplot as plt

# Please write id, fluorephore and thresholding value here.
id = 'M988'
fluorophore = 'mCherry'
thr_value = 0.35

directory = path.dirname(path.abspath(__file__))

image_name = r'%s\%s\%s_%s_%s.tif'%(directory, id, id, 'BLA', fluorophore)
image_array = io.imread(image_name)
image_std = image_array/4095
image_thr = np.where(image_std > thr_value, 1, 0) # Thresholding
image_max = np.max(image_thr, axis=0) # Maximal z-projection

plt.imshow(image_max, cmap = 'Greys_r')
plt.axis('off')
plt.savefig('%s_%s_%f.jpg'%(id, fluorophore, thr_value), format='jpg')
plt.show()
