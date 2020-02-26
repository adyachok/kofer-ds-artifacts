import logging
import os

import requests
import yaml

from jeeves import command, JeevesPipeline


logger = logging.getLogger(__name__)
ROOT = os.path.dirname(__file__)
MODELS_FOLDER = 'models'


class CustomJeevesPipeline(JeevesPipeline):

    def init_parser(self):
        parser = super().init_parser()
        # parser.add_argument('--cert', dest='cert',
        #                     type=str, help='Certificate', required=True)
        # parser.add_argument('--pem', dest='pem',
        #                     type=str, help='Certificate', required=True)
        # parser.add_argument('--upload-url-dev', dest='upload_url_dev',
        #                     type=str,
        #                     help='Url (dev) to upload model files')
        # parser.add_argument('--upload-url-test', dest='upload_url_test',
        #                     type=str,
        #                     help='Url (test) to upload model files')
        return parser

    def create_build_args_dict(self, args):
        build_args = super().create_build_args_dict(args)
        # extended = {
        #     'cert': args.cert,
        #     'pem': args.pem,
        #     'upload_url_dev': args.upload_url_dev,
        #     'upload_url_test': args.upload_url_test}
        # build_args.update(extended)
        return build_args

    def on_success(self, branch_name, model, build_args):
        self.verify_model_model_desc_integration(model)
        if 'master' in branch_name:
            pass
        else:
            pass


if __name__ == "__main__":
    CustomJeevesPipeline().main()
