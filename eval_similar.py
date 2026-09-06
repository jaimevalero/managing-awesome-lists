"""
Compara la calidad de los vecinos con un juez externo a los tres metodos:
las awesome lists, que las cura una persona.

La trampa evidente es que no todas valen igual. Compartir awesome-mcp-servers
(3.326 repos) o awesome-go (2.786) no significa parecerse, igual que compartir
el topic "apache" no emparentaba a superset con logging-flume. Compartir una
lista de treinta si dice algo.

Asi que cada lista pesa segun lo especifica que sea, 1/log2(2+tamaño), y de
paso se repite la cuenta usando solo las listas por debajo de 150 repos, que
son 45 de las 80. Si los dos numeros ordenan igual los metodos, la conclusion
no depende de como se haya elegido el peso.
"""
import json
import math
import os
import random
import struct
import sys

import numpy as np
from loguru import logger
from sklearn.feature_extraction.text import TfidfVectorizer

from build_embeddings import DIMS, FRONTEND_PUBLIC, build_text, load_repos

AWESOME_DIR = os.path.expanduser("~/git/managing-awesome-lists-frontend/public/awesome")
LISTA_PEQUENA = 150
TOP_K = 10
POOL = 60
RRF_K = 60
MUESTRA = 500


def cargar_listas():
    """ repo -> {lista: peso} y el conjunto de listas pequeñas. """
    pertenece, tamanos = {}, {}
    for f in os.listdir(AWESOME_DIR):
        if not f.endswith(".json"):
            continue
        try:
            d = json.load(open(os.path.join(AWESOME_DIR, f), encoding="utf-8"))
        except Exception:
            continue
        nombre = f[:-5]
        repos = d.get("repos_data") or []
        tamanos[nombre] = len(repos)
        for r in repos:
            pertenece.setdefault(r["full_name"], set()).add(nombre)
    pesos = {n: 1.0 / math.log2(2 + t) for n, t in tamanos.items()}
    pequenas = {n for n, t in tamanos.items() if 0 < t < LISTA_PEQUENA}
    return pertenece, pesos, pequenas


def evaluar(vecinos_por_repo, pertenece, pesos, pequenas):
    ponderada, binaria, evaluados = [], [], 0
    for nombre, vecinos in vecinos_por_repo.items():
        mias = pertenece.get(nombre)
        if not mias:
            continue
        evaluados += 1
        p = b = 0.0
        for v in vecinos:
            suyas = pertenece.get(v, set())
            comunes = mias & suyas
            p += sum(pesos[c] for c in comunes)
            b += 1.0 if (comunes & pequenas) else 0.0
        ponderada.append(p / max(len(vecinos), 1))
        binaria.append(b / max(len(vecinos), 1))
    return (sum(ponderada) / len(ponderada), sum(binaria) / len(binaria), evaluados)


def main():
    repos = load_repos()
    nombres = [r["full_name"] for r in repos]
    textos = [build_text(r) for r in repos]

    with open(os.path.join(FRONTEND_PUBLIC, "embeddings.bin"), "rb") as f:
        raw = f.read()
    _, count, _ = struct.unpack("<HII", raw[4:14])
    denso = np.frombuffer(raw[14:], dtype=np.int8).reshape(count, DIMS).astype(np.float32) / 127.0

    tfidf = TfidfVectorizer(sublinear_tf=True, min_df=2, max_df=0.4,
                            stop_words="english", ngram_range=(1, 2), max_features=300_000)
    disperso = tfidf.fit_transform(textos)
    logger.info(f"{len(repos)} repos, {disperso.shape[1]} terminos")

    pertenece, pesos, pequenas = cargar_listas()
    logger.info(f"{len(pertenece)} repos en alguna lista, {len(pequenas)} listas pequeñas")

    random.seed(42)
    # Solo repos que estan en alguna lista: los demas no se pueden juzgar.
    candidatos = [i for i, n in enumerate(nombres) if n in pertenece]
    muestra = random.sample(candidatos, min(MUESTRA, len(candidatos)))
    logger.info(f"muestra: {len(muestra)} repos")

    resultados = {m: {} for m in ("TF-IDF", "DENSO", "HIBRIDO")}
    for i in muestra:
        s_tfidf = (disperso @ disperso[i].T).toarray().ravel(); s_tfidf[i] = -1
        s_denso = denso @ denso[i]; s_denso[i] = -1

        rank = {}
        for clave, s in (("TF-IDF", s_tfidf), ("DENSO", s_denso)):
            top = np.argpartition(-s, POOL)[:POOL]
            rank[clave] = list(top[np.argsort(-s[top])])
            resultados[clave][nombres[i]] = [nombres[j] for j in rank[clave][:TOP_K]]

        puntos = {}
        for lista in rank.values():
            for pos, idx in enumerate(lista):
                puntos[idx] = puntos.get(idx, 0.0) + 1.0 / (RRF_K + pos + 1)
        fusion = sorted(puntos, key=lambda k: -puntos[k])[:TOP_K]
        resultados["HIBRIDO"][nombres[i]] = [nombres[j] for j in fusion]

    print(f"\n{'metodo':10} {'ponderada':>11} {'listas <150':>13}   (mayor es mejor)")
    for metodo, vecinos in resultados.items():
        pond, bina, n = evaluar(vecinos, pertenece, pesos, pequenas)
        print(f"{metodo:10} {pond:>11.4f} {bina:>13.3f}   sobre {n} repos")


if __name__ == "__main__":
    main()
