import os
from pathlib import PurePath

import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_datasets as tfds


SCRIPTS_DIR = PurePath(os.path.dirname(__file__))
DATA_DIR = PurePath(SCRIPTS_DIR.parents[0], 'data')

splits = ['train[:60%]', 'train[-40%:]', 'test']
splits, info = tfds.load(name="imdb_reviews", 
                         with_info=True, 
                        split=splits, 
                        as_supervised=True, 
                        data_dir=DATA_DIR)
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

model = tf.keras.Sequential([
        hub_layer,
        tf.keras.layers.Dense(16, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')])

model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy'])

history = model.fit(train_batches,
                    epochs=20,
                    validation_data=validation_batches)

eval_results = model.evaluate(test_batches, verbose=0)

for metric, value in zip(model.metrics_names, eval_results):
    print(metric + ': {:.3}'.format(value))

# Saving
MODEL_DIR = PurePath(SCRIPTS_DIR.parents[1], 'model')

# Model version
version = 1

export_path = os.path.join(MODEL_DIR, str(version))

model.save(export_path, save_format="tf")

print('\nexport_path = {}'.format(export_path))
