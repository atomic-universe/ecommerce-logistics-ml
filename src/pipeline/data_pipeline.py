import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from datetime import timedelta
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import PowerTransformer,OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
import os


from src.utils.load_data import load_raw_data

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
    

class Data_Pipeline():
    def __init__(self):
        '''
            read the dataset from the '/data/raw' folder and stored it into pandas dataframe object.\n
            parameter:\n
            file_names: list of raw data file names.
        '''
        file_names =  [ 'customers',
                    'sellers',
                    'geolocation',
                    'orders',
                    'order_items',
                    'products',
                    'order_payments',
                    'product_category_name_translation']
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
  


    def __product_aggrigate(self):
        '''
            
            Called by __items_aggrigate only.
            return the product aggrigate table.
        '''

        self.dataset['products']['product_volume_cm3'] = self.dataset['products']['product_length_cm'] * self.dataset['products']['product_height_cm'] * self.dataset['products']['product_width_cm'] 

        self.dataset['product_category_name_translation']['product_category_name_english'] = self.dataset['product_category_name_translation']['product_category_name_english'].str.lower()
        products_cat = self.dataset['products'].merge(self.dataset['product_category_name_translation'], on='product_category_name',how='left')

        return products_cat 
    

    def __items_aggrigate(self):
        """
        Aggrigate the items along with seller_geo, and proudct_cat also
        """
        products_cat = self.__product_aggrigate()

        # working on items table
        self.dataset['order_items']['shipping_limit_date'] = pd.to_datetime(self.dataset['order_items']['shipping_limit_date'])


        items_full =  (self.dataset['order_items'].merge(self.dataset['seller_geo'],on='seller_id',how='left')
                       
                       .merge(products_cat[['product_volume_cm3','product_category_name_english',
                                                         'product_weight_g','product_id']],on='product_id',how='left'))
        
        items_agg = items_full.groupby('order_id').agg(
                n_items = ('order_item_id','max'),
                seller_id = ('seller_id','first'),
                shipping_limit_date = ('shipping_limit_date','max'),
                total_price = ('price','sum'),
                total_freight_value = ('freight_value','sum'),
                seller_zip_code = ('seller_zip_code_prefix','first'),
                seller_state  = ('seller_state','first'),
                seller_latitude = ('seller_latitude','first'),
                seller_longitude = ('seller_longitude','first'),
                total_volume= ('product_volume_cm3','sum'),
                category = ('product_category_name_english','first'),
                total_product_weight_g = ('product_weight_g','sum'),
                n_unique_sellers = ('seller_id','nunique'),
                n_unique_states = ('seller_state','nunique'),
            ).reset_index()
        
        return items_agg
    

    def __payment_aggrigate(self):

        payments_agg = self.dataset['order_payments'].groupby('order_id').agg(payment_type = ('payment_type','first'),
                                 payment_installments=('payment_installments','max'),
                                 payment_value=('payment_value','sum')).reset_index()

        return payments_agg
    
   

    def __merge(self):
        """
        Combine all the import table with one single record. 
        for the next feature engineering and model training operation.
        """
        
        # 
        unique_geo = self.dataset['geolocation'].groupby('geolocation_zip_code_prefix').agg(lat = ('geolocation_lat','median'),lng = ('geolocation_lng','median'))

        self.dataset['cust_geo'] = self.dataset['customers'].merge(unique_geo.rename(columns ={'lat':'customer_latitude','lng':'customer_longitude'}), 
                                left_on='customer_zip_code_prefix',right_on='geolocation_zip_code_prefix',how='left')


        self.dataset['seller_geo'] = self.dataset['sellers'].merge(unique_geo.rename(columns ={'lat':'seller_latitude','lng':'seller_longitude'}), 
                                left_on='seller_zip_code_prefix',right_on='geolocation_zip_code_prefix',how='left')



        #  Converting object to datetime data type.
        dates_cols = ['order_purchase_timestamp','order_approved_at',
                    'order_delivered_carrier_date','order_delivered_customer_date',
                    'order_estimated_delivery_date']


        

        for col in dates_cols:
            self.dataset['orders'][col] = pd.to_datetime(self.dataset['orders'][col])

        items_agg = self.__items_aggrigate()
        payments_agg = self.__payment_aggrigate()

        df = (self.dataset['orders'].merge(self.dataset['cust_geo'],on='customer_id',how='left',validate='1:1')
            .merge(items_agg,on='order_id',how='left',validate='1:1')
            .merge(payments_agg,how='left',on='order_id',validate='1:1'))

        df = df[df['order_status']=='delivered']

        return df

    def __add_seller_performance(self,df):

        """
        ##----------------------------------------------------------------##
        #   Seller previous delivery on time rate and avg delivery days    #
        ##----------------------------------------------------------------##
        """

        seller_performance = df[['order_id','order_purchase_timestamp','order_delivered_customer_date','delivery_days','is_shipped_on_time','seller_id']].copy()

        seller_performance.sort_values(['seller_id','order_purchase_timestamp'],inplace=True)

        seller_previous_order_count = seller_performance.groupby('seller_id').cumcount()

        seller_timely_delivery_avg = seller_performance.groupby('seller_id')['is_shipped_on_time'].transform(lambda x: x.expanding().mean().shift())

        df['seller_previous_order_count'] = seller_previous_order_count
        df['seller_timely_delivery_avg'] = seller_timely_delivery_avg

        return df

    def __feature_engg(self,df):
        # target_feature.           
        df['delivery_days'] =  (df['order_delivered_customer_date'] - df['order_purchase_timestamp']).dt.days


        zero_time = timedelta(0)
        df['is_shipped_on_time'] =  np.where((df['shipping_limit_date'] - df['order_delivered_carrier_date'])>zero_time,1,0)

        df['is_same_state'] = np.where(df['customer_state'] == df['seller_state'],1,0)


        df['delivery_distance'] = df.apply(calculate_distance,axis=1)

        df['freight_ratio'] = df['total_freight_value'] / (df['total_price'] + 1)


        # ──  Weight per item (density proxy) ───────────────────────────────────────
        df['weight_per_item'] = df['total_product_weight_g'] / (df['n_items'] + 1)
        df['volume_per_item'] = df['total_volume'] / (df['n_items'] + 1)




        # ── Distance x Weight interaction (shipping complexity) ───────────────────
        df['distance_x_weight'] = df['delivery_distance'] * df['total_product_weight_g']
        df['distance_x_items']  = df['delivery_distance'] * df['n_items']



        # ── Cross-state multi-seller complexity ────────────────────────────────────
        df['logistics_complexity'] = df['n_unique_sellers'] * df['n_unique_states']

        # add the seller performance columns.
        df = self.__add_seller_performance(df)

        
        feature_cols = [
        
            # Core logistics
            'delivery_distance',
            'total_product_weight_g',
            'total_volume',
            'freight_ratio',
            'weight_per_item',
            'volume_per_item',

            # Order info
            'n_items',
            'total_price',
            'payment_value',
            'payment_installments',

            # Interactions
            'distance_x_weight',
            'logistics_complexity',

            # Seller behavior
            'seller_previous_order_count',
            'seller_timely_delivery_avg',

            # Structural
            'n_unique_sellers',
            'is_same_state',

            # prduct
            'category',
            'payment_type',

            #obj_cols 
            'category','payment_type',

            # binary cols
            'is_same_state'
        ]

        extras = ['order_purchase_timestamp']

        target = ['delivery_days']
        master_data = df[feature_cols + extras + target]

        return master_data
    


    def generate_train_test(self):
        df = self.__merge()
        master_df = self.__feature_engg(df)

        training_data , testing_data = train_test_split(master_df, test_size=0.2,random_state=42)


        path = os.path.join('data','processed')

        if not os.path.exists(path):
            os.makedirs(path)

        # save data

        training_data.to_csv(os.path.join(path,'training_data.csv'),index=False)
        testing_data.to_csv(os.path.join(path,'testing_data.csv'),index=False)


        print("train_test saved successfully..")


if __name__ == '__main__':
   

    dp = Data_Pipeline()
    dp.generate_train_test()