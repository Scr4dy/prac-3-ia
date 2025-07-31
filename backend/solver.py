from collections import deque

class State:
    def __init__(self, left_m, left_c, boat, path=None):
        self.left_m = left_m
        self.left_c = left_c
        self.right_m = 3 - left_m
        self.right_c = 3 - left_c
        self.boat = boat  # 'left' or 'right'
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
        return self.left_m == 0 and self.left_c == 0

    def get_key(self):
        return (self.left_m, self.left_c, self.boat)

    def get_children(self):
        moves = [(1,0), (2,0), (0,1), (0,2), (1,1)]
        children = []
        for m, c in moves:
            if self.boat == 'left':
                new_state = State(self.left_m - m, self.left_c - c, 'right', self.path + [self])
            else:
                new_state = State(self.left_m + m, self.left_c + c, 'left', self.path + [self])
            if new_state.is_valid():
                children.append(new_state)
        return children

def build_decision_tree():
    root = State(3, 3, 'left')
    queue = deque([root])
    visited = set()
    solutions = []

    while queue:
        current = queue.popleft()
        if current.get_key() in visited:
            continue
        visited.add(current.get_key())

        if current.is_goal():
            solutions.append(current.path + [current])
            continue

        for child in current.get_children():
            queue.append(child)

    # Devolvemos la primera solución encontrada
    if solutions:
        result = []
        for i, step in enumerate(solutions[0]):
            result.append({
                "step": i,
                "left": f"{step.left_m}M, {step.left_c}C",
                "right": f"{step.right_m}M, {step.right_c}C",
                "boat": step.boat
            })
        return result
    return []