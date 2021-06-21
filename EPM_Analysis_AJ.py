# -*- coding: utf-8 -*-
"""
Video analysis of Elevated Plus Maze (EPM) by Bonsai & Python

written by Anes Ju, 2021.06.15
modified by Anes Ju, 2021.06.21

This script analyzes all the csv and its video files of elevated plus maze experiments from mice which are listed in excel file in the same directory. 
This script is 

(1) to analyze the time spent (second) and distance travelled (cm) in each arm and center in specific time bin you enter (in second)
(2) to analyze the time spent (second), distance travelled (cm) and speed (cm/s) in open/closed arms and center for 05 minutes, 10 minutes and 15 minutes (depending on the experimental time)
(3) to draw the trajectory of each mouse for 05 minutes, 10 minutes and 15 minutes (depending on the experimental time)

*******
Important information before starting this code

1. In the same working directory, you should have a video file (F835_EPM.avi) and its bonsai file (F835_EPM-bonsai.csv) of each animal and an excel file (EPM_data.xlsx : Should include information with column names; 'Animal no':int, 'Sex':str,'Starting time':int (in sec), 'Group': str) with animal no, sex and the starting time (as second) of video analysis. Please keep the file name as above. 

2. In the console, there will be three questions poped up: 
    
    'Please enter how long one session of the experiment takes (in minutes):   ' --> Please write the experimental time in minutes. Then, press enter key.
    'Please enter the time bin (in second):   '. --> Please write the divisor of experimental time (in second) that you entered. Then, press enter key.
    'Do you want to define 5 regions of EPM (press 1) or 3 regions of EPM (press 2)?   ' --> Press 1 or 2. Then, press enter key.

3. When the first frame of video pops up, you should click 12 corners of EPM counterclockwise from the top left corner of upper closed arm and enter esc key to close the video.

4. It is important to click the exact coordinates of center, since the pixel size is calculated based on those coordinates.

5. At the end, you will have an excel file with all the data analyzed and the trajectory of each mouse for 05 minutes, 10 minutes and 15 minutes (depending on the experimental time).

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
import numpy as np

def onclick(event,x,y,flag,image):
    """
    Get the coordinates of mouse click (left mouse click) ane return the coordinates as list.
    """
    global coords
    if event == cv.EVENT_LBUTTONUP:
        coords.append((x,y))
        return

def define_ROI(coords):
    """
    Define the regions of interest from coordinate list.
    """
    open_arm_1 = Path([coords[1],coords[2],coords[3],coords[4]])
    open_arm_2 = Path([coords[7],coords[8],coords[9],coords[10]])
    closed_arm_1 = Path([coords[0],coords[1],coords[10],coords[11]])
    closed_arm_2 = Path([coords[4],coords[5],coords[6],coords[7]])
    center = Path([coords[1],coords[4],coords[7],coords[10]])
    coords_list = [open_arm_1, open_arm_2, closed_arm_1, closed_arm_2, center]
    return coords_list
        
def draw_trajectory(bonsai_file, coords_list, animal_no, animal_sex, time, width, height):
    """
    Draw the trajectory of mouse location depending on experimental time and save this graph.
    """   
    # Plot each point
    plt.scatter(bonsai_file['mouseX'], bonsai_file['mouseY'], s=0.5)
    
    # Draw each ROIs
    oa_1_patch = patches.PathPatch(coords_list[0],edgecolor='yellow',fill=0, lw=2)
    oa_2_patch = patches.PathPatch(coords_list[1],edgecolor='orange',fill=0, lw=2)
    ca_1_patch = patches.PathPatch(coords_list[2],edgecolor='green',fill=0, lw=2)
    ca_2_patch = patches.PathPatch(coords_list[3],edgecolor='blue',fill=0, lw=2)
    ct_patch = patches.PathPatch(coords_list[4],edgecolor='red',fill=0, lw=2)
    
    plt.gca().add_patch(oa_1_patch)
    plt.gca().add_patch(oa_2_patch)
    plt.gca().add_patch(ca_1_patch)
    plt.gca().add_patch(ca_2_patch)
    plt.gca().add_patch(ct_patch)
    
    # Assign the characteristics of the plot
    plt.title("%s%s_EPM_%s"%(animal_sex, animal_no, time))
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.xlim(0, width)
    plt.ylim(0, height)
    plt. rcParams["figure.figsize"] = (8,6)
    rc('font', **{'family':'Arial'})
    plt.axis('off')
    plt.savefig("%s%s_EPM_%s.jpg"%(animal_sex, animal_no, time), forat = 'jpg')
    plt.show()
    return

def calculate_pixel(coords_list):
    """
    Based on the coordinates of EPM (5cm x 5cm in center), calculate and return the size of pixel
    """
    x_1, y_1 = coords_list[1]
    x_2, y_2 = coords_list[4]
    x_3, y_3 = coords_list[7]
    x_4, y_4 = coords_list[10]

    p_1 = (25/((x_1-x_2)**2 + (y_1-y_2)**2))**0.5 # size of pixel in centimeter. 25 means 5cmx5cm for center of EPM. 
    p_2 = (25/((x_3-x_2)**2 + (y_3-y_2)**2))**0.5
    p_3 = (25/((x_3-x_4)**2 + (y_3-y_4)**2))**0.5
    p_4 = (25/((x_1-x_4)**2 + (y_1-y_4)**2))**0.5
    
    p = (p_1+p_2+p_3+p_4)/4
    return p

def calculate_time(bonsai_file, frame_rate, coords_list):
    """
    Calculate the time spent in ROIs and return the data in list format
    """
    bonsai_file_list = list(zip(bonsai_file['mouseX'], bonsai_file['mouseY']))
    time_spent=[]    
    for i in range(len(coords_list)):
        inside_region = coords_list[i].contains_points(bonsai_file_list)
        time_inside_region = sum(inside_region)/frame_rate
        time_spent.append(time_inside_region)        
    return time_spent

def calculate_distance(bonsai_file, p, coords_list):
    """
    Calculate distance travelled in ROI and return a list of [dist in OA_left, dist in OA_right, dist in CA_up, dist in CA_down, dist in center,  Total dist]. Please take the order of elements into account when you add these values in the data set!!
    """    
    x = bonsai_file['mouseX']
    y = bonsai_file['mouseY']
    Total_dist = []
    OA_left_dist = []
    OA_right_dist = []
    CA_up_dist = []
    CA_down_dist = []
    CT_dist = []
    
    for i in bonsai_file.index.values.tolist()[:-2]:
        a = i
        b = a+1
        dist = (((x[a] - x[b])*p)**2+((y[a] - y[b])*p)**2)**0.5
        Total_dist.append(dist)

        if coords_list[0].contains_point((x[a], y[a])):
            OA_left_dist.append(dist)
        elif coords_list[1].contains_point((x[a], y[a])):
            OA_right_dist.append(dist)
        elif coords_list[2].contains_point((x[a], y[a])):
            CA_up_dist.append(dist)
        elif coords_list[3].contains_point((x[a], y[a])):
            CA_down_dist.append(dist)
        elif coords_list[4].contains_point((x[a], y[a])):
            CT_dist.append(dist)
    return [np.nansum(OA_left_dist), np.nansum(OA_right_dist), np.nansum(CA_up_dist), np.nansum(CA_down_dist), np.nansum(CT_dist), np.nansum(Total_dist)]        

if __name__ == '__main__':

    # Get the address of excel file and open the file
    excel_file="EPM_data.xlsx"
    df = pd.read_excel(excel_file, converters={'Animal no':str,'Sex':str,'Starting time':int}, index_col = 'Animal no')

    # Get all the animal no, sex and starting time as list formats
    animal_sex = df['Sex'].to_list()
    animal_no = df.index.to_list()
    starting_time = df['Starting time'].to_list()    
        
    # Ask the time bin in sec and get the value in integer format
    total_exp_time_min = int(input('Please enter how long one session of the experiment takes (in minutes):   '))
    total_exp_time_sec = total_exp_time_min*60
    timebin_in_sec = int(input('Please enter the time bin in sec:  '))    
    analysis_way = int(input('Do you want to define 5 regions of EPM (press 1) or 3 regions of EPM (press 2)?   '))
        
    # Create the column names depending on the time bin    
    df_columns = ['Timebin']
    bin_5min = int(total_exp_time_min/5)
    for period in ['05min', '10min', '15min']:
        df_columns = df_columns + ['Time_OA_%s'%(period), 'Time_CA_%s'%(period), 'Time_CT_%s'%(period), 'Dist_OA_%s'%(period), 'Dist_CA_%s'%(period), 'Dist_CT_%s'%(period), 'Dist_Total_%s'%(period), 'Speed_OA_%s'%(period), 'Speed_CA_%s'%(period), 'Speed_CT_%s'%(period), 'Speed_Total_%s'%(period)]
    
    for i in range(int(total_exp_time_sec/timebin_in_sec)):
        start = timebin_in_sec * i
        end = timebin_in_sec * (i+1)
        period = '%ss_%ss'%(str(start), str(end))   
        if analysis_way == 2:
            df_columns = df_columns + ['Time_CT_%s'%(period), 'Time_OA_%s'%(period), 'Time_CA_%s'%(period), 'Dist_CT_%s'%(period), 'Dist_Total_%s'%(period), 'Dist_OA_%s'%(period), 'Dist_CA_%s'%(period)]                       
        elif analysis_way == 1:     
            df_columns = df_columns + ['Time_OA_left_%s'%(period), 'Time_OA_right_%s'%(period), 'Time_CA_up_%s'%(period), 'Time_CA_down_%s'%(period), 'Time_CT_%s'%(period), 'Time_OA_%s'%(period), 'Time_CA_%s'%(period), 'Dist_OA_left_%s'%(period), 'Dist_OA_right_%s'%(period), 'Dist_CA_up_%s'%(period), 'Dist_CA_down_%s'%(period), 'Dist_CT_%s'%(period), 'Dist_Total_%s'%(period), 'Dist_OA_%s'%(period), 'Dist_CA_%s'%(period)]        

    # Create the new columns with new column names in the dataframe
    df_add = pd.DataFrame(index = animal_no, columns = df_columns)
    df_add = df_add.fillna(0)
    df = pd.concat([df, df_add], axis=1)
    
    # Open the video file and its bonsai file of each mouse from excel file
    for no, sex, time in zip(animal_no, animal_sex, starting_time):
        anim_no = str(no)
        anim_id = sex + str(no)
        
        # Read the video file by opencv package
        video_file="%s_EPM.avi"%(anim_id)
        vid_cap=cv.VideoCapture(video_file)
        success, image = vid_cap.read()
        
        # Get the frame rate, height and width of a video file
        frame_rate = vid_cap.get(cv.CAP_PROP_FPS)        
        height = vid_cap.get(cv.CAP_PROP_FRAME_HEIGHT)
        width = vid_cap.get(cv.CAP_PROP_FRAME_WIDTH)        

        # Get the first image in img
        if success == 1:
            img = image               
        
        # Pop the first image from video file up
        coords = []  
        cv.namedWindow('Image_%s'%(anim_id), cv.WINDOW_NORMAL)
        cv.imshow('Image_%s'%(anim_id), img)
        
        # Save coordinates of 12 mouse clicks in coods
        cv.setMouseCallback('Image_%s'%(anim_id), onclick, img)        
        
        # wait for Esc or q key and then exit
        while True:
            key = cv.waitKey(1) & 0xFF
            if key == 27 or key == ord("q"):
                cv.destroyAllWindows()
                break             
        
        # Calculate the size of pixel (centimeter for EPM)
        coords_list = define_ROI(coords)
        p = calculate_pixel(coords)
        
        # Open the bonsai file in csv format
        bonsai_file = pd.read_csv(r'%s_EPM-bonsai.txt'%(anim_id),sep='\s+', engine='python', encoding = "cp949", converters={'mouseX': float,'mouseY': float,'mouseAngle': float,'mouseMajorAxisLength': float, 'mouseMinorAxisLength': float,'mouseArea': float})  
        
        # Calculate the time spent and the distance travelled in each region by specific time bin
        for i in range(int(total_exp_time_sec/(timebin_in_sec))):
            start = timebin_in_sec * i
            end = timebin_in_sec * (i+1)
            
            a = int(frame_rate * (time + start))
            b = int(frame_rate * (time + end))
            bonsai_file_timebin = bonsai_file.iloc[a:b]
            bonsai_file_timebin.columns = bonsai_file.columns
            df_time_timebin = calculate_time(bonsai_file_timebin, frame_rate, coords_list)
            df_dist_timebin = calculate_distance(bonsai_file_timebin, p, coords_list)
            
            period = '%ss_%ss'%(str(start), str(end))
            print(period)
            
            df['Time_CT_%s'%(period)][no] = df_time_timebin[4]
            df['Time_OA_%s'%(period)][no] = df_time_timebin[0] + df_time_timebin[1]
            df['Time_CA_%s'%(period)][no] = df_time_timebin[2] + df_time_timebin[3]            
    
            df['Dist_CT_%s'%(period)][no] = df_dist_timebin[4]
            df['Dist_Total_%s'%(period)][no] = df_dist_timebin[5]
            df['Dist_OA_%s'%(period)][no] = df_dist_timebin[0] + df_dist_timebin[1]
            df['Dist_CA_%s'%(period)][no] = df_dist_timebin[2] + df_dist_timebin[3]            
                            
            if analysis_way == 1:    
                df['Time_OA_left_%s'%(period)][no] = df_time_timebin[0]
                df['Time_OA_right_%s'%(period)][no] = df_time_timebin[1]
                df['Time_CA_up_%s'%(period)][no] = df_time_timebin[2]
                df['Time_CA_down_%s'%(period)][no] = df_time_timebin[3]
                
                df['Dist_OA_left_%s'%(period)][no] = df_dist_timebin[0]
                df['Dist_OA_right_%s'%(period)][no] = df_dist_timebin[1]
                df['Dist_CA_up_%s'%(period)][no] = df_dist_timebin[2]
                df['Dist_CA_down_%s'%(period)][no] = df_dist_timebin[3]
            
        # Draw the trajectory of each mouse for 05, 10 and 15 minutes
        for i in range(bin_5min):
            i = i+1
            a = int(frame_rate*time)
            b = int(frame_rate*(time+i*300))
            print(i)
            
            bonsai_file_new = bonsai_file.iloc[a:b]
            bonsai_file_new.columns = bonsai_file.columns
            df_time = calculate_time(bonsai_file_new, frame_rate, coords_list)
            df_dist = calculate_distance(bonsai_file_new, p, coords_list)
            time_str = str('%02d'%(i*5))+'min'

            df['Time_CT_%s'%(time_str)][no] = df_time[4]
            df['Time_OA_%s'%(time_str)][no] = df_time[0] + df_time[1]
            df['Time_CA_%s'%(time_str)][no] = df_time[2] + df_time[3]
            
            df['Dist_CT_%s'%(time_str)][no] = df_dist[4]
            df['Dist_Total_%s'%(time_str)][no] = df_dist[5]
            df['Dist_OA_%s'%(time_str)][no] = df_dist[0] + df_dist[1]
            df['Dist_CA_%s'%(time_str)][no] = df_dist[2] + df_dist[3]
    
            df['Speed_CT_%s'%(time_str)][no] = float(df_dist[4])/float(df_time[4])
            df['Speed_Total_%s'%(time_str)][no] = float(df_dist[5])/(i*300)
            df['Speed_OA_%s'%(time_str)][no] = float((df_dist[0] + df_dist[1]))/float((df_time[0] + df_time[1]))
            df['Speed_CA_%s'%(time_str)][no] = float((df_dist[2] + df_dist[3]))/float((df_time[2] + df_time[3]))
        
            draw_trajectory(bonsai_file_new, coords_list, anim_no, sex, time_str, width, height)                   
        
        df['Timebin'][no] = timebin_in_sec
    # Save all the data in excel file back
    df_write = pd.ExcelWriter(excel_file, engine='xlsxwriter')
    df.to_excel(df_write, sheet_name = 'Sheet1')
    df_write.save()
