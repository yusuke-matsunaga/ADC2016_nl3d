#! /usr/bin/env python3
#
# @file nlview_test.py
# @brief NlViewMgr のテストプログラム
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.

import sys
import nl3d
import nl3d.gui
from PyQt5.QtWidgets import *

if __name__ == '__main__' :

    argc = len(sys.argv)
    if argc != 2 and argc != 3 :
        print('USAGE: nlview_test <problem> ?<solution>?')
        exit(0)

    reader = nl3d.ADC2016_Reader()

    app = QApplication(sys.argv)

    vm = nl3d.gui.NlViewMgr()

    problem_filename = sys.argv[1]
    with open(problem_filename, 'rt') as fin :
        problem = reader.read_problem(fin)
        if problem is None :
            print('{}: read failed.'.format(problem_filename))
            exit(-1)

        if argc == 3 :
            solution_filename = sys.argv[2]
            with open(solution_filename, 'rt') as fin2 :
                solution = reader.read_solution(fin2)
                if solution is None :
                    print('{}: read failed.'.format(solution_filename))
                    exit(-1)
                vm.set_solution(problem, solution)
        else :
            vm.set_problem(problem)

        app.exec_()
