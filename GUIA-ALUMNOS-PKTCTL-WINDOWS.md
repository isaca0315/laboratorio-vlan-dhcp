# Guía paso a paso: Claude controla Packet Tracer (pktctl) en Windows

Al final, Claude Desktop (o OpenCode) podrá leer y cambiar tu red de **Cisco Packet Tracer
9.0.1** mediante el servidor `pktctl`.

Esta guía usa solo dos cosas:

1. **El JSON** del servidor, en la configuración de Claude Desktop u OpenCode.
2. **El registro `pktctl.pta`**, cargado en Packet Tracer una sola vez.

No necesitas ningún módulo `.pts`. Esa parte es de otro servidor (`packet-tracer-mcp`).

> Sigue **un solo cliente**: Claude Desktop (Paso 3A) **o** OpenCode (Paso 3B).
> No hace falta hacer los dos.

## Índice

1. Descargar `pktctl`
2. Generar el secreto
3. Configurar el cliente: **3A** Claude Desktop o **3B** OpenCode
4. Generar el registro `pktctl.pta`
5. Cargar el registro en Packet Tracer
6. Comprobar la conexión
7. Primer ejemplo

---

## Antes de empezar

- Windows 10 u 11.
- Packet Tracer **9.0.1** instalado.
- Claude Desktop con sesión iniciada, o OpenCode instalado.
- Conexión a Internet para descargar.
- No necesitas permisos de administrador.

Abre **PowerShell** (botón Inicio → escribe `PowerShell` → Intro). Lo usarás en varios pasos.

---

## Paso 1: descargar `pktctl`

1. Abre la página de releases: <https://github.com/TantiE100/pktctl/releases/tag/v0.2.2>
2. Descarga **`pktctl-0.2.2-x86_64-pc-windows-msvc.zip`**.
3. Abre el zip con el Explorador de archivos. Verás **una carpeta** llamada
   `pktctl-0.2.2-x86_64-pc-windows-msvc`. Entra en ella.
4. En PowerShell, copia el ejecutable a tu carpeta de trabajo. Cambia `<ruta-del-zip>` por la
   carpeta donde extrajiste el zip (por ejemplo `C:\Users\<usuario>\Downloads`):

   ```powershell
   New-Item -ItemType Directory -Force "$env:USERPROFILE\pktctl" | Out-Null
   Copy-Item "<ruta-del-zip>\pktctl-0.2.2-x86_64-pc-windows-msvc\pktctl.exe" "$env:USERPROFILE\pktctl\pktctl.exe" -Force
   ```

   Si prefieres el Explorador, copia **solo** `pktctl.exe` a `C:\Users\<usuario>\pktctl\`.

5. Comprueba que responde:

   ```powershell
   & "$env:USERPROFILE\pktctl\pktctl.exe" --version
   ```

   **Debe responder:** `pktctl 0.2.2`

**Si no aparece `pktctl 0.2.2`:** revisa que el archivo esté exactamente en
`C:\Users\<usuario>\pktctl\pktctl.exe`. Si Windows Defender lo bloquea, avisa a tu profesor.

---

## Paso 2: generar el secreto

El secreto es una clave aleatoria que comparten Claude y Packet Tracer. Tiene que ser el
**mismo** en todos los sitios donde lo pegues.

1. En PowerShell, pega estas tres líneas y pulsa Intro:

   ```powershell
   $bytes = New-Object byte[] 24
   [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
   $secret = -join ($bytes | ForEach-Object { $_.ToString('x2') })
   $secret
   ```

2. Verás una cadena de **48 caracteres** (letras `a`–`f` y números), por ejemplo:
   `3f9a1c0e7b2d4685a1f0e9c8d7b6a5f4e3d2c1b0a9f8e7d6`
3. **Cópiala** en un archivo del Bloc de notas (por ejemplo `secreto.txt` en el escritorio).
   La necesitarás en el Paso 3 y en el Paso 4.

**Importante:** la variable `$secret` solo existe en esa ventana de PowerShell. Si la cierras,
genera un secreto nuevo y cámbialo en todos los sitios donde lo pegaste.

> Estas tres líneas no se han ejecutado todavía en Windows. Si dan error, avisa a tu profesor
> antes de seguir.

---

## Paso 3: configurar el cliente

Haz **solo una** de estas dos opciones.

### Paso 3A: Claude Desktop

1. Cierra Claude Desktop del todo: icono de la bandeja → clic derecho → **Quit**.
2. Abre el Explorador de archivos, escribe `%APPDATA%\Claude` en la barra de direcciones y pulsa Intro.
   Si la carpeta no existe, créala con ese nombre.
3. Abre `claude_desktop_config.json` con el Bloc de notas. Si no existe, créalo con este contenido:

   ```json
   {
     "mcpServers": {}
   }
   ```

   > Si no encuentras la carpeta, abre Claude Desktop → **Settings → Developer → Edit Config**.
   > Ese botón abre el mismo archivo.

4. Dentro de `mcpServers`, añade la entrada `pktctl`. Sustituye `<usuario>` por tu nombre de
   usuario de Windows y `PEGA-AQUI-TU-SECRETO` por el secreto del Paso 2. Las barras invertidas
   van dobles:

   ```json
   {
     "mcpServers": {
       "pktctl": {
         "command": "C:\\Users\\<usuario>\\pktctl\\pktctl.exe",
         "args": [],
         "env": {
           "PKTCTL_APP_ID": "dev.pktctl",
           "PKTCTL_SECRET": "PEGA-AQUI-TU-SECRETO"
         }
       }
     }
   }
   ```

   Si ya tenías otros servidores, añade solo la entrada `pktctl` con su coma y no borres los demás.

5. Guarda el archivo (Ctrl+S).
6. Comprueba que el JSON es correcto. En PowerShell:

   ```powershell
   Get-Content "$env:APPDATA\Claude\claude_desktop_config.json" -Raw | ConvertFrom-Json | Out-Null
   "JSON correcto"
   ```

   Si aparece un error, revisa comas, llaves y comillas. No pegues el archivo en webs externas:
   contiene tu secreto.

7. Abre Claude Desktop de nuevo. Sigue con el **Paso 4**.

### Paso 3B: OpenCode

1. Abre `%USERPROFILE%\.config\opencode\opencode.json` con el Bloc de notas. Si no existe, crea la
   carpeta `%USERPROFILE%\.config\opencode\` y el archivo con este contenido:

   ```json
   {
     "$schema": "https://opencode.ai/config.json"
   }
   ```

2. Añade `pktctl` dentro de `mcp.servers`. Sustituye `<usuario>` y `PEGA-AQUI-TU-SECRETO`:

   ```json
   {
     "$schema": "https://opencode.ai/config.json",
     "mcp": {
       "servers": {
         "pktctl": {
           "type": "local",
           "command": ["C:\\Users\\<usuario>\\pktctl\\pktctl.exe"],
           "environment": {
             "PKTCTL_APP_ID": "dev.pktctl",
             "PKTCTL_SECRET": "PEGA-AQUI-TU-SECRETO"
           }
         }
       }
     }
   }
   ```

   Si ya tenías otras claves en el archivo, añade solo `"mcp"` y no dupliques `"$schema"`.

3. Guarda el archivo.
4. Comprueba que OpenCode ve el servidor. En PowerShell:

   ```powershell
   opencode mcp list
   ```

   **Debe mostrar:** `pktctl` con estado `connected`. Si no aparece, revisa el JSON y la ruta
   de `pktctl.exe`.

5. Sigue con el **Paso 4**.

---

## Paso 4: generar el registro `pktctl.pta`

Packet Tracer solo acepta aplicaciones registradas. El archivo `pktctl.pta` es ese registro.

### Camino A: que Claude lo genere (recomendado)

1. Abre Claude Desktop (o OpenCode) y escribe en una conversación nueva:

   > Ejecuta setup_exapp.

2. Claude responderá con la ruta del archivo `pktctl.pta` y con los pasos para registrarlo.
   Comprueba que el archivo existe. En PowerShell:

   ```powershell
   Test-Path "$env:USERPROFILE\.config\pktctl\pktctl.pta"
   ```

   **Debe responder:** `True`

Si `setup_exapp` responde `could not find Packet Tracer's meta tool`, usa el **Camino B**.

### Camino B: manual con `meta.exe` (plan de respaldo)

1. **Busca `meta.exe`.** Abre el Explorador, entra en la carpeta donde instalaste Packet Tracer
   (normalmente `C:\Program Files\Cisco Packet Tracer 9.0.1\`) y busca `meta.exe` con el
   buscador. Anota la ruta completa.
2. En PowerShell, ejecuta lo siguiente. Pega tu secreto del Paso 2 en la línea de `$secret` y
   cambia `<ruta a meta.exe>` por la ruta del punto anterior:

   ```powershell
   $secret = "PEGA-AQUI-TU-SECRETO"
   $dir = "$env:USERPROFILE\pktctl-registro"
   New-Item -ItemType Directory -Force $dir | Out-Null
   Set-Location $dir
   Invoke-WebRequest -Uri "https://raw.githubusercontent.com/TantiE100/pktctl/v0.2.2/crates/pktctl/assets/pktctl-exapp.xml" -OutFile "pktctl-exapp.xml"
   (Get-Content "pktctl-exapp.xml") -replace "REPLACE_WITH_YOUR_SECRET", $secret | Set-Content "pktctl-exapp.xml"
   & "<ruta a meta.exe>" "pktctl.pta" "pktctl-exapp.xml"
   Remove-Item "pktctl-exapp.xml"
   New-Item -ItemType Directory -Force "$env:USERPROFILE\.config\pktctl" | Out-Null
   Copy-Item "pktctl.pta" "$env:USERPROFILE\.config\pktctl\pktctl.pta" -Force
   ```

3. Comprueba el resultado:

   ```powershell
   Test-Path "$env:USERPROFILE\.config\pktctl\pktctl.pta"
   ```

   **Debe responder:** `True`

El XML contiene el secreto en claro; por eso se borra en cuanto se cifra. No lo compartas.

> El Camino B se ha probado en Linux con el mismo procedimiento, pero **no en Windows**.
> Si `meta.exe` no aparece en tu instalación, avisa a tu profesor.

---

## Paso 5: cargar el registro en Packet Tracer

Este paso se hace **una sola vez**.

1. Abre **Cisco Packet Tracer 9.0.1**.
2. Ve a **Extensions → IPC → Configure Apps**.
3. Pulsa **Add**.
4. Selecciona el archivo `C:\Users\<usuario>\.config\pktctl\pktctl.pta`.

   > La carpeta `.config` puede estar oculta. Si el diálogo no la muestra, escribe la ruta
   > completa en el campo **Nombre de archivo**.

5. Pulsa **Ok**.
6. **Cierra Packet Tracer con File → Exit.** No lo cierres con la X ni con el Administrador de
   tareas: solo al salir normalmente Packet Tracer guarda la lista de aplicaciones registradas.
7. Vuelve a abrir Packet Tracer.

---

## Paso 6: comprobar la conexión

Con Packet Tracer abierto, pide a Claude (o a OpenCode):

> Comprueba el estado de Packet Tracer.

**Respuesta correcta:** `connected: true`, con la versión de Packet Tracer y el número de
dispositivos y enlaces abiertos.

| Lo que ves | Qué significa | Qué hacer |
|------------|---------------|-----------|
| `connected: true` | Todo está bien | Sigue con el Paso 7 |
| `Packet Tracer is not reachable` | Packet Tracer no está abierto | Ábrelo y repite la pregunta |
| `rejected app id dev.pktctl` | El registro no está cargado o el secreto no coincide | Revisa el Paso 5 y que el secreto de tu cliente sea el mismo que el del `.pta` |
| `Cannot launch ExApp...` al pulsar **Launch** | Es lo esperado | No pulses Launch sobre `pktctl`; ignora el aviso y usa `status` |

---

## Paso 7: primer ejemplo

Pide a Claude:

> Crea una red nueva con un router 2911, un switch 2960-24TT y dos PC-PT. Conecta cada PC al
> switch y el router al switch. Guarda la red como `prueba.pkt`.

Mira la ventana de Packet Tracer: deben aparecer los equipos y los cables. Después pide:

> Lista los dispositivos y los enlaces de la red abierta.

---

## Qué no hacer

- **No pulses Launch** sobre `pktctl` dentro de Packet Tracer.
- **No cierres Packet Tracer** con la X ni con el Administrador de tareas justo después de cargar
  el registro: usa **File → Exit**.
- **No actives** **Allow Remote Applications** en **Extensions → IPC → Options**.
- **No compartas** tu archivo de configuración ni tu `.pta`: contienen el secreto.
- **No cambies el secreto** sin generar un `.pta` nuevo y cargarlo en Packet Tracer.

---

## Problemas típicos

| Síntoma | Causa y solución |
|---------|------------------|
| `pktctl 0.2.2` no aparece en el Paso 1 | El `.exe` no está en `C:\Users\<usuario>\pktctl\`, o el nombre no es exacto. |
| Claude no muestra ninguna herramienta de Packet Tracer | JSON inválido, ruta mal escrita o Claude no se cerró con **Quit**. Repite el Paso 3A. |
| `rejected app id` aunque cargaste el `.pta` | Packet Tracer no se cerró con **File → Exit** después de cargar el registro. Repite el Paso 5. |
| `does not have the necessary privilege` | El `.pta` es de una versión antigua. Repite el Paso 4 y carga el nuevo. |
| `could not find Packet Tracer's meta tool` | Usa el Camino B del Paso 4. |
| `opencode mcp list` muestra `failed` | Revisa la ruta de `pktctl.exe` y el JSON de OpenCode (Paso 3B). |

---

## Desinstalar

1. Quita la entrada `pktctl` de `claude_desktop_config.json` o de `opencode.json` y reinicia el cliente.
2. En Packet Tracer, quita el registro desde **Extensions → IPC → Configure Apps**, si la lista lo
   permite. No lo hemos probado en Windows.
3. Borra las carpetas `%USERPROFILE%\pktctl` y `%USERPROFILE%\.config\pktctl`.
