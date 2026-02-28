from sqlalchemy import create_engine

import pandas as pd

class Connect_MySQL():


    def __init__(self, password,db,username='root',host='localhost'):
        '''
        Connected to mysql server database.
        paramers :
        username: mysql username
        password: mysql password
        db : database name
        host: port number
        '''
        self.__username = username
        self.__password = password
        self.__host = host
        self.db = db

        self.engine = None

        try:
            connection_string = f'mysql+pymysql://{self.__username}:{self.__password}@{self.__host}/{self.db}'    
            self.engine = create_engine(connection_string)
                       
        
        except Exception as e:
            print(f"Database connection error:  {e}")
    

    def fetch_tables_to_dfs(self, table_names):
        '''
        Fetch multiple mysql tables into dictionary of pandas dataframe.

        parameter:
        tables_names: list of tables 
        '''

        try:
            dataframes = {}

            # verify that input is on list type.
            if not type( table_names) == list:
                raise ValueError("The tables should be in list type only.")
            
            # Connection to mysql server
            with self.engine.connect() as connection:

                for table in table_names:
                    query = f'SELECT * FROM {table}'

                    df = pd.read_sql(sql=query,con=connection)
                    

                    dataframes[table] = df

                print(f'Successfully fetch table {table} with {len(df)} rows.')

                
            return dataframes 
            
        except Exception as e:
            print(f"Error in fetching table : {e}")




    

    
# Testing 'Connect_MySQl' class is working or not.

# Result : class connection successfully working


# conn =  Connect_MySQL(username='root',password='vighnesh',host='localhost',db='ecommerce')
# print("Connection SUccessl")

# conn.fetch_tables_to_dfs(table_names=['customers'])