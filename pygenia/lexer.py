# -*- coding: utf-8 -*-
#
# This file is part of the pygenia interpreter that extends the
# python-agentspeak interpreter (Copyright (C) 2016-2019 Niklas
# Fiekas <niklas.fiekas@tu-clausthal.de>.)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

import collections
import enum
import re
import sys

import agentspeak
import agentspeak.util

from agentspeak import (SourceLocation, Trigger, GoalType, FormulaType,
                        UnaryOp, BinaryOp)

from agentspeak.lexer import tokenize, TokenStream, main, repl


class Token(object):
    def __init__(self, regex,
                 space=False, comment=False,
                 functor=False, numeric=False, variable=False, string=False,
                 boolean=None,
                 trigger=None, goal_type=None, formula_type=None,
                 unary_op=None, mult_op=None, add_op=None, comp_op=None):
        self.re = re.compile(regex)

        self.space = space
        self.comment = comment

        self.functor = functor
        self.numeric = numeric
        self.variable = variable
        self.string = string

        self.boolean = boolean

        self.trigger = trigger
        self.goal_type = goal_type
        self.formula_type = formula_type

        self.unary_op = unary_op
        self.mult_op = mult_op
        self.add_op = add_op
        self.comp_op = comp_op


TokenInfo = collections.namedtuple("TokenInfo", "lexeme token loc")


class TokenType(enum.Enum):
    __order__ = """
                personality
                others
                space comment
                paren_open paren_close
                bracket_open bracket_close
                brace_open brace_close concern
                functor numeric variable string
                lit_true lit_false
                tok_if tok_else tok_while tok_for
                include begin end
                arrow define colon
                fork_join_and fork_join_xor
                double_exclam exclam question minus_plus
                op_not op_plus op_minus op_power op_mult op_fdiv op_div op_mod op_and op_or
                op_le op_ge op_ne op_eq op_decompose op_unify op_lt op_gt
                fullstop comma semicolon at
                """

    personality = Token(r"personality__")

    others = Token(r"others__")

    space = Token(r"\s+", space=True)
    comment = Token(r"(//|#).*", comment=True)

    paren_open = Token(r"\(")
    paren_close = Token(r"\)")

    bracket_open = Token(r"\[")
    bracket_close = Token(r"\]")

    brace_open = Token(r"{")
    brace_close = Token(r"}")
    concern = Token(r"concern__")

    functor = Token(
        r"(~?(?!(true|false|not|div|mod|if|else|while|for|include|begin|end)($|[^a-zA-Z0-9_]))((\.?[a-z][a-zA-Z0-9_]*)+))", functor=True)
    numeric = Token(r"((\d*\.\d+|\d+)([eE][+-]?\d+)?)", numeric=True)
    variable = Token(r"(_*[A-Z][a-zA-Z0-9_]*|_+)", variable=True)
    string = Token(r"\"([^\\\"]|\\.)*\"", string=True)

    lit_true = Token(r"true", boolean=True)
    lit_false = Token(r"false", boolean=False)

    tok_if = Token(r"if")
    tok_else = Token(r"else")
    tok_while = Token(r"while")
    tok_for = Token(r"for")

    include = Token(r"include")
    begin = Token(r"begin")
    end = Token(r"end")

    arrow = Token(r"<-")
    define = Token(r":-")
    colon = Token(r":")

    fork_join_and = Token(r"\|&\|")
    fork_join_xor = Token(r"\|\|\|")

    double_exclam = Token(r"!!", formula_type=FormulaType.achieve_later)
    exclam = Token(r"!", formula_type=FormulaType.achieve,
                   goal_type=GoalType.achievement)
    question = Token(r"\?", formula_type=FormulaType.test,
                     goal_type=GoalType.test)
    minus_plus = Token(r"-\+", formula_type=FormulaType.replace)

    op_not = Token(r"not")
    op_plus = Token(r"\+", unary_op=UnaryOp.op_pos, add_op=BinaryOp.op_add,
                    trigger=Trigger.addition, formula_type=FormulaType.add)
    op_minus = Token(r"-", unary_op=UnaryOp.op_neg, add_op=BinaryOp.op_sub,
                     trigger=Trigger.removal, formula_type=FormulaType.remove)
    op_power = Token(r"\*\*")
    op_mult = Token(r"\*", mult_op=BinaryOp.op_mul)
    op_fdiv = Token(r"/", mult_op=BinaryOp.op_truediv)
    op_div = Token(r"div", mult_op=BinaryOp.op_floordiv)
    op_mod = Token(r"mod", mult_op=BinaryOp.op_mod)
    op_and = Token(r"&")
    op_or = Token(r"\|")

    op_le = Token(r"<=", comp_op=BinaryOp.op_le)
    op_ge = Token(r">=", comp_op=BinaryOp.op_ge)
    op_ne = Token(r"\\==", comp_op=BinaryOp.op_ne)
    op_eq = Token(r"==", comp_op=BinaryOp.op_eq)
    op_decompose = Token(r"=\.\.", comp_op=BinaryOp.op_decompose)
    op_unify = Token(r"=", comp_op=BinaryOp.op_unify)
    op_lt = Token(r"<", comp_op=BinaryOp.op_lt)
    op_gt = Token(r">", comp_op=BinaryOp.op_gt)

    fullstop = Token(r"\.")
    comma = Token(r",")
    semicolon = Token(r";")
    at = Token(r"@")


RE_START_COMMENT = re.compile(r"/\*")
RE_END_COMMENT = re.compile(r".*?\*/")


if __name__ == "__main__":
    try:
        args = sys.argv[1:]
        if args:
            for arg in args:
                with open(arg) as source:
                    main(source)
        elif sys.stdin.isatty():
            repl()
        else:
            main(sys.stdin)
    except agentspeak.AggregatedError as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
