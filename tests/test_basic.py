import studentFunctions as sF
import numpy as np

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


