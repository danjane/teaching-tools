import studentFunctions as sF
import sys


def latex_desk(name, xpos, ypos):
    name = '{' + name + '}'
    return '\\node[desk] at ' + "({:d},{:d}) {:s};".format(xpos, ypos, name) + '\n'


def two_desks(pair, i, nx):
    # coordinates of the desks
    x = i % nx
    y = i // nx

    # position of first student in latex
    s0_x = x * 5
    s0_y = y * 2

    # position of second student in latex
    s1_x = x * 5 + 2
    s1_y = y * 2

    # create latex text
    return latex_desk(pair[0], s0_x, s0_y) + latex_desk(pair[1], s1_x, s1_y)


def seatingplan(student_pairs, nx=3):
    plan = '% Students\n'
    for i in range(len(student_pairs)):
        plan += two_desks(student_pairs[i], i, nx)

    plan += '\n% Prof\n\\node[desk, ultra thick] at ({:d}, -1.5) {{\\bfseries Prof}};'.format(nx * 5 - 4)

    return plan


def alphabetic(course):
    s = list(sF.classes[course].values())

    # Add a blank desk if there's an odd number
    if len(s) % 2 == 1:
        s.append('')

    s = list(zip(s[0::2], s[1::2]))

    return seatingplan(s)


def correlation_to_GSpreferences(c):
    students = list(c.keys())

    # For each student, can only pair with the OTHER half of the group
    # i.e. guys and gals in marriage problem

    guys = students[:len(students)//2]
    gals = [s for s in students if s not in guys]

    guyprefers = {}
    galprefers = {}

    for s in guys:
        c[s] = [t for t in c[s] if t not in guys]
        guyprefers[s] = c[s]

    for s in gals:
        c[s] = [t for t in c[s] if t not in gals]
        galprefers[s] = c[s]

    # We'll use the Gale-Shapley algorithm with guys proposing to girls
    # The solution is optimal for guys, so perhaps swap the two groups for another solution
    swap_flag = True
    if swap_flag:
        galprefers, guyprefers = guyprefers, galprefers

    return guyprefers, galprefers


def best_correlations(course, xls_file):

    results, notes = sF.exam_marks(xls_file)
    students = list(results.index)
    c = sF.dict_of_correlations(results)

    for s in students:
        # Sort on the (increasing) correlation
        c[s].sort(key=lambda x: x[1], reverse=False)

        # Just remember the student name
        c[s] = [x[0] for x in c[s]]

    guyprefers, galprefers = correlation_to_GSpreferences(c)
    engaged = sF.matchmaker(guyprefers, galprefers)
    guys = engaged.keys()
    gals = engaged.values()

    def name(student_):
        return sF.first_name(student_, course)

    s = list(zip(
        [name(student) for student in guys],
        [name(student) for student in gals]))

    for student in set(students) - set(guys) - set(gals):
        s.append((name(student), ''))

    return seatingplan(s)


def main():
    course = sys.argv[1]
    report_file = sF.seatingplan_filename(course)

    if len(sys.argv) < 3:
        plan = alphabetic(course)
    else:
        xls_file = sys.argv[2]
        plan = best_correlations(course, xls_file)

    with open(sF.seatingplan_skeleton_file, 'r') as f:
        latex_str = f.read()

    with open(report_file, 'w') as f:
        f.write(latex_str.replace('DesksHere', plan))


if __name__ == "__main__":
    main()
