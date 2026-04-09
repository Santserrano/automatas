"""
AUTÓMATA DE PILA (PDA - Pushdown Automaton) - Implementación Educacional
=========================================================================

¿Qué es un Autómata de Pila?
------------------------------
Un Autómata de Pila es como un AFD pero con una PILA (stack) auxiliar.
Esa pila le da memoria ILIMITADA, permitiéndole reconocer lenguajes
que un AFD NUNCA podría procesar.

Definición formal:  M = (Q, Σ, Γ, δ, q0, Z0, F)
  ─────────────────────────────────────────────
  Q   : Conjunto finito de estados
  Σ   : Alfabeto de entrada  (símbolos que lee de la cinta)
  Γ   : Alfabeto de pila     (símbolos que puede apilar/desapilar)
  δ   : Función de transición
  q0  : Estado inicial
  Z0  : Símbolo de fondo de pila (marca el inicio de la pila)
  F   : Conjunto de estados de aceptación

La función de transición δ:
  δ(estado_actual, símbolo_leído, tope_de_pila) → (nuevo_estado, lo_que_se_apila)

  Siempre se hace POP del tope, luego PUSH de "lo_que_se_apila".
  Si "lo_que_se_apila" es [] → solo hubo POP (no se apila nada nuevo).
  La cadena 'ε' en el símbolo_leído → transición épsilon (sin consumir entrada).

════════════════════════════════════════════════════════════════════════════
  EJEMPLO: Lenguaje L = { a^n b^n | n ≥ 1 }
════════════════════════════════════════════════════════════════════════════
  Cadenas VÁLIDAS  :  ab   aabb   aaabbb   aaaabbbb
  Cadenas INVÁLIDAS:  a    b      ba       aab     abb

  Un AFD NO puede reconocer este lenguaje porque necesita recordar cuántas
  'a' leyó, sin ningún límite superior. La PILA resuelve esto:

    Estrategia:
      1. Por cada 'a' leída  →  hacer PUSH de 'A' en la pila
      2. Por cada 'b' leída  →  hacer POP  de 'A' de la pila
      3. Al terminar la cadena: si la pila solo tiene el fondo 'Z' → ACEPTAR

  Estados:
    q0  →  Estado inicial / leyendo las 'a'
    q1  →  Empezamos a leer las 'b' (ya no podemos leer más 'a')
    q2  →  Estado de aceptación (pila vaciada correctamente)

  Transiciones:
    δ(q0, 'a', 'Z') = (q0, ['Z','A'])   ←  primer  'a': reponemos Z, apilamos A (tope=A)
    δ(q0, 'a', 'A') = (q0, ['A','A'])   ←  demás   'a': reponemos A, apilamos otro A
    δ(q0, 'b', 'A') = (q1, [])          ←  primera 'b': desapilamos A
    δ(q1, 'b', 'A') = (q1, [])          ←  demás   'b': seguimos desapilando
    δ(q1, 'ε', 'Z') = (q2, ['Z'])       ←  pila vacía (solo Z): ACEPTAR

  push_list usa el convenio: el ÚLTIMO elemento queda en el tope.
    ['Z', 'A'] → pila crece como [..., Z, A]  donde tope es A.
"""

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    HAS_LIBS = True
except ImportError:
    HAS_LIBS = False
    print("=" * 60)
    print("ATENCIÓN: 'networkx' y 'matplotlib' no están instaladas.")
    print("El programa correrá en modo texto.")
    print("Para ver el gráfico: pip install networkx matplotlib")
    print("=" * 60 + "\n")


# ─────────────────────────────────────────────────────────────
#  Símbolo especial para epsilon (transición sin leer entrada)
# ─────────────────────────────────────────────────────────────
EPSILON = 'ε'
FONDO   = 'Z'   # Símbolo que marca el fondo de la pila


class AutomataDePila:
    """
    Autómata de Pila determinista que reconoce L = { a^n b^n | n >= 1 }.

    La pila se representa como una lista de Python donde:
      - pila[-1]  es el TOPE  (el elemento más reciente)
      - pila[0]   es el FONDO (símbolo 'Z', siempre el último)
    """

    def __init__(self):
        # ── Componentes formales ──────────────────────────────────────────
        self.Q  = ['q0', 'q1', 'q2']           # Estados (lista para orden determinista)
        self.sigma = {'a', 'b'}                 # Alfabeto de entrada
        self.gamma = {'A', FONDO}               # Alfabeto de pila
        self.q0 = 'q0'                          # Estado inicial
        self.Z0 = FONDO                         # Fondo de pila
        self.F  = {'q2'}                        # Estados de aceptación

        # ── Función de transición ─────────────────────────────────────────
        # Formato: delta[(estado, símbolo_entrada, tope_pila)] = (sig_estado, lo_que_se_apila)
        # "lo_que_se_apila" es una lista donde el ÚLTIMO elemento queda en el tope.
        # Ejemplo: ['Z','A'] → se apila primero Z (fondo) luego A → tope es A.
        self.delta = {
            ('q0', 'a', FONDO): ('q0', [FONDO, 'A']),   # primer 'a': tope→A
            ('q0', 'a', 'A'):   ('q0', ['A', 'A']),     # más 'a': tope→A
            ('q0', 'b', 'A'):   ('q1', []),              # primera 'b': pop A
            ('q1', 'b', 'A'):   ('q1', []),              # más 'b': pop A
            ('q1', EPSILON, FONDO): ('q2', [FONDO]),     # pila vacía → aceptar
        }

        # ── Posiciones para el grafo visual ──────────────────────────────
        if HAS_LIBS:
            self.pos = {
                'q0': (0, 0),
                'q1': (3, 0),
                'q2': (6, 0),
            }

    # ──────────────────────────────────────────────────────────────────────
    #  Método auxiliar: intentar transición épsilon si corresponde
    # ──────────────────────────────────────────────────────────────────────
    def _transicion_epsilon(self, estado, pila):
        """Retorna (nuevo_estado, nueva_pila) si hay transición ε, o None."""
        if not pila:
            return None
        tope = pila[-1]
        clave = (estado, EPSILON, tope)
        if clave in self.delta:
            sig_estado, push_list = self.delta[clave]
            nueva_pila = pila[:-1] + push_list  # pop tope, push lo nuevo
            return sig_estado, nueva_pila
        return None

    # ──────────────────────────────────────────────────────────────────────
    #  Visualización con matplotlib
    # ──────────────────────────────────────────────────────────────────────
    def _dibujar(self, estado_actual, pila, paso, simbolo_leido=None, entrada_restante=""):
        if not HAS_LIBS:
            return

        fig = plt.gcf()
        fig.clf()

        # Dos paneles: izquierda = grafo de estados, derecha = pila
        ax_grafo = fig.add_axes([0.03, 0.1, 0.62, 0.80])   # [left, bot, w, h]
        ax_pila  = fig.add_axes([0.70, 0.1, 0.26, 0.80])

        # ── Panel izquierdo: grafo de estados ────────────────────────────
        G = nx.DiGraph()
        for s in self.Q:
            G.add_node(s)

        # Etiquetas de aristas (resumimos las transiciones del delta)
        edges_labels = {}
        for (est, sym, tope), (sig_est, push) in self.delta.items():
            push_str = ''.join(push) if push else 'ε'
            label = f"{sym}/{tope}→{push_str}"
            key = (est, sig_est)
            existing = edges_labels.get(key, [])
            existing.append(label)
            edges_labels[key] = existing
            G.add_edge(est, sig_est)

        # Colores de nodos
        color_map = []
        for s in self.Q:
            if s == estado_actual:
                if s in self.F:
                    color_map.append('#00DD44')   # verde → aceptación activa
                else:
                    color_map.append('#FFDD00')   # amarillo → estado activo
            else:
                if s in self.F:
                    color_map.append('#AAFFCC')   # verde pálido
                else:
                    color_map.append('#ADD8E6')   # azul claro

        nx.draw_networkx_nodes(G, self.pos, ax=ax_grafo,
                               node_color=color_map, node_size=1800, edgecolors='black')
        nx.draw_networkx_labels(G, self.pos, ax=ax_grafo,
                                font_size=11, font_weight='bold')

        # Aristas — separamos self-loops de aristas normales
        regular_edges = [(u, v) for u, v in G.edges() if u != v]
        self_loops = [(u, v) for u, v in G.edges() if u == v]
        nx.draw_networkx_edges(G, self.pos, edgelist=regular_edges, ax=ax_grafo,
                               arrowsize=20, node_size=1800,
                               connectionstyle='arc3,rad=0.1')
        nx.draw_networkx_edges(G, self.pos, edgelist=self_loops, ax=ax_grafo,
                               arrowsize=15, node_size=1800,
                               connectionstyle='arc3,rad=0.4')

        # Etiquetas de aristas
        for (u, v), labels in edges_labels.items():
            x1, y1 = self.pos[u]
            x2, y2 = self.pos[v]
            if u == v:
                # Self-loop: etiqueta arriba del nodo
                mx, my = x1, y1 + 0.85
            else:
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + 0.25
            ax_grafo.text(mx, my, '\n'.join(labels),
                          fontsize=7, ha='center', va='center',
                          color='darkred',
                          bbox=dict(boxstyle='round,pad=0.2', fc='lightyellow', alpha=0.8))

        # Marcar estado inicial con flecha
        xi, yi = self.pos[self.q0]
        ax_grafo.annotate('', xy=(xi, yi),
                          xytext=(xi - 1.0, yi),
                          arrowprops=dict(arrowstyle='->', color='black', lw=2))

        # Marcar estados de aceptación con doble círculo
        for s in self.F:
            xf, yf = self.pos[s]
            circle = plt.Circle((xf, yf), 0.28, fill=False,
                                 edgecolor='black', linewidth=2)
            ax_grafo.add_patch(circle)

        ax_grafo.set_xlim(-1.5, 7.5)
        ax_grafo.set_ylim(-1.5, 1.5)
        ax_grafo.axis('off')

        # Subtítulo del grafo
        titulo = f"Paso {paso}"
        if simbolo_leido is not None:
            titulo += f"  |  Leyó: '{simbolo_leido}'"
        titulo += f"  |  Estado: {estado_actual}"
        if entrada_restante:
            titulo += f"\nEntrada restante: '{entrada_restante}'"
        ax_grafo.set_title(titulo, fontsize=10, pad=6)

        # ── Panel derecho: visualización de la PILA ──────────────────────
        ax_pila.set_xlim(0, 2)
        ax_pila.set_ylim(-0.5, 10)
        ax_pila.axis('off')
        ax_pila.set_title("PILA (stack)", fontsize=11, fontweight='bold', pad=6)

        if not pila:
            ax_pila.text(1, 4, "(vacía)", ha='center', va='center',
                         fontsize=10, color='gray')
        else:
            # Dibujar cada elemento de la pila (el tope arriba)
            altura_base = 0.4
            max_visible = 8
            inicio = max(0, len(pila) - max_visible)
            segmento = pila[inicio:]

            for i, elem in enumerate(segmento):
                y = altura_base + i * 1.0
                es_tope = (i == len(segmento) - 1)
                color_caja = '#FF9966' if es_tope else '#FFE0CC'
                rect = mpatches.FancyBboxPatch(
                    (0.3, y), 1.4, 0.75,
                    boxstyle="round,pad=0.05",
                    linewidth=1.5,
                    edgecolor='#884400',
                    facecolor=color_caja
                )
                ax_pila.add_patch(rect)
                ax_pila.text(1.0, y + 0.375, elem,
                             ha='center', va='center',
                             fontsize=14, fontweight='bold')
                if es_tope:
                    ax_pila.text(1.85, y + 0.375, '← tope',
                                 ha='left', va='center', fontsize=7, color='gray')

            # Flecha "base de la pila" debajo del primer elemento
            ax_pila.text(1.0, altura_base - 0.35, '▼ fondo',
                         ha='center', va='top', fontsize=8, color='gray')

        plt.draw()
        plt.pause(1.2)

    # ──────────────────────────────────────────────────────────────────────
    #  Método principal: procesar una cadena de entrada
    # ──────────────────────────────────────────────────────────────────────
    def procesar(self, cadena):
        """
        Simula el autómata de pila sobre la cadena dada.
        Muestra cada paso en consola (y opcionalmente en gráfico).
        """
        estado  = self.q0
        pila    = [self.Z0]   # Pila inicial: solo el fondo Z
        paso    = 0

        print(f"\n{'─'*60}")
        print(f"  Procesando: '{cadena}'")
        print(f"{'─'*60}")
        print(f"  Estado inicial : {estado}")
        print(f"  Pila inicial   : {self._repr_pila(pila)}")
        print(f"{'─'*60}")

        self._dibujar(estado, pila, paso, entrada_restante=cadena)

        for i, simbolo in enumerate(cadena):
            tope = pila[-1] if pila else None
            clave = (estado, simbolo, tope)

            if clave not in self.delta:
                # Intentar transición ε antes de rechazar
                resultado_eps = self._transicion_epsilon(estado, pila)
                if resultado_eps:
                    estado, pila = resultado_eps
                    paso += 1
                    print(f"  Paso {paso}: δ({estado}, ε, '{tope}') "
                          f"→ transición ε  |  Pila: {self._repr_pila(pila)}")
                    self._dibujar(estado, pila, paso, EPSILON, cadena[i:])
                    # Re-intentar con el nuevo estado
                    tope = pila[-1] if pila else None
                    clave = (estado, simbolo, tope)

                if clave not in self.delta:
                    paso += 1
                    print(f"  Paso {paso}: '{simbolo}' con tope '{tope}' en {estado} → SIN TRANSICIÓN")
                    self._dibujar(estado, pila, paso, simbolo, cadena[i+1:])
                    print(f"\n  [RECHAZADA] No existe transición válida.\n")
                    return False

            sig_estado, push_list = self.delta[clave]
            pila = pila[:-1] + push_list   # pop tope + push lo nuevo

            paso += 1
            push_str = ''.join(push_list) if push_list else 'ε (solo pop)'
            print(f"  Paso {paso}: δ({estado}, '{simbolo}', '{tope}') "
                  f"→ ({sig_estado}, [{push_str}])  |  Pila: {self._repr_pila(pila)}")

            estado = sig_estado
            self._dibujar(estado, pila, paso, simbolo, cadena[i+1:])

        # ── Intentar transición épsilon al final ─────────────────────────
        resultado_eps = self._transicion_epsilon(estado, pila)
        if resultado_eps:
            tope_antes = pila[-1]
            sig_estado, nueva_pila = resultado_eps
            paso += 1
            print(f"  Paso {paso}: δ({estado}, ε, '{tope_antes}') "
                  f"→ ({sig_estado})  [transición ε]"
                  f"  |  Pila: {self._repr_pila(nueva_pila)}")
            estado, pila = sig_estado, nueva_pila
            self._dibujar(estado, pila, paso, EPSILON, "")

        # ── Decisión de aceptación / rechazo ─────────────────────────────
        aceptada = estado in self.F
        print(f"{'─'*60}")
        if aceptada:
            print(f"  [ACEPTADA]  Estado final: {estado}  |  Pila: {self._repr_pila(pila)}")
        else:
            print(f"  [RECHAZADA] Estado final: {estado}  |  Pila: {self._repr_pila(pila)}")
            if pila != [FONDO]:
                print(f"             La pila no quedó solo con el fondo {FONDO}.")
        print(f"{'─'*60}\n")
        return aceptada

    def _repr_pila(self, pila):
        """Muestra la pila de forma legible: [fondo → ... → tope]."""
        if not pila:
            return "[ vacía ]"
        return "[" + " → ".join(pila) + "]  ← tope: " + pila[-1]


# ──────────────────────────────────────────────────────────────────────────
#  Punto de entrada
# ──────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if HAS_LIBS:
        plt.ion()
        fig = plt.figure("Autómata de Pila: aⁿbⁿ", figsize=(12, 5))

    pda = AutomataDePila()

    print("=" * 60)
    print("  SIMULADOR DE AUTÓMATA DE PILA")
    print("  Lenguaje: L = { aⁿbⁿ | n ≥ 1 }")
    print("  Ejemplos válidos:   ab  aabb  aaabbb")
    print("  Ejemplos inválidos: a   b   ba   aab")
    print("=" * 60)
    print("\n  Teoría rápida:")
    print("  ┌─────────────────────────────────────────────┐")
    print("  │  δ(estado, entrada, tope) → (nuevo, push)   │")
    print("  │  'push' vacío  = solo se hizo POP del tope  │")
    print("  └─────────────────────────────────────────────┘")
    print("\n  Escribí 'teoria' para ver las transiciones.")
    print("  Escribí 'salir'  para terminar.\n")

    while True:
        try:
            entrada = input("  Ingresá la cadena: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n  Cerrando...\n")
            break

        if entrada.lower() == 'salir':
            print("  ¡Nos vemos!\n")
            break
        elif entrada.lower() == 'teoria':
            print("\n  Transiciones del autómata:")
            print("  ─────────────────────────────────────────────────")
            for (est, sym, tope), (sig, push) in sorted(pda.delta.items()):
                push_str = ''.join(push) if push else 'ε'
                print(f"  δ({est}, {sym}, {tope}) → ({sig}, [{push_str}])")
            print("  ─────────────────────────────────────────────────\n")
        else:
            pda.procesar(entrada)
