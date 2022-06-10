import os

from string import Template


class SQL_Provider:
    def __init__(self, file_path):
        self._scripts = {}

        for file in os.listdir(file_path):
            if file.endswith('.sql'):
                self._scripts[file] = Template(open(f'{file_path}/{file}').read())

    def get(self, file_name, **kwargs):
        return self._scripts[file_name].substitute(**kwargs)
