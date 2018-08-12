import sys
sys.path.append('C:/Combo/combo')
import os

from dependencies_manager import *


def main():
    my_dir = os.path.basename(os.path.curdir)

    def is_test_case_dir(dir_name):
        if not os.path.isdir(os.path.join(my_dir, dir_name)):
            return False
        if dir_name.startswith('.'):
            return False
        return True

    test_sub_dirs = [os.path.join(my_dir, name) for name in os.listdir(my_dir) if is_test_case_dir(name)]

    for sub_directory in test_sub_dirs:
        print('Testing directory {}...\n'.format(sub_directory))

        sources_file = os.path.join(sub_directory, 'sources.json')
        root_dir = os.path.join(sub_directory, 'root')

        DependenciesManager(root_dir, sources_file).resolve()


if __name__ == '__main__':
    main()
