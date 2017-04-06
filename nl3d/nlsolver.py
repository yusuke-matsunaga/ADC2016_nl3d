#! /usr/bin/env python3
#
# @file nlsolver.py
# @brief NlSolver の定義ファイル
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.

from nlpoint import NlPoint
from nlvia import NlVia
from nlproblem import NlProblem


# @brief ナンバーリンクソルバーを表すクラス
class NlSolver :

    # @brief 初期化
    def __init__(self) :
        pass

    # @brief 問題を表すCNF式を生成する．
    # @param[in] problem 問題を表すオブジェクト(NlProblem)
    def make_cnf(self, problem) :
        w = problem.width
        h = problem.height
        d = problem.depth

        # 各層ごとに関係するネット数を数える．
        nets_array = [set() for i in range(d)]
        for net_id, label, start, end in problem.net_list() :
            z1 = start.z
            nets_array[z1] |= {net_id}
            z2 = end.z
            nets_array[z2] |= {net_id}

        for z in range(d) :
            print('Layer#{}:'.format(z), end = '')
            for net_id in nets_array[z] :
                print(' {}'.format(net_id), end = '')
            print('')
