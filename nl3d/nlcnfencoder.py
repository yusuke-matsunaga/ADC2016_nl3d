#! /usr/bin/env python3

## @file nlcnfencoderr.py
# @brief NlCnfEncoder の定義ファイル
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.

from nl3d.nlgraph import NlNode, NlEdge, NlGraph
from nl3d.sat.satsolver import SatSolver
from nl3d.sat.satbool3 import SatBool3

## @brief 問題を表すCNF式を生成するクラス
#
# 内部に NlGraph の要素に対する変数の割り当て情報を持つ．
class NlCnfEncoder :

    ## @brief 初期化
    # @param[in] graph 問題を表すグラフ
    # @param[in] solver SATソルバ
    def __init__(self, graph, solver) :
        nn = graph.net_num
        vn = graph.via_num

        # 枝に対応する変数を作る．
        # 結果は edge_var_list に格納する．
        # _edge_var_list[edge.id] に edge に対応する変数が入る．
        self._edge_var_list = [solver.new_variable() for edge in graph.edge_list]

        # 節点のラベルを表す変数のリストを作る．
        # 節点のラベルは nn 個の変数で表す(one-hotエンコーディング)
        # 結果は node_vars_list に格納する．
        # _node_vars_list[node.id] に node に対応する変数のリストが入る．
        self._node_vars_list = [[solver.new_variable() for i in range(0, nn)] \
                                for node in graph.node_list]

        # ビアと線分の割り当てを表す変数を作る．
        # _nv_map[net_id][via_id] に net_id の線分を via_id のビアに接続する時 True となる変数を入れる．
        self._nv_map = [[solver.new_variable() \
                         for via_id in range(0, vn)] \
                        for net_id in range(0, nn)]

        # 各節点に対して隣接する枝の条件を作る．
        # 具体的には
        # - 終端の場合
        #   ただ一つの枝のみが選ばれる．
        # - ビアの場合
        #   nv_map の変数
        # - それ以外
        #   全て選ばれないか2つの枝が選ばれる．
        for node in graph.node_list :
            # node に接続している枝の変数のリスト
            evar_list = [self._edge_var_list[edge.id] for edge in node.edge_list]

            # node のラベルを表す変数のリスト
            lvar_list = self._node_vars_list[node.id]

            if node.is_terminal :
                # node が終端の場合
                # ラベルの変数を固定する．
                tid = node.terminal_id
                for i in range(0, nn) :
                    lvar = lvar_list[i]
                    if i == tid :
                        solver.add_clause(lvar)
                    else :
                        solver.add_clause(-lvar)
                        # ただ一つの枝が選ばれる．
                        _make_one(solver, evar_list)
            elif node.is_via :
                # node がビアの場合
                # この層に終端を持つ線分と結びついている時はただ一つの枝が選ばれる．
                vid = node.via_id
                for net_id in range(0, nn) :
                    cvar = self._nv_map[net_id][vid]
                    node1, node2 = graph.terminal_node_pair(net_id)
                    if (node1.z == node2.z) or (node1.z != node.z and node2.z != node.z) :
                        # このビアは net_id の線分には使えない．
                        # このノードに接続する枝は選ばれない．
                        _make_conditional_zero(solver, cvar, evar_list)
                    else :
                        # このビアを終端と同様に扱う．
                        _make_conditional_one(solver, cvar, evar_list)
            else :
                # それ以外の場合は０か２個の枝が選ばれる．
                _make_zero_or_two(solver, evar_list)

        # 枝が選択された時にその両端のノードのラベルが等しくなるという制約を作る．
        for edge in graph.edge_list :
            evar = self._edge_var_list[edge.id]
            nvar_list1 = self._node_vars_list[edge.node1.id]
            nvar_list2 = self._node_vars_list[edge.node2.id]
            for i in range(0, nn) :
                nvar1 = nvar_list1[i]
                nvar2 = nvar_list2[i]
                _make_conditional_equal(solver, evar, nvar1, nvar2)


    ## @brief 枝に対する変数番号を返す．
    def edge_var(self, edge) :
        return self._edge_var_list[edge.id]

# end-of-class NlCnfEncoder


## @brief リストの中の変数が1つだけ True となる制約を作る．
def _make_one(solver, var_list) :
    n = len(var_list)
    # 要素数で場合分け
    if n == 2 :
        var0 = var_list[0]
        var1 = var_list[1]
        solver.add_clause(-var0, -var1)
        solver.add_clause( var0,  var1)
    elif n == 3 :
        var0 = var_list[0]
        var1 = var_list[1]
        var2 = var_list[2]
        solver.add_clause(-var0, -var1       )
        solver.add_clause(-var0,        -var2)
        solver.add_clause(       -var1, -var2)
        solver.add_clause( var0,  var1,  var2)
    elif n == 4 :
        var0 = var_list[0]
        var1 = var_list[1]
        var2 = var_list[2]
        var3 = var_list[3]
        solver.add_clause(-var0, -var1              )
        solver.add_clause(-var0,        -var2       )
        solver.add_clause(-var0,               -var3)
        solver.add_clause(       -var1, -var2       )
        solver.add_clause(       -var1,        -var3)
        solver.add_clause(              -var2, -var3)
        solver.add_clause( var0,  var1,  var2,  var3)
    else :
        assert False


## @brief 条件付きでリストの中の変数がすべて False となる制約を作る．
def _make_conditional_zero(solver, cvar, var_list) :
    for var in var_list :
        solver.add_clause(-cvar, -var)


## @brief 条件付きでリストの中の変数が1つだけ True となる制約を作る．
def _make_conditional_one(solver, cvar, var_list) :
    n = len(var_list)
    # 要素数で場合分け
    if n == 2 :
        var0 = var_list[0]
        var1 = var_list[1]
        solver.add_clause(-cvar, -var0, -var1)
        solver.add_clause(-cvar,  var0,  var1)
    elif n == 3 :
        var0 = var_list[0]
        var1 = var_list[1]
        var2 = var_list[2]
        solver.add_clause(-cvar, -var0, -var1       )
        solver.add_clause(-cvar, -var0,        -var2)
        solver.add_clause(-cvar,        -var1, -var2)
        solver.add_clause(-cvar,  var0,  var1,  var2)
    elif n == 4 :
        var0 = var_list[0]
        var1 = var_list[1]
        var2 = var_list[2]
        var3 = var_list[3]
        solver.add_clause(-cvar, -var0, -var1              )
        solver.add_clause(-cvar, -var0,        -var2       )
        solver.add_clause(-cvar, -var0,               -var3)
        solver.add_clause(-cvar,        -var1, -var2       )
        solver.add_clause(-cvar,        -var1,        -var3)
        solver.add_clause(-cvar,               -var2, -var3)
        solver.add_clause(-cvar,  var0,  var1,  var2,  var3)
    else :
        assert False


## @brief リストの中の変数が0個か2個 True になるという制約
def _make_zero_or_two(solver, var_list) :
    n = len(var_list)
    # 要素数で場合分け
    if n == 2 :
        var0 = var_list[0]
        var1 = var_list[1]
        solver.add_clause( var0, -var1)
        solver.add_clause(-var0,  var1)
    elif n == 3 :
        var0 = var_list[0]
        var1 = var_list[1]
        var2 = var_list[2]
        solver.add_clause(-var0, -var1, -var2)
        solver.add_clause( var0,  var1, -var2)
        solver.add_clause( var0, -var1,  var2)
        solver.add_clause(-var0,  var1,  var2)
    elif n == 4 :
        var0 = var_list[0]
        var1 = var_list[1]
        var2 = var_list[2]
        var3 = var_list[3]
        solver.add_clause(-var0, -var1, -var2       )
        solver.add_clause(-var0, -var1,        -var3)
        solver.add_clause(-var0,        -var2, -var3)
        solver.add_clause(       -var1, -var2, -var3)
        solver.add_clause( var0,  var1,  var2, -var3)
        solver.add_clause( var0,  var1, -var2,  var3)
        solver.add_clause( var0, -var1,  var2,  var3)
        solver.add_clause(-var0,  var1,  var2,  var3)
    else :
        assert False


## @brief 条件付きで２つの変数が等しくなるという制約を作る．
def _make_conditional_equal(solver, cvar, var1, var2) :
    solver.add_clause(-cvar, -var1,  var2)
    solver.add_clause(-cvar,  var1, -var2)
