'''
====================================
 :mod:`const_path` {constant values}
====================================
'''

import os
cur_path = os.path.dirname(os.path.abspath(__file__))

path = {
    "train_data_path" : os.path.join(cur_path, "../ml_engines/dataset/sample_train_data.csv"),
    "upload_model_path": os.path.join(cur_path, "../ml_engines/dataset/regression_upload.h5"),
    "download_model_path": os.path.join(cur_path, "../ml_engines/dataset/regression_upload.h5")
}
