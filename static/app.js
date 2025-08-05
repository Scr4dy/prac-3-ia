let secondsElapsed = 0;
let timerInterval = null;
let manualSteps = [];
let safePathData = [];
let randomPathData = [];

let state = {
    left: { m: 3, c: 3 },
    right: { m: 0, c: 0 },
    boat: { m: 0, c: 0 },
    boatSide: 'left'
};

function startTimer() {
    secondsElapsed = 0;
    updateTimerDisplay();
    timerInterval = setInterval(() => {
        secondsElapsed++;
        updateTimerDisplay();
    }, 1000);
}

function stopTimer() {
    clearInterval(timerInterval);
}

function updateTimerDisplay() {
    const mins = String(Math.floor(secondsElapsed / 60)).padStart(2, '0');
    const secs = String(secondsElapsed % 60).padStart(2, '0');
    document.getElementById("timer").textContent = `⏱️ Tiempo: ${mins}:${secs}`;
}

function render() {
    const left = document.getElementById("left");
    const right = document.getElementById("right");
    const boat = document.getElementById("boat");

    left.innerHTML = "";
    right.innerHTML = "";
    boat.innerHTML = "";

    function createPerson(type, location) {
        const el = document.createElement("div");
        el.textContent = type === 'm' ? "👼" : "👺";
        el.className = (type === 'm' ? "bg-blue-100" : "bg-red-100") +
            " rounded-full px-2 py-1 shadow cursor-pointer text-2xl";
        el.onclick = () => movePerson(type, location);
        return el;
    }

    for (let i = 0; i < state.left.m; i++) left.appendChild(createPerson('m', 'left'));
    for (let i = 0; i < state.left.c; i++) left.appendChild(createPerson('c', 'left'));
    for (let i = 0; i < state.right.m; i++) right.appendChild(createPerson('m', 'right'));
    for (let i = 0; i < state.right.c; i++) right.appendChild(createPerson('c', 'right'));
    for (let i = 0; i < state.boat.m; i++) boat.appendChild(createPerson('m', 'boat'));
    for (let i = 0; i < state.boat.c; i++) boat.appendChild(createPerson('c', 'boat'));

    // Muestra el bote
    const icon = document.createElement("span");
    icon.textContent = "⛵";
    icon.className = "cursor-pointer";
    icon.onclick = moveBoat;
    boat.appendChild(icon);

    boat.style.left = state.boatSide === 'left' ? "10%" : "60%";
    boat.style.transform = state.boatSide === 'left' ? "scaleX(1)" : "scaleX(-1)";
}

function recordManualStep() {
    const left = `${state.left.m}M,${state.left.c}C`;
    const right = `${state.right.m}M,${state.right.c}C`;
    const boat = state.boatSide;
    manualSteps.push({ left, right, boat });
    updateManualTable();
    showTable('manual');
}

function updateManualTable() {
    const body = document.getElementById("table-manual");
    body.innerHTML = "";
    manualSteps.forEach((step, i) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td class="px-4 py-2 border">${i}</td>
            <td class="px-4 py-2 border">${step.left}</td>
            <td class="px-4 py-2 border">${step.right}</td>
            <td class="px-4 py-2 border">${step.boat}</td>
        `;
        body.appendChild(row);
    });
}

function movePerson(type, location) {
    if (location === 'boat') {
        // bajar del bote
        if (state.boatSide === 'left') state.left[type]++;
        else state.right[type]++;
        state.boat[type]--;
    } else {
        // subir al bote
        if (state.boat.m + state.boat.c >= 2) return; // máx 2 en el bote
        if (state.boatSide !== location) return; // solo si están en el mismo lado
        if (state[location][type] > 0) {
            state[location][type]--;
            state.boat[type]++;
        }
    }
    recordManualStep();
    render();
}

function moveBoat() {
    if (state.boat.m + state.boat.c === 0) return; // no se puede mover vacío

    // mover bote
    state.boatSide = state.boatSide === 'left' ? 'right' : 'left';

    // descargar personas
    if (state.boatSide === 'left') {
        state.left.m += state.boat.m;
        state.left.c += state.boat.c;
    } else {
        state.right.m += state.boat.m;
        state.right.c += state.boat.c;
    }
    state.boat.m = 0;
    state.boat.c = 0;

    if (!isValidState()) {
        stopTimer();
        alert("💀 ¡Los misioneros fueron comidos! 😱");
        resetGame();
        return;
    }

    if (state.right.m === 3 && state.right.c === 3) {
        render();
        setTimeout(() => {
            stopTimer();
            document.getElementById("message").textContent = "🎉 ¡Ganaste! Todos cruzaron sanos y salvos.";
            document.getElementById("reset-btn").disabled = false;
        }, 200);
        return;
    }

    render();
    recordManualStep();
}

function isValidState() {
    const { left, right } = state;
    const lValid = (left.m === 0 || left.m >= left.c);
    const rValid = (right.m === 0 || right.m >= right.c);
    return lValid && rValid;
}

function resetGame() {
    // Estado inicial
    state = {
        left: { m: 3, c: 3 },
        right: { m: 0, c: 0 },
        boat: { m: 0, c: 0 },
        boatSide: 'left'
    };

    manualSteps = [];

    // Limpia mensajes y habilita el botón (quizá quieras mantenerlo deshabilitado)
    document.getElementById("message").textContent = "";
    document.getElementById("reset-btn").disabled = true;

    // Limpia el árbol
    document.getElementById("tree-container").innerHTML = "";

    // Limpia todas las tablas
    document.getElementById("table-safe").innerHTML = "";
    document.getElementById("table-random").innerHTML = "";
    document.getElementById("table-manual").innerHTML = "";

    // Opcional: oculta todos los contenedores de tablas (safe, random, manual)
    document.getElementById("safe-table-container").style.display = "none";
    document.getElementById("random-table-container").style.display = "none";
    document.getElementById("manual-table-container").style.display = "none";

    showTable('manual');
    stopTimer();
    startTimer();
    render();
}

async function startAuto() {
    const mode = document.getElementById("auto-mode").value;
    resetGame();
    document.getElementById("tree-container").innerHTML = "";

    const pathEndpoint = mode === 'safe' ? '/api/solution-safe' : '/api/solution-random';
    const treeEndpoint = mode === 'safe' ? '/api/tree-safe' : '/api/tree-random';

    try {
        showTable(mode);  // Mostrar solo la tabla activa

        // Limpiar tablas anteriores según modo
        if (mode === 'safe') {
            document.getElementById("table-safe").innerHTML = "";
        } else {
            document.getElementById("table-random").innerHTML = "";
        }
        document.getElementById("table-manual").innerHTML = "";

        const [pathRes, treeRes] = await Promise.all([
            fetch(pathEndpoint),
            fetch(treeEndpoint)
        ]);

        if (!pathRes.ok || !treeRes.ok) throw new Error("Error al obtener solución");

        const path = await pathRes.json();
        const tree = await treeRes.json();

        drawTree(tree);

        if (!path || path.length === 0) {
            const msg = document.getElementById("message");
            msg.textContent = mode === 'safe'
                ? "💀 ¡Modo seguro falló (no se encontró solución)!"
                : "💀 ¡Fracaso en modo aleatorio!";
            msg.style.color = "red";
            document.getElementById("reset-btn").disabled = false;
            stopTimer();
            return;
        }

        // Cargar la tabla correspondiente con los datos
        if (mode === 'safe') loadSafePath();
        else loadRandomPath();

        animateSteps(path, mode);

        if (mode === 'random') {
            loadRandomPath();
            setTimeout(() => {
                const tree = buildTreeFromStepsData(randomPathData);
                drawTree(tree);
            }, 300);
        }

    } catch (error) {
        alert("No se pudo obtener la solución: " + error.message);
    }
}

// Función para animar los pasos
function animateSteps(stepsArray, mode) {
    let i = 0;
    const interval = setInterval(() => {
        if (i >= stepsArray.length) {
            clearInterval(interval);
            const final = mode === 'safe' ? stepsArray[stepsArray.length - 1] : stepsArray[stepsArray.length - 1];

            if (final.status === "win") {
                document.getElementById("message").style.color = "green";
                document.getElementById("message").textContent = mode === 'safe'
                    ? "🎉 ¡Ganaste en modo seguro!"
                    : "🎉 ¡Ganaste en modo aleatorio!";
            } else {
                document.getElementById("message").style.color = "red";  // <-- aquí el color rojo
                document.getElementById("message").textContent = mode === 'safe'
                    ? "💀 ¡Modo seguro falló (no se encontró solución)!"
                    : "💀 ¡Fracaso en modo aleatorio (los misioneros fueron comidos o no se llegó)!";
            }

            if (final.status === "fail") {
                let detailMsg = "";
                if (final.left === "-1M,-1C") {
                    detailMsg = " (bloqueado - sin movimientos válidos)";
                } else if (final.left === "-2M,-2C") {
                    detailMsg = " (timeout - solución no encontrada a tiempo)";
                }
                document.getElementById("message").textContent += detailMsg;
            }

            document.getElementById("reset-btn").disabled = false;
            stopTimer();
            return;
        }

        const step = stepsArray[i];

        const [leftM, leftC] = step.left.split(',').map(v => parseInt(v));
        const [rightM, rightC] = step.right.split(',').map(v => parseInt(v));
        const boatSide = step.boat;

        const boatM = 3 - leftM - rightM;
        const boatC = 3 - leftC - rightC;

        state = {
            left: { m: leftM, c: leftC },
            right: { m: rightM, c: rightC },
            boat: { m: boatM, c: boatC },
            boatSide: boatSide
        };

        render();
        i++;
    }, 1000);
}

// Función para extraer el camino ganador desde el árbol (debe recorrer recursivamente)
function extractWinningPath(node) {
    if (!node) return [];
    if (node.status === "win") return [node];
    if (!node.children || node.children.length === 0) return [];

    for (const child of node.children) {
        const path = extractWinningPath(child);
        if (path.length > 0) {
            return [node].concat(path);
        }
    }

    return [];
}

// Función para dibujar el árbol usando D3
function drawTree(treeData) {
    document.getElementById("tree-container").innerHTML = "";

    const width = 800;
    const height = 600;

    const svg = d3.select("#tree-container")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    const root = d3.hierarchy(treeData, d => d.children);

    const treeLayout = d3.tree().size([height - 100, width - 150]);
    treeLayout(root);

    // Enlaces
    svg.selectAll('line.link')
        .data(root.links())
        .enter()
        .append('line')
        .attr('class', 'link')
        .attr('x1', d => d.source.y + 75)
        .attr('y1', d => d.source.x + 50)
        .attr('x2', d => d.target.y + 75)
        .attr('y2', d => d.target.x + 50)
        .attr('stroke', '#999');

    // Nodos
    svg.selectAll('circle.node')
        .data(root.descendants())
        .enter()
        .append('circle')
        .attr('class', 'node')
        .attr('cx', d => d.y + 75)
        .attr('cy', d => d.x + 50)
        .attr('r', 20)
        .attr('fill', d => {
            if (d.data.status === "win") return "green";
            if (d.data.status === "fail") return "red";
            return "#69b3a2";
        });

    // Etiquetas
    svg.selectAll('text.label')
        .data(root.descendants())
        .enter()
        .append('text')
        .attr('class', 'label')
        .attr('x', d => d.y + 75)
        .attr('y', d => d.x + 50)
        .attr('dy', 5)
        .attr('text-anchor', 'middle')
        .attr('fill', 'white')
        .text(d => `${d.data.left} | ${d.data.right}`);
}

window.onload = () => {
    render();
    startTimer();
    loadSafePath();
    loadRandomPath();
    showTable('manual');
};


function loadSafePath() {
    fetch('/api/solution-safe')
        .then(res => res.json())
        .then(data => {
            safePathData = data; // 🔥 Guardamos para construir árbol más adelante
            const body = document.getElementById("table-safe");
            body.innerHTML = "";
            data.forEach(step => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td class="px-4 py-2 border">${step.step}</td>
                    <td class="px-4 py-2 border">${step.left}</td>
                    <td class="px-4 py-2 border">${step.right}</td>
                    <td class="px-4 py-2 border">${step.boat}</td>
                    <td class="px-4 py-2 border">${step.status}</td>
                `;
                body.appendChild(row);
            });
        });
}

function loadRandomPath() {
    fetch('/api/solution-random')
        .then(res => res.json())
        .then(data => {
            randomPathData = data; // 🔥 Guardamos para el árbol
            const body = document.getElementById("table-random");
            body.innerHTML = "";
            data.forEach(step => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td class="px-4 py-2 border">${step.step}</td>
                    <td class="px-4 py-2 border">${step.left}</td>
                    <td class="px-4 py-2 border">${step.right}</td>
                    <td class="px-4 py-2 border">${step.boat}</td>
                    <td class="px-4 py-2 border">${step.status}</td>
                `;
                body.appendChild(row);
            });
        });
}


function showTable(mode) {
    const containers = {
        safe: document.getElementById("safe-table-container"),
        random: document.getElementById("random-table-container"),
        manual: document.getElementById("manual-table-container")
    };

    // Oculta todos
    Object.values(containers).forEach(c => c.style.display = "none");

    // Muestra el seleccionado (si existe)
    if (containers[mode]) containers[mode].style.display = "block";
}

function buildTreeFromStepsData(steps) {
    if (!steps || steps.length === 0) return null;

    const root = {
        left: steps[0].left,
        right: steps[0].right,
        boat: steps[0].boat,
        status: steps[0].status,
        children: []
    };

    let current = root;

    for (let i = 1; i < steps.length; i++) {
        const step = steps[i];
        const node = {
            left: step.left,
            right: step.right,
            boat: step.boat,
            status: step.status,
            children: []
        };
        current.children.push(node);
        current = node;
    }

    return root;
}

function extractStepsFromTable(tableId) {
    const table = document.getElementById(tableId);
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    const steps = rows.map(row => {
        const cells = row.querySelectorAll('td');
        return {
            izquierda: cells[1].textContent,
            derecha: cells[2].textContent,
            bote: cells[3].textContent,
            estado: cells[4].textContent
        };
    });
    return steps;
}

function updateTreeFromTable(tableId) {
    const steps = extractStepsFromTable(tableId);
    const tree = buildTreeFromTableSteps(steps);
    drawTree(tree);
}