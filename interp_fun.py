from dataclasses import dataclass
import os

type Expr = Add | Sub | Mul | Div | Neg | Lit | Let | Name | Ifnz | Letfun | App

# Literals
class Lit:
    __match_args__ = ('value',)
    
    
    def __init__(self, value):
        
        # Type contrsaint on Literals
        if not isinstance(value, (int, bool)):
            raise TypeError(f"Literals can only take int or bool, got {type(value).__name__}")
        
        self.value = value # int or bool
        self.type = type(value)
      
        
# Arithmetic 
class Add:
    __match_args__ = ('left', 'right')
    
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Sub:
    __match_args__ = ('left', 'right')
    
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Mul:
    __match_args__ = ('left', 'right')
     
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Div:
    __match_args__ = ('left', 'right')
    
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Neg:
    __match_args__ = ('expr',)
    
    def __init__(self, expr):
        self.expr = expr

# Boolean
class And:
    __match_args__ = ('left', 'right')
    
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Or:
    __match_args__ = ('left', 'right')
    
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Not:
    __match_args__ = ('expr',)
    
    def __init__(self, expr):
        self.expr = expr

# Variables
class Let:
    __match_args__ = ('name', 'expr', 'body')
    
    def __init__(self, name, expr, body):
        self.name = name        # variable name 
        self.expr = expr        # expression to bind
        self.body = body        # evaluate with new binding

class Name:
    __match_args__ = ('name',)
    
    def __init__(self, name):
        self.name = name        

# Comparisons 
class Eq:
    __match_args__ = ('left', 'right')
    
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Lt:
    __match_args__ = ('left', 'right')
    
    def __init__(self, left, right):
        self.left = left
        self.right = right

# Conditionals
class If:
    __match_args__ = ('cond', 'then_branch', 'else_branch')
    
    def __init__(self, cond, then_branch, else_branch):
        self.cond = cond
        self.then_branch = then_branch
        self.else_branch = else_branch

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
        # -- Literals -- #
        
        # Case: Literal
        # Input: int or bool
        # Output: int or bool
        case Lit(value):
            return value
        
        
        # -- Arithmetic Operations-- #

        # Case: Addition
        # Input: int
        # Output: int
        case Add(left, right):
            # Evaluate left
            l = eval(left, env)
            # Check left
            if isinstance(l, bool):
                raise TypeError("Add expects integers")

            if not isinstance(l, int):
                raise TypeError("Add expects integers")
            
            # Evaluate right
            r = eval(right, env)
            
            # Check right
            if not isinstance(r, int):
                raise TypeError("Add expects integers")
            
            if isinstance(r, bool):
                raise TypeError("Add expects integers")
            
            #  int + int
            return l + r
            
        
        # Case: Subtraction
        # Input: int
        # Output: int   
        case Sub(left, right):
            
            l = eval(left, env)
            
            if not isinstance(l, int):
                raise TypeError("Sub expects integers")
            
            if isinstance(l, bool):
                raise TypeError("Sub expects integers")
            
            r = eval(right, env)
            
         
            if not isinstance(r, int):
                raise TypeError("Sub expects integers")
            
            if isinstance(r, bool):
                raise TypeError("Sub expects integers")
            
            return l - r
        
        # Case: Multiplication
        # Input: int
        # Output: int 
        case Mul(left, right):
            l = eval(left, env)
            
            if not isinstance(l, int):
                raise TypeError("Mul expects integers")
            
            if isinstance(l, bool):
                raise TypeError("Mul expects integers") 
            
            r = eval(right, env)
            
            if isinstance(r, bool):
                raise TypeError("Mul expects integers")
            
            if not isinstance(r, int):
                raise TypeError("Mul expects integers")

            return l * r
        
        # Case: Division
        # Input: int
        # Output: int 
        case Div(left, right):
            l = eval(left, env)
            
            if not isinstance(l, int):
                raise TypeError("Div expects integers")
            
            if isinstance(l, bool):
                raise TypeError("Div expects integers") 
            
            r = eval(right, env)
            
            if isinstance(r, bool):
                raise TypeError("Div expects integers")
            
            if not isinstance(r, int):
                raise TypeError("Div expects integers")
            
            if r == 0:
                raise ZeroDivisionError("Division by zero")
                
            return l // r
                
        
        # Case: Negative
        # Input: int
        # Output: int 
        case Neg(inner):
            v = eval(inner, env)
            
            if isinstance(v,bool):
                raise TypeError("Negative expects an integer or boolean.")
            
            if not isinstance(v, int):
                raise TypeError("Negative expects an integer or boolean.")
                
            return -v
        
        
        # -- Boolean Expressions -- #
        
        case And(left, right):
            # Evaluate left
            l = eval(left, env)
            # Check left
            if not isinstance(l, bool):
                raise Exception("And expects booleans.")
            # If this was false, we can shorthand the evaluation
            if not l:
                return False
            # Evaluate right
            r = eval(right, env)
            # Check right
            if not isinstance(r, bool):
                raise Exception("And expects booleans.")
            
            return r
        
        case Or(left, right):
            l = eval(left, env)
            
            if not isinstance(l, bool):
                raise Exception("Or expects booleans")
            
            if l:
                return True
            
            r = eval(right, env)


            if not isinstance(r, bool):
                raise Exception("Or expects booleans")
            
            return r

        case Not(inner):
            v = eval(inner, env)
            
            if not isinstance(v,bool):
                raise TypeError("Not expects booleans")
            
            if isinstance(v, bool):
                return not v
            
        
               
        # -- Comparisons -- #
        
        case Eq(left, right):
            l = eval(left, env)
            r = eval(right, env)

            # Check if types are the same
            if type(l) != type(r):
                return False

            return l == r

        case Lt(left, right):
            # Can shorthand like boolean logic
            l = eval(left, env)
            
            if not isinstance(l, int):
                raise TypeError("Lt expects integers")
            
            if isinstance(l, bool):
                raise TypeError("Lt expects integers") 
            
            r = eval(right, env)
            
            if isinstance(r, bool):
                raise TypeError("Lt expects integers")
            
            if not isinstance(r, int):
                raise TypeError("Lt expects integers")
            
            return l < r  


        # -- Conditional -- #
        
        case If(cond, then_branch, else_branch):
            # Evaluate condition in current environment
            test = eval(cond, env)
            
            # If test is not a boolean, raise an exception
            if not isinstance(test, bool):
                raise Exception("If condition must be a boolean")
            
            
            # If test is true, evaluate then_branch
            if test:
                return eval(then_branch, env)
            
            # Else, evaluate else_branch
            else:
                return eval(else_branch, env)
        
        
        # -- Let and Variable -- #
        
        case Let(name, value_expr, body_expr):
            # Evaluate in current environment
            value = eval(value_expr, env)
            # Create a new environment as a copy
            new_env = env.copy()
            # Bind name to value in new environment
            new_env[name] = value
            # Evaluate body in new environment
            return eval(body_expr, new_env)

        case Name(name):
            # Check if name in environment
            if name in env:
                return env[name]
            
            raise Exception(f"Unbound variable: {name}")
        
        
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
            
            # Unpack left_value, get pipes, and append right_value
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
        
        