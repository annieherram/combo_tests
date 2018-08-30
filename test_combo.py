import sys
import os
import json
import subprocess

sys.path.append('C:/Combo/combo')
from dependencies_manager import DependenciesManager
from combo_general import ComboException
from source_locator_server import get_version_source


ROOT_DIR_NAME = 'root'
SOURCES_TEMPLATE_FILE_NAME = 'sources_template.json'
SOURCES_FILE_NAME = 'local_sources.json'
EXPECTATION_FILE_NAME = 'expected.json'


def normalize_sources_json(sub_dir, in_file_name, out_file_name):
    replacement = os.path.abspath(sub_dir)
    with open(os.path.join(sub_dir, in_file_name), 'r') as in_file:
        template_data = in_file.read()

    modified_data = template_data.replace('...', replacement).replace('\\', '/')
    with open(os.path.join(sub_dir, out_file_name), 'w') as out_file:
        out_file.write(modified_data)


def cmptree(s1, s2):
    return True  # TODO: Implement


def confirm_dependency_version(manager, expected_dependency, sources_file):
    # TODO: Fix exceptions
    expected_import_path = manager.get_dependency_path(expected_dependency['name'])

    if not os.path.exists(expected_import_path):
        print(expected_import_path)
        raise BaseException()

    import_src_path = get_version_source(expected_dependency['name'], expected_dependency['version'], sources_file)
    if not cmptree(expected_import_path, import_src_path):
        raise BaseException()


def run_test(root_dir, sources_file, expected_result):
    expected_error = expected_result.get('error')

    run_command = ['python', 'C:/Combo/combo/combo.py', root_dir, sources_file]
    p = subprocess.Popen(run_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    print(stdout)

    if stderr:
        line = str(stderr).split('\\r\\n')[-2]
        exception_name = line.split(':')[0].split('.')[-1]

        if not expected_error or exception_name != expected_error:
            raise RuntimeError('Unexpected error was raised. Expected {}, got {}'
                               .format(expected_error, exception_name), stderr)
    else:
        if expected_error:
            raise RuntimeError('Error {} was expected, but did not occur'.format(expected_error))

        expected_dependencies = expected_result['imports']
        manager = DependenciesManager(root_dir, sources_file)

        for expected_dependency in expected_dependencies:
            confirm_dependency_version(manager, expected_dependency, sources_file)


def main():
    my_dir = os.path.basename(os.path.curdir)

    def is_test_case_dir(dir_name):
        if not os.path.isdir(os.path.join(my_dir, dir_name)):
            return False
        if dir_name.startswith('.'):
            return False
        return True

    test_sub_dirs = [name for name in os.listdir(my_dir) if is_test_case_dir(name)]

    for sub_directory in test_sub_dirs:
        print('Testing directory "{}"...'.format(sub_directory))

        with open(os.path.join(sub_directory, EXPECTATION_FILE_NAME), 'r') as expected_file:
            expected_values = json.load(expected_file)

        normalize_sources_json(sub_directory, SOURCES_TEMPLATE_FILE_NAME, SOURCES_FILE_NAME)

        sources_file = os.path.join(sub_directory, SOURCES_FILE_NAME)
        root_dir = os.path.join(sub_directory, ROOT_DIR_NAME)

        run_test(root_dir, sources_file, expected_values)


if __name__ == '__main__':
    main()
