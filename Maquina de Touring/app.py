from flask import Flask, render_template_string, request, jsonify
import threading, webbrowser

app = Flask(__name__)

# Biblioteca de máquinas de Turing predefinidas
MACHINE_LIBRARY = {
    "anbn": {
        "name": "L = {aⁿbⁿ | n ≥ 0}",
        "description": "Reconoce cadenas con el mismo número de 'a' seguidas del mismo número de 'b'",
        "examples": ["aabb", "aaabbb", "ab", ""],
        "alphabet": ["a", "b"],
        "machine": {
            "states": ["q0", "q1", "q2", "q_check", "q_accept", "q_reject"],
            "start": "q0",
            "accept": ["q_accept"],
            "reject": ["q_reject"],
            "blank": "_",
            "transitions": {
                "q0": {"a": ["X", "R", "q1"], "X": ["X", "R", "q0"], "Y": ["Y", "R", "q0"], "b": ["b", "N", "q_reject"],
                       "_": ["_", "N", "q_check"]},
                "q1": {"X": ["X", "R", "q1"], "Y": ["Y", "R", "q1"], "a": ["a", "R", "q1"], "b": ["Y", "L", "q2"],
                       "_": ["_", "N", "q_reject"]},
                "q2": {"X": ["X", "R", "q0"], "Y": ["Y", "L", "q2"], "a": ["a", "L", "q2"], "b": ["b", "L", "q2"],
                       "_": ["_", "R", "q0"]},
                "q_check": {"X": ["X", "R", "q_check"], "Y": ["Y", "R", "q_check"], "_": ["_", "N", "q_accept"],
                            "a": ["a", "N", "q_reject"], "b": ["b", "N", "q_reject"]}
            }
        }
    },
    "palindrome": {
        "name": "Palíndromo sobre {a,b}",
        "description": "Reconoce cadenas que se leen igual de izquierda a derecha y de derecha a izquierda",
        "examples": ["aba", "abba", "aa", "a", ""],
        "alphabet": ["a", "b"],
        "machine": {
            "states": ["q0", "q1", "q2", "q3", "q4", "q_accept", "q_reject"],
            "start": "q0",
            "accept": ["q_accept"],
            "reject": ["q_reject"],
            "blank": "_",
            "transitions": {
                "q0": {"a": ["_", "R", "q1"], "b": ["_", "R", "q3"], "_": ["_", "N", "q_accept"]},
                "q1": {"a": ["a", "R", "q1"], "b": ["b", "R", "q1"], "_": ["_", "L", "q2"]},
                "q2": {"a": ["_", "L", "q4"], "b": ["b", "N", "q_reject"]},
                "q3": {"a": ["a", "R", "q3"], "b": ["b", "R", "q3"], "_": ["_", "L", "q2"]},
                "q4": {"a": ["a", "L", "q4"], "b": ["b", "L", "q4"], "_": ["_", "R", "q0"]}
            }
        }
    },
    "zerononen": {
        "name": "L = {0ⁿ1ⁿ | n ≥ 0}",
        "description": "Reconoce cadenas con el mismo número de '0' seguidas del mismo número de '1'",
        "examples": ["0011", "000111", "01", ""],
        "alphabet": ["0", "1"],
        "machine": {
            "states": ["q0", "q1", "q2", "q_check", "q_accept", "q_reject"],
            "start": "q0",
            "accept": ["q_accept"],
            "reject": ["q_reject"],
            "blank": "_",
            "transitions": {
                "q0": {"0": ["X", "R", "q1"], "X": ["X", "R", "q0"], "Y": ["Y", "R", "q0"], "1": ["1", "N", "q_reject"],
                       "_": ["_", "N", "q_check"]},
                "q1": {"X": ["X", "R", "q1"], "Y": ["Y", "R", "q1"], "0": ["0", "R", "q1"], "1": ["Y", "L", "q2"],
                       "_": ["_", "N", "q_reject"]},
                "q2": {"X": ["X", "R", "q0"], "Y": ["Y", "L", "q2"], "0": ["0", "L", "q2"], "1": ["1", "L", "q2"],
                       "_": ["_", "R", "q0"]},
                "q_check": {"X": ["X", "R", "q_check"], "Y": ["Y", "R", "q_check"], "_": ["_", "N", "q_accept"],
                            "0": ["0", "N", "q_reject"], "1": ["1", "N", "q_reject"]}
            }
        }
    },
    "even_ones": {
        "name": "Número par de 1s",
        "description": "Acepta cadenas con un número par de unos (0 es par)",
        "examples": ["11", "0110", "1111", "00", ""],
        "alphabet": ["0", "1"],
        "machine": {
            "states": ["q_even", "q_odd", "q_accept", "q_reject"],
            "start": "q_even",
            "accept": ["q_accept"],
            "reject": ["q_reject"],
            "blank": "_",
            "transitions": {
                "q_even": {"1": ["1", "R", "q_odd"], "0": ["0", "R", "q_even"], "_": ["_", "N", "q_accept"]},
                "q_odd": {"1": ["1", "R", "q_even"], "0": ["0", "R", "q_odd"], "_": ["_", "N", "q_reject"]}
            }
        }
    },
    "odd_ones": {
        "name": "Número impar de 1s",
        "description": "Acepta cadenas con un número impar de unos",
        "examples": ["1", "011", "111", "01010"],
        "alphabet": ["0", "1"],
        "machine": {
            "states": ["q_even", "q_odd", "q_accept", "q_reject"],
            "start": "q_even",
            "accept": ["q_accept"],
            "reject": ["q_reject"],
            "blank": "_",
            "transitions": {
                "q_even": {"1": ["1", "R", "q_odd"], "0": ["0", "R", "q_even"], "_": ["_", "N", "q_reject"]},
                "q_odd": {"1": ["1", "R", "q_even"], "0": ["0", "R", "q_odd"], "_": ["_", "N", "q_accept"]}
            }
        }
    },
    "ww": {
        "name": "L = {ww | w ∈ {0,1}*}",
        "description": "Reconoce cadenas que consisten en una palabra seguida de sí misma",
        "examples": ["0101", "1111", "00", ""],
        "alphabet": ["0", "1"],
        "machine": {
            "states": ["q0", "q1", "q2", "q3", "q4", "q5", "q_accept", "q_reject"],
            "start": "q0",
            "accept": ["q_accept"],
            "reject": ["q_reject"],
            "blank": "_",
            "transitions": {
                "q0": {"0": ["X", "R", "q1"], "1": ["Y", "R", "q3"], "_": ["_", "N", "q_accept"]},
                "q1": {"0": ["0", "R", "q1"], "1": ["1", "R", "q1"], "X": ["X", "R", "q1"], "Y": ["Y", "R", "q1"],
                       "_": ["_", "L", "q2"]},
                "q2": {"0": ["X", "L", "q5"], "X": ["X", "L", "q2"], "_": ["_", "N", "q_reject"]},
                "q3": {"0": ["0", "R", "q3"], "1": ["1", "R", "q3"], "X": ["X", "R", "q3"], "Y": ["Y", "R", "q3"],
                       "_": ["_", "L", "q4"]},
                "q4": {"1": ["Y", "L", "q5"], "Y": ["Y", "L", "q4"], "_": ["_", "N", "q_reject"]},
                "q5": {"0": ["0", "L", "q5"], "1": ["1", "L", "q5"], "X": ["X", "L", "q5"], "Y": ["Y", "L", "q5"],
                       "_": ["_", "R", "q0"]}
            }
        }
    },
    "anbncn": {
        "name": "L = {aⁿbⁿcⁿ | n ≥ 1}",
        "description": "Reconoce cadenas con el mismo número de a's, b's y c's en ese orden",
        "examples": ["abc", "aabbcc", "aaabbbccc"],
        "alphabet": ["a", "b", "c"],
        "machine": {
            "states": ["q0", "q1", "q2", "q3", "q4", "q_accept", "q_reject"],
            "start": "q0",
            "accept": ["q_accept"],
            "reject": ["q_reject"],
            "blank": "_",
            "transitions": {
                "q0": {"a": ["X", "R", "q1"], "Y": ["Y", "R", "q0"], "_": ["_", "N", "q_reject"]},
                "q1": {"a": ["a", "R", "q1"], "Y": ["Y", "R", "q1"], "b": ["Y", "R", "q2"],
                       "_": ["_", "N", "q_reject"]},
                "q2": {"b": ["b", "R", "q2"], "Z": ["Z", "R", "q2"], "c": ["Z", "L", "q3"],
                       "_": ["_", "N", "q_reject"]},
                "q3": {"a": ["a", "L", "q3"], "b": ["b", "L", "q3"], "Y": ["Y", "L", "q3"], "Z": ["Z", "L", "q3"],
                       "X": ["X", "R", "q4"]},
                "q4": {"Y": ["Y", "R", "q4"], "Z": ["Z", "R", "q4"], "_": ["_", "N", "q_accept"], "a": ["X", "R", "q1"]}
            }
        }
    }
}

PAGE = '''
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Máquina de Turing – Simulador Educativo</title>
<style>
body{font-family:Inter,system-ui,Arial;margin:20px;background:#f7fafc}
nav{display:flex;gap:20px;margin-bottom:20px;flex-wrap:wrap}
nav a{font-size:18px;color:#2563eb;text-decoration:none;padding:6px 10px;border-radius:8px}
nav a:hover{background:#dbeafe}
.section{background:white;padding:18px;border-radius:12px;box-shadow:0 6px 18px rgba(0,0,0,0.06);margin-bottom:22px}
.tape{display:flex;overflow-x:auto;align-items:flex-end;padding:8px;border-radius:6px;border:1px dashed #cbd5e1}
.cell{min-width:40px;height:56px;border-right:1px solid #e2e8f0;display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0}
.head{position:relative}
.head::after{content:'';position:absolute;left:0;right:0;height:6px;background:#f97316;top:-10px;border-radius:4px}
button{padding:8px 12px;border-radius:8px;border:0;background:#2563eb;color:white;cursor:pointer;margin-top:6px;margin-right:6px;font-size:14px}
button:disabled{background:#94a3b8;cursor:not-allowed}
button.secondary{background:#64748b}
button.secondary:hover{background:#475569}
label{font-weight:600}
.small{font-size:13px;color:#475569}
.machine-card{border:2px solid #e2e8f0;border-radius:10px;padding:14px;margin-bottom:12px;cursor:pointer;transition:all 0.2s}
.machine-card:hover{border-color:#2563eb;background:#f0f9ff;transform:translateY(-2px);box-shadow:0 4px 12px rgba(37,99,235,0.1)}
.machine-card.selected{border-color:#2563eb;background:#dbeafe}
.machine-card h3{margin:0 0 6px 0;color:#1e40af;font-size:16px}
.machine-card p{margin:4px 0;font-size:14px;color:#475569}
.examples{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
.example-badge{background:#f1f5f9;padding:3px 8px;border-radius:6px;font-size:12px;font-family:monospace;color:#334155}
.grid-2{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}
.status-bar{background:#f8fafc;padding:10px;border-radius:8px;margin-top:10px;display:flex;gap:20px;flex-wrap:wrap}
.status-item{display:flex;align-items:center;gap:8px}
.status-label{font-weight:600;color:#64748b}
.status-value{color:#1e293b;font-family:monospace}
.controls{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
</style>
</head>
<body>
<nav>
 <a href="#intro">¿Qué es?</a>
 <a href="#ejemplos">Ejemplos</a>
 <a href="#practica">Simulador</a>
</nav>

<div id="intro" class="section">
<h2>¿Qué es la Máquina de Turing?</h2>

<div style="background:#f0f9ff;padding:12px;border-radius:8px;margin-bottom:16px">
<p style="margin:0;font-size:15px">Esta sección te ofrece dos perspectivas: una <strong>explicación sencilla</strong> para entender el concepto intuitivamente, y una <strong>explicación formal</strong> con la teoría matemática completa. ¡Elige la que más te ayude!</p>
</div>

<!-- EXPLICACIÓN SIMPLE -->
<div style="background:#ffffff;border:2px solid #3b82f6;border-radius:10px;padding:16px;margin-bottom:16px">
<h3 style="color:#2563eb;margin-top:0">🌟 Explicación Simple (Para todos)</h3>

<p style="font-size:16px;color:#1e40af;background:#eff6ff;padding:12px;border-radius:8px;border-left:4px solid #2563eb">
<strong>En palabras simples:</strong> Imagina una calculadora muy básica que solo puede hacer tres cosas: leer un símbolo, escribir un símbolo, y moverse a la izquierda o derecha. Aunque parece simple, ¡con estas tres acciones se puede hacer cualquier cálculo que una computadora moderna puede hacer!
</p>

<h4>🎬 La historia</h4>
<p>En 1936, Alan Turing se preguntó: "¿Qué significa realmente 'calcular' algo?". Imaginó una máquina teórica tan simple que cualquiera pudiera entenderla, pero tan poderosa que pudiera hacer cualquier cálculo posible. Esa máquina se convirtió en la base teórica de todas las computadoras modernas.</p>

<h4>🔧 Las partes de la máquina (piensa en una cinta de casete)</h4>
<ul>
 <li><strong>🎞️ La cinta infinita:</strong> Como una película de cine que nunca termina, dividida en cuadritos. Cada cuadrito puede tener una letra, un número, o estar vacío (_).</li>
 
 <li><strong>👁️ El cabezal lector:</strong> Como el láser de un reproductor de CD. Puede:
   <ul style="margin-top:6px">
     <li>📖 Leer qué hay en el cuadrito actual</li>
     <li>✏️ Escribir algo nuevo en ese cuadrito</li>
     <li>⬅️➡️ Moverse un cuadrito a la izquierda o derecha</li>
   </ul>
 </li>
 
 <li><strong>🧠 Los estados (el "humor" de la máquina):</strong> La máquina puede estar en diferentes "modos" o "estados de ánimo". Por ejemplo: "buscando a", "borrando b", "verificando si terminé", etc. Dependiendo de su estado, hace cosas diferentes.</li>
 
 <li><strong>📋 La tabla de reglas:</strong> Es como una receta de cocina. Dice: "Si estás en el estado X y ves el símbolo Y, entonces escribe Z, muévete en tal dirección, y cambia al estado W".</li>
</ul>

<div style="background:#f0fdf4;padding:14px;border-radius:8px;margin:16px 0;border-left:4px solid #22c55e">
<h4 style="margin-top:0;color:#15803d">💡 Ejemplo de la vida real</h4>
<p><strong>Imagina que verificas si una palabra es un palíndromo (se lee igual al derecho y al revés):</strong></p>
<ol style="margin:8px 0">
  <li>Lees la primera letra y la memorizas (estado: "recordando primera letra")</li>
  <li>Corres hasta el final de la palabra</li>
  <li>Verificas si la última letra es igual a la que memorizaste</li>
  <li>Si son iguales, borras ambas y repites desde el paso 1</li>
  <li>Si al final no quedan letras, ¡es un palíndromo! ✅</li>
</ol>
<p class="small">Eso es exactamente lo que hace una Máquina de Turing: seguir reglas simples repetidamente hasta resolver el problema.</p>
</div>

<h4>🎯 ¿Para qué sirve?</h4>
<p>Las Máquinas de Turing son capaces de simular <strong>cualquier algoritmo computable</strong>. Esto significa:</p>
<ul>
  <li>✅ Si se puede calcular con una computadora, se puede hacer con una Máquina de Turing</li>
  <li>✅ Si no se puede hacer con una Máquina de Turing, ¡es imposible de calcular!</li>
  <li>✅ Son el modelo teórico que define qué es "computable" en matemáticas</li>
</ul>

<div style="background:#fef2f2;padding:14px;border-radius:8px;margin:16px 0;border-left:4px solid #ef4444">
<h4 style="margin-top:0;color:#991b1b">⚠️ Conceptos clave</h4>
<p><strong>Aceptar vs Rechazar:</strong></p>
<ul style="margin:8px 0">
  <li><strong>✅ Acepta:</strong> La máquina llega a un estado final (de aceptación) y se detiene</li>
  <li><strong>❌ Rechaza:</strong> La máquina se detiene en un estado que NO es de aceptación, o no encuentra una regla que aplicar</li>
  <li><strong>⚠️ Loop infinito:</strong> A veces la máquina nunca se detiene (¡esto puede pasar!)</li>
</ul>
</div>
</div>

<!-- EXPLICACIÓN FORMAL -->
<div style="background:#ffffff;border:2px solid #8b5cf6;border-radius:10px;padding:16px;margin-bottom:16px">
<h3 style="color:#7c3aed;margin-top:0">🎓 Explicación Formal (Teoría Matemática)</h3>

<h4>Definición</h4>
<p>Una Máquina de Turing es una 7-tupla <strong>M = (Q, Σ, Γ, s, _, F, δ)</strong>, donde:</p>
<ul style="background:#faf5ff;padding:12px;border-radius:6px">
 <li><strong>Q:</strong> Conjunto finito de estados.</li>
 <li><strong>Σ:</strong> Alfabeto de entrada.</li>
 <li><strong>Γ:</strong> Alfabeto de la cinta.</li>
 <li><strong>s:</strong> Estado inicial, s ∈ Q.</li>
 <li><strong>␣:</strong> Símbolo blanco _ ∈ Γ y _ ∉ Σ.</li>
 <li><strong>F:</strong> Conjunto de estados finales o de aceptación, F ⊆ Q.</li>
 <li><strong>δ:</strong> Función parcial de transición definida por: <strong>δ: Q × Γ → Q × Γ × {L, R}</strong></li>
</ul>

<p>En la definición se supone que el valor inicial de todas las celdas de la cinta es el símbolo ␣. Se exige que ␣ ∉ Σ, donde Σ ⊆ Γ − {␣} y δ(q, σ) = (p, t, x) donde q, p ∈ Q, σ, t ∈ Γ y x es la dirección del desplazamiento de la cabeza de lectoescritura. Asumir que la cinta se extiende de izquierda a derecha.</p>

<div style="background:#fef3c7;padding:12px;border-radius:6px;margin:12px 0">
<p style="margin:0"><strong>Nota:</strong> Una función "parcial" no está necesariamente definida para todo elemento del dominio, por lo tanto, puede que δ no tenga una imagen para algún par ordenado de Q × Γ.</p>
</div>

<p>Como las transiciones dependen únicamente del estado actual y del contenido de la celda sobre la que se encuentra la cabeza de lectoescritura, entonces cualquier cadena de entrada se debe presentar a la Máquina de Turing sobre su cinta.</p>

<h4>Notación para hacerle seguimiento a la Máquina de Turing</h4>
<p>Una <strong>configuración</strong> (o descripción instantánea) es un par ordenado (qᵢ, w₁σw₂), donde qᵢ es el estado actual, w₁ es la cadena de la cinta que precede a la celda sobre la que se encuentra la cabeza de lectoescritura, σ es el símbolo de la cinta sobre el que se encuentra la cabeza de lectoescritura y w₂ es la cadena que está a la derecha de la cabeza de lectoescritura.</p>

<h4>Máquinas de Turing como aceptadoras de lenguajes</h4>
<p>Una Máquina de Turing se puede comportar como un aceptador de lenguaje, de la misma forma como lo hace un autómata finito o un autómata de pila.</p>

<p>Para reconocer una cadena w, la cadena se coloca sobre la cinta, se sitúa la cabeza de lectoescritura sobre el símbolo del extremo izquierdo de la cadena w y se coloca en marcha la Máquina de Turing comenzando en el estado inicial. La palabra w es <strong>aceptada</strong> si después de una secuencia de movimientos, la Máquina de Turing llega a un estado de aceptación y se bloquea.</p>

<h4>Ejemplo 1: L = {aⁿbⁿ | n ≥ 0}</h4>
<p><strong>Objetivo:</strong> Construir una Máquina de Turing que reconozca única y exclusivamente las palabras del lenguaje L = {aⁿbⁿ | n ≥ 0}.</p>

<h5>Estrategia:</h5>
<p>En la estrategia se utilizará la destrucción o borrado de la primera 'a' del comienzo de la palabra y compensará destruyendo (es decir, borrando) la última 'b' de la palabra. Para lograr esto:</p>
<ol style="background:#f8fafc;padding:12px;border-radius:6px">
  <li>Se borra la 'a' del comienzo y se transita a un estado con un lazo que permite mover la cabeza de lectoescritura a la derecha sobre cada símbolo hasta alcanzar el símbolo blanco de la cinta (␣).</li>
  <li>Con el símbolo blanco se transita a otro estado moviendo la cabeza a la izquierda, quedando ubicada sobre la última 'b'.</li>
  <li>En dicho estado se transita destruyendo la 'b' (sobrescribiendo ␣ en lugar de 'b').</li>
  <li>Se construye un lazo para devolver la cabeza hasta el símbolo blanco, luego se transita moviendo la cabeza a la derecha sobre la primera 'a' y se repite el proceso.</li>
  <li>El reconocimiento termina cuando ya no hay ninguna otra letra 'a', aceptando si la cabeza quedó sobre ␣ o rechazando si quedó sobre 'b'.</li>
</ol>

<h5>Especificación formal:</h5>
<p>Sea la Máquina de Turing <strong>M = (Q, Σ, Γ, s, _, F, δ)</strong> donde:</p>
<ul style="background:#faf5ff;padding:12px;border-radius:6px">
 <li><strong>Q</strong> = {q₀, q₁, q₂, q₃, q₄, q₅}</li>
 <li><strong>Σ</strong> = {a, b}</li>
 <li><strong>Γ</strong> = {_, a, b}</li>
 <li><strong>s</strong> = q₀</li>
 <li><strong>_</strong> = _</li>
 <li><strong>F</strong> = {q₅}</li>
 <div class="contenedor">
    <img src="{{ url_for('static', filename='ejemplo.jpg') }}" class="foto">
</div>

<style>
    .contenedor {
        width: 300px;
        border: 1px solid #ccc;
    }
    
    .foto {
        width: 100%;
        height: auto;
    }
</style>

<p>La Máquina de Turing M tienen el siguiente diagrama de transición:</p>

<div class="contenedor2">
    <img src="{{ url_for('static', filename='grafo_ejemplo.jpg') }}" class="foto">
</div>

<style>
    .contenedor2 {
        width: 300px;
        border: 1px solid #ccc;
    }
    
    .foto {
        width: 100%;
        height: auto;
    }
</style>
</ul>
</div>

<h3 style="margin-top:20px">🎮 ¡Ahora pruébalo tú!</h3>
<p>Más abajo encontrarás máquinas predefinidas listas para usar. Selecciona una, prueba diferentes entradas y observa cómo la máquina procesa cada símbolo paso a paso. ¡Es como ver el cerebro de una computadora en acción!</p>

</div>

<div id="ejemplos" class="section">
<h2>📚 Catálogo de Máquinas de Turing</h2>
<p>Selecciona una máquina predefinida para explorar diferentes lenguajes formales. Haz clic en cualquier tarjeta para cargarla en el simulador.</p>
<div id="machineGallery" class="grid-2">
  <div style="grid-column: 1/-1; text-align:center; padding:40px; color:#94a3b8">
    <div style="font-size:48px">⏳</div>
    <p>Cargando máquinas disponibles...</p>
  </div>
</div>
</div>

<div id="practica" class="section">
<h2>🎮 Simulador Interactivo</h2>

<div style="background:#fef3c7;padding:12px;border-radius:8px;margin-bottom:12px;border-left:4px solid #f59e0b">
  <strong>Máquina actual:</strong> <span id="currentMachineName">Ninguna seleccionada</span>
</div>

<div style="display:flex;gap:12px;margin-bottom:12px;flex-wrap:wrap;align-items:flex-end">
  <div style="flex:1;min-width:200px">
    <label>Cadena de entrada:</label>
    <input id="inputStr" value="" placeholder="Ej: aabb" 
           style="width:100%;padding:10px;border-radius:6px;border:2px solid #cbd5e1;margin-top:6px;font-family:monospace;font-size:16px" />
  </div>
  <div>
    <button id="startBtn" style="background:#059669">▶ Cargar y Empezar</button>
  </div>
</div>

<div id="exampleSuggestions" style="margin-bottom:12px"></div>

<h3>Cinta de la Máquina:</h3>
<div id="tape" class="tape" style="min-height:72px;display:flex;align-items:center;justify-content:center;color:#94a3b8">
  Carga una cadena para comenzar
</div>

<div class="controls">
  <button id="stepBtn">⏯ Un Paso</button>
  <button id="playBtn">▶ Ejecutar</button>
  <button id="resetBtn" class="secondary">🔄 Reiniciar</button>
  <div style="display:flex;align-items:center;gap:8px;margin-left:auto">
    <label style="font-size:13px">Velocidad:</label>
    <input id="speed" type="range" min="100" max="2000" value="600" style="width:120px" />
    <span id="speedLabel" style="font-size:13px;color:#64748b">600ms</span>
  </div>
</div>

<div class="status-bar">
  <div class="status-item">
    <span class="status-label">Estado:</span>
    <span class="status-value" id="state">-</span>
  </div>
  <div class="status-item">
    <span class="status-label">Posición:</span>
    <span class="status-value" id="position">-</span>
  </div>
  <div class="status-item">
    <span class="status-label">Símbolo:</span>
    <span class="status-value" id="symbol">-</span>
  </div>
  <div class="status-item">
    <span class="status-label">Pasos:</span>
    <span class="status-value" id="steps">0</span>
  </div>
  <div class="status-item">
    <span class="status-label">Resultado:</span>
    <span class="status-value" id="result" style="font-weight:bold">-</span>
  </div>
</div>

<div style="margin-top:16px">
  <h4 style="margin-bottom:8px">📋 Historial de Ejecución:</h4>
  <div id="executionLog" style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px;max-height:300px;overflow-y:auto;font-family:monospace;font-size:13px;line-height:1.6">
    <div style="color:#94a3b8;text-align:center;padding:20px">
      Ejecuta la máquina para ver el historial paso a paso
    </div>
  </div>
</div>

<div id="finalExplanation" style="display:none;margin-top:16px;padding:14px;border-radius:8px;border-left:4px solid #3b82f6">
  <h4 style="margin-top:0;color:#1e40af">🔍 Explicación del Resultado</h4>
  <p id="explanationText" style="margin:0;font-size:14px"></p>
</div>

<details style="margin-top:16px">
<summary style="cursor:pointer;font-weight:600;padding:8px;background:#f1f5f9;border-radius:6px">🔧 Ver/Editar JSON de la Máquina</summary>
<textarea id="tmDef" style="width:100%;height:200px;padding:8px;border-radius:6px;border:1px solid #cbd5e1;font-family:monospace;margin-top:8px;font-size:12px"></textarea>
</details>

</div>

<script>
let tapeEl=document.getElementById('tape');
let stateEl=document.getElementById('state');
let resultEl=document.getElementById('result');
let positionEl=document.getElementById('position');
let symbolEl=document.getElementById('symbol');
let stepsEl=document.getElementById('steps');
let executionLog=document.getElementById('executionLog');
let finalExplanation=document.getElementById('finalExplanation');
let explanationText=document.getElementById('explanationText');
let tm=null,runner=null;
let currentMachine=null;
let stepCount=0;
let executionHistory=[];

const speedInput = document.getElementById('speed');
const speedLabel = document.getElementById('speedLabel');
speedInput.oninput = () => speedLabel.innerText = speedInput.value + 'ms';

// Cargar máquinas disponibles
fetch('/machines').then(r=>r.json()).then(machines=>{
  const gallery = document.getElementById('machineGallery');
  gallery.innerHTML = ''; // Limpiar primero
  for(let key in machines){
    const m = machines[key];
    const card = document.createElement('div');
    card.className = 'machine-card';
    card.innerHTML = `
      <h3>${m.name}</h3>
      <p>${m.description}</p>
      <p class="small"><strong>Alfabeto:</strong> {${m.alphabet.join(', ')}}</p>
      <div class="examples">
        ${m.examples.map(ex => `<span class="example-badge">${ex === '' ? 'ε (vacía)' : ex}</span>`).join('')}
      </div>
    `;
    card.onclick = () => selectMachine(key, m, card);
    gallery.appendChild(card);
  }
}).catch(err => {
  console.error('Error cargando máquinas:', err);
  document.getElementById('machineGallery').innerHTML = '<p style="color:#dc2626">Error al cargar las máquinas. Recarga la página.</p>';
});

function selectMachine(key, machine, cardEl){
  // Remover selección previa
  document.querySelectorAll('.machine-card').forEach(c=>c.classList.remove('selected'));
  cardEl.classList.add('selected');
  
  currentMachine = {key: key, ...machine};
  console.log('Máquina seleccionada:', currentMachine); 
  document.getElementById('currentMachineName').innerText = machine.name;
  document.getElementById('tmDef').value = JSON.stringify(machine.machine, null, 2);
  document.getElementById('inputStr').value = machine.examples[0];
  
  // Mostrar sugerencias de ejemplos
  const suggestions = document.getElementById('exampleSuggestions');
  suggestions.innerHTML = '<p class="small" style="margin:0 0 6px 0"><strong>Ejemplos sugeridos:</strong></p>';
  machine.examples.forEach(ex => {
    const btn = document.createElement('button');
    btn.innerText = ex === '' ? 'ε (vacía)' : ex;
    btn.className = 'secondary';
    btn.style.fontSize = '12px';
    btn.style.padding = '4px 10px';
    btn.onclick = () => document.getElementById('inputStr').value = ex;
    suggestions.appendChild(btn);
  });
  
  // Scroll al simulador
  document.getElementById('practica').scrollIntoView({behavior:'smooth'});
}

function parseTM(){try{return JSON.parse(document.getElementById('tmDef').value);}catch(e){alert('JSON inválido');return null}}
function buildTape(input,blank){if(input==='') return [blank,blank]; return [blank,...input.split(''),blank,blank]}
function renderTape(t,h){
  tapeEl.innerHTML='';
  for(let i=0;i<t.length;i++){
    let c=document.createElement('div');
    c.className='cell';
    if(i===h){
      let hh=document.createElement('div');
      hh.className='head';
      hh.innerText=t[i];
      c.appendChild(hh);
      c.scrollIntoView({behavior:'smooth',inline:'center',block:'nearest'});
    }else{
      c.innerText=t[i];
    }
    tapeEl.appendChild(c);
  }
}

function createRunner(tmDef,input){
  let blank=tmDef.blank||'_';
  let tape=buildTape(input,blank);
  let head=1;
  let state=tmDef.start;
  let halted=false;
  let lastDirection='N';
  
  return{
    getTape(){return tape},
    getHead(){return head},
    getState(){return state},
    get lastDirection(){return lastDirection},
    step(){
      if(halted)return{halted:true};
      let sym=tape[head]||blank;
      let rules=(tmDef.transitions[state]&&tmDef.transitions[state][sym])||null;
      if(!rules){
        halted=true;
        state='REJECT (no rule)';
        return{halted:true,result:'❌ REJECT'};
      }
      tape[head]=rules[0];
      let mv=rules[1];
      let next=rules[2];
      lastDirection=mv;
      if(mv==='R')head++;
      else if(mv==='L')head--;
      state=next;
      if(head<0){tape.unshift(blank);head=0}
      if(head>=tape.length)tape.push(blank);
      if(tmDef.accept.indexOf(state)!==-1){
        halted=true;
        return{halted:true,result:'✅ ACCEPT'};
      }
      if(tmDef.reject.indexOf(state)!==-1){
        halted=true;
        return{halted:true,result:'❌ REJECT'};
      }
      return{halted:false};
    }
  };
}

function updateStatus(){
  if(!tm)return;
  stateEl.innerText=tm.getState();
  positionEl.innerText=tm.getHead();
  symbolEl.innerText=tm.getTape()[tm.getHead()]||'_';
  stepsEl.innerText=stepCount;
}

function addToLog(step, state, tape, head, action){
  const logEntry = document.createElement('div');
  logEntry.style.padding = '6px';
  logEntry.style.borderBottom = '1px solid #e2e8f0';
  logEntry.style.background = step % 2 === 0 ? '#ffffff' : '#f8fafc';
  
  const tapeStr = tape.map((sym, idx) => {
    if(idx === head) return `[${sym}]`;
    return sym;
  }).join(' ');
  
  logEntry.innerHTML = `
    <div style="color:#64748b;font-size:11px">Paso ${step}</div>
    <div><strong style="color:#2563eb">Estado:</strong> ${state} | <strong style="color:#059669">Acción:</strong> ${action}</div>
    <div style="color:#475569;margin-top:2px">Cinta: ${tapeStr}</div>
  `;
  
  executionHistory.push({step, state, tape: [...tape], head, action});
  executionLog.appendChild(logEntry);
  executionLog.scrollTop = executionLog.scrollHeight;
}

function generateExplanation(result, inputStr){
  finalExplanation.style.display = 'block';

  // Limpio el resultado para asegurar coincidencia
  const clean = result.replace(/[^A-Z]/g, '');

  const isAccept = clean === 'ACCEPT';
  const isReject = clean === 'REJECT';

  if(isAccept){
    finalExplanation.style.borderLeftColor = '#22c55e';
    finalExplanation.style.background = '#f0fdf4';

    let explanation = `✅ <strong>La cadena "${inputStr}" fue ACEPTADA</strong><br><br>`;

    if(currentMachine && currentMachine.key === 'anbn'){
      explanation += `La máquina verificó exitosamente que hay el mismo número de 'a' que de 'b'. `;
      explanation += `Marcó cada 'a' con 'X' y su correspondiente 'b' con 'Y', `;
      explanation += `hasta dejar toda la cadena marcada correctamente.`;
    } 
    else if(currentMachine && currentMachine.key === 'palindrome'){
      explanation += `La máquina confirmó que la cadena es un palíndromo eliminando pares simétricos de letras.`;
    } 
    else if(currentMachine && currentMachine.key === 'zerononen'){
      explanation += `La máquina comprobó que el número de '0' coincide con el número de '1'.`;
    } 
    else if(currentMachine && currentMachine.key === 'even_ones'){
      explanation += `La máquina comprobó que la cantidad de '1' es par.`;
    } 
    else if(currentMachine && currentMachine.key === 'odd_ones'){
      explanation += `La máquina comprobó que la cantidad de '1' es impar.`;
    } 
    else if(currentMachine && currentMachine.key === 'ww'){
      explanation += `La máquina verificó que la cadena consiste en una palabra seguida de sí misma.`;
    } 
    else if(currentMachine && currentMachine.key === 'anbncn'){
      explanation += `La máquina comprobó que existen igual número de 'a', 'b' y 'c', en ese orden.`;
    } 
    else {
      explanation += `La máquina llegó a un estado de aceptación según su definición.`;
    }

    explanation += `<br><br><strong>Total de pasos ejecutados:</strong> ${stepCount}`;
    explanationText.innerHTML = explanation;
  }

  else if(isReject){
    finalExplanation.style.borderLeftColor = '#ef4444';
    finalExplanation.style.background = '#fef2f2';

    let explanation = `❌ <strong>La cadena "${inputStr}" fue RECHAZADA</strong><br><br>`;

    if(currentMachine && currentMachine.key === 'anbn'){
      explanation += `La máquina detectó que no hay la misma cantidad de 'a' y 'b', `;
      explanation += `o que no están en orden correcto (todas las 'a' seguidas de todas las 'b').`;
    } 
    else if(currentMachine && currentMachine.key === 'palindrome'){
      explanation += `La cadena no es un palíndromo: los extremos no coincidieron.`;
    } 
    else if(currentMachine && currentMachine.key === 'zerononen'){
      explanation += `El número de '0' no coincide con el de '1', o están desordenados.`;
    } 
    else if(currentMachine && currentMachine.key === 'even_ones'){
      explanation += `La cantidad de '1' no es par.`;
    } 
    else if(currentMachine && currentMachine.key === 'odd_ones'){
      explanation += `La cantidad de '1' no es impar.`;
    } 
    else if(currentMachine && currentMachine.key === 'ww'){
      explanation += `La cadena no corresponde a una palabra repetida dos veces.`;
    } 
    else if(currentMachine && currentMachine.key === 'anbncn'){
      explanation += `Las cantidades de 'a', 'b' y 'c' no coinciden, o el orden no es válido.`;
    }
    else {
      explanation += `La máquina llegó a un estado de rechazo o no encontró una transición válida.`;
    }

    explanation += `<br><br><strong>La máquina se detuvo en el paso:</strong> ${stepCount}`;
    explanationText.innerHTML = explanation;
  }
}


document.getElementById('startBtn').onclick = () => {
  let t = parseTM();
  if (!t) { alert('JSON inválido'); return; }

  let input = document.getElementById('inputStr').value.trim();

  // =============================================================
  // 🔍 NUEVO: VERIFICAR QUE LA CADENA USE SOLO EL ALFABETO VÁLIDO
  // =============================================================
  if (currentMachine && currentMachine.alphabet) {
    const alphabet = currentMachine.alphabet;

    // Tomo símbolos no permitidos
    const invalid = [...input].filter(ch => !alphabet.includes(ch));

    if (invalid.length > 0) {
      finalExplanation.style.display = 'block';
      finalExplanation.style.borderLeftColor = '#ef4444';
      finalExplanation.style.background = '#fef2f2';

      explanationText.innerHTML = `
        ❌ <strong>La cadena contiene símbolos NO válidos para esta máquina.</strong><br><br>
        <strong>Alfabeto permitido:</strong> { ${alphabet.join(', ')} }<br>
        <strong>Símbolos inválidos detectados:</strong> ${invalid.map(x => `'${x}'`).join(', ')}<br><br>
        La máquina no puede procesar la cadena porque contiene símbolos que no pertenecen 
        a su lenguaje de entrada.
      `;

      // Evitar que la máquina se ejecute
      return;
    }
  }
  // =============================================================

  tm = createRunner(t, input);
  stepCount = 0;
  executionHistory = [];
  executionLog.innerHTML = '';
  finalExplanation.style.display = 'none';

  renderTape(tm.getTape(), tm.getHead());
  updateStatus();
  resultEl.innerText = '-';
  resultEl.style.color = '#1e293b';

  // Log inicial
  addToLog(0, tm.getState(), tm.getTape(), tm.getHead(), 'Estado inicial - Cadena cargada');

  if (runner) {
    clearInterval(runner);
    runner = null;
    document.getElementById('playBtn').innerText = '▶ Ejecutar';
  }
};


document.getElementById('stepBtn').onclick=()=>{
  if(!tm){alert('⚠️ Primero carga una cadena');return;}
  
  const prevState = tm.getState();
  const prevSymbol = tm.getTape()[tm.getHead()] || '_';
  const prevHead = tm.getHead();
  
  let r=tm.step();
  stepCount++;
  
  const newState = tm.getState();
  const writtenSymbol = tm.getTape()[prevHead] || '_';  // El símbolo escrito está en la posición ANTERIOR
  const direction = tm.lastDirection || 'N';
  
  let action = `Lee '${prevSymbol}' → Escribe '${writtenSymbol}' → Mueve ${direction === 'L' ? '←' : direction === 'R' ? '→' : '•'} → Va a ${newState}`;
  
  renderTape(tm.getTape(),tm.getHead());
  updateStatus();
  addToLog(stepCount, newState, tm.getTape(), tm.getHead(), action);
  
  if(r.halted){
    resultEl.innerText=r.result;
    resultEl.style.color=r.result.includes('ACCEPT')?'#059669':'#dc2626';
    
    const inputStr = document.getElementById('inputStr').value.trim() || 'ε (vacía)';
    generateExplanation(r.result, inputStr);
  }
};

document.getElementById('playBtn').onclick=()=>{
  if(!tm){alert('⚠️ Primero carga una cadena');return;}
  if(runner){
    clearInterval(runner);
    runner=null;
    document.getElementById('playBtn').innerText='▶ Ejecutar';
    return;
  }
  document.getElementById('playBtn').innerText='⏸ Pausar';
  runner=setInterval(()=>{
    const prevState = tm.getState();
    const prevSymbol = tm.getTape()[tm.getHead()] || '_';
    const prevHead = tm.getHead();
    
    let r=tm.step();
    stepCount++;
    
    const newState = tm.getState();
    const writtenSymbol = tm.getTape()[prevHead] || '_';
    const direction = tm.lastDirection || 'N';
    
    let action = `Lee '${prevSymbol}' → Escribe '${writtenSymbol}' → Mueve ${direction === 'L' ? '←' : direction === 'R' ? '→' : '•'} → Va a ${newState}`;
    
    renderTape(tm.getTape(),tm.getHead());
    updateStatus();
    addToLog(stepCount, newState, tm.getTape(), tm.getHead(), action);
    
    if(r.halted){
      resultEl.innerText=r.result;
      resultEl.style.color=r.result.includes('ACCEPT')?'#059669':'#dc2626';
      clearInterval(runner);
      runner=null;
      document.getElementById('playBtn').innerText='▶ Ejecutar';
      
      const inputStr = document.getElementById('inputStr').value.trim() || 'ε (vacía)';
      generateExplanation(r.result, inputStr);
    }
  },parseInt(speedInput.value));
};

document.getElementById('resetBtn').onclick=()=>{
  tm=null;
  stepCount=0;
  executionHistory=[];
  if(runner){clearInterval(runner);runner=null;}
  tapeEl.innerHTML='<div style="color:#94a3b8">Carga una cadena para comenzar</div>';
  stateEl.innerText='-';
  positionEl.innerText='-';
  symbolEl.innerText='-';
  stepsEl.innerText='0';
  resultEl.innerText='-';
  resultEl.style.color='#1e293b';
  document.getElementById('playBtn').innerText='▶ Ejecutar';
  executionLog.innerHTML='<div style="color:#94a3b8;text-align:center;padding:20px">Ejecuta la máquina para ver el historial paso a paso</div>';
  finalExplanation.style.display='none';
};


</script>
</body>
</html>
'''


@app.route('/')
def index():
    return render_template_string(PAGE)


@app.route('/machines', methods=['GET'])
def get_machines():
    """Retorna el catálogo de máquinas disponibles"""
    simplified = {}
    for key, data in MACHINE_LIBRARY.items():
        simplified[key] = {
            'name': data['name'],
            'description': data['description'],
            'examples': data['examples'],
            'alphabet': data['alphabet'],
            'machine': data['machine']
        }
    return jsonify(simplified)


if __name__ == '__main__':
    threading.Timer(1.2, lambda: webbrowser.open('http://127.0.0.1:5000')).start()
    app.run()

