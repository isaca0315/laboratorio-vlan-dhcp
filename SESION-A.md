# Sesión A — Topología, VLSM, DHCP y rutas estáticas

Laboratorio N.º 13 · Unidad III · **Cisco Packet Tracer**

Objetivo: montar la red de 3 sedes, calcular el VLSM, configurar cada router
como servidor DHCP de su LAN y terminar con enrutamiento **estático** entre las
tres sedes.

## Parte 1 — Montar la topología

### Paso 1.1 — Colocar los dispositivos

Arrastra al área de trabajo:

| Cant. | Dispositivo | Nombre en Packet Tracer |
|-------|-------------|-------------------------|
| 3 | `Router 2911` | R1, R2, R3 |
| 3 | `Switch 2960` | SW1, SW2, SW3 |
| 9 | `PC-PT` | PC-A1…PC-A3, PC-B1…PC-B3, PC-C1…PC-C3 |

### Paso 1.2 — Cablear

Los **15 cables** son *Copper Straight-Through*. Con la topología ya colocada,
hazlos en este orden (puerto exacto, no "el que esté libre"):

**a) Gateways a los switches** (3 cables)

| Desde | Hasta |
|-------|-------|
| `R1 Gi0/0` | `SW1 Fa0/1` |
| `R2 Gi0/0` | `SW2 Fa0/1` |
| `R3 Gi0/0` | `SW3 Fa0/1` |

**b) Los 9 PCs a su switch** (9 cables)

| Desde | Hasta | | Desde | Hasta | | Desde | Hasta |
|-------|-------|---|-------|-------|---|-------|-------|
| `PC-A1 Fa0` | `SW1 Fa0/2` | | `PC-B1 Fa0` | `SW2 Fa0/2` | | `PC-C1 Fa0` | `SW3 Fa0/2` |
| `PC-A2 Fa0` | `SW1 Fa0/3` | | `PC-B2 Fa0` | `SW2 Fa0/3` | | `PC-C2 Fa0` | `SW3 Fa0/3` |
| `PC-A3 Fa0` | `SW1 Fa0/4` | | `PC-B3 Fa0` | `SW2 Fa0/4` | | `PC-C3 Fa0` | `SW3 Fa0/4` |

**c) Los 3 enlaces entre routers** (3 cables)

Van **directo de un router al otro**, sin switch de por medio:

| Desde | Hasta | Subred |
|-------|-------|--------|
| `R1 Gi0/1` | `R2 Gi0/1` | 192.168.2.48/30 |
| `R2 Gi0/2` | `R3 Gi0/1` | 192.168.2.52/30 |
| `R3 Gi0/2` | `R1 Gi0/2` | 192.168.2.56/30 |

Cuando PT te pregunte el tipo de cable al unir dos routers, elige **Copper
Straight-Through** (crossover también valdría: las Gi del 2911 negocian auto-MDIX).

### Paso 1.3 — Comprobación rápida antes de configurar

> **No esperes luces verdes todavía.** En Packet Tracer las interfaces Gi del 2911
> nacen *administrativamente shutdown*: los cables se ven **rojos** aunque estén
> bien conectados. Las Gi solo pasan a verde cuando ejecutes `no shutdown` en la
> Parte 3. Si las pones en verde ahora, es porque el router ya traía configuración.

Lo que sí comprueba en este punto es el **cableado**, no las luces:

1. Pasa el cursor por cada cable: debe mostrar **Device / Port** en los dos
   extremos (nunca "Connection" vacío).
2. Cada router debe tener **3 cables**: uno en `Gi0/0`, uno en `Gi0/1` y uno en
   `Gi0/2`.
3. Cada switch debe tener **4 cables**: `Fa0/1` (router) y `Fa0/2-4` (los 3 PCs).

Con eso la Parte 3 puede levantar los puertos y todos deben quedar en verde.

## Parte 2 — Cálculo del VLSM (completar a mano)

Resuelve antes de configurar, para justificar cada comando que escribas después.

> Si necesitas repasar el método, [`SUBNETEO.md`](SUBNETEO.md) lo desarrolla
> paso a paso y trae 6 ejercicios con respuestas. Para saber qué hace cada
> comando que escribes abajo, mira [`COMANDOS.md`](COMANDOS.md).

### Paso 2.1 — Prefijo mínimo para ≥10 hosts

`hosts útiles = 2^h − 2` → para 10 hosts: `2^4 − 2 = 14` → **h = 4** → prefijo
`32 − 4 = /28` (máscara `255.255.255.240`, bloque de 16).

Para los enlaces P2P se necesitan 2 hosts: `2^2 − 2 = 2` → h = 2 → **/30**
(máscara `255.255.255.252`, bloque de 4).

### Paso 2.2 — Reparto dentro de 192.168.2.0/24

Asigna **de mayor a menor** y sempre en múltiplos del bloque:

| # | Subred | Prefijo | Red | Rango usable | Broadcast | Uso |
|---|--------|---------|-----|--------------|-----------|-----|
| 1 | 192.168.2.0/28 | /28 | .0 | .1 – .14 | .15 | LAN-A |
| 2 | 192.168.2.16/28 | /28 | .16 | .17 – .30 | .31 | LAN-B |
| 3 | 192.168.2.32/28 | /28 | .32 | .33 – .46 | .47 | LAN-C |
| 4 | 192.168.2.48/30 | /30 | .48 | .49 – .50 | .51 | R1–R2 |
| 5 | 192.168.2.52/30 | /30 | .52 | .53 – .54 | .55 | R2–R3 |
| 6 | 192.168.2.56/30 | /30 | .56 | .57 – .58 | .59 | R3–R1 |
| — | .60 – .255 | — | — | — | — | libre (196 dir.) |

**Verificación del cálculo:** `16 × 3 + 4 × 3 = 60` direcciones usadas; el bloque
siguiente empezaría en `.60`, que es múltiplo de 16 y de 4 → asignación válida.

## Parte 3 — Configurar los 3 routers

> Los comandos completos de los tres routers están en `config/R1.txt`,
> `config/R2.txt` y `config/R3.txt`. Puedes copiarlos y pegarlos en la CLI del
> router (`clic derecho → Paste`) o escribirlos a mano.

### Paso 3.1 — R1 (Sede A / LAN-A)

```text
enable                        ! modo privilegiado
configure terminal             ! modo de configuración global
hostname R1-SEDE-A             ! nombre del router; sale en el prompt
no ip domain-lookup            ! evita que un typo se tome como dominio
enable secret cisco            ! contraseña del modo privilegiado
line console 0                 ! línea de consola
 password cisco                ! contraseña de la consola
 logging synchronous           ! que los mensajes no partan lo que escribes
line vty 0 4                   ! las 5 líneas de acceso remoto
 password cisco                ! contraseña de acceso remoto
 login                         ! exige la contraseña (si no, vty queda abierto)
!
interface GigabitEthernet0/0    ! puerto hacia el switch SW1
 description LAN-A - Gateway 192.168.2.1  ! etiqueta visible en show config
 ip address 192.168.2.1 255.255.255.240    ! gateway de LAN-A (máscara /28)
 no shutdown                   ! ENCIENDE la interfaz: sin esto no hay red
!
interface GigabitEthernet0/1   ! enlace punto a punto con R2
 description Enlace P2P a R2 (192.168.2.48/30)
 ip address 192.168.2.49 255.255.255.252   ! extremo de R1 en ese /30
 no shutdown
!
interface GigabitEthernet0/2   ! enlace punto a punto con R3
 description Enlace P2P a R3 (192.168.2.56/30)
 ip address 192.168.2.58 255.255.255.252   ! extremo de R1 en ese /30
 no shutdown
!
end                            ! vuelve al modo privilegiado
copy running-config startup-config ! guarda la config para que no se pierda
```

**Punto clave:** `no shutdown` es obligatorio. Las interfaces Gig0/0-Gig0/2 de un
2911 salen apagadas por defecto.

### Paso 3.2 — R2 (Sede B / LAN-B)

```text
enable                        ! modo privilegiado
configure terminal             ! modo de configuración global
hostname R2-SEDE-B             ! mismo esqueleto que R1, con los datos de B
no ip domain-lookup            ! evita que un typo se tome como dominio
enable secret cisco            ! contraseña del modo privilegiado
line console 0                 ! línea de consola
 password cisco                ! contraseña de la consola
 logging synchronous           ! que los mensajes no parten lo que escribes
line vty 0 4                   ! las 5 líneas de acceso remoto
 password cisco                ! contraseña de acceso remoto
 login                         ! exige la contraseña (si no, vty queda abierto)
!
interface GigabitEthernet0/0    ! puerto hacia el switch SW2
 description LAN-B - Gateway 192.168.2.17  ! etiqueta visible en show config
 ip address 192.168.2.17 255.255.255.240   ! gateway de LAN-B (máscara /28)
 no shutdown                   ! ENCIENDE la interfaz: sin esto no hay red
!
interface GigabitEthernet0/1   ! enlace con R1 (misma subred .48/30, otro extremo)
 description Enlace P2P a R1 (192.168.2.48/30)
 ip address 192.168.2.50 255.255.255.252   ! extremo de R2 en ese /30
 no shutdown
!
interface GigabitEthernet0/2   ! enlace con R3
 description Enlace P2P a R3 (192.168.2.52/30)
 ip address 192.168.2.53 255.255.255.252   ! extremo de R2 en ese /30
 no shutdown
!
end                            ! vuelve al modo privilegiado
copy running-config startup-config ! guarda la config para que no se pierda
```

### Paso 3.3 — R3 (Sede C / LAN-C)

```text
enable                        ! modo privilegiado
configure terminal             ! modo de configuración global
hostname R3-SEDE-C             ! mismo esqueleto que R1, con los datos de C
no ip domain-lookup            ! evita que un typo se tome como dominio
enable secret cisco            ! contraseña del modo privilegiado
line console 0                 ! línea de consola
 password cisco                ! contraseña de la consola
 logging synchronous           ! que los mensajes no parten lo que escribes
line vty 0 4                   ! las 5 líneas de acceso remoto
 password cisco                ! contraseña de acceso remoto
 login                         ! exige la contraseña (si no, vty queda abierto)
!
interface GigabitEthernet0/0    ! puerto hacia el switch SW3
 description LAN-C - Gateway 192.168.2.33  ! etiqueta visible en show config
 ip address 192.168.2.33 255.255.255.240   ! gateway de LAN-C (máscara /28)
 no shutdown                   ! ENCIENDE la interfaz: sin esto no hay red
!
interface GigabitEthernet0/1   ! enlace con R2
 description Enlace P2P a R2 (192.168.2.52/30)
 ip address 192.168.2.54 255.255.255.252   ! extremo de R3 en ese /30
 no shutdown
!
interface GigabitEthernet0/2   ! enlace con R1
 description Enlace P2P a R1 (192.168.2.56/30)
 ip address 192.168.2.57 255.255.255.252   ! extremo de R3 en ese /30
 no shutdown
!
end                            ! vuelve al modo privilegiado
copy running-config startup-config ! guarda la config para que no se pierda
```

### Paso 3.4 — Verificar las interfaces

```text
show ip interface brief   ! una línea por interfaz: IP, estado físico y protocolo
```

Esperado (interfaz = `up`/`up` y todas con IP):

```text
R1#show ip interface brief
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0     192.168.2.1     YES NVRAM  up                    up
GigabitEthernet0/1     192.168.2.49    YES NVRAM  up                    up
GigabitEthernet0/2     192.168.2.58    YES NVRAM  up                    up
```

## Parte 4 — DHCP: cada router sirve su propia LAN

### Paso 4.1 — Regla de oro

En el pool se **excluye**:

1. La **IP de la interfaz LAN** del router (es el gateway).
2. Las **IPs fijas administrativas** (servidor, impresora, AP, NVR, etc.).

Si el gateway quedara dentro del pool, un PC podría recibir `192.168.2.1` como IP
propia y la LAN quedaría aislada.

### Paso 4.2 — R1

```text
configure terminal             ! modo de configuración global
ip dhcp excluded-address 192.168.2.1 192.168.2.5
!   .1-.5 queda fuera del pool: es el gateway, no un PC
!
ip dhcp pool LAN-A             ! crea el pool y entra a su modo de configuración
 network 192.168.2.0 255.255.255.240   ! subred /28 que reparte este pool
 default-router 192.168.2.1       ! IP que recibe el PC como gateway
 dns-server 8.8.8.8             ! servidor DNS que recibe el PC
 domain-name lab-utp.pa        ! sufijo DNS: el host se llamará PC-A1.lab-utp.pa
! (lease 1 no existe en el 2911 de Packet Tracer 9.0.1: es valido en
!  IOS real pero PT lo rechaza. El alquiler por defecto de 1 dia ya
!  se aplica solo.)
exit                           ! sale del modo pool -> vuelve a config global
end                            ! vuelve al modo privilegiado
copy running-config startup-config ! guarda la config
```

### Paso 4.3 — R2

```text
configure terminal             ! modo de configuración global
ip dhcp excluded-address 192.168.2.17 192.168.2.21
!   .17-.21 queda fuera del pool: es el gateway, no un PC
!
ip dhcp pool LAN-B             ! crea el pool y entra a su modo de configuración
 network 192.168.2.16 255.255.255.240   ! subred /28 que reparte este pool
 default-router 192.168.2.17       ! IP que recibe el PC como gateway
 dns-server 8.8.8.8             ! servidor DNS que recibe el PC
 domain-name lab-utp.pa        ! sufijo DNS: el host se llamará PC-A1.lab-utp.pa
! (lease 1 no existe en el 2911 de Packet Tracer 9.0.1: es valido en
!  IOS real pero PT lo rechaza. El alquiler por defecto de 1 dia ya
!  se aplica solo.)
exit                           ! sale del modo pool -> vuelve a config global
end                            ! vuelve al modo privilegiado
copy running-config startup-config ! guarda la config
```

### Paso 4.4 — R3

```text
configure terminal             ! modo de configuración global
ip dhcp excluded-address 192.168.2.33 192.168.2.37
!   .33-.37 queda fuera del pool: es el gateway, no un PC
!
ip dhcp pool LAN-C             ! crea el pool y entra a su modo de configuración
 network 192.168.2.32 255.255.255.240   ! subred /28 que reparte este pool
 default-router 192.168.2.33       ! IP que recibe el PC como gateway
 dns-server 8.8.8.8             ! servidor DNS que recibe el PC
 domain-name lab-utp.pa        ! sufijo DNS: el host se llamará PC-A1.lab-utp.pa
! (lease 1 no existe en el 2911 de Packet Tracer 9.0.1: es valido en
!  IOS real pero PT lo rechaza. El alquiler por defecto de 1 dia ya
!  se aplica solo.)
exit                           ! sale del modo pool -> vuelve a config global
end                            ! vuelve al modo privilegiado
copy running-config startup-config ! guarda la config
```

### Paso 4.5 — Qué significa cada parámetro

| Comando | Significado |
|---------|-------------|
| `ip dhcp excluded-address A B` | Rango **reservado** que nunca se entrega (gateway + admin) |
| `network 192.168.2.0 255.255.255.240` | Subred del pool (se escriben red + máscara) |
| `default-router 192.168.2.1` | Gateway que se le entrega al PC |
| `dns-server 8.8.8.8` | Servidor DNS que recibe el PC (Google) |
| `domain-name lab-utp.pa` | Nombre de dominio que se envía en la opción 15 |
| `lease 1` | Duración del alquiler. **No existe en PT** (sí en IOS real) |
| `option 3` / `option 6` | Alternativa para gateway y DNS usando el número de opción |

> **Dos límites de Packet Tracer 9.0.1** (el 2911 de PT no implementa todo el
> IOS real). Si te aparece `% Invalid input detected`, no es un error de tipeo:
>
> - **`lease` no existe.** En un router real sí existe (`lease 1` = 1 día), pero
>   PT lo rechaza. No hace falta: el tiempo de alquiler por defecto ya es de 1 día,
>   así que omítelo. Está comentado en los CLI.
> - **`dns-server` acepta un solo IP.** En IOS real puedes escribir
>   `dns-server 8.8.8.8 1.1.1.1`; en PT solo uno. Por eso los CLI llevan
>   `dns-server 8.8.8.8` y no el segundo.
>
> Puedes comprobar qué acepta cada router con `?` dentro del pool:
> ```
> R1(config)#ip dhcp pool LAN-A
> R1(config-dhcp-pool)#?
> ```

### Paso 4.6 — Verificar el pool en el router

```text
show ip dhcp pool   ! muestra los pool y sus parámetros: red, gateway, DNS y dominio
```

```text
R1#show ip dhcp pool
IP Pool: LAN-A

Network:
  Network 192.168.2.0/28
  Netmask 255.255.255.240

Domain-Name: lab-utp.pa

Default Routers: 192.168.2.1
DNS Servers: 8.8.8.8
```

También sirve para detectar un error típico: si `Network:` aparece con una máscara
distinta a la de tu LAN, el DHCP no назнаará IPs útiles.

## Parte 5 — Verificar el DHCP en los PCs

### Paso 5.1 — Poner los 9 PCs en DHCP

En cada PC: `Desktop → IP Configuration → DHCP → Refresh` (o escribe
`ipconfig /release` y luego `ipconfig /renew` en el `Command Prompt`).

### Paso 5.2 — Comandos en el PC

```text
ipconfig /renew   ! pide una IP nueva al servidor DHCP (equivale a /release + /renew)
ipconfig /all    ! muestra la config completa: IP, máscara, gateway, DNS y lease
```

Esperado en PC-A1:

```text
C:\>ipconfig /all

Ethernet Adapter FastEthernet0:

   Connection-specific DNS Suffix  . lab-utp.pa
   IPv4 Address. . . . . . . . . . : 192.168.2.6
   Subnet Mask . . . . . . . . . . : 255.255.255.240
   Default Gateway . . . . . . . . : 192.168.2.1
   DHCP Server . . . . . . . . . . : 192.168.2.1
   Lease Obtained . . . . . . . . . : Wednesday, October 2, 2026 10:00 AM
   Lease Expires . . . . . . . . . . : Thursday, October 3, 2026 10:00 AM
```

Comprueba los 3 campos críticos: **IP dentro del rango asignable**, **máscara
/28** y **gateway = interfaz LAN del router**.

### Paso 5.3 — Confirmar el enlace DHCP desde el router

```text
show ip dhcp binding   ! qué IP se entregó a cada PC (MAC, tipo de lease y vencimiento)
```

```text
R1#show ip dhcp binding
IP address       Client-ID/          Lease type   Hardware address   Lease expiration
                  Lease type
192.168.2.6      0001.0A6A.0A6A      arp          000C.29A6.0A6A    Oct  3 10:00:00 2026
192.168.2.7      0001.0A6A.0A6A      arp          000C.29A6.0A6A    Oct  3 10:00:00 2026
192.168.2.8      0001.0A6A.0A6A      arp          000C.29A6.0A6A    Oct  3 10:00:00 2026
```

> Packet Tracer agrupa las tres filas con el mismo MAC simulado; la cantidad de
> leases y el rango de IPs son lo importante.

Otros comandos útiles:

```text
show ip dhcp server statistics  ! cuántas peticiones y qué han resuelto
show ip dhcp conflict           ! IPs que dos dispositivos reclaman a la vez
clear ip dhcp binding 192.168.2.6   ! borra esa entrega: el PC pedirá IP de nuevo
```

### Paso 5.4 — Conectividad local (dentro de cada LAN)

Desde PC-A1:

```text
ping 192.168.2.1     → gateway (OK)
ping 192.168.2.7     → otro PC de la misma LAN (OK)
```

Si el ping al gateway falla, el problema es de capa 1/2 o del DHCP, **no** de
enrutamiento.

## Parte 6 — Fase A: enrutamiento estático

### Paso 6.1 — Qué hay que escribir

En una malla cada router necesita **2 rutas estáticas** (una por cada LAN
remota). El siguiente salto es la IP del router vecino **en el enlace por el que
se le envía el paquete**.

| Router | Destino | Siguiente salto | Interfaz de salida |
|--------|---------|-----------------|--------------------|
| R1 | 192.168.2.16 255.255.255.240 | 192.168.2.50 | Gi0/1 |
| R1 | 192.168.2.32 255.255.255.240 | 192.168.2.57 | Gi0/2 |
| R2 | 192.168.2.0 255.255.255.240 | 192.168.2.49 | Gi0/1 |
| R2 | 192.168.2.32 255.255.255.240 | 192.168.2.54 | Gi0/2 |
| R3 | 192.168.2.0 255.255.255.240 | 192.168.2.58 | Gi0/2 |
| R3 | 192.168.2.16 255.255.255.240 | 192.168.2.53 | Gi0/1 |

> **Ojo con los dos extremos del enlace 3 (R1 Gi0/2 ↔ R3 Gi0/2):** ahí R1 es
> `.58` y R3 es `.57`. Como el siguiente salto es **la dirección del vecino**, la
> ruta de R1 hacia LAN-C usa `.57` y la de R3 hacia LAN-A usa `.58`. Escribir la
> propia IP como siguiente salto es el error más común de esta fase.

### Paso 6.2 — Comandos

```text
! ---------- R1 ----------          ! R1 no tiene camino propio a las otras LANs
configure terminal               ! modo de configuración global
ip route 192.168.2.16 255.255.255.240 192.168.2.50  ! LAN-B se alcanza por R2 (.50)
ip route 192.168.2.32 255.255.255.240 192.168.2.57  ! LAN-C se alcanza por R3 (.57)
end                              ! vuelve al modo privilegiado
copy running-config startup-config ! guarda la config

! ---------- R2 ----------
configure terminal               ! modo de configuración global
ip route 192.168.2.0 255.255.255.240 192.168.2.49   ! LAN-A se alcanza por R1 (.49)
ip route 192.168.2.32 255.255.255.240 192.168.2.54  ! LAN-C se alcanza por R3 (.54)
end
copy running-config startup-config

! ---------- R3 ----------
configure terminal               ! modo de configuración global
ip route 192.168.2.0 255.255.255.240 192.168.2.58   ! LAN-A se alcanza por R1 (.58)
ip route 192.168.2.16 255.255.255.240 192.168.2.53  ! LAN-B se alcanza por R2 (.53)
end
copy running-config startup-config
```

### Paso 6.3 — Verificar la tabla de enrutamiento

```text
show ip route   ! tabla de enrutamiento completa: connected, static y local
```

```text
R1#show ip route
Codes: L - local, C - connected, S - static, O - OSPF

Gateway of last resort is not set

      192.168.2.0/24 is variably subnetted, 5 subnets, 3 masks
C        192.168.2.0/28 is directly connected, GigabitEthernet0/0
L        192.168.2.1/32 is directly connected, GigabitEthernet0/0
C        192.168.2.48/30 is directly connected, GigabitEthernet0/1
L        192.168.2.49/32 is directly connected, GigabitEthernet0/1
C        192.168.2.56/30 is directly connected, GigabitEthernet0/2
L        192.168.2.58/32 is directly connected, GigabitEthernet0/2
S        192.168.2.16/28 [1/0] via 192.168.2.50
S        192.168.2.32/28 [1/0] via 192.168.2.57
```

> El encabezado `5 subnets, 3 masks` cuenta las 5 redes con entrada propia
> (3 `C` + 2 `S`); las 3 rutas locales `L` son /32. Packet Tracer puede mostrar
> un conteo levemente distinto según la versión de IOS: lo que no puede cambiar
> son las 8 líneas de la tabla.

Interpretación: `C` = connected (las 3 LANs/enlaces con IP propia), `L` = local
(dirección de la interfaz), `S` = static (las 2 que escribimos a mano).

Comprobaciones puntuales:

```text
show ip route 192.168.2.32       ← ¿cómo llega R1 a LAN-C?
show ip route static             ← solo las estáticas
show ip route summary
```

### Paso 6.4 — Probar conectividad entre sedes

Desde **PC-A1** (usa un PC, no el router: así pruebas la configuración completa):

```text
ping 192.168.2.22      → PC-B1   (LAN-B)
ping 192.168.2.23      → PC-B2   (LAN-B)
ping 192.168.2.38      → PC-C1   (LAN-C)
```

Todos deben responder. Desde PC-A1 hacia su propia LAN y hacia las otras dos:

| Origen | Destino | Resultado esperado |
|--------|---------|--------------------|
| PC-A1 | 192.168.2.1 (GW) | OK |
| PC-A1 | 192.168.2.7 (misma LAN) | OK |
| PC-A1 | 192.168.2.22 (LAN-B) | OK |
| PC-A1 | 192.168.2.38 (LAN-C) | OK |
| PC-B1 | 192.168.2.6 (LAN-A) | OK |
| PC-C1 | 192.168.2.46 (LAN-C) | OK |

Para localizar **en qué salto** se pierde el paquete, usa `tracert`:

```text
C:\>tracert 192.168.2.38
Tracing route to 192.168.2.38 over a maximum of 30 hops

  1   0 ms   0 ms   1 ms  192.168.2.1     ← gateway de R1
  2   1 ms   1 ms   1 ms  192.168.2.33    ← router R3
Trace complete.
```

En una malla, el camino más corto de LAN-A a LAN-C es de **2 saltos** (directo por
el enlace 3). Si aparecen 3 saltos, el paquete está pasando por R2.

También prueba desde la CLI del router (origen = interfaz LAN):

```text
ping 192.168.2.38                ! prueba básica: 4 paquetes enviados y recibidos
ping 192.168.2.22 source 192.168.2.1  ! sale con la IP del gateway, no con la del PC
traceroute 192.168.2.38          ! muestra por qué routers pasa el paquete
show ip arp                      ! tabla ARP: qué IP se ha resuelto a qué MAC
```

## Preguntas de la Sesión A

1. ¿Cuántas direcciones IP se usan en total (LANs + enlaces) y cuántas quedan
   libres? ¿Qué porcentaje de la red se desaprovecha?
2. ¿Por qué el bloque de un `/30` empieza en `.48` y no en `.50` si `.50` es una
   dirección utilizable? Explica la alineación por bloques.
3. Un PC de LAN-A obtiene `192.168.2.5` (una de las IPs administrativas
   reservadas). ¿Qué comando corregiste? ¿Cómo lo detectas con
   `show ip dhcp binding`?
4. ¿Qué pasaría si configuras el pool con `network 192.168.2.0 255.255.255.0`
   (máscara /24) en vez de `/28`? ¿Qué IPs entregaría a un PC de LAN-B?
5. Explica la diferencia entre una ruta `C` (connected) y una ruta `S` (static)
   en `show ip route`.
6. ¿Cuántas rutas estáticas escribirías en total si la topología fuera una cadena
   R1–R2–R3 en lugar de una malla?

## Entregable de la Sesión A

1. Captura de la topología completa con los 3 routers, 3 switches y 9 PCs
   (**cables en verde**).
2. Tabla de direccionamiento completa (routers + pools + rango DHCP).
3. `show ip interface brief` de los 3 routers.
4. `show ip dhcp pool` y `show ip dhcp binding` de los 3 routers (con los 3
   leases de cada LAN).
5. `ipconfig /all` de un PC de cada LAN y `ping` cruzado entre las 3 sedes.
6. `show ip route` de R1, R2 y R3 mostrando las rutas `S`.
7. Respuestas a las 6 preguntas.