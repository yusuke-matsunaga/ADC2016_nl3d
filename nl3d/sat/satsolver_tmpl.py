#! /usr/bin/env python3
#
# @file satsolver.py
# @brief SAT ソルバ用のインターフェイスクラス
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.


from enum import Enum


# @brief SAT の結果を表す列挙型
class SatBool3(Enum) :
    B3X     =  0
    B3True  =  1
    B3False = -1


    # @brief 否定を返す．
    def negate(self) :
        if self == SatBool3.B3X :
            return SatBool3.B3X
        elif self == SatBool3.B3True :
            return SatBool3.B3False
        elif self == SatBool3.B3False :
            return SatBool3.B3True
        else :
            assert False

    # @brief 文字列表現を返す．
    def __repr__(self) :
        if self == SatBool3.B3X :
            return 'X(unknown)'
        elif self == SatBool3.B3True :
            return 'True'
        elif self == SatBool3.B3False :
            return 'False'
        else :
            assert False


class SatSolver :

    # @brief 初期化
    def __init__(self) :
        self._var_count = 0


    # @brief 変数を作る．
    # @return 変数番号を返す．
    #
    # 変数番号は 1 から始まる．
    def new_variable(self) :
        self._var_count += 1
        return self._var_count


    # @brief 節を追加する．
    # @param[in] lit_list 節のリテラルのリスト
    #
    # リテラルは 0 以外の整数で，絶対値が番号を
    # 符号が極性を表す．
    # たとえば 3 なら 3番目の変数の肯定
    # -1 なら 1番目の変数の否定を表す．
    def add_clause(self, lit_list) :
        pass


    # @brief SAT問題を解く．
    # @param[in] assumption_list 仮定する割り当てリスト
    # @return (result, model) を返す．
    #
    # - result は SatBool3
    # - model は結果の各変数に対する値を格納したリスト
    #   変数番号が 1番の変数の値は model[1] に入っている．
    #   値は SatBool3
    def solve(self, assumption_list) :
        pass
