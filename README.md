# Cine T7 — la cinemateca de Edu

[Abrir la web](https://eduardoddddddd.github.io/cine-t7-catalogo/) · [Añadir una película desde el móvil](https://github.com/eduardoddddddd/cine-t7-catalogo/issues/new?template=add_movie.yml)

Catálogo personal con portadas, fichas, búsqueda por título/director/reparto, filtros, lista personal y modo sala. El diseño se conserva de la presentación original. La colección inicial contiene 194 películas y 17 series procedentes del inventario de T7 del 9 de octubre de 2026.

Este repo es independiente del anterior `cine-t7`. La web es pública y los vídeos permanecen en el disco.

Actualización del 12 de octubre de 2026: 206 películas, 17 series y 465 archivos medidos. Se incorporaron 12 películas comprobadas en `pelis2` y «No hay salida» (1987, Kevin Costner), cuya copia estaba pendiente de comprobación. Se retiró `Thunderbolts*` y la copia de Nosferatu de 4,62 GB; se conserva la versión de 2024 de 3,07 GB. El campo `scanned` conserva la fecha del inventario completo inicial; cada ficha registra su comprobación posterior en `inventory.recordedAt`.

## Añadir películas sin conectar el disco

**Desde el móvil:** abre «Añadir película desde el móvil», entra con la cuenta propietaria, indica título, año y ubicación y crea la solicitud. GitHub Actions incorpora el título y publica de nuevo. Puedes completar después la portada y la ficha con un LLM. Solicitudes de otras cuentas no se ejecutan automáticamente.

**Con cualquier LLM:** pásale la URL de este repo y una petición como:

> Lee AGENTS.md. Añade «el título», del año indicado, a mi colección en T7. Verifica la ficha y la portada, conserva los registros existentes, pasa las comprobaciones y publica el cambio.

El LLM necesita permiso para modificar el repo. Leer un repo público no concede permiso de escritura ni activa un modelo automáticamente.

**A mano o por terminal:** Python 3.10+ sin dependencias. Node se utiliza para la comprobación sintáctica de JavaScript.

```sh
git clone https://github.com/eduardoddddddd/cine-t7-catalogo.git
cd cine-t7-catalogo
python scripts/catalog.py add --title "Título de la película" --year 2026 --location "DVD"
python scripts/catalog.py validate
python -m unittest discover -s tests -v
node --check web/app.js
python scripts/catalog.py build
git add data/catalog.json
git commit -m "Añadir película a la colección"
git pull --rebase
git push
```

Los datos desconocidos se quedan sin dato. `files: []` permite incorporar una película sin inventar características del archivo. La web muestra la ubicación indicada y que aún no hay un archivo escaneado.

## Portadas y fichas de TMDB

Con una clave de TMDB en una variable de entorno local puedes buscar y seleccionar la película exacta:

```sh
python scripts/catalog.py search --title "Título" --year 2026
python scripts/catalog.py add --title "Título" --tmdb-id ID_VERIFICADO --location "T7"
python scripts/catalog.py update --id ID_EXISTENTE --tmdb-id ID_VERIFICADO
```

Variables admitidas: `TMDB_API_KEY` o `TMDB_ACCESS_TOKEN`. Nunca se envía una clave al navegador. No hace falta una clave para añadir títulos básicos ni publicar. Los LLM también pueden rellenar metadatos contrastados mediante `--metadata-file` o editar `data/catalog.json`; consulta [el formato](docs/FORMATO.md).

## Actualizar mediciones del disco

Un escaneo local puede exportar un JSON con `items` en el formato del catálogo original. Incorpóralo con:

```sh
python scripts/catalog.py import --file private/inventario.json
```

La importación conserva títulos manuales, IDs y metadatos existentes cuando identifica un título ya conocido. Actualiza las mediciones del escaneo y sanitiza rutas y nombres de vídeo. Si incorpora nuevos títulos con portadas locales, copia también las imágenes referenciadas a `web/assets/` y ejecuta `validate`.

## Estructura

- `data/catalog.json`: catálogo editable y fuente única.
- `web/`: HTML, CSS, JavaScript e imágenes.
- `scripts/catalog.py`: añadir, actualizar, importar, validar y generar la web.
- `AGENTS.md`: procedimiento para agentes y LLM.
- `.github/workflows/`: publicación y solicitudes del propietario.
- `tests/`: comprobaciones de duplicados, datos manuales, importación y privacidad.
- `dist/`: web generada, ignorada en Git.

## Vista local y publicación

```sh
python scripts/catalog.py build
python -m http.server 8766 --bind 127.0.0.1 --directory dist
```

Abre http://127.0.0.1:8766. GitHub Pages publica `dist/` mediante Actions cada vez que cambia `main`. La incorporación mediante solicitud lanza ese mismo workflow explícitamente, porque los commits hechos con `GITHUB_TOKEN` no disparan otro workflow de push automáticamente.

La lista de favoritos se guarda en cada navegador. La web permite consultar el catálogo; no reproduce los vídeos. Las portadas iniciales están empaquetadas con la web; algunas imágenes de fondo y futuras portadas pueden utilizar HTTPS externo.

## Datos y atribución

Las mediciones iniciales proceden de cabeceras multimedia, no de una reproducción completa de los vídeos. Las incorporaciones manuales se registran separadamente. Fichas e imágenes de TMDB: este producto utiliza su API pero TMDB no lo avala ni certifica. Las carátulas y fichas conservan los derechos de sus respectivos titulares.
