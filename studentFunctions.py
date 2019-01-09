import numpy as np
import pandas as pd
import re
import datetime
import dateutil
import matplotlib


# Find this year's information
import elevesPaths
student_class_path = elevesPaths.student_class_path
courses = elevesPaths.courses
rg_class = elevesPaths.rg_class


horaires = {
    'H1':  datetime.time( 8,  0),
    'H2':  datetime.time( 8, 50),
    'H3':  datetime.time( 9, 55),
    'H4':  datetime.time(10, 45),
    'H5':  datetime.time(11, 35),
    'H6':  datetime.time(12, 30),
    'H7':  datetime.time(13, 20),
    'H8':  datetime.time(14, 10),
    'H9':  datetime.time(15, 10),
    'H10': datetime.time(16, 00),
    'H11': datetime.time(16, 50),
    }


# Define classes and pensees when loaded
classes = {}


def load_student_file(f):
    f = open(f)
    students = {}
    for s in f.readlines():
        student = s.strip().split(', ')
        full_name = student[0]
        if len(student) > 1:
            # Has a given name
            first_name = student[1]
        else:
            # Take Title name
            first_name = re.search(r'[A-Z][a-z].+$', student[0]).group(0)
        students[full_name] = first_name

    return students


def find_students_in_info(str, course):
    students = []
    for full_name, first_name in classes[course].items():
        words_re = re.compile(r'\b' + first_name + r'\b')
        t = words_re.search(str)
        if t:
            students.append(full_name)

    if len(students) == 0:
        students = ['general']

    return students


def open_file(filename, open_type='r'):
    return open(student_class_path.replace('COURSE', filename), open_type)


def check_pensees(pensees, file_name):
    problems = pensees[pensees.Sentiment & pensees.Student.isin(['general'])]

    if len(problems) > 0:
        print('Problem while scraping pensees file {:s}'.format(file_name))
        print(problems)
        print(problems.iloc[0]['Info'])
        raise AssertionError('General comments should not have sentiments (+ -)!!')

    dates = pensees.Date.values
    d_flag = [dates[i] > dates[i + 1] for i in range(len(dates) - 1)]
    if any(d_flag):
        print('Problem while scraping pensees file {:s}'.format(file_name))
        print(dates[np.argmax(d_flag)])
        raise AssertionError('Dates are not ordered in pensees files!')


# Scrape the pensees file
def scrape_pensees():
    file_name = student_class_path.replace('COURSE', 'Pensees')
    with open(file_name, 'r') as f:
        pensees_file = [s.strip() for s in f.readlines()]

    current_info = {}
    pensees = pd.DataFrame()

    new_day_flag = True
    for line in pensees_file:

        # Blank line means we might be starting a new day
        if len(line) < 1:
            new_day_flag = True
            continue
        if new_day_flag:
            try:
                current_info['Date'] = [dateutil.parser.parse(line)]
                continue
            except ValueError as e:
                pass

        # Hash to ignore the line
        if line[0] == '#':
            continue

        # Actual information
        if line in courses:
            current_info['Class'] = [line]
        else:
            students = find_students_in_info(line, current_info['Class'][0])
            current_info['Info'] = [line]
            for student in students:
                current_info['Student'] = [student]
                pensees = pd.concat([pensees, pd.DataFrame(current_info)])

    pensees.reset_index(drop=True)

    pensees['Sentiment'] = pensees.apply(lambda row: row['Info'][0] in {'+', '-'}, axis=1)
    pensees['Positive'] = pensees.apply(lambda row: row['Info'][0] == '+', axis=1)

    # Create series object of delta dates
    date_diffs = (pensees['Date'] - max(pensees['Date'])).apply(lambda x: x.days)
    pensees['Weight'] = date_diffs.apply(lambda x: np.exp(x / 10.))

    check_pensees(pensees, file_name)

    return pensees


def first_name(student, course):
    return classes[course][student]


def round_note(note, step=0.5):
    if np.isnan(note):
        return 1.
    else:
        note = np.maximum(1., np.minimum(6., note))
        return round(note / step) * step


def positive_comments(pensees):
    # Should highlight students to engage with
    print('Positive comments needed for:')

    for course in courses - {rg_class}:
        pensees_class = pensees[pensees['Class'].isin([course]) & ~pensees['Student'].isin(['general'])]

        student_weights = pensees_class.groupby(['Student']).agg({'Weight': 'sum'})
        student_weights.sort_values('Weight', inplace=True)

        student_weights = student_weights.head(5)
        first_names = [first_name(student, course) for student in student_weights.index]

        print('\n' + course + '\n+' + '\n+'.join(first_names))


def exam_marks(xls_file):
    print('reading {:s}'.format(xls_file))
    df_exam_results = pd.read_excel(xls_file, sheet_name="Sheet1")

    # Find the questions
    question_count = 1
    while not df_exam_results.columns[question_count].startswith('Unnamed'):
        question_count += 1

    # Find the student rows
    def students():
        idx = df_exam_results.Questions.copy().values

        count = 0
        while not idx[count] == 'Student':
            idx[count] = False
            count += 1

        idx[count] = False
        count += 1

        while isinstance(idx[count], str):
            idx[count] = True
            count += 1

        idx[count:] = False
        return idx

    student_idx = students()

    def students_as_idx(df):
        df.rename(columns={'Questions': 'Student'}, inplace=True)
        df.set_index('Student', inplace=True)

        # Need to handle accidentally including used names (mistake in Notes.xls files)
        old_names = df.index[:]
        new_names = [t.split(',')[0] for t in old_names]
        dictionary = dict(zip(old_names, new_names))
        df.rename(dictionary, axis='index', inplace=True)

        return df

    # Pull off results per question...
    results = df_exam_results[student_idx][df_exam_results.columns[:question_count]]
    results = students_as_idx(results)

    # ... and the overall note given
    notes = df_exam_results[student_idx][['Questions', 'Note']]
    notes = students_as_idx(notes)

    return results, notes


def read_exam(xls_file):
    results, notes = exam_marks(xls_file)
    descriptions = pd.read_excel(xls_file, sheet_name="Sheet2")
    return results, notes, descriptions


# Load courses on startup
for c in courses:
    classes[c] = load_student_file(
        student_class_path.replace('COURSE', c))

