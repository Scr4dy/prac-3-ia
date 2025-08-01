from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from collections import deque
from fastapi.responses import JSONResponse
import random
import time

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class State:
    def __init__(self, left_m, left_c, right_m, right_c, boat_side, path=None):
        self.left_m = left_m
        self.left_c = left_c
        self.right_m = right_m
        self.right_c = right_c
        self.boat_side = boat_side
        self.path = path or []
        self.children = []  # <-- agregar aquí

    def is_valid(self):
    # 1. Verificar valores negativos
        if any(v < 0 for v in [self.left_m, self.left_c, self.right_m, self.right_c]):
            return False
    
    # 2. Calcular personas en el bote (asumiendo capacidad máxima 2)
        boat_m = 3 - (self.left_m + self.right_m)
        boat_c = 3 - (self.left_c + self.right_c)
    
    # 3. Verificar totales exactos (deben sumar 3 en cada tipo)
        if (self.left_m + self.right_m + boat_m) != 3:
            return False
        if (self.left_c + self.right_c + boat_c) != 3:
            return False
    
    # 4. Verificar capacidad del bote (máximo 2 personas)
        if boat_m + boat_c > 2 or boat_m + boat_c < 0:
            return False
    
    # 5. Verificar regla fundamental (caníbales no superen a misioneros)
        left_valid = (self.left_m == 0) or (self.left_m >= self.left_c)
        right_valid = (self.right_m == 0) or (self.right_m >= self.right_c)
    
        return left_valid and right_valid

    def is_goal(self):
        return self.left_m == 0 and self.left_c == 0 and self.right_m == 3 and self.right_c == 3

    def to_dict(self, step, status):
        return {
            "step": step,
            "left": f"{self.left_m}M,{self.left_c}C",
            "right": f"{self.right_m}M,{self.right_c}C",
            "boat": self.boat_side,
            "status": status
        }

    def get_children(self):
        moves = [(1, 0), (0, 1), (1, 1), (2, 0), (0, 2)]
        children = []
        for m, c in moves:
            if self.boat_side == 'left':
                new_state = State(
                    self.left_m - m,
                    self.left_c - c,
                    self.right_m + m,
                    self.right_c + c,
                    'right',
                    self.path + [self]
                )
            else:
                new_state = State(
                    self.left_m + m,
                    self.left_c + c,
                    self.right_m - m,
                    self.right_c - c,
                    'left',
                    self.path + [self]
                )
            if new_state.is_valid():
                children.append(new_state)
        self.children = children  # guardar solo los válidos
        return children
    
    def is_blocked(self):
        if self.is_goal() or not self.is_valid():
            return False
        return len(self.get_children()) == 0

def find_solution():
    initial = State(3, 3, 0, 0, 'left')
    visited = set()
    queue = deque([(initial, [])])  # state, path

    while queue:
        current, path = queue.popleft()
        key = (current.left_m, current.left_c, current.right_m, current.right_c, current.boat_side)

        if key in visited:
            continue
        visited.add(key)

        if not current.is_valid():
            continue
        if current.is_goal():
            return path + [current]  # camino exitoso

        for child in current.get_children():
            queue.append((child, path + [current]))

    return []  # no se encontró solución

def find_random_solution(timeout=5.0, allow_mistakes=True, mistake_prob=0.3):
    initial = State(3, 3, 0, 0, 'left')
    visited = set()
    path = [initial]
    current = initial

    start_time = time.time()
    while not current.is_goal():
        if time.time() - start_time > timeout:
            break

        children = current.get_children()
        random.shuffle(children)
        moved = False

        for child in children:
            key = (child.left_m, child.left_c, child.right_m, child.right_c, child.boat_side)
            if key in visited:
                continue
            visited.add(key)

            total_m = child.left_m + child.right_m
            total_c = child.left_c + child.right_c
            if total_m > 3 or total_c > 3:
                continue

            if child.is_valid() or (allow_mistakes and random.random() < mistake_prob and child.left_m >= 0 and child.left_c >= 0 and child.right_m >= 0 and child.right_c >= 0):
                current.children.append(child)  # <- construir el árbol
                path.append(child)
                current = child
                moved = True
                break

        if not moved:
            break  # no se pudo avanzar

        if not current.is_goal():
        # Cambiar el mensaje de error para ser más específico
            if not moved:
            # Crear estado de fallo explícito
                fail_state = State(-1, -1, -1, -1, 'left')
                path.append(fail_state)
            elif time.time() - start_time > timeout:
                timeout_state = State(-2, -2, -2, -2, 'left')
                path.append(timeout_state)

    return path

def build_full_tree():
    initial = State(3, 3, 0, 0, 'left')
    visited = set()
    queue = deque([initial])

    while queue:
        current = queue.popleft()
        key = (current.left_m, current.left_c, current.right_m, current.right_c, current.boat_side)
        if key in visited:
            continue
        visited.add(key)

        current.get_children()
        for child in current.children:
            queue.append(child)

    return initial  # raíz con árbol completo

def state_to_dict(state):
    status = None
    if state.is_goal():
        status = "win"
    elif not state.is_valid():
        status = "fail"

    return {
        "left": f"{state.left_m}M,{state.left_c}C",
        "right": f"{state.right_m}M,{state.right_c}C",
        "boat": state.boat_side,
        "status": status,
        "children": [state_to_dict(child) for child in state.children]
    }

@app.get("/api/solution-safe")
async def api_solution_safe():
    solution = find_solution()
    nodes = []
    for step, state in enumerate(solution):
        status = "win" if state.is_goal() else "valid"
        nodes.append(state.to_dict(step, status))

    return JSONResponse(content=nodes)

@app.get("/api/solution-random")
async def api_solution_random():
    solution = find_random_solution()
    nodes = []

    for step, state in enumerate(solution):
        if step == len(solution) - 1:
            if state.is_goal():
                status = "win"
            elif not state.is_valid():
                status = "fail"
            else:
                status = "incomplete"
        else:
            status = "valid"

        nodes.append(state.to_dict(step, status))

    # Asegurar que siempre se devuelvan nodos
    if not nodes:
        nodes.append({
            "step": 0,
            "left": "3M,3C",
            "right": "0M,0C",
            "boat": "left",
            "status": "fail"
        })

    return JSONResponse(content=nodes)

@app.get("/api/tree-safe")
async def api_tree_safe():
    full_tree = build_full_tree()
    tree_dict = state_to_dict(full_tree)
    return JSONResponse(content=tree_dict)

@app.get("/api/tree-random")
async def api_tree_random():
    path = find_random_solution()

    if not path:
        return JSONResponse(content={})

    root = path[0]

    # Reconstruir el árbol con los estados visitados en el camino
    for i in range(len(path) - 1):
        parent = path[i]
        child = path[i + 1]
        if child not in parent.children:
            parent.children.append(child)

    tree_dict = state_to_dict(root)
    return JSONResponse(content=tree_dict)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    solution = find_solution()
    nodes = []
    for step, state in enumerate(solution):
        status = "win" if state.is_goal() else "valid"
        nodes.append(state.to_dict(step, status))

    return templates.TemplateResponse("index.html", {"request": request, "nodes": nodes})