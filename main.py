import logging
import sys
import os

# NOTE: The absolute path is used for compatibility with Windows.
STUDENT_LIST_DIR_ABSOLUTE_PATH = os.path.join(sys.path[ 0 ], 'student_list/')
SUBJECTS_DIR_ABSOLUTE_PATH = os.path.join(sys.path[ 0 ], 'subjects/')

# TODO: Implement class Subject() and corresponding csv files for each subject.

# TODO: Link students and subjects by creating one relational file.csv:
# student1.csv, subject2.csv, subject3.csv, subject6.csv
# student5.csv, subject1.csv, subject2.csv
# ...

class FileHandler():
    error = '<N/A>'

    def __init__(self, filename, dir):
        self.filename = filename
        self.dir = dir

    def __call__(self, func, *args, **kwargs):
        try:
            return func(*args)

        except FileNotFoundError:
            # NOTE: `except RecursionError as e` will handle the
            # infinite recursion in case this function fails.
            FileHandler.create_dir_if_nonexistent(self)
            FileHandler(self.filename, self.dir)(self, func, *args, **kwargs)

        except RecursionError as e:
            e = str(e)
            e += f'.\nThis error most likely occurred because "{self.filename}" does not exist and cannot be created.'
            FileHandler.error = e
            FileHandler.__exit_with_error()

        except PermissionError as e:
            e = str(e)
            e += f'.\nMake the directory modifiable or grant this script the permission to modify it.'
            FileHandler.error = e
            FileHandler.__exit_with_error()

    def create_dir_if_nonexistent(self):
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)

    @staticmethod
    def __exit_with_error():
        sys.exit(f'ERROR: {FileHandler.error}')

    def get_list_of_files_sorted_by_date_from_dir(self):
        dir_handler = FileHandler(None, self.dir)
        dir_handler(os.chdir, self.dir) 
        list_of_files = os.listdir(self.dir)
        list_of_files.sort(key = os.path.getmtime)

        return list_of_files

    def get_contents_of_all_files_in_dir(self):
        files = FileHandler(None, self.dir).get_list_of_files_sorted_by_date_from_dir()
        list_of_contents = []

        for filename in files:
            with open(self.dir + filename, 'r') as cur_file:
                cur_contents = cur_file.read()
                list_of_contents.append(cur_contents)

        return list_of_contents

    def add_and_write_file_to_dir(self, contents):
        file_handler = FileHandler(self.filename, self.dir)
        file_handler.create_dir_if_nonexistent()
        full_path = str(self.dir + self.filename)
        file = file_handler(open, full_path, 'w')
        file.write(contents)

class Subjects():
    def __init__(self, subjects):
        self.subjects = subjects

    def generate_files(self):
        for key, values in self.subjects.items():
            filename = key + '.csv'
            values_in_csv_format = Subjects.__get_in_csv_format(self, values)
            FileHandler(filename, SUBJECTS_DIR_ABSOLUTE_PATH).add_and_write_file_to_dir(values_in_csv_format)
            print(f'Successfully generated "{SUBJECTS_DIR_ABSOLUTE_PATH}{filename}".')

    def list_all(self):
        subjects = Subjects.get_dict_of_subjects_from_files_in_dir(self)
        cnt = 1
        for subject in subjects.values():
            print(f'{cnt}) ', end='')
            i = 1
            for parameter in subject.values():
                is_last_iteration = i==len(subject.values())
                if not is_last_iteration:
                    print(f'{parameter}', end=', ')
                else:
                    print(f'{parameter}')
                i += 1
            cnt += 1

    def get_dict_of_subjects_from_files_in_dir(self):
        cnt = 0

        file_handler = FileHandler(None, SUBJECTS_DIR_ABSOLUTE_PATH)
        subject_files_contents = file_handler.get_contents_of_all_files_in_dir()
        list_of_subject_files = file_handler.get_list_of_files_sorted_by_date_from_dir()

        num_of_parameters = len(subject_files_contents[cnt].split(', '))
        keys = [ filename.replace('.csv', '') for filename in list_of_subject_files ]

        for key in keys:
            subject = {}

            for i in range(num_of_parameters):
                cur_param = subject_files_contents[cnt].replace('"', '').split(', ')[i].split(':')
                subject[cur_param[0]] = cur_param[1]

            subjects[key] = subject
            cnt += 1

        return subjects

    def __print_subject(self, subject):
        print(subject['name'])


    def __get_in_csv_format(self, values):
        values_no_braces = str(values).replace('{','').replace('}','')
        values_single_quotes = values_no_braces.replace('"',"'").replace("'", '"')
        values_in_csv_format = values_single_quotes.replace(': ',':')
        return values_in_csv_format

class Student():
    def __init__(self, parameters):
        self.parameters = parameters

    def get_parameter(self, parameter_name):
        if parameter_name in self.parameters:
            return self.parameters[ parameter_name ]
        else:
            raise TypeError(f'parameter {parameter_name} does not exist.')

    def set_parameter(self, parameter_name, parameter_value):
        if parameter_name in self.parameters:
            # TODO: Validate the parameter.
            self.parameters[ parameter_name ] = parameter_value
            return True
        else:
            return False

    def write_to_file(self):
        student_in_csv_format = Student.__get_in_csv_format(self)
        filename = Student.__generate_filename(self)
        FileHandler(filename, STUDENT_LIST_DIR_ABSOLUTE_PATH).add_and_write_file_to_dir(student_in_csv_format)

    def __get_in_csv_format(self):
        student_in_csv_format = ''

        i = 1
        for self.key, self.value in self.parameters.items():
            is_last_iteration = i==len(self.parameters)
            student_in_csv_format += Student.__get_parameter_with_delimiter(self, is_last_iteration)
            i += 1

        return student_in_csv_format

    def __get_parameter_with_delimiter(self, is_last_iteration):
        format = f'"{self.key}":"{self.value}"'
        if is_last_iteration:
            return format + '\n'
        else:
            return format + ', '

    def __generate_filename(self):
        first_name = self.parameters[ 'first_name' ]
        last_name = self.parameters[ 'last_name' ]
        extension = 'csv'
        filename = f'{first_name}_{last_name}.{extension}'
        return filename

class Validator():
    def __init__(self, entered_parameter):
        self.value = entered_parameter[ 'input_value' ]
        self.type = entered_parameter[ 'type' ]
        self.restrictions = entered_parameter[ 'restrictions' ]
        self.options = entered_parameter[ 'options' ]

        self.valid = False
        self.result = ''
        self.error = ''

    def is_valid(self):
        Validator.__validate_by_type(self)

        if self.valid:
            if self.restrictions:
                Validator.__validate_restrictions(self)

            if self.options:
                Validator.__validate_options(self)

        return self.valid

    def __validate_by_type(self):
        if self.type == 'string':
            Validator.__validate_string(self)
        elif self.type == 'number': 
            Validator.__validate_number(self)
        else:
            sys.exit('ERROR: Unknown parameter type.')

    def __validate_string(self):
        # NOTE: Any user input can be converted to string, so just return it.
        self.result = str(self.value)
        self.valid = True

    def __validate_number(self):
        try:
            self.result = float(self.value)
            self.valid = True
        except:
            self.error = 'The value is not a number.'
            self.valid = False

    def __validate_restrictions(self):
        for restriction in self.restrictions:
            if restriction == 'non-empty':
                Validator.__validate_non_empty_restriction(self, restriction)

            elif restriction == 'integer':
                Validator.__validate_integer_restriction(self)

            elif restriction == 'positive':
                Validator.__validate_positive_restriction(self, restriction)

            else:
                return

    def __validate_non_empty_restriction(self, restriction):
        try:
            Validator.__check_if_empty(self, self.result)
        except:
            Validator.__exit_with_error_invalid_restriction(self, restriction)

    def __check_if_empty(self, result):
        if result == '':
            self.error = 'The value is empty.'
            self.valid = False

    def __exit_with_error_invalid_restriction(self, restriction):
        sys.exit(f'ERROR: invalid restriction {restriction} for type {self.type}')

    def __validate_integer_restriction(self):
        try:
            Validator.__check_if_integer(self, self.result)
        except:
            self.error = 'The value is not an integer.'
            self.valid = False

    def __check_if_integer(self, result):
        if result == int(result):
            self.result = int(result)
        else:
            self.error = 'The value is a number but not an integer.'
            self.valid = False

    def __validate_positive_restriction(self, restriction):
        try:
            Validator.__check_if_positive(self, self.result)
        except:
            Validator.__exit_with_error_invalid_restriction(self, restriction)

    def __check_if_positive(self, result):
        if result <= 0:
            self.valid = False
            self.error = 'The value is not positive'

    def __validate_options(self):
        value_found = False

        for option in self.options:
            if option == self.result:
                value_found = True

        if not value_found:
            self.error = 'The value was not found in the list of valid options'
            self.valid = False

def main():
    initialisation()
    print_actions()
    while True:
        select_action()

def initialisation():
    global required_student_parameters, actions, subjects

    subjects = {
        'econ':    { 'name':'Economics',           'teacher':'Mr. Cameron Dron' }, \
        'p_maths': { 'name':'Pure Mathematics',    'teacher':'Mrs. Mojgan Estafani' }, \
        'a_maths': { 'name':'Applied Mathematics', 'teacher':'Mr. Richard Milner' }, \
        'eng':     { 'name':'English Language',    'teacher':'Mrs. Kira Ivanovna' }, \
        'cs':      { 'name':'Computer Science',    'teacher':'Mr. Anton Aleksandrovich' }, \
    }

    actions = [ 
        { 'description':'Quit',                          'function':quit },
        { 'description':'Add a new students',            'function':add_student },
        { 'description':'List all students',             'function':list_students },
        { 'description':'Edit an existing student',      'function':edit_student },
        { 'description':'List all subjects',             'function':Subjects(subjects).list_all },
        { 'description':'List all students by subjects', 'function':list_students_by_subjects },
        { 'description':'Generate subject files',        'function':Subjects(subjects).generate_files }
    ]

    required_student_parameters = {
        'first_name': { 'name':'first name', 'type':'string', 'restrictions':[ 'non-empty' ] },\
        'last_name':  { 'name':'last name',  'type':'string', 'restrictions':[ 'non-empty' ] }, \
        'age':        { 'name':'age',        'type':'number', 'restrictions':[ 'integer', 'positive' ] }, \
        'gender':     { 'name':'gender',     'type':'string', 'restrictions':[ 'non-empty' ], 'options':[ 'male', 'female' ] } \
    }

def print_actions():
    action_num = 0
    for action in actions:
        print(f'{action_num}) {action[ "description" ]}')
        action_num += 1
    print()

def select_action():
    selected_action = input('Please select an action: ')

    if not action_is_valid(selected_action):
        print('Error: invalid action.\n')
        print_actions()
        return

    # NOTE: Call a function corresponding to a selected action.
    actions[ int(selected_action) ][ 'function' ]()

def action_is_valid(selected_action):
    is_valid = selected_action.isdigit() and int(selected_action)>=0 and int(selected_action)<=len(actions)

    if is_valid:
        return True
    else:
        return False

def add_student():
    student_parameters = {}

    for i_parameter in required_student_parameters:
        parameter = required_student_parameters[ i_parameter ]
        student_parameters[ i_parameter ] = prompt_parameter_until_valid(parameter)

    student = Student(student_parameters)
    Student.write_to_file(student)

def prompt_parameter_until_valid(parameter):
    entered_parameter = enter_parameter(parameter)
    while not parameter_is_valid(entered_parameter):
        entered_parameter = enter_parameter(parameter)

    return entered_parameter[ 'input_value' ]

def enter_parameter(parameter):
    input_prompt = "Please enter the student's " + parameter[ 'name' ]

    options = None
    has_options = 'options' in parameter and len(parameter[ 'options' ])>0
    if has_options:
        options = parameter[ 'options' ]
        input_prompt += list_parameter_options(options)

    input_value = input(input_prompt + ": ")

    entered_parameter = { 
        'input_value':input_value,\
        'type':parameter[ 'type' ],\
        'restrictions':parameter[ 'restrictions' ],\
        # WARNING: Can return None.
        'options':options
    }

    return entered_parameter

def list_parameter_options(options):
    options_list = ''
    for option in options:
        if len(options_list) > 0:
            options_list += (f", '{option}'")
        else:
            options_list += (f"'{option}'")

    input_prompt = ("; possible values are " + options_list)
    return input_prompt

def parameter_is_valid(entered_parameter):
    validation_result = Validator(entered_parameter)

    if validation_result.is_valid():
        return True
    else:
        print("Error: " + validation_result.error)

def list_students():
    raw_list_of_students = FileHandler(None, STUDENT_LIST_DIR_ABSOLUTE_PATH).get_contents_of_all_files_in_dir()

    if list_of_students_is_empty(raw_list_of_students):
        print('There are no students in the list.')
        return
    else:
        print_each_student(raw_list_of_students)

def list_of_students_is_empty(students):
    if len(students) == 0:
        return True
    else:
        return False

def print_each_student(raw_list_of_students):
    student_num = 1
    for raw_student in raw_list_of_students:
        print(f'Student #{student_num}')

        print_student(raw_student)

        student_num += 1

def print_student(raw_student):
    parameter_num = 1

    str_raw_student_parameters = raw_student.split(', ')
    for str_raw_parameter in str_raw_student_parameters:
        print(f'{parameter_num}) ', end='')

        print_parameter(str_raw_parameter)

        parameter_num += 1

def print_parameter(str_raw_parameter):
    key_value_pair = str_raw_parameter.split(':')
    key = key_value_pair[ 0 ].replace('"', '')
    value = key_value_pair[ 1 ].replace('"', '')

    for req_parameter_key in required_student_parameters.keys():
        parameter_name = get_parameter_name_by_matching_keys(key, req_parameter_key)
        if parameter_name != None:
            print_formatted_student_parameter(parameter_name, value)

def get_parameter_name_by_matching_keys(key, req_parameter_key):
    if key == req_parameter_key:
        parameter_name = required_student_parameters[ req_parameter_key ][ 'name' ].capitalize()
        return parameter_name
    else:
        # WONTFIX: this function is intended to be used only in
        # print_parameter(...), where there is a check for None.
        return None

def print_formatted_student_parameter(parameter_name, parameter_value):
    print(f'{parameter_name}: {parameter_value}')

# TODO
def edit_student():
    pass

# TODO
def list_subjects():
    pass

# TODO
def list_students_by_subjects():
    pass

if __name__ == '__main__':
    # Logging
    lvl = logging.DEBUG 
    fmt = '%(lineno)s: [%(levelname)s] %(msg)s'
    logging.basicConfig(level = lvl, format = fmt)

    main()
