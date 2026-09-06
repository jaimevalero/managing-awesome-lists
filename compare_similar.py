"""
Compara como salen los repos parecidos con TF-IDF y con los vectores densos.

La duda es razonable: los vectores densos apenas separan (el vecino n1 saca
0,810 de mediana y el n20 saca 0,742, siete centesimas de rango), que es lo
que hace inutil cualquier umbral. TF-IDF pesa los terminos raros ("duckdb",
"oozie", "wasm"), que son justo los que identifican a un repo, y da un rango
mucho mas ancho. A cambio no entiende sinonimos.

Usa el mismo texto que se vectorizo, para que la comparacion sea justa.

Uso:
    python compare_similar.py --only duckdb/duckdb,facebook/react
"""
import argparse
import os
import struct

import numpy as np
from loguru import logger
from sklearn.feature_extraction.text import TfidfVectorizer

from build_embeddings import DIMS, FRONTEND_PUBLIC, build_text, load_repos

TOP_K = 10

# Cuantos candidatos aporta cada metodo a la fusion.
POOL = 60

# Constante de la fusion por rangos (RRF). Amortigua las primeras posiciones:
# con k=60, ser primero vale 1/61 y ser decimo 1/70, no diez veces menos. Evita
# que un metodo se lleve la lista entera por un solo acierto muy puntuado.
RRF_K = 60


def cargar_densos():
    with open(os.path.join(FRONTEND_PUBLIC, "embeddings.bin"), "rb") as f:
        raw = f.read()
    _, count, dims = struct.unpack("<HII", raw[4:14])
    return np.frombuffer(raw[14:], dtype=np.int8).reshape(count, dims).astype(np.float32) / 127.0


def fusionar(rank_a, rank_b):
    """
    Fusion por rangos (Reciprocal Rank Fusion).

    No se pueden sumar las puntuaciones de los dos metodos: TF-IDF se mueve
    entre 0,38 y 0,07 y el denso entre 0,86 y 0,80, asi que cualquier suma la
    domina el denso por pura escala. Lo que si es comparable es la posicion:
    ser el tercero de una lista significa lo mismo en las dos.

    Un repo que sale bien colocado en ambas sube; uno que solo aparece en una
    se queda a medio camino, que es justo lo que se busca al combinar un
    metodo que entiende sinonimos con otro que pesa terminos raros.
    """
    puntos = {}
    for lista in (rank_a, rank_b):
        for posicion, idx in enumerate(lista):
            puntos[idx] = puntos.get(idx, 0.0) + 1.0 / (RRF_K + posicion + 1)
    return sorted(puntos.items(), key=lambda kv: -kv[1])


def mostrar(titulo, repos, pares):
    print(f"\n  {titulo}")
    if not pares:
        print("      (ninguno)")
        return
    for idx, score in pares:
        r = repos[idx]
        print(f"      {score:.3f}  {r['full_name']:38} {r.get('stargazers_count',0):>7}  "
              f"{(r.get('description') or '')[:44]}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", required=True)
    parser.add_argument("--top-k", type=int, default=TOP_K)
    args = parser.parse_args()

    repos = load_repos()
    textos = [build_text(r) for r in repos]
    logger.info(f"{len(repos)} repos")

    # min_df=2 tira los terminos que salen en un solo repo (erratas, nombres
    # propios) y max_df=0.4 los que salen en casi todos ("library", "python"),
    # que no distinguen nada. Bigramas para que "machine learning" o "time
    # series" cuenten como una cosa.
    tfidf = TfidfVectorizer(
        sublinear_tf=True, min_df=2, max_df=0.4,
        stop_words="english", ngram_range=(1, 2), max_features=300_000,
    )
    disperso = tfidf.fit_transform(textos)   # ya normalizado L2
    logger.info(f"TF-IDF: {disperso.shape[1]} terminos, "
                f"{disperso.nnz / disperso.shape[0]:.0f} por repo")

    denso = cargar_densos()
    indice = {r["full_name"]: i for i, r in enumerate(repos)}

    for nombre in [n.strip() for n in args.only.split(",") if n.strip()]:
        if nombre not in indice:
            logger.warning(f"{nombre} no esta")
            continue
        i = indice[nombre]
        print(f"\n{'='*72}\n{nombre}")

        rankings = {}
        for titulo, puntuaciones in (
            ("TF-IDF", (disperso @ disperso[i].T).toarray().ravel()),
            ("DENSO (bge-small)", denso @ denso[i]),
        ):
            puntuaciones[i] = -1
            top = np.argpartition(-puntuaciones, POOL)[:POOL]
            top = top[np.argsort(-puntuaciones[top])]
            rankings[titulo] = list(top)
            mostrar(titulo, repos, [(int(c), float(puntuaciones[c])) for c in top[:args.top_k]])

        fusion = fusionar(rankings["TF-IDF"], rankings["DENSO (bge-small)"])
        mostrar("HIBRIDO (fusion por rangos)", repos, fusion[:args.top_k])


if __name__ == "__main__":
    main()
