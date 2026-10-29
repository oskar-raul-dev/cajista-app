# Guía de estilo y pipeline de exportación DOCX/PDF — Versión 3 (Gris)

---

# Sección 1: Lista de estilos para PDF y DOCX

## 1.1 Objetivo de la guía

Esta guía define los estilos que deben aplicarse al convertir documentos Markdown del proyecto a:

* PDF
* Word / DOCX
* HTML intermedio autocontenido

La regla principal es:

> El contenido fuente no debe modificarse. Solo debe transformarse su representación visual respetando la estructura Markdown original.

El PDF debe priorizar lectura.
El DOCX debe priorizar edición futura.
El HTML intermedio debe servir como fuente controlada para generar PDF con CSS real.

---

## 1.2 Principios generales

Los documentos exportados deben ser técnicos, limpios y consistentes.

Reglas generales:

* Fondo blanco.
* Sin portada compleja salvo solicitud explícita.
* Márgenes amplios y consistentes.
* Tipografía sans-serif para texto.
* Tipografía monoespaciada para código, comandos, rutas y texto preformateado.
* Paleta visual única en todo el proyecto.
* Jerarquía de títulos clara.
* Tablas reales, no simuladas.
* Código y texto verbatim claramente diferenciados.
* Negritas e itálicas reales.
* No añadir contenido que no exista en el Markdown fuente.
* No eliminar contenido del Markdown fuente.
* No reescribir el texto fuente.

---

## 1.3 Paleta oficial (Versión 3 - Gris)

Usar siempre la misma paleta en todos los documentos del proyecto.

| Uso                                      | Color     |
| ---------------------------------------- | --------- |
| Gris principal                           | `#2C3E50` |
| Gris de línea/acento                     | `#64748B` |
| Gris claro para cabecera de tabla        | `#F3F4F6` |
| Texto principal                          | `#1F2937` |
| Texto alternativo                        | `#374151` |
| Bordes                                   | `#D1D5DB` |
| Fondo claro alterno                      | `#F9FAFB` |
| Fondo claro de bloque                    | `#F3F4F6` |
| Fondo código oscuro, solo si se solicita | `#1F2937` |
| Borde código oscuro, solo si se solicita | `#374151` |

Regla actual del proyecto:

> Los bloques Markdown de código con triple backtick deben usar fondo claro, borde lateral izquierdo y fuente monoespaciada. El tema oscuro queda como alternativa opcional, no como estilo base.

---

## 1.4 Tamaño de página

Usar **A4** como estándar principal.

Motivos:

* Es estándar internacional.
* Funciona bien en Colombia, Europa y la mayoría de flujos técnicos.
* Mantiene buena relación de ancho para tablas.
* Es más portable que Letter cuando se comparten documentos fuera de EE. UU.

Configuración recomendada:

```text
Formato: A4
Márgenes: 2.5 cm
Orientación: vertical por defecto
Orientación horizontal: solo para tablas muy anchas, si se solicita
```

---

## 1.5 Tipografías base

Usar tipografías disponibles o razonablemente reemplazables en Windows, Linux y macOS.

### 1.5.1 Texto normal

Orden recomendado:

```css
font-family: Arial, "Liberation Sans", "DejaVu Sans", sans-serif;
```

Motivo:

* Arial está en Windows y macOS.
* Liberation Sans suele estar disponible en Linux.
* DejaVu Sans suele estar disponible en entornos Linux/headless.
* Todas tienen lectura clara para documentación técnica.

### 1.5.2 Texto monoespaciado

Orden recomendado:

```css
font-family: Consolas, "Liberation Mono", "DejaVu Sans Mono", "Courier New", monospace;
```

Motivo:

* Consolas funciona bien en Windows.
* Liberation Mono y DejaVu Sans Mono son buenas alternativas Linux.
* Courier New es fallback universal.

---

## 1.6 Reglas Markdown que deben respetarse

| Markdown fuente            | Resultado esperado                   |
| -------------------------- | ------------------------------------ |
| `# Título`                 | Heading 1 real                       |
| `## Título`                | Heading 2 real                       |
| `### Título`               | Heading 3 real                       |
| `#### Título`              | Heading 4 real                       |
| `##### Título`             | Heading 5 real                       |
| `###### Título`            | Heading 6 real                       |
| `**texto**`                | Negrita real                         |
| `_texto_`                  | Itálica real                         |
| `` `codigo` ``             | Texto monoespaciado inline sin fondo |
| Bloque con triple backtick | Bloque de código o verbatim          |
| Tabla Markdown             | Tabla real                           |
| Lista Markdown             | Lista real                           |
| Blockquote                 | Cita visual con barra lateral        |

---

## 1.7 Regla transversal de coloración de sintaxis

Esta regla aplica por igual a las salidas:

* PDF
* DOCX
* HTML intermedio usado para generar PDF

Cuando un bloque Markdown fenced code indique lenguaje:

````markdown
```python
print("hola")
```
````

el pipeline debe intentar aplicar coloración de sintaxis en todos los formatos de salida que lo permitan.

La coloración de sintaxis no debe cambiar la estructura del documento ni el contenido del código. Solo debe aplicar color visual a tokens reconocidos.

Si el lenguaje no se reconoce, si el motor no soporta el lenguaje o si la herramienta de salida tiene limitaciones, el bloque debe mantenerse como texto plano monoespaciado.

Regla de fallback:

```text
Lenguaje reconocido     → aplicar syntax highlighting.
Lenguaje no reconocido  → texto plano monoespaciado.
Sin lenguaje declarado  → texto plano monoespaciado.
Error del highlighter   → texto plano monoespaciado.
```

La exportación nunca debe fallar por no poder colorear sintaxis.

---

### 1.7.1 Lenguajes objetivo soportados

Lista mínima objetivo de 30 lenguajes tradicionales y frecuentes que el pipeline debe intentar reconocer tanto para PDF como para DOCX.

|  # | Lenguaje              | Alias comunes                        |
| -: | --------------------- | ------------------------------------ |
|  1 | Python                | `python`, `py`                       |
|  2 | JavaScript            | `javascript`, `js`                   |
|  3 | TypeScript            | `typescript`, `ts`                   |
|  4 | Java                  | `java`                               |
|  5 | C                     | `c`                                  |
|  6 | C++                   | `cpp`, `c++`, `cc`, `cxx`            |
|  7 | C#                    | `csharp`, `c#`, `cs`                 |
|  8 | SQL                   | `sql`, `postgresql`, `mysql`, `tsql` |
|  9 | PHP                   | `php`                                |
| 10 | Ruby                  | `ruby`, `rb`                         |
| 11 | Go                    | `go`, `golang`                       |
| 12 | Rust                  | `rust`, `rs`                         |
| 13 | Kotlin                | `kotlin`, `kt`                       |
| 14 | Swift                 | `swift`                              |
| 15 | Perl                  | `perl`, `pl`                         |
| 16 | Visual Basic / VB.NET | `vb`, `vbnet`, `visual-basic`        |
| 17 | HTML                  | `html`                               |
| 18 | CSS                   | `css`                                |
| 19 | SCSS                  | `scss`                               |
| 20 | XML                   | `xml`                                |
| 21 | JSON                  | `json`                               |
| 22 | JSONL                 | `jsonl`, `ndjson`                    |
| 23 | YAML                  | `yaml`, `yml`                        |
| 24 | Bash / Shell          | `bash`, `sh`, `shell`                |
| 25 | PowerShell            | `powershell`, `ps1`                  |
| 26 | Dockerfile            | `dockerfile`                         |
| 27 | Makefile              | `makefile`, `make`                   |
| 28 | Markdown              | `markdown`, `md`                     |
| 29 | GraphQL               | `graphql`, `gql`                     |
| 30 | Scala                 | `scala`                              |

Lenguajes adicionales opcionales:

| Lenguaje      | Alias                 |
| ------------- | --------------------- |
| Dart          | `dart`                |
| Objective-C   | `objective-c`, `objc` |
| Groovy        | `groovy`              |
| Terraform HCL | `hcl`, `terraform`    |
| R             | `r`                   |
| Lua           | `lua`                 |
| MATLAB        | `matlab`              |
| COBOL         | `cobol`               |

---

### 1.7.2 Tema claro recomendado para syntax highlighting

Este tema aplica tanto a PDF como a DOCX, salvo que la herramienta tenga limitaciones técnicas.

| Token        | Color     |
| ------------ | --------- |
| Keyword      | `#A626A4` |
| String       | `#0B7285` |
| Number       | `#986801` |
| Comment      | `#64748B` |
| Function     | `#2C3E50` |
| Class / Type | `#B45309` |
| Operator     | `#1F2937` |
| Builtin      | `#0F766E` |
| Error        | `#B91C1C` |
| Plain text   | `#1F2937` |

Regla de contraste:

* El fondo del bloque sigue siendo claro: `#F3F4F6`.
* El borde lateral izquierdo sigue siendo gris: `#64748B`.
* El texto debe mantenerse legible aun si la coloración falla parcialmente.

---

### 1.7.3 Aplicación en PDF

En PDF, la coloración debe aplicarse preferiblemente en el HTML intermedio antes de renderizar.

Flujo recomendado:

```text
Markdown fenced code
→ HTML con tokens coloreados
→ CSS de syntax highlighting
→ PDF
```

Si se usa Pygments, Highlight.js, Prism.js u otro motor, la salida visual debe mantenerse dentro del estilo del proyecto.

El bloque final en PDF debe conservar:

```text
Fondo: #F3F4F6
Borde izquierdo: #64748B (2px)
Fuente: monoespaciada
Padding: cómodo (aumentado en lado izquierdo)
Coloración: si el lenguaje es reconocido
Fallback: texto plano monoespaciado
```

---

### 1.7.4 Aplicación en DOCX

En DOCX, la coloración debe aplicarse dentro de los runs del bloque de código cuando la herramienta lo permita.

Flujo recomendado:

```text
Markdown fenced code
→ detección de lenguaje
→ tokenización
→ runs DOCX con color por token
→ párrafos estilo Code Block
```

El bloque final en DOCX debe conservar:

```text
Estilo: Code Block
Fondo: #F3F4F6
Borde izquierdo: #64748B (2px)
Fuente: Consolas / Liberation Mono / DejaVu Sans Mono
Coloración: si el lenguaje es reconocido y python-docx lo permite
Fallback: texto plano monoespaciado
```

Regla importante:

> Aunque el DOCX no logre una coloración tan fina como el PDF, debe mantener el mismo lenguaje visual: fondo claro, borde lateral, fuente monoespaciada y texto legible.

---

### 1.7.5 Regla para texto plano y verbatim

Cuando el bloque no declare lenguaje:

````markdown
```
src/
  main.js
  App.vue
```
````

debe tratarse como verbatim, no como código coloreado.

Estilo:

```text
Fondo: #F9FAFB o #F3F4F6
Borde lateral izquierdo: #64748B (2px)
Fuente: monoespaciada
Sin coloración de sintaxis
Preservar espacios y saltos de línea
```

---

## 1.8 Estilos para PDF

### 1.8.1 Principios visuales del PDF

El PDF es una versión congelada para lectura.

Reglas:

* Fondo blanco.
* Sin portada compleja salvo solicitud explícita.
* Márgenes amplios.
* Jerarquía visual clara.
* Tablas legibles.
* Código y verbatim distinguibles.
* No usar diseño decorativo innecesario.
* Evitar columnas excesivamente anchas.
* Mantener numeración de páginas si el motor lo permite.

---

### 1.8.2 Encabezados PDF H1-H6

Todos los encabezados principales usan gris `#2C3E50`.

| Nivel | Tamaño recomendado | Peso | Borde inferior     |
| ----- | -----------------: | ---- | ------------------ |
| H1    |              24 pt | Bold | Sí, gris `#64748B` |
| H2    |              20 pt | Bold | Sí, gris `#64748B` |
| H3    |              16 pt | Bold | Sí, gris `#64748B` |
| H4    |              14 pt | Bold | Sí, gris `#64748B` |
| H5    |              12 pt | Bold | Sí, gris `#64748B` |
| H6    |              11 pt | Bold | Sí, gris `#64748B` |

Regla ajustada por decisión visual del proyecto:

> Desde H2 en adelante todos los encabezados deben tener borde inferior. H1 también puede llevar borde inferior cuando funcione como título principal del documento.

---

### 1.8.3 Párrafos PDF

```text
Fuente: Arial / Liberation Sans / DejaVu Sans
Tamaño: 10.5 pt a 11 pt
Color: #1F2937
Interlineado: 1.45 - 1.6
Separación posterior: 0.6em
```

Reglas:

* Mantener alineación izquierda.
* No justificar texto técnico si produce espacios irregulares.
* Respetar negritas e itálicas del Markdown.
* No convertir párrafos en bloques visuales salvo que el Markdown indique blockquote, código o tabla.

---

### 1.8.4 Negritas e itálicas PDF

Reglas Markdown:

```markdown
**texto**
```

Debe convertirse en texto bold real.

```markdown
_texto_
```

Debe convertirse en texto italic real.

No deben quedar visibles los caracteres `**` ni `_`.

---

### 1.8.5 Código inline PDF

Ejemplo Markdown:

```markdown
El archivo `package.json` define los scripts.
```

Resultado esperado:

* `package.json` debe usar fuente monoespaciada.
* No debe tener fondo.
* No debe tener borde.
* No debe alterar el alto de línea de forma excesiva.

Estilo:

```css
code {
  font-family: Consolas, "Liberation Mono", "DejaVu Sans Mono", "Courier New", monospace;
  background: transparent;
  border: none;
  padding: 0;
  color: inherit;
}
```

---

### 1.8.6 Bloques de código PDF

Ejemplo Markdown:

````markdown
```javascript
const app = new Vue({
  el: '#app'
});
```
````

Resultado esperado:

* Fondo claro `#F3F4F6`.
* Borde lateral izquierdo gris `#64748B` (2px).
* Fuente monoespaciada.
* Padding interno cómodo.
* Bordes suaves.
* Mantener indentación.
* Aplicar coloración de sintaxis cuando se reconozca el lenguaje.
* Si no se reconoce el lenguaje, usar texto plano monoespaciado.

La lista de lenguajes soportados y la regla de fallback están definidas en la sección transversal **1.7 Regla transversal de coloración de sintaxis**. Esa misma lista aplica a PDF, DOCX y HTML intermedio.

Estilo base:

```css
pre,
.code-block {
  background: #F3F4F6;
  border-left: 2px solid #64748B;
  border-top: 1px solid #D1D5DB;
  border-right: 1px solid #D1D5DB;
  border-bottom: 1px solid #D1D5DB;
  border-radius: 6px;
  padding: 12px 14px 12px 18px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: normal;
  font-family: Consolas, "Liberation Mono", "DejaVu Sans Mono", "Courier New", monospace;
  font-size: 0.92em;
  line-height: 1.45;
}
```

---

### 1.8.7 Bloques verbatim PDF

Aplica a:

* Árboles de carpetas.
* Salidas de consola simples.
* Pseudoflujos.
* Prompts largos.
* Texto preformateado sin lenguaje de programación.

Estilo:

```css
.verbatim-block {
  background: #F9FAFB;
  border-left: 2px solid #64748B;
  border-top: 1px solid #D1D5DB;
  border-right: 1px solid #D1D5DB;
  border-bottom: 1px solid #D1D5DB;
  border-radius: 6px;
  padding: 12px 14px 12px 18px;
  font-family: Consolas, "Liberation Mono", "DejaVu Sans Mono", "Courier New", monospace;
  white-space: pre-wrap;
}
```

---

### 1.8.8 Tablas PDF

Las tablas deben ser tablas reales en HTML/PDF, no texto simulado.

Reglas:

* Ancho completo cuando sea posible.
* Encabezado con fondo `#F3F4F6`.
* Texto de encabezado bold.
* Bordes `#D1D5DB`.
* Filas alternas `#F9FAFB`.
* Padding cómodo.
* Evitar tablas demasiado anchas.
* En tablas largas, permitir salto de página sin cortar contenido.
* Repetir encabezado si el motor PDF lo soporta.

CSS:

```css
table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
  font-size: 0.95em;
}

thead {
  display: table-header-group;
}

th {
  background: #F3F4F6;
  color: #2C3E50;
  font-weight: 700;
  border: 1px solid #D1D5DB;
  padding: 8px 10px;
  text-align: left;
}

td {
  border: 1px solid #D1D5DB;
  padding: 8px 10px;
  vertical-align: top;
}

tbody tr:nth-child(even) {
  background: #F9FAFB;
}
```

---

### 1.8.9 Blockquotes PDF

```css
blockquote {
  background: #F9FAFB;
  border-left: 2px solid #64748B;
  border-top: 1px solid #D1D5DB;
  border-right: 1px solid #D1D5DB;
  border-bottom: 1px solid #D1D5DB;
  border-radius: 6px;
  margin: 1rem 0;
  padding: 10px 14px;
  color: #374151;
}
```

---

### 1.8.10 Links PDF

```css
a {
  color: #2C3E50;
  text-decoration: underline;
  text-decoration-thickness: 0.06em;
}
```

---

### 1.8.11 Encabezado y pie PDF

Si se usa encabezado:

```text
Documento corto en gris medio
```

Si se usa pie:

```text
Página X de Y
```

No saturar encabezado ni pie.

---

## 1.9 Estilos para DOCX

### 1.9.1 Principios DOCX

El DOCX es una versión editable.

Reglas obligatorias:

* Usar estilos reales de Word.
* No simular encabezados con texto grande manual.
* No simular tablas con texto alineado.
* No simular secciones con líneas de texto.
* Usar tablas reales.
* Usar estilos de párrafo reales.
* Usar estilos de carácter para inline code si la herramienta lo permite.
* Renderizar y verificar visualmente antes de entregar.

---

### 1.9.2 Página DOCX

```text
Tamaño: A4
Márgenes: 2.5 cm
Orientación: vertical
Fuente normal: Arial 11 pt
Interlineado: 1.15 a 1.4
Color texto: #1F2937
```

---

### 1.9.3 Estilos Word obligatorios

| Estilo Word                | Uso                                     |
| -------------------------- | --------------------------------------- |
| Normal                     | Párrafo base                            |
| Heading 1                  | H1 Markdown                             |
| Heading 2                  | H2 Markdown                             |
| Heading 3                  | H3 Markdown                             |
| Heading 4                  | H4 Markdown                             |
| Heading 5                  | H5 Markdown                             |
| Heading 6                  | H6 Markdown                             |
| Code Inline                | Texto entre backticks dentro de párrafo |
| Code Block                 | Bloque fenced code                      |
| Verbatim Block             | Bloque preformateado no código          |
| Table Grid / estilo propio | Tablas reales                           |
| Quote                      | Blockquotes                             |

---

### 1.9.4 Encabezados DOCX H1-H6

Reglas:

* Todos los Heading 1-6 usan gris `#2C3E50`.
* Todos en bold.
* Heading 2 a Heading 6 llevan borde inferior gris `#64748B`.
* Heading 1 puede llevar borde inferior cuando funciona como título principal.

Tabla recomendada:

| Nivel | Estilo Word | Tamaño | Color     | Borde inferior                  |
| ----- | ----------- | -----: | --------- | ------------------------------- |
| H1    | Heading 1   |  24 pt | `#2C3E50` | Opcional / recomendado en título |
| H2    | Heading 2   |  20 pt | `#2C3E50` | Sí                              |
| H3    | Heading 3   |  16 pt | `#2C3E50` | Sí                              |
| H4    | Heading 4   |  14 pt | `#2C3E50` | Sí                              |
| H5    | Heading 5   |  12 pt | `#2C3E50` | Sí                              |
| H6    | Heading 6   |  11 pt | `#2C3E50` | Sí                              |

---

### 1.9.5 Párrafo base DOCX

```text
Estilo: Normal
Fuente: Arial
Tamaño: 11 pt
Color: #1F2937
Espaciado posterior: 6 pt
Interlineado: 1.15 o 1.3
```

---

### 1.9.6 Código inline DOCX

Ejemplo:

```markdown
Ejecutar `npm run serve`.
```

Resultado esperado:

* `npm run serve` queda como texto monoespaciado.
* No usa fondo.
* No usa borde.
* No debe afectar todo el párrafo.

Estilo:

```text
Nombre recomendado: Code Inline
Tipo: character style
Fuente: Consolas
Tamaño: igual al texto base o 10.5 pt
Fondo: ninguno
Color: igual al texto normal
```

---

### 1.9.7 Bloques de código DOCX

Resultado esperado:

* Bloque real con párrafos de estilo `Code Block`.
* Fondo claro `#F3F4F6`.
* Borde izquierdo gris `#64748B` (2px).
* Fuente monoespaciada.
* Indentación preservada.
* Syntax highlighting si la conversión DOCX lo permite.
* Fallback a texto plano monoespaciado.

La lista de lenguajes soportados y la regla de fallback están definidas en la sección transversal **1.7 Regla transversal de coloración de sintaxis**. En DOCX la coloración debe aplicarse mediante runs cuando la herramienta lo permita; si no, se mantiene texto plano monoespaciado.

Estilo:

```text
Nombre recomendado: Code Block
Tipo: paragraph style
Fuente: Consolas
Tamaño: 10 pt
Fondo: #F3F4F6
Borde izquierdo: #64748B (2px)
Borde general: #D1D5DB
Espaciado interno: aproximado con sangría y espaciado
```

---

### 1.9.8 Verbatim DOCX

Igual que bloque de código, pero sin coloración de sintaxis.

Usar para:

* Árbol de carpetas.
* Salida de consola sin lenguaje.
* Prompts largos.
* Texto plano preformateado.

---

### 1.9.9 Tablas DOCX

Reglas obligatorias:

* Deben ser tablas reales de Word.
* No deben ser texto separado por pipes.
* No deben ser imágenes.
* Deben permitir edición futura.

Estilo:

```text
Cabecera:
- Fondo #F3F4F6
- Texto #2C3E50
- Bold

Cuerpo:
- Bordes #D1D5DB
- Filas alternas #F9FAFB
- Padding interno razonable
- Alineación vertical arriba
```

---

### 1.9.10 Negritas e itálicas DOCX

Reglas Markdown:

```markdown
**texto**
```

Debe convertirse a run bold real.

```markdown
_texto_
```

Debe convertirse a run italic real.

---

### 1.9.11 Blockquotes DOCX

Estilo esperado:

```text
Nombre recomendado: Quote
Fondo: #F9FAFB
Borde izquierdo: #64748B
Borde general: #D1D5DB
Texto: #374151
```

---

# Sección 2: Pipeline de exportación

## 2.1 Objetivo del pipeline

El pipeline debe permitir generar documentos consistentes desde Markdown hacia:

* HTML intermedio autocontenido
* PDF final para lectura
* DOCX final para edición

La regla central es:

```text
Markdown fuente -> HTML intermedio con CSS -> PDF
                -> DOCX con estructuras reales
```

---

## 2.2 Diagrama general del pipeline

```text
┌────────────────────────────┐
│  Archivo Markdown fuente   │
│  ejemplo: documento.md     │
└─────────────┬──────────────┘
              │
              │ Leer Markdown sin modificar contenido
              ▼
┌────────────────────────────┐
│ Parser Markdown             │
│ - headings                  │
│ - párrafos                  │
│ - listas                    │
│ - tablas                    │
│ - inline code               │
│ - fenced code blocks        │
│ - bold / italic             │
└─────────────┬──────────────┘
              │
              ├─────────────────────────────────────┐
              │                                     │
              ▼                                     ▼
┌────────────────────────────┐       ┌────────────────────────────┐
│ HTML intermedio             │       │ DOCX                       │
│ - CSS completo              │       │ - Heading 1-6 reales        │
│ - tablas HTML reales        │       │ - tablas Word reales        │
│ - code blocks               │       │ - estilos Word reales       │
│ - syntax highlighting       │       │ - runs bold/italic/code     │
└─────────────┬──────────────┘       └─────────────┬──────────────┘
              │                                    │
              │ WeasyPrint / wkhtmltopdf            │ Render DOCX para QA
              ▼                                    ▼
┌────────────────────────────┐       ┌────────────────────────────┐
│ PDF final                   │       │ PNG QA DOCX                 │
│ - lectura                   │       │ - revisión visual           │
│ - paginado                  │       │ - detectar tablas rotas     │
│ - estilos CSS aplicados     │       │ - detectar clipping         │
└─────────────┬──────────────┘       └────────────────────────────┘
              │
              │ Render PDF para QA
              ▼
┌────────────────────────────┐
│ PNG QA PDF                  │
│ - revisión página a página  │
│ - detectar cortes           │
│ - detectar tablas ilegibles │
└────────────────────────────┘
```

---

## 2.3 Skills o capacidades requeridas

En ChatGPT o una IA generativa con herramientas, pedir explícitamente estas capacidades.

### 2.3.1 Lectura de archivos

Uso:

* Leer Markdown fuente.
* Leer guía de estilos.
* Leer archivos previos si se va a conservar convención.

---

### 2.3.2 Capacidad de generación DOCX

Uso:

* Crear Word editable.
* Crear secciones reales.
* Crear tablas reales.
* Aplicar estilos Word reales.
* Renderizar el DOCX para revisión visual.

---

### 2.3.3 Capacidad de generación PDF

Uso:

* Crear PDF a partir de HTML intermedio.
* Usar CSS completo.
* Validar visualmente mediante render a PNG.

---

### 2.3.4 Capacidad de ejecución Python

Uso:

* Ejecutar script de conversión.
* Generar HTML, PDF, DOCX.
* Crear carpetas temporales.
* Verificar archivos finales.

---

### 2.3.5 Capacidad de revisión visual

Uso:

* Renderizar DOCX a PNG.
* Renderizar PDF a PNG.
* Revisar páginas.
* Corregir y repetir.

---

## 2.4 Archivos temporales y finales

### 2.4.1 Entrada

```text
/mnt/data/documento.md
```

### 2.4.2 Temporales

```text
/mnt/data/build/
  01-source-normalized.md
  02-document.html
  03-styles.css
  04-highlight.css
  qa-docx/
    page-1.png
    page-2.png
    ...
  qa-pdf/
    page-1.png
    page-2.png
    ...
```

### 2.4.3 Finales

Ejemplo con nombre base `07-lista-final-fases`:

```text
/mnt/data/07-lista-final-fases.html
/mnt/data/07-lista-final-fases.docx
/mnt/data/07-lista-final-fases.pdf
```
