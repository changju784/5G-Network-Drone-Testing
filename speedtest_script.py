import speedtest

wifi = speedtest.Speedtest()
ul = wifi.upload()
dl = wifi.download()
print("WiFi DL speed is:")
print(dl)
print("WiFi UL speed is:")
print(ul)
