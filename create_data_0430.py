import psycopg2

# Establish a connection to the PostgreSQL database
conn = psycopg2.connect("dbname=ShoppingGO user=postgres password=1022")
cur = conn.cursor()

# Sample data for BUYER
buyers = [
    ('buyer1', 'Alice Johnson', '../Photos/image_tmp.png'),
    ('buyer2', 'Bob Smith', '../Photos/image_tmp.png')
]

# Sample data for SELLER
sellers = [
    ('seller1', 'Charlie Brown', '../Photos/image_tmp.png'),
    ('seller2', 'Dana Scully', '../Photos/image_tmp.png')
]

# Sample data for GOODS
goods = [
    (1, '../Photos/image_tmp.png', 'Description of first item', 'seller1'),
    (2, '../Photos/image_tmp.png', 'Description of second item', 'seller2')
]

# Sample data for AD
ads = [
    (1, '2023-01-01 08:00:00', '2023-01-15 08:00:00', 50.00, 'seller1'),
    (2, '2023-02-01 08:00:00', '2023-02-15 08:00:00', 75.00, 'seller2')
]

# Sample data for GRP
groups = [
    (1, 'Group A', 'Location X', '../Photos/image_tmp.png'),
    (2, 'Group B', 'Location Y', '../Photos/image_tmp.png')
]

# Sample data for GO_ACTIVITY
go_activities = [
    (1, 10.00, 100, True, False, 1, 1),
    (2, 15.00, 150, False, True, 2, 2)
]

# Sample data for ODR
orders = [
    ('buyer1', 1, 2, 20.00, '2023-04-10 12:00:00', 'Shipped', 'Nice product', 5),
    ('buyer2', 2, 3, 45.00, '2023-04-11 12:00:00', 'Pending', 'Late delivery', 3)
]

# Sample data for BUYER_PARTICIPATE
buyer_participates = [
    ('buyer1', 1),
    ('buyer2', 2)
]

# Sample data for SELLER_PARTICIPATE
seller_participates = [
    ('seller1', 1),
    ('seller2', 2)
]

# Function to insert data into each table
def insert_data(table, data):
    placeholders = ', '.join(['%s'] * len(data[0]))
    cur.executemany(f"INSERT INTO {table} VALUES ({placeholders})", data)
    conn.commit()

# Insert data into tables
insert_data('BUYER', buyers)
insert_data('SELLER', sellers)
insert_data('GOODS', goods)
insert_data('AD', ads)
insert_data('GRP', groups)
insert_data('GO_ACTIVITY', go_activities)
insert_data('ODR', orders)
insert_data('BUYER_PARTICIPATE', buyer_participates)
insert_data('SELLER_PARTICIPATE', seller_participates)

# Close connection
cur.close()
conn.close()
