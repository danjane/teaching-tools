import studentFunctions as sF
import os
import elevesPaths
import matplotlib.pyplot as plt
import matplotlib


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


def main():
    plt.rcParams["figure.figsize"] = (8, 5)

    path, file = os.path.split(elevesPaths.student_class_path)
    path = os.path.join(path, "Latex", "Images.nosync")  # nosync to stop iCloud uploading all images

    for course in sF.courses - {sF.rg_class}:
        print(course)
        notes, noted_exams, not_noted_exams, exam_names = sF.merge_exams(course)

        for student in sF.classes[course].keys():
            print(student)
            image_file = os.path.join(path, "{:s}_Notes.png".format(student).replace(" ", ""))
            exam_plot(student, notes, (noted_exams, not_noted_exams), file_name=image_file)


if __name__ == "__main__":
    main()
