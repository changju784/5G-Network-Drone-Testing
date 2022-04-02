# from "../ml_engines" import build_dataset
# from "../ml_engines" import model_regression
import sys

sys.path.insert(0, '../ml_engines')

from build_dataset import BuildData
from model_regression import Modeling

if __name__ == '__main__':
    bd = BuildData.instance()
    md = Modeling.instance()

    bd.get_data()
    # md.data_analysis()
    md.train()
    # md.predict(42.348178, -71.105248, 0)
    # 96 Mountfort: 42.348178, -71.105248, 81.93, 115.30

