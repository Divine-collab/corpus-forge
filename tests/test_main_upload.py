import io
import importlib.util
import os


def load_app_from_path(path):
    spec = importlib.util.spec_from_file_location('main_module', path)
    module = importlib.util.module_from_spec(spec)
    # Ensure the module's directory is on sys.path so sibling imports work
    import sys
    module_dir = os.path.dirname(path)
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)
    spec.loader.exec_module(module)
    return module.app


def run_test():
    cwd = os.path.dirname(os.path.dirname(__file__))
    main_path = os.path.join(cwd, 'main.py')
    app = load_app_from_path(main_path)
    client = app.test_client()
    data = {
        'file': (io.BytesIO(b'Hello world'), 'sample.txt')
    }
    resp = client.post('/upload', data=data, content_type='multipart/form-data')
    print('STATUS', resp.status_code)
    try:
        print('JSON', resp.get_json())
    except Exception as e:
        print('TEXT', resp.data)


if __name__ == '__main__':
    run_test()
