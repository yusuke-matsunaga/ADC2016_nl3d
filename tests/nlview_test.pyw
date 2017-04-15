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

    if len(sys.argv) != 2 :
        print('USAGE: nlview_test <filename>')
        exit(0)

    reader = nl3d.ADC2016_Reader()

    filename = sys.argv[1]
    with open(filename, 'rt') as fin :
        problem = reader.read(fin)
        if problem is None :
            print('{}: read failed.'.format(filename))
            exit(-1)

        app = QApplication(sys.argv)

        vm = nl3d.gui.NlViewMgr()
        vm.set_problem(problem)

        app.exec_()
