import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import os
from ..features.pipeline import Training_pipeline


 
# try:
#     path = os.path.join('data','processed','testing_data.csv')
#     # path = os.path.join('..','..','data','processed','training_data.csv')
    
    
#     tp = Training_pipeline(pd.read_csv(path))
#     tp.process()
#     (x,y) = tp.get_data()

#     lr = LinearRegression()
#     lr.fit(x,y)
#     print("Model trained successfully!")

   
    
    
    

# except (FileNotFoundError, FileExistsError) as e:
#     print(f"Error: Could not find or access the dataset at {path}")
#     print(f"Details: {e}")

# except Exception as e:
#     print(f"An unexpected error occurred: {e}")