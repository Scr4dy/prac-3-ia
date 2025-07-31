// Funcionalidad adicional para mejorar la interactividad
document.addEventListener('DOMContentLoaded', function () {
    // Colapsar/expandir soluciones
    document.querySelectorAll('h3').forEach(title => {
        title.addEventListener('click', function () {
            this.nextElementSibling.classList.toggle('hidden');
        });
    });

    // Mejorar visualización del árbol JSON
    const arbolJson = document.getElementById('arbol-json');
    if (arbolJson) {
        try {
            const jsonData = JSON.parse(arbolJson.textContent);
            arbolJson.textContent = JSON.stringify(jsonData, null, 2);
        } catch (e) {
            console.error('Error al parsear JSON:', e);
        }
    }
});