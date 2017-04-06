#! /usr/bin/env python3
#
# @file read_problem_test.py
# @brief NlProblem と ADC2016_Reader の簡単なテストプログラム
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.


import sys
from nl3d.nlproblem import NlProblem
from nl3d.adc2016_reader import ADC2016_Reader


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
            print('[{:2d}] Net#{}: ({}, {}, {}) - ({}, {}, {})'.format(net_id, label, start_point.x, start_point.y, start_point.z, end_point.x, end_point.y, end_point.z))

        for via_id, via in problem.via_list() :
            print('[{:2d}] Via#{}: {}, {}, {} - {}'.format(via_id, via.label, via.x, via.y, via.z1, via.z2))
