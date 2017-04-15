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


# @brief 節点を表すクラス
class NlNode :

    # @brief 初期化
    def __init__(self, x, y, z) :
        self._x = x
        self._y = x
        self._z = z
        self._var = None
        self._edge_list = []
        self._var_list = []
        self._is_terminal = False
        self._is_via = False
        self._via_id = None


# @brief 枝を表すクラス
class NlEdge :

    # @brief 初期化
    def __init__(self, node1, node2, var) :
        self._node1 = node1
        self._node2 = node2
        self._var = var


# @brief ナンバーリンクソルバーを表すクラス
class NlSolver :

    # @brief 初期化
    def __init__(self) :
        pass

    # @brief 問題を表すCNF式を生成する．
    # @param[in] problem 問題を表すオブジェクト(NlProblem)
    # @param[in] solver SATソルバ
    def make_cnf(self, problem, solver) :
        w = problem.width
        h = problem.height
        d = problem.depth
        nn = problem.net_num
        vn = problem.via_num

        # ネット数の log を求める．
        nn_log = 0
        while (1 << nn_log) < nn :
            nn_log += 1

        # 節点を作る．
        # node_array[x][y][z] に (x, y, z) の節点が入る．
        node_array = [[[NlNode(x, y, z) for z in range(0, d)] for y in range(0, h)] for x in range(0, w)]

        # 枝を作る．
        for z in range(0, d) :
            # 水平の枝に番号を振る．
            for x in range(0, w - 1) :
                for y in range(0, h) :
                    # (x, y) - (x + 1, y) を結ぶ枝
                    node1 = node_array[x][y][z]
                    node2 = node_array[x + 1][y][z]
                    self.new_edge(node1, node2, solver)

            # 垂直の枝に番号を振る．
            for x in range(0, w) :
                for y in range(0, h - 1) :
                    # (x, y) - (x, y + 1) を結ぶ枝
                    node1 = node_array[x][y][z]
                    node2 = node_array[x][y + 1][z]
                    self.new_edge(node1, node2, solver)

        # 節点のラベルを表す変数を作る．
        for z in range(0, d) :
            for x in range(0, w) :
                for y in range(0, h) :
                    node = node_array[x][y][z]
                    node._var_list = [solver.new_variable() for i in range(0, nn_log)]

        # ビアと線分の割り当てを表す変数を作る．
        # nv_map[net_id][via_id] に net_id の線分を via_id のビアに接続する時 True となる変数を入れる．
        nv_map = [[solver.new_variable() for via_id in range(0, nv)] for net_id in range(0, nn)]

        # 端子の印をつける．
        for net_id, (label, s, e) in problem.net_list() :
            node1 = node_array[s.x][s.y][s.z]
            node2 = node_array[e.x][e.y][e.z]
            self.set_terminal(node1, net_id, solver)
            self.set_terminal(node2, net_id, solver)

        # ビアの印をつける．
        for via_id, via in problem.via_list() :
            for z in range(via.z1, via.z2 - via.z1 + 1) :
                node = node_array[via.x][via.y][z]
                self.set_via(node, via_id, solver)

        # 各節点に対して隣接する枝の条件を作る．
        # 具体的には
        # - 終端の場合
        #   ただ一つの枝のみが選ばれる．
        # - ビアの場合
        #   nv_map の変数
        # - それ以外
        #   全て選ばれないか2つの枝が選ばれる．
        for z in range(0, d) :
            for x in range(0, w) :
                for y in range(0, h) :
                    node = node_array[x][y][z]
                    var_list = [edge._var for edge in node._edge_list]
                    if node._is_terminal :
                        self.make_one(var_list, solver)
                    elif node._is_via :
                    else :
                        self.make_zero_or_two(var_list, solver)


    # @brief 枝を作る．
    # @param[in] node1, node2 両端の節点
    # @param[in] solver SATソルバ
    def new_edge(self, node1, node2, solver) :
        var = solver.new_variable()
        edge = NlEdge(node1, node2, var)
        node1._edge_list.append(edge)
        node2._edge_list.append(edge)


    # @brief 節点に終端の印をつける．
    def set_terminal(self, node, net_id, solver) :
        node._is_terminal = True
        # ラベルを固定する．
        for i, var in enumerate(node._var_list) :
            if (1 << i) & net_id :
                solver.add_clause(var)
            else :
                solver.add_clause(-var)

    # @brief 節点にビアの印をつける．
    def set_via(self, node, via_id, solver) :
        node._is_via = True
        node._via_id = via_id
