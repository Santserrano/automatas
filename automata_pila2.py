import matplotlib.pyplot as plt
import matplotlib.patches as patches
from IPython.display import clear_output
import time

# Paleta de colores exacta
COLORS = {
    'q0': '#5C73B8', 'q1': '#1DB09E', 'q2': '#835CB8', 'q3': '#4C9E5C',
    'bg_label': '#F1F5F9', 'text': '#475569', 'highlight': '#FFD700'
}

class AutomataVisual:
    def __init__(self, cadena):
        self.cadena = cadena
        self.pila = ['Z']
        self.estado_actual = 'q0'
        self.idx = 0

    def graficar(self, char_actual):
        clear_output(wait=True)
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.set_aspect('equal') # EVITA QUE SE VEA ESTIRADO

        pos = {'q0': (0, 0), 'q1': (2.5, 0), 'q2': (5, 0), 'q3': (7.5, 0)}

        # 1. Dibujar transiciones (Flechas)
        self._f(ax, pos['q0'], pos['q1'], "ε, Z / push Z")
        self._f(ax, pos['q1'], pos['q2'], "b, A / pop A")
        self._f(ax, pos['q2'], pos['q3'], "ε, Z / -")

        # 2. Dibujar Bucles (a y b)
        self._bucle(ax, pos['q1'], "a, * / push A", COLORS['q1'])
        self._bucle(ax, pos['q2'], "b, A / pop A", COLORS['q2'])

        # 3. Dibujar Nodos
        for nodo, p in pos.items():
            # Borde de resaltado si es el estado actual
            if nodo == self.estado_actual:
                ax.add_patch(patches.Circle(p, 0.42, color=COLORS['highlight'], zorder=1))

            # Círculo principal
            ax.add_patch(patches.Circle(p, 0.38, color=COLORS[nodo], zorder=2))

            # Doble círculo para q3 (Aceptación)
            if nodo == 'q3':
                ax.add_patch(patches.Circle(p, 0.45, fill=False, edgecolor=COLORS['q3'], lw=2))

            ax.text(p[0], p[1], nodo, color='white', ha='center', va='center', fontsize=14, fontweight='bold', zorder=3)

        # Flecha de inicio
        ax.annotate('inicio', xy=(0, 0), xytext=(-1, 0), arrowprops=dict(arrowstyle='->', color='#475569'), va='center', ha='right')

        # 4. Leyenda inferior
        self._leyenda(ax)

        plt.title(f"Estado: {'ACEPTADA' if self.estado_actual == 'q3' else 'PROCESANDO'} | Leyendo: '{char_actual}' | Pila: {self.pila}",
                  fontsize=14, fontweight='bold', pad=20)
        plt.xlim(-1.5, 9)
        plt.ylim(-1.5, 1.5)
        plt.axis('off')
        plt.show()

    def _f(self, ax, p1, p2, txt):
        ax.annotate("", xy=(p2[0]-0.4, p2[1]), xytext=(p1[0]+0.4, p1[1]),
                    arrowprops=dict(arrowstyle='-|>', color='#475569', lw=1.5))
        ax.text((p1[0]+p2[0])/2, 0.15, txt, fontsize=10, ha='center', fontweight='bold',
                color='#475569', bbox=dict(facecolor='white', edgecolor='none', alpha=0.8))

    def _bucle(self, ax, p, txt, color):
        arc = patches.Arc((p[0], p[1]+0.4), 0.6, 0.6, theta1=0, theta2=180, color=color, lw=2)
        ax.add_patch(arc)
        # Punta de la flecha del bucle
        ax.annotate("", xy=(p[0]-0.25, p[1]+0.4), xytext=(p[0]-0.26, p[1]+0.4),
                    arrowprops=dict(arrowstyle='->', color=color, lw=2))
        ax.text(p[0], p[1]+0.8, txt, fontsize=10, ha='center', fontweight='bold', color='#475569')

    def _leyenda(self, ax):
        items = [('q0', 'Estado inicial'), ('q1', "Leyendo a's (apilando)"),
                 ('q2', "Leyendo b's (desapilando)"), ('q3', 'Estado de aceptación')]
        for i, (k, v) in enumerate(items):
            x_off = 0 if i < 2 else 4
            y_off = -1.0 if i % 2 == 0 else -1.3
            ax.add_patch(patches.Rectangle((x_off, y_off), 0.3, 0.15, color=COLORS[k]))
            ax.text(x_off+0.4, y_off+0.07, f"{k} — {v}", va='center', fontsize=10, color='#475569')

    def run(self):
        # Simulación simplificada de pasos
        steps = [('q0', 'ε'), ('q1', 'a'), ('q1', 'a'), ('q2', 'b'), ('q2', 'b'), ('q3', 'FIN')]
        for est, char in steps:
            self.estado_actual = est
            if char == 'a': self.pila.append('A')
            elif char == 'b': self.pila.pop()
            self.graficar(char)
            time.sleep(1.2)

# Ejecutar
AutomataVisual("aabb").run()