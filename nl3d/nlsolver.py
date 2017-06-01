#! /usr/bin/env python3

## @file nlsolver.py
# @brief NlSolver の定義ファイル
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.

from nl3d.nlgraph import NlNode, NlEdge, NlGraph
from nl3d.nlcnfencoder import NlCnfEncoder
from nl3d.nlsolution import NlSolution
from nl3d.sat.satsolver import SatSolver
from nl3d.sat.satbool3 import SatBool3

## @brief 問題を表すCNF式を生成する．
# @param[in] graph 問題を表すグラフ(NlGraph)
# @param[in] solver SATソルバ
# @return <status>, <solution> のタプルを返す．
#
# <status> は "OK", "NG", "Abort" のいずれか
# <solution> は "OK" の時は NlSolution のオブジェクト
# それ以外は None
def solve_nlink(graph, solver) :
    # 問題を表す CNF式を生成する．
    enc = NlCnfEncoder(graph, solver)

    enc.make_base_constraint(False)
    enc.make_ushape_constraint()
    enc.make_wshape_constraint()
    enc.make_w2shape_constraint()

    # SAT問題を解く．
    result, model = solver.solve()

    if result == SatBool3.B3True :
        # 解けた．

        # SATモデルから解を作る．
        route_list = [enc.model_to_route(model, net_id) \
                      for net_id in range(0, graph.net_num)]

        solution = NlSolution()
        solution.set_from_routes(graph, route_list)
        return "OK", solution

    elif result == SatBool3.B3False :
        # 解けなかった．
        return "NG"

    elif result == SatBool3.B3X :
        # アボートした．
        return "Abort"

## @brief 経路のリストから解を作る．
# @param[in] graph 問題を表すグラフ
# @param[in] route_list 経路のリスト
def _make_solution(graph, route_list) :
    w = graph.width
    h = graph.height
    d = graph.depth
    n = graph.net_num

    # 各マス目の値を格納する３次元配列
    grid_array = [[[0 for z in range(0, d)] for y in range(0, h)] for x in range(0, w)]

    # 経路上のマス目に線分番号を書き込む．
    for net_id in range(0, n) :
        route = route_list[net_id]
        for node in route :
            x = node.x
            y = node.y
            z = node.z
            grid_array[x][y][z] = net_id + 1

    # 解を出力する．
    print('SIZE {}X{}X{}'.format(w, h, d))
    for z in range(0, d) :
        print('LAYER {}'.format(z + 1))
        for y in range(0, h) :
            line = ''
            comma = ''
            for x in range(0, w) :
                line += comma
                comma = ','
                line += '{:02d}'.format(grid_array[x][y][z])
            print(line)
