# -*- coding: utf-8 -*-
"""
Video analysis of OFT by Bonsai & Python

written by Anes Ju, 20201202
corrected by Anes Ju, 20210326

This code analyze all the csv and its video file  of mice which are written in excel file in the same directory. This is to draw the trajectory of mouse location from csv file analyzed by Bonsai program and calculate the time spent and distance travelled in small (10% of OFT area) and large center (50% of OFT area), and border (out of large center) in open field test (OFT) experiments.

*******
Important information before starting this code

1. In the working directory, you should have a video file (F835_OFT.avi) and its bonsai file (F835_OFT-bonsai.csv) of each animal and an excel file (OFT_Time_Spent.xlsx) with animal no, sex and the starting time (as second) of video analysis. Please keep the file name as above. 

2. When the first frame of video pops up, you should click 4 corners of OFT clockwise and esc key to close the video.
*******

Enjoy the analysis!

"""

# Import packages
import pandas as pd
import matplotlib.pyplot as plt
import cv2 as cv
from matplotlib.path import Path
import matplotlib.patches as patches
from os import path
import numpy as np
# import os


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
    # xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    xdiff = (coords[0][0] - coords[2][0], coords[1][0] - coords[3][0])
    # ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])
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
def draw_graph(bonsai_file, coords_list, animal_no, animal_sex, time, width, height):
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
    plt.title("%s%s_OFT_%s"%(animal_sex, animal_no, time))  
    plt.xlim(0, width)
    plt.ylim(0, height)    
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
    print(total_time)       
    time_total = total_time / frame_rate
    time_small_ct = small_ct_time / frame_rate
    time_large_ct = large_ct_time / frame_rate
    time_border = border_time / frame_rate
    print(time_total)   
    time_spent = [time_total, time_small_ct, time_large_ct, time_border]

    return time_spent

def calculate_distance(bonsai_file, coords_list, p):
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
            
    return [np.nansum(total_dist), np.nansum(small_ct_dist), np.nansum(large_ct_dist), np.nansum(border_dist)]


if __name__ == '__main__':
          
    # Get the current directory where the python file exists
    directory = path.dirname(path.abspath(__file__))

    # Take the address of excel file and open it
    excel_file="%s\OFT_Time_Spent.xlsx"%(directory)
    df = pd.read_excel(excel_file, converters={'Animal no':str,'Sex':str,'Starting time':int}, index_col = 'Animal no')

    # Get all the animal no, sex and starting time
    animal_sex = df['Sex'].to_list()
    animal_no = df.index.to_list()
    starting_time = df['Starting time'].to_list()
    
    # Open each video file and its bonsai file
    for no, sex, time in zip(animal_no, animal_sex, starting_time):

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

        cv.namedWindow('Image_%s'%(anim_id), cv.WINDOW_NORMAL)
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
        
        # Save ROI in this list
        coords_list=[]
        coords_list.append(OFT_area)
        coords_list.append(Path(resize_center(coords, 0.1), closed = True))
        coords_list.append(Path(resize_center(coords, 0.5), closed = True))
        
        # Starting and ending time
        starting_frame = int(time*frame_rate)
        ending_frame_20min = int((time+60*20)*frame_rate)
        ending_frame_10min = int((time+60*10)*frame_rate)
        ending_frame_05min = int((time+60*5)*frame_rate)
        
        # Read bonsai file and assign according to duration
        bonsai_file = pd.read_csv(r'%s_OFT-bonsai.csv'%(anim_id),sep='\s+', engine='python', encoding = "cp949", converters={'mouseX': float,'mouseY': float,'mouseAngle': float,'mouseMajorAxisLength': float, 'mouseMinorAxisLength': float,'mouseArea': float})
        
        bonsai_file_20min = bonsai_file.iloc[starting_frame:ending_frame_20min]
        bonsai_file_10min = bonsai_file.iloc[starting_frame:ending_frame_10min]
        bonsai_file_20min.columns = bonsai_file.columns
        bonsai_file_10min.columns = bonsai_file.columns
        bonsai_file_05min = bonsai_file.iloc[starting_frame:ending_frame_05min]
        bonsai_file_05min.columns = bonsai_file.columns
        
        # Calculate the size of pixel (centimeter for 60cm X 60cm OFT)
        p = calculate_pixel(coords)
        
         # Data for 20 mins        
        draw_graph(bonsai_file_20min, coords_list, no, sex, '20min', width, height)        
        df_data_time_20min = calculate_time(bonsai_file_20min, frame_rate, coords_list)        
        df_data_distance_20min = calculate_distance(bonsai_file_20min, coords_list, p)    
        df['Time_Small_ct_20min'][no] = df_data_time_20min[1]
        df['Time_Large_ct_20min'][no] = df_data_time_20min[2]
        df['Time_Borders_20min'][no] = df_data_time_20min[3]
        df['Dist_Total_20min'][no] = df_data_distance_20min[0]
        df['Dist_Small_ct_20min'][no] = df_data_distance_20min[1]
        df['Dist_Large_ct_20min'][no] = df_data_distance_20min[2]
        df['Dist_Borders_20min'][no] = df_data_distance_20min[3]
        
        # Data for 10 mins        
        draw_graph(bonsai_file_10min, coords_list, no, sex, '10min', width, height)        
        df_data_time_10min = calculate_time(bonsai_file_10min, frame_rate, coords_list)
        df_data_distance_10min = calculate_distance(bonsai_file_10min, coords_list, p)        
        df['Time_Small_ct_10min'][no] = df_data_time_10min[1]
        df['Time_Large_ct_10min'][no] = df_data_time_10min[2]   
        df['Time_Borders_10min'][no] = df_data_time_10min[3]
        df['Dist_Total_10min'][no] = df_data_distance_10min[0]
        df['Dist_Small_ct_10min'][no] = df_data_distance_10min[1]
        df['Dist_Large_ct_10min'][no] = df_data_distance_10min[2]
        df['Dist_Borders_10min'][no] = df_data_distance_10min[3]
        
        # Data for 05 mins        
        draw_graph(bonsai_file_05min, coords_list, no, sex, '05min', width, height)
        df_data_time_05min = calculate_time(bonsai_file_05min, frame_rate, coords_list)
        df_data_distance_05min = calculate_distance(bonsai_file_05min, coords_list, p)        
        df['Time_Small_ct_05min'][no] = df_data_time_05min[1]
        df['Time_Large_ct_05min'][no] = df_data_time_05min[2]   
        df['Time_Borders_05min'][no] = df_data_time_05min[3]
        df['Dist_Total_05min'][no] = df_data_distance_05min[0]
        df['Dist_Small_ct_05min'][no] = df_data_distance_05min[1]
        df['Dist_Large_ct_05min'][no] = df_data_distance_05min[2]
        df['Dist_Borders_05min'][no] = df_data_distance_05min[3]

        # excel_file_new = 'OFT_Time_Spent_new.xlsx'
        df_write = pd.ExcelWriter(excel_file, engine='xlsxwriter')
        df.to_excel(df_write, sheet_name = 'Sheet1')
        df_write.save()
