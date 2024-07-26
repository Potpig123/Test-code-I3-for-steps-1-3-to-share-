import pandas as pd


df = pd.read_csv('subset_data.txt', sep='\t') 

# change directory function
old_directory = 's3://NDAR_Central_3/submission_60350/'
new_directory = './image03/'

def change_directory(file_path):
    return file_path.replace(old_directory, new_directory)

# Apply the function to change image path
df['image_file'] = df['image_file'].apply(change_directory)

# save new file as txt
df.to_csv('RAW_test', sep='\t', index=False)











