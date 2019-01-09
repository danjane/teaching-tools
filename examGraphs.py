import studentFunctions as sF
import pandas as pd
import dateutil
import os
import elevesPaths
import re
import matplotlib.pyplot as plt
import matplotlib


def exam_files(course_):
    path_ = os.path.join(elevesPaths.exam_path, course_)
    files = os.listdir(path_)

    words_re = re.compile('Notes.xls') #picks up both xls and xlsx files
    files = list(filter(lambda t: words_re.search(t), files))
    print(files)
    return files, path_


def get_date(exam_file_name):
    date = exam_file_name.split('_')[0]
    return dateutil.parser.parse(date)


def merge_exams(c):
    files, path_ = exam_files(c)

    notes_ = []
    noted_exams_ = []
    not_noted_exams_ = []
    for f in files:
        d = get_date(f)
        if f in elevesPaths.noted_exams:
            noted_exams_.append(d)
        else:
            not_noted_exams_.append(d)

        r, n = sF.exam_marks(os.path.join(path_, f))
        n = n.rename(columns={"Note": d})
        notes_.append(n)

    notes_ = pd.concat(notes_, axis=1, sort=True)

    return notes_, noted_exams_, not_noted_exams_


def exam_plot(student_, notes_, noted_array, show=False, file_name=''):
    fig, ax = plt.subplots()

    def part_plot(ax, results, marker):
        dates = matplotlib.dates.date2num(results.index.tolist())
        results = [sF.round_note(r) for r in results.values]
        ax.plot(dates, results, marker=marker, markersize=12, linestyle='none')

    part_plot(ax, notes_.loc[student_, noted_array[0]], 'D')
    part_plot(ax, notes_.loc[student_, noted_array[1]], '.')

    myFmt = matplotlib.dates.DateFormatter('%d-%b')
    plt.xlim()
    ax.xaxis.set_major_formatter(myFmt)
    ax.xaxis.grid(True)

    plt.ylim((0.9, 6.1))
    ax.yaxis.grid(True)

    plt.title("notes")

    if len(file_name) > 0:
        plt.savefig(file_name)
        plt.close()

    if show:
        plt.show(block=True)
    else:
        plt.close()


if __name__ == "__main__":
    plt.rcParams["figure.figsize"] = (8, 5)

    path, file = os.path.split(elevesPaths.student_class_path)
    path = os.path.join(path, "Latex", "Images.nosync")  # nosync to stop iCloud uploading all images

    for course in sF.courses - {sF.rg_class}:
        print(course)
        notes, noted_exams, not_noted_exams = merge_exams(course)

        for student in sF.classes[course].keys():
            print(student)
            image_file = os.path.join(path, "{:s}_Notes.png".format(student).replace(" ", ""))
            exam_plot(student, notes, (noted_exams, not_noted_exams), file_name=image_file)


