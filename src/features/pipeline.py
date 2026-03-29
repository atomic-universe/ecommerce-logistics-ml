

import pandas as pd
import numpy as np
import os
# from sklearn.model_selection import
from datetime import timedelta

def calculate_distance(record):
    lat1 = np.radians( record['customer_latitude'])
    lng1 = np.radians(record['customer_longitude'])
    lat2 = np.radians(record['seller_latitude'])
    lng2 = np.radians(record['seller_longitude'])

    # Calucate the difference.
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    
    a = (np.sin(dlat/2)**2) + np.cos(lat1) * np.cos(lat2) * np.sin(dlng/2)**2

    c =  2 * np.asin(np.sqrt(a))

    r = 6371

    return np.round((c * r),0)
    

class Training_pipeline():

   

    def __init__(self,data):
        self.data = data

    
    def __clean_data(self):
        # Convert columns to their appropriate datatypes.

        date_col = ['order_purchase_timestamp','order_approved_at','order_delivered_carrier_date',
            'order_delivered_customer_date','order_estimated_delivery_date','shipping_limit_date']

        number_col = ['payment_sequential','payment_installments','order_item_id','seller_zip_code_prefix']

        for col in date_col:
            self.data[col] = pd.to_datetime( self.data[col])
            

        for col in number_col:
            self.data[col] = self.data[col].astype('Int64')

        imp_features = ['order_id','order_purchase_timestamp','order_delivered_customer_date',
                'payment_type','customer_state','customer_latitude',
                'customer_longitude','price','freight_value','product_weight_g',
                'seller_state','seller_latitude','seller_longitude']
        self.data = self.data[imp_features]      

        # Those zip code are not present in geolocation table so we need to drop them.
        self.data.dropna(axis=0,subset=['customer_latitude','customer_longitude','seller_latitude','seller_longitude'],inplace=True)
        self.data = self.data.dropna(subset=['order_delivered_customer_date'])
        self.data.dropna(inplace=True)

        # adding output feature
        self.__add_output_feature()
        upper_lim = self.data['delivery_days'].quantile(0.99)
        self.data = self.data[  self.data['delivery_days']<upper_lim]


        # adding new feature.
        self.__add_distance()

        self.__feature_engg()

        # filtering records.
        self.data = self.data[(self.data['delivery_distance_km']>25) & (self.data['delivery_days']>1)]        

      

    def __add_distance(self):
        
       self.data['delivery_distance_km']  = self.data.apply(calculate_distance, axis=1)

    
    def __add_output_feature(self):
        self.data['delivery_days'] = (self.data['order_delivered_customer_date'] - self.data['order_purchase_timestamp']).dt.days


    def __feature_engg(self):
        
        self.data['is_same_state']= np.where((self.data['customer_state'].str.lower()) == (self.data['seller_state'].str.lower()),1,0 )

    def __transform(self):
        cols = ['delivery_days' ,'delivery_distance_km' ,'freight_value' ]
        for col in cols:
            self.data[f'{col}_log']= np.log1p(self.data[col])


    def get_data(self):
        '''
        get the processed features and targets,
        return tuple: features, target.
        '''
        data_groupby = self.data.groupby('order_id').agg(  
                                delivery_days = ('delivery_days_log','first'), 
                                order_count = ('seller_state','nunique'), 
                              # min_distance = ('delivery_distance_km_log','min'),
                              # max_distance=('delivery_distance_km_log','max') ,
                                avg_distance = ('delivery_distance_km_log','mean'),
                                 # purchase_year = ('purchase_year_log', 'first'),
                                 is_same_state = ('is_same_state','first'),
                                 
                                 freight_value = ('freight_value_log','sum')                             
                              
                            
                            )
        output_data = data_groupby.reset_index().drop(columns = 'order_id')
        return (output_data.drop(columns='delivery_days'),output_data['delivery_days'])
        
    def process(self):
        self.__clean_data()       
        self.__transform()
        
   

#    ---------------

if __name__ == "__main__":
    
    try:
        path = os.path.join('data','processed','testing_data.csv')
        # path = os.path.join('..','..','data','processed','training_data.csv')
        
        
        tp = Training_pipeline(pd.read_csv(path))
        tp.process()
        (x,y) = tp.get_data()

        print(x.shape, y.shape)

        print("Data processed successfully!")

    
        
        
        

    except (FileNotFoundError, FileExistsError) as e:
        print(f"Error: Could not find or access the dataset at {path}")
        print(f"Details: {e}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")