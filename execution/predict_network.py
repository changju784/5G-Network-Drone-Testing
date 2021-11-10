'''
====================================
 :mod:`predict_network` {execution function to handle train / prediction}
====================================
'''
from ml_engines.train import train, predict


if __name__ == '__main__':
    train("upload")
    # train("download")
    # data = [925.211, 1666258, 127.944]
    # print(predict(data, 'upload'))



