# MCP de Cisco Packet Tracer (pktctl)

Guía para que un agente de OpenCode construya, configure y pruebe las redes de
este laboratorio dentro de **Cisco Packet Tracer 9.0.1** usando el servidor MCP
[`pktctl`](https://github.com/TantiE100/pktctl).

> `pktctl` no reemplaza a Packet Tracer: lo maneja. Necesita la ventana de
> Packet Tracer abierta y el `.pkt` cargado. No funciona en modo headless.

## Qué instala esta configuración

| Componente | Ruta / valor |
|------------|--------------|
| Binario | `~/.local/bin/pktctl` (v0.2.2, Linux x86_64) |
| Registro ExApp | `~/pktctl.pta` (copia visible; el original está en `~/.config/pktctl/pktctl.pta`) |
| Secreto IPC | `~/.config/pktctl/secret` (modo 600, **no versionar**) |
| App ID | `dev.pktctl` |
| Config de OpenCode | `~/.config/opencode/opencode.json` → `mcp.servers.pktctl` |

`pktctl` habla con Packet Tracer por **PTMP**, el protocolo nativo de
aplicaciones externas (puertos `39000`–`39009`). Expone 72 herramientas:
topología, cables, CLI de IOS, DHCP/PCs, servidores, simulación, actividades y
acceso directo a la API IPC.

## Instalar en otra máquina

Requisitos: Packet Tracer **9.0.1**, OpenCode y, en Linux, glibc **2.39** o
superior (Ubuntu 24.04 / Debian 13). Hay binarios para macOS, Windows y ARM64 en
los [releases](https://github.com/TantiE100/pktctl/releases).

```sh
VERSION=0.2.2
curl -fsSLO "https://github.com/TantiE100/pktctl/releases/download/v$VERSION/pktctl-$VERSION-x86_64-unknown-linux-gnu.tar.gz"
curl -fsSLO "https://github.com/TantiE100/pktctl/releases/download/v$VERSION/SHA256SUMS"
sha256sum -c SHA256SUMS --ignore-missing
tar -xzf "pktctl-$VERSION-x86_64-unknown-linux-gnu.tar.gz"
install -m 755 "pktctl-$VERSION-x86_64-unknown-linux-gnu/pktctl" ~/.local/bin/pktctl
```

Genera un App ID y un secreto, y registra el servidor en OpenCode:

```sh
SECRET=$(openssl rand -hex 24)
opencode mcp add pktctl --global \
  --env PKTCTL_APP_ID=dev.pktctl \
  --env "PKTCTL_SECRET=$SECRET" \
  -- "$HOME/.local/bin/pktctl"
```

Abre Packet Tracer, pide al agente **«ejecuta setup_exapp»** y sigue los pasos
del archivo `.pta` que genera. Después completa el registro único de abajo.

## Registro único en Packet Tracer

En esta instalación ya está generado `~/pktctl.pta` (copia visible del original
en `~/.config/pktctl/`). Si Packet Tracer todavía no lo conoce, hazlo una sola
vez:

1. Abre Packet Tracer.
2. **Extensions → IPC → Configure Apps → Add**.
3. Selecciona `/home/ponciop/pktctl.pta` y confirma con **Ok**.

   Si el selector no muestra los archivos ocultos, copia el `.pta` a una carpeta
   visible (`cp ~/.config/pktctl/pktctl.pta ~/pktctl.pta`) o pulsa **Ctrl+H**
   en el diálogo para mostrarlos.
4. Cierra Packet Tracer con **File → Exit** (no lo mates con `kill`). Solo al
   salir normalmente guarda la lista de aplicaciones.

> Si Packet Tracer se cierra mal después de registrar, el registro se pierde:
> repite el paso y vuelve a salir con **File → Exit**.

> **No pulses «Launch» sobre `pktctl`.** Si lo haces verás
> `Cannot launch ExApp. The executable file name or location may be incorrect...`.
> Es normal: `pktctl` no lo lanza Packet Tracer, lo lanza OpenCode y se conecta
> por TCP. El `.pta` no lleva archivo de integridad justamente para que PT no
> intente ejecutarlo. El registro está bien si la app aparece en la lista y
> `status` responde `connected: true`.

## Verificar la conexión

```sh
opencode mcp list
```

Debe mostrar `✓ pktctl  connected`. Luego, desde OpenCode, pide al agente:

> Comprueba el estado de Packet Tracer.

La herramienta `status` responde `connected: true`, la versión de PT y cuántos
dispositivos y enlaces hay abiertos. Si PT está cerrado verás
`Packet Tracer is not reachable`; es lo esperado.

## Cómo se usa en estas sesiones

Abre el `.pkt` que quieras trabajar y pide las acciones en lenguaje natural. El
agente descubre los nombres con `list_devices`, ejecuta comandos con `run_cli` y
usa `fast_forward` después de cablear o configurar DHCP/OSPF para que STP, DHCP
y routing converjan antes de probar.

Ejemplos útiles:

**Sesión A (IPv4 o IPv6)**

> Abre `sesion-a.pkt`, configura R1, R2 y R3 con las direcciones de
> `SESION-A-IPV6.md`, activa DHCPv6 y comprueba con `show ipv6 interface brief`.

> Desde PC-A1 haz ping a PC-B1 y PC-C1. Si falla, revisa `show ipv6 route` en
> los tres routers.

**Sesión B (hub-and-spoke)**

> Abre `sesion-b.pkt` y verifica que R1 vea dos vecinos OSPFv3 en `FULL` con
> `show ipv6 ospf neighbor`.

> Apaga `GigabitEthernet0/1` de R1, espera la convergencia y comprueba desde
> PC-B1 con `tracert` que el camino pasa por R3. Después vuelve a encenderla.

**Construir desde cero**

> Crea la topología de la Sesión A: tres routers 2911, tres switches 2960 y
> nueve PCs. Cablea según `SESION-A.md`, guarda como `sesion-a-nueva.pkt` y
> aplica las configuraciones de `config/`.

> Crea la topología hub-and-spoke de la Sesión B con VLAN 10/20, aplica
> `config/ipv6/R1.txt`…`R3.txt` y verifica DHCPv6 y OSPFv3.

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

- El secreto de `~/.config/pktctl/secret` da **control total** de Packet
  Tracer. No lo subas al repo ni lo pegues en un chat.
- El archivo de OpenCode quedó con permisos `600` porque contiene ese secreto.
- En **Extensions → IPC → Options**, deja **Allow Remote Applications**
  desactivado salvo que lo necesites: PT escucha en todas las interfaces.
- Antes de pedir cambios masivos, guarda una copia del `.pkt`. El agente puede
  sobrescribir el archivo abierto.

## Problemas típicos

| Síntoma | Causa y solución |
|---------|------------------|
| `Packet Tracer is not reachable` | PT cerrado, o IPC en un puerto fuera de `39000`–`39009`. Abre PT y revisa **Extensions → IPC → Options**. |
| `Cannot launch ExApp...` al pulsar **Launch** | Esperado. `pktctl` lo arranca OpenCode, no PT. Ignora el aviso y usa `status`; si da `connected: true`, todo está bien. |
| `rejected app id dev.pktctl` | Falta registrar el `.pta`, el secreto no coincide o PT no salió con **File → Exit**. Registra de nuevo y cierra bien. |
| `does not have the necessary privilege` | El `.pta` se registró con una plantilla vieja. Vuelve a registrar el actual. |
| `opencode mcp list` muestra `failed` | Revisa la ruta del binario y las variables `PKTCTL_APP_ID` / `PKTCTL_SECRET` en la config. |
| Los cambios no aparecen | Ejecuta `fast_forward` y vuelve a consultar; STP/DHCP/OSPF tardan en converger. |
| PT se cuelga o no responde | Cierra PT normalmente y vuelve a abrirlo. No hace falta reinstalar `pktctl`. |

## Actualizar o desinstalar

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
```

Al cambiar de versión de Packet Tracer, revisa las notas de `pktctl`: la
versión validada es **9.0.1**. Otras versiones pueden funcionar, pero no están
garantizadas.
