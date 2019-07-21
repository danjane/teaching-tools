import pandas as pd
import studentFunctions as sF

pd.set_option('display.max_colwidth', -1)
pensees = sF.scrape_pensees()


def student_notes_for_latex(student_, course_):
    notes_df = pensees[pensees['Student'].isin([student_])]
    notes_df = notes_df[['Date', 'Info']]

    s = '\\begin{minipage}[t][\\textheight]{\\textwidth} \n{\\large \\textbf{' + student_ + '}}\\hfill '
    s += course_ + '\n\\vspace{1cm}\n\n'
    s += notes_df.to_latex(index=False)
    s += '\n\\vfill'

    s += '\n\\begin{minipage}[t]{0.5\\textwidth}'
    s += '\n\\includegraphics[width = 0.8\\textwidth]{' + student_.replace(" ", "") + '_Sentiment.png}'
    s += '\\end{minipage}'

    s += '\n\\begin{minipage}[t]{0.5\\textwidth}'
    s += '\n\\includegraphics[width = 0.8\\textwidth]{' + student_.replace(" ", "") + '_Notes.png}'
    s += '\\end{minipage}'

    s += '\n\n\\end{minipage}\n\n\\newpage \n\n'

    return s


def main():
    report = ''
    for course in sF.courses - {sF.rg_class}:
        for student in sF.classes[course].keys():  # TODO(dan) add each substring to a list and afterwards ''.join the list
            report += student_notes_for_latex(student, course)

    #  nums = [str(n) for n in range(20)]
    # print "".join(nums)

    report_file = sF.student_class_path.replace('COURSE.txt', 'Latex/report.tex')
    skeleton_file = sF.student_class_path.replace('COURSE.txt', 'Latex/report_skeleton.tex')

    with open(skeleton_file, 'r') as f:
        latex_str = f.read()

    with open(report_file, 'w') as f:
        f.write(latex_str.replace('ReportHere', report))

    # Finish off with some useful info
    sF.positive_comments(pensees)
    print('\nReport written to: {:s}'.format(report_file))


if __name__ == "__main__":
    main()
