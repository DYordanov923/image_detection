from PIL import Image
import glob
import os
import time
import threading
import numpy as np
from datetime import datetime
import random
import pandas as pd
import scipy.misc


#function to add rows to the dataframe
def df_add_row(width, height, img_id, time_st, my_df):
    
    #assing labels based on image resolution,
	if (width!=1920 and height !=1080):

		label = 1
		last_label = 1
		duration=0
		# create row in dataframe
		my_df.loc[len(my_df)] = [img_id, label, last_label, duration, time_st]

	else:

		label = 0
		last_label = 0
		duration=0
		my_df.loc[len(my_df)] = [img_id, label, last_label, duration, time_st]




#function to update rows in the dataframe
def df_update_row(width, height, img_id, time_st, my_df):
    
    # assign label based on image resolution, last_label - the label in previous iteration, duration and time_stamp
    # if last_label is different then calculate how long the image was with label = 1

	if (width!=1920 and height !=1080):
		label = 1
		last_label = my_df.loc[my_df['ID'] == img_id, 'Label']
        
		if label != int(last_label):
			last_time_st = my_df.loc[my_df['ID'] == img_id, 'Time_stamp']
			duration = time_st - last_time_st
			print(duration)
		else:
			duration=0
        #add values to the dataframe
		my_df.loc[my_df['ID'] == img_id, ['Label']] = label
		my_df.loc[my_df['ID'] == img_id, ['Last_label']] = last_label
		my_df.loc[my_df['ID'] == img_id, ['Duration']] = duration
		my_df.loc[my_df['ID'] == img_id, ['Time_stamp']] = time_st


	else:

		label = 0
		last_label = my_df.loc[my_df['ID'] == img_id, 'Label']

		my_df.loc[my_df['ID'] == img_id, ['Label']] = label
		my_df.loc[my_df['ID'] == img_id, ['Last_label']] = last_label
		my_df.loc[my_df['ID'] == img_id, ['Duration']] = 0
		my_df.loc[my_df['ID'] == img_id, ['Time_stamp']] = time_st



#funtion to compare current image_ids in directory and image_ids in the dataframe
def update_df(df_id_list, current_ids, my_df):
	result = list(set(df_id_list) - set(current_ids))
	updated_df = my_df[~my_df['ID'].isin(result)]
	return updated_df

#funtion to resize random image based on resolution
def auto_resize_img(path):

	list_images= [filename for filename in glob.glob(path+'*.jpeg')]
	random_img = random.choice(list_images)
	random_img_raw = Image.open(random_img)
	width, height = random_img_raw.size

	if (width!=1920 and height !=1080):
		new_img = random_img_raw.resize((1920,1080))
	else:
		new_img = random_img_raw.resize((400,400))
	new_img.save(random_img,'jpeg')


#function to scan folder of images and store info for them in dataframe
#to_save - use False;  True is to write log files .csv 

def scan(path, to_save):
  rnd=0
  #create dataframe
  col_names =  ['ID', 'Label', 'Last_label','Duration', 'Time_stamp']
  my_df  = pd.DataFrame(columns = col_names)

  while True:
	print("-----------\n")
	#list to store current images in the directory
	current_ids = []
	for filename in glob.glob(path+'*.jpeg'):
		#get image size
		im=Image.open(filename)
		width, height = im.size
		#get name of the image
		name = os.path.basename(filename)
		img_id, sep, tail = name.partition('.')
		#get time stamp of the file
		time_st = os.stat(filename).st_mtime

		current_ids.append(img_id)
		#add row if it is the first round of the loop, else update 
		if rnd ==0:
			df_add_row(width, height, img_id, time_st, my_df)
		else:
			df_update_row(width, height, img_id, time_st, my_df)

	#get list of image names in stored in the dataframe
	df_id_list = my_df['ID'].tolist()
	#if images are missing from the diretory, drop them and update the dataframe
	df_v2=update_df(df_id_list,current_ids,my_df)
	print(df_v2)
	#safe the dataframe to csv file
	if to_save == True:
	   df_v2.to_csv(path+"log/log_"+str(rnd)+".csv", sep='\t')

	rnd+=1
	#wait 4s for next iteratration
	time.sleep(4)
    

    #resize 2 random images every 4 iterations
	if rnd %4 ==0:
		 print("\n   Resize...")
		 for i in range(2):
		     auto_resize_img(path)