#! /usr/bin/env python3

## @file adc2016_reader.py
# @brief ADC2016 フォーマットのファイルを読んで NlProblem に設定するプログラム
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.

import re
from nl3d.nlproblem import NlProblem
from nl3d.nlpoint import NlPoint

## @brief 3D版(ADC2016)のファイルを読み込むためのパーサークラス
#
# @code
# reader = ADC2016_Reader()
#
# fin = file('filename', 'r')
# if fin is not None :
#    problem = reader.read(fin)
#    ...
# @endcode
#
# という風に用いる．
class ADC2016_Reader :

    ## @brief 初期化
    def __init__(self) :
        # 正規表現のパタンを作る．
        # nlcheck.py のパクリ
        self.pSIZE3D = re.compile('SIZE +([0-9]+)X([0-9]+)X([0-9]+)', re.IGNORECASE)
        self.pLINE_NUM = re.compile('LINE_NUM +([0-9]+)', re.IGNORECASE)
        self.pLINE3D_name = re.compile('LINE#(\d+) +\((\d+),(\d+),(\d+)\)', re.IGNORECASE)
        self.pLINE3D_pos  = re.compile('[- ]\((\d+),(\d+),(\d+)\)', re.IGNORECASE)
        self.pVIA3D_name = re.compile('VIA#([a-z]+) +(\((\d+),(\d+),(\d+)\))+', re.IGNORECASE)
        self.pVIA3D_pos  = re.compile('[- ]\((\d+),(\d+),(\d+)\)', re.IGNORECASE)


    ## @brief ファイルを読み込む．
    # @param[in] fin ファイルオブジェクト
    # @return NlProblem を返す．
    #
    # 読み込んだファイルの内容に誤りがある場合には None を返す．
    def read(self, fin) :
        self.problem = NlProblem()

        self.nerr = 0
        self.width = 0
        self.height = 0
        self.depth = 0
        self.line_num = 0
        self.via_num = 0

        self.cur_line = ''
        self.cur_lineno = 0

        self.has_SIZE = False
        self.has_LINE_NUM = False

        # ネット番号の重複チェック用の辞書
        # そのネット番号を定義している行番号を入れる．
        self.net_dict = dict()

        # ビアラベルの重複チェック用の辞書
        # そのビアを定義している行番号を入れる．
        self.via_dict = dict()

        # 基本的には1行づつ読み込んで処理していく．
        while True :
            # 1行を読み出し末尾の改行を取る．
            # ほぼ定石のコード
            line = fin.readline()
            self.cur_lineno += 1
            if line == '' :
                # EOF
                break

            line = line.rstrip()
            if line == '' :
                # 空行を読み飛ばす．
                continue

            self.cur_line = line

            # SIZE 行の処理
            if self.read_SIZE() :
                continue;

            # LINE_NUM 行の処理
            if self.read_LINE_NUM() :
                continue

            # LINE# 行の処理
            if self.read_LINE() :
                continue

            # VIA# 行の処理
            if self.read_VIA() :
                continue

            # それ以外はエラー
            self.error('syntax error')

        # エラーがなければ NlProblem を返す．
        if self.nerr == 0 :
            return self.problem
        else :
            return None


    ## @brief SIZE行の処理を行う．
    # @retval True SIZE行だった．
    # @retval False SIZE行ではなかった．
    #
    # 以下の場合にエラーとなる．
    # - すでに別のSIZE行があった．
    #
    # 返り値の真偽はエラーの有無とは関係ない．
    def read_SIZE(self) :
        # SIZE行のパターンにマッチするか調べる．
        m = self.pSIZE3D.match(self.cur_line)
        if m is None :
            return False

        if self.has_SIZE :
            # すでに別の SIZE行があった．
            self.error("Duplicated 'SIZE' line, previously defined at line {}".format(self.SIZE_lineno))
            return True

        width = int(m.group(1))
        height = int(m.group(2))
        depth = int(m.group(3))
        self.problem.set_size(width, height, depth)
        self.width = width
        self.height = height
        self.depth = depth
        self.has_SIZE = True
        self.SIZE_lineno = self.cur_lineno
        return True


    ## LINE_NUM行の処理を行う．
    # @retval True LINE_NUM行だった．
    # @retval False LINE_NUM行ではなかった．
    #
    # 以下の場合にエラーとなる．
    # - すでに別の LINE_NUM 行があった．
    #
    # 返り値の真偽はエラーの有無とは関係ない．
    def read_LINE_NUM(self) :
        # LINE_NUM 行のパターンにマッチするか調べる．
        m = self.pLINE_NUM.match(self.cur_line)
        if m is None :
            return False

        if self.has_LINE_NUM :
            # すでに別の LINE_NUM 行があった．
            self.error("Duplicated 'LINE_NUM' line, previously defined at line {}".format(self.LINE_NUM_lineno))
            return True

        self.line_num = int(m.group(1))
        self.has_LINE_NUM = True
        self.LINE_NUM_lineno = self.cur_lineno
        return True


    ## LINE 行の処理を行う．
    # @retval True LINE行だった．
    # @retval False LINE行ではなかった．
    #
    # 以下の場合にエラーとなる．
    # - SIZE 行が定義されていない．
    # - LINE_NUM 行が定義されていない．
    # - LINE# の番号が LINE_NUM の範囲外．
    # - LINE# の番号が重複している．
    # - 座標の値が SIZE の範囲外．
    # - 指定されている座標の数が2つ以外(syntax error)．
    #
    # 返り値の真偽はエラーの有無とは関係ない．
    def read_LINE(self) :
        # LINE行のパターンにマッチするか調べる．
        m = self.pLINE3D_name.match(self.cur_line)
        if m is None :
            return False

        if not self.has_SIZE :
            # SIZE 行がない．
            self.error("Missing 'SIZE' before 'LINE'")
            return True

        if not self.has_LINE_NUM :
            # LINE_NUM 行がない．
            self.error("Missing 'LINE_NUM' before 'LINE'")
            return True

        # 線分番号を得る．
        net_id = int(m.groups()[0])

        # 番号が範囲内にあるかチェックする．
        if not 1 <= net_id <= self.line_num :
            self.error('LINE#{} is out of range'.format(net_id))
            return True

        # 重複していないか調べる．
        if net_id in self.net_dict :
            prev = self.net_dict[net_id]
            self.error('Duplicated LINE#{}, previously defined at line {}.'.format(net_id, prev))
            return True
        self.net_dict[net_id] = self.cur_lineno

        # 線分の始点と終点を求める．
        count = 0
        for m in self.pLINE3D_pos.finditer(self.cur_line) :
            x = int(m.group(1))
            y = int(m.group(2))
            z = int(m.group(3)) - 1 # ADC2016フォーマットでは層番号は1から始まる．
            # 範囲チェックを行う．
            if not self.check_range(x, y, z) :
                return True

            if count == 0 :
                start_point = NlPoint(x, y, z)
            elif count == 1 :
                end_point = NlPoint(x, y, z)
            else :
                break
            count += 1

        if count != 2 :
            self.error('Syntax error')
            return True

        self.problem.add_net(net_id, start_point, end_point)
        return True


    ## @brief VIA行を読み込む．
    # @retval True VIA行だった．
    # @retval False VIA行ではなかった．
    #
    # 以下の場合にエラーとなる．
    # - SIZE行が定義されていない．
    # - 座標または層番号が範囲外だった．
    # - 層ごとのX座標またはY座標が異なっている．
    # - 層番号が連続していない．(順不同)
    #
    # 返り値の真偽はエラーの有無とは関係ない．
    def read_VIA(self) :
        # VIA行のパターンにマッチするか調べる．
        m = self.pVIA3D_name.match(self.cur_line)
        if m is None :
            return False

        if not self.has_SIZE :
            # SIZE 行がない．
            self.error("Missing 'SIZE' before 'VIA'")
            return True

        via_label = m.groups()[0]

        # ラベルが重複していないか調べる．
        if via_label in self.via_dict :
            prev = self.via_dict[via_label]
            self.error('Duplicated VIA#{}, previously defined at line {}'.format(via_label, prev))
            return True
        self.via_dict[via_label] = self.cur_lineno

        first_time = True
        z_list = []
        for m in self.pVIA3D_pos.finditer(self.cur_line) :
            x, y, z = m.groups()
            x = int(x)
            y = int(y)
            z = int(z) - 1 # ファイルフォーマットでは層番号は1から始まる．
            # 範囲チェックを行う．
            if not self.check_range(x, y, z) :
                return True

            if first_time :
                x0 = x
                y0 = y
                first_time = False
            else :
                # すべての層で x, y 座標は同じでなければならない．
                if x != x0 :
                    self.error("X({}) is differnt from the first point's X({})".format(x, x0))
                    return True
                if y != y0 :
                    self.error("Y({}) is differnt from the first point's Y({})".format(y, y0))
                    return True
                # 同じことが確認されたら x, y に用はない．
            z_list.append(z)

        # z のリストをソートする．
        z_list.sort()
        n = len(z_list)
        z1 = z_list[0]
        z2 = z_list[n - 1]
        if (z2 - z1) != (n - 1) :
            # z1 から z2 の連続した区間になっていない．
            self.error('Some layers are missing')
            return True

        self.problem.add_via(via_label, x0, y0, z1, z2)
        return True


    ## (x, y, z) が範囲内にあるか調べる
    # @param[in] x, y, z 座標
    # @retval True 範囲内だった．
    # @retval False 範囲外だった．
    def check_range(self, x, y, z) :
        if not 0 <= x < self.width :
            self.error('X({}) is out of range.'.format(x))
            return False

        if not 0 <= y < self.height :
            self.error('Y({}) is out of range.'.format(y))
            return False

        if not 0 <= z < self.depth :
            self.error('Z({}) is out of range.'.format(z + 1))
            return False

        return True


    ## エラー処理
    # @param[in] msg エラーメッセージ
    #
    # nerr の値が加算される．
    def error(self, msg) :
        print('Error at line {}: {}'.format(self.cur_lineno, msg))
        print('    {}'.format(self.cur_line))
        self.nerr += 1
