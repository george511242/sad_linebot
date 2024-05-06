import psycopg2
from psycopg2 import sql

# Connect to your postgres DB
conn = psycopg2.connect("dbname=ShoppingGO user=postgres password=1022")

# Open a cursor to perform database operations
cur = conn.cursor()

# Create a table
cur.execute("""
    CREATE TABLE BUYER (
        Buyer_account VARCHAR PRIMARY KEY,
        Buyer_name VARCHAR NOT NULL,
        Buyer_picture VARCHAR
    );

    CREATE TABLE SELLER (
        Seller_account VARCHAR PRIMARY KEY,
        Seller_name VARCHAR NOT NULL,
        Seller_picture VARCHAR
    );

    CREATE TABLE GOODS (
        Goods_ID SERIAL PRIMARY KEY,
        Goods_picture VARCHAR,
        Goods_description TEXT,
        Seller_ID VARCHAR REFERENCES SELLER(Seller_account)
    );

    CREATE TABLE AD (
        Ad_ID SERIAL PRIMARY KEY,
        Ad_start_time TIMESTAMP NOT NULL,
        Ad_end_time TIMESTAMP NOT NULL,
        Ad_price NUMERIC(10, 2) NOT NULL,
        Seller_ID VARCHAR REFERENCES SELLER(Seller_account)
    );

    CREATE TABLE GRP (
        Group_ID SERIAL PRIMARY KEY,
        Group_name VARCHAR NOT NULL,
        Group_location VARCHAR,
        Group_picture VARCHAR
    );

    CREATE TABLE GO_ACTIVITY (
        Go_Activity_ID SERIAL PRIMARY KEY,
        Min_price NUMERIC(10, 2),
        Unit_quantity INTEGER,
        Logistic_status BOOLEAN,
        Notification_status BOOLEAN,
        Goods_ID INTEGER REFERENCES GOODS(Goods_ID),
        Group_ID INTEGER REFERENCES GRP(Group_ID)
    );


    CREATE TABLE ODR (
        Buyer_account VARCHAR REFERENCES BUYER(Buyer_account),
        Go_Activity_ID INTEGER REFERENCES GO_ACTIVITY(Go_Activity_ID),
        Quantity INTEGER NOT NULL,
        Price NUMERIC(10, 2) NOT NULL,
        Order_timestamp TIMESTAMP NOT NULL,
        Order_status VARCHAR NOT NULL,
        Comment TEXT,
        Star_rating INTEGER
    );

    CREATE TABLE BUYER_PARTICIPATE (
        Buyer_account VARCHAR REFERENCES BUYER(Buyer_account),
        Group_ID INTEGER REFERENCES GRP(Group_ID)
    );

    CREATE TABLE SELLER_PARTICIPATE (
        Seller_account VARCHAR REFERENCES SELLER(Seller_account),
        Group_ID INTEGER REFERENCES GRP(Group_ID)
    );
""")

# Commit changes
conn.commit()

# Close communication with the database
cur.close()
conn.close()
