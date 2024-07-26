import pandas as pd

df = pd.read_csv('raw_test.txt', delimiter='\t', header=0,)

# Print the original column names
#print("Original Column Names:")
#print(df.columns)

#condition to check 
condition = df['comments_misc'].str.contains('MR')

#Filter rows based on the condition 
filtered_df = df[condition]

# Save the filtered DataFrame
filtered_df.to_csv('MR_test_withcolnames.txt', sep="\t" , index=False)

print("Saved")

