alfabeto = {chr(65 + i): i for i in range(26)} # gera o dicionario com as letras e os index delas

def entra(texto, tipo=str):
    """Função utilitária para validar entradas de dados."""
    while True:
        try:
            valor = tipo(input(texto))
            if valor == "":
                continue
            return valor
        except ValueError:
            print(f"Digite um valor válido do tipo {tipo.__name__}")

def verificar_intersecao(p1, p2, p3, p4):
    """
    Verifica se o segmento (p1,p2) cruza com (p3,p4) usando o produto vetorial.
    p = (x, y)
    """
    def ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

    # Se os segmentos compartilham um nó, não contamos como cruzamento proibido
    if len({p1, p2, p3, p4}) < 4:
        return False

    return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)

def obter_equacao_reta(p1, p2):
    """Retorna m e c para y = mx + c ou (None, x) se vertical."""
    x1, y1 = p1
    x2, y2 = p2
    if x2 - x1 == 0:
        return None, x1
    m = (y2 - y1) / (x2 - x1)
    c = y1 - m * x1
    return m, c