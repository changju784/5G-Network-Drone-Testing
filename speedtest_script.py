import speedtest
import pyodbc


wifi = speedtest.Speedtest()
ul = wifi.upload()
dl = wifi.download()
print("WiFi DL speed is:")
print(dl)
print("WiFi UL speed is:")
print(ul)

## sql code

#conn = pyodbc.connect('Driver={SQL Server};'
#                      'Server=server;'
#                      'Database=database;'
#                      'Trusted_Connection=yes;')

#cursor = conn.cursor()

#cursor.execute('''
#               INSERT INTO thing (field1, field2, etc)
#               VALUES 
#               (Var1, dl, ul)
#               ''')

#conn.commit()

