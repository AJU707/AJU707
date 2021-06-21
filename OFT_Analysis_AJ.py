# -*- coding: utf-8 -*-
"""
Video analysis of Open Field Test (OFT) by Bonsai & Python

written by Anes Ju, 2021.06.15
modified by Anes Ju, 2021.06.21

This script analyzes all the csv and its video files of elevated plus maze experiments from mice which are listed in excel file in the same directory. 
This script is 

(1) to analyze the time spent (second) and distance travelled (cm) in border and small/large center (small center: 10% of OFT area, large center: 50% of OFT area) in specific time bin you enter (second) for the experimental time
(2) to analyze the time spent (second), distance travelled (cm) and speed (cm/s) in border and small/large center for 05, 10, 15 and 20 minutes (depending on the experimental time)
(3) to draw the trajectory of each mouse for 05, 10, 15 and 20 minutes (depending on the experimental time)

*******
Important information before starting this code

1. In the same working directory, you should have a video file (F835_OFT.avi) and its bonsai file (F835_OFT-bonsai.csv) of each animal and an excel file (OFT_data.xlsx : Should include information with column names; 'Animal no':int, 'Sex':str,'Starting time':int (in sec), 'Group': str) with animal no, sex and the starting time (as second) of video analysis. Please keep the file name as above.

2. In the console, there will be two questions poped up: 
    
    'Please enter how long one session of the experiment takes (in minutes):' --> Please write the experimental time in minutes. Then, press enter key.
    'Please enter the time bin (in second): ' --> Please write the divisor of experimental time (in second) that you entered. Then, press enter key.

3. When the first frame of video pops up, you should click 4 corners of OFT area and enter esc key to close the video.

4. It is important to click the exact coordinates of OFT corners, since the pixel size and the coordinates of small/large center are calculated based on those coordinates.

5. At the end, you will have an excel file with all the data analyzed and the trajectory of each mouse for 05, 10, 15 and 20 minutes (depending on the experimental time).

6. If you want to reanalyze, please check whether you have proper column names and remove previous data in excel file.
*******
Enjoy the analysis!
"""

# Import packages
import pandas as pd
import matplotlib.pyplot as plt
import cv2 as cv
from matplotlib.path import Path
import matplotlib.patches as patches
from matplotlib import rc
from os import path
import numpy as np

def getFirstFrame(vid_cap):
    """
    Read the video file and return the first frame as an image file
    """
    success, image = vid_cap.read()
    if success == 1:
        first_image = image
    return first_image

def onclick(event,x,y,flag,image):
    """
    Get the pixel coordinate of mouse click
    """
    global coords
    if event == cv.EVENT_LBUTTONUP:
        coords.append((x,y))
        # wait for Esc or q key and then exit
        return

def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

def line_intersection(coords):    
    """
    Get the 4 coordinates of OFT corners and return the coordinate of OFT center point
    """    
    xdiff = (coords[0][0] - coords[2][0], coords[1][0] - coords[3][0])
    ydiff = (coords[0][1] - coords[2][1], coords[1][1] - coords[3][1])
    div = det(xdiff, ydiff)
    if div == 0:
       raise Exception('lines do not intersect')
    d = (det(coords[0], coords[2]), det(coords[1], coords[3]))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return [x, y]

def resize_center(coords, factor):
    """
    coords must be clockwise
    how much the coordinates are moved as an absolute value
    """    
    new_coords = []
    intersection = tuple(line_intersection (coords))
    for i in range(len(coords)):        
        new_coords.append(((coords[i][0]-intersection[0])*factor+intersection[0],(coords[i][1]-intersection[1])*factor+intersection[1]))
    return new_coords

def calculate_pixel(coords_list):
    """
    Based on the coordinates of OFT (60cmx60cm), calculate and return the size of pixel
    """
    x_1 = coords_list[0][0]
    y_1 = coords_list[0][1]    
    x_2 = coords_list[1][0]
    y_2 = coords_list[1][1]    
    p = (3600/((x_1-x_2)**2 + (y_1-y_2)**2))**0.5 # size of pixel in centimeter. 3600 means 60x60. Change 3600 depending on the size of OFT
    return p
   
# Define a function to draw/save a graph
def draw_trajectory(bonsai_file, coords_list, animal_no, animal_sex, time, width, height):
    """
    Draw the trajectory of mouse location depending on experimental time and save this graph.
    """    
    # Plot each point
    plt.scatter(bonsai_file['mouseX'], bonsai_file['mouseY'], s=1)       
    # Draw each ROIs
    oft_patch = patches.PathPatch(coords_list[0],edgecolor='yellow',fill=0, lw=2)
    small_ct_patch = patches.PathPatch(coords_list[1],edgecolor='orange',fill=0, lw=2)
    large_ct_patch = patches.PathPatch(coords_list[2],edgecolor='green',fill=0, lw=2)
    
    plt.gca().add_patch(oft_patch)
    plt.gca().add_patch(small_ct_patch)
    plt.gca().add_patch(large_ct_patch)
    
    # Assign the characteristics of the plot
    plt. rcParams["figure.figsize"] = (8,6)
    plt.title("%s%s_OFT_%s"%(animal_sex, animal_no, time))  
    rc('font', **{'family':'Arial'})
    plt.xlim(0, width)
    plt.ylim(0, height)        
    plt.axis('off')
    plt.savefig("%s%s_OFT_%s.jpg"%(animal_sex, animal_no, time), format = 'jpg')
    plt.show()
    return

def calculate_time(bonsai_file, frame_rate, coords_list):    
    """
    Calculate time spent in ROI and return a list of [total time, time spent in small ct, time spent in large ct, time spent out of large ct]. Please take the order of elements into account when you add these values in the data set!!
    """
    x = bonsai_file['mouseX']
    y = bonsai_file['mouseY']
    total_time = 0
    small_ct_time = 0
    large_ct_time = 0
    border_time = 0
        
    for i in bonsai_file.index.values.tolist():
        a = i    
        total_time = total_time+1
        if coords_list[1].contains_point((x[a], y[a])):
            small_ct_time = small_ct_time+1            
        if coords_list[2].contains_point((x[a], y[a])):
            large_ct_time = large_ct_time+1
        else:
            border_time = border_time+1   
    time_small_ct = small_ct_time / frame_rate
    time_large_ct = large_ct_time / frame_rate
    time_border = border_time / frame_rate
    time_total = total_time / frame_rate
    return [time_small_ct, time_large_ct, time_border, time_total]

def calculate_distance(bonsai_file, p, coords_list):
    """
    Calculate time spent in ROI and return a list of [total time, time spent in small ct, time spent in large ct, time spent out of large ct]. Please take the order of elements into account when you add these values in the data set!!
    """
    x = bonsai_file['mouseX']
    y = bonsai_file['mouseY']
    total_dist = []
    small_ct_dist = []
    large_ct_dist = []
    border_dist = []
    
    for i in bonsai_file.index.values.tolist()[:-2]:
        a = i
        b = a+1
        dist = (((x[a] - x[b])*p)**2+((y[a] - y[b])*p)**2)**0.5
        total_dist.append(dist)
        if coords_list[1].contains_point((x[a], y[a])):
            small_ct_dist.append(dist)            
        if coords_list[2].contains_point((x[a], y[a])):
            large_ct_dist.append(dist)
        else:
            border_dist.append(dist)            
    return [np.nansum(small_ct_dist), np.nansum(large_ct_dist), np.nansum(border_dist), np.nansum(total_dist)]


if __name__ == '__main__':
          
    # Get the current directory where the python file exists
    directory = path.dirname(path.abspath(__file__))

    # Take the address of excel file and open it
    excel_file="%s\OFT_data.xlsx"%(directory)
    df = pd.read_excel(excel_file, converters={'Animal no':str,'Sex':str,'Starting time':int}, index_col = 'Animal no')

    # Get all the animal no, sex and starting time
    animal_sex = df['Sex'].to_list()
    animal_no = df.index.to_list()
    starting_time = df['Starting time'].to_list()
    
    # Ask the time bin in sec and get the value in integer format
    total_exp_time_min = int(input('Please enter how long one session of the experiment takes (in minutes):  '))
    total_exp_time_sec = total_exp_time_min*60
    timebin_in_sec = int(input('Please enter the time bin (in seconds):   '))    
        
    # Create the column names depending on the time bin    
    df_columns = ['Timebin']
    for i in range(int(total_exp_time_sec/timebin_in_sec)):
        start = timebin_in_sec * i
        end = timebin_in_sec * (i+1)
        period = '%ss_%ss'%(str(start), str(end))        
        df_columns = df_columns + ['Time_smallCT_%s'%(period), 'Time_largeCT_%s'%(period), 'Time_border_%s'%(period), 'Dist_smallCT_%s'%(period), 'Dist_largeCT_%s'%(period), 'Dist_border_%s'%(period), 'Dist_Total_%s'%(period)]
    
    bin_5min = int(total_exp_time_min/5)
    for i in range(bin_5min):
    
        period = str('%02d'%((i+1)*5))+'min'
        df_columns = df_columns + ['Time_smallCT_%s'%(period), 'Time_largeCT_%s'%(period), 'Time_border_%s'%(period), 'Dist_smallCT_%s'%(period), 'Dist_largeCT_%s'%(period), 'Dist_border_%s'%(period), 'Dist_Total_%s'%(period), 'Speed_smallCT_%s'%(period), 'Speed_largeCT_%s'%(period), 'Speed_border_%s'%(period), 'Speed_Total_%s'%(period)]       

    # Create the new columns with new column names in the dataframe
    df_add = pd.DataFrame(index = animal_no, columns = df_columns)
    df_add = df_add.fillna(0)
    df = pd.concat([df, df_add], axis=1)
    
    # Open each video file and its bonsai file
    for no, sex, time in zip(animal_no, animal_sex, starting_time):
        anim_no=str(no)
        anim_id = sex + str(no)
        video_file="%s_OFT.avi"%(anim_id)
        vid_cap=cv.VideoCapture(video_file)
        
        # Get the frame rate, height and width of a video file
        frame_rate = vid_cap.get(cv.CAP_PROP_FPS)        
        height = vid_cap.get(cv.CAP_PROP_FRAME_HEIGHT)
        width = vid_cap.get(cv.CAP_PROP_FRAME_WIDTH)
        
        success, image = vid_cap.read()
        if success == 1:
            img = image
        
        coords = []   
        cv.namedWindow('Image_%s'%(anim_no), cv.WINDOW_NORMAL)
        cv.imshow('Image_%s'%(anim_id), img)
        # Save coordinates of 12 mouse clicks in coods
        cv.setMouseCallback('Image_%s'%(anim_id), onclick, img)        
        
        # wait for Esc or q key and then exit
        while True:
            key = cv.waitKey(1) & 0xFF
            if key == 27 or key == ord("q"):
                # print('Image cropped at coordinates: {}'.format(coords))
                cv.destroyAllWindows()
                break             
        
        # Set the region of interest (OFT area, Small center (10%) and Large center (50%))
        coords.append(coords[0])
        OFT_area = Path([coords[0],coords[1],coords[2],coords[3],coords[0]], closed = True)
        p = calculate_pixel(coords)
        
        # Save ROI in this list
        coords_list=[]
        coords_list.append(OFT_area)
        coords_list.append(Path(resize_center(coords, 0.1), closed = True))
        coords_list.append(Path(resize_center(coords, 0.5), closed = True))
        
        # Read bonsai file and assign according to duration
        bonsai_file = pd.read_csv(r'%s-OFT-bonsai.csv'%(anim_id),sep='\s+', engine='python', encoding = "cp949", converters={'mouseX': float,'mouseY': float,'mouseAngle': float,'mouseMajorAxisLength': float, 'mouseMinorAxisLength': float,'mouseArea': float})
        
        # Calculate the time spent and the distance travelled in each region by specific time bin
        for i in range(int(total_exp_time_sec/(timebin_in_sec))):
            start = timebin_in_sec * i
            end = timebin_in_sec * (i+1)
            period = '%ss_%ss'%(str(start), str(end))
            
            a = int(frame_rate * (time + start))
            b = int(frame_rate * (time + end))
            bonsai_file_timebin = bonsai_file.iloc[a:b]
            bonsai_file_timebin.columns = bonsai_file.columns
            df_time_timebin = calculate_time(bonsai_file_timebin, frame_rate, coords_list)
            df_dist_timebin = calculate_distance(bonsai_file_timebin, p, coords_list)

            df['Time_smallCT_%s'%(period)][no] = df_time_timebin[0]
            df['Time_largeCT_%s'%(period)][no] = df_time_timebin[1]
            df['Time_border_%s'%(period)][no] = df_time_timebin[2]

            df['Dist_smallCT_%s'%(period)][no] = df_dist_timebin[0]
            df['Dist_largeCT_%s'%(period)][no] = df_dist_timebin[1]
            df['Dist_border_%s'%(period)][no] = df_dist_timebin[2]
            df['Dist_Total_%s'%(period)][no] = df_dist_timebin[3]
            
        # Calculate the time spent (second), the distance (cm) travelled and speed (cm/s) in each region/entire region and draw the trajectory of each mouse for 05, 10, 15 and 20 minutes
        for i in range(bin_5min):
            i = i+1
            a = int(frame_rate*time)
            b = int(frame_rate*(time+i*300))
            
            bonsai_file_new = bonsai_file.iloc[a:b]
            bonsai_file_new.columns = bonsai_file.columns
            df_time = calculate_time(bonsai_file_new, frame_rate, coords_list)
            df_dist = calculate_distance(bonsai_file_new, p, coords_list)
            time_str = str('%02d'%(i*5))+'min'

            df['Time_smallCT_%s'%(time_str)][no] = df_time[0]
            df['Time_largeCT_%s'%(time_str)][no] = df_time[1]
            df['Time_border_%s'%(time_str)][no] = df_time[2]

            df['Dist_smallCT_%s'%(time_str)][no] = df_dist[0]
            df['Dist_largeCT_%s'%(time_str)][no] = df_dist[1]
            df['Dist_border_%s'%(time_str)][no] = df_dist[2]
            df['Dist_Total_%s'%(time_str)][no] = df_dist[3]
            
            df['Speed_smallCT_%s'%(time_str)][no] = float(df_dist[0])/float(df_time[0])
            df['Speed_largeCT_%s'%(time_str)][no] = float(df_dist[1])/float(df_time[1])
            df['Speed_border_%s'%(time_str)][no] = float(df_dist[2])/float(df_time[2])
            df['Speed_Total_%s'%(time_str)][no] = float(df_dist[3])/(i*300)
        
            draw_trajectory(bonsai_file_new, coords_list, anim_id, sex, time_str, width, height)     
        
        df['Timebin'][no] = timebin_in_sec

        df_write = pd.ExcelWriter(excel_file, engine='xlsxwriter')
        df.to_excel(df_write, sheet_name = 'Sheet1')
        df_write.save()

