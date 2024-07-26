import pandas as pd

file_path= 'image03.txt'

df = pd.read_csv(file_path, delimiter='\t') 
 
#pick out columns
col_interest= ['collection_id',
               'image03_id',
               'dataset_id',
               'src_subject_id',
               'experiment_id',
               'sex',
               'comments_misc',
               'image_file',
               'image_description',
               'Sex of subject at birth'
               'Age in months at the time of the interview/test/sampling/imaging.',
               
               ]

specific_df=df[col_interest]

# Specify the output file 
output_file_path = 'subset_data.txt'

# Save the subset DataFrame to a new text file
specific_df.to_csv(output_file_path, sep='\t', index=False)

print(specific_df)