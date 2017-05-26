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

    # SAT問題を解く．
    result, model = solver.solve()

    if result == SatBool3.B3True :
        # 解けた．
        print("OK")

        # SATモデルから解を作る．
        route_list = [_model_to_route(graph, enc, model, net_id) \
                      for net_id in range(0, graph.net_num)]

    elif result == SatBool3.B3False :
        # 解けなかった．
        print("NG")
    elif result == SatBool3.B3X :
        # アボートした．
        print("Abort")


## @brief モデルから線分(NlNode のリスト)を作る
def _model_to_route(graph, enc, model, net_id) :
    start, end = graph.terminal_node_pair(net_id)

    prev = None
    node = start
    route = []
    while node != end :
        route.append(node)
        next = None
        for edge in node.edge_list :
            if model[enc.edge_var(edge)] != SatBool3.B3True :
                continue
            node1 = edge.alt_node(node)
            if node1 == prev :
                continue
            next = node1
        assert next != None
        prev = node
        node = next
    route.append(end)

    return route
