# -*- coding: utf-8 -*-
"""
Video analysis of EPM by Bonsai & Python

written by Anes Ju, 20200408
modified by Yoni Couderc, 25/03/2021

This code analyze all the csv and its video file  of mice which are written in excel file in the same directory. This is to draw the trajectory of mouse location from csv file analyzed by Bonsai program and calculate the time spent and distance travelled in each arm and center in elevated plus maze (EPM) experiments.

*******
Important information before starting this code

1. In the working directory, you should have a video file (F835_EPM.avi) and its bonsai file (F835_EPM-bonsai.csv) of each animal and an excel file (EPM_Time_Spent.xlsx) with animal no, sex and the starting time (as second) of video analysis. Please keep the file name as above. 

2. When the first frame of video pops up, you should click 12 corners of EPM counterclockwise from top left corner of upper closed arm and esc key to close the video.
*******

Enjoy the analysis!

"""

# Import packages
import pandas as pd
import matplotlib.pyplot as plt
import cv2 as cv
from matplotlib.path import Path
import matplotlib.patches as patches
import numpy as np

def onclick(event,x,y,flag,image):
    """
    Get the coordinates of mouse click (left mouse click) ane return the coordinates as list.
    """
    global coords
    if event == cv.EVENT_LBUTTONUP:
        coords.append((x,y))
        # wait for Esc or q key and then exit
        # if len(coords) ==12:
        #     # cv.polylines(img,coords,True, (0,255,255),
        #     #         lineType=cv.LINE_AA)
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
        
def draw_graph(bonsai_file, coords_list, animal_no, animal_sex, time, width, height):
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
    plt.savefig("%s%s_EPM_%s.jpg"%(animal_sex, animal_no, time), forat = 'jpg')
    plt.show()
    return

def calculate_pixel(coords_list):
    """
    Based on the coordinates of EPM (60cmx60cm), calculate and return the size of pixel
    """
    x_1, y_1 = coords_list[1]
    x_2, y_2 = coords_list[4]
    x_3, y_3 = coords_list[7]
    x_4, y_4 = coords_list[10]

    p_1 = (25/((x_1-x_2)**2 + (y_1-y_2)**2))**0.5 # size of pixel in centimeter. 25 means 5cm x5cm for center of EPM. 
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

def calculate_distance(bonsai_file, coords_list, p):
    """
    Calculate distance travelled in ROI and return a list of [dist in OA_left, dist in OA_right, dist in CA_up, dist in CA_down, dist in center,  total dist]. Please take the order of elements into account when you add these values in the data set!!
    """    
    x = bonsai_file['mouseX']
    y = bonsai_file['mouseY']
    total_dist = []
    OA_left_dist = []
    OA_right_dist = []
    CA_up_dist = []
    CA_down_dist = []
    CT_dist = []
    
    for i in bonsai_file.index.values.tolist()[:-2]:
        a = i
        b = a+1
        dist = (((x[a] - x[b])*p)**2+((y[a] - y[b])*p)**2)**0.5
        total_dist.append(dist)

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

    return [np.nansum(OA_left_dist), np.nansum(OA_right_dist), np.nansum(CA_up_dist), np.nansum(CA_down_dist), np.nansum(CT_dist), np.nansum(total_dist)]        

if __name__ == '__main__':

    # Get the address of excel file and open the file
    excel_file="EPM_data.xlsx"
    df = pd.read_excel(excel_file, converters={'Animal no':str,'Sex':str,'Starting time':int}, index_col = 'Animal no')

    # Get all the animal no, sex and starting time as list formats
    animal_sex = df['Sex'].to_list()
    animal_no = df.index.to_list()
    starting_time = df['Starting time'].to_list()
    
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
                print('Image cropped at coordinates: {}'.format(coords))
                cv.destroyAllWindows()
                break             

        coords_list=define_ROI(coords)
        
        # Open the bonsai file in csv format
        bonsai_file = pd.read_csv(r'%s-EPM-bonsai.csv'%(anim_id),sep='\s+', engine='python', encoding = "cp949", converters={'mouseX': float,'mouseY': float,'mouseAngle': float,'mouseMajorAxisLength': float, 'mouseMinorAxisLength': float,'mouseArea': float})  
        
        # Get the starting time and calculate the ending time        
        starting_frame = int(time*frame_rate)
        ending_frame_15min = int((time+60*15)*frame_rate)
        ending_frame_10min = int((time+60*10)*frame_rate)
        ending_frame_05min = int((time+60*5)*frame_rate)
                
        # Calculate the size of pixel (centimeter for EPM)
        p = calculate_pixel(coords)
        print(p)
        
        # Data for 15 mins        
        bonsai_file_15min = bonsai_file.iloc[starting_frame:ending_frame_15min]
        bonsai_file_15min.columns = bonsai_file.columns
        df_time_15min = calculate_time(bonsai_file_15min, frame_rate, coords_list)
        df_dist_15min = calculate_distance(bonsai_file_15min, coords_list, p)
        draw_graph(bonsai_file_15min, coords_list, anim_no, sex, '15min', width, height)
    
        df['Time_OA_left_15min'][no] = df_time_15min[0]
        df['Time_OA_right_15min'][no] = df_time_15min[1]
        df['Time_CA_up_15min'][no] = df_time_15min[2]
        df['Time_CA_down_15min'][no] = df_time_15min[3]
        df['Time_CT_15min'][no] = df_time_15min[4]
        df['Time_OA_15min'][no] = df_time_15min[0] + df_time_15min[1]
        df['Time_CA_15min'][no] = df_time_15min[2] + df_time_15min[3]
        
        df['Dist_OA_left_15min'][no] = df_dist_15min[0]
        df['Dist_OA_right_15min'][no] = df_dist_15min[1]
        df['Dist_CA_up_15min'][no] = df_dist_15min[2]
        df['Dist_CA_down_15min'][no] = df_dist_15min[3]
        df['Dist_CT_15min'][no] = df_dist_15min[4]
        df['Dist_total_15min'][no] = df_dist_15min[5]
        df['Dist_OA_15min'][no] = df_dist_15min[0] + df_dist_15min[1]
        df['Dist_CA_15min'][no] = df_dist_15min[2] + df_dist_15min[3]
        
         # Data for 10 mins        
        bonsai_file_10min = bonsai_file.iloc[starting_frame:ending_frame_10min]
        bonsai_file_10min.columns = bonsai_file.columns
        df_time_10min = calculate_time(bonsai_file_10min, frame_rate, coords_list)
        df_dist_10min = calculate_distance(bonsai_file_10min, coords_list, p)
        draw_graph(bonsai_file_10min, coords_list, anim_no, sex, '10min', width, height)
    
        df['Time_OA_left_10min'][no] = df_time_10min[0]
        df['Time_OA_right_10min'][no] = df_time_10min[1]
        df['Time_CA_up_10min'][no] = df_time_10min[2]
        df['Time_CA_down_10min'][no] = df_time_10min[3]
        df['Time_CT_10min'][no] = df_time_10min[4]
        df['Time_OA_10min'][no] = df_time_10min[0] + df_time_10min[1]
        df['Time_CA_10min'][no] = df_time_10min[2] + df_time_10min[3]
        
        df['Dist_OA_left_10min'][no] = df_dist_10min[0]
        df['Dist_OA_right_10min'][no] = df_dist_10min[1]
        df['Dist_CA_up_10min'][no] = df_dist_10min[2]
        df['Dist_CA_down_10min'][no] = df_dist_10min[3]
        df['Dist_CT_10min'][no] = df_dist_10min[4]
        df['Dist_total_10min'][no] = df_dist_10min[5]
        df['Dist_OA_10min'][no] = df_dist_10min[0] + df_dist_10min[1]
        df['Dist_CA_10min'][no] = df_dist_10min[2] + df_dist_10min[3]
        
        # Data for 05 mins        
        bonsai_file_05min = bonsai_file.iloc[starting_frame:ending_frame_05min]
        bonsai_file_05min.columns = bonsai_file.columns
        df_time_05min = calculate_time(bonsai_file_05min, frame_rate, coords_list)
        df_dist_05min = calculate_distance(bonsai_file_05min, coords_list, p)
        draw_graph(bonsai_file_05min, coords_list, anim_no, sex, '05min', width, height)
    
        df['Time_OA_left_05min'][no] = df_time_05min[0]
        df['Time_OA_right_05min'][no] = df_time_05min[1]
        df['Time_CA_up_05min'][no] = df_time_05min[2]
        df['Time_CA_down_05min'][no] = df_time_05min[3]
        df['Time_CT_05min'][no] = df_time_05min[4]
        df['Time_OA_05min'][no] = df_time_05min[0] + df_time_05min[1]
        df['Time_CA_05min'][no] = df_time_05min[2] + df_time_05min[3]
        
        df['Dist_OA_left_05min'][no] = df_dist_05min[0]
        df['Dist_OA_right_05min'][no] = df_dist_05min[1]
        df['Dist_CA_up_05min'][no] = df_dist_05min[2]
        df['Dist_CA_down_05min'][no] = df_dist_05min[3]
        df['Dist_CT_05min'][no] = df_dist_05min[4]
        df['Dist_total_05min'][no] = df_dist_05min[5]
        df['Dist_OA_05min'][no] = df_dist_05min[0] + df_dist_05min[1]
        df['Dist_CA_05min'][no] = df_dist_05min[2] + df_dist_05min[3]

        df_write = pd.ExcelWriter(excel_file, engine='xlsxwriter')
        df.to_excel(df_write, sheet_name = 'Sheet1')
        df_write.save()
