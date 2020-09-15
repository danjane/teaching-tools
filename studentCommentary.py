import pandas as pd
import studentFunctions as sF

pd.set_option('display.max_colwidth', None)
pensees = sF.scrape_pensees()


def student_notes_for_latex(student_, course_):
    notes_df = pensees[pensees['Student'].isin([student_])]
    notes_df = notes_df[['Date', 'Info']]

    s = list('\\begin{minipage}[t][\\textheight]{\\textwidth} \n{\\large \\textbf{' + student_ + '}}\\hfill ')

    s.append(course_ + '\n\\vspace{1cm}\n\n')
    s.append(notes_df.to_latex(index=False, escape=False))
    s.append('\n\\vfill')

    s.append('\n\\begin{minipage}[t]{0.5\\textwidth}')
    s.append('\n\\includegraphics[width = 0.8\\textwidth]{' + student_.replace(" ", "") + '_Sentiment.png}')
    s.append('\\end{minipage}')

    s.append('\n\\begin{minipage}[t]{0.5\\textwidth}')
    s.append('\n\\includegraphics[width = 0.8\\textwidth]{' + student_.replace(" ", "") + '_Notes.png}')
    s.append('\\end{minipage}')

    s.append('\n\n\\end{minipage}\n\n\\newpage \n\n')

    return ''.join(s)


def main():
    report = []
    for course in sF.courses():
        for student in sF.classes[course].keys():
            report.append(student_notes_for_latex(student, course))

    report = ''.join(report)

    report_file = sF.report_filepath()
    skeleton_file = sF.report_skeleton_file()

    with open(skeleton_file, 'r') as f:
        latex_str = f.read()

    with open(report_file, 'w') as f:
        f.write(latex_str.replace('ReportHere', report))

    # Finish off with some useful info
    sF.positive_comments(pensees)
    print('\nReport written to: {:s}'.format(report_file))


if __name__ == "__main__":
    main()
