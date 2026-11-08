# MCP de Cisco Packet Tracer (pktctl)

Guía para que un agente de **Claude Desktop** u **OpenCode** construya,
configure y pruebe las redes de este laboratorio dentro de **Cisco Packet
Tracer 9.0.1** usando el servidor MCP
[`pktctl`](https://github.com/TantiE100/pktctl).

> `pktctl` no reemplaza a Packet Tracer: lo maneja. Necesita la ventana de
> Packet Tracer abierta y el `.pkt` cargado. No funciona en modo headless.

## Estado de la verificación

Esta guía se probó **en Linux**. La parte de Windows está escrita con la misma
lógica y con los datos del zip oficial, pero **no se ha ejecutado en Windows**.

| Paso | Linux | Windows |
|------|-------|---------|
| Descarga del release y comprobación SHA256 | Probado | Zip descargado y comprobado (SHA256 correcto); no instalado |
| `pktctl --version` | Probado (`pktctl 0.2.2`) | No probado |
| Estructura del zip (`pktctl.exe` dentro de una carpeta) | Probado | Probado en el zip; no extraído en Windows |
| Servidor MCP con la configuración de Claude Desktop (`initialize`, 72 herramientas, `status`) | Probado | No probado |
| Respuesta con secreto incorrecto (`rejected app id`) | Probado | No probado |
| `setup_exapp` | **Falla** en esta instalación (ver abajo) | No probado |
| Registro manual con `meta` (el `.pta` sale byte a byte igual al registrado) | Probado | No probado |
| Bloques JSON de esta guía | Probados (4 de 4) | Probados (son los mismos) |
| `opencode mcp list` → `pktctl connected` | Probado | No probado |
| Claude Desktop cargando el servidor en la ventana | Pendiente: hay que reiniciar Claude Desktop | No probado |
| Generación del secreto en PowerShell | No aplica | No probado |

## Qué instala esta configuración

| Componente | Ruta / valor |
|------------|--------------|
| Binario | `~/.local/bin/pktctl` (Linux) · `C:\Users\<usuario>\pktctl\pktctl.exe` (Windows), v0.2.2 |
| Registro ExApp | `~/.config/pktctl/pktctl.pta` (Linux) · `%USERPROFILE%\.config\pktctl\pktctl.pta` (Windows) |
| Secreto IPC | `~/.config/pktctl/secret` (Linux, modo 600, **no versionar**) |
| App ID | `dev.pktctl` |
| Config de OpenCode | `~/.config/opencode/opencode.json` → `mcp.servers.pktctl` (Linux) · `%USERPROFILE%\.config\opencode\opencode.json` (Windows) |
| Config de Claude Desktop | `~/.config/Claude/claude_desktop_config.json` (Linux) · `%APPDATA%\Claude\claude_desktop_config.json` (Windows) |

`pktctl` habla con Packet Tracer por **PTMP**, el protocolo nativo de
aplicaciones externas (puertos `39000`–`39009`). Expone 72 herramientas:
topología, cables, CLI de IOS, DHCP/PCs, servidores, simulación, actividades y
acceso directo a la API IPC.

## Instalar pktctl

Requisitos: Packet Tracer **9.0.1** y un cliente MCP (Claude Desktop u
OpenCode). Internet solo para descargar. En Linux hace falta glibc **2.39** o
superior (Ubuntu 24.04 / Debian 13).

### Windows

1. **Descarga** `pktctl-0.2.2-x86_64-pc-windows-msvc.zip` desde los
   [releases](https://github.com/TantiE100/pktctl/releases/tag/v0.2.2).
2. **Extrae el zip.** Dentro hay una carpeta `pktctl-0.2.2-x86_64-pc-windows-msvc`
   con `pktctl.exe`. Crea `C:\Users\<usuario>\pktctl\` y copia **solo**
   `pktctl.exe` ahí, para que la ruta final sea
   `C:\Users\<usuario>\pktctl\pktctl.exe`.
3. **Comprueba** que arranca. Abre PowerShell:

   ```powershell
   C:\Users\<usuario>\pktctl\pktctl.exe --version
   ```

   Debe responder `pktctl 0.2.2`. Si Windows Defender o SmartScreen bloquea el
   archivo, la ruta de excepción la decide el equipo del alumno; no lo he
   comprobado en Windows.
4. **Genera el secreto** en PowerShell. Guárdalo: va en la config del cliente y
   en el `.pta` de Packet Tracer, y tiene que ser idéntico en los dos sitios:

   ```powershell
   $bytes = New-Object byte[] 24
   [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
   $secret = -join ($bytes | ForEach-Object { $_.ToString('x2') })
   $secret
   ```

   Devuelve 48 caracteres hexadecimales.

El App ID es `dev.pktctl`. Puedes usar otro con formato de dominio inverso, pero
entonces cámbialo en todas las configs y en el registro.

### Linux

```sh
VERSION=0.2.2
curl -fsSLO "https://github.com/TantiE100/pktctl/releases/download/v$VERSION/pktctl-$VERSION-x86_64-unknown-linux-gnu.tar.gz"
curl -fsSLO "https://github.com/TantiE100/pktctl/releases/download/v$VERSION/SHA256SUMS"
sha256sum -c SHA256SUMS --ignore-missing
tar -xzf "pktctl-$VERSION-x86_64-unknown-linux-gnu.tar.gz"
install -m 755 "pktctl-$VERSION-x86_64-unknown-linux-gnu/pktctl" ~/.local/bin/pktctl
pktctl --version
SECRET=$(openssl rand -hex 24)
```

En macOS el archivo es `pktctl-$VERSION-x86_64-apple-darwin.tar.gz`
(o `aarch64-apple-darwin` en Apple Silicon).

## Registrar pktctl en el cliente

Los dos clientes necesitan el mismo App ID y el mismo secreto.

### Claude Desktop

Claude Desktop arranca `pktctl` como proceso hijo y habla MCP por stdio. No hay
que instalar nada más.

**Windows**

1. Abre el Explorador de archivos, escribe `%APPDATA%\Claude` en la barra de
   direcciones y pulsa Intro.
2. Abre `claude_desktop_config.json` con el Bloc de notas. Si no existe, créalo
   con este contenido:

   ```json
   {
     "mcpServers": {}
   }
   ```

3. Añade la entrada `pktctl` dentro de `mcpServers`. Las barras invertidas van
   dobles (`\\`) y la ruta debe ser absoluta:

   ```json
   {
     "mcpServers": {
       "pktctl": {
         "command": "C:\\Users\\<usuario>\\pktctl\\pktctl.exe",
         "args": [],
         "env": {
           "PKTCTL_APP_ID": "dev.pktctl",
           "PKTCTL_SECRET": "el-secreto-del-paso-4"
         }
       }
     }
   }
   ```

   Si ya hay otros servidores, añade solo la entrada `pktctl` con su coma
   delante o detrás; no borres las demás.
4. Cierra Claude Desktop del todo: icono de la bandeja del sistema →
   **Quit**. Cerrar la ventana no basta. Vuelve a abrirlo.

**Linux**

Mismo bloque en `~/.config/Claude/claude_desktop_config.json`, con barras
normales:

```json
"pktctl": {
  "command": "/home/<usuario>/.local/bin/pktctl",
  "args": [],
  "env": {
    "PKTCTL_APP_ID": "dev.pktctl",
    "PKTCTL_SECRET": "el-secreto-que-generaste"
  }
}
```

### OpenCode

**Linux/macOS:**

```sh
opencode mcp add pktctl --global \
  --env PKTCTL_APP_ID=dev.pktctl \
  --env "PKTCTL_SECRET=$SECRET" \
  -- "$HOME/.local/bin/pktctl"
```

**Windows:** edita `%USERPROFILE%\.config\opencode\opencode.json` y añade la
entrada dentro de `mcp.servers` (no dentro de `mcpServers`):

```json
{
  "mcp": {
    "servers": {
      "pktctl": {
        "type": "local",
        "command": ["C:\\Users\\<usuario>\\pktctl\\pktctl.exe"],
        "environment": {
          "PKTCTL_APP_ID": "dev.pktctl",
          "PKTCTL_SECRET": "el-secreto-del-paso-4"
        }
      }
    }
  }
}
```

## Registro de pktctl en Packet Tracer

Packet Tracer solo acepta aplicaciones registradas. El registro es un archivo
`pktctl.pta` que se crea **una vez** y se carga en Packet Tracer con
**Configure Apps**.

Hay dos formas de crearlo.

### Opción A: `setup_exapp` (desde el cliente)

Pide al agente **«ejecuta setup_exapp»**. Escribe el `.pta` en
`PKTCTL_SETUP_DIR` o, por defecto, en `~/.config/pktctl/` (Linux) o
`%USERPROFILE%\.config\pktctl\` (Windows).

> **En Linux con la instalación de Packet Tracer de esta clase no funciona.**
> `setup_exapp` solo busca `meta` en `<carpeta>/extensions/`, y en esta
> instalación `meta` está en `bin/` dentro de un AppImage montado en `/tmp`
> (la ruta cambia en cada arranque). Responde:
> `could not find Packet Tracer's meta tool`. Usa la opción B.

### Opción B: manual con `meta` (probada en Linux)

`meta` es la herramienta de Packet Tracer que cifra la plantilla XML. Cuesta un
minuto y no depende de `setup_exapp`.

**1. Localiza `meta`** dentro de la carpeta de instalación de Packet Tracer.

- Linux (AppImage): `bin/meta`. Con `find <carpeta de PT> -name meta -type f`.
- Windows: el archivo se llama `meta.exe`. Busca `meta.exe` en la carpeta donde
  instalaste Packet Tracer con el buscador del Explorador. Lo normal es que esté
  en una subcarpeta `extensions` o `bin`.

**2. Prepara la plantilla.** Descárgala del tag `v0.2.2` de pktctl, cambia el
secreto por el tuyo y cifra:

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
mkdir $env:USERPROFILE\pktctl-registro; cd $env:USERPROFILE\pktctl-registro
Invoke-WebRequest -Uri https://raw.githubusercontent.com/TantiE100/pktctl/v0.2.2/crates/pktctl/assets/pktctl-exapp.xml -OutFile pktctl-exapp.xml
(Get-Content pktctl-exapp.xml) -replace 'REPLACE_WITH_YOUR_SECRET', $secret | Set-Content pktctl-exapp.xml
& "<ruta a meta.exe>" pktctl.pta pktctl-exapp.xml
Remove-Item pktctl-exapp.xml
New-Item -ItemType Directory -Force "$env:USERPROFILE\.config\pktctl" | Out-Null
Copy-Item pktctl.pta "$env:USERPROFILE\.config\pktctl\pktctl.pta"
```

`$secret` es la variable del paso 4 de Windows. Si cerraste esa ventana de
PowerShell, vuelve a generar el secreto **y** cambia el valor en la config del
cliente, porque tienen que coincidir.

El XML contiene el secreto en claro. Por eso se borra justo después de cifrarlo.

### Cargar el `.pta` en Packet Tracer

1. Abre Packet Tracer.
2. **Extensions → IPC → Configure Apps → Add** y selecciona el `.pta`
   (`~/.config/pktctl/pktctl.pta` o `%USERPROFILE%\.config\pktctl\pktctl.pta`).
   Si el diálogo no muestra archivos ocultos, escribe la ruta a mano.
3. Pulsa **Ok**. La app aparece en la lista como `pktctl`.
4. Cierra Packet Tracer con **File → Exit**. No lo mates con `kill` ni con el
   Administrador de tareas: solo al salir normalmente guarda la lista de apps.

> Si Packet Tracer se cierra mal después de registrar, el registro se pierde:
> repite el paso y vuelve a salir con **File → Exit**.

> **No pulses «Launch» sobre `pktctl`.** Verás
> `Cannot launch ExApp. The executable file name or location may be incorrect...`.
> Es normal: el cliente MCP lanza `pktctl` y se conecta por TCP. El registro
> está bien si la app aparece en la lista y `status` responde `connected: true`.

## Verificar la conexión

**Claude Desktop.** Reinicia Claude (paso anterior) y, en una conversación
nueva, pregunta:

> Comprueba el estado de Packet Tracer.

Claude debe llamar a `status`. Si todavía no cargaste el `.pta`, responde
`rejected app id`: el servidor está bien configurado y falta la sección de
registro. Con el registro cargado y Packet Tracer abierto, responde
`connected: true` con la versión de PT, los dispositivos y los enlaces. Los
logs del servidor están en `%APPDATA%\Claude\logs\mcp-server-pktctl.log`
(Windows) o `~/.config/Claude/logs/mcp-server-pktctl.log` (Linux).
Esa convención de nombres es la de los otros servidores de tu instalación; en
`pktctl` todavía no lo he visto aparecer.

**OpenCode:**

```sh
opencode mcp list
```

Debe mostrar `✓ pktctl  connected`.

## Cómo se usa en estas sesiones

Abre el `.pkt` que quieras trabajar y pide las acciones en lenguaje natural. El
agente descubre los nombres con `list_devices`, ejecuta comandos con `run_cli` y
usa `fast_forward` después de cablear o configurar DHCP/OSPF para que STP, DHCP
y routing converjan antes de probar.

Ejemplos con los archivos de `packet-tracer/`:

**Sesión A (IPv4 o IPv6)**

> Abre `packet-tracer/Sesion-A-IPv6.pkt`, comprueba con `show ipv6 interface brief`
> que R1, R2 y R3 tienen sus direcciones y que `ipconfig` de PC-A1 muestra un
> `/64` por DHCPv6.

> Desde PC-A1 haz ping a PC-B1 y PC-C1. Si falla, revisa `show ipv6 route` en
> los tres routers.

**Sesión B (hub-and-spoke)**

> Abre `packet-tracer/Sesion-B-IPv6.pkt` y verifica que R1 vea dos vecinos OSPFv3
> en `FULL` con `show ipv6 ospf neighbor`.

> Apaga `GigabitEthernet0/1` de R1, espera la convergencia y comprueba desde
> PC-B1 con `tracert` que el camino pasa por R3. Después vuelve a encenderla.

**Construir desde cero**

> Crea la topología de la Sesión A: tres routers 2911, tres switches 2960 y
> nueve PCs. Cablea según `SESION-A.md`, guarda como `sesion-a-nueva.pkt` y
> aplica las configuraciones de `config/`.

### Archivos generados con pktctl

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

## Herramientas que más vas a usar

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

- El secreto da **control total** de Packet Tracer. No lo subas al repo ni lo
  pegues en un chat.
- El secreto queda en claro en la config del cliente (`claude_desktop_config.json`
  y `opencode.json`) y en el XML temporal del registro manual. Mantén esos
  archivos privados. En Linux, `claude_desktop_config.json` queda en modo `600`.
- En **Extensions → IPC → Options**, deja **Allow Remote Applications**
  desactivado salvo que lo necesites: PT escucha en todas las interfaces.
- Antes de pedir cambios masivos, guarda una copia del `.pkt`. El agente puede
  sobrescribir el archivo abierto.

## Problemas típicos

| Síntoma | Causa y solución |
|---------|------------------|
| `Packet Tracer is not reachable` | PT cerrado, o IPC en un puerto fuera de `39000`–`39009`. Abre PT y revisa **Extensions → IPC → Options**. |
| `Cannot launch ExApp...` al pulsar **Launch** | Esperado. El cliente MCP lanza `pktctl`, no PT. Ignora el aviso y usa `status`; si da `connected: true`, todo está bien. |
| `rejected app id dev.pktctl` | Falta cargar el `.pta`, el secreto no coincide con el del `.pta`, o PT no salió con **File → Exit**. Vuelve a generar el `.pta` con el mismo secreto y cárgalo. |
| `could not find Packet Tracer's meta tool` (`setup_exapp`) | Usa la opción B del registro manual. |
| `does not have the necessary privilege` | El `.pta` se registró con una plantilla vieja. Genera y carga el de la plantilla `v0.2.2`. |
| `opencode mcp list` muestra `failed` | Revisa la ruta del binario y las variables `PKTCTL_APP_ID` / `PKTCTL_SECRET`. En Windows usa la ruta absoluta al `.exe`. |
| Claude Desktop no muestra las herramientas de Packet Tracer | JSON inválido (coma sobrante), ruta del binario inexistente o Claude no se cerró del todo (**Quit** desde la bandeja). Revisa los logs de la sección de verificación. |
| Claude Desktop no arranca `pktctl` en Windows | La ruta del `command` debe ser absoluta y con `\\`. Claude no siempre hereda el `PATH`, por eso `pktctl.exe` sin ruta completa puede no encontrarse. |
| Los cambios no aparecen | Ejecuta `fast_forward` y vuelve a consultar; STP/DHCP/OSPF tardan en converger. |
| PT se cuelga o no responde | Cierra PT normalmente y vuelve a abrirlo. No hace falta reinstalar `pktctl`. |

## Actualizar o desinstalar

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
# y borra mcp.servers.pktctl de ~/.config/opencode/opencode.json
# y mcpServers.pktctl de ~/.config/Claude/claude_desktop_config.json
```

**Windows:** para actualizar, sustituye `pktctl.exe` por el de un zip nuevo.
Para desinstalar, borra `C:\Users\<usuario>\pktctl\`, la carpeta
`%USERPROFILE%\.config\pktctl`, y la entrada `pktctl` de
`%APPDATA%\Claude\claude_desktop_config.json` y de `opencode.json`.

Al cambiar de versión de Packet Tracer, revisa las notas de `pktctl`: la
versión validada es **9.0.1**. Otras versiones pueden funcionar, pero no están
garantizadas.
