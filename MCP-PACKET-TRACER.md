# MCP de Cisco Packet Tracer (pktctl)

Guía para que **Claude Desktop** o **Hermes Agent** construyan, configuren y
prueben las redes de este laboratorio dentro de **Cisco Packet Tracer 9.0.1**,
usando el servidor MCP [`pktctl`](https://github.com/TantiE100/pktctl).

Para que funcione hacen falta solo dos cosas:

1. **La configuración** del servidor en el cliente (JSON en Claude Desktop, YAML
   en Hermes).
2. **El registro `pktctl.pta`**, cargado en Packet Tracer una sola vez.

El repositorio incluye [`pktctl.pta`](pktctl.pta) ya generado. No depende del
sistema operativo: sirve igual en Windows, Linux y macOS.

> `pktctl` no reemplaza a Packet Tracer: lo maneja. Necesita la ventana de Packet
> Tracer abierta y el `.pkt` cargado. No funciona en modo headless.

## Índice

1. [Estado de la verificación](#estado-de-la-verificación)
2. [Qué instala](#qué-instala)
3. [Descargar pktctl](#paso-1-descargar-pktctl)
4. [Elegir el secreto](#paso-2-elegir-el-secreto)
5. [Configurar el cliente](#paso-3-configurar-el-cliente)
6. [Conseguir el registro `.pta`](#paso-4-conseguir-el-registro-pta)
7. [Cargar el registro en Packet Tracer](#paso-5-cargar-el-registro-en-packet-tracer)
8. [Comprobar la conexión](#paso-6-comprobar-la-conexión)
9. [Construir el laboratorio desde cero](#paso-7-construir-el-laboratorio-desde-cero)
10. [Seguridad](#seguridad)
11. [Problemas típicos](#problemas-típicos)
12. [Actualizar y desinstalar](#actualizar-y-desinstalar)

## Estado de la verificación

La guía se probó **en Linux**. La parte de Windows está escrita con la misma
lógica y con los datos del zip oficial, pero **no se ha ejecutado en Windows**.

| Paso | Linux | Windows |
|------|-------|---------|
| Descarga del release y comprobación SHA256 | Probado | Zip descargado y comprobado (SHA256 correcto); no instalado |
| `pktctl --version` | Probado (`pktctl 0.2.2`) | No probado |
| Estructura del zip (`pktctl.exe` dentro de una carpeta) | Probado | Probado en el zip; no extraído en Windows |
| Servidor MCP con la configuración de Claude Desktop (`initialize`, 72 herramientas, `status`) | Probado | No probado |
| Respuesta con secreto incorrecto (`rejected app id`) | Probado | No probado |
| `setup_exapp` | **Falla** en esta instalación (ver Paso 4) | No probado |
| Registro manual con `meta` (el `.pta` sale byte a byte igual al registrado) | Probado | No probado |
| `.pta` del repositorio (mismo procedimiento, secreto de práctica) | Generado y comprobado (478 bytes, determinista) | No cargado en Packet Tracer |
| Ejercicios del Paso 7 (construcción desde cero) | Valores esperados comprobados en `Sesion-A-IPv4.pkt` y `Sesion-B-IPv6.pkt`; A-IPv6 y B-IPv4 salen de las guías | Construcción completa no ejecutada |
| Bloques JSON y YAML de esta guía | JSON validados; YAML probado con `hermes mcp test` | JSON: mismos bloques; YAML: no probado |
| Configuración de Hermes (`mcp_servers`, 72 herramientas) | Probado con un `HERMES_HOME` temporal | No probado |
| Claude Desktop cargando el servidor en la ventana | Pendiente: hay que reiniciar Claude Desktop | No probado |
| Generación del secreto en PowerShell | No aplica | No probado |

## Qué instala

| Componente | Ruta / valor |
|------------|--------------|
| Binario | `~/.local/bin/pktctl` (Linux) · `C:\Users\<usuario>\pktctl\pktctl.exe` (Windows), v0.2.2 |
| Registro ExApp | [`pktctl.pta`](pktctl.pta) (el mismo archivo en cualquier sistema) · copia en `~/pktctl.pta` o `%USERPROFILE%\pktctl.pta` |
| Secreto IPC | `~/.config/pktctl/secret` (Linux, modo 600, **no versionar**) |
| App ID | `dev.pktctl` |
| Config de Hermes | `hermes config edit` → `mcp_servers.pktctl` en `~/.hermes/config.yaml` (Linux/macOS) · `%LOCALAPPDATA%\hermes\config.yaml` (Windows) |
| Config de Claude Desktop | `~/.config/Claude/claude_desktop_config.json` (Linux) · `%APPDATA%\Claude\claude_desktop_config.json` (Windows) |

`pktctl` habla con Packet Tracer por **PTMP**, el protocolo nativo de
aplicaciones externas (puertos `39000`–`39009`). Expone 72 herramientas:
topología, cables, CLI de IOS, DHCP/PCs, servidores, simulación, actividades y
acceso directo a la API IPC.

> Sigue **un solo cliente**: Claude Desktop (Paso 3A) **o** Hermes Agent (Paso 3B).
> No hace falta hacer los dos.

## Paso 1: descargar pktctl

Requisitos: Packet Tracer **9.0.1**, un cliente MCP y conexión a Internet para
descargar. En Linux hace falta glibc **2.39** o superior (Ubuntu 24.04 / Debian 13).

### Windows

1. Descarga `pktctl-0.2.2-x86_64-pc-windows-msvc.zip` desde los
   [releases](https://github.com/TantiE100/pktctl/releases/tag/v0.2.2).
2. Abre el zip. Dentro hay **una carpeta** `pktctl-0.2.2-x86_64-pc-windows-msvc`
   con `pktctl.exe`. Crea `C:\Users\<usuario>\pktctl\` y copia **solo**
   `pktctl.exe` ahí. La ruta final debe ser exactamente
   `C:\Users\<usuario>\pktctl\pktctl.exe`.

   ```powershell
   New-Item -ItemType Directory -Force "$env:USERPROFILE\pktctl" | Out-Null
   Copy-Item "<ruta-del-zip>\pktctl-0.2.2-x86_64-pc-windows-msvc\pktctl.exe" "$env:USERPROFILE\pktctl\pktctl.exe" -Force
   ```

3. Comprueba que arranca:

   ```powershell
   & "$env:USERPROFILE\pktctl\pktctl.exe" --version
   ```

   **Debe responder** `pktctl 0.2.2`. Si Windows Defender o SmartScreen lo
   bloquea, la excepción la decide el equipo del alumno; no lo he comprobado en
   Windows.

### Linux

```sh
VERSION=0.2.2
curl -fsSLO "https://github.com/TantiE100/pktctl/releases/download/v$VERSION/pktctl-$VERSION-x86_64-unknown-linux-gnu.tar.gz"
curl -fsSLO "https://github.com/TantiE100/pktctl/releases/download/v$VERSION/SHA256SUMS"
sha256sum -c SHA256SUMS --ignore-missing
tar -xzf "pktctl-$VERSION-x86_64-unknown-linux-gnu.tar.gz"
install -m 755 "pktctl-$VERSION-x86_64-unknown-linux-gnu/pktctl" ~/.local/bin/pktctl
pktctl --version
```

En macOS el archivo es `pktctl-$VERSION-x86_64-apple-darwin.tar.gz`
(o `aarch64-apple-darwin` en Apple Silicon).

## Paso 2: elegir el secreto

El secreto es una clave que comparten el cliente y Packet Tracer. Tiene que ser
**el mismo** en todos los sitios donde lo pegues.

### Opción rápida: el secreto de práctica

Si vas a usar el [`pktctl.pta`](pktctl.pta) del repositorio, no generes nada.
El secreto con el que se creó es:

```text
eb9a6706129c3c6d40979a5540e110e76773eba055862c33
```

Es una clave **publicada a propósito** para las prácticas. No la reutilices para
otra cosa y no la cambies: si la cambias, el `.pta` del repositorio deja de
coincidir y Packet Tracer responde `rejected app id`.

### Opción propia: generar el secreto

Solo si vas a generar tu propio `.pta` (Paso 4, opciones B o C).

**Windows**, en PowerShell:

```powershell
$bytes = New-Object byte[] 24
[System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
$secret = -join ($bytes | ForEach-Object { $_.ToString('x2') })
$secret
```

Devuelve **48 caracteres** hexadecimales. Guárdalo en un archivo temporal: lo
necesitas en el Paso 3 y en el Paso 4.

> La variable `$secret` solo existe en esa ventana de PowerShell. Si la cierras,
> genera un secreto nuevo y cámbialo en todos los sitios donde lo pegaste.

**Linux:**

```sh
SECRET=$(openssl rand -hex 24)
```

El App ID es `dev.pktctl`. Puedes usar otro con formato de dominio inverso, pero
entonces cámbialo en todas las configs y en el registro.

## Paso 3: configurar el cliente

Haz **solo una** de estas dos opciones.

### Paso 3A: Claude Desktop

1. Cierra Claude Desktop del todo: icono de la bandeja del sistema → clic
   derecho → **Quit**. Cerrar la ventana no basta.
2. Abre el Explorador de archivos, escribe `%APPDATA%\Claude` en la barra de
   direcciones y pulsa Intro. Si la carpeta no existe, créala con ese nombre.
3. Abre `claude_desktop_config.json` con el Bloc de notas. Si no existe, créalo
   con este contenido:

   ```json
   {
     "mcpServers": {}
   }
   ```

   > Si no encuentras la carpeta: Claude Desktop → **Settings → Developer →
   > Edit Config**. Ese botón abre el mismo archivo.

4. Dentro de `mcpServers`, añade la entrada `pktctl`. Sustituye `<usuario>` por
   tu nombre de usuario. Las barras invertidas van dobles:

   ```json
   {
     "mcpServers": {
       "pktctl": {
         "command": "C:\\Users\\<usuario>\\pktctl\\pktctl.exe",
         "args": [],
         "env": {
           "PKTCTL_APP_ID": "dev.pktctl",
           "PKTCTL_SECRET": "eb9a6706129c3c6d40979a5540e110e76773eba055862c33"
         }
       }
     }
   }
   ```

   Ese es el secreto de práctica del Paso 2. Si generaste uno propio, ponlo en
   `PKTCTL_SECRET`: tiene que coincidir con el `.pta` que cargues.

   Si ya tenías otros servidores, añade solo la entrada `pktctl` con su coma y no
   borres las demás.

5. Guarda el archivo y comprueba que el JSON es válido:

   ```powershell
   Get-Content "$env:APPDATA\Claude\claude_desktop_config.json" -Raw | ConvertFrom-Json | Out-Null
   "JSON correcto"
   ```

   Si aparece un error, revisa comas, llaves y comillas. No pegues el archivo en
   webs externas: contiene tu secreto.

6. Abre Claude Desktop de nuevo.

**Linux:** el mismo bloque, en `~/.config/Claude/claude_desktop_config.json` y con
barras normales:

```json
{
  "mcpServers": {
    "pktctl": {
      "command": "/home/<usuario>/.local/bin/pktctl",
      "args": [],
      "env": {
        "PKTCTL_APP_ID": "dev.pktctl",
        "PKTCTL_SECRET": "eb9a6706129c3c6d40979a5540e110e76773eba055862c33"
      }
    }
  }
}
```

### Paso 3B: Hermes Agent

Hermes Agent (Nous Research) guarda los servidores MCP en `mcp_servers`, dentro
de `config.yaml`. La forma segura de abrir el archivo correcto es:

```sh
hermes config edit
```

También puedes editarlo a mano:

- Linux/macOS: `~/.hermes/config.yaml`
- Windows (instalación por script): `%LOCALAPPDATA%\hermes\config.yaml`

Añade la entrada `pktctl` con tu ruta y el secreto de práctica. En YAML, las
comillas simples dejan las barras invertidas tal cual:

```yaml
mcp_servers:
  pktctl:
    command: 'C:\Users\<usuario>\pktctl\pktctl.exe'
    args: []
    env:
      PKTCTL_APP_ID: 'dev.pktctl'
      PKTCTL_SECRET: 'eb9a6706129c3c6d40979a5540e110e76773eba055862c33'
```

En Linux/macOS cambia solo `command`:

```yaml
    command: '/home/<usuario>/.local/bin/pktctl'
```

Si ya tenías otros servidores bajo `mcp_servers`, añade `pktctl` con su sangría
y no borres los demás.

Comprueba que Hermes lo carga:

```sh
hermes mcp list
hermes mcp test pktctl
```

**Debe aceptar la conexión** y listar las herramientas. Después entra en
`hermes chat` y pide **«ejecuta status de pktctl»**: la respuesta correcta es
`connected: true`. Si editaste el archivo con Hermes ya abierto, ejecuta
`/reload-mcp` dentro de la sesión.

> Si `hermes mcp test` falla con `rejected app id`, el problema es el Paso 4 o 5
> (registro `.pta` o secreto), no la configuración YAML.

## Paso 4: conseguir el registro `.pta`

Packet Tracer solo acepta aplicaciones registradas. El registro es un archivo
`pktctl.pta` que se crea **una vez**. Hay tres formas.

### Opción A: el `.pta` del repositorio (recomendado)

Descarga [`pktctl.pta`](pktctl.pta) y guárdalo en tu carpeta de usuario. Está
creado con el secreto de práctica del Paso 2 y el App ID `dev.pktctl`.

No depende del sistema operativo: el **mismo archivo** sirve en Windows, Linux y
macOS.

**Windows**, en PowerShell:

```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/isaca0315/laboratorio-vlan-dhcp/main/pktctl.pta" -OutFile "$env:USERPROFILE\pktctl.pta"
Test-Path "$env:USERPROFILE\pktctl.pta"
```

**Linux:**

```sh
curl -fsSL https://raw.githubusercontent.com/isaca0315/laboratorio-vlan-dhcp/main/pktctl.pta -o ~/pktctl.pta
ls -l ~/pktctl.pta
```

Comprueba que pesa **478 bytes**. Es un archivo binario y cifrado: no se puede
editar a mano ni revisar su contenido. Si el profesor cambia el secreto, pide el
`.pta` nuevo.

### Opción B: `setup_exapp` (desde el cliente)

Pide al agente **«ejecuta setup_exapp»**. Escribe el `.pta` en `PKTCTL_SETUP_DIR`
o, por defecto, en `~/.config/pktctl/` (Linux) o `%USERPROFILE%\.config\pktctl\`
(Windows). Comprueba que existe:

```powershell
Test-Path "$env:USERPROFILE\.config\pktctl\pktctl.pta"
```

**Debe responder** `True`. Si responde `could not find Packet Tracer's meta
tool`, usa la opción C.

> **En Linux con la instalación de esta clase no funciona.** `setup_exapp` solo
> busca `meta` en `<carpeta>/extensions/`, y en esta instalación `meta` está en
> `bin/` dentro de un AppImage montado en `/tmp` (la ruta cambia en cada
> arranque). Por eso se responde con la opción C.

### Opción C: manual con `meta` (probada en Linux)

`meta` es la herramienta de Packet Tracer que cifra la plantilla XML. Cuesta un
minuto y no depende de `setup_exapp`.

1. **Localiza `meta`** dentro de la carpeta de instalación de Packet Tracer.
   - Linux (AppImage): `bin/meta`. Búscalo con
     `find <carpeta de PT> -name meta -type f`.
   - Windows: el archivo se llama `meta.exe`. Búscalo en
     `C:\Program Files\Cisco Packet Tracer 9.0.1\` (normalmente en una
     subcarpeta `extensions` o `bin`). Anota la ruta completa.
2. **Prepara la plantilla, cámbiale el secreto y cifra.**

   *Linux:*

   ```sh
   mkdir -p ~/pktctl-registro && cd ~/pktctl-registro
   curl -fsSL https://raw.githubusercontent.com/TantiE100/pktctl/v0.2.2/crates/pktctl/assets/pktctl-exapp.xml -o pktctl-exapp.xml
   SECRET=$(cat ~/.config/pktctl/secret)
   sed -i "s|REPLACE_WITH_YOUR_SECRET|$SECRET|" pktctl-exapp.xml
   "<ruta a meta>" pktctl.pta pktctl-exapp.xml
   rm pktctl-exapp.xml
   mkdir -p ~/.config/pktctl && cp pktctl.pta ~/.config/pktctl/pktctl.pta
   ```

   *Windows (PowerShell, sin probar en Windows):*

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

   **Debe responder** `True`.

El XML contiene el secreto en claro; por eso se borra justo después de cifrarlo.
No lo compartas.

## Paso 5: cargar el registro en Packet Tracer

Este paso se hace **una sola vez**.

1. Abre **Cisco Packet Tracer 9.0.1**.
2. Ve a **Extensions → IPC → Configure Apps → Add** y selecciona el `.pta`:
   - Opción A: `%USERPROFILE%\pktctl.pta` o `~/pktctl.pta`.
   - Opciones B y C: `%USERPROFILE%\.config\pktctl\pktctl.pta` o
     `~/.config/pktctl/pktctl.pta`.

   Si el diálogo no muestra archivos ocultos, escribe la ruta completa a mano.
3. Pulsa **Ok**. La app aparece en la lista como `pktctl`.
4. Cierra Packet Tracer con **File → Exit**. No lo cierres con la X, con `kill`
   ni con el Administrador de tareas: solo al salir normalmente guarda la lista
   de aplicaciones registradas.
5. Vuelve a abrir Packet Tracer.

> Si Packet Tracer se cierra mal después de registrar, el registro se pierde:
> repite el paso y vuelve a salir con **File → Exit**.

> **No pulses «Launch» sobre `pktctl`.** Verás
> `Cannot launch ExApp. The executable file name or location may be incorrect...`.
> Es normal: el cliente MCP lanza `pktctl` y se conecta por TCP. El registro está
> bien si la app aparece en la lista y `status` responde `connected: true`.

## Paso 6: comprobar la conexión

Con Packet Tracer abierto, pide al cliente:

> Comprueba el estado de Packet Tracer.

**Respuesta correcta:** `connected: true`, con la versión de Packet Tracer y el
número de dispositivos y enlaces abiertos.

| Lo que ves | Qué significa | Qué hacer |
|------------|---------------|-----------|
| `connected: true` | Todo está bien | Sigue con el Paso 7 |
| `Packet Tracer is not reachable` | Packet Tracer no está abierto, o IPC usa un puerto fuera de `39000`–`39009` | Ábrelo y revisa **Extensions → IPC → Options** |
| `rejected app id dev.pktctl` | El registro no está cargado o el secreto no coincide | Repite el Paso 5 y usa el mismo secreto en el cliente y en el `.pta` |
| `Cannot launch ExApp...` al pulsar **Launch** | Es lo esperado | No pulses Launch; usa `status` |

Los logs del servidor están en `%APPDATA%\Claude\logs\mcp-server-pktctl.log`
(Windows) o `~/.config/Claude/logs/mcp-server-pktctl.log` (Linux). Esa convención
de nombres es la de los otros servidores de esta instalación; en `pktctl` todavía
no la he visto aparecer.

## Paso 7: construir el laboratorio desde cero

Ocho ejercicios cortos, **en orden**, para **montar el laboratorio con el MCP**
partiendo de una red vacía. Se repiten dos veces por sesión: una en IPv4 y otra
en IPv6.

| | Sesión A | Sesión B |
|---|---|---|
| Guía | `SESION-A.md` y `SESION-A-IPV6.md` | `SESION-B.md` y `SESION-B-IPV6.md` |
| LAN por sede | una | VLAN 10 (usuarios) y 20 (invitados) |
| Enrutamiento | rutas estáticas | OSPF / OSPFv3 |
| Ejercicio 7 | el enlace cortado **rompe** el ping | el tráfico **se desvía** por R3 |

Los cuatro `.pkt` de `packet-tracer/` son la **solución**. Ábrelos solo al final,
para comparar: si el agente los lee antes, copia y el ejercicio no prueba nada.
Las configuraciones de `config/` y `config/ipv6/` también son de la Sesión B.

| Tarea | IPv4 | IPv6 |
|-------|------|------|
| Ver direcciones | `show ip interface brief` | `show ipv6 interface brief` |
| Ver rutas | `show ip route` | `show ipv6 route` |
| Ver DHCP | `show ip dhcp binding` | `show ipv6 dhcp binding` |
| Ver vecinos | `show ip ospf neighbor` | `show ipv6 ospf neighbor` |

**Cómo se pide.** Un prompt útil tiene cuatro partes: qué construir, con qué
datos exactos, cómo comprobarlo y qué **no** tocar. Escribe tu predicción antes
de enviarlo: el objetivo es detectar si el agente se equivoca.

> Si aplicas las configuraciones de `config/`, los routers piden contraseña de
> consola y de `enable`: `cisco`. Sin ese dato el agente se queda en `Password:`.

### 1. Topología vacía

**Predice:** cuántos equipos hay al terminar y cómo se llaman.

> Empieza una red nueva. Coloca 3 routers 2911 llamados R1, R2 y R3; 3 switches
> 2960-24TT llamados SW1, SW2 y SW3; y 9 PCs llamados PC-A1…A3, PC-B1…B3 y
> PC-C1…C3. No cables ni configures nada. Al terminar, lista cada equipo con su
> modelo.

**Comprueba:** 15 equipos de red con esos nombres y modelos, y 0 enlaces. Si
aparece `Power Distribution Device0`, no lo cuentes: es un accesorio de Packet
Tracer. Un nombre cambiado rompe los prompts siguientes.

### 2. Cableado exacto

**Predice:** cuántos cables tendrá cada router y cada switch.

> Cablea los 15 enlaces con cable straight-through y los puertos exactos:
> R1 Gi0/0→SW1 Fa0/1, R2 Gi0/0→SW2 Fa0/1, R3 Gi0/0→SW3 Fa0/1; PC-A1/A2/A3
> Fa0→SW1 Fa0/2/3/4 y lo mismo en B y C; R1 Gi0/1→R2 Gi0/1,
> R2 Gi0/2→R3 Gi0/1, R3 Gi0/2→R1 Gi0/2. No configures nada. Dime cuántos
> enlaces hay y qué puertos usa cada router.

**Comprueba:** 15 enlaces; 3 por router (`Gi0/0`, `Gi0/1`, `Gi0/2`) y 4 por
switch (`Fa0/1` y `Fa0/2-4`). Las luces rojas son normales hasta el `no
shutdown`.

### 3. Switches y VLAN (solo Sesión B)

**Predice:** qué puertos quedan en VLAN 10, cuáles en VLAN 20 y cuál es trunk.

> Configura SW1, SW2 y SW3: VLAN 10 `USUARIOS` y VLAN 20 `INVITADOS`. Fa0/2 y
> Fa0/3 en acceso a VLAN 10, Fa0/4 en acceso a VLAN 20, y Fa0/1 en trunk con
> native VLAN 10 y allowed 10,20. No toques los routers. Muéstrame `show vlan
> brief` y `show interfaces trunk` de SW1.

**Comprueba:** VLAN 10 y 20 activas; Fa0/2-3 en 10 y Fa0/4 en 20; trunk con
native 10 y allowed 10,20. Si la native se queda en 1, los PCs de VLAN 10 no
reciben DHCP.

En la Sesión A salta al ejercicio 4: los switches van de fábrica, sin VLANs.

### 4. Direccionamiento de los routers

**Predice:** la IP de cada interfaz y qué dos subredes no pueden solaparse.

> Asigna a R1, R2 y R3 las direcciones del plan de tu guía y levanta las
> interfaces. En la Sesión B añade `Gi0/0.20` con `encapsulation dot1Q 20`.
> Antes de ejecutar, dime la IP de cada interfaz. No configures DHCP ni rutas.

**Comprueba (Sesión A):** R1 `.1/28`, `.49/30`, `.58/30`; R2 `.17/28`, `.50/30`,
`.53/30`; R3 `.33/28`, `.54/30`, `.57/30`, todas `up/up`. En IPv6: R1
`2001:DB8:13:0::1`, `:48::1`, `:56::2`; R2 `:16::1`, `:48::2`, `:52::1`; R3
`:32::1`, `:52::2`, `:56::1`.

**Comprueba (Sesión B):** lo anterior más `Gi0/0.20`: R1 `.65`, R2 `.81`, R3
`.97`; en IPv6 `:64::1`, `:80::1`, `:96::1`.

### 5. DHCP

**Predice:** cuántas concesiones habrá y en qué rango cae cada PC.

> Configura cada router como servidor DHCP de sus LAN conectadas: un pool por
> LAN y, en la Sesión B, uno por VLAN. Pon los 9 PCs en DHCP, ejecuta
> `fast_forward` y muéstrame las concesiones y el `ipconfig` de PC-A1 y PC-C1.
> No asignes IP fija a ningún PC.

**Comprueba:** una concesión por PC, dentro de la subred de su sede. En la
Sesión A: LAN-A `.6–.14`, LAN-B `.22–.30`, LAN-C `.38–.46`. En la B: VLAN 10
`.6–.14`, `.22–.30`, `.38–.46` y VLAN 20 `.70–.78`, `.86–.94`, `.102–.110`.
En IPv6 no hay rangos: cada PC recibe una dirección del `/64` de su LAN y el
gateway llega por RA (link-local).

### 6. Enrutamiento

**Predice:** cuántas rutas añade cada router y por qué vecino sale el paquete.

*Sesión A (estáticas):*

> Configura las rutas estáticas de tu guía en los tres routers, usando como
> siguiente salto la IP del vecino, no la propia. No uses ruta por defecto.
> Muéstrame la tabla de R1 y la entrada que usa para `192.168.2.32/28`
> (`2001:DB8:13:32::/64` en IPv6).

**Comprueba:** 2 rutas `S` por router. En R1, LAN-C por `.57` (`Gi0/2`); en IPv6,
`S 2001:DB8:13:32::/64` por `2001:DB8:13:56::1`. Si el siguiente salto es la IP
propia, el paquete se pierde.

*Sesión B (OSPF):*

> Configura OSPF área 0 en los tres routers (OSPFv3 en IPv6) y deja el enlace
> R2–R3 como respaldo con costo 100. Ejecuta `fast_forward` y muéstrame los
> vecinos y la ruta de R2 a la LAN-C.

**Comprueba:** 2 vecinos en `FULL` por router. R2 llega a LAN-C por R1 con
métrica 2; por el respaldo sería 101. Si el respaldo no está en 100, el tráfico
puede tomar el camino largo.

### 7. Fallo controlado

**Predice:** si el ping sobrevive y, si sobrevive, por dónde pasa.

*Sesión A:*

> Desde PC-B1 haz ping a PC-C1 y un tracert. Luego apaga `R2 Gi0/2`, ejecuta
> `fast_forward` y repite el ping. Después vuelve a encender la interfaz. No
> guardes.

**Comprueba:** el ping **falla**. La ruta estática no se adapta: ese es su
límite.

*Sesión B:*

> Desde PC-B1 haz ping a PC-C1 y un tracert. Luego apaga `R1 Gi0/1`, ejecuta
> `fast_forward` y repite el tracert. Después vuelve a encender la interfaz. No
> guardes.

**Comprueba:** el ping **sigue funcionando** y el camino pasa por R3
(`2001:DB8:13:52::2` en IPv6); la ruta de R2 a LAN-C marca métrica 101. Al
encender, vuelve por R1 y baja a 3. Esa es la redundancia de la Sesión B.

### 8. Diagnóstico y entrega

**Prepara el fallo:** cambia tú una IP (por ejemplo, el gateway de una LAN) y no
digas cuál.

> Hay un fallo de conectividad entre PC-B1 y PC-C1. Diagnostícalo leyendo las
> interfaces y las tablas de rutas, explica la causa y propón la corrección. No
> cambies nada hasta que lo confirme. Cuando lo confirme, corrígelo, comprueba
> con un ping y guarda el laboratorio con un nombre propio, por ejemplo
> `packet-tracer/entrega-A-ipv4-TUNOMBRE.pkt`.

**Comprueba:** encuentra la interfaz cambiada, propone la IP correcta, el ping
vuelve y el archivo se guarda con tu nombre. Deben quedar los 15 enlaces y la
tabla de rutas completa. No sobrescribas el `.pkt` de referencia.

> Repite la lista completa en IPv6 y en la otra sesión. Cada vuelta empieza con
> `new_network`: no reutilices el archivo anterior.

### Solución de los ejercicios

Los cuatro `.pkt` de `packet-tracer/` son la solución. Compáralos solo al final:

| Archivo | Contenido |
|---------|-----------|
| `packet-tracer/Sesion-A-IPv4.pkt` | 3 sedes, DHCPv4 por LAN, rutas estáticas |
| `packet-tracer/Sesion-A-IPv6.pkt` | Igual, con DHCPv6 y rutas estáticas IPv6 |
| `packet-tracer/Sesion-B-IPv4.pkt` | VLAN 10/20, DHCP por VLAN, OSPF 10 con respaldo costo 100 |
| `packet-tracer/Sesion-B-IPv6.pkt` | Igual, con DHCPv6 por VLAN y OSPFv3 |

Comprobado en los cuatro: 15 enlaces, direcciones por DHCP/DHCPv6 en los 9 PCs,
ping entre sedes y tabla de rutas correcta. En la Sesión B se apagó el uplink de
R1 y el tráfico pasó por el enlace de respaldo (costo 100), y volvió al camino
primario al encenderlo.

Notas de la API que conviene conocer:

- `configure_host_ipv6` solo admite `static`, `auto` (SLAAC) y `off`. Para
  DHCPv6 stateful hay que usar IPC:
  `getProcess("Dhcpv6MainProcess")` → `enableDhcpClient("CLIENT_ENABLED_VIA_DHCP", "FastEthernet0", "", false, true, false)`.
  El nombre del proceso distingue mayúsculas: `DHCPv6MainProcess` no existe.
- `configure_ios` corta el lote después de `no shutdown` y de
  `logging synchronous`. Parte los comandos en trozos de una interfaz o usa
  `run_cli` en modo `global`/`current`.
- Después de `enable secret cisco`, pasa `enable_password: "cisco"` a `run_cli`.

### Herramientas que más vas a usar

| Herramienta | Para qué |
|-------------|----------|
| `status` | Saber si PT responde y qué red hay abierta |
| `list_devices`, `list_links`, `list_ports` | Descubrir nombres y puertos antes de actuar |
| `add_device`, `add_link`, `remove_device` | Construir o corregir la topología |
| `run_cli` | Escribir comandos IOS en routers y switches |
| `configure_host`, `configure_host_ipv6`, `configure_dhcp_server` | Direcciones, DHCP y servicios de los hosts |
| `run_host_command` | Ejecutar `ping`, `tracert` o `ipconfig` en un PC |
| `fast_forward` | Acelerar STP, DHCP y convergencia de routing |
| `save_network`, `open_network` | Guardar o abrir `.pkt` |
| `screenshot` | Capturar la topología para el entregable |
| `describe_ipc`, `call_ipc` | Llegar a cualquier método de la API IPC |

## Seguridad

- El secreto da **control total** de Packet Tracer. El de práctica
  (`eb9a…c33`) está publicado en este repositorio a propósito: sirve solo para
  las prácticas. No lo reutilices en un equipo o una red que no sean del
  laboratorio.
- El secreto queda en claro en la config del cliente (`claude_desktop_config.json`
  y el `config.yaml` de Hermes) y en el XML temporal del registro manual.
  Mantén esos archivos privados: el `config.yaml` de Hermes también puede
  contener claves de API.
- En **Extensions → IPC → Options**, deja **Allow Remote Applications**
  desactivado salvo que lo necesites: PT escucha en todas las interfaces.
- Antes de pedir cambios masivos, guarda una copia del `.pkt`. El agente puede
  sobrescribir el archivo abierto.

## Problemas típicos

| Síntoma | Causa y solución |
|---------|------------------|
| `pktctl 0.2.2` no aparece en el Paso 1 | El `.exe` no está en `C:\Users\<usuario>\pktctl\`, o el nombre no es exacto. |
| `Packet Tracer is not reachable` | PT cerrado, o IPC en un puerto fuera de `39000`–`39009`. Abre PT y revisa **Extensions → IPC → Options**. |
| `Cannot launch ExApp...` al pulsar **Launch** | Esperado. El cliente MCP lanza `pktctl`, no PT. Ignora el aviso y usa `status`. |
| `rejected app id dev.pktctl` | Falta cargar el `.pta`, el secreto no coincide, o PT no salió con **File → Exit**. Repite el Paso 5 con el mismo secreto. |
| `could not find Packet Tracer's meta tool` (`setup_exapp`) | Usa la opción B del Paso 4. |
| `does not have the necessary privilege` | El `.pta` se registró con una plantilla vieja. Genera y carga el de la plantilla `v0.2.2`. |
| Claude Desktop no muestra las herramientas | JSON inválido (coma sobrante), ruta inexistente o Claude no se cerró con **Quit**. Revisa el Paso 3A y los logs. |
| Claude Desktop no arranca `pktctl` en Windows | La ruta del `command` debe ser absoluta y con `\\`. Claude no siempre hereda el `PATH`. |
| `hermes mcp test pktctl` muestra `failed` | Revisa la ruta del binario y `PKTCTL_APP_ID` / `PKTCTL_SECRET`. |
| Los cambios no aparecen | Ejecuta `fast_forward` y vuelve a consultar; STP/DHCP/OSPF tardan en converger. |
| PT se cuelga o no responde | Cierra PT normalmente y vuelve a abrirlo. No hace falta reinstalar `pktctl`. |

## Actualizar y desinstalar

**Windows:** para actualizar, sustituye `pktctl.exe` por el de un zip nuevo. Para
desinstalar, borra `C:\Users\<usuario>\pktctl\`, la carpeta
`%USERPROFILE%\.config\pktctl`, y la entrada `pktctl` de
`claude_desktop_config.json` o de `config.yaml`. En Packet Tracer, quita el
registro desde **Extensions → IPC → Configure Apps** (si la lista lo permite; no
lo he probado en Windows).

**Linux:**

```sh
# Actualizar el binario (ajusta VERSION si hay una más nueva)
VERSION=0.2.2
curl -fsSLO "https://github.com/TantiE100/pktctl/releases/download/v$VERSION/pktctl-$VERSION-x86_64-unknown-linux-gnu.tar.gz"
tar -xzf "pktctl-$VERSION-x86_64-unknown-linux-gnu.tar.gz"
install -m 755 "pktctl-$VERSION-x86_64-unknown-linux-gnu/pktctl" ~/.local/bin/pktctl

# Desinstalar
rm ~/.local/bin/pktctl
rm -r ~/.config/pktctl
# y borra mcp_servers.pktctl de ~/.hermes/config.yaml
# y mcpServers.pktctl de ~/.config/Claude/claude_desktop_config.json
```

Al cambiar de versión de Packet Tracer, revisa las notas de `pktctl`: la versión
validada es **9.0.1**. Otras versiones pueden funcionar, pero no están
garantizadas.
