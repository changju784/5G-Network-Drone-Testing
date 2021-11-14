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
import const.const_path as cpath

__all__ = ['build_model']

def model_regression(X, y, train_len, prediction):
    path = cpath.path
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

    optimizer = tf.keras.optimizers.RMSprop(0.001)
    # optimizer = Adam(learning_rate=0.001)
    es = EarlyStopping(monitor='val_loss', patience=10)
    mc = ModelCheckpoint('regression_' + prediction + '.h5', monitor='val_acc', mode='max', verbose=1,
                         save_best_only=False)
    model.compile(loss='mean_squared_error', optimizer=optimizer, metrics=['mae', 'mse'])
    model.summary()

    history = model.fit(X, y, epochs=20, validation_split=0.2, verbose=0, callbacks=[es, PrintDot()])
    if prediction == "upload":
        model.save(path["upload_model_path"])
        loaded_model = load_model(path["upload_model_path"])
    else:
        model.save(path["download_model_path"])
        loaded_model = load_model(path["download_model_path"])
    return loaded_model