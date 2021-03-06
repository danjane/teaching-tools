import numpy as np
import pandas as pd
import re
import datetime
import dateutil
import os
import copy
import yaml


def load_config(config_file=None):
    if not config_file:
        config_file = os.path.join(os.getcwd(), 'config.yaml')
        config_file = config_file.replace('sandpit/config.yaml', 'config.yaml')

    if os.path.isfile(config_file):
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
    else:
        raise FileNotFoundError('no config.yaml file found!! Searched in {}'.format(config_file))

    # Use default skeleton files if not given
    if not 'report_skeleton_file' in config:
        config['report_skeleton_file'] = os.path.abspath(
            os.path.join('example_files', 'Latex', 'Report_Skeleton.tex'))
    if not 'marks_skeleton_file' in config:
        config['marks_skeleton_file'] = os.path.abspath(
            os.path.join('example_files', 'Latex', 'Marks_Skeleton.tex'))
    if not 'seatingplan_skeleton_file' in config:
        config['seatingplan_skeleton_file'] = os.path.abspath(
            os.path.join('example_files', 'Latex', 'SeatingPlan_Skeleton.tex'))

    if 'front_row' not in config:
        config['front_row'] = []

    return config


config = load_config()

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


def seatingplan_skeleton():
    with open(config['seatingplan_skeleton_file'], 'r') as f:
        latex_str = f.read()
    return latex_str


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
            first_name = first_name.split(' ')[0] # take first given name, e.g. 'James Dan' -> 'James'

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
    raise NotImplementedError('needs to be redone')
    return open(config['student_class_path'].replace('COURSE', filename), open_type)


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
    file_name = config['pensees_filepath']
    print("Loading pensees file {}".format(file_name))
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
                # new_day_flag = False TODO(Dan): dateparser v slow, does this help?
                continue
            except ValueError as e:
                pass

        # Hash to ignore the line
        if line[0] == '#':
            continue

        # Actual information
        if line in classes:
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
    if np.isscalar(note):
        if np.isnan(note):
            return 1.
        else:
            note = np.maximum(1.5, np.minimum(6., note))

    else:
        nidx = np.isnan(note)
        note[nidx] = 1.5
        note = np.maximum(1.5, np.minimum(6., note))
        note[nidx] = 1

    return np.round(note / step) * step


def positive_comments(pensees):
    # Should highlight students to engage with
    print('Positive comments needed for:')

    for course in config['courses']:
        pensees_class = pensees[pensees['Class'].isin([course]) & ~pensees['Student'].isin(['general'])]

        # Handle edge case that some students haven't been mentioned yet by putting one zero for everyone
        students = list(classes[course].keys())
        base = pd.DataFrame({'Student': students, 'Weight': [0] * len(students)})

        pensees_class = pd.concat([pensees_class, base], sort=False)

        student_weights = pensees_class.groupby(['Student']).agg({'Weight': 'sum'})
        student_weights.sort_values('Weight', inplace=True)

        student_weights = student_weights.head(7)
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


def exam_files(course_):
    path_ = os.path.join(config['exam_path'], course_)
    files = os.listdir(path_)

    words_re = re.compile(r'Notes.xlsx*\Z')  # picks up both xls and xlsx files
    files = list(filter(lambda t: words_re.search(t), files))
    print(files)
    return files, path_


def get_date(exam_file_name):
    date = exam_file_name.split('_')[0]
    return dateutil.parser.parse(date)


def get_date_name(exam_file_name):
    filename_parts = exam_file_name.split('_')
    date = filename_parts[0]
    name = filename_parts[1]
    return dateutil.parser.parse(date), name


def merge_exams(course_):
    files, path_ = exam_files(course_)

    # Allow for adding a new student to a class, read the list from the student file
    students = classes[course_].keys()
    notes_ = [pd.DataFrame(index=students)]

    noted_exams_ = []
    not_noted_exams_ = []
    exam_names_ = []
    for f in files:
        d, name = get_date_name(f)
        if f in config['noted_exams']:
            noted_exams_.append(d)
        else:
            not_noted_exams_.append(d)

        r, n = exam_marks(os.path.join(path_, f))
        n = n.rename(columns={"Note": d})
        notes_.append(n)
        exam_names_.append(name)

    notes_ = pd.concat(notes_, axis=1, sort=True)

    return notes_, noted_exams_, not_noted_exams_, exam_names_


def seatingplan_filename(txt=None):
    if txt is None:
        txt = 'test.tex'
    elif txt[-4:] != '.tex':
        txt += '.tex'

    return os.path.join(config['seatingplan_output_path'], txt)


def m(x, w=np.nan):
    """Weighted Mean"""
    if np.isnan(np.sum(w)):
        w = np.ones(np.shape(x))
    return np.sum(x * w) / np.sum(w)


def cov(x, y, w=np.nan):
    """Weighted Covariance"""
    if np.isnan(np.sum(w)):
        w = np.ones(np.shape(x))
    return np.sum(w * (x - m(x, w)) * (y - m(y, w))) / np.sum(w)


def corr(x, y, w=np.nan):
    """Weighted Correlation"""
    if np.isnan(np.sum(w)):
        w = np.ones(np.shape(x))
    nidx = [not np.isnan(xx + yy + ww) for xx, yy, ww in zip(x, y, w)]
    return cov(x[nidx], y[nidx], w[nidx]) / np.sqrt(cov(x[nidx], x[nidx], w[nidx]) * cov(y[nidx], y[nidx], w[nidx]))


def dict_of_correlations(results):
    """Return a dict where each student points to a couple (another student, correlation)"""

    # results from exam_marks(xls_file)
    students = list(results.index)

    # Handy look up of each student's results
    d = {}
    for s in students:
        d[s] = results.loc[s].values

    c = {}
    for s in students:
        c[s] = []
        for t in students:
            # Calculate the correlation and include the student name
            c[s].append((t, corr(d[s], d[t])))

    return c


# From rosettacode.org/wiki/Stable_marriage_problem#Python
def matchmaker(guyprefers, galprefers):
    guysfree = list(guyprefers.keys())
    engaged = {}
    guyprefers2 = copy.deepcopy(guyprefers)
    galprefers2 = copy.deepcopy(galprefers)
    while guysfree:
        guy = guysfree.pop(0)
        guyslist = guyprefers2[guy]
        gal = guyslist.pop(0)
        fiance = engaged.get(gal)
        if not fiance:
            # She's free
            engaged[gal] = guy
            print("  %s and %s" % (guy, gal))
        else:
            # The bounder proposes to an engaged lass!
            galslist = galprefers2[gal]
            if galslist.index(fiance) > galslist.index(guy):
                # She prefers new guy
                engaged[gal] = guy
                print("  %s dumped %s for %s" % (gal, fiance, guy))
                if guyprefers2[fiance]:
                    # Ex has more girls to try
                    guysfree.append(fiance)
            else:
                # She is faithful to old fiance
                if guyslist:
                    # Look again
                    guysfree.append(guy)
    return engaged


def courses():
    return config['courses']


def report_skeleton_file():
    return config['report_skeleton_file']


def marks_skeleton_file():
    return config['marks_skeleton_file']


def report_filepath():
    return config['report_filepath']


# Load courses on startup
for c in config['courses']:
    class_file = os.path.join(config['courses_path'], c + '.txt')
    classes[c] = load_student_file(class_file)

if config['rg_class']:
    class_file = os.path.join(config['courses_path'], config['rg_class'] + '.txt')
    classes[config['rg_class']] = load_student_file(class_file)