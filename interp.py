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
        self.name = name        # variable name (str)
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


# Evaluate
def eval(expr, env=None):
    if env is None:
        env = {}

    match expr:
        
        # -- Literals -- #
        
        # Case: Literal
        # Input: int or bool
        # Output: int or bool
        case Lit(value):
            return value
        
        
        # -- Arithmetic Operations-- #

        # Case: Addition
        # Input: int/bool
        # Output: int
        case Add(left, right):
            l = eval(left, env)
            
            if isinstance(l, bool):
                raise TypeError("Add expects integers")

            if not isinstance(l, int):
                raise TypeError("Add expects integers")
            
            r = eval(right, env)
            
            # int + int
            if not isinstance(r, int):
                raise TypeError("Add expects integers")
            
            if isinstance(l, bool):
                raise TypeError("Add expects integers")
            
            return l + r
            
        
        # Case: Subtraction
        # Input: int/bool
        # Output: int   
        case Sub(left, right):
            
            l = eval(left, env)
            
            if not isinstance(l, int):
                raise TypeError("Sub expects integers")
            
            r = eval(right, env)
            
            # int + int
            if not isinstance(r, int):
                raise TypeError("Sub expects integers")
            
            return l - r
        
        # Case: Multiplication
        # Input: int/bool
        # Output: int 
        case Mul(left, right):
            l = eval(left, env)
            
            if not isinstance(l, int):
                raise TypeError("Mul expects integers")
            
            if isinstance(l, bool):
                raise TypeError("Add expects integers") 
            
            r = eval(right, env)
            
            # int + int
            if isinstance(r, bool):
                raise TypeError("Add expects integers")
            
            if not isinstance(r, int):
                raise TypeError("Mul expects integers")

            return l * r
        
        # Case: Division
        # Input: int/bool
        # Output: int 
        case Div(left, right):
            l = eval(left, env)
            
            if not isinstance(l, int):
                raise TypeError("Mul expects integers")
            
            if isinstance(l, bool):
                raise TypeError("Add expects integers") 
            
            r = eval(right, env)
            
            # int + int
            if isinstance(r, bool):
                raise TypeError("Add expects integers")
            
            if not isinstance(r, int):
                raise TypeError("Add expects integers")
            
            if r == 0:
                raise ZeroDivisionError("Division by zero")
                
            return l // r
                
        
        # Case: Negative
        # Input: int/bool
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
            l = eval(left, env)
            
            if not isinstance(l, bool):
                raise Exception("And expects booleans.")
            
            if not l:
                return False
            
            r = eval(right, env)
            
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

            if isinstance(v, int):
                raise TypeError("Not expects booleans")
            
            return not v
        
               
        # -- Comparisons -- #
        
        case Eq(left, right):
            l = eval(left, env)
            r = eval(right, env)

            if type(l) != type(r):
                return False

            return l == r

        case Lt(left, right):
            l = eval(left, env)
            r = eval(right, env)
            
            if isinstance(l, int) and isinstance(r, int):
                return l < r
            
            raise Exception("Lt expects expressions that evaluate to integers.")


        # -- Conditional -- #
        
        case If(cond, then_branch, else_branch):
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
            # Create a new environment  as a copy
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
        
        
        # -- Unknown -- #
        case _:
            raise Exception(f"Unknown expression: {expr}")  

    
def run(expr):
    result = eval(expr, {})
    print(f"Result: {result}")
        
        
        
        
        
