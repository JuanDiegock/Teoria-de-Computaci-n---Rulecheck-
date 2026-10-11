
const ruleInput = document.getElementById("ruleInput");
const analyzeBtn = document.getElementById("analyzeBtn");
const exampleBtn = document.getElementById("exampleBtn");
const clearBtn = document.getElementById("clearBtn");

const tokensBody = document.getElementById("tokensBody");
const errorsList = document.getElementById("errorsList");
const summary = document.getElementById("summary");

const tokenCount = document.getElementById("tokenCount");
const lineCount = document.getElementById("lineCount");
const errorCount = document.getElementById("errorCount");

const example = `REGLA validar_venta
SI monto > 0
Y stock >= cantidad
ENTONCES aprobar_venta
SINO rechazar_venta
FIN_REGLA`;

function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);
}

async function analyzeRule() {
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Analizando...";

    try {
        const response = await fetch("/api/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                source: ruleInput.value
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(
                result.error || "No se pudo analizar la regla."
            );
        }

        showTokens(result.tokens);
        showErrors(result.errors);

        tokenCount.textContent = result.token_count;
        lineCount.textContent = result.line_count;
        errorCount.textContent = result.error_count;

        if (result.valid) {
            summary.className = "summary success";
            summary.textContent =
                "Análisis completado. No se detectaron errores básicos.";
        } else {
            summary.className = "summary";
            summary.textContent =
                "Se encontraron " + result.error_count +
                " error(es). Revisa la lista de errores.";
        }

    } catch (error) {
        summary.className = "summary";
        summary.textContent =
            "Error de conexión con Python: " + error.message;
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = "Analizar regla";
    }
}

function showTokens(tokens) {
    if (tokens.length === 0) {
        tokensBody.innerHTML = `
            <tr>
                <td colspan="3">No se encontraron tokens.</td>
            </tr>
        `;
        return;
    }

    tokensBody.innerHTML = tokens.map(item => `
        <tr>
            <td>${item.line}</td>
            <td>${escapeHtml(item.lexeme)}</td>
            <td>${escapeHtml(item.token)}</td>
        </tr>
    `).join("");
}

function showErrors(errors) {
    if (errors.length === 0) {
        errorsList.innerHTML = `
            <p class="success">
                No se detectaron errores básicos.
            </p>
        `;
        return;
    }

    errorsList.innerHTML = errors.map(error => `
        <div class="error-item">
            <strong>
                ${error.line ? "Línea " + error.line : "Regla"}
            </strong>
            <p>${escapeHtml(error.message)}</p>
        </div>
    `).join("");
}

analyzeBtn.addEventListener("click", analyzeRule);

exampleBtn.addEventListener("click", () => {
    ruleInput.value = example;
    analyzeRule();
});

clearBtn.addEventListener("click", () => {
    ruleInput.value = "";

    tokensBody.innerHTML = `
        <tr>
            <td colspan="3">Ejecuta el análisis para ver los resultados.</td>
        </tr>
    `;

    errorsList.innerHTML = "<p>No hay resultados todavía.</p>";
    summary.className = "summary";
    summary.textContent = "Esperando análisis...";

    tokenCount.textContent = "0";
    lineCount.textContent = "0";
    errorCount.textContent = "0";
});
