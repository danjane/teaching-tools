import os.path
import numpy as np
import pandas as pd
import sklearn.preprocessing

import studentFunctions as sF
import elevesPaths

import matplotlib.pyplot as plt
import matplotlib

path, file = os.path.split(elevesPaths.student_class_path)
path = os.path.join(path, "Latex", "Images.nosync")  # nosync to stop iCloud uploading all images


def sentiments_df(course):
    df = p[p['Class'].isin([course]) & p.Sentiment]
    df = df[['Date', 'Student', 'Positive']]
    df.reindex()

    df['DayCount'] = (df['Date'] - min(df['Date'])).apply(lambda x: x.days + 1)

    le = sklearn.preprocessing.LabelEncoder()
    le.fit(list(sF.classes[course].keys()))
    df.Student = le.transform(df.Student)

    return df, le


def student_sentiment_in_class(student, show=False):
    position = le.transform([student])

    fig, ax = plt.subplots()

    ax.plot(dates, student_sentiments, '0.8')
    ax.plot(dates, student_sentiments[:, position], 'k')

    myFmt = matplotlib.dates.DateFormatter('%d-%b')
    ax.xaxis.set_major_formatter(myFmt)
    ax.xaxis.grid(True)
    ax.set_yticklabels([])

    plt.title("indication du sentiment")
    plt.savefig(image_file)
    plt.close()

    if show:
        plt.show(block=True)


def sentiments(df):
    n_weights = 5

    weights = np.exp(np.linspace(0, -1, n_weights))

    student_sentiments = np.zeros((max(df.DayCount) + n_weights, len(le.classes_)))
    for row in df.itertuples():
        dc = getattr(row, "DayCount")
        if getattr(row, "Positive"):
            # Note, if I give multiple comments in succession the last counts more
            student_sentiments[dc:dc + n_weights, getattr(row, "Student")] = +weights
        else:
            student_sentiments[dc:dc + n_weights, getattr(row, "Student")] = -weights

    student_sentiments = student_sentiments[:-n_weights, :]
    student_sentiments = np.cumsum(student_sentiments, axis=0)

    return student_sentiments


p = sF.scrape_pensees()
for course in sF.courses - {sF.rg_class}:
    df, le = sentiments_df(course)
    student_sentiments = sentiments(df)

    list_of_datetimes = pd.date_range(min(df.Date), max(df.Date))
    dates = matplotlib.dates.date2num(list_of_datetimes)

    for student in sF.classes[course].keys():
        print(student)
        image_file = os.path.join(path, "{:s}.png".format(student).replace(" ", ""))
        student_sentiment_in_class(student)
