import os
from pathlib import PurePath

import numpy as np
import tensorflow as tf


print("\u2022 Using TensorFlow Version:", tf.__version__)

xs = np.array([-1.0,  0.0, 1.0, 2.0, 3.0, 4.0], dtype=float)
ys = np.array([-3.0, -1.0, 1.0, 3.0, 5.0, 7.0], dtype=float)

model = tf.keras.Sequential([tf.keras.layers.Dense(units=1, input_shape=[1])])

model.compile(optimizer='sgd',
              loss='mean_squared_error')

history = model.fit(xs, ys, epochs=500, verbose=0)

print("Finished training the model!")

SCRIPTS_DIR = PurePath(os.path.dirname(__file__))
print(SCRIPTS_DIR)
ROOT_DIR = SCRIPTS_DIR.parents[1]
print(ROOT_DIR)
ROOT_DIR_NAME = os.path.basename(ROOT_DIR)
print(ROOT_DIR_NAME)
MODEL_DIR = PurePath(ROOT_DIR, 'model')
print(MODEL_DIR)
# Model should be saved under model/<model-name> path
MODEL_SAVE_DIR = os.path.join(MODEL_DIR, ROOT_DIR_NAME)
print(MODEL_SAVE_DIR)
os.mkdir(MODEL_SAVE_DIR)

version = 8

export_path = os.path.join(MODEL_SAVE_DIR, str(version))
model.save(export_path, save_format="tf")

print('\nexport_path = {}'.format(export_path))
