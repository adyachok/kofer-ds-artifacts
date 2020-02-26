import logging
import os

import requests
import yaml

from jeeves import command, JeevesPipeline
from smart_suit.rules.verification import ModelVerificationManager


logger = logging.getLogger(__name__)
ROOT = os.path.dirname(__file__)
MODELS_FOLDER = 'models_integration'


class CustomJeevesPipeline(JeevesPipeline):

    def init_parser(self):
        parser = super().init_parser()
        parser.add_argument('--cert', dest='cert',
                            type=str, help='Certificate', required=True)
        parser.add_argument('--pem', dest='pem',
                            type=str, help='Certificate', required=True)
        parser.add_argument('--upload-url-dev', dest='upload_url_dev',
                            type=str, help='Url (dev) to upload model files')
        parser.add_argument('--upload-url-test', dest='upload_url_test',
                            type=str, help='Url (test) to upload model files')
        return parser

    def create_build_args_dict(self, args):
        build_args = super().create_build_args_dict(args)
        extended = {
            'cert': args.cert,
            'pem': args.pem,
            'upload_url_dev': args.upload_url_dev,
            'upload_url_test': args.upload_url_test}
        build_args.update(extended)
        return build_args

    def on_success(self, branch_name, model, build_args):
        self.verify_model_model_desc_integration(model)
        if 'master' in branch_name:
            upload_url = build_args.get('upload_url_test')
        else:
            upload_url = build_args.get('upload_url_dev')
        model_upload_url = upload_url + '/model/upload'
        status, payload = self.upload_model(model, build_args, model_upload_url)
        if status:
            return
        model_data = payload.get('model')
        model_id = model_data.get('id')
        model_revision = model_data.get('currentModelRevision')
        self.upload_shap_plots(model, model_id, model_revision,
                               build_args, upload_url)

    @command('Model Description File Verification')
    def verify_model_model_desc_integration(self, model):
        status = 0
        msg = 'Verification Success.'
        model_path = os.path.join(model, 'model')
        print(f'Running description file verification in folder {model_path}')
        errors = ModelVerificationManager([model_path]).verify()
        if errors:
            print(f'Model and model description file verification '
                  f'failed for model {model}.')
            status = 1
            msg = errors
        return status, msg

    def get_model_files_for_upload(self, model_path):
        model_path = os.path.join(model_path, 'model')
        files = os.listdir(model_path)
        # Uploading should be done after model and model description file
        # verification, that's why here should not be errors
        desc_file_path = [f for f in files if f.endswith('desc.yml')][0]
        desc_file_path = os.path.join(model_path, desc_file_path)
        models_files_paths = []
        with open(desc_file_path, 'r') as desc:
            data = yaml.load(desc, Loader=yaml.FullLoader)
            for model in data.get('models'):
                model_files = model.get('files')
                models_files_paths.extend([os.path.join(model_path, m)
                                           for m in model_files])
        for f in models_files_paths:
            if not os.path.exists(f):
                raise Exception(f'File {f} does not exists.')
        return desc_file_path, models_files_paths

    @command('Model Upload Step')
    def upload_model(self, model_path, build_args, upload_url):
        msg = f'Cannot upload model {model_path} to {upload_url}.'
        status = 0
        desc_file_path, model_files_paths = self.get_model_files_for_upload(
            model_path)
        files = [
            ('descriptionFile', open(desc_file_path, 'rb'))
        ]
        files.extend([('modelFiles', open(f, 'rb')) for f
                      in model_files_paths])
        with requests.Session() as session:
            session.cert = (
               build_args.get('cert'),
               build_args.get('pem'))
            try:
                resp = session.post(upload_url, files=files, verify=False)
                if not resp.ok:
                    print(resp.__dict__)
                    status = resp.status_code
                else:
                    msg = resp.json().get('payload')
            except Exception as e:
                msg += f' During upload next error occured: {e}'
                status = 1
            finally:
                for fd in files:
                    fd[1].close()
        return status, msg

    @command('Upload Shap plots')
    def upload_shap_plots(self, model_path, model_id, model_revision,
                          build_args, upload_url):
        status = 0
        msg = ''
        model_path = os.path.join(model_path, 'model')
        plots_path = os.path.join(model_path, 'plots')
        if not os.path.exists(plots_path):
            msg = 'Model has no Shap plots.'
            print(msg)
            return status, msg
        plots = []
        for plot_filename in os.listdir(plots_path):
            plot_path = os.path.join(plots_path, plot_filename)
            plots.append(('modelFiles', open(plot_path, 'rb')))
        plots_upload_url = upload_url + '/model/shap/upload'
        with requests.Session() as session:
            session.cert = (
               build_args.get('cert'),
               build_args.get('pem'))
            try:
                resp = session.post(plots_upload_url,
                                    files=plots,
                                    verify=False,
                                    data={
                                        'modelId': model_id,
                                        'revision': model_revision})
                if not resp.ok:
                    print(resp.__dict__)
                    status = resp.status_code
                else:
                    msg = resp.json().get('payload')
            except Exception as e:
                msg += f' During plots upload next error occured: {e}'
                status = 1
            finally:
                for fd in plots:
                    fd[1].close()
        return status, msg


if __name__ == "__main__":
    CustomJeevesPipeline().main()
