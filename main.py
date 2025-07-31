from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Optional
import json

app = FastAPI()

# Montar archivos estáticos y templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Clase para representar el estado del juego
class Estado:
    def __init__(self, misioneros_izq: int, canibales_izq: int, barca_izq: bool, 
                 misioneros_der: int, canibales_der: int, padre=None, accion=None):
        self.misioneros_izq = misioneros_izq
        self.canibales_izq = canibales_izq
        self.barca_izq = barca_izq
        self.misioneros_der = misioneros_der
        self.canibales_der = canibales_der
        self.padre = padre
        self.accion = accion
        self.hijos = []
    
    def es_valido(self) -> bool:
        # Verificar que no haya más caníbales que misioneros en ninguna orilla
        if (self.misioneros_izq < self.canibales_izq and self.misioneros_izq > 0) or \
           (self.misioneros_der < self.canibales_der and self.misioneros_der > 0):
            return False
        # Verificar que los números no sean negativos
        if self.misioneros_izq < 0 or self.canibales_izq < 0 or \
           self.misioneros_der < 0 or self.canibales_der < 0:
            return False
        return True
    
    def es_meta(self) -> bool:
        return self.misioneros_izq == 0 and self.canibales_izq == 0
    
    def __eq__(self, other):
        return self.misioneros_izq == other.misioneros_izq and \
               self.canibales_izq == other.canibales_izq and \
               self.barca_izq == other.barca_izq
    
    def __hash__(self):
        return hash((self.misioneros_izq, self.canibales_izq, self.barca_izq))
    
    def to_dict(self):
        return {
            "misioneros_izq": self.misioneros_izq,
            "canibales_izq": self.canibales_izq,
            "barca_izq": self.barca_izq,
            "misioneros_der": self.misioneros_der,
            "canibales_der": self.canibales_der,
            "accion": self.accion
        }

# Generar posibles movimientos
def generar_movimientos(estado_actual: Estado) -> list:
    movimientos = []
    if estado_actual.barca_izq:
        # Movimientos de izquierda a derecha
        for m in range(3):
            for c in range(3):
                if 1 <= m + c <= 2:
                    nuevo_estado = Estado(
                        estado_actual.misioneros_izq - m,
                        estado_actual.canibales_izq - c,
                        False,
                        estado_actual.misioneros_der + m,
                        estado_actual.canibales_der + c,
                        estado_actual,
                        f"Llevar {m} misionero(s) y {c} caníbal(es) a la derecha"
                    )
                    if nuevo_estado.es_valido():
                        movimientos.append(nuevo_estado)
    else:
        # Movimientos de derecha a izquierda
        for m in range(3):
            for c in range(3):
                if 1 <= m + c <= 2:
                    nuevo_estado = Estado(
                        estado_actual.misioneros_izq + m,
                        estado_actual.canibales_izq + c,
                        True,
                        estado_actual.misioneros_der - m,
                        estado_actual.canibales_der - c,
                        estado_actual,
                        f"Llevar {m} misionero(s) y {c} caníbal(es) a la izquierda"
                    )
                    if nuevo_estado.es_valido():
                        movimientos.append(nuevo_estado)
    return movimientos

# Construir árbol de decisión
def construir_arbol(estado_inicial: Estado, visitados=None, profundidad=0, max_profundidad=20) -> Estado:
    if visitados is None:
        visitados = set()
    
    if profundidad > max_profundidad:
        return estado_inicial
    
    visitados.add(estado_inicial)
    
    if estado_inicial.es_meta():
        return estado_inicial
    
    movimientos = generar_movimientos(estado_inicial)
    for movimiento in movimientos:
        if movimiento not in visitados:
            hijo = construir_arbol(movimiento, visitados, profundidad + 1, max_profundidad)
            estado_inicial.hijos.append(hijo)
    
    return estado_inicial

# Convertir árbol a formato JSON
def arbol_a_json(nodo: Estado) -> dict:
    return {
        "estado": nodo.to_dict(),
        "hijos": [arbol_a_json(hijo) for hijo in nodo.hijos]
    }

# Encontrar todas las soluciones
def encontrar_soluciones(nodo: Estado, camino_actual=None, soluciones=None):
    if camino_actual is None:
        camino_actual = []
    if soluciones is None:
        soluciones = []
    
    camino_actual.append(nodo.to_dict())
    
    if nodo.es_meta():
        soluciones.append(camino_actual.copy())
    else:
        for hijo in nodo.hijos:
            encontrar_soluciones(hijo, camino_actual, soluciones)
    
    camino_actual.pop()
    return soluciones

# Ruta principal
@app.get("/", response_class=HTMLResponse)
async def leer_inicio(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Ruta para resolver el problema
@app.post("/resolver", response_class=HTMLResponse)
async def resolver_problema(request: Request, misioneros: int = Form(3), canibales: int = Form(3)):
    estado_inicial = Estado(misioneros, canibales, True, 0, 0)
    arbol = construir_arbol(estado_inicial)
    soluciones = encontrar_soluciones(arbol)
    
    # Convertir el árbol a JSON para visualización
    arbol_json = json.dumps(arbol_a_json(arbol), indent=2)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "arbol_json": arbol_json,
        "soluciones": soluciones,
        "misioneros": misioneros,
        "canibales": canibales
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)