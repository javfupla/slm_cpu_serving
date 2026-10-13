## Guía de Contingencias y Resolución de Problemas

El taller está diseñado para poder completarse incluso si algunos servicios externos no están disponibles.

### Árbol de Decisión Rápido

| Situación | Acción |
|------------|----------|
| GitHub Codespaces funciona | Utilizar Codespaces (recomendado) |
| Codespaces no funciona | Utilizar instalación local de Python |
| GitHub no está accesible | Descargar los archivos desde la carpeta compartida |
| PyPI no está accesible | Instalar dependencias desde el wheelhouse |
| Hugging Face no está accesible | Utilizar el archivo de modelos proporcionado |
| La conexión a Internet es inestable | Utilizar los archivos descargados previamente |
| Todo falla | Seguir la demostración guiada del instructor |

---

## Archivos Compartidos

Si alguna dependencia online falla, descarga los recursos necesarios desde:

**[URL_CARPETA_COMPARTIDA]**

La carpeta compartida contiene:

```text
code.zip
models.zip
wheelhouse.zip
```

### code.zip

Contiene el código tal como se encuentra publicado en GitHub

### models.zip

Contiene:

```text
models/
└── <model>.gguf
```

### wheelhouse.zip

Contiene los paquetes Python necesarios para instalación sin acceso a Internet:

```text
wheelhouse/
├── windows/
├── linux/
└── mac/
```

---

## Escenario 1: GitHub Codespaces No Disponible

Síntomas:

- No es posible crear un Codespace.
- Errores de conexión.
- La interfaz se queda cargando indefinidamente.
- Restricciones debidas a firewall, proxy o similar.

Solución:

1. Descargar:
   - code.zip
   - models.zip
   - wheelhouse.zip

2. Extraer los archivos.

3. Crear un entorno virtual.

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

4. Instalar dependencias utilizando:
   - Instalación estándar (si PyPI está accesible), o
   - Instalación offline desde wheelhouse (ver Escenario 3).

---

## Escenario 2: GitHub No Disponible

Síntomas:

- No se puede clonar el repositorio.
- GitHub bloqueado por políticas de red.
- Incidencia temporal en GitHub.

Solución:

Descargar:

```text
code.zip
```

desde:

```text
[URL_CARPETA_COMPARTIDA]
```

Extraer el contenido y continuar.

No se requiere acceso a GitHub después de este paso.

---

## Escenario 3: PyPI No Disponible

Síntomas:

- Los comandos `pip install` fallan.
- Acceso a `pypi.org` bloqueado.
- Acceso a `files.pythonhosted.org` bloqueado.
- Problemas de certificados SSL o inspección HTTPS.

Solución:

1. Descargar:

```text
wheelhouse.zip
```

2. Extraer el contenido.

3. Instalar utilizando los paquetes locales.

### Windows

```powershell
pip install --no-index --find-links wheelhouse/windows .
```

### Linux

```bash
pip install --no-index --find-links wheelhouse/linux .
```

### macOS (Apple Silicon)

```bash
pip install --no-index --find-links wheelhouse/mac .
```

No se requiere acceso a Internet para esta instalación.

---

## Escenario 4: Hugging Face No Disponible

Síntomas:

- Error al descargar modelos.
- huggingface.co bloqueado.
- Problemas de proxy o certificados.
- Limitaciones temporales de acceso.

Solución:

Descargar:

```text
models.zip
```

desde:

```text
[URL_CARPETA_COMPARTIDA]
```

Extraer el modelo y continuar.

No se requiere acceso a Hugging Face.

---

## Escenario 5: Problemas con Proxy / Firewall

Síntomas:

- Desconexiones frecuentes de Codespaces.
- Errores CORS en el navegador.
- Problemas conectando con VS Code Web.
- Errores relacionados con túneles o WebSockets.

Solución:

Omitir Codespaces y utilizar la instalación local.

Archivos necesarios:

```text
code.zip
models.zip
wheelhouse.zip
```

Todos los ejercicios del taller pueden completarse localmente.

---

## Escenario 6: Conexión a Internet Lenta o Inestable

Síntomas:

- Descargas muy lentas.
- Cortes de conexión.
- Timeouts durante instalaciones.
- Codespaces se desconecta frecuentemente.

Solución:

Utilizar las copias descargadas previamente de:

```text
code.zip
models.zip
wheelhouse.zip
```

Una vez instalados los recursos, no será necesaria ninguna conexión adicional para completar los ejercicios.

---

## Validación del Entorno

Tras completar la instalación, ejecutar:

```bash
python workspace_check.py
```

La salida esperada debe ser similar a:

```text
✅ Versión de Python correcta
✅ Dependencias instaladas
✅ Memoria disponible suficiente
✅ Modelo encontrado
✅ Prueba de inferencia completada correctamente
```

Si todas las comprobaciones son correctas, el entorno está listo para el taller.

---

## Requisitos Mínimos

```text
Python 3.12 o superior
4 núcleos de CPU
8 GB de RAM
10 GB de espacio libre en disco
```

## Requisitos Recomendados

```text
4 o más núcleos de CPU
16 GB de RAM
15 GB de espacio libre en disco
```

No se requiere GPU.

---

## Configuraciones Soportadas

### Opción Recomendada

```text
GitHub Codespaces
```

### Opción Alternativa Totalmente Soportada

```text
VS Code
Python 3.12+
Wheelhouse offline
Modelo GGUF local
```

Todos los ejercicios del taller pueden realizarse utilizando cualquiera de las dos opciones.