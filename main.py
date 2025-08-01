from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from collections import deque
import random
import time
import uvicorn

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

    def is_valid(self):
        if self.left_m < 0 or self.left_c < 0 or self.right_m < 0 or self.right_c < 0:
            return False
        if self.left_m > 0 and self.left_m < self.left_c:
            return False
        if self.right_m > 0 and self.right_m < self.right_c:
            return False
        return True

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
            children.append(new_state)
        return children

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



def find_random_solution(timeout=5.0):
    initial = State(3, 3, 0, 0, 'left')
    visited = set()
    path = [initial]
    current = initial

    start_time = time.time()
    while not current.is_goal():
        if time.time() - start_time > timeout:
            break  # tiempo agotado

        children = [child for child in current.get_children() if child.is_valid()]
        random.shuffle(children)

        for child in children:
            key = (child.left_m, child.left_c, child.right_m, child.right_c, child.boat_side)
            if key not in visited:
                visited.add(key)
                path.append(child)
                current = child
                break
        else:
            # no hay hijos válidos no visitados → termina
            break

    if current.is_goal():
        return path
    else:
        return []  # no encontró solución

@app.get("/random", response_class=HTMLResponse)
async def random_solution(request: Request):
    solution = find_random_solution()
    nodes = []
    for step, state in enumerate(solution):
        status = "win" if state.is_goal() else "valid"
        nodes.append(state.to_dict(step, status))

    if not solution:
        nodes.append({
            "step": 0,
            "left": "3M,3C",
            "right": "0M,0C",
            "boat": "left",
            "status": "fail"
        })

    return templates.TemplateResponse("index.html", {"request": request, "nodes": nodes})

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    solution = find_solution()
    nodes = []
    for step, state in enumerate(solution):
        status = "win" if state.is_goal() else "valid"
        nodes.append(state.to_dict(step, status))

    return templates.TemplateResponse("index.html", {"request": request, "nodes": nodes})