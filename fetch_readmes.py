"""
Descarga y cachea el README de cada repo conocido, para tener texto de verdad
que indexar. La descripcion de GitHub se queda en 74 caracteres de media y uno
de cada cinco repos la tiene practicamente vacia; el README multiplica por ~25
el texto disponible.

Estrategia en dos fases, para no malgastar el rate limit de la API:

  Fase 1 (raw.githubusercontent.com): resuelve la gran mayoria en 1-2 peticiones
    y NO consume el rate limit de la API REST, asi que se puede paralelizar.
  Fase 2 (API /repos/{owner}/{repo}/readme): solo para los que fallan en la
    fase 1. Una peticion resuelve cualquier nombre, extension y rama por
    defecto (README.rst, .github/README.md, rama develop...), cosas que la
    fase 1 no cubre. Aqui si cuenta el rate limit, asi que va serializado.

Es incremental: solo se vuelve a bajar un README si el repo tiene un pushed_at
mas reciente que el de la ultima descarga. Los fallos permanentes (repos
borrados, sin README) se recuerdan para no reintentarlos cada mes.

Uso:
    python fetch_readmes.py            # incremental
    python fetch_readmes.py --limit 50 # prueba corta
    python fetch_readmes.py --force    # ignora el cache y baja todo
"""
import argparse
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from http import HTTPStatus
from itertools import product

import requests
from dotenv import load_dotenv
from loguru import logger

REPO_DIR = "./var/repo"
CATEGORY_DIRS = ["./var/topic", "./var/awesome", "./var/similar"]
README_DIR = "./var/readme"
STATE_FILE = "./var/readme-state.json"

# Con guardar el principio sobra: la señal esta al principio y luego vienen
# instalacion, licencia y changelog. 12k deja margen para que la limpieza de
# markdown (que se come ~47%) pueda sacar sus ~1.800 caracteres utiles.
MAX_README_CHARS = 12000

# raw aguanta bien la concurrencia; la API no se paraleliza (rate limit).
RAW_WORKERS = 16
HTTP_TIMEOUT = 20

RAW_CANDIDATES = list(product(["main", "master"], ["README.md", "readme.md"]))


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False)


def readme_path(full_name):
    return os.path.join(README_DIR, full_name.replace("/", "@") + ".md")


def iter_known_repos():
    """
    (full_name, pushed_at) de cada repo conocido.

    var/repo son fichas sueltas por repo, pero renew.sh lo vacia al empezar el
    ciclo mensual, asi que ahi no siempre hay nada. Las categorias
    (var/topic, var/awesome, var/similar) llevan los mismos campos dentro de
    repos_data y sobreviven al borrado, asi que valen de respaldo: leyendo
    ambas cosas esto funciona en cualquier punto del ciclo.

    Un repo sale en varias categorias; nos quedamos con el pushed_at mas
    reciente, que es el que decide si hay que volver a bajar el README.
    """
    vistos = {}

    if os.path.isdir(REPO_DIR):
        for filename in os.listdir(REPO_DIR):
            if not filename.endswith(".json"):
                continue
            try:
                with open(os.path.join(REPO_DIR, filename), encoding="utf-8") as f:
                    repo = json.load(f)
            except (ValueError, OSError):
                continue
            if repo.get("full_name"):
                nombre = repo["full_name"]
                pushed = repo.get("pushed_at", "")
                vistos[nombre] = max(vistos.get(nombre, ""), pushed)

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
                nombre = repo.get("full_name")
                if nombre:
                    pushed = repo.get("pushed_at", "")
                    vistos[nombre] = max(vistos.get(nombre, ""), pushed)

    for nombre in sorted(vistos):
        yield nombre, vistos[nombre]


def needs_download(full_name, pushed_at, state, force):
    if force:
        return True
    entry = state.get(full_name)
    if not entry:
        return True
    # Un repo sin README sigue sin tenerlo salvo que lo hayan tocado.
    if entry.get("pushed_at") == pushed_at:
        return False
    return True


def store(full_name, text):
    with open(readme_path(full_name), "w", encoding="utf-8") as f:
        f.write(text[:MAX_README_CHARS])


def fetch_raw(session, full_name):
    """Fase 1. Devuelve el texto, o None si ninguna combinacion existe."""
    for branch, name in RAW_CANDIDATES:
        url = f"https://raw.githubusercontent.com/{full_name}/{branch}/{name}"
        try:
            response = session.get(url, timeout=HTTP_TIMEOUT)
        except requests.RequestException:
            continue
        if response.status_code == HTTPStatus.OK:
            return response.text
    return None


def fetch_api(session, full_name, access_token):
    """Fase 2. Resuelve nombre, extension y rama por defecto de una vez."""
    url = f"https://api.github.com/repos/{full_name}/readme"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.raw",
    }
    for attempt in range(3):
        try:
            response = session.get(url, headers=headers, timeout=HTTP_TIMEOUT)
        except requests.RequestException:
            time.sleep(2 * (attempt + 1))
            continue

        if response.status_code == HTTPStatus.OK:
            return response.text, "ok"
        # 404 sin README, 451 retirado por DMCA: no insistir nunca mas.
        if response.status_code in (HTTPStatus.NOT_FOUND, 451):
            return None, "missing"
        if response.status_code == HTTPStatus.FORBIDDEN:
            reset = int(response.headers.get("X-RateLimit-Reset", 0))
            espera = max(reset - int(time.time()), 0) + 5
            if espera > 1:
                logger.warning(f"Rate limit alcanzado, esperando {espera}s")
                time.sleep(min(espera, 3600))
                continue
        time.sleep(2 * (attempt + 1))
    return None, "error"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="procesa solo N repos")
    parser.add_argument("--force", action="store_true", help="ignora el cache")
    args = parser.parse_args()

    load_dotenv()
    access_token = os.getenv("CREDENTIALS")
    if not access_token:
        raise SystemExit("Falta CREDENTIALS en .env")

    os.makedirs(README_DIR, exist_ok=True)
    state = load_state()

    repos = list(iter_known_repos())
    pendientes = [(n, p) for n, p in repos if needs_download(n, p, state, args.force)]
    if args.limit:
        pendientes = pendientes[: args.limit]

    logger.info(f"{len(repos)} repos conocidos, {len(pendientes)} por descargar")
    if not pendientes:
        return

    pushed_by_name = dict(pendientes)
    inicio = time.time()

    # --- Fase 1: raw en paralelo -------------------------------------------
    fallidos = []
    ok_raw = 0
    with requests.Session() as session:
        with ThreadPoolExecutor(max_workers=RAW_WORKERS) as pool:
            futuros = {
                pool.submit(fetch_raw, session, nombre): nombre
                for nombre, _ in pendientes
            }
            for hechos, futuro in enumerate(as_completed(futuros), 1):
                nombre = futuros[futuro]
                texto = futuro.result()
                if texto:
                    store(nombre, texto)
                    state[nombre] = {"pushed_at": pushed_by_name[nombre], "status": "ok"}
                    ok_raw += 1
                else:
                    fallidos.append(nombre)
                if hechos % 500 == 0:
                    logger.info(f"raw: {hechos}/{len(futuros)} ({ok_raw} ok)")

    logger.info(f"Fase 1: {ok_raw} ok, {len(fallidos)} a resolver por API")

    # --- Fase 2: API, serializada por el rate limit -------------------------
    ok_api = sin_readme = errores = 0
    with requests.Session() as session:
        for hechos, nombre in enumerate(fallidos, 1):
            texto, estado = fetch_api(session, nombre, access_token)
            if estado == "ok":
                store(nombre, texto)
                ok_api += 1
            elif estado == "missing":
                sin_readme += 1
            else:
                errores += 1
            # Un error de red no se cachea: se reintenta el mes que viene.
            if estado in ("ok", "missing"):
                state[nombre] = {"pushed_at": pushed_by_name[nombre], "status": estado}
            if hechos % 200 == 0:
                logger.info(f"api: {hechos}/{len(fallidos)}")
                save_state(state)

    save_state(state)
    logger.info(
        f"Hecho en {time.time() - inicio:.0f}s | "
        f"raw {ok_raw} + api {ok_api} = {ok_raw + ok_api} READMEs, "
        f"{sin_readme} sin README, {errores} con error (se reintentan)"
    )


if __name__ == "__main__":
    main()
