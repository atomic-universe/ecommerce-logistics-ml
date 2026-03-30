import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import os
from ..features.pipeline import Training_pipeline

import joblib


class LinearRegressionModel():

    def __init__(self,x,y):
        self.model = LinearRegression();
        self.model.fit(x,y)
        print("Model trained successfully!")
    
    def load_model(self,model_path):
        path = os.path.join('models','linear_regression_model.pkl')
        if not os.path.exists('models'):
            os.mkdir('models')
        
        joblib.dump(self.model,path)
        return path



if __name__ == "__main__":
    try:
        path = os.path.join('data','processed','training_data.csv')
        # path = os.path.join('..','..','data','processed','training_data.csv')
        
        
        tp = Training_pipeline(pd.read_csv(path))
        tp.process()
        (x,y) = tp.get_data()

        lr = LinearRegressionModel(x,y)
        lr.load_model('models/linear_regression_model.pkl')

    except (FileNotFoundError, FileExistsError) as e:
        print(f"Error: Could not find or access the dataset at {path}")
        print(f"Details: {e}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")


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