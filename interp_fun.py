from dataclasses import dataclass
import os

type Expr = Add | Sub | Mul | Div | Neg | Lit | Let | Name | Ifnz | Letfun | App

# Literals
@dataclass
class Lit:
    value: int | bool
    __match_args__ = ('value',)
    
    def __init__(self, value):
        if not isinstance(value, (int, bool)):
            raise TypeError(f"Literals can only take int or bool, got {type(value).__name__}")
        self.value = value
        self.type = type(value)

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

type Binding[V] = tuple[str,V]  # this tuple type is always a pair
type Env[V] = tuple[Binding[V], ...] # this tuple type has arbitrary length 

from typing import Any
emptyEnv : Env[Any] = ()  # the empty environment has no bindings

def extendEnv[V](name: str, value: V, env:Env[V]) -> Env[V]:
    '''Return a new environment that extends the input environment 
       env with a new binding from name to value'''
    return ((name,value),) + env

def lookupEnv[V](name: str, env: Env[V]) -> (V | None) :
    '''Return the first value bound to name in the input environment env
       (or raise an exception if there is no such binding)'''
    # exercises2b.py shows a different implementation alternative
    match env:
        case ((n,v), *rest) :
            if n == name:
                return v
            else:
                return lookupEnv(name, rest) # type:ignore
        case _ :
            return None        
        
class EvalError(Exception):
    pass

type Value = int | Closure

@dataclass
class Closure:
    param: str
    body: Expr
    env: Env[Value]

def eval(e: Expr, env=None) -> Value :

    if env is None:
        env = emptyEnv
    return evalInEnv(env, e)

def evalInEnv(env: Env[Value], e:Expr) -> Value:
    match e:
        case Lit(value):
            return value
            
        case Add(left, right):
            l = eval(left, env)
            r = eval(right, env)
            if not all(isinstance(x, int) for x in (l, r)):
                raise TypeError("Add expects integers")
            return l + r
            
        case Sub(left, right):
            l = eval(left, env)
            r = eval(right, env)
            if not all(isinstance(x, int) for x in (l, r)):
                raise TypeError("Sub expects integers")
            return l - r
        
        case Mul(left, right):
            l = eval(left, env)
            r = eval(right, env)
            if not all(isinstance(x, int) for x in (l, r)):
                raise TypeError("Mul expects integers")
            return l * r
        
        case Div(left, right):
            l = eval(left, env)
            r = eval(right, env)
            if not all(isinstance(x, int) for x in (l, r)):
                raise TypeError("Div expects integers")
            if r == 0:
                raise ZeroDivisionError("Division by zero")
            return l // r
                
        case Neg(expr):
            v = eval(expr, env)
            if not isinstance(v, int):
                raise TypeError("Negative expects an integer")
            return -v
        
        case And(left, right):
            l = eval(left, env)
            if not isinstance(l, bool):
                raise TypeError("And expects booleans")
            if not l:
                return False
            r = eval(right, env)
            if not isinstance(r, bool):
                raise TypeError("And expects booleans")
            return r
        
        case Or(left, right):
            l = eval(left, env)
            if not isinstance(l, bool):
                raise TypeError("Or expects booleans")
            if l:
                return True
            r = eval(right, env)
            if not isinstance(r, bool):
                raise TypeError("Or expects booleans")
            return r

        case Not(expr):
            v = eval(expr, env)
            if not isinstance(v, bool):
                raise TypeError("Not expects booleans")
            return not v
        
        case Eq(left, right):
            l = eval(left, env)
            r = eval(right, env)
            if type(l) != type(r):
                return False
            return l == r

        case Lt(left, right):
            l = eval(left, env)
            r = eval(right, env)
            if not all(isinstance(x, int) for x in (l, r)):
                raise TypeError("Lt expects integers")
            return l < r

        case If(cond, then_branch, else_branch):
            test = eval(cond, env)
            if not isinstance(test, bool):
                raise TypeError("If condition must be a boolean")
            return eval(then_branch if test else else_branch, env)
        
        case Let(name, value_expr, body_expr):
            value = eval(value_expr, env)
            new_env = extendEnv(name, value, env)
            return eval(body_expr, new_env)

        case Name(name):
            value = lookupEnv(name, env)
            if value is None:
                raise EvalError(f"Unbound variable: {name}")
            return value
        
        # -- Shell -- #
        case Command(command_string):
            # Split the command into parts
            parts = command_string.split()
            processed_parts = []
            
            # Process each part for variable substitution
            for part in parts:
                if part.startswith('$'):
                    var_name = part[1:]
                    var_value = lookupEnv(var_name, env)
                    if var_value is None:
                        raise EvalError(f"Undefined variable: {var_name}")
                    processed_parts.append(str(var_value))
                else:
                    processed_parts.append(part)
            
            # Ensure we have at least one part (the command)
            if not processed_parts:
                raise EvalError("Empty command")
            
            return {
                'type': 'command',
                'executable': processed_parts[0],
                'args': processed_parts[1:],
                'redirects': {}
            }
            
        case Pipe(left, right):
  
            left_value = eval(left, env)
            right_value = eval(right, env)
            
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
            
            #Exec IN FUTURE
            value = eval(command, env)
            
            return {
                **value, 'redirects': [value.get('redirects', []), {stream: target}]
            }
            
        case Ifnz(c,t,e):
            match evalInEnv(env,c):
                case 0:
                    return evalInEnv(env,e)
                case _:
                    return evalInEnv(env,t)
        
        case Letfun(n,p,b,i):
            c = Closure(p,b,env)
            newEnv = extendEnv(n,c,env)
            c.env = newEnv        
            return evalInEnv(newEnv,i)
        
        case App(f,a):
            fun = evalInEnv(env,f)
            arg = evalInEnv(env,a)
            match fun:
                case Closure(p,b,cenv):
                    newEnv = extendEnv(p,arg,cenv) 
                    return evalInEnv(newEnv,b)
                case _:
                    raise EvalError("application of non-function")


def run(e: Expr) -> None:
    print(f"running: {e}")
    try:
        i = eval(e)
        print(f"result: {i}")
    except EvalError as err:
        print(err)

