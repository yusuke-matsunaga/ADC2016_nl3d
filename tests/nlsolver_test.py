#! /usr/bin/env python3
#
# @file nlsolver_test.py
# @brief solver_nlink の簡単なテストプログラム
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.


import sys
import nl3d
import nl3d.sat


if __name__ == '__main__' :

    if len(sys.argv) != 2 :
        print('USAGE: read_problem_test <filename>')
        exit(0)

    reader = nl3d.ADC2016_Reader()

    filename = sys.argv[1]
    with open(filename, 'rt') as fin :
        problem = reader.read(fin)
        if problem is None :
            print('{}: read failed.'.format(filename))
            exit(-1)

        problem.dump()

        graph = nl3d.NlGraph(problem)

        graph.dump()

        solver = nl3d.sat.SatSolver('minisat_static')

        nl3d.solve_nlink(graph, solver)
