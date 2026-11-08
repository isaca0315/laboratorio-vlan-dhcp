# Guía para alumnos: Claude controla Packet Tracer en Windows (packet-tracer-mcp)

Con esta guía, Claude Desktop puede crear topologías en **Cisco Packet Tracer 9.0.1**,
configurar los equipos, ejecutar `ping` y revisar la red. Lo hace a través del servidor
[`packet-tracer-mcp`](https://github.com/Mats2208/MCP-Packet-Tracer), que no es el mismo que
`pktctl` de [`MCP-PACKET-TRACER.md`](MCP-PACKET-TRACER.md).

> **Usa una sola de las dos guías** sobre la misma red. Los dos servidores hablan con el
> mismo Packet Tracer y no está probado que funcionen a la vez.

## Antes de empezar

- Windows 10 u 11, con Packet Tracer **9.0.1** instalado.
- Claude Desktop instalado y con sesión iniciada.
- Conexión a Internet para la descarga.
- Esta guía no necesita permisos de administrador.

## Qué está probado y qué no

Esta guía se comprobó en **Linux** con los mismos comandos y configuraciones. Los
pasos de Windows vienen de la documentación del proyecto y de la misma lógica, pero **no se
han ejecutado en Windows**.

| Paso | Linux | Windows |
|------|-------|---------|
| Servidor arranca con la configuración de Claude Desktop y responde a `initialize` | Probado | No probado |
| 96 herramientas en la versión publicada (0.11.0) | Probado | No probado |
| `pt_list_devices` funciona sin Packet Tracer abierto | Probado | No probado |
| Sin Packet Tracer: `pt_bridge_status` responde «NOT connected» | Probado | No probado |
| Instalación de la skill (`install-skill`) | Probado | No probado |
| Variante `packet-tracer-mcp[ui]` | Probada (se instala y arranca) | No probada |
| Extensión añadida desde **Configure PT Script Modules → Add…** | No probado (requiere la interfaz de PT) | No probado |
| Ejemplo completo: construir y hacer ping en PT | No probado | No probado |

## Paso 1: instalar uv

`uv` trae su propio Python y ejecuta el servidor. Abre **PowerShell** y pega:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Cierra PowerShell, ábrelo de nuevo y comprueba:

```powershell
uv --version
```

Si dice que no reconoce `uv`, cierra y abre PowerShell otra vez. Comprueba también
que existe el ejecutable que usaremos en el Paso 5:

```powershell
Test-Path "$env:USERPROFILE\.local\bin\uvx.exe"
```

Debe responder `True`. Si responde `False`, repite la instalación de `uv`.

## Paso 2: comprobar que el servidor descarga

Esto descarga el servidor y muestra su ayuda, sin abrir Packet Tracer:

```powershell
uvx --from "packet-tracer-mcp[ui]" packet-tracer-mcp install-skill --help
```

La primera vez tarda porque descarga las dependencias. Debe mostrar
`usage: pt-mcp install-skill ...`.

## Paso 3: descargar la extensión y comprobar su huella

La extensión **MCP Control Center** (`MCP-Control-Center.pts`) es el módulo que Packet Tracer
ejecuta para recibir las órdenes de Claude. Descárgala de la última versión oficial:

1. Abre <https://github.com/Mats2208/MCP-Packet-Tracer/releases/latest>.
2. Descarga **`MCP-Control-Center.pts`** (en la versión 0.11.0 pesa 28 666 bytes).

Comprueba la huella en PowerShell:

```powershell
Get-FileHash "$env:USERPROFILE\Downloads\MCP-Control-Center.pts" -Algorithm SHA256
```

Compara el resultado con el valor que publica tu profesor. Para la versión 0.11.0, en la
comprobación del 8 de noviembre de 2026, el valor fue:

```text
d2ef03725f0c7128583a8b2a5f6a5e84c477f1ba125c28123da9a9930981f1d0
```

> Si la release cambia, el valor cambia. Compara siempre con el que indica tu profesor,
> no con este si ya hay una versión nueva. El proyecto no publica su propia huella, así que
> esta comprobación solo confirma que tu copia es idéntica a la que se verificó en clase.

## Paso 4: añadir la extensión a Packet Tracer

No hace falta copiar nada a `Program Files`. Se añade desde el menú de Packet Tracer:

1. Abre **Cisco Packet Tracer 9.0.1**.
2. Ve a **Extensions → Scripting → Configure PT Script Modules**.
3. Pulsa **Add…**, selecciona `MCP-Control-Center.pts` y confirma.
4. Si Packet Tracer pregunta si quieres habilitar el módulo, responde **Yes**.
5. Ve a **Extensions → MCP BUILDER**. Se abre la ventana **MCP Control Center**.

Deja esa ventana abierta mientras trabajas. Si Packet Tracer se pone lento, **minimízala**;
no la pongas solo detrás de la ventana de Packet Tracer.

> Esta ruta está descrita en la documentación del proyecto para Windows y Linux. No la hemos
> probado en Windows.

## Paso 5: configurar Claude Desktop

1. Cierra Claude Desktop del todo: icono de la bandeja del sistema → **Quit**.
2. Abre el Explorador de archivos, escribe `%APPDATA%\Claude` en la barra de direcciones
   y pulsa Intro.
3. Abre `claude_desktop_config.json` con el Bloc de notas. Si no existe, créalo con este
   contenido:

   ```json
   {
     "mcpServers": {}
   }
   ```

4. Añade la entrada `packet-tracer` dentro de `mcpServers`. Sustituye `<usuario>` por tu
   nombre de usuario de Windows. Las barras invertidas van dobles y la ruta debe ser completa.
   JSON no expande variables como `%USERPROFILE%`, así que escribe la ruta entera:

   ```json
   {
     "mcpServers": {
       "packet-tracer": {
         "command": "C:\\Users\\<usuario>\\.local\\bin\\uvx.exe",
         "args": ["--from", "packet-tracer-mcp[ui]", "packet-tracer-mcp", "--stdio"]
       }
     }
   }
   ```

   Si ya tienes otros servidores, añade solo la entrada `packet-tracer` con su coma; no
   borres las demás.

5. Guarda el archivo y abre Claude Desktop de nuevo.

> La variante `[ui]` permite que el agente abra las ventanas de los equipos en Packet Tracer
> (solo en Windows). Sin ella el servidor funciona igual para construir y configurar.

## Paso 6: comprobar la conexión

Con Packet Tracer abierto y la ventana **MCP Control Center** abierta, escribe en Claude:

> Comprueba el estado de Packet Tracer.

Claude debe usar `pt_bridge_status`. Con la extensión activa, el estado debe ser conectado
(la documentación del proyecto indica «Bridge ACTIVE and CONNECTED»).

Si todavía no has abierto la ventana, verás:

```text
Packet Tracer is NOT connected over any channel.
```

Es lo esperado: abre **Extensions → MCP BUILDER** y repite la pregunta.

Puedes probar el servidor **sin** Packet Tracer abierto con:

> Lista los routers que puedo usar en Packet Tracer.

## Paso 7: primer ejemplo

Con la conexión comprobada, pide:

> Crea una red con 1 switch y 2 PCs, impleméntala en Packet Tracer y haz ping entre los dos PCs.

Claude planifica la red, la valida, la envía a Packet Tracer y comprueba el resultado con un
`ping` real. Mira la ventana de Packet Tracer mientras trabaja.

## Si usas Claude Code (opcional)

La skill del proyecto (`install-skill`) está pensada para Claude Code y OpenCode, y se
instala en `~/.claude/skills` (`%USERPROFILE%\.claude\skills`). Con Claude Code, el registro
es:

```powershell
claude mcp add --scope user --transport stdio packet-tracer "--" uvx --from "packet-tracer-mcp[ui]" packet-tracer-mcp --stdio
```

Las comillas en `"--"` son obligatorias en PowerShell; sin ellas, Claude responde
`unknown option '-m'`. Después instala la skill:

```powershell
uvx packet-tracer-mcp install-skill
```

Y reinicia Claude Code o ejecuta `/reload-skills`.

> En Claude Desktop no está comprobado que lea la skill desde esa carpeta. Empieza sin ella y
> revisa si las respuestas son correctas.

## Solución de problemas

| Síntoma | Qué hacer |
|---------|-----------|
| `uv` no se reconoce | Cierra y abre PowerShell. Si sigue igual, repite el Paso 1. |
| Claude Desktop no muestra ninguna herramienta de Packet Tracer | Revisa el JSON (una coma sobrante lo rompe), la ruta a `uvx.exe` (Paso 5) y que cerraste Claude con **Quit**. |
| La primera consulta tarda mucho o da timeout | Es la primera descarga de dependencias. Espera un minuto y repite la consulta. |
| `Packet Tracer is NOT connected` | Abre **Extensions → MCP BUILDER** y deja la ventana abierta. |
| No aparece **Extensions → MCP BUILDER** | Repite el Paso 4 con el archivo `.pts` correcto. |
| Aparece una ventana roja `An error occurred on line N` | Tienes una extensión antigua. Descarga la última versión de la release y añádela otra vez. |
| Packet Tracer va lento con la ventana del MCP abierta | Minimiza la ventana **MCP Control Center**. |
| La pestaña Terminal dice que no encuentra el token | Abre Claude con el servidor activo, espera a que conecte y vuelve a abrir la ventana de MCP BUILDER. |
| `unknown option '-m'` (solo Claude Code) | Pon las comillas en `"--"` como se indica arriba. |

## Seguridad

- Usa el MCP en tu equipo y para las prácticas de la asignatura.
- La extensión ejecuta código dentro de Packet Tracer. Instala **solo** el `.pts` de la
  release oficial, con la huella que indica tu profesor.
- El servidor puede ejecutar JavaScript arbitrario dentro de Packet Tracer
  (`pt_send_raw`). Si Claude propone algo que no entiendes, no lo ejecutes.
- El token del puente es un secreto local. Está en
  `%LOCALAPPDATA%\packet-tracer-mcp\bridge_token`. No lo compartas ni lo pegues en el chat.
- Las exportaciones y capturas se guardan en `%USERPROFILE%\PacketTracerMCP`.

## Desinstalar

1. Quita la entrada `packet-tracer` de `claude_desktop_config.json` y reinicia Claude Desktop.
2. Quita el módulo desde **Extensions → Scripting → Configure PT Script Modules**, en el mismo
   diálogo donde lo añadiste (no lo hemos probado).
3. Elimina el servidor:

   ```powershell
   uv tool uninstall packet-tracer-mcp
   ```

4. Si quieres borrar los datos locales, elimina `%USERPROFILE%\PacketTracerMCP` y
   `%LOCALAPPDATA%\packet-tracer-mcp`.

---

## Para el profesor

- **Versión:** la guía describe `packet-tracer-mcp` **0.11.0** (la que publica PyPI y la
  release `v0.11.0`). Esa versión expone **96 herramientas**. El `main` del repositorio tiene 98
  porque incluye `pt_canvas_info` y `pt_auto_layout`, que aún no están publicados.
- **Huella de referencia:** `d2ef03725f0c7128583a8b2a5f6a5e84c477f1ba125c28123da9a9930981f1d0`
  (`MCP-Control-Center.pts`, descargado el 8 de noviembre de 2026). Si cambia la release,
  vuelve a calcular la huella, verifícala y actualiza este valor.
- **Lo que no puede comprobar la guía por sí sola:** la extensión solo se puede revisar
  dentro de Packet Tracer. El `.pts` es binario, así que no se puede auditar su código
  desde el archivo descargado; el proyecto publica las fuentes en `EXTENSION/`, pero no
  demuestra que el `.pts` se compile a partir de ellas.
- **Sobre Windows:** la prueba completa de la guía (extensión, Claude Desktop y ejemplo de
  ping) debe hacerse en un equipo Windows antes de la clase.
