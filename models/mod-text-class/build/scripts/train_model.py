import os
from pathlib import Path

import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_datasets as tfds

from utils.saver import ModelSaver

SCRIPTS_DIR = Path(os.path.dirname(__file__))
DATA_DIR = Path(SCRIPTS_DIR.parents[0], 'data')

splits = ['train[:60%]', 'train[-40%:]', 'test']
splits, info = tfds.load(name="imdb_reviews", 
                         with_info=True, 
                        split=splits, 
                        as_supervised=True, 
                        data_dir=DATA_DIR.resolve())
train_data, validation_data, test_data = splits

num_train_examples = info.splits['train'].num_examples
num_test_examples = info.splits['test'].num_examples
num_classes = info.features['label'].num_classes

print('The Dataset has a total of:')
print('\u2022 {:,} classes'.format(num_classes))

print('\u2022 {:,} movie reviews for training'.format(num_train_examples))
print('\u2022 {:,} movie reviews for testing'.format(num_test_examples))

class_names = ['negative', 'positive']

embedding = "https://tfhub.dev/google/tf2-preview/gnews-swivel-20dim/1"
hub_layer = hub.KerasLayer(embedding, input_shape=[], dtype=tf.string, trainable=True)

batch_size = 512
train_batches = train_data.shuffle(num_train_examples // 4).batch(batch_size).prefetch(1)
validation_batches = validation_data.batch(batch_size).prefetch(1)
test_batches = test_data.batch(batch_size)

current_folder_path = Path(os.path.dirname(__file__))
logdir = Path(current_folder_path.parents[1], 'logs')
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=logdir)


model = tf.keras.Sequential([
        hub_layer,
        tf.keras.layers.Dense(16, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')])

model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy'])

history = model.fit(train_batches,
                    epochs=5,
                    validation_data=validation_batches,
                    callbacks=[tensorboard_callback])

eval_results = model.evaluate(test_batches, verbose=0)

for metric, value in zip(model.metrics_names, eval_results):
    print(metric + ': {:.3}'.format(value))

version = 1

ModelSaver(current_folder_path.resolve(), model=model, version=version)()
