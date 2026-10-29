# cajista

> Antes `md2word` / `md-exporter-highlight`.

Conversor local de documentos Markdown a:

- HTML autocontenido;
- DOCX editable con estilos reales de Word;
- PDF paginado para lectura;
- ZIP opcional para conversiones por lotes.

El resaltado de sintaxis se delega al programa de línea de comandos [`highlight`](https://andre-simon.de/doku/highlight/en/highlight.php), de André Simon.

El objetivo del proyecto es mantener una sola definición visual, evitar servicios externos y ejecutar todo localmente.

---

## 0. Origen del nombre

El **cajista** era el oficial de imprenta que componía el texto a mano. La Real Academia Española lo define como el *«oficial de imprenta que, juntando y ordenando las letras, compone lo que se ha de imprimir»*. El cajista tomaba los tipos móviles de la **caja** (de ahí el nombre), los alineaba en el **componedor** y armaba las líneas y las páginas que después pasaban a la prensa. Debía conocer la ortografía y las normas de composición, porque de su trabajo dependía que el texto saliera correcto y legible. En el siglo XIX el oficio tenía incluso sus propios manuales en español, como el *Manual del cajista* de José María Palacios (1845).

El proyecto hace lo mismo con un documento Markdown: lo compone a partir de una única definición visual (el CSS) y lo entrega en el formato que haga falta. Esos formatos son:

- PDF;
- DOCX;
- ODT, el formato de texto de OpenDocument (estándar OASIS, nativo de LibreOffice), *planificado*;
- HTML de página única o multipágina, *multipágina planificado*;
- LaTeX, *a futuro*.

El nombre anterior, `md2word`, dejó de ser adecuado cuando Word pasó a ser solo una de varias salidas. Al elegir el nombre nuevo se descartaron:

- `imprenta`, porque ya está ocupado en PyPI;
- `galera` y `galera-converter`, porque se confunden con Galera Cluster, la replicación de MySQL/MariaDB.

En octubre de 2026, `cajista` no aparecía como paquete en PyPI, npm, crates.io ni Homebrew, ni como repositorio en GitHub.

---

## 1. Arquitectura

```text
Markdown
   ↓
MarkdownIt: análisis estructural
   ↓
HTML semántico autocontenido
   ├── bloques fenced → highlight → HTML con spans coloreados
   ├── CSS embebido o cargado desde archivo
   └── títulos, tablas, listas, citas, enlaces y código preservados
          ├──→ WeasyPrint → PDF
          └──→ BeautifulSoup + python-docx → DOCX
```

El HTML es el formato intermedio común, pero cada salida se genera con un motor adecuado:

- **PDF:** aplica directamente todo el CSS mediante WeasyPrint.
- **DOCX:** recorre el HTML y crea estructuras reales de Word. Los colores de los `<span>` generados por `highlight` se convierten en runs coloreados.

No se usa una captura del HTML ni se convierten tablas o bloques de código en imágenes.

---

## 2. Personalización de estilos

### 2.1 Fuente de verdad visual

El archivo CSS es la fuente principal de estilo.

```text
styles/default.css
```

Puede reemplazarse desde:

1. una opción de CLI;
2. el archivo YAML;
3. el CSS predeterminado incluido en el proyecto.

Prioridad general:

```text
opciones CLI > configuración YAML > valores predeterminados
```

Ejemplo:

```bash
python export.py convert documento.md \
  --config config.yaml \
  --css ./mis-estilos/curso.css
```

En Windows PowerShell:

```powershell
python export.py convert documento.md `
  --config config.yaml `
  --css .\mis-estilos\curso.css
```

### 2.2 CSS completo para PDF

El PDF aplica todo el CSS compatible con WeasyPrint, incluyendo:

- `@page`;
- tamaño de página y márgenes;
- encabezados y pies;
- contadores de página;
- tipografía;
- colores;
- tablas;
- saltos de página;
- bloques de código;
- listas;
- citas;
- enlaces;
- imágenes;
- selectores y variables CSS.

### 2.3 CSS para DOCX

Word no interpreta CSS directamente. El conversor obtiene del mismo CSS los valores que puede trasladar a Word.

La implementación debe leer primero las variables definidas en `:root`. Estas variables son la interfaz estable de personalización para ambos formatos:

```css
:root {
  --page-size: A4;
  --page-margin-top: 2.5cm;
  --page-margin-right: 2.5cm;
  --page-margin-bottom: 2.5cm;
  --page-margin-left: 2.5cm;

  --font-body: Arial, "Liberation Sans", sans-serif;
  --font-mono: Consolas, "Liberation Mono", monospace;
  --font-size-body: 11pt;
  --font-size-code: 9.2pt;

  --color-primary: #2c3e50;
  --color-accent: #64748b;
  --color-text: #1f2937;
  --color-border: #d1d5db;
  --color-surface: #f3f4f6;

  --h1-size: 24pt;
  --h2-size: 20pt;
  --h3-size: 16pt;
}
```

El conversor DOCX debe mapear estas variables a:

| Variable CSS | Aplicación DOCX |
|---|---|
| `--page-size` | tamaño de sección |
| `--page-margin-*` | márgenes de sección |
| `--font-body` | estilo `Normal` |
| `--font-mono` | `Code Inline`, `Code Block`, `Verbatim Block` |
| `--font-size-body` | tamaño del texto normal |
| `--font-size-code` | tamaño de bloques de código |
| `--color-primary` | Heading 1–6 y cabeceras de tabla |
| `--color-accent` | bordes de títulos, citas y código |
| `--color-text` | texto principal |
| `--color-border` | bordes de tablas y bloques |
| `--color-surface` | fondo de código y cabeceras de tabla |
| `--h1-size`–`--h6-size` | tamaños de Heading 1–6 |

Además, el conversor puede interpretar un subconjunto documentado de reglas:

- `body`;
- `h1` a `h6`;
- `p`;
- `a`;
- `blockquote`;
- `table`, `th`, `td`;
- `.code-container pre`;
- `.verbatim-block`.

Las propiedades no traducibles a DOCX se ignoran para Word, pero siguen funcionando en el PDF.

### 2.4 Configuración YAML

El YAML controla comportamiento, rutas y herramientas. No debe duplicar la paleta ni la tipografía salvo que se necesite una excepción específica de Word.

Ejemplo:

```yaml
project:
  output_dir: ./output
  build_dir: ./.build
  cache_dir: ./.cache/highlight
  overwrite: false
  keep_html: false

formats:
  docx: true
  pdf: true
  html: false
  zip: false

styles:
  css: ./styles/default.css
  docx_from_css: true
  reference_docx: null

highlight:
  executable: highlight
  theme: base16/atelier-cave-light
  inline_css: true
  fragment: true
  cache: true
  fallback: plain

pdf:
  engine: weasyprint

word:
  split_code_by_line: true
  repeat_table_header: true
  disable_spellcheck_in_code: true

qa:
  enabled: false
  render_docx: true
  render_pdf: true
```

Archivo incluido:

```text
config.example.yaml
```

---

## 3. Requisitos

### 3.1 Requisitos obligatorios

| Componente | Recomendación | Uso |
|---|---:|---|
| Python | 3.14.9 (fijada en `.python-version`); el paquete declara ≥ 3.10 | ejecución del conversor |
| `highlight` | 4.x; 4.18 o superior recomendado | coloración de sintaxis |
| WeasyPrint | 67 o superior | HTML a PDF |
| `python-docx` | 1.1 o superior | creación del DOCX |
| MarkdownIt | 3.x | análisis Markdown |
| BeautifulSoup + lxml | versiones indicadas en `requirements.txt` | lectura del HTML intermedio |
| PyYAML | 6.x | configuración YAML |
| tinycss2 | 1.4 o superior | lectura segura de CSS y variables |

WeasyPrint estable requiere Python 3.10 o superior y Pango 1.44 o superior. El entorno de referencia usa Python 3.14.9; las versiones exactas verificadas de los paquetes están en `requirements.lock`.

### 3.2 Requisitos opcionales de QA

| Componente | Uso |
|---|---|
| LibreOffice | renderizar DOCX en modo headless para inspección |
| Poppler (`pdftoppm`, `pdfinfo`) | renderizar e inspeccionar PDF |
| Pillow | generar hojas de contacto y detectar páginas anómalas |

La conversión base puede funcionar sin LibreOffice y Poppler. Son necesarios cuando se activa la revisión visual automática.

---

## 4. Comprobar versiones

### 4.1 Python y paquetes

```bash
python --version
python -m pip --version
python -m pip show weasyprint python-docx markdown-it-py beautifulsoup4 lxml PyYAML tinycss2 typer
```

En sistemas donde Python 3 se instala como `python3`:

```bash
python3 --version
python3 -m pip --version
```

### 4.2 `highlight`

```bash
highlight --version
highlight --list-scripts=langs
highlight --list-scripts=themes
```

### 4.3 WeasyPrint

```bash
weasyprint --info
```

También puede ejecutarse como módulo:

```bash
python -m weasyprint --info
```

### 4.4 LibreOffice

```bash
soffice --version
```

En Windows, si LibreOffice no está en `PATH`:

```powershell
& "C:\Program Files\LibreOffice\program\soffice.com" --version
```

### 4.5 Poppler

```bash
pdftoppm -v
pdfinfo -v
```

### 4.6 Diagnóstico integrado recomendado

El CLI debería proporcionar:

```bash
python export.py doctor
```

Salida esperada:

```text
Python:        3.12.10            OK
highlight:     4.18               OK
WeasyPrint:    69.0               OK
LibreOffice:   26.2               opcional / encontrado
pdftoppm:      25.x               opcional / encontrado
CSS:           styles/default.css OK
Config YAML:   config.yaml        OK
```

El comando debe devolver código de salida distinto de cero si falta un requisito obligatorio.

---

## 5. Instalación en Windows

Guía paso a paso para levantar el entorno desde cero en Windows 10/11 x64. Los comandos usan **PowerShell** salvo donde se indica la terminal de MSYS2. Cierre y vuelva a abrir PowerShell cada vez que instale algo que modifique `PATH`.

Resumen de lo que se instala:

| Componente | Para qué | Obligatorio |
|---|---|---|
| Python 3.14.9 x64 | ejecutar `cajista` | sí |
| Highlight 4.x | coloración de sintaxis | sí (sin él, el código sale sin colores) |
| MSYS2 + Pango | bibliotecas nativas de WeasyPrint (PDF) | sí, para PDF |
| Poppler (`pdftoppm`) | QA de PDF | no |
| LibreOffice | QA de DOCX | no |

### 5.1 Instalar Python 3.14.9

El repositorio fija la versión en `.python-version` (`3.14.9`). Use la edición de **64 bits (x64)**: las DLL de Pango que instala MSYS2 son de 64 bits y deben coincidir con Python.

**Opción A: instalador de python.org (recomendada)**

1. Descargue *Windows installer (64-bit)* de Python 3.14.9 desde <https://www.python.org/downloads/windows/>.
2. En el instalador, marque *Add python.exe to PATH* y deje habilitado el lanzador `py`.

**Opción B: pyenv-win**, que respeta `.python-version` igual que pyenv en macOS:

```powershell
pyenv update
pyenv install 3.14.9
pyenv local 3.14.9      # ya está fijado en .python-version
```

Compruebe:

```powershell
py -3.14 --version      # Python 3.14.9 (Opción A)
python --version        # Python 3.14.9
```

### 5.2 Instalar Highlight

1. Descargue el instalador o el ZIP para Windows x64 desde <http://www.andre-simon.de/zip/download.php>.
2. Instálelo (ruta típica: `C:\Program Files\Highlight\`) o extraiga el ZIP, por ejemplo en `C:\Tools\highlight\`.
3. Agregue la carpeta que contiene `highlight.exe` al `PATH` del usuario (*Configuración → Sistema → Información → Configuración avanzada del sistema → Variables de entorno*).
4. Cierre y vuelva a abrir PowerShell.

Compruebe:

```powershell
highlight --version
```

Si prefiere no tocar `PATH`, indique la ruta completa en YAML:

```yaml
highlight:
  executable: "C:/Program Files/Highlight/highlight.exe"
```

o por CLI:

```powershell
python export.py convert documento.md --highlight-exe "C:\Program Files\Highlight\highlight.exe"
```

### 5.3 Instalar MSYS2 y Pango (para WeasyPrint)

WeasyPrint se instala con pip, pero necesita Pango, que no viene con pip.

1. Instale MSYS2 desde <https://www.msys2.org/> en la **ruta predeterminada** `C:\msys64`.
2. Abra la terminal **MSYS2 MINGW64** y ejecute:

```text
pacman -Syu
pacman -S mingw-w64-x86_64-pango
```

Si `pacman -Syu` pide cerrar la terminal, ciérrela, ábrala de nuevo y repita `pacman -Syu` antes de instalar Pango.

Opcional, en la misma terminal, Poppler para QA de PDF (deja `pdftoppm.exe` en la misma carpeta):

```text
pacman -S mingw-w64-x86_64-poppler
```

WeasyPrint busca las DLL por defecto en `C:\msys64\mingw64\bin`; si MSYS2 quedó en esa ruta no hace falta configurar nada más. Si lo instaló en otra ruta:

```powershell
$env:WEASYPRINT_DLL_DIRECTORIES = "D:\msys64\mingw64\bin"
```

Para hacerlo permanente, defina `WEASYPRINT_DLL_DIRECTORIES` como variable de entorno del usuario.

**No** agregue `C:\msys64\mingw64\bin` al `PATH` general: contiene su propio `python.exe` y otras herramientas que pueden ocultar las de Windows. Para `pdftoppm`, use la ruta completa en YAML (ver 5.6).

### 5.4 Crear el entorno virtual

Desde la raíz del proyecto:

```powershell
cd C:\ruta\a\cajista
py -3.14 -m venv .venv          # o: python -m venv .venv  (pyenv-win)
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Para no repetirlo en cada sesión: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`.

Alternativa con `cmd.exe`:

```bat
.venv\Scripts\activate.bat
```

Con el entorno activo, confirme que se usa el Python del `.venv`:

```powershell
(Get-Command python).Source     # ...\cajista\.venv\Scripts\python.exe
python --version                # Python 3.14.9
```

### 5.5 Instalar dependencias de Python

```powershell
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt     # rangos compatibles
# o, para replicar exactamente el entorno verificado:
# python -m pip install -r requirements.lock
python -m pip install -e . --no-deps          # opcional: comando `cajista`
python -m pip check                           # "No broken requirements found."
```

`requirements.lock` se generó en macOS. No contiene paquetes exclusivos de macOS, así que debería instalarse igual en Windows; si algún paquete no tiene wheel para Windows y Python 3.14, use `requirements.txt`.

Compruebe que WeasyPrint encuentra Pango:

```powershell
python -c "import weasyprint; print(weasyprint.__version__)"
```

### 5.6 QA opcional: LibreOffice y Poppler

```powershell
winget install TheDocumentFoundation.LibreOffice
& "C:\Program Files\LibreOffice\program\soffice.com" --version
```

LibreOffice no queda en `PATH`, y Poppler de MSYS2 tampoco (ver 5.3). Declare ambas rutas en su YAML:

```yaml
qa:
  libreoffice_executable: "C:/Program Files/LibreOffice/program/soffice.com"
  pdftoppm_executable: "C:/msys64/mingw64/bin/pdftoppm.exe"
```

### 5.7 Diagnóstico y prueba de humo

`config.example.yaml` no trae las rutas de Windows. Copie la configuración y ajústela si `highlight`, LibreOffice o `pdftoppm` no están en `PATH`:

```powershell
Copy-Item config.example.yaml config.yaml
# edite config.yaml: highlight.executable, qa.libreoffice_executable, qa.pdftoppm_executable
python export.py doctor --config config.yaml
```

Todos los componentes obligatorios deben aparecer como `OK`; si falta alguno, `doctor` termina con código 1. Luego:

```powershell
python export.py convert examples\example.md --config config.yaml `
  -f html -f docx -f pdf --overwrite
dir output
```

Abra `output\example.pdf` y compruebe que el bloque de JavaScript sale con colores y sangría. Si sale en texto plano, `highlight` no se encontró: corríjalo y vuelva a convertir con `--no-cache`, porque el resultado sin colores queda en caché.

### 5.8 Problemas frecuentes en Windows

| Síntoma | Causa probable | Solución |
|---|---|---|
| `cannot load library 'libgobject-2.0-0'` o `'libpango-1.0-0'` | Pango no instalado, o MSYS2 fuera de `C:\msys64` | 5.3; defina `WEASYPRINT_DLL_DIRECTORIES` |
| `OSError: [WinError 193]` al cargar DLL | Python de 32 bits o ARM64 con DLL x64 | instale Python 3.14.9 **x64** y recree el `.venv` |
| `highlight` no encontrado en `doctor` | `PATH` no actualizado | reabra PowerShell o use `highlight.executable` en YAML |
| `Activate.ps1 cannot be loaded` | política de ejecución | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
| `python` abre Microsoft Store | alias de ejecución de aplicaciones | desactive los alias `python.exe`/`python3.exe` en *Configuración → Aplicaciones → Alias de ejecución*, o use `py -3.14` |

---

## 6. Instalación en Linux

### 6.1 Debian y Ubuntu

```bash
sudo apt update
sudo apt install -y \
  python3 \
  python3-venv \
  python3-pip \
  highlight \
  libpango-1.0-0 \
  libpangoft2-1.0-0 \
  libharfbuzz-subset0
```

Para QA opcional:

```bash
sudo apt install -y libreoffice-writer poppler-utils
```

Crear entorno:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Comprobar:

```bash
python --version
highlight --version
weasyprint --info
soffice --version
pdftoppm -v
```

> En algunas versiones estables de Debian, el paquete `highlight` del repositorio puede ser anterior a 4.x. Si necesita una versión reciente, use los paquetes oficiales del proyecto o compile Highlight siguiendo su documentación.

### 6.2 Fedora

```bash
sudo dnf install -y \
  python3 \
  python3-pip \
  highlight \
  pango
```

Para QA opcional:

```bash
sudo dnf install -y libreoffice-writer poppler-utils
```

Después:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 6.3 Arch Linux

Instale Python, Pango, LibreOffice y Poppler desde los repositorios de la distribución. Si `highlight` no se encuentra en los repositorios habilitados, instálelo desde una fuente confiable o compile el proyecto oficial.

Después:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## 7. Instalación en macOS

### 7.1 Homebrew

Instale Homebrew si todavía no está disponible.

Instale pyenv (para Python 3.14.9), Highlight y Pango:

```bash
brew install pyenv highlight pango
```

WeasyPrint se instala con pip dentro del `.venv` (7.2); de Homebrew solo hace falta Pango. `brew install weasyprint` no es necesario: instala su propio Python, separado del entorno del proyecto.

Si pyenv es nuevo en su equipo, agregue a `~/.zshrc` y abra una terminal nueva:

```bash
eval "$(pyenv init - zsh)"
```

Para QA opcional:

```bash
brew install poppler
brew install --cask libreoffice
```

### 7.2 Entorno virtual

El repositorio fija Python 3.14.9 en `.python-version`. Con pyenv:

```bash
pyenv install 3.14.9        # solo si todavía no está instalada
python --version            # Python 3.14.9 (pyenv lee .python-version)
python -m venv .venv
source .venv/bin/activate
```

Con el entorno activo, confirme que se usa el Python del `.venv`:

```bash
which python                # .../cajista/.venv/bin/python
python --version            # Python 3.14.9
```

Instale las herramientas de build y las dependencias:

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt   # solo dependencias
python -m pip install -e .                  # opcional: paquete editable + comando `cajista`
python -m pip check                         # debe responder "No broken requirements found."
```

WeasyPrint necesita Pango, que no se instala con pip. Si no instaló `weasyprint` con Homebrew en el paso 7.1, instale al menos Pango y Highlight:

```bash
brew install pango highlight
```

Diagnóstico final:

```bash
python export.py doctor --config config.example.yaml
```

#### Versiones fijadas

`requirements.txt` declara rangos compatibles. `requirements.lock` congela las versiones exactas de un entorno verificado (Python 3.14.9, `doctor` y `convert` OK). Para reproducirlo:

```bash
python -m pip install -r requirements.lock
python -m pip install -e . --no-deps        # opcional: comando `cajista`
```

Para regenerarlo después de actualizar dependencias y volver a verificar:

```bash
python -m pip freeze --exclude-editable > requirements.lock
```

Versiones de sistema verificadas con ese lock (Homebrew, Apple Silicon): `highlight` 4.21, `pango` 1.58.2, `cairo` 1.18.6, `harfbuzz` 15.0.0, `poppler` 26.10.0, LibreOffice 26.8.1. No se fijan con `brew pin`: así se reciben parches de seguridad y se evitan conflictos con otras fórmulas que dependen de Pango. Después de cada `brew upgrade`, verifique:

```bash
python export.py doctor --config config.example.yaml
python export.py convert examples/example.md --config config.example.yaml \
  -f html -f docx -f pdf --overwrite
```

Si alguna vez se convirtió sin `highlight` instalado, el código sin colores quedó en caché: limpie `.cache/highlight/` o use `--no-cache` una vez instalado.

Comprobar:

```bash
python --version
highlight --version
weasyprint --info
soffice --version
pdftoppm -v
```

En macOS, el comando de LibreOffice puede no quedar automáticamente en `PATH`. Ruta habitual:

```bash
/Applications/LibreOffice.app/Contents/MacOS/soffice --version
```

Puede configurarla en YAML:

```yaml
qa:
  libreoffice_executable: /Applications/LibreOffice.app/Contents/MacOS/soffice
```

Si WeasyPrint no encuentra bibliotecas instaladas por Homebrew:

```bash
export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_FALLBACK_LIBRARY_PATH
```

En equipos Intel, Homebrew suele usar `/usr/local/lib` en lugar de `/opt/homebrew/lib`.

---

## 8. Estructura recomendada

```text
cajista/
├── export.py
├── config.yaml
├── config.example.yaml
├── requirements.txt
├── README.md
├── cajista/
│   ├── cli.py
│   ├── configuration.py
│   ├── markdown_parser.py
│   ├── highlight_runner.py
│   ├── html_builder.py
│   ├── css_tokens.py
│   ├── html_to_docx.py
│   ├── html_to_pdf.py
│   ├── docx_styles.py
│   ├── batch.py
│   └── qa.py
├── styles/
│   └── default.css
├── input/
├── output/
├── .build/
└── .cache/
    └── highlight/
```

---

## 9. Resolución de configuración

El programa debe resolver la configuración en este orden:

```text
1. valores predeterminados internos
2. YAML predeterminado, si existe
3. YAML indicado por --config
4. opciones explícitas de CLI
```

Ejemplo:

```yaml
# config.yaml
formats:
  docx: true
  pdf: true

styles:
  css: ./styles/gris.css

highlight:
  theme: base16/atelier-cave-light
```

```bash
python export.py convert documento.md \
  --config config.yaml \
  --css ./styles/azul.css \
  --format pdf
```

Resultado:

- se carga `config.yaml`;
- `--css` reemplaza `styles.css`;
- `--format pdf` genera solamente PDF aunque el YAML habilite DOCX.

Las rutas relativas dentro del YAML deben resolverse respecto a la carpeta donde se encuentra el YAML, no respecto al directorio actual de la terminal.

---

## 10. Uso del CLI

### 10.1 Convertir un archivo

```bash
python export.py convert documento.md
```

Salidas predeterminadas:

```text
output/documento.docx
output/documento.pdf
```

### 10.2 Usar configuración y CSS personalizados

```bash
python export.py convert documento.md \
  --config ./config.yaml \
  --css ./styles/curso-vue.css
```

### 10.3 Generar solo DOCX

```bash
python export.py convert documento.md --format docx
```

### 10.4 Generar solo PDF

```bash
python export.py convert documento.md --format pdf
```

### 10.5 Generar varios formatos

```bash
python export.py convert documento.md \
  --format docx \
  --format pdf \
  --format html
```

### 10.6 Conservar HTML intermedio

```bash
python export.py convert documento.md --keep-html
```

### 10.7 Elegir tema de `highlight`

```bash
python export.py convert documento.md \
  --highlight-theme base16/atelier-cave-light
```

Liste los temas instalados:

```bash
highlight --list-scripts=themes
```

### 10.8 Indicar la ruta de `highlight`

```bash
python export.py convert documento.md \
  --highlight-exe /opt/highlight/bin/highlight
```

Windows:

```powershell
python export.py convert documento.md `
  --highlight-exe "C:\Tools\highlight\highlight.exe"
```

### 10.9 Cambiar directorio de salida

```bash
python export.py convert documento.md --output-dir ./dist
```

### 10.10 Cambiar nombre base

```bash
python export.py convert documento.md \
  --output-name fase-03-axios-servicios-v1
```

### 10.11 Sobrescribir archivos existentes

```bash
python export.py convert documento.md --overwrite
```

Sin `--overwrite`, el programa debe fallar si la salida ya existe.

### 10.12 Procesamiento por lotes

```bash
python export.py batch ./input \
  --pattern "*.md" \
  --output-dir ./output
```

Recursivo:

```bash
python export.py batch ./input \
  --recursive \
  --pattern "*.md"
```

### 10.13 Generar ZIP

```bash
python export.py batch ./input \
  --format docx \
  --zip ./output/documentos-docx.zip
```

### 10.14 Validar sin convertir

```bash
python export.py validate documento.md \
  --config config.yaml \
  --css styles/default.css
```

Debe verificar:

- Markdown legible;
- YAML válido;
- CSS válido;
- variables CSS obligatorias;
- disponibilidad de `highlight`;
- tema y lenguaje solicitados;
- motores requeridos para los formatos elegidos;
- permisos de escritura.

### 10.15 Diagnóstico del entorno

```bash
python export.py doctor --config config.yaml
```

---

## 11. Opciones propuestas

| Opción | Descripción |
|---|---|
| `--config PATH` | YAML de configuración |
| `--css PATH` | CSS visual; reemplaza la ruta del YAML |
| `--format FORMAT` | `docx`, `pdf` o `html`; repetible |
| `--output-dir PATH` | directorio de salida |
| `--output-name NAME` | nombre base de salida |
| `--highlight-exe PATH` | ejecutable de Highlight |
| `--highlight-theme NAME` | tema de Highlight |
| `--keep-html` | conserva el HTML intermedio |
| `--overwrite` | permite sobrescribir salidas |
| `--no-cache` | desactiva caché de Highlight |
| `--qa` | habilita revisión automatizada |
| `--zip PATH` | comprime resultados por lote |
| `--recursive` | busca Markdown en subdirectorios |
| `--pattern GLOB` | patrón para procesamiento por lotes |
| `--verbose` | diagnóstico detallado |
| `--quiet` | salida mínima |

---

## 12. Integración de `highlight`

Para cada bloque fenced:

````markdown
```javascript
const app = new Vue({ el: "#app" });
```
````

El programa debe:

1. detectar `javascript`;
2. normalizar aliases, por ejemplo `js` → `javascript`;
3. escribir el código en un archivo temporal con extensión adecuada;
4. ejecutar `highlight` en modo fragmento HTML y CSS inline;
5. insertar el fragmento en el HTML intermedio;
6. guardar el resultado en caché;
7. usar texto plano si el lenguaje no se reconoce o el comando falla.

Comando conceptual:

```bash
highlight \
  --out-format=html \
  --fragment \
  --inline-css \
  --syntax=javascript \
  --style=base16/atelier-cave-light \
  --input=source.js \
  --output=fragment.html
```

El código debe invocarse con `subprocess.run()` usando una lista de argumentos, nunca construyendo una cadena con `shell=True`.

### 12.1 Caché

La clave de caché debe incluir:

```text
versión de highlight
+ tema
+ lenguaje normalizado
+ contenido exacto del bloque
+ opciones relevantes
```

Ejemplo de clave:

```text
SHA-256(JSON normalizado)
```

La caché evita ejecutar un proceso nuevo para bloques repetidos.

### 12.2 Estilo exterior e interior

Responsabilidades:

- **CSS documental:** fondo, borde, padding, tipografía y tamaño del bloque.
- **Highlight:** colores de tokens internos.

No se debe permitir que el tema de Highlight reemplace el fondo general del documento salvo que el usuario lo solicite explícitamente.

---

## 13. Generación del DOCX

El DOCX debe contener:

- `Normal`;
- `Heading 1` a `Heading 6`;
- `Code Inline`;
- `Code Block`;
- `Verbatim Block`;
- `Quote`;
- listas reales;
- tablas reales;
- hipervínculos funcionales;
- runs separados por color para bloques de código.

Para mejorar rendimiento y editabilidad, cada línea de un bloque de código debe convertirse en un párrafo `Code Block`. Los bordes se coordinan para que visualmente el conjunto parezca un único bloque.

Los `<span style="color: ...">` generados por Highlight se convierten en runs:

```text
span HTML → texto + color → run DOCX
```

Las propiedades Word no expresables en CSS pueden configurarse en YAML, por ejemplo:

```yaml
word:
  split_code_by_line: true
  repeat_table_header: true
  disable_spellcheck_in_code: true
  keep_headings_with_next: true
```

Opcionalmente puede usarse un `reference.docx` como base avanzada:

```yaml
styles:
  css: ./styles/default.css
  reference_docx: ./styles/reference.docx
```

El CSS sigue siendo la fuente visual; el documento de referencia puede aportar estilos Word específicos, encabezados, pies o metadatos que no conviene reconstruir por código.

---

## 14. Generación del PDF

El PDF se genera desde el HTML autocontenido:

```python
from weasyprint import HTML

HTML(
    filename="documento.html",
    base_url="."
).write_pdf("documento.pdf")
```

Si el CSS se carga por separado:

```python
from weasyprint import CSS, HTML

HTML(filename="documento.html").write_pdf(
    "documento.pdf",
    stylesheets=[CSS(filename="styles/default.css")]
)
```

Para evitar discrepancias, la modalidad recomendada es incrustar el CSS dentro del HTML final y conservar el archivo HTML solamente cuando se use `--keep-html` o se solicite formato HTML.

---

## 15. QA opcional

### 15.1 Renderizar DOCX

Ejemplo genérico:

```bash
soffice \
  --headless \
  --nologo \
  --norestore \
  --convert-to pdf \
  --outdir .build/qa-docx \
  output/documento.docx
```

LibreOffice necesita acceso de escritura a su perfil. Para ejecuciones paralelas, use perfiles temporales separados.

### 15.2 Renderizar PDF a imágenes

```bash
pdftoppm \
  -png \
  -r 140 \
  output/documento.pdf \
  .build/qa-pdf/page
```

### 15.3 Controles automáticos

El módulo QA puede detectar:

- páginas casi vacías;
- contenido en el borde exterior;
- imágenes o tablas cortadas;
- páginas con densidad anómala;
- errores de renderizado;
- diferencias de recuento de páginas;
- ausencia de fuentes;
- cuadros negros o caracteres sustituidos.

La comparación textual debe hacerse además entre Markdown, HTML y DOCX para verificar que la exportación no eliminó contenido.

---

## 16. Ejemplos completos

### 16.1 Conversión individual con estilo personalizado

Linux/macOS:

```bash
source .venv/bin/activate

python export.py convert ./input/fase-03.md \
  --config ./config.yaml \
  --css ./styles/tecnico-gris.css \
  --highlight-theme base16/atelier-cave-light \
  --format docx \
  --format pdf \
  --output-dir ./output \
  --overwrite
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1

python export.py convert .\input\fase-03.md `
  --config .\config.yaml `
  --css .\styles\tecnico-gris.css `
  --highlight-theme base16/atelier-cave-light `
  --format docx `
  --format pdf `
  --output-dir .\output `
  --overwrite
```

### 16.2 Lote DOCX y ZIP

```bash
python export.py batch ./input \
  --config ./config.yaml \
  --css ./styles/default.css \
  --format docx \
  --output-dir ./output/docx \
  --zip ./output/curso-docx.zip
```

### 16.3 PDF con otro CSS sin tocar YAML

```bash
python export.py convert documento.md \
  --config config.yaml \
  --css styles/lectura-compacta.css \
  --format pdf
```

---

## 17. Resolución de problemas

### `highlight: command not found`

Compruebe:

```bash
highlight --version
```

Soluciones:

- agregue Highlight al `PATH`;
- indique la ruta en YAML;
- use `--highlight-exe`.

### El tema de Highlight no existe

Liste temas:

```bash
highlight --list-scripts=themes
```

Use exactamente uno de los nombres instalados.

### WeasyPrint no encuentra Pango en Windows

Compruebe primero que Pango está instalado en MSYS2 (sección 5.3) y que Python es x64 (sección 5.8). Si MSYS2 está fuera de `C:\msys64`, configure:

```powershell
$env:WEASYPRINT_DLL_DIRECTORIES = "D:\msys64\mingw64\bin"   # su ruta real
```

Después:

```powershell
python -m weasyprint --info
```

### WeasyPrint no encuentra bibliotecas en macOS

Síntoma típico al ejecutar `doctor` o `convert`:

```text
WeasyPrint could not import some external libraries.
OSError: cannot load library 'libpango-1.0-0': dlopen(libpango-1.0-0, 0x0002): tried: ...
```

Si la lista de rutas probadas ya incluye `/opt/homebrew/lib`, la ruta es correcta y lo que falta es Pango. Instálelo:

```bash
brew install pango
ls /opt/homebrew/lib/libpango-1.0*   # debe mostrar libpango-1.0.dylib
```

Si Pango está instalado y aun así no se encuentra, indique la ruta de las bibliotecas.

Apple Silicon:

```bash
export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_FALLBACK_LIBRARY_PATH
```

Intel:

```bash
export DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib:$DYLD_FALLBACK_LIBRARY_PATH
```

### El DOCX no reproduce una propiedad CSS

El PDF aplica CSS; Word utiliza un mapeo. Compruebe que la propiedad esté cubierta por:

- una variable soportada de `:root`;
- un selector compatible;
- una opción `word:` del YAML;
- el `reference.docx`, si se usa.

### El código se ve bien en PDF pero no en DOCX

Compruebe que Highlight esté generando CSS inline y que el parser DOCX lea:

```html
<span style="color:#A626A4">...</span>
```

No dependa únicamente de clases CSS como `.hl.kwa`, salvo que el conversor también resuelva esas clases contra la hoja de estilo.

### El PDF cambia de tipografía entre equipos

Instale las mismas fuentes en todos los sistemas o use familias portables. No distribuya archivos de fuentes salvo que su licencia lo permita.

---

## 18. Seguridad

- No use `shell=True` para ejecutar Highlight, LibreOffice o Poppler.
- Use directorios temporales propios del sistema.
- Valide extensiones y rutas.
- No permita que un Markdown no confiable lea archivos arbitrarios mediante enlaces locales.
- WeasyPrint advierte que HTML y CSS no confiables pueden representar riesgos; limite recursos externos y rutas accesibles.
- Resuelva los archivos relativos respecto al documento o al YAML de forma explícita.
- No sobrescriba salidas salvo `--overwrite`.

---

## 19. Archivos incluidos en este paquete

```text
README.md
config.example.yaml
requirements.txt
styles/default.css
```

Copie la configuración de ejemplo:

Linux/macOS:

```bash
cp config.example.yaml config.yaml
```

Windows PowerShell:

```powershell
Copy-Item config.example.yaml config.yaml
```

Después edite:

```text
config.yaml
styles/default.css
```

El CSS controla el aspecto del documento. El YAML controla cómo se ejecuta el pipeline.

---

## 20. Referencias oficiales

- Highlight: <https://andre-simon.de/doku/highlight/en/highlight.php>
- Instalación de Highlight: <https://andre-simon.de/doku/highlight/en/install.html>
- WeasyPrint: <https://doc.courtbouillon.org/weasyprint/stable/>
- Instalación de WeasyPrint: <https://doc.courtbouillon.org/weasyprint/stable/first_steps.html>
- Python: <https://www.python.org/downloads/>
- Parámetros de LibreOffice: <https://help.libreoffice.org/latest/en-US/text/shared/guide/start_parameters.html>

---

## 17. Estado de esta distribución

Esta distribución ya incluye una implementación funcional del pipeline descrito:

- `export.py` y `cajista/cli.py`: CLI con `convert`, `batch`, `validate` y `doctor`.
- `cajista/highlight_runner.py`: ejecución segura de `highlight`, aliases, caché y fallback.
- `cajista/html_builder.py`: Markdown a HTML semántico autocontenido.
- `cajista/html_to_pdf.py`: HTML a PDF mediante WeasyPrint.
- `cajista/html_to_docx.py`: HTML a estructuras Word editables y spans coloreados a runs.
- `cajista/css_tokens.py`: lectura de variables CSS para trasladarlas al DOCX.
- `styles/default.css`: estilo visual predeterminado.

### Prueba rápida

```bash
python export.py doctor --config config.example.yaml
python export.py convert examples/example.md \
  --config config.example.yaml \
  --format html \
  --format docx \
  --format pdf \
  --overwrite
```

Windows PowerShell:

```powershell
python export.py doctor --config config.example.yaml
python export.py convert examples\example.md `
  --config config.example.yaml `
  --format html `
  --format docx `
  --format pdf `
  --overwrite
```

### Limitaciones conocidas

- WeasyPrint interpreta el CSS completo; Word solo puede reproducir el subconjunto trasladado por el conversor.
- HTML arbitrario incrustado en Markdown puede requerir un renderer adicional si contiene componentes complejos.
- Las imágenes remotas no se incrustan todavía en el DOCX; se conserva una referencia textual. Las imágenes locales pueden añadirse en una extensión posterior.
- El resaltado cae a texto monoespaciado cuando `highlight` no está instalado o el lenguaje no es reconocido.
