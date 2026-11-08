# Sesión A (IPv6) — Topología, direccionamiento, DHCPv6 y rutas estáticas

Laboratorio N.º 13 · Unidad III · **Cisco Packet Tracer**

Objetivo: montar la misma red de 3 sedes de la Sesión A, ahora con **IPv6**:
un `/64` por segmento, cada router como **servidor DHCPv6** de su LAN y
enrutamiento **estático** entre sedes. Al final, de forma opcional, se sustituye
lo estático por **OSPFv3** (y se compara con **RIPng**).

> Esta guía es la **versión IPv6 de [`SESION-A.md`](SESION-A.md)**. La topología,
> el cableado y los nombres de dispositivos son idénticos; cambian el
> direccionamiento, el servicio de asignación y el protocolo de enrutamiento.
> La versión IPv4 sigue siendo válida: son dos laboratorios alternativos.

## Qué cambia respecto a IPv4

| Concepto | IPv4 (Sesión A) | IPv6 (esta sesión) |
|----------|-----------------|--------------------|
| Dirección de LAN | `192.168.2.0/28` | `2001:db8:13:0::/64` |
| Tamaño de subred | VLSM: `/28` y `/30` | `/64` fijo por segmento (sin VLSM) |
| Broadcast | `192.168.2.15` | No existe: se usa multicast (`ff02::1`) |
| Resolución IP→MAC | ARP | **NDP** (*Neighbor Discovery*) |
| Asignación de IP | DHCPv4 (DORA) | **DHCPv6** stateful (o SLAAC) |
| Gateway que recibe el PC | `default-router` del pool | **Router Advertisement (RA)**, link-local |
| Ruta estática | `ip route` | `ipv6 route` |
| Routing dinámico | OSPFv2 / RIPv2 | **OSPFv3 / RIPng** |
| Ver tabla de rutas | `show ip route` | `show ipv6 route` |
| Ver interfaces | `show ip interface brief` | `show ipv6 interface brief` |

### Tres ideas que hay que tener claras

1. **En IPv6 no se hace VLSM.** El tamaño estándar de una LAN es `/64` (64 bits
   para hosts). No hay dirección de broadcast ni se resta 2. Un `/48` se divide
   en 65 536 redes `/64`, así que no hay desperdicio que optimizar.
2. **DHCPv6 no entrega el gateway.** El PC aprende su puerta de enlace del
   *Router Advertisement* (RA) que envía el router: es su dirección
   **link-local** (`FE80::…`). El pool DHCPv6 solo entrega dirección, DNS y
   dominio.
3. **Packet Tracer no soporta DHCPv6 relay.** Por eso cada router es servidor
   DHCPv6 **solo de sus LAN directamente conectadas**. Este laboratorio ya está
   diseñado así: no hace falta relay.

## Convención de direcciones

Se usa el prefijo de documentación `2001:db8:13::/48`. El **cuarto hextet**
reutiliza el número del plan IPv4 (`0`, `16`, `32`, `48`, `52`, `56`). No es una
conversión matemática: es una convención para comparar ambos planes de un
vistazo.

- El router usa `::1` en su LAN (gateway).
- En un enlace punto a punto, el extremo de menor número IPv4 usa `::1` y el
  otro `::2`.
- Los PCs reciben su dirección por **DHCPv6** (dinámica). Anota la que te
  asigne cada PC con `ipconfig`; no la escribas a mano.

---

## Parte 1 — Montar la topología

El cableado es **idéntico** al de la Sesión A: los mismos 15 cables *Copper
Straight-Through*. Si ya tienes el `.pkt` de IPv4, puedes reutilizarlo borrando
las direcciones; si empiezas de cero, sigue esta lista.

### Paso 1.1 — Dispositivos

| Cant. | Dispositivo | Nombre |
|-------|-------------|--------|
| 3 | `Router 2911` | R1, R2, R3 |
| 3 | `Switch 2960` | SW1, SW2, SW3 |
| 9 | `PC-PT` | PC-A1…A3, PC-B1…B3, PC-C1…C3 |

### Paso 1.2 — Cableado (15 cables)

**a) Gateways a los switches (3 cables)**

| Desde | Hasta |
|-------|-------|
| `R1 Gi0/0` | `SW1 Fa0/1` |
| `R2 Gi0/0` | `SW2 Fa0/1` |
| `R3 Gi0/0` | `SW3 Fa0/1` |

**b) Los 9 PCs a su switch (9 cables)**

| Desde | Hasta | | Desde | Hasta | | Desde | Hasta |
|-------|-------|---|-------|-------|---|-------|-------|
| `PC-A1 Fa0` | `SW1 Fa0/2` | | `PC-B1 Fa0` | `SW2 Fa0/2` | | `PC-C1 Fa0` | `SW3 Fa0/2` |
| `PC-A2 Fa0` | `SW1 Fa0/3` | | `PC-B2 Fa0` | `SW2 Fa0/3` | | `PC-C2 Fa0` | `SW3 Fa0/3` |
| `PC-A3 Fa0` | `SW1 Fa0/4` | | `PC-B3 Fa0` | `SW2 Fa0/4` | | `PC-C3 Fa0` | `SW3 Fa0/4` |

**c) Los 3 enlaces entre routers (3 cables)**

Van directo de router a router, sin switch:

| Desde | Hasta | Prefijo |
|-------|-------|---------|
| `R1 Gi0/1` | `R2 Gi0/1` | `2001:db8:13:48::/64` |
| `R2 Gi0/2` | `R3 Gi0/1` | `2001:db8:13:52::/64` |
| `R3 Gi0/2` | `R1 Gi0/2` | `2001:db8:13:56::/64` |

> Los switches son **capa 2**: no necesitan ninguna configuración IPv6. En esta
> sesión se quedan de fábrica (sin VLANs). Solo hay que encender los puertos del
> router con `no shutdown`.

### Paso 1.3 — Comprobación del cableado

Las interfaces Gi del 2911 nacen apagadas (rojas) hasta el `no shutdown` de la
Parte 3. Antes de configurar, comprueba:

1. Cada cable muestra **Device / Port** en ambos extremos.
2. Cada router tiene 3 cables: `Gi0/0`, `Gi0/1`, `Gi0/2`.
3. Cada switch tiene 4: `Fa0/1` (router) y `Fa0/2-4` (PCs).

---

## Parte 2 — Plan de direccionamiento IPv6

### Paso 2.1 — Del `/48` a los `/64`

`2001:db8:13::/48` tiene 80 bits para subredes y hosts. Se reservan los 16 bits
del cuarto hextet para numerar segmentos; cada segmento es un `/64`:

```text
2001:db8:13::/48
├── 2001:db8:13:0::/64     LAN-A
├── 2001:db8:13:16::/64    LAN-B
├── 2001:db8:13:32::/64    LAN-C
├── 2001:db8:13:48::/64    enlace R1–R2
├── 2001:db8:13:52::/64    enlace R2–R3
└── 2001:db8:13:56::/64    enlace R3–R1
```

Cada `/64` tiene `2^64` direcciones. No se calcula `2^h − 2` porque en IPv6 no
hay dirección de red ni de broadcast reservadas: la primera (`::`) y la última
pueden usarse (aunque `::` se evita por claridad).

### Paso 2.2 — Direcciones de los routers

| Router | Interfaz | Prefijo | Dirección IPv6 | Uso |
|--------|----------|---------|----------------|-----|
| R1 | Gi0/0 | `2001:db8:13:0::/64` | `2001:db8:13:0::1` | Gateway LAN-A |
| R1 | Gi0/1 | `2001:db8:13:48::/64` | `2001:db8:13:48::1` | Enlace a R2 |
| R1 | Gi0/2 | `2001:db8:13:56::/64` | `2001:db8:13:56::2` | Enlace a R3 |
| R2 | Gi0/0 | `2001:db8:13:16::/64` | `2001:db8:13:16::1` | Gateway LAN-B |
| R2 | Gi0/1 | `2001:db8:13:48::/64` | `2001:db8:13:48::2` | Enlace a R1 |
| R2 | Gi0/2 | `2001:db8:13:52::/64` | `2001:db8:13:52::1` | Enlace a R3 |
| R3 | Gi0/0 | `2001:db8:13:32::/64` | `2001:db8:13:32::1` | Gateway LAN-C |
| R3 | Gi0/1 | `2001:db8:13:52::/64` | `2001:db8:13:52::2` | Enlace a R2 |
| R3 | Gi0/2 | `2001:db8:13:56::/64` | `2001:db8:13:56::1` | Enlace a R1 |

> **Truco de lectura:** cada dirección es `prefijo + ::1` (o `::2`). No hay
> máscara que memorizar: todo es `/64`.

---

## Parte 3 — Configurar los 3 routers

`ipv6 unicast-routing` es obligatorio: sin él el router no reenvía IPv6 ni
envía Router Advertisements, aunque las interfaces tengan dirección.

### Paso 3.1 — R1 (Sede A / LAN-A)

```text
enable
configure terminal
hostname R1-SEDE-A
no ip domain-lookup
enable secret cisco
service password-encryption
!
ipv6 unicast-routing                    ! habilita el reenvío IPv6 (clave)
!
interface GigabitEthernet0/0            ! LAN-A
 description LAN-A - Gateway IPv6 2001:db8:13:0::1/64
 ipv6 address 2001:db8:13:0::1/64
 no shutdown
!
interface GigabitEthernet0/1            ! enlace a R2
 description Enlace a R2 - 2001:db8:13:48::/64
 ipv6 address 2001:db8:13:48::1/64
 no shutdown
!
interface GigabitEthernet0/2            ! enlace a R3
 description Enlace a R3 - 2001:db8:13:56::/64
 ipv6 address 2001:db8:13:56::2/64
 no shutdown
!
end
copy running-config startup-config
```

### Paso 3.2 — R2 (Sede B / LAN-B)

```text
enable
configure terminal
hostname R2-SEDE-B
no ip domain-lookup
enable secret cisco
service password-encryption
!
ipv6 unicast-routing
!
interface GigabitEthernet0/0            ! LAN-B
 description LAN-B - Gateway IPv6 2001:db8:13:16::1/64
 ipv6 address 2001:db8:13:16::1/64
 no shutdown
!
interface GigabitEthernet0/1            ! enlace a R1
 description Enlace a R1 - 2001:db8:13:48::/64
 ipv6 address 2001:db8:13:48::2/64
 no shutdown
!
interface GigabitEthernet0/2            ! enlace a R3
 description Enlace a R3 - 2001:db8:13:52::/64
 ipv6 address 2001:db8:13:52::1/64
 no shutdown
!
end
copy running-config startup-config
```

### Paso 3.3 — R3 (Sede C / LAN-C)

```text
enable
configure terminal
hostname R3-SEDE-C
no ip domain-lookup
enable secret cisco
service password-encryption
!
ipv6 unicast-routing
!
interface GigabitEthernet0/0            ! LAN-C
 description LAN-C - Gateway IPv6 2001:db8:13:32::1/64
 ipv6 address 2001:db8:13:32::1/64
 no shutdown
!
interface GigabitEthernet0/1            ! enlace a R2
 description Enlace a R2 - 2001:db8:13:52::/64
 ipv6 address 2001:db8:13:52::2/64
 no shutdown
!
interface GigabitEthernet0/2            ! enlace a R1
 description Enlace a R1 - 2001:db8:13:56::/64
 ipv6 address 2001:db8:13:56::1/64
 no shutdown
!
end
copy running-config startup-config
```

### Paso 3.4 — Verificar interfaces

```text
show ipv6 interface brief
```

Salida esperada en R1 (cada interfaz `up/up`, con su link-local `FE80::…` y su
dirección global):

```text
R1#show ipv6 interface brief
GigabitEthernet0/0         [up/up]
    FE80::2D0:97FF:FE5A:1A01
    2001:DB8:13:0::1
GigabitEthernet0/1         [up/up]
    FE80::2D0:97FF:FE5A:1A02
    2001:DB8:13:48::1
GigabitEthernet0/2         [up/up]
    FE80::2D0:97FF:FE5A:1A03
    2001:DB8:13:56::2
```

> La dirección `FE80::…` es la **link-local**: la genera el router solo y sirve
> para hablar con los vecinos del mismo enlace. No se configura y no se enruta.

---

## Parte 4 — DHCPv6: cada router sirve su LAN

### Paso 4.1 — Stateful frente a SLAAC

En IPv6 hay dos formas de dar dirección a un PC:

| Modo | Quién asigna la dirección | Cuándo usarlo |
|------|---------------------------|---------------|
| **SLAAC** | El propio PC, con el prefijo del RA (`ipv6 address autoconfig`) | Redes simples, sin servidor |
| **DHCPv6 stateful** | El router, con un pool (`ipv6 dhcp pool`) | Cuando se quiere control central, DNS y dominio |

Este laboratorio usa **DHCPv6 stateful** para mantener el objetivo de la sesión
IPv4. La interfaz lleva `ipv6 nd managed-config-flag` (bit **M**) para indicar
al PC que pida la dirección por DHCPv6.

### Paso 4.2 — R1

```text
configure terminal
!
ipv6 dhcp pool LAN-A
 address prefix 2001:db8:13:0::/64      ! prefijo que reparte este pool
 dns-server 2001:4860:4860::8888        ! DNS IPv6 (ilustrativo)
 domain-name lab-utp.pa                 ! sufijo de dominio
!
interface GigabitEthernet0/0
 ipv6 nd managed-config-flag            ! bit M: usen DHCPv6 para la dirección
 ipv6 dhcp server LAN-A                 ! asocia el pool a esta interfaz
!
end
copy running-config startup-config
```

### Paso 4.3 — R2

```text
configure terminal
ipv6 dhcp pool LAN-B
 address prefix 2001:db8:13:16::/64
 dns-server 2001:4860:4860::8888
 domain-name lab-utp.pa
!
interface GigabitEthernet0/0
 ipv6 nd managed-config-flag
 ipv6 dhcp server LAN-B
!
end
copy running-config startup-config
```

### Paso 4.4 — R3

```text
configure terminal
ipv6 dhcp pool LAN-C
 address prefix 2001:db8:13:32::/64
 dns-server 2001:4860:4860::8888
 domain-name lab-utp.pa
!
interface GigabitEthernet0/0
 ipv6 nd managed-config-flag
 ipv6 dhcp server LAN-C
!
end
copy running-config startup-config
```

### Paso 4.5 — Qué significa cada comando

| Comando | Significado |
|---------|-------------|
| `ipv6 unicast-routing` | Activa el reenvío IPv6 y los RA (global) |
| `ipv6 dhcp pool NOMBRE` | Crea el pool DHCPv6 |
| `address prefix PREFIJO/64` | Red que reparte el pool |
| `dns-server DIR` | DNS que recibe el PC |
| `domain-name NOMBRE` | Sufijo DNS que recibe el PC |
| `ipv6 nd managed-config-flag` | Bit M del RA: el PC debe usar DHCPv6 para la dirección |
| `ipv6 dhcp server NOMBRE` | Aplica el pool a esa interfaz |

> **No existe `default-router` en DHCPv6.** El gateway se aprende del RA y es la
> link-local del router. Tampoco existe `ipv6 dhcp excluded-address`: el router
> no entrega su propia dirección `::1`.

### Paso 4.6 — Verificar los pools

```text
show ipv6 dhcp pool
show ipv6 dhcp binding
```

`show ipv6 dhcp pool` debe mostrar el prefijo, el DNS y el dominio de cada pool.
`show ipv6 dhcp binding` se llena cuando los PCs piden dirección.

---

## Parte 5 — Verificar el DHCPv6 en los PCs

### Paso 5.1 — Poner los 9 PCs en DHCPv6

En cada PC: `Desktop → IP Configuration`, baja a **IPv6 Configuration** y
selecciona **DHCP** (no "Auto Config"; esa opción es SLAAC). Espera unos
segundos a que aparezca la dirección.

### Paso 5.2 — Comprobar en el PC

En `Desktop → Command Prompt`:

```text
ipconfig /all       ! muestra IPv4 e IPv6; fíjate en la sección IPv6
```

Salida esperada en PC-A1 (la dirección exacta puede variar; el prefijo no):

```text
IPv6 Address. . . . . . . . . . . : 2001:db8:13:0::2
Default Gateway . . . . . . . . . : FE80::2D0:97FF:FE5A:1A01
DNS Server . . . . . . . . . . . : 2001:4860:4860::8888
```

Tres comprobaciones:

1. La dirección empieza por el prefijo de la LAN (`2001:db8:13:0::/64`).
2. El gateway es una **link-local** (`FE80::…`), no la `::1`. Es lo correcto.
3. El DNS es el que configuraste en el pool.

> Anota la dirección IPv6 de cada PC. La usarás en los `ping` de las partes
> siguientes. En los ejemplos se escribe `<IPv6-PC-A1>` para no fijar una
> dirección que depende del orden en que los PCs piden DHCPv6.

### Paso 5.3 — Conectividad local

Desde PC-A1:

```text
ping 2001:db8:13:0::1        ! gateway (debe responder)
ping <IPv6-PC-A2>            ! otro PC de la misma LAN
```

Si el ping al gateway funciona, la LAN y el DHCPv6 están bien; si falla, el
problema es de capa 2 o del pool, no de enrutamiento.

### Paso 5.4 — Leases en el router

```text
show ipv6 dhcp binding      ! qué dirección se entregó y a qué DUID/MAC
```

En PT verás una entrada por PC. Si aparece vacío, el PC no está en modo DHCP o
la interfaz no tiene `ipv6 dhcp server`.

---

## Parte 6 — Fase A: rutas estáticas IPv6

En una malla, cada router necesita **2 rutas** (una por LAN remota). El
siguiente salto es la dirección del vecino en el enlace de salida.

| Router | Destino | Siguiente salto | Interfaz |
|--------|---------|-----------------|----------|
| R1 | `2001:db8:13:16::/64` | `2001:db8:13:48::2` | Gi0/1 |
| R1 | `2001:db8:13:32::/64` | `2001:db8:13:56::1` | Gi0/2 |
| R2 | `2001:db8:13:0::/64` | `2001:db8:13:48::1` | Gi0/1 |
| R2 | `2001:db8:13:32::/64` | `2001:db8:13:52::2` | Gi0/2 |
| R3 | `2001:db8:13:0::/64` | `2001:db8:13:56::2` | Gi0/2 |
| R3 | `2001:db8:13:16::/64` | `2001:db8:13:52::1` | Gi0/1 |

```text
! ---------- R1 ----------
configure terminal
ipv6 route 2001:db8:13:16::/64 2001:db8:13:48::2   ! LAN-B por R2
ipv6 route 2001:db8:13:32::/64 2001:db8:13:56::1   ! LAN-C por R3
end
copy running-config startup-config

! ---------- R2 ----------
configure terminal
ipv6 route 2001:db8:13:0::/64  2001:db8:13:48::1   ! LAN-A por R1
ipv6 route 2001:db8:13:32::/64 2001:db8:13:52::2   ! LAN-C por R3
end
copy running-config startup-config

! ---------- R3 ----------
configure terminal
ipv6 route 2001:db8:13:0::/64  2001:db8:13:56::2   ! LAN-A por R1
ipv6 route 2001:db8:13:16::/64 2001:db8:13:52::1   ! LAN-B por R2
end
copy running-config startup-config
```

### Paso 6.1 — Verificar la tabla

```text
show ipv6 route
show ipv6 route static
```

```text
R1#show ipv6 route
Codes: C - Connected, L - Local, S - Static, O - OSPF Intra

C   2001:DB8:13:0::/64 [0/0]
     via GigabitEthernet0/0, directly connected
L   2001:DB8:13:0::1/128 [0/0]
     via GigabitEthernet0/0, receive
C   2001:DB8:13:48::/64 [0/0]
     via GigabitEthernet0/1, directly connected
L   2001:DB8:13:48::1/128 [0/0]
     via GigabitEthernet0/1, receive
C   2001:DB8:13:56::/64 [0/0]
     via GigabitEthernet0/2, directly connected
L   2001:DB8:13:56::2/128 [0/0]
     via GigabitEthernet0/2, receive
S   2001:DB8:13:16::/64 [1/0]
     via 2001:DB8:13:48::2
S   2001:DB8:13:32::/64 [1/0]
     via 2001:DB8:13:56::1
```

Interpretación: `C` = conectada, `L` = dirección local de la interfaz (`/128`),
`S` = estática. `[1/0]` es distancia administrativa/métrica, igual que en IPv4.

### Paso 6.2 — Conectividad entre sedes

Desde PC-A1 (usa las direcciones que anotaste):

```text
ping <IPv6-PC-B1>      ! LAN-B
ping <IPv6-PC-C1>      ! LAN-C
```

Desde la CLI del router:

```text
ping 2001:db8:13:32::1              ! gateway de LAN-C, sale por el enlace 3
traceroute 2001:db8:13:32::1        ! muestra los saltos
show ipv6 neighbors                ! tabla NDP (el equivalente a ARP)
```

En una malla, LAN-A → LAN-C son **2 saltos** (directo por el enlace 3). Si ves
3, el paquete está pasando por R2.

---

## Parte 7 (opcional) — Fase B: OSPFv3 y RIPng

> Esta parte sustituye a las rutas estáticas. **Borra primero las estáticas**
> (`no ipv6 route …`), porque una ruta estática tiene mejor distancia
> administrativa y taparía las rutas OSPF.

### Paso 7.1 — OSPFv3

En OSPFv3 **no hay `network`**: se activa por interfaz. Además, el `router-id`
es obligatorio si no hay direcciones IPv4.

```text
! ---------- R1 ----------
ipv6 router ospf 1
 router-id 1.1.1.1
 passive-interface GigabitEthernet0/0    ! la LAN no tiene vecinos OSPF
!
interface GigabitEthernet0/0
 ipv6 ospf 1 area 0
interface GigabitEthernet0/1
 ipv6 ospf 1 area 0
interface GigabitEthernet0/2
 ipv6 ospf 1 area 0
!
```

| Router | `router-id` |
|--------|-------------|
| R1 | `1.1.1.1` |
| R2 | `2.2.2.2` |
| R3 | `3.3.3.3` |

Repite el bloque en R2 y R3 con su `router-id` y sus interfaces. Verifica:

```text
show ipv6 ospf neighbor       ! vecinos en estado FULL
show ipv6 route ospf          ! rutas O
show ipv6 protocols
```

Las rutas OSPFv3 muestran el siguiente salto como **link-local**:

```text
O   2001:DB8:13:16::/64 [110/2]
     via FE80::2D0:97FF:FE5A:1A02, GigabitEthernet0/1
```

`FE80::…` es normal: OSPFv3 usa la link-local del vecino, no su dirección
global. Para saber a qué vecino corresponde, cruza `show ipv6 ospf neighbor` con
`show ipv6 interface <interfaz>`.

### Paso 7.2 — RIPng (alternativa para comparar)

```text
! Quita OSPFv3 antes de activar RIPng
no ipv6 router ospf 1
interface GigabitEthernet0/1
 no ipv6 ospf 1 area 0
interface GigabitEthernet0/2
 no ipv6 ospf 1 area 0
!
ipv6 router rip LAB
 passive-interface GigabitEthernet0/0
!
interface GigabitEthernet0/0
 ipv6 rip LAB enable
interface GigabitEthernet0/1
 ipv6 rip LAB enable
interface GigabitEthernet0/2
 ipv6 rip LAB enable
```

En `show ipv6 route` las rutas de RIPng aparecen con `R`. RIPng usa multicast
`FF02::9` y no tiene `network`: también se activa por interfaz.

---

## Parte 8 — Troubleshooting

| Síntoma | Causa probable | Solución |
|---------|----------------|----------|
| `show ipv6 interface brief` sin dirección global | Falta `ipv6 address` o `no shutdown` | Revisa la interfaz |
| El PC no recibe IPv6 | PC en "Auto Config" en vez de "DHCP" | Cámbialo a DHCP |
| El PC no recibe IPv6 (2) | Falta `ipv6 dhcp server` o el prefijo del pool no coincide | Revisa pool e interfaz |
| El PC no tiene gateway | El router no envía RA | Falta `ipv6 unicast-routing` |
| Ping al gateway falla | Interfaz caída o PC en otra subred | `show ipv6 interface brief` |
| Ping entre sedes falla | Falta una ruta estática o el next-hop es el propio | `show ipv6 route` |
| OSPFv3 no forma vecinos | Falta `ipv6 ospf 1 area 0` en una interfaz, o `router-id` repetido | Revisa interfaces y IDs |
| Ruta OSPF no aparece | Hay una estática con mejor AD | Borra la estática |
| No responde el ping a `FE80::` | Falta el zone ID (`%Gi0/0`) | Usa la dirección global para probar |

Comandos de diagnóstico:

```text
show ipv6 interface brief
show ipv6 route
show ipv6 neighbors
show ipv6 dhcp pool
show ipv6 dhcp binding
show ipv6 ospf neighbor
show ipv6 protocols
ping 2001:db8:13:0::1
traceroute 2001:db8:13:32::1
```

---

## Preguntas de la Sesión A (IPv6)

1. ¿Por qué en IPv6 no se calcula `2^h − 2`? ¿Cuántas direcciones tiene un
   `/64` y por qué se usa ese tamaño en las LAN?
2. ¿Por qué el gateway que aparece en `ipconfig` es una `FE80::` y no la
   `2001:db8:13:0::1`? ¿Quién lo entrega?
3. ¿Qué diferencia hay entre **SLAAC** y **DHCPv6 stateful**? ¿Qué bit del RA
   activa cada modo?
4. ¿Por qué DHCPv6 no necesita `default-router`? ¿Qué pasaría si el router no
   enviara RA?
5. ¿Qué indica una ruta `L` en `show ipv6 route`? ¿Por qué su prefijo es `/128`?
6. ¿Qué ventaja tiene OSPFv3 sobre las rutas estáticas en esta malla? ¿Qué
   significa que el next-hop sea `FE80::…`?

## Entregable de la Sesión A (IPv6)

1. Captura de la topología con los 3 routers, 3 switches y 9 PCs (cables en
   verde).
2. Tabla de direccionamiento IPv6 completa (prefijos, gateways y enlaces).
3. `show ipv6 interface brief` de los 3 routers.
4. `show ipv6 dhcp pool` y `show ipv6 dhcp binding` de los 3 routers.
5. `ipconfig /all` de un PC de cada LAN y `ping` cruzado entre las 3 sedes.
6. `show ipv6 route` de R1, R2 y R3 mostrando las rutas `S`.
7. Respuestas a las 6 preguntas.

> Si haces la Parte 7 opcional, añade `show ipv6 ospf neighbor` y
> `show ipv6 route ospf` de los 3 routers.
