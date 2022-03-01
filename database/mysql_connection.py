import pymysql

db_manager = pymysql.connect(host='drone-network-test.cxgmkpckrzov.us-east-2.rds.amazonaws.com',
                             port=3306,
                             user='admin',
                             password='Team16~!',
                             db='network_test_data',
                             charset='utf8')

# cursor = db_manager.cursor(pymysql.cursors.DictCursor)
# rows = []
# cursor.execute("SHOW COLUMNS FROM network_test_data.network_result")
# rows = cursor.fetchall()
# cursor.close()
# for i in rows:
#     print(i)
d1, u1 = str(0.5), str(0.7)
query = "INSERT INTO network_result (upload, download) VALUES (" + d1 + ", " + u1 + ");"
cursor = db_manager.cursor()
try:
    cursor.execute(query)
except Exception as e:
    print(query)
    print(e)
finally:
    cursor.close()







def write_wo_commit(self, query):
    """
    INSERT, UPDATE, DELETE
    :param SQL query
    """
    cursor = self.db_manager.cursor()
    try:
        cursor.execute(query)
    except Exception as e:
        print(query)
        print(e)
    finally:
        cursor.close()

def read(query):
    """
    SQL query
    :rtype: arr sql columns
    """
    cursor = db_manager.cursor(pymysql.cursors.DictCursor)
    rows = []
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
    except Exception as e:
        print(e)
    finally:
        cursor.close()
    return rows

def write(query):
    """
    INSERT, UPDATE, DELETE.
    :param SQL query
    """
    connection = db_manager.get_connection()
    if connection.is_connected():
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query)
        except Exception as e:
            print(query)
            print(e)
        finally:
            # cursor.close()
            connection.commit()
            connection.close()
