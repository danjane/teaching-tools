import re
import dateutil
import numpy as np
import pandas as pd


# Find this year's information
import elevesPaths
student_class_path = elevesPaths.student_class_path
courses = elevesPaths.courses
rg_class = elevesPaths.rg_class


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


# Scrape the pensees file
def scrape_pensees():
    with open_file('Pensees') as f:
        pensees_file = [s.strip() for s in f.readlines()]

    current_info = {}
    pensees = pd.DataFrame()

    new_day_flag = True
    for line in pensees_file:
        if len(line) < 1:
            new_day_flag = True
            continue

        if new_day_flag:
            try:
                current_info['Date'] = [dateutil.parser.parse(line)]
                continue
            except ValueError as e:
                pass

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

    return pensees


def first_name(student, course):
    return classes[course][student]


def positive_comments(pensees):
    # Should highlight students to engage with
    print('Positive comments needed for:')

    for course in courses - {rg_class}:
        pensees_class = pensees[pensees['Class'].isin([course]) & ~pensees['Student'].isin(['general'])]

        student_weights = pensees_class.groupby(['Student']).agg({'Weight': 'sum'})
        student_weights.sort_values('Weight', inplace=True)

        student_weights = student_weights.head(5)
        first_names = [first_name(student, course) for student in student_weights.index]

        print('\n' + course)
        print(' '.join(first_names))


def exam_marks(xlsx_file):
    df_exam_results = pd.read_excel(xlsx_file, sheet_name="Sheet1")

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
        return df

    # Pull off results per question...
    results = df_exam_results[student_idx][df_exam_results.columns[:question_count]]
    results = students_as_idx(results)

    # ... and the overall note given
    notes = df_exam_results[student_idx][['Questions', 'Note']]
    notes = students_as_idx(notes)

    return results, notes


# Load courses on startup
for c in courses:
    classes[c] = load_student_file(
        student_class_path.replace('COURSE', c))

