"""
Recalcula los repos parecidos por similitud de vectores, en vez de por topics
compartidos.

El metodo por topics se queda sin señal enseguida: la mitad de las paginas
tienen menos de 5 vecinos, el techo son 12, y 579 repos con mas de 5.000
estrellas se quedan en 2 o menos. facebook/react tiene 2 vecinos y
ggml-org/llama.cpp ninguno. Ademas confunde: apache/superset acaba emparejado
con apache/echarts y apache/logging-flume, que solo comparten el topic
"apache".

Con el coseno siempre hay un vecino numero 20, y el parecido sale de lo que el
repo hace (descripcion, topics y README) y no de que dos etiquetas coincidan.

Esto corre en torre y se materializa en los JSON que ya sirve el frontend: el
visitante no descarga nada nuevo, recibe el mismo fichero con mejores vecinos.

Uso:
    python build_similar.py --only facebook/react,duckdb/duckdb --dry-run
    python build_similar.py
"""
import argparse
import json
import os
import struct
from collections import Counter

import numpy as np
from loguru import logger

from build_embeddings import DIMS, FRONTEND_PUBLIC, load_repos

SIMILAR_DIR = "./var/similar"

# Cuantos vecinos como mucho. Veinte llenan la pagina y dan recorrido para
# saltar de vecino en vecino sin que el rastro se corte a los dos saltos.
TOP_K = 20

# Por debajo de esto no son parecidos, son relleno. Con el coseno siempre hay
# un vigesimo mejor candidato, y sin umbral acabariamos publicando paginas
# llenas de repos que no tienen nada que ver, que es peor que no tener pagina.
MIN_SIMILARITY = 0.62

# Bloques para no materializar la matriz entera: 23.473^2 en float32 son 2,2 GB.
BLOCK = 1024


def load_vectors():
    path = os.path.join(FRONTEND_PUBLIC, "embeddings.bin")
    with open(path, "rb") as f:
        raw = f.read()
    if raw[:4] != b"AWSM":
        raise SystemExit(f"{path} no tiene la cabecera esperada")
    version, count, dims = struct.unpack("<HII", raw[4:14])
    if dims != DIMS:
        raise SystemExit(f"el indice tiene {dims} dimensiones y se esperaban {DIMS}")
    vectors = np.frombuffer(raw[14:], dtype=np.int8).reshape(count, dims)
    # De int8 a float32 para operar; siguen normalizados, asi que el producto
    # escalar es directamente el coseno.
    return (vectors.astype(np.float32) / 127.0), count


def frequent_topics(repos):
    contador = Counter()
    for repo in repos:
        for topic in repo.get("topics") or []:
            contador[topic] += 1
    return dict(contador.most_common(5))


def slim(repo):
    """ Los campos que el frontend pinta, en el mismo orden que ya usaba. """
    return {
        "full_name": repo["full_name"],
        "description": repo.get("description") or "",
        "stargazers_count": repo.get("stargazers_count", 0),
        "language": repo.get("language"),
        "topics": repo.get("topics") or [],
        "created_at": repo.get("created_at"),
        "pushed_at": repo.get("pushed_at"),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", help="lista de repos separada por comas, para comparar")
    parser.add_argument("--dry-run", action="store_true", help="no escribe, solo muestra")
    parser.add_argument("--top-k", type=int, default=TOP_K)
    parser.add_argument("--min-similarity", type=float, default=MIN_SIMILARITY)
    args = parser.parse_args()

    repos = load_repos()
    vectors, count = load_vectors()
    if count != len(repos):
        raise SystemExit(
            f"el indice tiene {count} vectores y load_repos ve {len(repos)} repos: "
            "se han regenerado por separado y ya no estan alineados"
        )
    logger.info(f"{count} repos, {DIMS} dimensiones")

    indice_por_nombre = {r["full_name"]: i for i, r in enumerate(repos)}
    if args.only:
        pedidos = [n.strip() for n in args.only.split(",") if n.strip()]
        objetivo = []
        for nombre in pedidos:
            if nombre in indice_por_nombre:
                objetivo.append(indice_por_nombre[nombre])
            else:
                logger.warning(f"{nombre} no esta en el indice")
    else:
        objetivo = range(count)

    if not args.dry_run:
        os.makedirs(SIMILAR_DIR, exist_ok=True)

    objetivo = list(objetivo)
    escritos = sin_vecinos = 0
    for inicio in range(0, len(objetivo), BLOCK):
        bloque = objetivo[inicio:inicio + BLOCK]
        similitudes = vectors[bloque] @ vectors.T          # (len(bloque), count)
        # Un repo siempre es su propio vecino perfecto.
        for fila, idx in enumerate(bloque):
            similitudes[fila, idx] = -1.0

        for fila, idx in enumerate(bloque):
            puntuaciones = similitudes[fila]
            # argpartition evita ordenar los 23.473 para quedarnos con 20.
            candidatos = np.argpartition(-puntuaciones, args.top_k)[:args.top_k]
            candidatos = candidatos[np.argsort(-puntuaciones[candidatos])]
            vecinos = [(int(c), float(puntuaciones[c])) for c in candidatos
                       if puntuaciones[c] >= args.min_similarity]

            repo = repos[idx]
            if not vecinos:
                sin_vecinos += 1
                if args.dry_run:
                    print(f"\n=== {repo['full_name']} -> 0 vecinos por encima de {args.min_similarity}")
                continue

            vecinos_data = [slim(repos[i]) for i, _ in vecinos]
            if args.dry_run:
                print(f"\n=== {repo['full_name']}  ->  {len(vecinos_data)} vecinos")
                for (i, score), r in zip(vecinos, vecinos_data):
                    print(f"    {score:.3f}  {r['full_name']:40} {r['stargazers_count']:>7}  "
                          f"{(r['description'] or '')[:46]}")
                continue

            salida = {
                "category_type": "similar",
                "category_name": repo["full_name"],
                "repos_data": vecinos_data,
                "frecuent_topics": frequent_topics(vecinos_data),
                "repo_meta_data": slim(repo),
            }
            destino = os.path.join(SIMILAR_DIR, repo["full_name"].replace("/", "@") + ".json")
            with open(destino, "w", encoding="utf-8") as f:
                json.dump(salida, f, ensure_ascii=False)
            escritos += 1

        if not args.dry_run and inicio and inicio % (BLOCK * 5) == 0:
            logger.info(f"{inicio}/{len(objetivo)}")

    if not args.dry_run:
        logger.info(f"{escritos} paginas escritas, {sin_vecinos} repos sin vecinos claros")


if __name__ == "__main__":
    main()
