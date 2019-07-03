import sys
import os.path
import pandas as pd
import studentFunctions as sF


def student_notes_for_latex(results_, notes_, descriptions_, student_, exam_, date_):
    descriptions_['Mark'] = (results_.loc[student_]).values.T

    string = '\\begin{minipage}[t]{\\textwidth}\n'
    string += '\section*{\centering Exam: ' + exam_ + ', ' + date_ + ' }\n'
    string += '\\textbf{' + student_ + ', ' + "{:.1f}".format(notes_.loc[student_].values[0]) + '}'
    string += '\n\\vspace{1em}\n\n\\rowcolors{1}{}{lightgray}'

    string += descriptions_.to_latex(decimal=',', index=False, escape=False)

    string += '\\end{minipage}\n\n\\newpage\n\n'

    # don't want NaNs for non-programmers
    string = string.replace('NaN', '')

    return string


def main():
    pd.set_option('display.max_colwidth', -1)

    xls_file = sys.argv[1]

    results, notes, descriptions = sF.read_exam(xls_file)
    notes = notes[notes.Note > 0]  # only for students who took the exam
    notes.Note = [sF.round_note(n) for n in notes.Note]
    descriptions.drop(['Weight'], axis=1, inplace=True)

    path, file = os.path.split(xls_file)
    date, exam, type_ = file.split('_')

    report_file = os.path.join(path, "{:s}_{:s}_Marks.tex".format(date, exam))
    skeleton_file = sF.student_class_path.replace('COURSE.txt', 'Latex/Marks_Skeleton.tex')

    report = ''
    for student in notes.index:
        report += student_notes_for_latex(results, notes, descriptions, student, exam, date)

    with open(skeleton_file, 'r') as f:
        latex_str = f.read()

    with open(report_file, 'w') as f:
        f.write(latex_str.replace('ReportHere', report))

    print(report_file)


if __name__ == "__main__":
    main()
