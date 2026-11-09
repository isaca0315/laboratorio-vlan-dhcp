# Laboratorio N.º 13 — VLSM, DHCP y Enrutamiento en Packet Tracer

Unidad III · Capa de red · **Cisco Packet Tracer**

## Objetivo general

El laboratorio tiene **dos sesiones independientes** sobre la red base
`192.168.2.0/24`, aplicando **subneteo VLSM** y **DHCP**:

- **Sesión A** — malla de 3 sedes (LAN-A/B/C): VLSM, DHCP y dos fases de
  enrutamiento (**estático → dinámico con OSPF/RIPv2**).
- **Sesión B** — red corporativa **sede central + 2 sucursales** (hub-and-spoke)
  montada desde cero: VLAN 10/20, DHCP por VLAN y **OSPF área 0 directo** (sin
  rutas estáticas) con prueba de redundancia.

Cada sesión tiene además su **versión IPv6**: misma topología y cableado, `/64`
por segmento, **DHCPv6**, rutas estáticas en A y **OSPFv3** en B.

Al terminar sabrás calcular un plan de direccionamiento sin desperdicio,
configurar un router como servidor DHCP por VLAN y verificar el comportamiento de
la red con comandos de diagnóstico.

## Cómo se trabaja esta sesión

| Sesión | Qué haces | Entregable breve | Guía |
|--------|-----------|------------------|------|
| **Sesión A** — Topología, VLSM, DHCP y rutas estáticas | Montar la topología (1), calcular el VLSM (2), configurar interfaces y DHCP en los 3 routers (3), configurar rutas estáticas (4) y verificar el DHCP en los PCs (5). | Tabla de direccionamiento completa + `show ip dhcp binding` con 3 leases por router + pings cruzados OK en Fase A. | [Sesión A](SESION-A.md) |
| **Sesión B** — Red corporativa con OSPF (independiente) | Montar la topología sede central + 2 sucursales (1), plan VLSM de referencia (2), VLAN 10/20 y DHCP por VLAN (3-5), OSPF área 0 con costes (6-7), probar la redundancia apagando un uplink (8), alternativa RIPv2 (9) y diagnóstico (10-11). | `show ip route` con rutas `O` y **sin** `S`, 2 vecinos OSPF en `FULL` y pings OK **con el uplink de una sucursal caído**. | [Sesión B](SESION-B.md) |
| **Sesión A IPv6** — Misma malla con `/64` y DHCPv6 | Repetir la Sesión A con IPv6: `/64` por segmento (sin VLSM), DHCPv6 en cada router, rutas estáticas `ipv6 route` y, opcional, OSPFv3/RIPng. | Tabla de prefijos `/64`, `show ipv6 dhcp binding` y pings cruzados. | [Sesión A IPv6](SESION-A-IPV6.md) |
| **Sesión B IPv6** — Hub-and-spoke con DHCPv6 y OSPFv3 | Repetir la Sesión B con IPv6: mismo cableado y VLANs, dos pools DHCPv6 por router, OSPFv3 área 0 con costo 100 en el respaldo y prueba de redundancia. | `show ipv6 route` con rutas `O` y **sin** `S`, vecinos OSPFv3 en `FULL` y pings OK con el uplink caído. | [Sesión B IPv6](SESION-B-IPV6.md) |

## Materiales

- Cisco Packet Tracer (cuenta de estudiante Cisco NetAcad).
- Guías de las cuatro sesiones: [`SESION-A.md`](SESION-A.md),
  [`SESION-B.md`](SESION-B.md), [`SESION-A-IPV6.md`](SESION-A-IPV6.md) y
  [`SESION-B-IPV6.md`](SESION-B-IPV6.md).
- Configuraciones de routers y switches para copiar y pegar en `config/`
  (`R1.txt`…`R3.txt`, `SW1.txt`…`SW3.txt`) y en `config/ipv6/`.
- Referencias: [`SUBNETEO.md`](SUBNETEO.md) (cálculo VLSM y ejercicios),
  [`COMANDOS.md`](COMANDOS.md) (qué hace cada comando),
  [`DIAGRAMAS.md`](DIAGRAMAS.md) (diagramas Mermaid para draw.io).
- Proyectos Packet Tracer ya armados y verificados en `packet-tracer/`:
  `Sesion-A-IPv4.pkt`, `Sesion-A-IPv6.pkt`, `Sesion-B-IPv4.pkt` y
  `Sesion-B-IPv6.pkt`. Son locales: `*.pkt` está en `.gitignore`.
- Teoría en [`TEORIA-LAB-VLSM-DHCP.md`](TEORIA-LAB-VLSM-DHCP.md) y en
  [`Teoria-Lab-VLSM-DHCP.pptx`](Teoria-Lab-VLSM-DHCP.pptx).
- Presentación de la Sesión B en [`SESION-B-PPT.md`](SESION-B-PPT.md) y
  [`Sesion-B.pptx`](Sesion-B.pptx).

## Topología

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

  R1 Gi0/1 (.49) ════ enlace 1 ════ R2 Gi0/1 (.50)      192.168.2.48/30
  R2 Gi0/2 (.53) ════ enlace 2 ════ R3 Gi0/1 (.54)      192.168.2.52/30
  R3 Gi0/2 (.57) ════ enlace 3 ════ R1 Gi0/2 (.58)      192.168.2.56/30
```

Los tres enlaces punto a punto **no salen de los switches**: van directo de un
router a otro. Los 15 cables son *Copper Straight-Through*.

- **Sesión A:** cableado completo en
  [`SESION-A.md`](SESION-A.md) (Parte 1, Paso 1.2) y diagramas en
  [`DIAGRAMAS.md`](DIAGRAMAS.md).
- **Sesión B:** es un laboratorio independiente con **la misma estructura de
  cables e IPs, pero roles distintos** — R1 = sede central, R2 y R3 = sucursales,
  y el enlace 2 (R2↔R3) como respaldo de costo alto. Detalle en
  [`SESION-B.md`](SESION-B.md).

## Direccionamiento

| Dispositivo | Interfaz | Descripción | Dirección IP | Máscara | Prefijo |
|-------------|----------|-------------|--------------|---------|---------|
| R1 | Gi0/0 | LAN-A (gateway) | 192.168.2.1 | 255.255.255.240 | /28 |
| R1 | Gi0/1 | Enlace a R2 | 192.168.2.49 | 255.255.255.252 | /30 |
| R1 | Gi0/2 | Enlace a R3 | 192.168.2.58 | 255.255.255.252 | /30 |
| R2 | Gi0/0 | LAN-B (gateway) | 192.168.2.17 | 255.255.255.240 | /28 |
| R2 | Gi0/1 | Enlace a R1 | 192.168.2.50 | 255.255.255.252 | /30 |
| R2 | Gi0/2 | Enlace a R3 | 192.168.2.53 | 255.255.255.252 | /30 |
| R3 | Gi0/0 | LAN-C (gateway) | 192.168.2.33 | 255.255.255.240 | /28 |
| R3 | Gi0/1 | Enlace a R2 | 192.168.2.54 | 255.255.255.252 | /30 |
| R3 | Gi0/2 | Enlace a R1 | 192.168.2.57 | 255.255.255.252 | /30 |

| LAN | Red | Gateway (fijo, excluido) | IPs fijas admin (excluidas) | Rango DHCP asignable | PC de ejemplo |
|-----|-----|--------------------------|-----------------------------|----------------------|---------------|
| LAN-A | 192.168.2.0/28 | 192.168.2.1 | .2 – .5 (servidor, impresora, AP, NVR) | **.6 – .14** (9 IPs) | PC-A1 .6 · PC-A2 .7 · PC-A3 .8 |
| LAN-B | 192.168.2.16/28 | 192.168.2.17 | .18 – .21 | **.22 – .30** (9 IPs) | PC-B1 .22 · PC-B2 .23 · PC-B3 .24 |
| LAN-C | 192.168.2.32/28 | 192.168.2.33 | .34 – .37 | **.38 – .46** (9 IPs) | PC-C1 .38 · PC-C2 .39 · PC-C3 .40 |

Las exclusiones de cada pool son el **gateway + las 4 IPs administrativas fijas**.
Ninguna IP del rango DHCP puede repetirse.

En la **Sesión B** los routers suman la subinterfaz `Gi0/0.20` (VLAN 20,
invitados) y cambian de rol; el enlace 2 pasa a ser el respaldo entre sucursales:

| Router | Rol (Sesión B) | Gi0/0.20 · VLAN 20 | Pool VLAN 20 | Rango DHCP |
|--------|----------------|--------------------|--------------|------------|
| R1 | Sede central | .65/28 (dot1Q 20) | `VLAN20-CENTRAL` | .70 – .78 |
| R2 | Sucursal 1 | .81/28 (dot1Q 20) | `VLAN20-SUC1` | .86 – .94 |
| R3 | Sucursal 2 | .97/28 (dot1Q 20) | `VLAN20-SUC2` | .102 – .110 |

El plan de rutas estáticas de la Fase A y los rangos completos están en
[`SESION-A.md`](SESION-A.md); el desarrollo del cálculo VLSM, en
[`SUBNETEO.md`](SUBNETEO.md).

## Presentaciones

- [`Teoria-Lab-VLSM-DHCP.pptx`](Teoria-Lab-VLSM-DHCP.pptx) — 31 diapositivas
  (16:9) con notas del orador: IP y CIDR, VLSM, switch/router/ARP, DHCP, rutas,
  OSPF/RIPv2, verificación y checklist. El texto equivalente está en
  [`TEORIA-LAB-VLSM-DHCP.md`](TEORIA-LAB-VLSM-DHCP.md).
- [`Sesion-B.pptx`](Sesion-B.pptx) — 26 diapositivas con notas del orador: hub-and-spoke,
  VLAN y router-on-a-stick, DHCP por VLAN, OSPF con costes, redundancia y RIPv2.
  El texto equivalente está en [`SESION-B-PPT.md`](SESION-B-PPT.md).

Se regeneran con `python3 tools/build_teoria_lab.py` y
`python3 tools/build_sesion_b.py`. El layout se verifica con
`python3 tools/check_layout.py <archivo>.pptx`.

## Automatización con Packet Tracer (MCP)

[`MCP-PACKET-TRACER.md`](MCP-PACKET-TRACER.md) explica cómo está configurado
`pktctl`, el servidor MCP que maneja Packet Tracer desde **Claude Desktop** u
**OpenCode**: crear topologías, cablear, escribir comandos IOS, ejecutar
ping/traceroute y verificar DHCP y OSPF sin usar el ratón. Incluye los pasos para
Windows y Linux, el registro `.pta` y la solución de problemas.

Hacen falta solo el JSON del cliente y el registro `.pta`. Requiere Packet
Tracer 9.0.1 abierto.

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
