# Formato del catálogo

La raíz contiene `schemaVersion: 1`, `updated`, `scanned` (fecha del último inventario, si existe), `volume` y `items`.

Cada título tiene:

| Campo | Significado |
|---|---|
| `id` | Identificador estable y único; no cambiar al actualizar. |
| `title`, `year`, `type` | Título, año conocido como cadena o null, y `movies` / `series`. |
| `inventory.source` | `scan` para mediciones o `manual` por indicación del propietario. |
| `inventory.location` | T7, DVD, Blu-ray u otra ubicación indicada; no una ruta privada. |
| `inventory.recordedAt`, `note` | Fecha de incorporación y comentario opcional. |
| `files` | Copias o capítulos escaneados. Vacío para una incorporación manual. |
| `bytes` | Tamaño total medido o null si no se ha medido. |
| `meta` | Ficha documental contrastada o datos básicos pendientes. |

`meta` admite `matched`, `tmdb`, `imdb`, `title`, `original`, `year`, `synopsis`, `genres`, `runtime`, `rating`, `votes`, `tagline`, `country`, `director`, `cast`, `poster`, `backdrop`, `source`, `trailer` y `checkedAt`.

`runtime` es la duración de la ficha cinematográfica en minutos. `files[].technical.seconds` es una duración real de archivo, en segundos. No confundir ambas. Para una ficha pendiente, usa `matched: false` y listas vacías. No inventes puntuaciones, reparto ni sinopsis.

Cada archivo público contiene un nombre genérico (`Copia 1` o temporada/capítulo), tamaño medido, temporada/episodio si se conocen y `technical` con las mediciones. Las rutas y nombres originales no pertenecen al catálogo público.

`files[].location` indica el soporte de esa copia, por ejemplo `USB Patriot` o `Samsung T7`, y `files[].recordedAt` la fecha de comprobación cuando se dispone de ella. Si un título está en varios soportes, conserva su ID y todos sus archivos, asigna la ubicación a cada copia y resume ambos soportes en `inventory.location`. No reemplaces las copias de otro disco al actualizar uno. En registros antiguos sin ubicación por archivo se utiliza la ubicación de su ficha.

Las imágenes se referencian mediante HTTPS o una ruta `assets/nombre.jpg` existente en `web/`. No uses rutas absolutas al disco ni enlaces con tokens.

Ejemplo mínimo real de estructura (rellena los datos con el título indicado, no publiques ejemplos como películas reales):

```json
{
  "id": "IDENTIFICADOR_UNICO",
  "title": "TITULO_INDICADO",
  "type": "movies",
  "year": null,
  "files": [],
  "bytes": null,
  "inventory": {"source": "manual", "location": "Sin especificar", "recordedAt": "FECHA_REAL", "note": ""},
  "meta": {"matched": false, "title": "TITULO_INDICADO", "synopsis": "", "genres": [], "director": [], "cast": []}
}
```
