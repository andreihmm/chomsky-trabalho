import sys
from collections import defaultdict

def ler_gramatica(caminho):
    with open(caminho, 'r') as f:
        linhas = [linha.strip() for linha in f if linha.strip()]
    
    variaveis = linhas[0].split()
    inicial = linhas[1]
    producoes = defaultdict(list)
    
    for linha in linhas[2:]:
        partes = linha.split()
        esquerda = partes[0]
        direita = partes[1:]
        producoes[esquerda].append(direita)
    
    return variaveis, inicial, producoes

def remover_vazias(producoes):
    anulaveis = set()
    for v, regras in producoes.items():
        for r in regras:
            if r == ['ε']:
                anulaveis.add(v)
    mudou = True
    while mudou:
        mudou = False
        for v, regras in producoes.items():
            for r in regras:
                if all(s in anulaveis for s in r) and v not in anulaveis:
                    anulaveis.add(v)
                    mudou = True
    novas = defaultdict(list)
    for v, regras in producoes.items():
        for r in regras:
            if r == ['ε']:
                continue
            novas[v].append(r)
            indices = [i for i, s in enumerate(r) if s in anulaveis]
            for i in range(1, 1 << len(indices)):
                nova = r[:]
                for j in range(len(indices)):
                    if i & (1 << j):
                        nova[indices[j]] = None
                alternativa = [s for s in nova if s]
                if alternativa:
                    novas[v].append(alternativa)
    return novas

def remover_unitarias(producoes):
    unitarias = defaultdict(set)
    for v in producoes:
        for r in producoes[v]:
            if len(r) == 1 and r[0].isupper():
                unitarias[v].add(r[0])
    
    mudou = True
    while mudou:
        mudou = False
        for v in list(unitarias):
            novos = set()
            for u in unitarias[v]:
                novos |= unitarias[u]
            if not novos.issubset(unitarias[v]):
                unitarias[v] |= novos
                mudou = True

    novas = defaultdict(list)
    for v in producoes:
        for r in producoes[v]:
            if not (len(r) == 1 and r[0].isupper()):
                novas[v].append(r)
        for u in unitarias[v]:
            for r in producoes[u]:
                if not (len(r) == 1 and r[0].isupper()):
                    novas[v].append(r)
    return novas

def remover_inuteis(variaveis, inicial, producoes):
    geradores = set()
    for v in variaveis:
        for r in producoes[v]:
            if all(s.islower() for s in r):
                geradores.add(v)
    mudou = True
    while mudou:
        mudou = False
        for v in variaveis:
            if v not in geradores:
                for r in producoes[v]:
                    if all(s in geradores or s.islower() for s in r):
                        geradores.add(v)
                        mudou = True
    acessiveis = set()
    fila = [inicial]
    while fila:
        atual = fila.pop()
        if atual not in acessiveis:
            acessiveis.add(atual)
            for r in producoes[atual]:
                for s in r:
                    if s.isupper():
                        fila.append(s)
    validos = geradores & acessiveis
    novas = defaultdict(list)
    for v in validos:
        novas[v] = [r for r in producoes[v] if all(s in validos or s.islower() for s in r)]
    return list(validos), novas

def converter_chomsky(variaveis, producoes):
    novas = defaultdict(list)
    novos_simbolos = {}
    contador = 1

    def nova_var(terminal):
        nonlocal contador
        if terminal not in novos_simbolos:
            nome = f"T{contador}"
            contador += 1
            novos_simbolos[terminal] = nome
            novas[nome].append([terminal])
        return novos_simbolos[terminal]

    for v in producoes:
        for r in producoes[v]:
            if len(r) == 1 and r[0].islower():
                novas[v].append([nova_var(r[0])])

            else:
                nova_regra = []
                for s in r:
                    if s.islower():
                        nova_regra.append(nova_var(s))
                    else:
                        nova_regra.append(s)
                while len(nova_regra) > 2:
                    x1, x2 = nova_regra[0], nova_regra[1]
                    nome = f"X{contador}"
                    contador += 1
                    novas[nome].append([x1, x2])
                    nova_regra = [nome] + nova_regra[2:]
                novas[v].append(nova_regra)
    return novas

def salvar_gramatica(caminho, inicial, producoes):
    with open(caminho, 'w') as f:
        f.write(" ".join(sorted(producoes.keys())) + "\n")
        f.write(inicial + "\n")
        for v in producoes:
            for r in producoes[v]:
                f.write(f"{v} {' '.join(r)}\n")

# ========== EXECUÇÃO ==========

entrada = "input.txt"
saida = "gramatica_fnc.txt"

variaveis, inicial, producoes = ler_gramatica(entrada)
producoes = remover_vazias(producoes)
producoes = remover_unitarias(producoes)
variaveis, producoes = remover_inuteis(variaveis, inicial, producoes)
# Salva versão limpa (sem vazias, unitárias, inúteis)
salvar_gramatica("gramatica_limpa.txt", inicial, producoes)

# Converte para Chomsky
producoes = converter_chomsky(variaveis, producoes)

# Salva versão final (Forma Normal de Chomsky)
salvar_gramatica(saida, inicial, producoes)


print("Gramática convertida para FNC e salva em:", saida)
