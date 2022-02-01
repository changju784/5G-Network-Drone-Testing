'''
====================================
 :mod:`build_dataset` {GET data from DB and build a format to training data set}
====================================
'''

import pymysql
import pandas as pd

__all__ = ['build_dataset']
def get_data():
    mydb = pymysql.connect(
        host='drone-network-test.cxgmkpckrzov.us-east-2.rds.amazonaws.com',
        port=3306,
        user='admin',
        password='Team16~!',
        database='network_test_data',
    )
    columns = ['id', 'download', 'upload', 'distance_to_server', 'latitude', 'longtitude']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM network_result")
    myresult = mycursor.fetchall()
    df = pd.DataFrame(list(myresult))
    df.columns = ['id', 'download', 'upload', 'distance_to_server', 'latitude', 'longtitude']
    print(df)
    return df