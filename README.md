# Información del proyecto

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