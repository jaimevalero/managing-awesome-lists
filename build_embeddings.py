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
    repos = []
    for filename in sorted(os.listdir(REPO_DIR)):
        if not filename.endswith(".json"):
            continue
        try:
            with open(os.path.join(REPO_DIR, filename), encoding="utf-8") as f:
                repo = json.load(f)
        except (ValueError, OSError):
            continue
        if repo.get("full_name"):
            repos.append(repo)
        if limit and len(repos) >= limit:
            break
    return repos


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

    from sentence_transformers import SentenceTransformer
    import torch

    repos = load_repos(args.limit)
    logger.info(f"{len(repos)} repos a vectorizar")

    textos = [build_text(r) for r in repos]
    con_readme = sum(1 for t, r in zip(textos, repos) if len(t) > 300)
    logger.info(f"{con_readme} ({100*con_readme//max(len(repos),1)}%) con texto abundante")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Cargando {MODEL_NAME} en {device}")
    model = SentenceTransformer(MODEL_NAME, device=device)

    vectors = model.encode(
        textos,
        batch_size=args.batch,
        normalize_embeddings=True,   # imprescindible: el cliente hace producto escalar
        show_progress_bar=True,
        convert_to_numpy=True,
    )

    bin_path, meta_path = write_index(repos, vectors)
    logger.info(
        f"{bin_path} ({os.path.getsize(bin_path)/1e6:.1f} MB) y "
        f"{meta_path} ({os.path.getsize(meta_path)/1e6:.1f} MB) escritos"
    )


if __name__ == "__main__":
    main()
