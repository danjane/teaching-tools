import numpy as np
import pandas as pd

import studentFunctions as sF
import studentCommentary

# Tests for round_note


def test_round_single_note():
    assert sF.round_note(4.4) == 4.5


def test_round_list_note():
    assert sF.round_note(np.array([2.4])) == [2.5]


def test_round_nan_note():
    assert sF.round_note(np.nan) == 1


def test_round_list_notes():
    assert np.all(sF.round_note(np.array([4.4, 3.6])) == [4.5, 3.5])


def test_round_list_notes_tenth():
    assert np.all(sF.round_note(np.array([4.41, 3.67, 4.92]), 0.1) == [4.4, 3.7, 4.9])


def test_round_single_note_hundredth():
    assert sF.round_note(2.22222, 0.01) == 2.22


# Tests for loading and processing

def test_loading_students():
    expected = {
        'CRAMER Gabriel': 'Gabriel',
        'CURIE Marie': 'Marie',
        'EINSTEIN Albert': 'Albert',
        'FEYNMAN Richard': 'Dick'}
    assert sF.load_student_file('./example_files/example_class.txt') == expected


def test_scrape_pensees():
    example_class = sF.load_student_file('./example_files/example_class.txt')  # TODO(dan) where should this be?

    sF.courses = ['example_class']
    sF.student_class_path = './example_files/COURSE.txt'
    sF.courses = ['example_class']
    sF.rg_class = None
    sF.classes = {'example_class': example_class}

    expected_pensees = pd.read_csv('example_pensees_scrape.csv')

    example_pensees = sF.scrape_pensees()
    example_pensees.reset_index(inplace=True)
    example_pensees.drop(columns=['index'], inplace=True)

    for col in expected_pensees:
        if col in ['Date', 'Weight']:
            continue
        assert (example_pensees[col] == expected_pensees[col]).all()  # TODO(dan) why is all not happy?


def test_report():
    example_class = sF.load_student_file('./example_files/example_class.txt')

    sF.courses = ['example_class']
    sF.student_class_path = './example_files/COURSE.txt'
    sF.courses = ['example_class']
    sF.rg_class = None
    sF.classes = {'example_class': example_class}

    studentCommentary.pensees = sF.scrape_pensees()
    assert studentCommentary.student_notes_for_latex('EINSTEIN Albert', 'example_class') == (
        "\\begin{minipage}[t][\\textheight]{\\textwidth} \n{\\large \\textbf{EINSTEIN Albert}}\\hfill example_class\n\\"
        "vspace{1cm}\n\n\\begin{tabular}{ll}\n\\toprule\n      Date &                                    Info \\\\\n"
        "\\midrule\n2018-08-27 &  -Albert s'ennui en classe \\\\\n2018-08-28 &  +Albert interagis bien avec les autres "
        "\\\\\n\\bottomrule\n\\end{tabular}\n\n\\vfill\n\\begin{minipage}[t]{0.5\\textwidth}\n\\includegraphics[width ="
        " 0.8\\textwidth]{EINSTEINAlbert_Sentiment.png}\\end{minipage}\n\\begin{minipage}[t]{0.5\\textwidth}\n\\include"
        "graphics[width = 0.8\\textwidth]{EINSTEINAlbert_Notes.png}\\end{minipage}\n\n\\end{minipage}\n\n\\newpage \n\n"
    )
