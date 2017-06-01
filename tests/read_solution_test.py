#! /usr/bin/env python3
#
# @file read_solution_test.py
# @brief NlProblem と ADC2016_Reader の簡単なテストプログラム
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.


import sys
import nl3d


if __name__ == '__main__' :

    if len(sys.argv) != 2 :
        print('USAGE: read_solution_test <filename>')
        exit(0)

    reader = nl3d.ADC2016_Reader()

    filename = sys.argv[1]
    with open(filename, 'rt') as fin :
        solution = reader.read_solution(fin)
        if solution is None :
            print('{}: read failed.'.format(filename))
            exit(-1)

        solution.print(sys.stdout)
