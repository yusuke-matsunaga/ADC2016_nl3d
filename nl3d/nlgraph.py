#! /usr/bin/env python3

## @file nlgraph.py
# @brief NlGraph の定義ファイル
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.

from nlpoint import NlPoint
from nlvia import NlVia
from nlproblem import NlProblem


## @brief 節点を表すクラス
#
# 以下のメンバを持つ．
# - 座標(_x, _y, _z)
# - 接続している枝のリスト(_edge_list)
# - 終端の時に True となるフラグ(_is_terminal)
# - 終端の時の線分番号(_terminal_id)
# - ビアの時に True となるフラグ(_is_via)
# - ビアの時のビア番号(_via_id)
class NlNode :

    ## @brief 初期化
    def __init__(self, x, y, z) :
        self._x = x
        self._y = x
        self._z = z
        self._edge_list = []
        self._is_terminal = False
        self._terminal_id = None
        self._is_via = False
        self._via_id = None

    ## @brief 終端の印をつける．
    def set_terminal(self, net_id) :
        self._is_terminal = True
        self._terminal_id = net_id

    ## @brief ビアの印をつける．
    def set_via(self, via_id) :
        self._is_via = True
        self._via_id = via_id

    ## @brief 枝を追加する．
    def add_edge(self, edge) :
        self._edge_list.append(edge)

    ## @brief X座標
    @property
    def x(self) :
        return self._x

    ## @brief Y座標
    @property
    def y(self) :
        return self._y

    ## @brief Z座標
    @property
    def z(self) :
        return self._z

    ## @brief 接続している枝のリストを返す
    @property
    def edge_list(self) :
        return self._edge_list

    ## @brief 終端フラグ
    @property
    def is_terminal(self) :
        return self._is_terminal

    ## @brief 終端番号
    #
    # is_terminal == False の場合の値は不定
    @property
    def terminal_id(self) :
        return self._terminal_id

    ## @brief ビアフラグ
    @property
    def is_via(self) :
        return self._is_via

    ## @brief ビア番号
    #
    # is_via == False の場合の値は不定
    @property
    def via_id(self) :
        return self._via_id


## @brief 枝を表すクラス
#
# 以下のメンバを持つ．
# - 両端の節点(_node1, _node2)と
# - 自身が線分として選ばれている時 True
#   となる命題変数の番号(_var)を持つ．
class NlEdge :

    ## @brief 初期化
    def __init__(self, node1, node2, var) :
        self._node1 = node1
        self._node2 = node2
        self._var = var

    ## @brief ノード1
    @property
    def node1(self) :
        return self._node1

    ## @brief ノード2
    @property
    def node2(self) :
        return self._node2

    ## @brief 反対のノードを返す．
    def alt_node(self, node) :
        if node == self._node1 :
            return self._node2
        elif node == self._node2 :
            return self._node1
        else :
            assert False


## @brief ナンバーリンクの問題を表すグラフ
class NlGraph :

    ## @brief 初期化
    #
    # @param[in] problem 問題を表すオブジェクト(NlProblem)
    def __init__(self, problem) :
        w = problem.width
        h = problem.height
        d = problem.depth
        nn = problem.net_num
        vn = problem.via_num

        self._net_num = nn
        self._via_num = vn

        # ネット数の log を求める．
        nn_log = 0
        while (1 << nn_log) < nn :
            nn_log += 1

        # 節点を作る．
        # node_array[x][y][z] に (x, y, z) の節点が入る．
        # Python 特有の内包表記で one-liner で書けるけど1行が長すぎ．
        node_array = [[[self._new_node(x, y, z) for z in range(0, d)] \
                       for y in range(0, h)] for x in range(0, w)]

        # 枝を作る．
        for z in range(0, d) :
            # 水平の枝を作る．
            for x in range(0, w - 1) :
                for y in range(0, h) :
                    # (x, y) - (x + 1, y) を結ぶ枝
                    node1 = node_array[x][y][z]
                    node2 = node_array[x + 1][y][z]
                    self._new_edge(node1, node2)

            # 垂直の枝を作る．
            for x in range(0, w) :
                for y in range(0, h - 1) :
                    # (x, y) - (x, y + 1) を結ぶ枝
                    node1 = node_array[x][y][z]
                    node2 = node_array[x][y + 1][z]
                    self._new_edge(node1, node2)

        # 端子の印をつける．
        self._terminal_node_pair_list = []
        for net_id, (label, s, e) in problem.net_list() :
            node1 = node_array[s.x][s.y][s.z]
            node2 = node_array[e.x][e.y][e.z]
            node1.set_terminal(net_id)
            node2.set_terminal(net_id)
            self._terminal_node_pair_list.append((node1, node2))

        # ビアの印をつける．
        for via_id, via in problem.via_list() :
            for z in range(via.z1, via.z2 - via.z1 + 1) :
                node = node_array[via.x][via.y][z]
                node.set_via(via_id)


    ## @brief ネット数
    @property
    def net_num(self) :
        return self._net_num


    ## @brief ビア数
    @property
    def via_num(self) :
        return self._via_num


    ## @brief ノードのリスト
    @property
    def node_list(self) :
        return self._node_list


    ## @brief 枝のリスト
    @property
    def edge_list(self) :
        return self._edge_list


    ## @brief 端点のノード対を返す．
    # @param[in] net_id 線分番号
    def terminal_node_pair(self, net_id) :
        return self._terminal_node_pair[net_id]


    ## @brief 枝を作る．
    # @param[in] node1, node2 両端の節点
    def _new_edge(self, node1, node2) :
        edge = NlEdge(node1, node2)
        self._edge_list.append(edge)
        node1.add_edge(edge)
        node2.add_edge(edge)


    ## @brief ノードを作る．
    # @param[in] x, y, z 座標
    #
    # 結果を self._node_list に入れる．
    def _new_node(self, x, y, z) :
        node = NlNode(x, y, z)
        self._node_list.append(node)

        return node
