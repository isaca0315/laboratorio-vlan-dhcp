# Sesión B (IPv6) — Red corporativa con VLANs, DHCPv6 y OSPFv3

Laboratorio N.º 13 · Unidad III · **Cisco Packet Tracer**

> **Laboratorio independiente.** Es la versión IPv6 de [`SESION-B.md`](SESION-B.md):
> misma topología hub-and-spoke, mismo cableado y mismas VLAN, pero con
> direccionamiento IPv6, **DHCPv6 por VLAN** y **OSPFv3 área 0** desde el
> principio. No se hereda nada de la Sesión A.

- Escenario: **sede central (R1)** con **dos sucursales (R2 y R3)**.
- Cada sitio se segmenta en **VLAN 10 (usuarios)** y **VLAN 20 (invitados)**.
- El enrutamiento es **OSPFv3 área 0**: **no hay rutas estáticas**.
- Uplinks directos a la central y **enlace de respaldo entre sucursales** con
  costo alto para demostrar la redundancia.

## Qué cambia respecto a la Sesión B IPv4

| Concepto | IPv4 | IPv6 |
|----------|------|------|
| LAN usuarios | `192.168.2.0/28` etc. | `2001:db8:13:0::/64` etc. |
| LAN invitados | `192.168.2.64/28` etc. | `2001:db8:13:64::/64` etc. |
| Enlaces | `/30` | `/64` |
| Asignación | DHCPv4 | **DHCPv6 stateful** |
| Gateway | `default-router` | **RA** (link-local del router) |
| Routing | OSPFv2 (`network`) | **OSPFv3** (`ipv6 ospf` por interfaz) |
| Alternativa | RIPv2 | **RIPng** |
| Tabla | `show ip route` | `show ipv6 route` |
| Vecinos | `show ip ospf neighbor` | `show ipv6 ospf neighbor` |

> **Recordatorio:** DHCPv6 no entrega el gateway; el PC lo aprende del Router
> Advertisement como dirección **link-local** (`FE80::…`). Y Packet Tracer **no
> soporta DHCPv6 relay**, así que cada router es servidor solo de sus propias
> VLAN. Este diseño ya lo cumple.

## Convención de direcciones

Base `2001:db8:13::/48`. El cuarto hextet reutiliza el número del plan IPv4
(`0`, `16`, `32`, `48`, `52`, `56`, `64`, `80`, `96`). No es una conversión: es
una convención para comparar ambos planes.

- En cada LAN/VLAN, el router usa `::1` como gateway.
- En un enlace punto a punto, el extremo de menor número IPv4 usa `::1` y el
  otro `::2`.
- Los PCs reciben su dirección por DHCPv6; anótala con `ipconfig`.

---

## Parte 1 — Estado inicial

Todo arranca **de fábrica**:

1. En los 3 routers, si traen configuración, límpiala:

   ```text
   enable
   erase startup-config
   reload
   ```

   Responde `yes`. Queda como equipo nuevo.

2. Los switches 2960 y los PCs no traen configuración: no hace falta tocarlos
   todavía.
3. Las interfaces GigabitEthernet del 2911 nacen apagadas (rojas): es normal, se
   encienden con `no shutdown` en la Parte 5.

---

## Parte 2 — Montar la topología

El cableado es **idéntico** al de la Sesión B IPv4: los mismos 15 cables
*Copper Straight-Through*.

### Paso 2.1 — Dispositivos

| Cant. | Dispositivo | Nombre |
|-------|-------------|--------|
| 3 | `Router 2911` | R1, R2, R3 |
| 3 | `Switch 2960` | SW1, SW2, SW3 |
| 9 | `PC-PT` | PC-A1…A3, PC-B1…B3, PC-C1…C3 |

### Paso 2.2 — Cableado (15 cables)

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

| Desde | Hasta | Prefijo | Papel |
|-------|-------|---------|-------|
| `R1 Gi0/1` | `R2 Gi0/1` | `2001:db8:13:48::/64` | Uplink SUC-1 (primario) |
| `R2 Gi0/2` | `R3 Gi0/1` | `2001:db8:13:52::/64` | Respaldo entre sucursales |
| `R3 Gi0/2` | `R1 Gi0/2` | `2001:db8:13:56::/64` | Uplink SUC-2 (primario) |

> Todos los cables son *Copper Straight-Through*. Al unir dos routers, elige ese
> tipo (las Gi del 2911 negocian auto-MDIX).

### Paso 2.3 — Comprobación

1. Cada cable muestra **Device / Port** en ambos extremos.
2. Cada router tiene 3 cables: `Gi0/0`, `Gi0/1`, `Gi0/2`.
3. Cada switch tiene 4: `Fa0/1` (router) y `Fa0/2-4` (PCs).

---

## Parte 3 — Plan de direccionamiento IPv6

### Paso 3.1 — Los `/64`

```text
2001:db8:13::/48
├── 2001:db8:13:0::/64     Central · VLAN 10 (usuarios)
├── 2001:db8:13:16::/64    SUC-1 · VLAN 10
├── 2001:db8:13:32::/64    SUC-2 · VLAN 10
├── 2001:db8:13:64::/64    Central · VLAN 20 (invitados)
├── 2001:db8:13:80::/64    SUC-1 · VLAN 20
├── 2001:db8:13:96::/64    SUC-2 · VLAN 20
├── 2001:db8:13:48::/64    enlace R1–R2
├── 2001:db8:13:52::/64    enlace R2–R3
└── 2001:db8:13:56::/64    enlace R3–R1
```

Cada segmento es un `/64`: 64 bits de hosts y ningún broadcast. No hay VLSM.

### Paso 3.2 — Direcciones de los routers

| Router | Rol | Gi0/0 · VLAN 10 | Gi0/0.20 · VLAN 20 | Gi0/1 | Gi0/2 |
|--------|-----|-----------------|--------------------|-------|-------|
| R1 | Central | `:0::1/64` | `:64::1/64` (dot1Q 20) | `:48::1/64` → R2 | `:56::2/64` → R3 |
| R2 | SUC-1 | `:16::1/64` | `:80::1/64` (dot1Q 20) | `:48::2/64` → R1 | `:52::1/64` → R3 |
| R3 | SUC-2 | `:32::1/64` | `:96::1/64` (dot1Q 20) | `:52::2/64` → R2 | `:56::1/64` → R1 |

> Todas las direcciones completas llevan delante `2001:db8:13`. Por ejemplo,
> `:16::1` es `2001:db8:13:16::1`.

### Paso 3.3 — Extremos de los enlaces

| Enlace | Prefijo | Extremo A | Extremo B |
|--------|---------|-----------|-----------|
| Uplink SUC-1 | `2001:db8:13:48::/64` | R1 Gi0/1 `::1` | R2 Gi0/1 `::2` |
| Respaldo | `2001:db8:13:52::/64` | R2 Gi0/2 `::1` | R3 Gi0/1 `::2` |
| Uplink SUC-2 | `2001:db8:13:56::/64` | R3 Gi0/2 `::1` | R1 Gi0/2 `::2` |

---

## Parte 4 — Switches: VLAN 10 y 20

La configuración del switch **no cambia con IPv6**: VLAN y trunk son capa 2.
Usa tal cual los archivos [`config/SW1.txt`](config/SW1.txt),
[`config/SW2.txt`](config/SW2.txt) y [`config/SW3.txt`](config/SW3.txt).

### Paso 4.1 — Crear VLAN (en SW1; igual en SW2 y SW3)

```text
enable
configure terminal
vlan 10
 name USUARIOS-CENTRAL
vlan 20
 name INVITADOS-CENTRAL
end
copy running-config startup-config
```

### Paso 4.2 — Acceso y trunk (SW1)

```text
configure terminal
interface FastEthernet0/2
 switchport mode access
 switchport access vlan 10
interface FastEthernet0/3
 switchport mode access
 switchport access vlan 10
interface FastEthernet0/4
 switchport mode access
 switchport access vlan 20
interface FastEthernet0/1
 switchport mode trunk
 switchport trunk native vlan 10
 switchport trunk allowed vlan 10,20
end
copy running-config startup-config
```

> **La trampa del native.** Si el trunk deja la VLAN nativa por defecto (VLAN 1),
> las tramas sin etiqueta de `Gi0/0` caen en la VLAN 1 y los PCs de la VLAN 10 no
> ven su gateway IPv6. Fija `switchport trunk native vlan 10`.

### Paso 4.3 — Valores de SW2 y SW3

| | SW1 · Central | SW2 · SUC-1 | SW3 · SUC-2 |
|--|---------------|-------------|-------------|
| VLAN 10 | `USUARIOS-CENTRAL` | `USUARIOS-SUC1` | `USUARIOS-SUC2` |
| VLAN 20 | `INVITADOS-CENTRAL` | `INVITADOS-SUC1` | `INVITADOS-SUC2` |
| Fa0/2, Fa0/3 | access VLAN 10 | access VLAN 10 | access VLAN 10 |
| Fa0/4 | access VLAN 20 | access VLAN 20 | access VLAN 20 |
| Fa0/1 | trunk · native 10 · allowed 10,20 | igual | igual |

### Paso 4.4 — Verificar

```text
show vlan brief
show interfaces trunk
```

---

## Parte 5 — Routers: interfaces y subinterfaces

Cada router tiene una dirección IPv6 para la VLAN 10 (en `Gi0/0`) y otra para la
VLAN 20 (en `Gi0/0.20`), más las dos interfaces de enlace. `ipv6 unicast-routing`
es obligatorio.

### Paso 5.1 — R1 (sede central)

```text
enable
configure terminal
hostname R1-SEDE-CENTRAL
no ip domain-lookup
enable secret cisco
service password-encryption
!
ipv6 unicast-routing
!
interface GigabitEthernet0/0          ! VLAN 10 (nativa)
 description CENTRAL - Usuarios VLAN10 GW 2001:db8:13:0::1
 ipv6 address 2001:db8:13:0::1/64
 no shutdown
!
interface GigabitEthernet0/0.20       ! VLAN 20 (etiquetada)
 description CENTRAL - Invitados VLAN20 GW 2001:db8:13:64::1
 encapsulation dot1Q 20
 ipv6 address 2001:db8:13:64::1/64
 no shutdown
!
interface GigabitEthernet0/1          ! uplink SUC-1
 description Uplink SUC-1 - 2001:db8:13:48::/64
 ipv6 address 2001:db8:13:48::1/64
 no shutdown
!
interface GigabitEthernet0/2          ! uplink SUC-2
 description Uplink SUC-2 - 2001:db8:13:56::/64
 ipv6 address 2001:db8:13:56::2/64
 no shutdown
!
end
copy running-config startup-config
```

### Paso 5.2 — Interfaz por interfaz

| Router | Gi0/0 · VLAN 10 | Gi0/0.20 · VLAN 20 | Enlace A | Enlace B |
|--------|-----------------|--------------------|----------|----------|
| R1 Central | `:0::1/64` | `:64::1/64` (dot1Q 20) | Gi0/1 `:48::1` → R2 | Gi0/2 `:56::2` → R3 |
| R2 SUC-1 | `:16::1/64` | `:80::1/64` (dot1Q 20) | Gi0/1 `:48::2` → R1 | Gi0/2 `:52::1` → R3 |
| R3 SUC-2 | `:32::1/64` | `:96::1/64` (dot1Q 20) | Gi0/1 `:52::2` → R2 | Gi0/2 `:56::1` → R1 |

Las configs completas de los tres routers están en
[`config/ipv6/R1.txt`](config/ipv6/R1.txt), `R2.txt` y `R3.txt`.

### Paso 5.3 — Verificar

```text
show ipv6 interface brief
```

```text
R1#show ipv6 interface brief
GigabitEthernet0/0         [up/up]
    FE80::2D0:97FF:FE5A:1A01
    2001:DB8:13:0::1
GigabitEthernet0/0.20      [up/up]
    FE80::2D0:97FF:FE5A:1A04
    2001:DB8:13:64::1
GigabitEthernet0/1         [up/up]
    FE80::2D0:97FF:FE5A:1A02
    2001:DB8:13:48::1
GigabitEthernet0/2         [up/up]
    FE80::2D0:97FF:FE5A:1A03
    2001:DB8:13:56::2
```

> Cada interfaz tiene **dos** direcciones: la link-local `FE80::…` (automática,
> para hablar con vecinos del enlace) y la global `2001:DB8:…` (la que se enruta).

---

## Parte 6 — DHCPv6 por VLAN

Cada VLAN es un `/64`, así que necesita su propio pool DHCPv6. La interfaz lleva
`ipv6 nd managed-config-flag` (bit M) para que el PC pida la dirección por
DHCPv6, y `ipv6 dhcp server` para asociar el pool.

### Paso 6.1 — R1 (sede central, 2 pools)

```text
configure terminal
!
ipv6 dhcp pool VLAN10-CENTRAL
 address prefix 2001:db8:13:0::/64
 dns-server 2001:4860:4860::8888
 domain-name lab-utp.pa
!
ipv6 dhcp pool VLAN20-CENTRAL
 address prefix 2001:db8:13:64::/64
 dns-server 2001:4860:4860::8888
 domain-name lab-utp.pa
!
interface GigabitEthernet0/0
 ipv6 nd managed-config-flag
 ipv6 dhcp server VLAN10-CENTRAL
interface GigabitEthernet0/0.20
 ipv6 nd managed-config-flag
 ipv6 dhcp server VLAN20-CENTRAL
!
end
copy running-config startup-config
```

### Paso 6.2 — Pools por sitio

| Sitio | VLAN 10 · pool | Prefijo | VLAN 20 · pool | Prefijo |
|-------|----------------|---------|----------------|---------|
| Central | `VLAN10-CENTRAL` | `2001:db8:13:0::/64` | `VLAN20-CENTRAL` | `2001:db8:13:64::/64` |
| SUC-1 | `VLAN10-SUC1` | `2001:db8:13:16::/64` | `VLAN20-SUC1` | `2001:db8:13:80::/64` |
| SUC-2 | `VLAN10-SUC2` | `2001:db8:13:32::/64` | `VLAN20-SUC2` | `2001:db8:13:96::/64` |

Repite el bloque de R1 en R2 y R3 con sus prefijos y nombres. En los tres
routers, las dos interfaces (`Gi0/0` y `Gi0/0.20`) llevan el `managed-config-flag`
y su `ipv6 dhcp server`.

> **Diferencias con DHCPv4:** no existe `default-router` (el gateway viene del
> RA) ni `ipv6 dhcp excluded-address` (el router no entrega su propia `::1`).
> Packet Tracer **no soporta DHCPv6 relay**, pero aquí no hace falta: el servidor
> está en la misma VLAN que los PCs.

### Paso 6.3 — Verificar

En los 9 PCs: `Desktop → IP Configuration → IPv6 Configuration → DHCP`. Espera
unos segundos y comprueba:

```text
ipconfig /all
```

```text
IPv6 Address. . . . . . . . . . . : 2001:db8:13:0::2
Default Gateway . . . . . . . . . : FE80::2D0:97FF:FE5A:1A01
DNS Server . . . . . . . . . . . : 2001:4860:4860::8888
```

Los 3 campos críticos: **prefijo correcto de SU VLAN**, **gateway link-local** y
**DNS del pool**. El gateway `FE80::…` es normal; no es un error.

En el router:

```text
show ipv6 dhcp pool
show ipv6 dhcp binding
```

---

## Parte 7 — OSPFv3 área 0 (sin rutas estáticas)

En OSPFv3 **no existe `network`**: se activa por interfaz con
`ipv6 ospf 1 area 0`. El `router-id` es obligatorio porque no hay direcciones
IPv4 de las que tomarlo.

### Paso 7.1 — Configurar los 3 routers

```text
! ---------- R1 (sede central) ----------
configure terminal
ipv6 router ospf 1
 router-id 1.1.1.1
 passive-interface GigabitEthernet0/0
 passive-interface GigabitEthernet0/0.20
!
interface GigabitEthernet0/0
 ipv6 ospf 1 area 0
interface GigabitEthernet0/0.20
 ipv6 ospf 1 area 0
interface GigabitEthernet0/1
 ipv6 ospf 1 area 0
interface GigabitEthernet0/2
 ipv6 ospf 1 area 0
end
!
! ---------- R2 (sucursal 1) ----------
configure terminal
ipv6 router ospf 1
 router-id 2.2.2.2
 passive-interface GigabitEthernet0/0
 passive-interface GigabitEthernet0/0.20
!
interface GigabitEthernet0/0
 ipv6 ospf 1 area 0
interface GigabitEthernet0/0.20
 ipv6 ospf 1 area 0
interface GigabitEthernet0/1
 ipv6 ospf 1 area 0
interface GigabitEthernet0/2
 ipv6 ospf 1 area 0
end
!
! ---------- R3 (sucursal 2) ----------
configure terminal
ipv6 router ospf 1
 router-id 3.3.3.3
 passive-interface GigabitEthernet0/0
 passive-interface GigabitEthernet0/0.20
!
interface GigabitEthernet0/0
 ipv6 ospf 1 area 0
interface GigabitEthernet0/0.20
 ipv6 ospf 1 area 0
interface GigabitEthernet0/1
 ipv6 ospf 1 area 0
interface GigabitEthernet0/2
 ipv6 ospf 1 area 0
end
```

| Router | `router-id` |
|--------|-------------|
| R1 | `1.1.1.1` |
| R2 | `2.2.2.2` |
| R3 | `3.3.3.3` |

### Paso 7.2 — Costes: uplink primario vs respaldo

Cada enlace Gigabit cuesta **1**. Para que el respaldo entre sucursales sea solo
de emergencia, se sube su costo a 100 en **ambos extremos**:

```text
! ---------- R2 (hacia R3, respaldo) ----------
configure terminal
interface GigabitEthernet0/2
 ipv6 ospf cost 100
end
!
! ---------- R3 (hacia R2, respaldo) ----------
configure terminal
interface GigabitEthernet0/1
 ipv6 ospf cost 100
end
```

| Destino desde R2 | Camino preferido | Costo |
|------------------|------------------|-------|
| Central (VLAN 10 y 20) | Directo por R1 | `1 + 1 = 2` |
| Central por el respaldo | R2 → R3 → R1 | `100 + 1 + 1 = 102` |
| SUC-2 (VLAN 10 y 20) | Por la central R2 → R1 → R3 | `1 + 1 + 1 = 3` |
| SUC-2 por el respaldo | Directo R2 → R3 | `100 + 1 = 101` |

> Si tu versión de Packet Tracer no acepta `ipv6 ospf cost`, usa
> `bandwidth 1000` en esa interfaz: el costo pasa a `100000/1000 = 100`.

### Paso 7.3 — Verificar la vecindad

```text
show ipv6 ospf neighbor
```

```text
R1#show ipv6 ospf neighbor

Neighbor ID     Pri   State           Dead Time   Interface ID    Interface
2.2.2.2           1   FULL/DR         00:00:37    3               GigabitEthernet0/1
3.3.3.3           1   FULL/BDR        00:00:35    3               GigabitEthernet0/2
```

**FULL** = vecindad establecida. Los vecinos se identifican por su `router-id`
(`2.2.2.2`, `3.3.3.3`), no por una IP global.

### Paso 7.4 — Verificar la tabla

```text
show ipv6 route
```

```text
R1#show ipv6 route
Codes: C - Connected, L - Local, O - OSPF Intra

C   2001:DB8:13:0::/64 [0/0]
     via GigabitEthernet0/0, directly connected
L   2001:DB8:13:0::1/128 [0/0]
     via GigabitEthernet0/0, receive
C   2001:DB8:13:64::/64 [0/0]
     via GigabitEthernet0/0.20, directly connected
L   2001:DB8:13:64::1/128 [0/0]
     via GigabitEthernet0/0.20, receive
C   2001:DB8:13:48::/64 [0/0]
     via GigabitEthernet0/1, directly connected
L   2001:DB8:13:48::1/128 [0/0]
     via GigabitEthernet0/1, receive
C   2001:DB8:13:56::/64 [0/0]
     via GigabitEthernet0/2, directly connected
L   2001:DB8:13:56::2/128 [0/0]
     via GigabitEthernet0/2, receive
O   2001:DB8:13:16::/64 [110/2]
     via FE80::2D0:97FF:FE5A:1A02, GigabitEthernet0/1
O   2001:DB8:13:80::/64 [110/2]
     via FE80::2D0:97FF:FE5A:1A02, GigabitEthernet0/1
O   2001:DB8:13:32::/64 [110/2]
     via FE80::2D0:97FF:FE5A:1A03, GigabitEthernet0/2
O   2001:DB8:13:96::/64 [110/2]
     via FE80::2D0:97FF:FE5A:1A03, GigabitEthernet0/2
```

Lectura: `C` conectada, `L` dirección local (`/128`), `O` OSPF. `[110/2]` es
distancia administrativa/métrica. El next-hop `FE80::…` es la **link-local del
vecino**: OSPFv3 siempre enruta así, aunque las redes sean globales. Para saber a
qué vecino corresponde, cruza con `show ipv6 ospf neighbor` y
`show ipv6 interface <interfaz>`.

---

## Parte 8 — Redundancia: la prueba clave

1. En R1: `configure terminal` → `interface GigabitEthernet0/1` → `shutdown`
   (cae el uplink de la SUCURSAL 1).
2. Espera ~40 s (detección OSPF).
3. En R2: `show ipv6 route 2001:db8:13:0::/64` — la ruta a la central ahora es
   `[110/102]` y sale por la **link-local de R3**, en lugar de `[110/2]` por la
   de R1.
4. Desde **PC-B1** haz ping a un PC de la central (usa la IPv6 que anotaste):

   ```text
   C:\>ping <IPv6-PC-A1>       ! sigue respondiendo por SUC-1 → SUC-2 → Central
   C:\>tracert <IPv6-PC-A1>    ! camino nuevo: gateway SUC-1 → R3 → R1
   ```

5. Restaura el enlace:

   ```text
   interface GigabitEthernet0/1
    no shutdown
   ```

Al volver, OSPFv3 detecta el vecino y **regresa al camino primario** (costo 2):
`show ipv6 route 2001:db8:13:0::/64` debe mostrar otra vez la link-local de R1.

> Con rutas estáticas esta recuperación no existe. OSPFv3 converge solo y elige
> el camino de menor costo.

---

## Parte 9 — Alternativa: RIPng (opcional, para comparar)

```text
! ---------- R1 ----------
configure terminal
no ipv6 router ospf 1         ! apaga OSPFv3: esta es la alternativa
!
interface GigabitEthernet0/0
 no ipv6 ospf 1 area 0
interface GigabitEthernet0/0.20
 no ipv6 ospf 1 area 0
interface GigabitEthernet0/1
 no ipv6 ospf 1 area 0
interface GigabitEthernet0/2
 no ipv6 ospf 1 area 0
!
ipv6 router rip LAB
 passive-interface GigabitEthernet0/0
 passive-interface GigabitEthernet0/0.20
!
interface GigabitEthernet0/0
 ipv6 rip LAB enable
interface GigabitEthernet0/0.20
 ipv6 rip LAB enable
interface GigabitEthernet0/1
 ipv6 rip LAB enable
interface GigabitEthernet0/2
 ipv6 rip LAB enable
end
! repetir en R2 y R3
```

| Comando | Por qué |
|---------|---------|
| `ipv6 router rip LAB` | Crea el proceso RIPng (nombre local) |
| `ipv6 rip LAB enable` | Activa RIPng **por interfaz** (no hay `network`) |
| `passive-interface` | No envía RIPng por las LAN, solo por los enlaces |

Verificación: `show ipv6 route` mostrará rutas `R` con `[120/2]` (distancia 120).
RIPng puede tardar **1-3 minutos** en converger en Packet Tracer.

| Característica | OSPFv3 | RIPng |
|----------------|--------|-------|
| Tipo | Estado de enlace | Vector de distancia |
| Distancia administrativa | 110 | 120 |
| Convergencia | Rápida (SPF) | Lenta (temporizadores) |
| Métrica | Costo por ancho de banda | Saltos (máx. 15) |
| Configuración | Por interfaz (`ipv6 ospf 1 area 0`) | Por interfaz (`ipv6 rip enable`) |
| Next-hop | Link-local del vecino | Link-local del vecino |

Para volver a OSPFv3: `no ipv6 router rip LAB` y repetir la Parte 7.

---

## Parte 10 — Checklist final

| # | Comando | Dónde | Resultado esperado |
|---|---------|-------|--------------------|
| 1 | `show ipv6 interface brief` | R1, R2, R3 | Gi0/0, Gi0/0.20, Gi0/1 y Gi0/2 `up/up` con global |
| 2 | `show vlan brief` | SW1, SW2, SW3 | VLAN 10 y 20; Fa0/4 en la 20 |
| 3 | `show interfaces trunk` | SW1, SW2, SW3 | Fa0/1 trunk, native 10, allowed 10,20 |
| 4 | `show ipv6 dhcp pool` | R1, R2, R3 | 2 pools por router |
| 5 | `show ipv6 dhcp binding` | R1, R2, R3 | leases de VLAN 10 y VLAN 20 |
| 6 | `ipconfig /all` | 1 PC de cada VLAN | prefijo correcto + gateway `FE80::` + DNS |
| 7 | `show ipv6 route` | R1, R2, R3 | rutas `O` y **sin** `S` |
| 8 | `show ipv6 route <prefijo central>` | R2 | por R1 en normal y por R3 con el uplink caído |
| 9 | `show ipv6 ospf neighbor` | R1, R2, R3 | 2 vecinos en **FULL** |
| 10 | `ping` cruzado entre sitios | PC | OK entre las 3 sedes |
| 11 | `shutdown` del uplink SUC-1 | R1 Gi0/1 | el ping sigue OK por el respaldo |

---

## Parte 11 — Troubleshooting: los 8 errores típicos

| Síntoma | Causa probable | Solución |
|---------|----------------|----------|
| Interfaz `administratively down` | Falta `no shutdown` | `interface Gi0/x` → `no shutdown` |
| PC sin IPv6 | Está en "Auto Config" (SLAAC) en vez de DHCP | Cámbialo a **DHCP** |
| PC sin IPv6 (2) | Falta `ipv6 dhcp server` o el prefijo del pool no coincide | `show ipv6 dhcp pool`, revisar interfaz |
| PC sin gateway | Falta `ipv6 unicast-routing` (no hay RA) | Actívalo en el router |
| PC con IPv6 pero sin ping al gateway | Interfaz caída o PC en otra VLAN/prefijo | `show ipv6 interface brief` |
| Ping al gateway OK, a otra VLAN falla | OSPFv3 no activo en una interfaz o falta la subinterfaz | `show ipv6 route`, `show ipv6 ospf interface brief` |
| `show ipv6 ospf neighbor` vacío | `router-id` duplicado, área distinta o enlace caído | Revisa IDs y `ipv6 ospf 1 area 0` |
| No aparece una VLAN de los vecinos | `passive-interface` puesto en un enlace, o falta `ipv6 ospf` en `Gi0/0.20` | `show ipv6 ospf interface brief` |
| RIPng no anuncia | Falta `ipv6 rip LAB enable` en una interfaz | Actívalo en todas las interfaces de router |

### Comando de rescate

```text
enable
erase startup-config
reload
```

Tras el reset, vuelve a la Parte 4.

---

## Preguntas de la Sesión B (IPv6)

1. En `[110/2]`, ¿qué significan los dos números? ¿Por qué OSPFv3 usa la
   link-local del vecino como next-hop y no su dirección global?
2. ¿Por qué el tráfico entre sucursales pasa por la central y no por el enlace
   R2–R3? ¿Qué comando lo provoca?
3. Con el uplink de la SUC-1 caído, ¿qué camino toma un paquete de PC-B1 a la
   central? Describe el `tracert` esperado (los saltos serán direcciones IPv6).
4. ¿Qué pasa si quitas `passive-interface GigabitEthernet0/0` en R1? ¿Y si lo
   pones en `Gi0/1`?
5. ¿Por qué DHCPv6 no tiene `default-router`? ¿De dónde saca el PC su gateway?
6. Compara OSPFv3 y RIPng: distancia administrativa, métrica y convergencia.
   ¿Cuál usarías en una red de 50 routers?
7. Un PC de la VLAN 10 obtiene una dirección de la VLAN 20. ¿Qué revisaste y con
   qué `show` lo detectaste?
8. ¿Qué diferencia hay entre `show ipv6 route` y `show ipv6 protocols`?

## Entregable de la Sesión B (IPv6)

1. Captura de la topología completa (central + 2 sucursales, cables en verde).
2. `show vlan brief` y `show interfaces trunk` de un switch.
3. `show ipv6 interface brief` de los 3 routers (4 interfaces cada uno).
4. `show ipv6 dhcp pool` y `show ipv6 dhcp binding` de los 3 routers.
5. `ipconfig /all` de un PC de cada VLAN.
6. `show ipv6 route` de R1 y R2 con rutas `O` (y **sin** `S`).
7. `show ipv6 ospf neighbor` de los 3 routers en `FULL`.
8. Evidencia de redundancia: `ping` OK desde PC-B1 con `R1 Gi0/1` en `shutdown`
   y `tracert` mostrando el camino por el respaldo.
9. Respuestas a las 8 preguntas.
