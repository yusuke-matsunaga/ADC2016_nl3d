#! /usr/bin/env python3

## @file nlsolver.py
# @brief NlSolver の定義ファイル
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.

from nl3d.nlgraph import NlNode, NlEdge, NlGraph
from nl3d.nlcnfencoder import NlCnfEncoder
from nl3d.sat.satsolver import SatSolver
from nl3d.sat.satbool3 import SatBool3

## @brief 問題を表すCNF式を生成する．
# @param[in] graph 問題を表すグラフ(NlGraph)
# @param[in] solver SATソルバ
def solve_nlink(graph, solver) :
    # 問題を表す CNF式を生成する．
    enc = NlCnfEncoder(graph, solver)

    enc.make_base_constraint(True)
    enc.make_ushape_constraint()

    # SAT問題を解く．
    result, model = solver.solve()

    if result == SatBool3.B3True :
        # 解けた．
        print("OK")

        # SATモデルから解を作る．
        route_list = [enc.model_to_route(model, net_id) \
                      for net_id in range(0, graph.net_num)]

        for net_id in range(0, graph.net_num) :
            route = route_list[net_id]
            print('Net#{}'.format(net_id))
            dash = ''
            for node in route :
                print(dash, end = '')
                dash = ' - '
                print('({}, {}, {})'.format(node.x, node.y, node.z), end='')
            print('')

    elif result == SatBool3.B3False :
        # 解けなかった．
        print("NG")
    elif result == SatBool3.B3X :
        # アボートした．
        print("Abort")
