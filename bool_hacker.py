import ctypes
import random
import sys
from itertools import product
from string import ascii_uppercase
from types import FunctionType
from typing import Union, List, Callable, Tuple, Iterable, Any

#
# Colors
# imported from https://github.com/Radolyn/RadLibrary/tree/master/RadLibrary/Colors
#

#
# Font decorations
#
BOLD = '\x1b[1m'
UNDERLINE = '\x1b[4m'

#
# Text color
#
LIGHT_GREEN = '\x1b[92m'
LIGHT_BLUE = '\x1b[36m'
LIGHT_YELLOW = '\x1b[93m'
LIGHT_RED = '\x1b[91m'

#
# Mixes
#
STEP_DEC = BOLD + LIGHT_YELLOW
RESULT_DEC = UNDERLINE + LIGHT_GREEN
HEADER = STEP_DEC

#
# Color and font reset
#
RESET_COLOR = '\x1b[39m'
RESET_FONT = '\x1b[0m'
RESET = RESET_COLOR + RESET_FONT

#
# Setup environment
# imported from https://github.com/Radolyn/LogManager/tree/master/LogManager.py
#
if sys.platform == 'win32':
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

#
# Types
#
BooleanFunction = Union[FunctionType, Callable[[bool], bool]]
BooleanArguments = List[Tuple[bool]]
BooleanExpression = List[List[str]]

#
# Constants
#
TOKEN_AND = '*'
TOKEN_OR = '+'
TOKEN_NOT = '¬'
TOKEN_SHEFFER = '↑'


#
# Wrapper for benchmarking
#
def timeit(f: FunctionType):
    def wrapper(*args, **kwargs):
        from datetime import datetime

        start = datetime.now()
        f(*args, **kwargs)
        stop = datetime.now()

        res = stop - start

        print(f'\n\n{STEP_DEC}Hack done in {RESET}{RESULT_DEC}{res.total_seconds()} seconds{RESET}')

    return wrapper


#
# Wrapper for logo
#
def logo(f: FunctionType):
    def wrapper(*args, **kwargs):
        print('''
bool_hacker by
           _                     ______                     
     /\   | |                   |___  /                     
    /  \  | | _____  _____ _   _   / / __ ___   ____ _ _ __ 
   / /\ \ | |/ _ \ \/ / _ \ | | | / / / _` \ \ / / _` | '__|
  / ____ \| |  __/>  <  __/ |_| |/ /_| (_| |\ V / (_| | |   
 /_/    \_\_|\___/_/\_\___|\__, /_____\__,_| \_/ \__,_|_|   
                            __/ |                           
                           |___/                            
''')
        f(*args, **kwargs)

    return wrapper


#
# Helper classes
#
class Table:
    def __init__(self, headers: Iterable[str], append_result=True):
        self.headers = list(headers)
        if append_result:
            self.headers.append('●')

        self.__column_size = len(max(headers, key=lambda x: len(x))) + 2
        self.__column_count = len(self.headers)
        self.__row_size = (((self.__column_size + 1) * self.__column_count) - 1)

    def generate_top(self):
        s = ''

        s += '┌'
        s += '┬'.join(['─' * self.__column_size for _ in self.headers])
        s += '┐'

        s += '\n'

        s += '│'
        s += '│'.join([f'{HEADER}{arg:^{self.__column_size}}{RESET}' for arg in self.headers])
        s += '│'

        s += '\n'

        s += '├'
        s += '┼'.join(['─' * self.__column_size for _ in self.headers])
        s += '┤'

        return s

    def generate_bottom(self):
        s = ''

        s += '├'
        s += '┼'.join(['─' * self.__column_size for _ in self.headers])
        s += '┤'

        s += '\n'

        s += '│'
        s += '│'.join([f'{HEADER}{arg:^{self.__column_size}}{RESET}' for arg in self.headers])
        s += '│'

        s += '\n'

        s += '└'
        s += '┴'.join(['─' * self.__column_size for _ in self.headers])

        s += '┘'
        return s

    def generate_row(self, *args: Any):
        args = [f'{arg:^{self.__column_size}}' for arg in args]

        s = ''

        s += '│'
        s += '│'.join(args)
        s += '│'

        return s


#
# Helper functions
#
def inspect_args(f: BooleanFunction):
    # P. S. signature is slower than __code__ in 4 times.
    return f.__code__.co_argcount, f.__code__.co_varnames


def generate_args(arg_count: int) -> BooleanArguments:
    return list(product(*[[False, True]] * arg_count))


def generate_dnf_arg(arg_names: List[str], *args):
    args = list(args)
    res = []

    for i in range(len(args)):
        arg = args[i]
        if arg:
            res.append(arg_names[i])
        else:
            res.append(TOKEN_NOT + arg_names[i])

    return res


def print_step(step: str, result: str):
    print(f'{STEP_DEC}{step:<17}{RESET}: {RESULT_DEC}{result}{RESET}')


def stringify_dnf(dnf_expressions: BooleanExpression):
    return '(' + f') {TOKEN_OR} ('.join([f' {TOKEN_AND} '.join(item) for item in dnf_expressions]).strip() + ')'


def print_dnf_step(method: str, dnf_expressions: BooleanExpression):
    print_step(method, stringify_dnf(dnf_expressions))


def regenerate_table(simplified: BooleanExpression, hacked_table: List[List[bool]], arg_names: List[str]):
    hacked_table.clear()

    exp = stringify_dnf(simplified).replace(TOKEN_NOT, 'not ').replace(TOKEN_AND, ' and ').replace(TOKEN_OR, ' or ')
    f = eval(f'''lambda {", ".join(arg_names)}: {exp}''')

    for item in generate_args(len(arg_names)):
        res = [*item, f(*item)]
        hacked_table.append(res)


#
# Simplification
#
def get_alter_value(s: str):
    return '0' if s == '1' else '1'


def multiply(first, second):
    res = []

    for left in first:
        for right in second:
            r = left
            if right not in r:
                r += right
            if r not in res:
                res.append(r)

    return res


def petric(vars, step2):
    letters = {ascii_uppercase[i]: var for i, var in enumerate(vars)}

    fucked = []
    res = []
    for i in range(len(step2[0])):
        exp = []
        for j in range(len(step2)):
            if step2[j][i]:
                exp.append(ascii_uppercase[j])

        if len(exp) == 0:
            fucked.append(i)
        else:
            res.append(exp)

    while len(res) > 1:
        res[0] = multiply(res[0], res[1])
        del res[1]

    final = min(res[0], key=len)
    super_final = [letters[item] for item in final]

    return super_final, fucked


def simplify(arg_names: List[str], dnf_expressions: BooleanExpression):
    bits = set()
    for item in dnf_expressions:
        b = ''
        for var in item:
            b += '0' if var.startswith(TOKEN_NOT) else '1'

        bits.add(b)

    implicants = set()
    prev_bits = None
    while bits != prev_bits:
        new_bits = set()

        for item1 in bits:
            replaced = set()

            for item2 in bits:
                res = None
                for i in range(len(item1)):
                    l1 = item1[i]
                    l2 = item2[i]
                    if l1 == l2:
                        continue
                    elif l1 == get_alter_value(l2) or l1 == '-' or l2 == '-':
                        if res is None:
                            res = i
                        else:
                            res = None
                            break
                    else:
                        res = None
                        break

                if res is not None:
                    s = item2[0:res] + '-' + item2[res + 1:]
                    replaced.add(s)

            if len(replaced) == 0:
                implicants.add(item1)
            else:
                new_bits.update(replaced)

        prev_bits = bits
        bits = new_bits

    vars = []
    for s in implicants:
        impl = []
        for i, ch in enumerate(s):
            if ch == '1':
                impl.append(arg_names[i])
            elif ch == '0':
                impl.append(TOKEN_NOT + arg_names[i])

        vars.append(impl)

    step2 = [[False for _ in dnf_expressions] for _ in vars]
    # step2 = [[all(arg in orig for arg in impl) for j, orig in enumerate(dnf_expressions)] for i, impl in enumerate(vars)]

    for i, impl in enumerate(vars):
        for j, orig in enumerate(dnf_expressions):
            if all(arg in orig for arg in impl):
                step2[i][j] = True

    sdnf, fucked = petric(vars, step2)

    for item in fucked:
        sdnf.append(dnf_expressions[item])

    return sdnf


def sheffer(sdnf: BooleanExpression):
    sheffer_sdnf = [item.copy() for item in sdnf]

    for i in range(len(sheffer_sdnf)):
        item = sheffer_sdnf[i]
        for j in range(len(item)):
            if item[j][0] == TOKEN_NOT:
                s = item[j].replace(TOKEN_NOT, '')
                item[j] = f'({s} {TOKEN_SHEFFER} {s})'

    res = []
    for i in range(len(sdnf)):
        while len(sheffer_sdnf[i]) > 1:
            sheffer_sdnf[i][
                0] = f'(({sheffer_sdnf[i][0]} {TOKEN_SHEFFER} {sheffer_sdnf[i][1]}) {TOKEN_SHEFFER} ({sheffer_sdnf[i][0]} {TOKEN_SHEFFER} {sheffer_sdnf[i][1]}))'
            del sheffer_sdnf[i][1]
        res.extend(sheffer_sdnf[i])

    if len(sheffer_sdnf) > 1:
        final = []

        for item in res:
            s = f'(({item}) {TOKEN_SHEFFER} ({item}))'
            final.append(s)

        final_res = f' {TOKEN_SHEFFER} '.join(final)
    else:
        final_res = f' {TOKEN_SHEFFER} '.join(sheffer_sdnf[0])

    print_step('Sheffer', final_res)


#
# EGE task generator
#
def ege(arg_names: List[str], hacked_table: List[List[bool]], sdnf: BooleanExpression):
    pos = list(filter(lambda x: x[-1], hacked_table))
    neg = list(filter(lambda x: not x[-1], hacked_table))

    if len(neg) > len(pos) >= len(arg_names) - 1:
        shared = pos
        is_neg = False
    elif len(pos) > len(neg) >= len(arg_names) - 1:
        shared = neg
        is_neg = True
    else:
        shared = None

    if shared is None or len(arg_names) > 4:
        return f'{LIGHT_RED}Unable to generate EGE task for this function{RESET}'

    s = f'Логическая функция F задаётся выражением {stringify_dnf(sdnf)}. Ниже приведён фрагмент таблицы ' \
        f'истинности функции F, содержащий все наборы аргументов, при которых функция F {"отрицательна" if is_neg else "положительна"}. Определите, ' \
        f'какому столбцу таблицы истинности функции F соответствует каждая из переменных {", ".join(arg_names)}. Все ' \
        f'строки в представленном фрагменте разные. '

    s = ' ' + '.\n'.join(s.split('.'))
    s += RESET

    s += '\n'

    hidden_names = ['*' for _ in arg_names]
    table = Table(hidden_names, False)
    table_header = table.generate_top()
    table_bottom = table.generate_bottom()

    s += table_header + '\n'

    random.shuffle(shared)

    for row in shared:
        row.pop()

    order = list(arg_names)
    random.shuffle(order)

    for row in shared:
        copy = list(row)
        for i in range(len(row)):
            row[i] = copy[order.index(arg_names[i])]

    not_hidden = True
    for row_i, row in enumerate(shared):
        for i in range(len(row)):
            if random.uniform(0.0, 1.0) > 0.9 and not_hidden or (
                    row_i == len(shared) - 1 and i == len(row) - 1 and not_hidden):
                row[i] = ' '
                not_hidden = False
        s += table.generate_row(*row) + '\n'

    s += table_bottom + '\n'

    s += '\n\n\n\n'
    s += f'Ответ: {" ".join(order)}'
    s += '\n'

    return s


#
# Entry point
#
@logo
@timeit
def hack(f: BooleanFunction):
    arg_count, arg_names = inspect_args(f)
    arg_names = list(arg_names)

    table = Table(arg_names)

    print(table.generate_top())

    dnf_expressions = []
    hacked_table = []
    for arg in generate_args(arg_count):
        res: bool = f(*arg)
        hacked_table.append([*arg, res])
        print(table.generate_row(*arg, res))

        if res:
            dnf_expressions.append(generate_dnf_arg(arg_names, *arg))

    print(table.generate_bottom())

    if len(dnf_expressions) == 2 ** arg_count:
        print_step('DNF', '1')
        print()
        print_step('Simplified', '1')
    elif len(dnf_expressions) == 0:
        print_step('DNF', '0')
        print()
        print_step('Simplified', '0')
    else:
        print_dnf_step('DNF', dnf_expressions)
        print()
        simplified = simplify(arg_names, dnf_expressions)
        print_dnf_step('Simplified', simplified)

        sheffer(simplified)

        print()
        print()

        new_arg_names = []
        for arg in arg_names:
            for item in simplified:
                for var in item:
                    if arg == var.replace(TOKEN_NOT, ''):
                        new_arg_names.append(arg)
                        break
                if arg in new_arg_names:
                    break

        arg_names = new_arg_names
        arg_count = len(arg_names)
        print_step('Nonfictive', ', '.join(arg_names))

        regenerate_table(simplified, hacked_table, arg_names)

        task = ege(arg_names, hacked_table, simplified)
        print(LIGHT_BLUE + task + RESET)
