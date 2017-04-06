#! /usr/bin/env python3
#
# @file read_problem_test.py
# @brief
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2016 Yusuke Matsunaga
# All rights reserved.

import sys
from nlproblem import NlProblem
from nlviewmgr import NlViewMgr
from nlviewwidget import NlViewWidget
from ADC2016_Reader import ADC2016_Reader
from PyQt5.QtWidgets import *

if __name__ == '__main__' :

    if len(sys.argv) != 2 :
        print('USAGE: read_problem_test <filename>')
        exit(0)

    reader = ADC2016_Reader()

    filename = sys.argv[1]
    with open(filename, 'rt') as fin :
        problem = reader.read(fin)
        if problem is None :
            print('{}: read failed.'.format(filename))
            exit(-1)

        print('width  = {}'.format(problem.width))
        print('height = {}'.format(problem.height))
        print('depth  = {}'.format(problem.depth))

        for net_id, label, start_point, end_point in problem.net_list() :
            print('Net#{}[{}]: ({}, {}, {}) - ({}, {}, {})'.format(label, net_id, start_point.x, start_point.y, start_point.z, end_point.x, end_point.y, end_point.z))

        for via_id, via in problem.via_list() :
            print('Via#{}[{}]: {}, {}, {} - {}'.format(via.label, via_id, via.x, via.y, via.z1, via.z2))

        app = QApplication(sys.argv)

        vm = NlViewMgr()
        vm.set_problem(problem)

        app.exec_()