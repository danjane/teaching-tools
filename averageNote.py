import studentFunctions as sF
import numpy as np
import pandas as pd


def nan_average(course_):
    notes, noted_exams, not_noted_exams = sF.merge_exams(course_)
    notes = notes[noted_exams]

    notes = notes.reindex(sorted(notes.columns), axis=1)

    ma = np.ma.MaskedArray(notes, mask=np.isnan(notes))
    ma = ma.clip(1.5, 6.)

    weights = np.ones(np.shape(ma)[1])

    if course_ == '2MA1DFb05':
        weights[2] = 1.5

    weights[-1] = sum(weights[:-1]) * .33 / (1. - .33)
    weights = weights / sum(weights)
    print(weights)

    notes = notes.assign(Average=pd.Series(np.ma.average(ma, weights=weights, axis=1).data, index=notes.index))

    return notes


def main():
    for course in sF.courses - {sF.rg_class}:
        notes = nan_average(course)

        print(course)
        for student in sF.classes[course].keys():
            nom = sF.classes[course][student]
            print('NOTE SEMESTRE 1: {:.1f}, {}'.format(notes.loc[student, 'Average'], nom))


if __name__ == "__main__":
    main()

