# MCP de Cisco Packet Tracer (pktctl)

Guía para que **Claude Desktop** u **OpenCode** construyan, configuren y prueben
las redes de este laboratorio dentro de **Cisco Packet Tracer 9.0.1**, usando el
servidor MCP [`pktctl`](https://github.com/TantiE100/pktctl).

Para que funcione hacen falta solo dos cosas:

1. **El JSON** del servidor en la configuración del cliente.
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
9. [Práctica guiada con el MCP](#paso-7-práctica-guiada-con-el-mcp)
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
| Ejercicios del Paso 7 en `Sesion-B-IPv6.pkt` | Probados (sesión 1-6; el 7 y el 8 son de corrección manual) | No probados |
| Bloques JSON de esta guía | Probados (4 de 4) | Probados (son los mismos) |
| `opencode mcp list` → `pktctl connected` | Probado | No probado |
| Claude Desktop cargando el servidor en la ventana | Pendiente: hay que reiniciar Claude Desktop | No probado |
| Generación del secreto en PowerShell | No aplica | No probado |

## Qué instala

| Componente | Ruta / valor |
|------------|--------------|
| Binario | `~/.local/bin/pktctl` (Linux) · `C:\Users\<usuario>\pktctl\pktctl.exe` (Windows), v0.2.2 |
| Registro ExApp | [`pktctl.pta`](pktctl.pta) (el mismo archivo en cualquier sistema) · copia en `~/pktctl.pta` o `%USERPROFILE%\pktctl.pta` |
| Secreto IPC | `~/.config/pktctl/secret` (Linux, modo 600, **no versionar**) |
| App ID | `dev.pktctl` |
| Config de OpenCode | `~/.config/opencode/opencode.json` → `mcp.servers.pktctl` (Linux) · `%USERPROFILE%\.config\opencode\opencode.json` (Windows) |
| Config de Claude Desktop | `~/.config/Claude/claude_desktop_config.json` (Linux) · `%APPDATA%\Claude\claude_desktop_config.json` (Windows) |

`pktctl` habla con Packet Tracer por **PTMP**, el protocolo nativo de
aplicaciones externas (puertos `39000`–`39009`). Expone 72 herramientas:
topología, cables, CLI de IOS, DHCP/PCs, servidores, simulación, actividades y
acceso directo a la API IPC.

> Sigue **un solo cliente**: Claude Desktop (Paso 3A) **o** OpenCode (Paso 3B).
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

### Paso 3B: OpenCode

Abre `%USERPROFILE%\.config\opencode\opencode.json` (Linux:
`~/.config/opencode/opencode.json`). Si no existe, créalo con este contenido y
añade `pktctl` dentro de `mcp.servers`, no dentro de `mcpServers`:

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
          "PKTCTL_SECRET": "eb9a6706129c3c6d40979a5540e110e76773eba055862c33"
        }
      }
    }
  }
}
```

Si ya tenías otras claves, añade solo `"mcp"` y no dupliques `"$schema"`.

En Linux/macOS también puedes usar la CLI:

```sh
opencode mcp add pktctl --global \
  --env PKTCTL_APP_ID=dev.pktctl \
  --env "PKTCTL_SECRET=eb9a6706129c3c6d40979a5540e110e76773eba055862c33" \
  -- "$HOME/.local/bin/pktctl"
```

Comprueba que OpenCode ve el servidor:

```sh
opencode mcp list
```

**Debe mostrar** `pktctl` con estado `connected`.

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

## Paso 7: práctica guiada con el MCP

Ocho ejercicios cortos, **en orden**, sobre una **copia** del `.pkt`. Sirven para
las cuatro sesiones: cambia el nombre del archivo y usa la columna que
corresponda.

| Tarea | IPv4 | IPv6 |
|-------|------|------|
| Ver direcciones | `show ip interface brief` | `show ipv6 interface brief` |
| Ver rutas | `show ip route` | `show ipv6 route` |
| Ver DHCP | `show ip dhcp binding` | `show ipv6 dhcp binding` |
| Ver vecinos | `show ip ospf neighbor` | `show ipv6 ospf neighbor` |

**Cómo se pide.** Un prompt útil tiene cuatro partes: qué archivo abrir, qué
comprobar, en qué formato devolverlo y qué **no** tocar. Escribe tu predicción
antes de enviarlo: el objetivo es que detectes si el agente se equivoca.

> Los routers del laboratorio piden contraseña de consola y de `enable`: es
> `cisco`. Si el agente se queda esperando un `Password:`, dale ese dato.

### 1. Reconocer la red (sin cambios)

**Predice:** cuántos routers, switches y PCs hay, y cuántos enlaces.

> Abre `packet-tracer/Sesion-A-IPv4.pkt` y no cambies nada. Dime la versión de
> Packet Tracer, cuántos routers, switches y PCs hay, y cuántos enlaces. Preséntalo
> como una lista con los nombres de los dispositivos.

**Comprueba:** 3 routers, 3 switches, 9 PCs y 15 enlaces (`status` responde
`connected: true`). El `Power Distribution Device0` no cuenta: es un accesorio de
Packet Tracer. Si el agente cuenta mal, no confíes en el resto.

### 2. Leer el direccionamiento

**Predice:** las direcciones de R1 y cuáles deben estar `up`.

> En R1, muéstrame todas las interfaces con su dirección y estado. Marca las que
> estén down y no cambies la configuración.

**Comprueba:** Gi0/0 = .1/28, Gi0/1 = .49/30, Gi0/2 = .58/30, todas `up/up`. En la
Sesión B aparece además `Gi0/0.20` = .65/28. En IPv6: `2001:DB8:13::1`,
`2001:DB8:13:48::1`, `2001:DB8:13:56::2` y, en la Sesión B,
`2001:DB8:13:64::1` en `Gi0/0.20`.

### 3. Comprobar el DHCP

**Predice:** cuántas concesiones debe haber y en qué rango.

> En R2, lista las concesiones DHCP y dime qué PC tiene cada IP. No renueves ni
> liberes ninguna.

**Comprueba:** en IPv4, todas las concesiones caen dentro de los rangos de sus
pools (Sesión A: .22–.30; Sesión B: VLAN 10 .22–.30 y VLAN 20 .86–.94). En IPv6
hay una concesión por PC y las direcciones caen en los prefijos del sitio
(`2001:DB8:13:16::/64` y `2001:DB8:13:80::/64` en la Sesión B). Compara la MAC
de cada lease con la del PC.

### 4. Seguir el camino de un paquete

**Predice:** por qué router sale el paquete y cuántos saltos hay.

> Desde PC-A1 haz ping a PC-C1 y luego un tracert. Dime el primer salto, el camino
> completo y si coincide con las rutas de la tabla.

**Comprueba:** ping OK y el camino pasa por R1 y R3 (LAN-A → LAN-C). En IPv6,
`2001:DB8:13::1` → `2001:DB8:13:56::1`. Un salto inesperado suele ser una ruta
mal escrita.

### 5. Interpretar la tabla de rutas

**Predice:** qué código (`S`, `O`, `C`) y qué siguiente salto debe usar R1 para
llegar a 192.168.2.32/28.

> Muéstrame la tabla de rutas de R1 y explica qué entrada usa para llegar a
> 192.168.2.32/28. Indica el código, el siguiente salto y la interfaz de salida.

**Comprueba:** en la Sesión A debe ser `S` por .57 (Gi0/2). En la Sesión B, `O`
con costo. En IPv6 es `O 2001:DB8:13:32::/64 [110/2]` por `GigabitEthernet0/2`.
Si sale `S` en la Sesión B, OSPF no convergió.

### 6. Fallo controlado

**Predice:** qué debería pasar según el tipo de enrutamiento de tu sesión.

*Sesión A (rutas estáticas):*

> En R2 apaga GigabitEthernet0/2, ejecuta fast_forward y comprueba desde PC-B1 si
> llega a PC-C1. Después vuelve a encender la interfaz. No guardes el archivo.

**Comprueba:** el ping **falla**. La ruta estática no se adapta: ese es su límite.

*Sesión B (OSPF):*

> En R1 apaga GigabitEthernet0/1, ejecuta fast_forward y comprueba desde PC-B1 si
> llega a PC-C1 y por qué camino. Después vuelve a encender la interfaz. No
> guardes el archivo.

**Comprueba:** el ping **sigue funcionando** y el camino pasa por R3: en IPv6,
`2001:DB8:13:52::2`, y `show ipv6 route` en R2 marca métrica 101. Esa es la
redundancia de la Sesión B y la pregunta 5 de la rúbrica. Al encender la interfaz
el camino vuelve por R1 y la métrica baja a 3.

### 7. Diagnóstico a ciegas

**Prepara el fallo:** cambia tú una IP (por ejemplo, el gateway de una LAN) y no
digas cuál.

> Hay un fallo de conectividad entre PC-B1 y PC-C1. Diagnostícalo leyendo las
> interfaces y las tablas de rutas, explica la causa y propón la corrección. No
> cambies nada todavía; espera mi confirmación.

**Comprueba:** el agente debe encontrar la interfaz cambiada y proponer la IP
correcta. Si acierta, pide que la corrija y verifica con un ping. Si no acierta,
corrige tú y explica qué pista faltó en el prompt.

### 8. Reto de VLSM

**Predice:** qué subred libre usarías y por qué no vale la primera dirección libre.

> Sin cambiar nada, planifica una cuarta LAN de 10 hosts dentro de
> 192.168.2.0/24. Indica red, máscara, gateway, rango DHCP y el bloque que
> elegiste. No la configures.

**Comprueba:** debe ser un `/28` alineado. En la **Sesión A** el primero libre es
192.168.2.64/28; en la **Sesión B**, 192.168.2.112/28 (gateway .113, DHCP
.118–.126). Si propone .60 (A) o .114 (B) como dirección de red, no alineó el
bloque. Es solo IPv4: IPv6 no usa VLSM en este laboratorio.

> Los ejercicios 6 y 7 modifican la red. Trabaja sobre una copia y no guardes el
> `.pkt` original.

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
  y `opencode.json`) y en el XML temporal del registro manual. Mantén esos
  archivos privados. En Linux, `claude_desktop_config.json` queda en modo `600`.
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
| `opencode mcp list` muestra `failed` | Revisa la ruta del binario y `PKTCTL_APP_ID` / `PKTCTL_SECRET`. |
| Los cambios no aparecen | Ejecuta `fast_forward` y vuelve a consultar; STP/DHCP/OSPF tardan en converger. |
| PT se cuelga o no responde | Cierra PT normalmente y vuelve a abrirlo. No hace falta reinstalar `pktctl`. |

## Actualizar y desinstalar

**Windows:** para actualizar, sustituye `pktctl.exe` por el de un zip nuevo. Para
desinstalar, borra `C:\Users\<usuario>\pktctl\`, la carpeta
`%USERPROFILE%\.config\pktctl`, y la entrada `pktctl` de
`claude_desktop_config.json` o de `opencode.json`. En Packet Tracer, quita el
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
# y borra mcp.servers.pktctl de ~/.config/opencode/opencode.json
# y mcpServers.pktctl de ~/.config/Claude/claude_desktop_config.json
```

Al cambiar de versión de Packet Tracer, revisa las notas de `pktctl`: la versión
validada es **9.0.1**. Otras versiones pueden funcionar, pero no están
garantizadas.
