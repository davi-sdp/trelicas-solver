test_cases = [
    {
        "name": "Caso de Teste 1",
        "n_nos": 2, # número de nós
        "n_forcas": 2, # número de forças
        "n_barras": 1, # número de barras
        "n_apoios": 1, # número de apoios
        "coords": [(0, 0), (3, 5)], # Coordenadas dos nós (x, y)
        "forcas": [(0, -1000, 1), (0, -500, 2)], # Força de 1000N para baixo no nó 1 e 500N para baixo no nó 2
        "barras": [(1, 2)], # 1 barra conectando os nós 1 e 2
        "apoios": {1: 1}, # Nó 1 é um apoio fixo
        "chao": True
    }
]