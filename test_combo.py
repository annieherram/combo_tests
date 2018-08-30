import sys
import os
import json

sys.path.append('C:/Combo/combo')
from dependencies_manager import DependenciesManager
from combo_general import ComboException
from source_locator_server import get_version_source
import utils


ROOT_DIR_NAME = 'root'
SOURCES_TEMPLATE_FILE_NAME = 'sources_template.json'
SOURCES_FILE_NAME = 'local_sources.json'
EXPECTATION_FILE_NAME = 'expected.json'

EXCLUDED_TESTS = ['unclear_circle']


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
        raise BaseException()

    import_src_path = get_version_source(expected_dependency['name'], expected_dependency['version'], sources_file)
    if not cmptree(expected_import_path, import_src_path):
        raise BaseException()


def run_test(root_dir, sources_file, expected_result):
    expected_error = expected_result.get('error')

    try:
        utils.rmtree(os.path.join(root_dir, '.combo'))
        manager = DependenciesManager(root_dir, sources_file)
        manager.resolve()

        if expected_error:
            raise RuntimeError('Error {} was expected, but did not occur'.format(expected_error))

        expected_dependencies = expected_result['imports']

    except ComboException as e:
        if type(e).__name__ != expected_error:
            raise e
        return

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
        if sub_directory in EXCLUDED_TESTS:
            print('Skipping excluded directory "{}"'.format(sub_directory))
        else:
            print('Testing directory "{}"...'.format(sub_directory))

            with open(os.path.join(sub_directory, EXPECTATION_FILE_NAME), 'r') as expected_file:
                expected_values = json.load(expected_file)

            normalize_sources_json(sub_directory, SOURCES_TEMPLATE_FILE_NAME, SOURCES_FILE_NAME)

            sources_file = os.path.join(sub_directory, SOURCES_FILE_NAME)
            root_dir = os.path.join(sub_directory, ROOT_DIR_NAME)

            run_test(root_dir, sources_file, expected_values)


if __name__ == '__main__':
    main()
