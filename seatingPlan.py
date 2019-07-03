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


def main():
    course = sys.argv[1]
    report_file = sF.seatingplan_filename(course)

    plan = alphabetic(course)

    with open(sF.seatingplan_skeleton_file, 'r') as f:
        latex_str = f.read()

    with open(report_file, 'w') as f:
        f.write(latex_str.replace('DesksHere', plan))


if __name__ == "__main__":
    main()