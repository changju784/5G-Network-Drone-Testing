'''
====================================
 :mod:`build_model` {modeling factory using keras}
====================================
'''
import tensorflow as tf
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.models import load_model
from mxnet.optimizer import Adam
from tensorflow import keras
from tensorflow.keras import layers
# import const.const_path as cpath


__all__ = ['build_model']

def model_regression(X, y, train_len):
    # path = cpath.path
    path = "dataset/sample_train_data.csv"
    model = keras.Sequential([
        layers.Dense(64, activation='relu', input_shape=[train_len]),
        layers.Dense(32, activation='relu'),
        layers.Dense(16, activation='relu'),
        layers.Dense(1)
    ])

    class PrintDot(keras.callbacks.Callback):
        def on_epoch_end(self, epoch, logs):
            if epoch % 100 == 0: print('')
            print('.', end='')

    # optimizer = tf.keras.optimizers.RMSprop(0.001)
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.01)
    es = EarlyStopping(monitor='val_loss', patience=10)
    mc = ModelCheckpoint('regression.h5', monitor='val_acc', mode='max', verbose=1,
                         save_best_only=False)
    model.compile(loss='mean_squared_error', optimizer=optimizer, metrics=['mae', 'mse'])
    model.summary()

    history = model.fit(X, y, epochs=20, validation_split=0.2, verbose=0, callbacks=[es, PrintDot()])
    # if prediction == "upload":
    #     model.save("../ml_engines/dataset/regression_upload.h5")
    #     loaded_model = load_model("../ml_engines/dataset/regression_upload.h5")
    # else:
    #     model.save("../ml_engines/dataset/regression_download.h5")
    #     loaded_model = load_model("../ml_engines/dataset/regression_download.h5")
    model.save("../ml_engines/dataset/regression.h5")
    loaded_model = load_model("../ml_engines/dataset/regression.h5")

    return loaded_model


