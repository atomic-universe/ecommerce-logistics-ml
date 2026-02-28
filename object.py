from sqlalchemy import create_engine,  Column, REAL, DateTime, Integer,  String, Date, ForeignKey, UniqueConstraint

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class customers(Base):
#     customer_id
# customer_unique_id
# customer_zip_code_prefix
# customer_city
# customer_state


    __tablename__ ='customers'
    customer_id = Column(String(255), primary_key=True)
    customer_unique_id = Column(String(255))
    customer_zip_code_prefix = Column(Integer, ForeignKey('geolocation.geolocation_zip_code_prefix'))
    customer_city = Column(String(30))
    customer_state = Column(String(30))

class orders(Base): 
    '''
    order_id
    customer_id
    order_status
    order_purchase_timestamp
    order_approved_at
    order_delivered_carrier_date
    order_delivered_customer_date
    order_estimated_delivery_date
    '''
    __tablename__ = 'orders'

    order_id  = Column(String(100),primary_key=True)
    customer_id = Column(String(100),ForeignKey('customers.customer_id'))
    order_status = Column(String(100))
    order_purchase_timestamp = Column(DateTime)
    order_approved_at = Column(DateTime)
    order_delivered_carrier_date = Column(DateTime)
    order_delivered_customer_date = Column(DateTime)
    order_estimated_delivery_date = Column(DateTime)


class order_payments(Base):
    # order_id
    # payment_sequential
    # payment_type
    # payment_installments
    # payment_value

    __tablename__ = 'order_payments'

    order_id = Column(String(100), ForeignKey('orders.order_id'))
    payment_sequential = Column(Integer)
    payment_type = Column(String(100))
    payment_installments = Column(Integer)
    payment_value = Column(REAL)


class Products(Base):

# product_id
# product_category_name
# product_name_lenght
# product_description_lenght
# product_photos_qty
# product_weight_g
# product_length_cm
# product_height_cm
# product_width_cm

    __tablename__ = 'products'


    product_id =  Column(String(100), primary_key=True)
    product_category_name =  Column(String(100), ForeignKey('product_category_name_translation.product_category_name'))
    product_name_lenght =  Column(REAL)
    product_description_lenght =  Column(REAL)
    product_photos_qty =  Column(REAL)
    product_weight_g =  Column(REAL)
    product_length_cm =  Column(REAL)
    product_height_cm =  Column(REAL)
    product_width_cm =  Column(REAL)


class order_items(Base):
    # order_id
    # order_item_id
    # product_id
    # seller_id
    # shipping_limit_date
    # price
    # freight_value
    __tablename__ = 'order_items'

    order_id = Column(String(200),ForeignKey('orders.order_id'))
    order_item_id = Column(Integer)
    product_id = Column(String(200),ForeignKey('products.product_id'))
    seller_id = Column(String(200),ForeignKey('sellers.seller_id'))
    shipping_limit_date = Column(String(200))
    price = Column(REAL)
    freight_value = Column(REAL)


class order_reviews (Base):


    # review_id
    # order_id
    # review_score
    # review_comment_title
    # review_comment_message
    # review_creation_date
    # review_answer_timestamp
    
    __tablename__ ='order_reviews'


    review_id = Column(String(100))
    order_id = Column(String(100),ForeignKey('orders.order_id'))
    review_score = Column(Integer)
    review_comment_title = Column(String(100))
    review_comment_message = Column(String(100))
    review_creation_date = Column(String(100))
    review_answer_timestamp = Column(String(100))



class geolocation(Base):

    # geolocation_zip_code_prefix
    # geolocation_lat
    # geolocation_lng
    # geolocation_city
    # geolocation_state
    __tablename__ = 'geolocation'


    geolocation_zip_code_prefix  = Column(Integer, nullable=False)
    geolocation_lat  = Column(REAL)
    geolocation_lng  = Column(REAL)
    geolocation_city = Column(String(100))
    geolocation_state= Column(String(100))


class sellers(Base):

    # seller_id
    # seller_zip_code_prefix
    # seller_city
    # seller_state

    __tablename__ = 'sellers'

    seller_id = Column(String(100), primary_key=True)
    seller_zip_code_prefix = Column(Integer, ForeignKey('geolocation.geolocation_zip_code_prefix'))
    seller_city = Column(String(100))
    seller_state = Column(String(100))



class product_category_name_translation(Base):
    __tablename__ = 'product_category_name_translation'

# product_category_name
# product_category_name_english

    product_category_name = Column(String(100))
    product_category_name_english = Column(String(100))


class leads_qualified(Base):
    __tablename__ ='leads_qualified'

    # mql_id
    # first_contact_date
    # landing_page_id
    # origin


    mql_id  = Column(String(150),primary_key=True)
    first_contact_date  = Column(String(150))
    landing_page_id  = Column(String(150))
    origin  = Column(String(150))


class leads_closed(Base):

    __tablename__ = 'leads_closed'

    # mql_id
    # seller_id
    # sdr_id
    # sr_id
    # won_date
    # business_segment
    # lead_type
    # lead_behaviour_profile
    # has_company
    # has_gtin
    # average_stock
    # business_type
    # declared_product_catalog_size
    # declared_monthly_revenue


    mql_id = Column(String(100),ForeignKey('leads_qualified.mql_id'))
    seller_id = Column(String(100), ForeignKey('sellers.seller_id'))
    sdr_id = Column(String(100))
    sr_id = Column(String(100))
    won_date = Column(String(100))
    business_segment = Column(String(100))
    lead_type = Column(String(100))
    lead_behaviour_profile = Column(String(100))
    has_company = Column(Integer)
    has_gtin = Column(Integer)
    average_stock = Column(String(100))
    business_type = Column(String(100))
    declared_product_catalog_size = Column(REAL)
    declared_monthly_revenue = Column(REAL)