import os
from pathlib import Path

import numpy as np
import tensorflow as tf

from utils.saver import ModelSaver


print("\u2022 Using TensorFlow Version:", tf.__version__)

xs = np.array([-1.0,  0.0, 1.0, 2.0, 3.0, 4.0], dtype=float)
ys = np.array([-3.0, -1.0, 1.0, 3.0, 5.0, 7.0], dtype=float)

current_folder_path = Path(os.path.dirname(__file__))
logdir = Path(current_folder_path.parents[1], 'logs')
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=logdir)

model = tf.keras.Sequential([tf.keras.layers.Dense(units=1, input_shape=[1])])

model.compile(optimizer='sgd',
              loss='mean_squared_error')

history = model.fit(xs,
                    ys,
                    epochs=500,
                    verbose=0,
                    callbacks=[tensorboard_callback])

print("Finished training the model!")

version = 8

ModelSaver(current_folder_path.resolve(), model=model, version=version)()
