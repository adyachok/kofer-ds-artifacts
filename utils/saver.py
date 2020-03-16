import json
import os
from pathlib import Path

import yaml

import tensorflow as tf


class ModelSaver():
    """Helper class to build SavedModel from Keras models and attach model
    business description as an info method.
    Logic is based on:
      - https://www.tensorflow.org/guide/saved_model
      - https://www.tensorflow.org/guide/concrete_function
      - https://www.tensorflow.org/guide/keras/save_and_serialize
      - https://www.tensorflow.org/tutorials/customization/performance
    """

    def __init__(self, calling_script_path, model, version):
        """
        :param calling_script_path: os.path.dirname(__file__) of the
        calling script
        :param model: Keras model
        :param version: Keras model version
        """
        self.model = model
        self.model_desc_path, self.export_path = self._build_required_paths(
            calling_script_path, version
        )
        self.model_description = self._get_model_description()

    def __call__(self):
        """Allows to call class object as a function."""
        self._save_model()
        self._set_info_signature()

    def _build_required_paths(self, calling_script_path, version):
        """Builds paths from os.path.dirname(__file__)"""
        scripts_dir = Path(calling_script_path)
        root_dir = scripts_dir.parents[1]
        root_dir_name = os.path.basename(root_dir.resolve())
        model_dir = Path(root_dir, 'model')
        # Model should be saved under model/<model-name> path
        model_save_dir = Path(model_dir, root_dir_name)
        model_desc_path = Path(model_dir, 'model.desc.yml')
        export_path = os.path.join(model_save_dir.resolve(), str(version))
        return model_desc_path, export_path

    def _save_model(self):
        """Saves SavedModel to specified directory."""
        self.model.save(self.export_path, save_format="tf")
        print('\nexport_path = {}'.format(self.export_path))

    def _get_model_description(self):
        """Reads model.desc.yml file."""
        if os.path.exists(self.model_desc_path):
            with open(self.model_desc_path, 'r') as desc:
                return yaml.load(desc)
        else:
            raise Exception('Cannot build a model, dmodel description is not '
                            'provided. Please, put `model.desc.yml` file '
                            'into your <model-name>/model folder.')

    def _set_info_signature(self):
        """Sets info signature for a model."""
        imported = tf.saved_model.load(self.export_path)
        signatures = {
            "serving_default": imported.signatures["serving_default"],
            "info": self.info}
        tf.saved_model.save(imported,
                            self.export_path,
                            signatures)

    @tf.function(input_signature=[tf.TensorSpec([], tf.bool)])
    def info(self, x):
        return json.dumps(self.model_description)
