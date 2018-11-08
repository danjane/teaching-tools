import pandas as pd

import studentFunctions as sF

pd.set_option('display.max_colwidth', -1)
pensees = sF.scrape_pensees()


def student_notes_for_latex(student):
    notes_df = pensees[pensees['Student'].isin([student])]
    notes_df = notes_df[['Date', 'Info']]

    s = '\\begin{minipage}[t][\\textheight]{\\textwidth} \n{\\large \\textbf{' + student + '}}\\hfill '
    s += course + '\n\\vspace{1cm}\n\n'
    s += notes_df.to_latex(index=False)
    s += '\n\\vfill'

    s += '\n\\begin{minipage}[t]{0.5\\textwidth}'
    s += '\n\\includegraphics[width = 0.8\\textwidth]{' + student.replace(" ", "") + '_Sentiment.png}'
    s += '\\end{minipage}'

    s += '\n\\begin{minipage}[t]{0.5\\textwidth}'
    s += '\n\\includegraphics[width = 0.8\\textwidth]{' + student.replace(" ", "") + '_Notes.png}'
    s += '\\end{minipage}'

    s += '\n\n\\end{minipage}\n\n\\newpage \n\n'

    return s


report = ''
for course in sF.courses - {sF.rg_class}:
    for student in sF.classes[course].keys():
        report += student_notes_for_latex(student)


report_file = sF.student_class_path.replace('COURSE.txt', 'Latex/report.tex')
skeleton_file = sF.student_class_path.replace('COURSE.txt', 'Latex/report_skeleton.tex')

with open(skeleton_file, 'r') as f:
    latex_str = f.read()

with open(report_file, 'w') as f:
    f.write(latex_str.replace('ReportHere', report))

# Finish off with some useful info
sF.positive_comments(pensees)
print('\nReport written to: {:s}'.format(report_file))
