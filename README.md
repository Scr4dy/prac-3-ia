# Información del proyecto
Este proyecto es una aplicación web interactiva para visualizar y resolver el clásico problema de los "Misioneros y Caníbales". Utiliza FastAPI como backend para servir la lógica y las rutas de la API, y una interfaz frontend construida con HTML, JavaScript y TailwindCSS para la visualización y la interacción del usuario.

## Características principales:

- **Simulación visual**: Permite mover misioneros y caníbales entre orillas y el bote de forma manual o automática.
- **Modos de juego**: Incluye un modo seguro (solución óptima) y un modo aleatorio para explorar diferentes caminos.
- **Visualización de árbol**: Muestra el árbol de decisiones generado por los algoritmos de búsqueda usando D3.js.
- **Tablas de pasos**: Presenta tablas con los pasos realizados en cada modo (seguro, aleatorio y manual).
- **Temporizador y mensajes**: Incluye un temporizador y mensajes de estado para guiar al usuario durante el juego.

## Objetivo
El objetivo es cruzar a todos los misioneros y caníbales de un lado al otro del río sin que los caníbales superen en número a los misioneros en ninguna orilla, evitando así que los misioneros sean comidos.

## Instalar paquetes

### Python
```
pip install -r requirements.txt
```
### NodeJS
```
npm install
```
## Modificar estilos
### Instalar TailwindCSS
```
npm install tailwindcss @tailwindcss/cli
```
### Crear archivo `input.css` y agregar
```
@import "tailwindcss";
```
### Ejecutar TailwindCSS
```
npx @tailwindcss/cli -i ./static/input.css -o ./static/styles.css --watch
```
## Ejecutar proyecto
```
py main.py
```