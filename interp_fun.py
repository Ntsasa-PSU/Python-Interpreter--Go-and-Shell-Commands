from dataclasses import dataclass

import os

from typing import Dict



type Expr = Add | Sub | Mul | Div | Neg | Lit | Let | Name | Ifnz | Letfun | App | Assign | Seq | Show | Command | Pipe | Redirect | If | And | Or | Not | Eq | Lt | Gt | ShellAnd | ShellOr | StrLit
#| Read | Show | Assign | Seq





# Literals
class Store:
    def __init__(self):
        self._data = []  
        self._next_loc = 0

    def alloc(self, value):
        loc = self._next_loc
        self._data.append(value)  # Append to list
        self._next_loc += 1
        return loc

    def get(self, loc):
        if 0 <= loc < len(self._data):
            return self._data[loc]
        raise KeyError(f"Invalid location: {loc}")

    def set(self, loc, value):
        if 0 <= loc < len(self._data):
            self._data[loc] = value
        else:
            raise KeyError(f"Invalid location: {loc}")

    def copy(self):
        new_store = Store()
        new_store._data = self._data.copy()
        new_store._next_loc = self._next_loc
        return new_store




@dataclass

class Lit:

    value: int | bool

    __match_args__ = ('value',)

    

    def __init__(self, value):

        if not isinstance(value, (int, bool)):

            raise TypeError(f"Literals can only take int or bool, got {type(value).__name__}")

        self.value = value

        self.type = type(value)


# Added string literal
@dataclass
class StrLit:
    value: str
    __match_args__ = ('value',)



# Arithmetic

@dataclass

class Add:

    left: Expr

    right: Expr

    __match_args__ = ('left', 'right')



@dataclass

class Sub:

    left: Expr

    right: Expr

    __match_args__ = ('left', 'right')



@dataclass

class Mul:

    left: Expr

    right: Expr

    __match_args__ = ('left', 'right')



@dataclass

class Div:

    left: Expr

    right: Expr

    __match_args__ = ('left', 'right')



@dataclass

class Neg:

    expr: Expr

    __match_args__ = ('expr',)



# Boolean

@dataclass

class And:

    left: Expr

    right: Expr

    __match_args__ = ('left', 'right')



@dataclass

class Or:

    left: Expr

    right: Expr

    __match_args__ = ('left', 'right')



@dataclass

class Not:

    expr: Expr

    __match_args__ = ('expr',)



# Variables

@dataclass

class Let:

    name: str

    expr: Expr  

    body: Expr

    __match_args__ = ('name', 'expr', 'body')


@dataclass

class Name:

    name: str

    __match_args__ = ('name',)



# Comparisons

@dataclass

class Eq:

    left: Expr

    right: Expr

    __match_args__ = ('left', 'right')



@dataclass

class Lt:

    left: Expr

    right: Expr

    __match_args__ = ('left', 'right')


@dataclass
class Gt:
    left: Expr
    right: Expr
    __match_args__ = ('left', 'right')

# Conditionals 

@dataclass

class If:

    cond: Expr

    then_branch: Expr

    else_branch: Expr

    __match_args__ = ('cond', 'then_branch', 'else_branch')



# Shell Commands



#Value 

@dataclass

class Command:

    command: str

    __match_args__ = ('command',)

    

    def __eq__(self, other):

        if not isinstance(other, Command):

            return False

        return self.command == other.command



#Operator 1

@dataclass

class Pipe:

    left: 'Command | Pipe | Redirect'

    right: 'Command | Pipe | Redirect'

    __match_args__ = ('left', 'right')



#Operator 2

@dataclass

class Redirect:

    command: 'Command'

    stream: str

    target: str

    __match_args__ = ('command','stream', 'target')


#Operator 3 - Sequential execution (runs second command only if first succeeds)
@dataclass
class ShellAnd:
    left: 'Command | Pipe | Redirect | ShellAnd | ShellOr'
    right: 'Command | Pipe | Redirect | ShellAnd | ShellOr'
    __match_args__ = ('left', 'right')


#Operator 4 - Alternative execution (runs second command only if first fails)
@dataclass
class ShellOr:
    left: 'Command | Pipe | Redirect | ShellAnd | ShellOr'
    right: 'Command | Pipe | Redirect | ShellAnd | ShellOr'
    __match_args__ = ('left', 'right')


@dataclass

class Ifnz():

    cond: Expr

    thenexpr: Expr

    elseexpr: Expr

    def __str__(self) -> str:

        return f"(if {self.cond} != 0 then {self.thenexpr} else {self.elseexpr})"

    

@dataclass

class Letfun():

    name: str

    param: str

    bodyexpr: Expr

    inexpr: Expr

    def __str__(self) -> str:

        return f"letfun {self.name} ({self.param}) = {self.bodyexpr} in {self.inexpr} end"

    

@dataclass

class App():

    fun: Expr

    arg: Expr

    def __str__(self) -> str:

        return f"({self.fun} ({self.arg}))"



@dataclass
class Assign:
    name: str
    expr: Expr
    __match_args__ = ('name', 'expr')



@dataclass
class Seq:
    first: Expr
    second: Expr
    __match_args__ = ('first', 'second')
    
@dataclass
class Show:
    expr: Expr
    __match_args__ = ('expr',)
    
@dataclass
class Read:
    __match_args__ = ()

Binding = tuple[str, int]  # name to location
Env = tuple[Binding, ...]
emptyEnv: Env = ()



def extendEnv(name: str, loc: int, env: Env) -> Env:
    '''Return a new environment that extends the input environment env with a new binding from name to location'''
    return ((name, loc),) + env

def lookupEnv(name: str, env: Env) -> int | None:
    '''Return the first location bound to name in the input environment env (or None if not found)'''
    match env:
        case ((n, v), *rest):
            if n == name:
                return v
            else:
                return lookupEnv(name, rest)  # type: ignore
        case _:
            return None
        

class EvalError(Exception):
    pass


type Value = int | Closure | str | bool

@dataclass

class Closure:

    param: str

    body: Expr

    env: Env


def eval(e: Expr, env=None, store=None):
    if env is None:
        env = emptyEnv
    if store is None:
        store = Store()
    return evalInEnv(env, store, e)


def evalInEnv(env: Env, store: Store, e: Expr):
    match e:

        case Lit(value):

            return value

        case StrLit(value):
            return value

            

        case Add(left, right):
            l = evalInEnv(env, store, left)
            r = evalInEnv(env, store, right)
            
            # Support both integer addition and string concatenation
            if isinstance(l, int) and isinstance(r, int):
                return l + r
            elif isinstance(l, str) and isinstance(r, str):
                return l + r
            elif isinstance(l, str) and isinstance(r, int):
                return l + str(r)
            elif isinstance(l, int) and isinstance(r, str):
                return str(l) + r
            else:
                raise TypeError(f"Add expects integers or strings, got {type(l).__name__} and {type(r).__name__}")

            

        case Sub(left, right):


            l = evalInEnv(env, store, left)

            r = evalInEnv(env, store, right)

            if not all(isinstance(x, int) for x in (l, r)):

                raise TypeError("Sub expects integers")

            return l - r

        

        case Mul(left, right):


            l = evalInEnv(env, store, left)

            r = evalInEnv(env, store, right)
            
            if not all(isinstance(x, int) for x in (l, r)):

                raise TypeError("Mul expects integers")

            return l * r

        

        case Div(left, right):


            l = evalInEnv(env, store, left)

            r = evalInEnv(env, store, right)

            if not all(isinstance(x, int) for x in (l, r)):

                raise TypeError("Div expects integers")

            if r == 0:

                raise ZeroDivisionError("Division by zero")

            return l // r

                

        case Neg(expr):

            v =  evalInEnv(env, store, expr)

            if not isinstance(v, int):

                raise TypeError("Negative expects an integer")

            return -v

        

        case And(left, right):

            l = evalInEnv(env, store, left)


            if not isinstance(l, bool):

                raise TypeError("And expects booleans")

            if not l:

                return False

            r = evalInEnv(env, store, right)


            if not isinstance(r, bool):

                raise TypeError("And expects booleans")

            return r

        

        case Or(left, right):

            l = evalInEnv(env, store, left)

            if not isinstance(l, bool):

                raise TypeError("Or expects booleans")

            if l:

                return True

            r = evalInEnv(env, store, right)


            if not isinstance(r, bool):

                raise TypeError("Or expects booleans")

            return r


        case Not(expr):

            v = evalInEnv(env, store, expr)
            if not isinstance(v, bool):

                raise TypeError("Not expects booleans")

            return not v

        

        case Eq(left, right):
            l = evalInEnv(env, store, left)
            r = evalInEnv(env, store, right)
            if type(l) != type(r):
                return False
            return l == r

        case Lt(left, right):
            l = evalInEnv(env, store, left)
            r = evalInEnv(env, store, right)
            if not all(isinstance(x, int) for x in (l, r)):
                raise TypeError("Lt expects integers")
            return l < r

        case Gt(left, right):
            l = evalInEnv(env, store, left)
            r = evalInEnv(env, store, right)
            if not all(isinstance(x, int) for x in (l, r)):
                raise TypeError("Gt expects integers")
            return l > r

        case If(cond, then_branch, else_branch):
            test = evalInEnv(env, store, cond)
            if not isinstance(test, bool):
                raise TypeError("If condition must be a boolean")
            return evalInEnv(env, store, then_branch if test else else_branch)

        

        case Let(name, value_expr, body_expr):

            val = evalInEnv(env, store, value_expr)
            loc = store.alloc(val)
            new_env = extendEnv(name, loc, env)
            return evalInEnv(new_env, store, body_expr)


        case Name(name):

            loc = lookupEnv(name, env)

            if loc is None:

                raise EvalError(f"Unbound variable: {name}")
            return store.get(loc)


        case Assign(name, expr):

            loc = lookupEnv(name, env)
            if loc is None:
                raise EvalError(f"Assignment to unbound variable: {name}")
            # Check if the variable contains a function
            current_value = store.get(loc)
            if isinstance(current_value, Closure):
                raise EvalError(f"Cannot assign to function: {name}")
            val = evalInEnv(env, store, expr)
            store.set(loc, val)
            return val
        
        case Show(expr):
            val = evalInEnv(env, store, expr)
            print(val)  # or use your display logic
            return val

        # -- Shell -- #

        case Command(command_string):
            # Split the command into parts
            parts = command_string.split()
            processed_parts = []
            
            # Process each part for variable substitution
            for part in parts:
                if part.startswith('$'):
                    var_name = part[1:]
                    loc = lookupEnv(var_name, env)
                    if loc is None:
                        raise EvalError(f"Undefined variable: {var_name}")
                    var_value = store.get(loc)
                    processed_parts.append(str(var_value))
                else:
                    processed_parts.append(part)
            
            # Make sure we have at least one part (the command)
            if not processed_parts:
                raise EvalError("Empty command")
            
            return {
                'type': 'command',
                'executable': processed_parts[0],
                'args': processed_parts[1:],
                'redirects': {}
            }

            

        case Pipe(left, right):
            left_value = evalInEnv(env, store, left)
            right_value = evalInEnv(env, store, right)
            
            if left_value['type'] != 'command':
                raise ValueError("Left side of pipe must be a command")
            if right_value['type'] != 'command':
                raise ValueError("Right side of pipe must be a command")
            
            # Unpack left_value, and append right_value to pipes
            return {
                **left_value, 'pipes': [*left_value.get('pipes', []), right_value]
            }
            

        case Redirect(command, stream, target):
            if stream not in ['stdin', 'stdout', 'stderr']:
                raise ValueError(f"Invalid stream: {stream}")
            
            # Never got to execing lol 
            value = evalInEnv(env, store, command)
            
            return {
                **value, 'redirects': [value.get('redirects', []), {stream: target}]
            }

            

        case Ifnz(c,t,e):

            val = evalInEnv(env, store, c)
            if not isinstance(val, int):
                raise TypeError("Ifnz condition must be an integer")
            match val:
                case 0:
                    return evalInEnv(env, store, e)
                case _:
                    return evalInEnv(env, store, t)

        

        case Letfun(n,p,b,i):

            c = Closure(p,b,env)

            loc = store.alloc(c)

            newEnv = extendEnv(n, loc, env)
            
            c.env = newEnv        

            return evalInEnv(newEnv, store, i)

        

        case App(f,a):
            fun = evalInEnv(env, store, f)
            arg = evalInEnv(env, store, a)
            match fun:
                case Closure(p,b,cenv):
                    arg_loc = store.alloc(arg)
                    newEnv = extendEnv(p, arg_loc, cenv) 
                    return evalInEnv(newEnv, store, b)
                case _:
                    raise EvalError ("application of non-function")

        case Seq(first, second):
            evalInEnv(env, store, first)   # Evaluate the first expression, discard its result
            return evalInEnv(env, store, second)  # Return the result of the second expression
        
        case Read():
            s = input("Enter an integer: ")
            try:
                # Remove quotes if they exist
                s = s.strip().strip("'\"")
                return int(s)
            except Exception:
                raise EvalError("Input was not an integer")


        case ShellAnd(left, right):
            left_value = evalInEnv(env, store, left)
            
            # Check if left operand is a shell command
            if not isinstance(left_value, dict) or left_value.get('type') != 'command':
                raise ValueError("Left side of shell && must be a command")
            
            right_value = evalInEnv(env, store, right)
            
            # Check if right operand is a shell command  
            if not isinstance(right_value, dict) or right_value.get('type') != 'command':
                raise ValueError("Right side of shell && must be a command")
            
            # Return a combined command structure
            return {
                'type': 'command',
                'executable': 'shell_and',
                'left_cmd': left_value,
                'right_cmd': right_value,
                'operator': '&&'
            }

        case ShellOr(left, right):
            left_value = evalInEnv(env, store, left)
            
            # Check if left operand is a shell command
            if not isinstance(left_value, dict) or left_value.get('type') != 'command':
                raise ValueError("Left side of shell || must be a command")
            
            right_value = evalInEnv(env, store, right)
            
            # Check if right operand is a shell command  
            if not isinstance(right_value, dict) or right_value.get('type') != 'command':
                raise ValueError("Right side of shell || must be a command")
            
            return {
                'type': 'command',
                'executable': 'shell_or',
                'left_cmd': left_value,
                'right_cmd': right_value,
                'operator': '||'
            }


def run(e: Expr) -> None:
    print(f"running: {e}")
    try:
        i = eval(e)
        print(f"result: {i}")
    except EvalError as err:
        print(err)

