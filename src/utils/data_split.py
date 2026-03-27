from sklearn.model_selection import train_test_split

import pandas as pd
import os



data_path = os.path.join('data','processed','merged_data.csv')

data = pd.read_csv(data_path)

train,test = train_test_split(data,test_size=0.25)


train.to_csv(os.path.join('data','processed','training_data.csv'),index=False)
test.to_csv(os.path.join('data','processed','testing_data.csv'),index=False)