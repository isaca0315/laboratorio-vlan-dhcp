# Laboratorio N.º 13 — VLSM, DHCP y Enrutamiento en Packet Tracer

Unidad III · Capa de red · **Cisco Packet Tracer**

## Objetivo general

Diseñar e implementar una red de 3 sedes (LAN-A, LAN-B, LAN-C) sobre la red base
`192.168.2.0/24`, aplicando **subneteo VLSM**, configuring **DHCP** en cada router
y dos fases de enrutamiento (**estático → dinámico con OSPF/RIPv2**).

Al terminar sabrás calcular un plan de direccionamiento sin desperdicio,
configurar un router como servidor DHCP y verificar el comportamiento de la red
con comandos de diagnóstico.

## Materiales

- Cisco Packet Tracer (cuenta de estudiante Cisco NetAcad).
- Este instructivo (`README.md`, `SESION-A.md`, `SESION-B.md`).
- Referencias: [`SUBNETEO.md`](SUBNETEO.md) (máscaras),
  [`COMANDOS.md`](COMANDOS.md) (qué hace cada comando),
  [`DIAGRAMAS.md`](DIAGRAMAS.md) (diagramas para draw.io).
- CLI de los tres routers en `config/` (copiar y pegar).
- Diagramas en Mermaid para draw.io en [`DIAGRAMAS.md`](DIAGRAMAS.md).
- Cálculo de subneteo VLSM en [`SUBNETEO.md`](SUBNETEO.md).
- Qué hace cada comando en [`COMANDOS.md`](COMANDOS.md).

## Cómo se trabaja esta sesión

| Sesión | Qué haces | Entregable breve | Guía |
|--------|-----------|------------------|------|
| **Sesión A** — Topología, VLSM, DHCP y rutas estáticas | Montar la topología (1), calcular el VLSM (2), configurar interfaces y DHCP en los 3 routers (3), configurar rutas estáticas (4) y verificar el DHCP en los PCs (5). | Tabla de direccionamiento completa + `show ip dhcp binding` con 3 leases por router + pings cruzados OK en Fase A. | [Sesión A](SESION-A.md) |
| **Sesión B** — Enrutamiento dinámico y diagnóstico | Quitar las estáticas (1), configurar OSPF área 0 (2), alternativa RIPv2 (3), verificar con `show ip route`/`show ip ospf neighbor` (4) y diagnosticar fallas (5). | `show ip route` con rutas `O`, `show ip ospf neighbor` en FULL y pings OK **con un enlace caído**. | [Sesión B](SESION-B.md) |

## Topología

> **Diagramas listos para draw.io:** topología, enlaces VLSM, flujo DHCP,
> recorrido de un paquete y convergencia OSPF en [`DIAGRAMAS.md`](DIAGRAMAS.md)
> (insertar con *Arrange > Insert > Mermaid*).

Malla (full mesh) de 3 routers: cada router se enlaza con los otros dos. Así el
tráfico entre sedes tiene **dos caminos posibles** y, en la Fase B, se puede
demostrar la **redundancia** de OSPF apagando un enlace.

```text
   LAN-A  192.168.2.0/28        LAN-B  192.168.2.16/28       LAN-C  192.168.2.32/28
   GW .1                        GW .17                        GW .33
   PCs .6 .7 .8                 PCs .22 .23 .24               PCs .38 .39 .40
        │                             │                            │
      SW1 Fa0/1                    SW2 Fa0/1                    SW3 Fa0/1
        │                             │                            │
    R1 Gi0/0                      R2 Gi0/0                     R3 Gi0/0

  Los tres enlaces punto a punto NO salen de los switches: van directo de un
  router a otro, cada uno en su propio par de puertos GigabitEthernet.

  R1 Gi0/1 (.49) ════ enlace 1 ════ R2 Gi0/1 (.50)      192.168.2.48/30
  R2 Gi0/2 (.53) ════ enlace 2 ════ R3 Gi0/1 (.54)      192.168.2.52/30
  R3 Gi0/2 (.57) ════ enlace 3 ════ R1 Gi0/2 (.58)      192.168.2.56/30
```

Resumen de los tres enlaces punto a punto (malla completa):

| Enlace | Subred | Extremo A | Extremo B |
|--------|--------|-----------|-----------|
| Enlace 1 · R1 Gi0/1 ↔ R2 Gi0/1 | 192.168.2.48/30 | R1 = .49 | R2 = .50 |
| Enlace 2 · R2 Gi0/2 ↔ R3 Gi0/1 | 192.168.2.52/30 | R2 = .53 | R3 = .54 |
| Enlace 3 · R3 Gi0/2 ↔ R1 Gi0/2 | 192.168.2.56/30 | R3 = .57 | R1 = .58 |

### Conexionado de interfaces

Los **15 cables** son todos *Copper Straight-Through*. Fíjate en que los
cables 13-15 van **de un router al otro**, sin pasar por un switch:

| # | Cable | Desde | Hasta | Enlace / uso |
|---|-------|-------|-------|--------------|
| 1 | Copper Straight-Through | `R1 Gi0/0` | `SW1 Fa0/1` | LAN-A · gateway .1/28 |
| 2 | Copper Straight-Through | `R2 Gi0/0` | `SW2 Fa0/1` | LAN-B · gateway .17/28 |
| 3 | Copper Straight-Through | `R3 Gi0/0` | `SW3 Fa0/1` | LAN-C · gateway .33/28 |
| 4 | Copper Straight-Through | `PC-A1 Fa0` | `SW1 Fa0/2` | LAN-A |
| 5 | Copper Straight-Through | `PC-A2 Fa0` | `SW1 Fa0/3` | LAN-A |
| 6 | Copper Straight-Through | `PC-A3 Fa0` | `SW1 Fa0/4` | LAN-A |
| 7 | Copper Straight-Through | `PC-B1 Fa0` | `SW2 Fa0/2` | LAN-B |
| 8 | Copper Straight-Through | `PC-B2 Fa0` | `SW2 Fa0/3` | LAN-B |
| 9 | Copper Straight-Through | `PC-B3 Fa0` | `SW2 Fa0/4` | LAN-B |
| 10 | Copper Straight-Through | `PC-C1 Fa0` | `SW3 Fa0/2` | LAN-C |
| 11 | Copper Straight-Through | `PC-C2 Fa0` | `SW3 Fa0/3` | LAN-C |
| 12 | Copper Straight-Through | `PC-C3 Fa0` | `SW3 Fa0/4` | LAN-C |
| 13 | Copper Straight-Through | `R1 Gi0/1` | `R2 Gi0/1` | enlace 1 · 192.168.2.48/30 · .49 ↔ .50 |
| 14 | Copper Straight-Through | `R2 Gi0/2` | `R3 Gi0/1` | enlace 2 · 192.168.2.52/30 · .53 ↔ .54 |
| 15 | Copper Straight-Through | `R3 Gi0/2` | `R1 Gi0/2` | enlace 3 · 192.168.2.56/30 · .57 ↔ .58 |

> Al cablear de router a router, Packet Tracer te deja elegir el tipo de cable.
> Elige **Copper Straight-Through**. (Crossover también funcionaría: las Gi del
> 2911 negocian auto-MDIX.)

> **Variante con enlaces Serial** (opcional, para practicar): en los 2911 inserta
> el módulo `HWIC-2T` (HWIC-2T aparece al apagar el router) y usa `S0/0/0` en
> cada router con cable **Serial DCE**. El lado DCE lleva `clock rate 64000`. El
> resto de la configuración es idéntica; solo cambian los nombres de interfaz.

## Subneteo VLSM paso a paso

> El desarrollo completo del cálculo (por qué `/28` y no `/29`, cómo se alinean
> los bloques, los errores típicos y 6 ejercicios con respuestas) está en
> [`SUBNETEO.md`](SUBNETEO.md). Aquí solo va el resumen.

### 1. Necesidades y prefijo mínimo

| Requisito | Hosts mínimos | Prefijo elegido | Máscara | Total dir. | Hosts útiles | Desperdicio |
|-----------|---------------|-----------------|---------|-----------|--------------|-------------|
| LAN-A | 10 | `/28` | 255.255.255.240 | 16 | 14 | 4 |
| LAN-B | 10 | `/28` | 255.255.255.240 | 16 | 14 | 4 |
| LAN-C | 10 | `/28` | 255.255.255.240 | 16 | 14 | 4 |
| Enlace P2P | 2 | `/30` | 255.255.255.252 | 4 | 2 | 0 |

Cálculo del prefijo LAN: `2^h − 2 ≥ 10` → `h = 4` → `/28` (es el prefijo **más
eficiente** que cumple; un `/29` daría solo 6 hosts y un `/27` desperdiciaría 18).

En el bloque de red: `h = 4` bits de host (16 direcciones) y `h = 2` bits de host
(4 direcciones) respectivamente.

### 2. Máscaras en binario

```text
/28 = 255.255.255.240 = 11111111.11111111.11111111.11110000  (bloque = 16)
/30 = 255.255.255.252 = 11111111.11111111.11111111.11111100  (bloque =  4)
```

### 3. Asignación (de mayor a menor, en múltiplos del bloque)

```text
192.168.2.0/28    red 192.168.2.0     usable .1  - .14    bcast .15   LAN-A
192.168.2.16/28   red 192.168.2.16    usable .17 - .30    bcast .31   LAN-B
192.168.2.32/28   red 192.168.2.32    usable .33 - .46    bcast .47   LAN-C
192.168.2.48/30   red 192.168.2.48    usable .49 - .50    bcast .51   R1 - R2
192.168.2.52/30   red 192.168.2.52    usable .53 - .54    bcast .55   R2 - R3
192.168.2.56/30   red 192.168.2.56    usable .57 - .58    bcast .59   R3 - R1
192.168.2.60 - 192.168.2.255  → reservado para crecimiento (196 direcciones)
```

Consumo total: `3×16 + 3×4 = 60` direcciones de 256 (**76 % libre**).

## Tabla de direccionamiento IP

### Routers

| Dispositivo | Interfaz | Descripción | Dirección IP | Máscara | Prefijo | Gateway |
|-------------|----------|-------------|--------------|---------|---------|---------|
| R1 | Gi0/0 | LAN-A (gateway) | 192.168.2.1 | 255.255.255.240 | /28 | — |
| R1 | Gi0/1 | Enlace a R2 | 192.168.2.49 | 255.255.255.252 | /30 | — |
| R1 | Gi0/2 | Enlace a R3 | 192.168.2.58 | 255.255.255.252 | /30 | — |
| R2 | Gi0/0 | LAN-B (gateway) | 192.168.2.17 | 255.255.255.240 | /28 | — |
| R2 | Gi0/1 | Enlace a R1 | 192.168.2.50 | 255.255.255.252 | /30 | — |
| R2 | Gi0/2 | Enlace a R3 | 192.168.2.53 | 255.255.255.252 | /30 | — |
| R3 | Gi0/0 | LAN-C (gateway) | 192.168.2.33 | 255.255.255.240 | /28 | — |
| R3 | Gi0/1 | Enlace a R2 | 192.168.2.54 | 255.255.255.252 | /30 | — |
| R3 | Gi0/2 | Enlace a R1 | 192.168.2.57 | 255.255.255.252 | /30 | — |

### Pools DHCP y PC (3 por LAN)

| LAN | Red | Gateway (fijo, excluido) | IPs fijas admin (excluidas) | Rango DHCP asignable | PC de ejemplo |
|-----|-----|--------------------------|-----------------------------|----------------------|---------------|
| LAN-A | 192.168.2.0/28 | 192.168.2.1 | .2 – .5 (servidor, impresora, AP, NVR) | **.6 – .14** (9 IPs) | PC-A1 .6 · PC-A2 .7 · PC-A3 .8 |
| LAN-B | 192.168.2.16/28 | 192.168.2.17 | .18 – .21 | **.22 – .30** (9 IPs) | PC-B1 .22 · PC-B2 .23 · PC-B3 .24 |
| LAN-C | 192.168.2.32/28 | 192.168.2.33 | .34 – .37 | **.38 – .46** (9 IPs) | PC-C1 .38 · PC-C2 .39 · PC-C3 .40 |

Las tres primeras exclusiones de cada pool son el **gateway (IP de la interfaz
LAN del router) + las 4 IPs administrativas fijas**. Ninguna IP del rango DHCP
puede repetirse.

### Plan de rutas (Fase A · estático)

| Router | Red destino | Máscara | Siguiente salto | Interfaz de salida |
|--------|-------------|---------|----------------|--------------------|
| R1 | 192.168.2.16 | 255.255.255.240 | 192.168.2.50 | Gi0/1 |
| R1 | 192.168.2.32 | 255.255.255.240 | 192.168.2.57 | Gi0/2 |
| R2 | 192.168.2.0 | 255.255.255.240 | 192.168.2.49 | Gi0/1 |
| R2 | 192.168.2.32 | 255.255.255.240 | 192.168.2.54 | Gi0/2 |
| R3 | 192.168.2.0 | 255.255.255.240 | 192.168.2.58 | Gi0/2 |
| R3 | 192.168.2.16 | 255.255.255.240 | 192.168.2.53 | Gi0/1 |

## Contexto teórico mínimo

- **VLSM**: subredes de tamaños distintos según la necesidad real de cada
  segmento. Se asigna **de mayor a menor** para no fragmentar el espacio.
- **Máscara**: `2^h − 2` = hosts útiles (`−2` = dirección de red y broadcast).
- **Gateway**: es la IP de la interfaz LAN del router; por eso se **excluye** del
  pool DHCP (si no, un PC podría tomarla y aislar la LAN).
- **DORA** del DHCP: **D**iscover (broadcast `255.255.255.255:67`) → **O**ffer →
  **R**equest → **A**ck. Un PC que no obtiene respuesta queda en `169.254.x.x`.
- **Ruta estática**: entrada manual en la tabla de enrutamiento; no se adapta a
  cambios y hay que mantenerla.
- **OSPF**: protocolo de estado de enlace; converge rápido (SPF/Dijkstra),
  detecta enlaces caídos y elige la mejor ruta (menor costo). Sustituye a las
  estáticas cuando hay topología dinámica.
- **`passive-interface`**: evita que el router envíe hellos por una LAN donde no
  hay routers (ahorra tráfico y no ensucia la tabla).

## Rúbrica global (100 puntos)

| Criterio | Puntos |
|----------|--------|
| Topología armada y cableada correctamente (malla completa) | 10 |
| Cálculo VLSM correcto (máscaras, rangos, broadcast) | 15 |
| Tabla de direccionamiento completa y coherente | 10 |
| Interfaces de los 3 routers configuradas y activas | 10 |
| Pools DHCP correctos (exclusiones, gateway, DNS, dominio) | 15 |
| Los 3 PCs de cada LAN recibieron IP por DHCP (`ipconfig /renew`) | 10 |
| Rutas estáticas de Fase A funcionando (ping cruzado OK) | 10 |
| OSPF área 0 convergido y **`show ip route` con rutas `O`** | 10 |
| Evidencia de redundancia (ping OK con un enlace deshabilitado) | 5 |
| Preguntas de reflexión | 5 |
| **Total** | **100** |

## Preguntas de reflexión

1. ¿Por qué `/28` y no `/29` para una LAN de 10 hosts? ¿Cuánta dirección se
   desperdicia con `/27` en lugar de `/28`?
2. Explica qué pasaría si el gateway LAN (`192.168.2.1`) **no** estuviera
   excluido del pool DHCP.
3. ¿Cuántas rutas estáticas hay que escribir si la malla se convierte en una
   cadena (R1–R2–R3)? Explica por qué OSPF escala mejor.
4. ¿Qué diferencia hay entre una ruta `S` y una ruta `O` en
   `show ip route`? ¿Qué indica `[110/2]`?
5. ¿Qué pasa con los pings entre sedes si deshabilitas (`shutdown`) la interfaz
   `R2 Gi0/2`? Compara con el comportamiento de las rutas estáticas.

## Limpieza

En Packet Tracer basta con `File > Close Project` y descartar; si guardaste el
`.pkt`, el estado queda en el archivo. Para reiniciar la configuración desde
cero: en cada router `erase startup-config` + `reload` (responde `yes`).

## Referencias

- Cisco IOS 15.x — Configuring IP Access: DHCP (`ip dhcp pool`, `ip dhcp
  excluded-address`).
- Cisco — OSPFv3/OSPFv2 design guide (`area 0`, `passive-interface`,
  `network ... wildcard`).
- Cisco Networking Academy — *CCNA 1: Introduction to Networks* y *CCNA 2:
  Switching, Routing and Wireless*.