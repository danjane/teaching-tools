import os.path
import numpy as np
import pandas as pd
import sklearn.preprocessing

import studentFunctions as sF
import elevesPaths

import matplotlib.pyplot as plt
import matplotlib

plt.rcParams["figure.figsize"] = (8, 5)

path, file = os.path.split(elevesPaths.student_class_path)
path = os.path.join(path, "Latex", "Images.nosync")  # nosync to stop iCloud uploading all images


def sentiments_df(p, course):
    df = p[p['Class'].isin([course]) & p.Sentiment]
    df = df[['Date', 'Student', 'Positive']]
    df.reindex()

    df['DayCount'] = (df['Date'] - min(df['Date'])).apply(lambda x: x.days + 1)

    le = sklearn.preprocessing.LabelEncoder()
    le.fit(list(sF.classes[course].keys()))
    df.Student = le.transform(df.Student)

    return df, le


def student_sentiment_in_class(student, student_sentiments, le, xd, show=False, file_name=''):
    position = le.transform([student])

    fig, ax = plt.subplots()

    ax.plot(xd, student_sentiments, '0.8')
    ax.plot(xd, student_sentiments[:, position], 'k')

    myFmt = matplotlib.dates.DateFormatter('%d-%b')
    ax.xaxis.set_major_formatter(myFmt)
    ax.xaxis.grid(True)
    ax.set_yticklabels([])

    plt.title("indication du sentiment")
    if len(file_name) > 0:
        plt.savefig(file_name)

    if show:
        plt.show(block=True)
    else:
        plt.close()


def sentiments(df, le):
    n_weights = 5

    weights = np.exp(np.linspace(0, -1, n_weights))

    ss = np.zeros((max(df.DayCount) + n_weights, len(le.classes_)))
    for row in df.itertuples():
        dc = getattr(row, "DayCount")
        if getattr(row, "Positive"):
            # Note, if I give multiple comments in succession the last counts more
            ss[dc:dc + n_weights, getattr(row, "Student")] = +weights
        else:
            ss[dc:dc + n_weights, getattr(row, "Student")] = -weights

    ss = ss[:-n_weights, :]
    ss = np.cumsum(ss, axis=0)

    return ss


def main():
    p = sF.scrape_pensees()
    for course in sF.courses - {sF.rg_class}:
        df, le = sentiments_df(p, course)
        student_sentiments = sentiments(df, le)

        list_of_datetimes = pd.date_range(min(df.Date), max(df.Date))
        dates = matplotlib.dates.date2num(list_of_datetimes)

        for student in sF.classes[course].keys():
            print(student)
            image_file = os.path.join(path, "{:s}_Sentiment.png".format(student).replace(" ", ""))
            student_sentiment_in_class(student, student_sentiments, le, dates, file_name=image_file)

if __name__ == "__main__":
    main()
