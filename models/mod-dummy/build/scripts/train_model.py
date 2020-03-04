import os
from pathlib import Path

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

SCRIPTS_DIR = Path(os.path.dirname(__file__))
ROOT_DIR = SCRIPTS_DIR.parents[1]
ROOT_DIR_NAME = os.path.basename(ROOT_DIR.resolve())
MODEL_DIR = Path(ROOT_DIR, 'model')
# Model should be saved under model/<model-name> path
MODEL_SAVE_DIR = Path(MODEL_DIR, ROOT_DIR_NAME)
# os.makedirs(MODEL_SAVE_DIR.resolve())

version = 8


export_path = os.path.join(MODEL_SAVE_DIR.resolve(), str(version))
model.save(export_path, save_format="tf")

print('\nexport_path = {}'.format(export_path))
