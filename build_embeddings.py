"""
Vectoriza cada repo (descripcion + topics + lenguaje + README limpio) y deja en
el frontend un indice que el navegador pueda buscar entero, sin backend.

Con 13.465 repos la fuerza bruta es la respuesta correcta: un producto escalar
contra todo el indice son ~5M multiplicaciones, menos de 10ms en JS. Un indice
aproximado (HNSW y companiia) solo empieza a compensar sobre el millon de
vectores, y aqui solo añadiria peso y error.

El modelo lo manda el navegador, no la GPU: el que vectoriza aqui tiene que ser
exactamente el mismo que vectoriza la consulta en el cliente, o los vectores no
viven en el mismo espacio. Por eso bge-small (33M parametros, 384 dims, 512
tokens): ~30 MB en Transformers.js y encaja con los ~460 tokens de README
limpio que sale de media.

Se vectoriza con fastembed, que corre sobre ONNX Runtime, y no con torch. Pesa
60 MB en vez de 5 GB de CUDA, y sobre todo es el mismo runtime que usa
Transformers.js en el navegador: mismo grafo a los dos lados, en vez de
PyTorch aqui y ONNX alli. En CPU son unos 5 minutos para 23.000 textos, de
sobra para un proceso mensual.

Salida en public/ del frontend:
    embeddings.bin        int8, N x 384, normalizado  (~5 MB)
    embeddings-meta.json  full_name y datos para pintar resultados

Uso:
    python build_embeddings.py                 # todo, en GPU si la hay
    python build_embeddings.py --limit 200     # prueba corta
"""
import argparse
import json
import os
import re
import struct

import numpy as np
from loguru import logger

REPO_DIR = "./var/repo"
CATEGORY_DIRS = ["./var/topic", "./var/awesome", "./var/similar"]
README_DIR = "./var/readme"
FRONTEND_PUBLIC = os.path.expanduser("~/git/managing-awesome-lists-frontend/public")

MODEL_NAME = "BAAI/bge-small-en-v1.5"
DIMS = 384

# El README limpio da ~1.850 caracteres de media (~460 tokens), justo por
# debajo de los 512 que acepta el modelo. Pasarse solo sirve para que trunque.
MAX_TEXT_CHARS = 1800


def clean_markdown(text):
    """
    Quita lo que es identico en todos los README (badges, bloques de codigo,
    HTML, indices). No es cosmetica: ese ruido esta correlacionado entre repos,
    asi que mete un componente comun en todos los vectores y aplasta el
    contraste justo donde queremos distinguir. Se come ~47% del texto.
    """
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)       # imagenes y badges
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)     # enlaces -> texto
    text = re.sub(r"[#>`*_|=~-]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def readme_for(full_name):
    path = os.path.join(README_DIR, full_name.replace("/", "@") + ".md")
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8", errors="ignore") as f:
        return clean_markdown(f.read())


def build_text(repo):
    """
    El orden importa: lo mas denso primero, porque si hay que truncar se pierde
    la cola. Nombre y topics son vocabulario controlado y casi siempre caben.
    """
    partes = [
        repo["full_name"].replace("/", " ").replace("-", " "),
        repo.get("language") or "",
        " ".join(repo.get("topics") or []),
        (repo.get("description") or "").strip(),
        readme_for(repo["full_name"]),
    ]
    return " ".join(p for p in partes if p)[:MAX_TEXT_CHARS]


def load_repos(limit=None):
    """
    Los repos conocidos, vengan de donde vengan.

    var/repo son fichas sueltas, pero renew.sh lo vacia al empezar el ciclo, asi
    que ahi no siempre hay nada. Las categorias llevan los mismos campos dentro
    de repos_data y sobreviven al borrado. Mismo criterio que fetch_readmes.py,
    para que ambos vean exactamente la misma lista de repos: si uno viera mas
    que el otro, habria vectores sin README o README sin vector.

    Un repo sale en varias categorias; gana la copia con el pushed_at mas
    reciente, que es la que trae las estrellas mas frescas.
    """
    vistos = {}

    def considerar(repo):
        nombre = repo.get("full_name")
        if not nombre:
            return
        previo = vistos.get(nombre)
        if previo is None or (repo.get("pushed_at") or "") > (previo.get("pushed_at") or ""):
            vistos[nombre] = repo

    if os.path.isdir(REPO_DIR):
        for filename in os.listdir(REPO_DIR):
            if not filename.endswith(".json"):
                continue
            try:
                with open(os.path.join(REPO_DIR, filename), encoding="utf-8") as f:
                    considerar(json.load(f))
            except (ValueError, OSError):
                continue

    for categoria in CATEGORY_DIRS:
        if not os.path.isdir(categoria):
            continue
        for filename in os.listdir(categoria):
            if not filename.endswith(".json"):
                continue
            try:
                with open(os.path.join(categoria, filename), encoding="utf-8") as f:
                    data = json.load(f)
            except (ValueError, OSError):
                continue
            for repo in data.get("repos_data") or []:
                considerar(repo)

    # Orden estable: el indice i del binario tiene que ser siempre el repo i
    # del meta, y ambos se regeneran juntos cada mes.
    repos = [vistos[nombre] for nombre in sorted(vistos)]
    return repos[:limit] if limit else repos


def quantize(vectors):
    """
    Vectores normalizados L2 -> componentes en [-1, 1] -> int8 escalando por 127.
    Cuarta parte del tamaño y el error del coseno se queda en ~0,3%, que no
    mueve un ranking. 384 dims x int8 = 384 bytes por repo.
    """
    return np.clip(np.rint(vectors * 127.0), -127, 127).astype(np.int8)


def write_index(repos, vectors):
    os.makedirs(FRONTEND_PUBLIC, exist_ok=True)
    quantized = quantize(vectors)

    # Cabecera para que el cliente valide que lee lo que cree: "AWSM", version,
    # numero de vectores y dimensiones.
    bin_path = os.path.join(FRONTEND_PUBLIC, "embeddings.bin")
    with open(bin_path, "wb") as f:
        f.write(b"AWSM")
        f.write(struct.pack("<HII", 1, len(repos), DIMS))
        f.write(quantized.tobytes())

    meta_path = os.path.join(FRONTEND_PUBLIC, "embeddings-meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "model": MODEL_NAME,
                "dims": DIMS,
                "count": len(repos),
                # Mismo orden que los vectores: el indice i del binario es
                # el repo i de esta lista.
                "repos": [
                    {
                        "n": r["full_name"],
                        "d": (r.get("description") or "")[:200],
                        "s": r.get("stargazers_count", 0),
                        "l": r.get("language") or "",
                    }
                    for r in repos
                ],
            },
            f,
            ensure_ascii=False,
            separators=(",", ":"),
        )
    return bin_path, meta_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="procesa solo N repos")
    parser.add_argument("--batch", type=int, default=256)
    args = parser.parse_args()

    from fastembed import TextEmbedding

    repos = load_repos(args.limit)
    logger.info(f"{len(repos)} repos a vectorizar")

    textos = [build_text(r) for r in repos]
    con_readme = sum(1 for t, r in zip(textos, repos) if len(t) > 300)
    logger.info(f"{con_readme} ({100*con_readme//max(len(repos),1)}%) con texto abundante")

    logger.info(f"Cargando {MODEL_NAME} (onnxruntime)")
    model = TextEmbedding(MODEL_NAME)

    # bge-small ya devuelve los vectores normalizados a norma 1, que es lo que
    # necesita el cliente para resolver el coseno con un producto escalar.
    vectors = np.array(list(model.embed(textos, batch_size=args.batch)), dtype=np.float32)

    normas = np.linalg.norm(vectors, axis=1)
    if not np.allclose(normas, 1.0, atol=1e-3):
        raise SystemExit(f"vectores sin normalizar (norma media {normas.mean():.4f})")

    bin_path, meta_path = write_index(repos, vectors)
    logger.info(
        f"{bin_path} ({os.path.getsize(bin_path)/1e6:.1f} MB) y "
        f"{meta_path} ({os.path.getsize(meta_path)/1e6:.1f} MB) escritos"
    )


if __name__ == "__main__":
    main()
