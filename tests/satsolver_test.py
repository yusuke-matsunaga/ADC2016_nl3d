#! /usr/bin/env python3
#
# @file satsolver_test.py
# @brief SatSolver のテスト
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.


import nl3d
from nl3d.sat import SatBool3, SatSolver


if __name__ == '__main__' :

    solver = SatSolver('minisat_static')
    solver._debug = True

    v1 = solver.new_variable()
    v2 = solver.new_variable()

    # v1 + v2'
    solver.add_clause(v1, -v2)
    # v1'
    solver.add_clause(-v1)

    # なので結果は v1 = 0, v2 = 0 で SAT
    result, model = solver.solve()

    print('result = {}'.format(result))
    print('model = {}'.format(model))

    assert result == SatBool3.B3True
    assert model[v1] == SatBool3.B3False
    assert model[v2] == SatBool3.B3False
