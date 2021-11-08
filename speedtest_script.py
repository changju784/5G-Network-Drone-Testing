import pymysql
import speedtest
import threading



def test_speed():
    st = speedtest.Speedtest()
    dl = st.download()
    ul = st.upload()
    
    mydb = pymysql.connect(
        host='drone-network-test.cxgmkpckrzov.us-east-2.rds.amazonaws.com',
        port=3306,
        user='admin',
        password='Team16~!',
        database='network_test_data',
    )

    cursor = mydb.cursor()

    sql = "INSERT INTO network_result (download, \
       upload) \
       VALUES ('%f', '%f')" % \
       (dl, ul)
    cursor.execute(sql)

    mydb.commit()
    mydb.close()




try:
   t1 = threading.Thread(target = test_speed )
   t2 = threading.Thread(target = test_speed )
   t3 = threading.Thread(target = test_speed )
   t1.start()
   t2.start()
   t3.start()

   t1.join()
   t2.join()
   t3.join()
   #data_to_insert = [(download1,upload1),(download2,upload2),
   #                 (download3,upload3)]
   
   #cursor = mydb.cursor()
   
   #sql = "INSERT INTO network_result (download, \
   #upload) \
   #VALUES ('%f', '%f')"
   
   #cursor.executemany(sql,data_to_insert)
   #mydb.commit
   #mydb.close()
   
except:
   print("Error: unable to start thread")


#mydb = pymysql.connect(
#    host='drone-network-test.cxgmkpckrzov.us-east-2.rds.amazonaws.com',
#    port=3306,
#    user='admin',
#    password='Team16~!',
#    database='network_test_data',
#)
#data_to_insert = [(download1,upload1),(download2,upload2),
#                    (download3,upload3)]
#cursor = mydb.cursor()
#sql = "INSERT INTO network_result (download, \
#    upload) \
#    VALUES ('%f', '%f')"
#cursor.executemany(sql,data_to_insert)
#mydb.commit
#mydb.close()

   
