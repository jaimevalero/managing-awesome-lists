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
from sklearn.feature_extraction.text import TfidfVectorizer

from build_embeddings import DIMS, FRONTEND_PUBLIC, build_text, load_repos

SIMILAR_DIR = "./var/similar"

# Cuantos vecinos como mucho. Doce llenan la pagina y dan recorrido para saltar
# de vecino en vecino sin que el rastro se corte a los dos saltos. Con veinte,
# los ultimos puestos ya eran relleno y public/similar se iba a 203 MB.
TOP_K = 12

# Constante de la fusion por rangos (RRF). Amortigua las primeras posiciones,
# para que un metodo no se lleve la lista entera por un solo acierto.
RRF_K = 60

# Se combinan dos medidas de parecido porque fallan en sitios distintos, y
# medido contra las awesome lists la combinacion gana o empata siempre:
#
#   denso (bge-small)  entiende sinonimos, pero apenas separa: el vecino n1
#                      saca 0,810 de mediana y el n20 saca 0,742.
#   TF-IDF             pesa los terminos raros ("duckdb", "oozie"), que son
#                      los que identifican a un repo, y separa cinco veces
#                      mejor, pero no sabe que ETL y data pipeline son lo
#                      mismo.
#
# Los umbrales estan medidos, no elegidos a ojo: cada uno es el punto donde la
# mediana cae a unos doce vecinos, que es lo que se publica. El primero que
# puse (0,62 para el denso) dejaba pasar casi 5.000 repos por pagina.
MIN_DENSE = 0.75
MIN_TFIDF = 0.09

# Bloques para no materializar la matriz entera: 23.473^2 en float32 son 2,2 GB.
BLOCK = 1024

# Se miran mas candidatos de los que se publican, porque al descartar copias
# del mismo repo hay que poder rellenar el hueco con el siguiente.
CANDIDATE_FACTOR = 4


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


def identidad(repo):
    """
    Que hace unico a un repo, sobreviviendo a los cambios de dueño.

    RepoModel ya lo explica: full_name no identifica, porque cuando un repo se
    traspasa github lo sigue sirviendo con los dos nombres y acaba cacheado dos
    veces. La fecha de creacion si sobrevive al traspaso, al segundo.

    Con vectores esto se nota mucho mas que antes: las dos copias tienen el
    mismo README, sacan 0,99 y se plantan en los primeros puestos. Le pasaba a
    apache/airflow con airbnb/airflow y a ggml-org/llama.cpp con
    ggerganov/llama.cpp.
    """
    return repo.get("created_at") or repo["full_name"]


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
    parser.add_argument("--min-dense", type=float, default=MIN_DENSE)
    parser.add_argument("--min-tfidf", type=float, default=MIN_TFIDF)
    args = parser.parse_args()

    repos = load_repos()
    vectors, count = load_vectors()
    logger.info("construyendo TF-IDF sobre el mismo texto que se vectorizo")
    # min_df=2 tira lo que sale en un solo repo (erratas, nombres propios) y
    # max_df=0.4 lo que sale en casi todos ("library", "open source"), que no
    # distingue nada. Bigramas para que "time series" cuente como una cosa.
    tfidf = TfidfVectorizer(sublinear_tf=True, min_df=2, max_df=0.4,
                            stop_words="english", ngram_range=(1, 2),
                            max_features=300_000)
    disperso = tfidf.fit_transform(build_text(r) for r in repos)
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
    pool = args.top_k * CANDIDATE_FACTOR

    def mejores(puntuaciones, idx, minimo):
        """ Los mejores candidatos de una medida, ya ordenados y filtrados. """
        puntuaciones[idx] = -1.0
        cuantos = min(pool, len(puntuaciones) - 1)
        top = np.argpartition(-puntuaciones, cuantos)[:cuantos]
        top = top[np.argsort(-puntuaciones[top])]
        return [int(c) for c in top if puntuaciones[c] >= minimo]

    for inicio in range(0, len(objetivo), BLOCK):
        bloque = objetivo[inicio:inicio + BLOCK]
        sim_densa = vectors[bloque] @ vectors.T
        sim_dispersa = (disperso[bloque] @ disperso.T).toarray()

        for fila, idx in enumerate(bloque):
            repo = repos[idx]
            ranking_denso = mejores(sim_densa[fila], idx, args.min_dense)
            ranking_tfidf = mejores(sim_dispersa[fila], idx, args.min_tfidf)

            # Fusion por rangos: las puntuaciones de las dos medidas no son
            # comparables (el denso vive en 0,8 y TF-IDF en 0,1), asi que
            # sumarlas la decidiria el denso por escala y no por acierto. La
            # posicion si significa lo mismo en las dos listas.
            puntos = {}
            for lista in (ranking_denso, ranking_tfidf):
                for posicion, candidato in enumerate(lista):
                    puntos[candidato] = puntos.get(candidato, 0.0) + 1.0 / (RRF_K + posicion + 1)

            vecinos = []
            vistas = {identidad(repo)}   # el propio repo, con cualquiera de sus nombres
            for c in sorted(puntos, key=lambda k: -puntos[k]):
                quien = identidad(repos[c])
                if quien in vistas:
                    continue
                vistas.add(quien)
                vecinos.append((c, puntos[c]))
                if len(vecinos) >= args.top_k:
                    break
            if not vecinos:
                sin_vecinos += 1
                if args.dry_run:
                    print(f"\n=== {repo['full_name']} -> 0 vecinos por encima de los umbrales")
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
