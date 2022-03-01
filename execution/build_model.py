from ml_engines.build_dataset import BuildData
from ml_engines.model_regression import Modeling

if __name__ == '__main__':
    bd = BuildData.instance()
    md = Modeling.instance()
    md.train()
