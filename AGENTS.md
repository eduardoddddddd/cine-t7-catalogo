# Cine T7 — instrucciones para cualquier LLM

Este es el nuevo catálogo de Edu. El repo anterior `cine-t7` pertenece a otro trabajo: no lo modifiques.

## Fuente de datos y publicación

- La fuente única es `data/catalog.json`. `web/` contiene el diseño. `dist/` se genera: no lo edites.
- Rama `main`. Antes de empezar, `git pull`; antes de subir, `git pull --rebase`. No sobrescribas cambios ajenos ni fuerces el push.
- Los cambios en `main` se publican automáticamente mediante `.github/workflows/pages.yml`.
- Lee `README.md` y `docs/FORMATO.md`. No necesitas acceder al disco T7 para añadir títulos.
- Conserva IDs existentes: mantienen favoritos y relaciones con las portadas.

## Peticiones como «añade esta película»

1. Busca el título en los datos y comprueba duplicados por título/año o ID de TMDB.
2. Distingue remakes, películas, series y secuelas. Si no queda claro el título concreto, pregunta; no elijas la primera coincidencia.
3. Para añadir sin API ni disco:
   `python scripts/catalog.py add --title "Título indicado por Edu" --year 2026 --location "Sin especificar"`.
   Omite el año si no lo ha indicado o no lo has verificado.
4. Para obtener una ficha real, usa tu conector de películas/búsqueda o TMDB. Con API local:
   `python scripts/catalog.py search --title "Título" --year 2026` y después
   `python scripts/catalog.py add --title "Título" --tmdb-id ID_VERIFICADO --location "T7"`.
   La clave se recibe por `TMDB_API_KEY` / `TMDB_ACCESS_TOKEN`. Nunca se escribe en el repo o el navegador.
5. Si tienes metadatos contrastados de otro conector, guarda un JSON temporal ignorado en `private/` y usa `--metadata-file private/ficha.json` (campos en FORMATO.md). También puedes editar el JSON directamente.
6. `files: []` significa que no se ha escaneado un archivo; conserva ese dato. No inventes tamaño, códecs, pistas, resolución, duración del archivo ni capítulos.
7. «Está en T7» indicado por Edu se registra como `inventory.location: "T7"` y origen `manual`; una indicación no es una medición del disco.
8. Completa portadas con URL HTTPS contrastada o imagen en `web/assets/`. No borres títulos manuales al importar un inventario.

## Comprobaciones antes de entregar

```
python scripts/catalog.py validate
python -m unittest discover -s tests -v
node --check web/app.js
python scripts/catalog.py build
```

Comprueba en un navegador una incorporación sin archivos y los filtros/fichas afectados. Después haz commit con `git commit -m`, sube y espera a que GitHub Pages termine. Informa de la URL y del resultado real.

## Ediciones y eliminaciones

`update --id ID --location "DVD" --note "Edición especial"` conserva las mediciones existentes.
`update --id ID --tmdb-id ID_VERIFICADO` completa una ficha pendiente.
`remove --id ID` solo con petición explícita de Edu.
`import --file inventario.json` incorpora un inventario con `items`, preserva registros manuales y elimina rutas y nombres de vídeo de la copia publicada. No elimina automáticamente títulos que no aparezcan en el nuevo escaneo.

## Privacidad y alcance

GitHub Pages y este repo son públicos. Publica fichas, portadas y datos técnicos; no rutas de Windows, nombres originales de archivos, correos, borradores de Gmail, secretos ni vídeos. Usa `private/` para información auxiliar local. Mantén las modificaciones dentro del alcance pedido y la interfaz en castellano.
