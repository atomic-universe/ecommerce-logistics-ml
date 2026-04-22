import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from datetime import timedelta
import os
from src.utils.load_data import load_raw_data

# method to calcuate distnace on latitude-longitude
def calculate_distance(record):
    '''
     Calcuate distnace between the latitudes and longitudes.

    '''

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




class Data_Pipline:

    # read the dataset from the '/data/raw' folder and stored it into pandas dataframe object.
    def __init__(self,file_names: list):
        '''
            read the dataset from the '/data/raw' folder and stored it into pandas dataframe object.\n
            parameter:\n
            file_names: list of raw data file names.
        '''
        path = os.path.join('data','raw')
        if not os.path.exists(path):
            os.makedirs(path)

        else:
            dataset = {}

            # looping each file on 'file_names' list.
            for file in file_names:
                file_path =  os.path.join(path, f'{file}.csv')
                
                # load the data 
                if os.path.exists(file_path):
                    dataset[file] =  pd.read_csv(file_path)

                else:
                    load_raw_data()
                    if os.path.exists(file_path):
                        dataset[file] =  pd.read_csv(file_path)

                    

            self.dataset = dataset



        
    def __create_distance_feature(self,delivered_seller,customers_geo,sellers_geo):

        '''
            calcuate the distance feature of between seller and customer.

        '''

        # customer 

        delivered_seller_customer = delivered_seller.merge(customers_geo[['customer_id','latitude','longitude','customer_state']],on='customer_id',how='left',validate='m:1')
        delivered_seller_customer.rename(columns = {'latitude':'customer_latitude','longitude':'customer_longitude'},inplace=True)


        # seller

        delivered_seller_customer = delivered_seller_customer.merge(sellers_geo[['seller_id','latitude','longitude','seller_state']],on='seller_id',how='left',validate='m:1')
        delivered_seller_customer.rename(columns = {'latitude':'seller_latitude','longitude':'seller_longitude'},inplace=True)


        # new features. Same_state belong of customer and seller?

        delivered_seller_customer['is_same_state'] = (delivered_seller_customer['seller_state'] == delivered_seller_customer['customer_state'] )

        # drop the used columns
        delivered_seller_customer.drop(columns=['seller_state','customer_state'],inplace=True)


        # new feature of delivery distance in km.
        delivered_seller_customer['delivery_distance_km'] = delivered_seller_customer.apply(calculate_distance,axis=1)

        return delivered_seller_customer


        
    def processe(self):
        '''
        Convert raw data into complete processed and final data ready for model training.
        '''

        # unique geolocation

        unique_geolocations =  self.dataset['geolocation'].groupby('geolocation_zip_code_prefix').agg(latitude = ('geolocation_lat','median'),
                                                                              longitude = ('geolocation_lng','median')
                                                                             )
        


        # mergin customer and sellers table with unique geolocation table
        # to get theire respected latitude and longitude coordinates.

        # customer
        customers_geo = self.dataset['customers'].merge(unique_geolocations ,left_on='customer_zip_code_prefix',
                                        right_on='geolocation_zip_code_prefix',how='left',validate='m:1')

        # seller
        sellers_geo = self.dataset['sellers'].merge(unique_geolocations,left_on='seller_zip_code_prefix',
                                    right_on='geolocation_zip_code_prefix',how='left',validate='m:1')




        # get orders that successfully delivared.

        delivered_orders = self.dataset['orders'][self.dataset['orders']['order_status']=='delivered']
        delivered_orders = delivered_orders.drop(columns=['order_status'])


        # drop null values of target column extraction.
        delivered_orders.dropna(subset=['order_purchase_timestamp','order_delivered_customer_date'],inplace=True)

        # change object to datetime data-type.
        delivered_orders['order_purchase_timestamp']      =  pd.to_datetime(delivered_orders['order_purchase_timestamp'])
        delivered_orders['order_approved_at']             =  pd.to_datetime(delivered_orders['order_approved_at'])
        delivered_orders['order_delivered_carrier_date']  =  pd.to_datetime(delivered_orders['order_delivered_carrier_date'])
        delivered_orders['order_delivered_customer_date'] =  pd.to_datetime(delivered_orders['order_delivered_customer_date'])  
        delivered_orders['order_estimated_delivery_date'] =  pd.to_datetime(delivered_orders['order_estimated_delivery_date'])


        # create target feature and get the existing date prediction result

        # actual target
        delivered_orders['delivery_day'] = (delivered_orders['order_delivered_customer_date'] - 
                                            delivered_orders['order_purchase_timestamp']).dt.days

        # existing predicted result 
        delivered_orders['delivery_estimated_day'] =(delivered_orders['order_estimated_delivery_date'] - 
                                                    delivered_orders['order_purchase_timestamp']).dt.days


        # sort values by date. (early dates first late dates last)
        delivered_orders.sort_values('order_purchase_timestamp',inplace=True)


        # join the items column and to get seller id and create new feature of seller_dispach_on_time or not?
        delivered_seller = delivered_orders.merge(self.dataset['order_items'][['order_id','seller_id','shipping_limit_date']],on='order_id',how='left',validate='1:m')
        delivered_seller['shipping_limit_date'] = pd.to_datetime(delivered_seller['shipping_limit_date'])
        seller_shippingDate_differenceby_limitDate = (delivered_seller['shipping_limit_date'] -  delivered_seller['order_delivered_carrier_date'] )
        zero_time = timedelta(0)


        # feature of seller_dispach_on_time or not?
        delivered_seller['shipping_dispach_onTime'] =  np.where(seller_shippingDate_differenceby_limitDate > zero_time,1,0)
        # drop_unwanted_columns
        delivered_seller = delivered_seller.drop(columns=['shipping_limit_date','order_delivered_carrier_date'])
        # drop duplicates
        delivered_seller.drop_duplicates(subset=['order_id','seller_id'],inplace=True)


        # calcuate the distance feature of between seller and customer.
        delivered_seller_customer = self.__create_distance_feature(delivered_seller,customers_geo,sellers_geo)

        
        # sorting the values in ascending order.
        delivered_seller_customer.sort_values(['seller_id','order_purchase_timestamp'],inplace=True)


        # feature of seller_previous order count.
        delivered_seller_customer['seller_prev_order_count'] = delivered_seller_customer.groupby('seller_id').cumcount()


        # seller previous timely shipping score.
        delivered_seller_customer['seller_avg_timely_shipping']= delivered_seller_customer.groupby('seller_id')['shipping_dispach_onTime'].transform(lambda x: x.expanding().mean().shift(1))

        # seller average delivary time

        delivered_seller_customer['avg_seller_delivery_days'] = (delivered_seller_customer.groupby('seller_id')['delivery_day'].expanding().mean().shift(1).reset_index(level=0,drop=True))

        order_seller_count = (delivered_seller_customer.groupby('order_id')['seller_id'].nunique().reset_index(name='unique_seller_count'))
        delivered_seller_customer = delivered_seller_customer.merge(order_seller_count,on='order_id',how='left')

        delivary_seller_max_timing_and_avgDelDays =  delivered_seller_customer.groupby('order_id').agg(max_avg_seller_delivery_days = ('avg_seller_delivery_days','max'),seller_max_timely_shipping=('seller_avg_timely_shipping','max'))
        delivered_seller_customer = delivered_seller_customer.merge(delivary_seller_max_timing_and_avgDelDays,on='order_id',how='left',validate='m:1')
        delivered_seller_customer['is_same_state'] = delivered_seller_customer['is_same_state'].astype('int')


        dataset =  delivered_seller_customer.drop(columns = ['customer_id','order_approved_at','order_delivered_customer_date',
                                          'order_estimated_delivery_date','unique_seller_count','customer_latitude','customer_longitude',
                                          'seller_latitude','seller_longitude'])
        


        order_purchase =  dataset.groupby('order_id').agg(order_purchase_timestamp=('order_purchase_timestamp','min'))

        dataset = dataset.drop_duplicates(subset =['order_id'])

        dataset = dataset.dropna(subset=['delivery_distance_km'])

        
        return dataset
       


    def __split_data(self,dataset):
        '''
            SPlit the processed and final data into train, test split.
        '''

         # final data features.
        # independent_feature = dataset.drop(columns = ['order_id','order_purchase_timestamp' ,'seller_id','seller_avg_timely_shipping','avg_seller_delivery_days','delivery_day','delivery_estimated_day','shipping_dispach_onTime'])
        # target = dataset['delivery_day']
        # existing_system_output =  dataset['delivery_estimated_day']

        train,test  = train_test_split(dataset,test_size=0.2)

        path = os.path.join('data','processed')
        
        if not os.path.exists(path):
            os.makedirs(path)

        train.to_csv(os.path.join(path,'training_data.csv'),index=False)
        test.to_csv(os.path.join(path,'testing_data.csv'),index=False)

        print("Data saved successfully.")

        # = train_test_split(target,test_size=0.2)



    def sequential(self):

        dataset = self.processe()
        self.__split_data(dataset)
        


if __name__ == '__main__':
    pipeline =  Data_Pipline(file_names=['customers','sellers','order_items','orders','geolocation'])

    pipeline.sequential()


    



