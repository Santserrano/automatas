import sys

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    HAS_LIBS = True
except ImportError:
    HAS_LIBS = False
    print("=========================================================")
    print("⚠️ ATENCIÓN: Las librerías 'networkx' y 'matplotlib' NO están instaladas.")
    print("El programa se ejecutará en modo texto exclusivamente.")
    print("Para ver los gráficos iterativos, cancelá (Ctrl+C) e instalalas con:")
    print("pip install networkx matplotlib")
    print("=========================================================\n")

class AFD_HolaMundo:
    def __init__(self):

        self.Q = {
            'q0', 'q1', 'q2', 'q3', 'q4',
            'q5', 'q6', 'q7', 'q8', 'q9', 'q10', 'q_trampa'
        }
        self.q0 = 'q0'
        self.F = {'q10'}

        self.delta = {
            'q0': {'h': 'q1'},
            'q1': {'o': 'q2'},
            'q2': {'l': 'q3'},
            'q3': {'a': 'q4'},
            'q4': {' ': 'q5'},
            'q5': {'m': 'q6'},
            'q6': {'u': 'q7'},
            'q7': {'n': 'q8'},
            'q8': {'d': 'q9'},
            'q9': {'o': 'q10'},
            'q10': {},
            'q_trampa': {}
        }

        # Preparamos las coordenadas para el grafo interactivo
        if HAS_LIBS:
            # Dibujamos q0..q10 en línea recta horizontal
            self.pos = {f'q{i}': (i * 2, 0) for i in range(11)}
            # Ponemos el estado trampa más abajo en el centro
            self.pos['q_trampa'] = (10, -2)

    def draw_automaton(self, current_state, step, char_read=None):
        if not HAS_LIBS:
            return

        plt.clf()
        G = nx.DiGraph()

        # Agregar nodos
        for s in self.Q:
            G.add_node(s)

        # Determinar aristas en base a delta
        edges_dict = {}
        for from_s, trans in self.delta.items():
            for char, to_s in trans.items():
                if (from_s, to_s) not in edges_dict:
                    edges_dict[(from_s, to_s)] = []
                edges_dict[(from_s, to_s)].append(char)

        for (from_s, to_s), chars in edges_dict.items():
            # Si el carácter es un espacio en blanco, lo hacemos visible con un texto distintivo
            labels = ["'<esp>'" if c == ' ' else f"'{c}'" for c in chars]
            G.add_edge(from_s, to_s, label=','.join(sorted(labels)))

        # Coloreado dinámico para identificar en qué estado estamos
        node_colors = []
        for s in self.Q:
            if s == current_state:
                if s in self.F:
                    node_colors.append('#00FF00') # Verde encendido (Aceptación actual)
                elif s == 'q_trampa':
                    node_colors.append('#FF4500') # Rojo anaranjado (Trampa actual)
                else:
                    node_colors.append('#FFFF00') # Amarillo (Normal actual)
            else:
                if s in self.F:
                    node_colors.append('#D3FFD3') # Verde pálido (Aceptación inactivo)
                elif s == 'q_trampa':
                    node_colors.append('#FFB6C1') # Rosa claro (Trampa inactivo)
                else:
                    node_colors.append('#ADD8E6') # Azul claro (Normal inactivo)

        # Dibujar red de nodos
        nx.draw_networkx_nodes(G, self.pos, node_color=node_colors, node_size=1000, edgecolors='black')
        labels = {n: n for n in self.Q}
        nx.draw_networkx_labels(G, self.pos, labels=labels, font_size=10, font_weight='bold')

        # Dibujar aristas
        regular_edges = [e for e in G.edges() if e[0] != e[1]]
        nx.draw_networkx_edges(G, self.pos, edgelist=regular_edges, arrowsize=15, node_size=1000)

        # Dibujar etiquetas de las aristas (letras procesadas)
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, self.pos, edge_labels=edge_labels, font_size=10, font_color='red')

        # Control del Título
        title = f"--- PASO {step} ---"
        if char_read is not None:
            display_char = "<espacio>" if char_read == ' ' else char_read
            title += f"\nCarácter leído: '{display_char}'"
        title += f"\nEstado Actual: {current_state}"

        if current_state == 'q_trampa':
            title += " (¡Trampa!)"

        plt.title(title, fontsize=12, pad=10)
        plt.axis('off')

        # Efecto de loop visual
        plt.draw()
        plt.pause(1.0) # Pausa reducida a 1 segundo para agilizar la lectura

    def procesar_cadena(self, cadena):
        estado_actual = self.q0
        print(f"[*] Iniciando en estado: {estado_actual}")

        # Dibujamos el estado inicial antes de leer cualquier caracter
        self.draw_automaton(estado_actual, step=0)

        for i, simbolo in enumerate(cadena):
            diccionario_estado = self.delta.get(estado_actual, {})
            # Cualquier caracter no esperado va directo a q_trampa
            estado_siguiente = diccionario_estado.get(simbolo, 'q_trampa')

            print(f"    Estado {estado_actual:<8} --(lee '{simbolo}')--> Estado {estado_siguiente}")
            estado_actual = estado_siguiente

            # Dibujamos este cambio de estado
            self.draw_automaton(estado_actual, step=i+1, char_read=simbolo)

            if estado_actual == 'q_trampa':
                print("    [!] Secuencia rota. Cayó en el estado trampa.")
                # Aunque caiga en estado trampa, podríamos seguir mostrando la animación,
                # pero si se rompió la secuencia, optimizamos saliendo:
                break

        es_aceptada = estado_actual in self.F

        print("-" * 40)
        if es_aceptada:
            print(f"[✓] Cadena ACEPTADA. Finalizó en el estado final: {estado_actual}")
        else:
            print(f"[X] Cadena RECHAZADA. Finalizó en el estado: {estado_actual}")

        return es_aceptada

if __name__ == "__main__":
    if HAS_LIBS:
        plt.ion() # Modo interactivo para evitar el bloqueo del input
        plt.figure("Simulador de AFD: Hola Mundo", figsize=(15, 5))

    afd = AFD_HolaMundo()

    print("===========================================")
    print(" Simulador de Autómata: 'hola mundo'")
    print("===========================================")
    print("Escribí 'salir' para terminar el programa.\n")

    while True:
        try:
            cadena_usuario = input("Ingresá la cadena a evaluar (o 'salir'): ")
        except KeyboardInterrupt:
            break

        if cadena_usuario.lower() == 'salir':
            print("¡Nos vemos! Cerrando simulador...")
            break

        print(f"\nProcesando la cadena: '{cadena_usuario}'\n" + "-"*40)
        afd.procesar_cadena(cadena_usuario)
        print("\n")