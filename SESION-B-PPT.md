
## 1. Sesión B — Red corporativa con OSPF

> UNIVERSIDAD TECNOLÓGICA DE PANAMÁ · FACULTAD DE INGENIERÍA DE SISTEMAS COMPUTACIONALES

Sede central + 2 sucursales · VLANs · DHCP por VLAN · laboratorio independiente

- Hub-and-spoke: la sede central R1 y las sucursales R2 y R3
- VLAN 10 (usuarios) y VLAN 20 (invitados) con router-on-a-stick
- OSPF área 0 directo, costes primario/respaldo y prueba de redundancia

<details><summary>Notas del orador</summary>

⏱ 0-3 min · Apertura.

Esta sesión NO depende de la Sesión A: se parte de equipos de fábrica y
se construye una red completa nueva. Escenario: una sede central (R1) y
dos sucursales (R2 y R3), cada sitio partido en VLAN 10 (usuarios) y
VLAN 20 (invitados), con DHCP por VLAN y OSPF área 0 como único
protocolo (no hay rutas estáticas).

Idea de arranque: en una red real las sedes no se conectan escribiendo
rutas a mano; descubren los caminos solas. Hoy demostramos que la red
sobrevive a la caída de un enlace sin que nadie toque nada.

</details>

---

## 2. Qué vamos a ver

> Seis partes: del escenario al diagnóstico de una red independiente

| # | Parte | Qué haces | Min |
|---|---|---|---|
| 1 | Escenario y topología | Roles central/sucursales, 15 cables, reset de fábrica | 10 |
| 2 | Direccionamiento | El plan VLSM de referencia (tabla dada) | 5 |
| 3 | VLAN y DHCP | VLAN 10/20 en switches, subinterfaces y pool por VLAN | 30 |
| 4 | OSPF área 0 | Enrutamiento dinámico directo, costes y redundancia | 40 |
| 5 | RIPv2 (alternativa) | Comparar con OSPF en la misma topología | 10 |
| 6 | Verificación y diagnóstico | Checklist final y los 8 errores típicos | 30 |
| — | Preguntas | Reflexión y entregable de la sesión | 25 |

**La regla de la sesión**
- **Nada se hereda, todo se construye aquí.** Si algo falla, se diagnostica por capas desde el cable.
- Cada parte depende de la anterior: sin el trunk y la subinterfaz no hay VLAN 20; sin la subinterfaz no hay pool; sin OSPF no hay redundancia.
- Al terminar debes poder demostrar que **la red sobrevive a la caída de un uplink**.

<details><summary>Notas del orador</summary>

⏱ 3-4 min · Mapa de la sesión.

Enmarca el orden: primero se monta y se segmenta con VLANs, después se
vuelve dinámico el enrutamiento con OSPF, y al final se aprende a
diagnosticar.

A diferencia de la Sesión A, aquí no hay fase estática: OSPF se
configura directamente y el contraste con las estáticas es solo teoría.

</details>

---

## 3. Escenario y topología

Una sede central y dos sucursales, montado desde cero

- R1 sede central · R2 sucursal 1 · R3 sucursal 2, con uplinks a la central
- Un enlace de respaldo entre sucursales para la redundancia
- Cablear los 15 cables y empezar con equipos de fábrica
- Nada que ver con la parte A: no se hereda configuración

10 min

<details><summary>Notas del orador</summary>

⏱ 4-5 min · Transición.

Primera parte corta. La clave: la topología cambia. Ya no hay tres sedes
equivalentes en malla: ahora hay una central y dos sucursales, y el
enlace entre sucursales existe solo como respaldo.

Esto es lo que hace que OSPF tenga sentido: hay más de un camino y la
red debe elegir y re-elegir.

</details>

---

## 4. La red: una central y dos sucursales

> Cada sitio tiene usuarios (VLAN 10) e invitados (VLAN 20)

| Router | Rol | VLAN 10 · GW | VLAN 20 · GW |
|---|---|---|---|
| R1 | Sede central | .1/28 | .65/28 |
| R2 | Sucursal 1 | .17/28 | .81/28 |
| R3 | Sucursal 2 | .33/28 | .97/28 |

| Enlace | Subred | Extremos |
|---|---|---|
| Uplink SUC-1 | 192.168.2.48/30 | R1 .49 ↔ R2 .50 |
| Respaldo R2–R3 | 192.168.2.52/30 | R2 .53 ↔ R3 .54 |
| Uplink SUC-2 | 192.168.2.56/30 | R3 .57 ↔ R1 .58 |

**Hub-and-spoke**
- Las sucursales hablan con el mundo **a través de R1**.
- Es el camino normal (bajo costo).
- Más realista que tres sedes iguales: hay una central.

**El enlace R2–R3 es el respaldo**
- Su costo se sube (Parte 4) para que no compita con los uplinks.
- Solo se usa si cae un uplink de una sucursal.
- Es ahí donde se demuestra la redundancia OSPF.

**Cada PC de la tabla anterior sigue igual: PC-A/B/C con 2 en VLAN 10 y 1 en VLAN 20.**

<details><summary>Notas del orador</summary>

⏱ 5-8 min.

Recorre la tabla de routers: cada sitio conserva su subred /28 de
usuarios y suma otra /28 para invitados.

El cambio conceptual: R2 y R3 suben a R1 (hub-and-spoke), y el enlace
R2-R3 queda como camino de emergencia. Ahí está la gracia de OSPF:
sin él, ese enlace de respaldo sería cable de adorno.

</details>

---

## 5. Montar la topología desde cero

> 15 cables y equipos de fábrica: esto es un lab independiente

| Tramo | Cables | Qué conecta |
|---|---|---|
| Gateway → switch | 3 | R1 Gi0/0 → SW1 Fa0/1, y análogo en R2, R3 |
| PC → switch | 9 | 3 PCs por sitio (Fa0/2, Fa0/3, Fa0/4) |
| Router → router | 3 | .48/30, .52/30 y .56/30 (directo, sin switch) |

**Empezar de fábrica**
- Routers: `erase startup-config` + `reload` (responde yes).
- Switches 2960 y PCs: sin configuración por defecto.
- Las interfaces Gi nacen apagadas (rojas): es normal.

**Comprobar el cableado**
- Cada router tiene sus 3 cables (Gi0/0, Gi0/1, Gi0/2).
- Cada switch tiene 4: Fa0/1 (router) y Fa0/2-4 (PCs).
- Los cables se ponen en verde recién en la Parte 3.

**Los cables entre routers no pasan por ningún switch**
- Son enlaces de capa 2 punto a punto con su propia subred /30.
- Los tres juntos son el corazón de la topología: dos caminos desde cada sucursal hacia la central.

<details><summary>Notas del orador</summary>

⏱ 8-12 min.

Insistir en el reset: es lo que hace que el laboratorio sea
independiente. Si no borran la config de un router usado antes, se
arrastran IPs y rutas viejas.

Los 15 cables son los mismos números de siempre, pero la narrativa
cambió: dos de los tres enlaces entre routers son uplinks a la central
y el tercero es un respaldo.

</details>

---

## 6. Direccionamiento

El plan VLSM de referencia (ya calculado)

- La tabla de 9 subredes está dada: se copia, no se recalcula
- VLAN 10 y VLAN 20 por sitio: dos /28 por router
- Tres /30 para los enlaces: .48, .52 y .56
- Cualquier IP que escribas debe caer en su rango

5 min

<details><summary>Notas del orador</summary>

⏱ 12-13 min · Transición.

El cálculo completo está en SUBNETEO.md. Aquí solo se entrega la tabla
para trabajar rápido y sin equivocarse.

Única novedad frente a otros labs: las VLAN 20 usan las subredes .64,
.80 y .96, que encajan justo después de los tres enlaces /30.

</details>

---

## 7. Plan VLSM de referencia

> 9 subredes sobre 192.168.2.0/24 · se toma tal cual

| Subred | Red | Rango útil | Uso |
|---|---|---|---|
| 192.168.2.0/28 | .0 | .1 – .14 | Central · VLAN 10 · GW .1 |
| 192.168.2.16/28 | .16 | .17 – .30 | SUC-1 · VLAN 10 · GW .17 |
| 192.168.2.32/28 | .32 | .33 – .46 | SUC-2 · VLAN 10 · GW .33 |
| 192.168.2.48/30 | .48 | .49 – .50 | Uplink SUC-1 (R1–R2) |
| 192.168.2.52/30 | .52 | .53 – .54 | Respaldo (R2–R3) |
| 192.168.2.56/30 | .56 | .57 – .58 | Uplink SUC-2 (R3–R1) |
| 192.168.2.64/28 | .64 | .65 – .78 | Central · VLAN 20 · GW .65 |
| 192.168.2.80/28 | .80 | .81 – .94 | SUC-1 · VLAN 20 · GW .81 |
| 192.168.2.96/28 | .96 | .97 – .110 | SUC-2 · VLAN 20 · GW .97 |

**Verificación rápida de cualquier IP**
- Un /28 empieza en múltiplo de 16 (0, 16, 32, 64, 80, 96) y un /30 en múltiplo de 4 (48, 52, 56).
- Los enlaces /30 ocupan de .48 a .59; las VLAN 20 saltan a .64 en adelante.
- De .112 a .255 queda reservado para crecer.

<details><summary>Notas del orador</summary>

⏱ 13-18 min.

Recorrer la tabla por bloques: los seis /28 (tres de usuarios, tres de
invitados) y los tres /30 de enlaces.

Subrayar la regla de los múltiplos: es la que permite darse cuenta si
una IP está mal antes de configurarla.

Dejar claro que el cálculo está documentado en SUBNETEO.md para quien
quiera entenderlo.

</details>

---

## 8. VLAN y DHCP

Segmentar cada sede y servir dos VLANs con un solo cable

- Switches: crear VLAN 10 y 20, puertos access y un trunk
- La trampa del native: si no se fija, el gateway queda en la VLAN 1
- Router-on-a-stick: subinterfaz .20 con encapsulation dot1Q
- Un pool DHCP por VLAN y la verificación con pings

30 min

<details><summary>Notas del orador</summary>

⏱ 18-19 min · Transición.

Hasta aquí solo topología e IPs. Ahora cada sede deja de ser una LAN
plana y se parte en dos dominios de broadcast.

Todo lo de esta parte es nuevo para esta sesión (no viene de la A):
VLANs, trunk, subinterfaces y el segundo pool.

</details>

---

## 9. Switches: VLAN 10 y 20

> Primero se crea la VLAN, después se asigna el puerto

```text
SW1(config)# vlan 10
SW1(config-vlan)# name USUARIOS-CENTRAL
SW1(config-vlan)# vlan 20
SW1(config-vlan)# name INVITADOS-CENTRAL
SW1(config)# interface Fa0/2        ! PC-A1
SW1(config-if)# switchport mode access
SW1(config-if)# switchport access vlan 10
SW1(config-if)# interface Fa0/4     ! PC-A3 (invitados)
SW1(config-if)# switchport access vlan 20
SW1(config-if)# interface Fa0/1     ! hacia R1
SW1(config-if)# switchport mode trunk
SW1(config-if)# switchport trunk native vlan 10
SW1(config-if)# switchport trunk allowed vlan 10,20
```

**Access vs trunk**
- **access**: un puerto, un VLAN (un PC).
- **trunk**: lleva las 2 VLAN etiquetadas (hacia el router).

**Dos dominios de broadcast**
- PC-A1 y PC-A2 se ven entre sí (VLAN 10).
- PC-A3 ya no los ve (VLAN 20): ese aislamiento es el objetivo.
- Fa0/2 y Fa0/3 en VLAN 10 · Fa0/4 en VLAN 20.

**La trampa del native VLAN**
- Por defecto, la **native** de un trunk es la **VLAN 1** y viaja **sin etiqueta**.
- La IP de `Gi0/0` del router llega sin etiqueta: con el native por defecto cae en la VLAN 1, en una subred que no existe.
- Se fija `switchport trunk native vlan 10`: así la VLAN 10 viaja sin etiqueta y coincide con el gateway.
- Comprobación: `show interfaces trunk` debe ver `Native vlan 10` y `allowed 10,20`.

En SW2 y SW3 es idéntico, con nombres SUC1/SUC2.

<details><summary>Notas del orador</summary>

⏱ 19-25 min.

La mitad del tiempo de VLANs va en la trampa del native: es el fallo
que más confunde. Si el ping al gateway de la VLAN 10 falla justo
después de crear el trunk, es aquí.

Analogía útil: la native es el 'carril sin etiqueta' del trunk. Si los
extremos no acuerdan cuál es, el tráfico acaba en el carril equivocado.

Recordar: VLAN 10 sin etiqueta (gateway en Gi0/0), VLAN 20 etiquetada
(gateway en Gi0/0.20).

</details>

---

## 10. Router-on-a-stick: dos gateways en un cable

> La física para la VLAN 10, la subinterfaz para la 20

| Interfaz | VLAN | IP / máscara | Etiqueta |
|---|---|---|---|
| Gi0/0 | 10 | 192.168.2.1/28 | sin etiqueta |
| Gi0/0.20 | 20 | 192.168.2.65/28 | 802.1Q 20 |

```text
R1(config)# interface GigabitEthernet0/0
R1(config-if)# ip address 192.168.2.1 255.255.255.240
R1(config-if)# no shutdown
R1(config-if)# interface GigabitEthernet0/0.20
R1(config-subif)# encapsulation dot1Q 20
R1(config-subif)# ip address 192.168.2.65 255.255.255.240
R1(config-subif)# no shutdown
```

**Una interfaz, dos mundos**
- La física enciende todas las subinterfaces.
- Cada subinterfaz es el gateway de una VLAN.

**El router enruta entre las dos VLAN de su sitio**
- Un `ping` de PC-A3 a PC-A1 sale por `Gi0/0.20` (VLAN 20) y vuelve por `Gi0/0` (VLAN 10).
- Enrutamiento de capa 3 sobre un solo cable físico: eso es **router-on-a-stick**.

**No olvides los uplinks**
- Cada router configura además sus dos enlaces /30 (Parte 2): R1 Gi0/1=.49 y Gi0/2=.58; R2 .50/.53; R3 .54/.57.

<details><summary>Notas del orador</summary>

⏱ 25-30 min.

El concepto clave: una interfaz física soporta subinterfaces lógicas,
cada una con su VLAN y su IP.

El `encapsulation dot1Q 20` es lo que hace que la subinterfaz entienda
el tráfico etiquetado de la VLAN 20.

En R2 y R3 es idéntico: siempre `Gi0/0.20`, con sus IPs (.81 y .97).

</details>

---

## 11. DHCP por VLAN

> Cada VLAN es una subred: necesita su propio pool

| Sitio | Gateway | Pool VLAN 20 | Rango DHCP |
|---|---|---|---|
| Central | .65 | VLAN20-CENTRAL | .70 – .78 |
| SUC-1 | .81 | VLAN20-SUC1 | .86 – .94 |
| SUC-2 | .97 | VLAN20-SUC2 | .102 – .110 |

```text
R1(config)# ip dhcp excluded-address 192.168.2.65 192.168.2.69
R1(config)# ip dhcp pool VLAN20-CENTRAL
R1(dhcp-config)# network 192.168.2.64 255.255.255.240
R1(dhcp-config)# default-router 192.168.2.65
R1(dhcp-config)# dns-server 8.8.8.8
R1(dhcp-config)# domain-name lab-utp.pa
```

**Mismo patrón que la VLAN 10**
- Se excluye el gateway de la VLAN 20 y 4 IPs fijas.
- Cada router termina con **2 pools**.

**Dos pools por router, no uno**
- VLAN 10 usa `LAN-CENTRAL` (red .0/28, gateway .1); la VLAN 20 usa `VLAN20-CENTRAL` (red .64/28, gateway .65).
- `show ip dhcp pool` debe listar dos pools; `show ip dhcp binding` reparte leases entre ambos.

**Recordatorio de Packet Tracer 9.0.1**
- `lease` no existe en el 2911 (el alquiler por defecto es 1 día) y `dns-server` acepta una sola IP.
- En los 9 PCs: `ipconfig /renew` y comprobar IP del rango + máscara /28 + gateway de SU VLAN.

<details><summary>Notas del orador</summary>

⏱ 30-35 min.

El punto que sorprende: el mismo router atiende dos subredes porque
ahora tiene dos IP (la física y la subinterfaz).

Verificación tipo: `show ip dhcp pool`, `show ip dhcp binding` y
`ipconfig /all` de un PC de cada VLAN. Los tres campos críticos: IP en
rango, máscara /28, gateway correcto.

</details>

---

## 12. Verificar: los pings que lo demuestran

> Aquí se ve el enrutamiento entre VLANs en acción

| Prueba | Resultado |
|---|---|
| PC-A3 ping .1 (gateway VLAN 20) | OK |
| PC-A3 ping .6 (VLAN 10) | Falla (a propósito) |
| PC-A1 ping .70 (VLAN 20) | OK · R1 enruta |

```text
SW1# show vlan brief
SW1# show interfaces trunk   ! native 10, allowed 10,20
R1#  show ip interface brief ! Gi0/0 y Gi0/0.20 con IP
R1#  show ip dhcp binding    ! leases de los 2 pools
```

**¿Por qué el segundo falla?**
- PC-A3 (VLAN 20) y PC-A1 (VLAN 10) están en subredes distintas.
- Sin el router no se alcanzan: es el aislamiento deseado.

**¿Por qué el tercero funciona?**
- PC-A1 sale por su gateway (.1) y R1 reenvía por Gi0/0.20 hacia .70.
- Router-on-a-stick: capa 3 sobre un solo cable.

**Primer vistazo a la tabla**
- Estos pings solo funcionan dentro de cada sede. Para cruzar entre sedes falta OSPF (Parte 4).
- Guiño: `show ip route` hoy solo muestra conectadas; en la Parte 4 aparecen las `O`.

<details><summary>Notas del orador</summary>

⏱ 35-40 min.

Tres pings que cuentan la historia de la segmentación por sedes.

Ojo con la asimetría: PC-A3 → PC-A1 falla (el PC no tiene ruta a otra
VLAN), pero PC-A1 → PC-A3 funciona porque el router sí enruta. Que el
grupo explique eso.

Si el ping al gateway de la VLAN 20 falla, revisar `encapsulation` y el
`native vlan` del trunk.

</details>

---

## 13. OSPF área 0

Enrutamiento dinámico directo: ni una sola ruta estática

- Por qué OSPF y no mantener estáticas en la topología
- Anatomía del comando: proceso, network, área y passive
- Costes: uplink primario frente a respaldo (ip ospf cost 100)
- Vecinos FULL, rutas O [110/2] y la prueba de redundancia

40 min

<details><summary>Notas del orador</summary>

⏱ 40-41 min · Transición.

Aquí empieza lo dinámico. A diferencia de la Sesión A, no hay fase
estática previa: OSPF se configura directo y la red aprende sola.

Pregunta de apertura: si R1 no tuviera ruta a la LAN de SUC-1, ¿qué
haría con un paquete para esa red? Lo descartaría. OSPF evita tener
que escribírsela.

</details>

---

## 14. Por qué OSPF y no estáticas

> Cuatro ventajas que se notan en esta topología

| Ventaja | Explicación |
|---|---|
| Automático | No hay que escribir rutas cuando se añade un sitio |
| Detección de caídas | Los hellos detectan un enlace caído en segundos |
| Mejor ruta | Elige por costo (métrica), no por lo que se escribió |
| Redundancia real | Con el enlace R2–R3 de respaldo, recalcula solo |

**Qué pasaría con una estática**
- La ruta estática apuntaría al uplink de cada sucursal.
- Si cae ese uplink, el estático no se entera y el paquete se descarta.
- La red se parte en dos hasta que alguien la corrija.

**Qué pasa con OSPF**
- Si cae el uplink de SUC-1, OSPF usa el respaldo R2→R3→R1.
- En minutos (o segundos) la red vuelve a estar completa.
- Ese es el contrato de este laboratorio.

**¿Y las estáticas en la Sesión A?**
- La Sesión A las usa como base pedagógica. Esta sesión es independiente: OSPF desde el inicio.
- La distancia administrativa (estática 1, OSPF 110) se comenta en la teoría, aquí no hay conflicto porque no hay estáticas.

<details><summary>Notas del orador</summary>

⏱ 41-45 min.

Contraste directo: sin OSPF el enlace R2-R3 es inútil; con OSPF es
seguro de vida de la red.

Subrayar que aquí no hay que 'quitar estáticas': nunca se pusieron.
La ventaja es aprender OSPF sobre una red limpia, sin tener que
deshacer la Fase A de otro lab.

</details>

---

## 15. Anatomía del comando OSPF

> Tres piezas: proceso, red y área (más passive)

```text
R1(config)# router ospf 10
R1(config-router)# router-id 192.168.2.1
R1(config-router)# network 192.168.2.0 0.0.0.255 area 0
R1(config-router)# passive-interface GigabitEthernet0/0
R1(config-router)# passive-interface GigabitEthernet0/0.20
```

**El 10 no es el área**
- `router ospf 10` es un número local del proceso.
- El área debe ser **0** en los tres.

**Wildcard = máscara invertida**
- `0.0.0.255` es la inversa de /24.
- Una línea cubre las 9 subredes.

**Qué anuncia `network`**
- Toda interfaz dentro de 192.168.2.x entra en OSPF.
- Incluye las subinterfaces: la VLAN 20 se anuncia sola.
- No hay que tocar OSPF al añadir VLANs.

**`passive-interface` en las LAN**
- En Gi0/0 y Gi0/0.20 no hay vecinos OSPF: solo PCs.
- La red se anuncia, pero no se envían hellos.
- **Nunca** passive en gi0/1 ni gi0/2 (los enlaces).

**Router-id fijo: R1=.1, R2=.17, R3=.33. Without él cada router elige la IP más alta y el lab no coincide.**

<details><summary>Notas del orador</summary>

⏱ 45-52 min.

Desglosar el comando en sus piezas. El `router-id` se fija para que los
resultados coincidan con el material.

El wildcard es la confusión clásica: es la máscara invertida, no la
máscara. /24 → 0.0.0.255.

Passive en las dos LAN de cada router: la red se anuncia igual, pero no
se gastan hellos con PCs.

</details>

---

## 16. Costes: uplink primario y respaldo

> `ip ospf cost 100` en el enlace R2–R3 hace que solo sea de emergencia

| Desde R2… | Camino | Costo |
|---|---|---|
| a la central | R2→R1 (uplink) | 1 + 1 = 2 |
| a la central | R2→R3→R1 (respaldo) | 100+1+1 = 102 |
| a SUC-2 | R2→R1→R3 (por central) | 1+1+1 = 3 |
| a SUC-2 | R2→R3 (respaldo) | 100+1 = 101 |

```text
R2(config)# interface GigabitEthernet0/2
R2(config-if)# ip ospf cost 100    ! hacia R3 (respaldo)
R3(config)# interface GigabitEthernet0/1
R3(config-if)# ip ospf cost 100    ! hacia R2 (respaldo)
```

**Con Gigabit todo cuesta 1**
- OSPF usa costo = referencia / ancho de banda.
- Sin ajuste, R2 vería **dos caminos de igual costo** a la central (ECMP).
- El costo 100 fuerza primario → respaldo como único orden.

**El efecto hub-and-spoke**
- Entre sucursales se prefiere **pasar por la central** (3 < 101).
- El enlace R2–R3 queda en modo dormido hasta que un uplink falle.
- Si `ip ospf cost` no lo acepta tu PT: `bandwidth 1000` (100000/1000 = 100).

**Los uplinks se dejan con costo 1: comparan entre ellos para elegir el mejor camino hacia la central.**

<details><summary>Notas del orador</summary>

⏱ 52-60 min.

Este es el detalle que distingue al laboratorio: sin el costo 100, OSPF
haría balanceo ECMP por los dos caminos, y la prueba de redundancia
sería menos clara.

La tabla de costos se lee en columna: el costo acumulado decide la
ruta. El tráfico entre sucursales sale por la central.

El comando fallback (`bandwidth 1000`) logra el mismo número.

</details>

---

## 17. Vecinos FULL y rutas O

> Los dos `show` que prueban que OSPF funciona

```text
R1# show ip ospf neighbor
Neighbor ID     Pri   State   Dead Time   Address      Interface
192.168.2.17      0   FULL/-  00:00:37  192.168.2.50  Gi0/1  SUC-1
192.168.2.33      0   FULL/-  00:00:35  192.168.2.57  Gi0/2  SUC-2
```

**FULL, no 2-WAY**
- FULL = vecindad establecida.
- 2-WAY / EXSTART = área o red mal.

**El Pri 0 no es error**
- Confirma `Gi0/0` pasiva: sin hellos.

```text
R1# show ip route
C  192.168.2.0/28   Gi0/0        L 192.168.2.1/32
C  192.168.2.64/28  Gi0/0.20     L 192.168.2.65/32
C  192.168.2.48/30  Gi0/1        L 192.168.2.49/32
C  192.168.2.56/30  Gi0/2        L 192.168.2.58/32
O  192.168.2.16/28 [110/2] via 192.168.2.50
O  192.168.2.80/28 [110/2] via 192.168.2.50
O  192.168.2.32/28 [110/2] via 192.168.2.57
O  192.168.2.96/28 [110/2] via 192.168.2.57
```

**Lectura de [110/2]**
- **110** = distancia administrativa de OSPF.
- **2** = costo: 1 del enlace + 1 de la LAN del destino.

**Cada router ve 2 vecinos**
- R2 y R3 también deben mostrar FULL con los otros dos.
- `show ip route 192.168.2.0` en R2 → via R1 (o via R3 si el uplink cae).

<details><summary>Notas del orador</summary>

⏱ 60-68 min.

Dos capturas obligatorias: vecinos FULL y tabla con rutas O. Son la
prueba de que OSPF está enrutando.

El [110/2]: 110 es la distancia administrativa y 2 la métrica. Es la
duda más frecuente al leer `show ip route`.

Probar también `show ip protocols` en R1 para ver el proceso, el
router-id y las interfaces pasivas.

</details>

---

## 18. La prueba de redundancia

> Apagar un uplink y ver la red sobrevivir por el respaldo

**1. shutdown**
R1 Gi0/1
(uplink SUC-1)

**2. espera ~40 s**
OSPF detecta
la caída

**3. R2 recalcula**
ruta a central
via R3 (.54)

**4. ruta nueva**
[110/102] via
192.168.2.54

**5. ping OK**
PC-B1 → .6
por el respaldo

**Qué demuestra**
- Con el uplink de la sucursal 1 caído, el tráfico SUC-1 → Central sale por **R2 → R3 → R1** (enlace de respaldo).
- El `ping` desde PC-B1 sigue respondiendo y el `tracert` muestra el camino nuevo: `.17 → .54 (R3) → .1 (R1)`.
- OSPF recalculó solo: nadie tocó una ruta a mano.

**Con rutas estáticas no pasa**
- El estático seguiría apuntando al uplink caído.
- Sin ruta alternativa, el tráfico se corta hasta que alguien la corrija.
- Por eso OSPF: resilencia sin intervención.

**Restaurar el enlace**
- `interface Gi0/1` → `no shutdown` en R1.
- Esperar la convergencia: la ruta vuelve a `[110/2] via .50`.
- Verificar con `show ip route 192.168.2.0` en R2.

Usa `tracert` antes y después del shutdown: el camino se ve cambiar.

<details><summary>Notas del orador</summary>

⏱ 68-75 min.

Es la prueba estrella y cierra la Parte 4. Hazla en directo si se puede
proyectar.

Pasos: apagar R1 Gi0/1, esperar los ~40 s de convergencia, comprobar el
ping desde PC-B1 y leer `show ip route 192.168.2.0` en R2 (debe decir
via .54 con costo 102).

No olvides restaurar con `no shutdown` o el resto de la sesión quedará
con medio enlace caído.

</details>

---

## 19. RIPv2 (alternativa)

El otro dinámico, para comparar

- Configurar RIPv2 y por qué `no auto-summary` es obligatorio
- Verificar rutas `R` en la tabla
- Comparar OSPF y RIPv2 en esta misma topología
- Volver a OSPF al terminar la comparación

10 min

<details><summary>Notas del orador</summary>

⏱ 75-76 min · Transición.

Parte opcional: se hace si el profesor la pide o para comparar. RIP no
sustituye a OSPF en producción, pero enseña el concepto de vector de
distancia.

</details>

---

## 20. RIPv2: la alternativa

> Más simple de escribir, más frágil con VLSM

| Comando | Por qué |
|---|---|
| version 2 | RIPv2 envía la máscara (VLSM lo exige) |
| no auto-summary | Sin esto resume mal las subredes |
| network 192.168.2.0 | Activa RIP en esa red, sin máscara ni área |

```text
R1(config)# no router ospf 10
R1(config)# router rip
R1(config-router)# version 2
R1(config-router)# no auto-summary
R1(config-router)# network 192.168.2.0
```

**`no auto-summary` no es opcional aquí**
- Con VLSM, el resumen automático manda `192.168.2.0/24` en vez de las subredes reales.
- El vecino recibe una ruta que no corresponde y descarta la información correcta.
- Con `no auto-summary` se difunden las subredes con su máscara real.

**Es solo enrutamiento**
- `network 192.168.2.0` le dice a RIP qué interfaces anunciar: el DHCP por VLAN no cambia.
- RIPv2 puede tardar 1-3 min en aparecer en Packet Tracer: es normal.

<details><summary>Notas del orador</summary>

⏱ 76-82 min.

El `no auto-summary` es el corazón de esta parte: es el error clásico
de RIP con VLSM.

Recordar apagar OSPF primero (`no router ospf 10`): si corren juntos,
compiten y OSPF gana por distancia administrativa.

La paciencia es obligatoria: RIP en PT tarda en converger.

</details>

---

## 21. OSPF frente a RIPv2

> Mismo laboratorio, dos maneras de aprender rutas

| Característica | OSPF (área 0) | RIPv2 |
|---|---|---|
| Tipo | estado de enlace | vector de distancia |
| Distancia administrativa | 110 | 120 |
| Convergencia | rápida (segundos, SPF) | lenta (temporizadores) |
| Métrica | costo por ancho de banda | saltos (máx. 15) |
| VLSM | nativo | requiere `no auto-summary` |
| Configuración | más comandos | más simple |

**Con cuál te quedas**
- En este laboratorio, **OSPF**: converge rápido y aprende VLSM sin trucos.
- RIPv2 sirve para **comparar** y para ver por qué el resumen automático rompe con subredes.
- Mientras corren juntos gana OSPF (110 < 120). Para volver a OSPF: `no router rip` y repetir la Parte 4.

<details><summary>Notas del orador</summary>

⏱ 82-86 min.

No hace falta dominar RIP: la idea es comparar y justificar por qué
OSPF es el protocolo de producción.

La distancia administrativa distinta (110 vs 120) explica por qué se
apaga uno cuando se prueba el otro.

</details>

---

## 22. Verificación y diagnóstico

El checklist final y los 8 errores que te vas a encontrar

- Checklist de 10 comprobaciones con su resultado esperado
- Los 8 errores típicos: síntoma, causa y solución
- El método por capas y el comando de rescate
- Preguntas de reflexión y entregable

30 min

<details><summary>Notas del orador</summary>

⏱ 86-87 min · Transición.

Última parte: comprobar y saber arreglar. El checklist es el mismo que
se entrega; los 8 errores cubren el 90 % de lo que sale mal.

</details>

---

## 23. Checklist final de la Sesión B

> Cada comando responde una pregunta

| # | Comando | Dónde | Resultado esperado |
|---|---|---|---|
| 1 | show ip interface brief | R1, R2, R3 | Gi0/0 y Gi0/0.20 up/up con IP |
| 2 | show vlan brief | SW1, SW2, SW3 | VLAN 10 y 20; Fa0/4 en la 20 |
| 3 | show interfaces trunk | SW1, SW2, SW3 | Fa0/1 troncal, native 10, allowed 10,20 |
| 4 | show ip dhcp pool | R1, R2, R3 | 2 pools por router |
| 5 | show ip dhcp binding | R1, R2, R3 | 2 leases VLAN 10 + 1 de VLAN 20 |
| 6 | ipconfig /all | 1 PC de cada VLAN | IP del pool + máscara /28 + gateway correcto |
| 7 | show ip route | R1, R2, R3 | rutas O (o R) y sin S |
| 8 | show ip ospf neighbor | R1, R2, R3 | 2 vecinos en FULL |
| 9 | show ip route 192.168.2.0 | R2 | via R1 normal; via R3 con uplink caído |
| 10 | shutdown R1 Gi0/1 | R1 | ping PC-B1 sigue OK (redundancia) |

**El orden importa**
- No puede haber lease de la VLAN 20 (paso 5) sin la subinterfaz y el pool (Parte 3).
- Y no puede haber vecinos FULL (paso 8) si un enlace está caído o mal configurado.

<details><summary>Notas del orador</summary>

⏱ 87-92 min.

Usa el checklist como índice del entregable: cada fila es una captura
de pantalla.

Los pasos 5 y 9 son los que más se olvidan. El 10 cierra la demostración
de redundancia de la Parte 4.

</details>

---

## 24. Los 8 errores típicos

> Reconocerlos por el síntoma es más rápido que depurar

| Síntoma | Causa probable | Solución |
|---|---|---|
| Interfaz administratively down | Falta `no shutdown` | `interface Gi0/x` → `no shutdown` |
| PC en 169.254.x.x (APIPA) | DHCP sin responder o pool malo | Revisar `show ip dhcp pool` y el cable |
| IP pero no ping al gateway | IP fuera del rango o máscara mala | `ipconfig /renew`, revisar `network` |
| PC tomó la IP del gateway | Gateway no excluido | `excluded-address`, `clear ip dhcp binding` |
| Gateway OK, otra VLAN falla | OSPF no anuncia, o subinterfaz mal | `show ip route`; `encapsulation dot1Q` y `network` |
| OSPF sin vecinos | Área distinta, red mal o enlace caído | Revisar `area 0`, `show ip ospf interface brief` |
| No aparece una subred vecina | passive en un enlace, o falta la subinterfaz | Quitar passive de Gi0/1 y Gi0/2 |
| RIPv2 no anuncia subredes | Falta `no auto-summary` | `no auto-summary` en `router rip` |

**El patrón que hay detrás**
- La mitad de estos errores **no son de enrutamiento**: son de capa 1 o 2 (cable, `no shutdown`, DHCP).
- Antes de tocar OSPF, mirar `show ip interface brief` y `show ip dhcp binding`.
- Rescate de emergencia: `erase startup-config` + `reload` deja el equipo de fábrica (se vuelve a la Parte 1).

<details><summary>Notas del orador</summary>

⏱ 92-102 min.

No hace falta leerlos todos: elegir 2 o 3 y preguntar el síntoma. La
tabla completa está en SESION-B.md, Parte 11.

El más costoso en este lab es 'gateway OK pero otra VLAN falla': se
pierde tiempo en OSPF cuando el problema es la subinterfaz o un
`network` mal declarado.

El rescate `erase + reload` es la última carta: documentar config antes
o tenerla en config/R*.txt.

</details>

---

## 25. Preguntas de la Sesión B

> Para cerrar el entregable

**Responde con lo que viste en la CLI**
1. En `[110/2]`, ¿qué significan los dos números? ¿Cómo se calcula el 2 en el camino de R1 a la VLAN 20 de una sucursal?
2. ¿Por qué el tráfico entre sucursales pasa por la central y no por el enlace R2–R3? ¿Qué comando lo provoca?
3. Con el uplink de la SUC-1 caído, ¿qué camino toma un paquete de PC-B1 a un PC de la central? Escribe el `tracert` esperado.
4. ¿Qué pasa si quitas `passive-interface Gi0/0`? ¿Y si lo pusieras en Gi0/1?
5. ¿Qué diferencia hay entre `show ip route` y `show ip protocols`?
6. Compara la convergencia de OSPF y RIPv2. ¿Cuál usarías en una red de 50 routers y por qué?
7. Un PC de la VLAN 10 obtuvo una IP de la VLAN 20. ¿Qué comando corregiste y con qué `show` lo detectas?

<details><summary>Notas del orador</summary>

⏱ 102-112 min.

Las siete preguntas son el entregable escrito. La 2 y la 3 conectan
directo con los costes y la prueba de redundancia; la 7 con el
troubleshooting de DHCP.

Déjalas como tarea si el tiempo no alcanza: están al final de
SESION-B.md con más contexto.

</details>

---

## 26. Repaso: lo que hay que saber

> Cinco ideas y el entregable de la Sesión B

**Las 5 ideas de la Sesión B**
1. La red es hub-and-spoke: R1 central y R2/R3 suben por uplinks; R2–R3 es el respaldo.
2. El trunk viaja sin etiqueta en la native VLAN: si no se fija en 10, el gateway queda en la VLAN 1.
3. Router-on-a-stick: una interfaz física, dos gateways con `encapsulation dot1Q` y un pool por VLAN.
4. OSPF aprende las 9 subredes solo: no hay estáticas y no hace falta quitarlas porque nunca se pusieron.
5. Con los costes (uplink 1, respaldo 100), si cae un uplink OSPF recalcula y el tráfico sigue por el respaldo.

**Entregable de la Sesión B**
- `show vlan brief` y `show interfaces trunk` de un switch.
- `show ip interface brief` de los 3 routers.
- `show ip dhcp pool` y `show ip dhcp binding` de R1.
- `show ip route` de R1 y R2 con rutas `O` y **sin** `S`.
- `show ip ospf neighbor` de los 3 routers en FULL.
- Evidencia de redundancia: ping OK desde PC-B1 con `R1 Gi0/1` en `shutdown` + `tracert`.
- `ipconfig /all` de un PC de cada VLAN y respuestas a las 7 preguntas.

<details><summary>Notas del orador</summary>

⏱ 112-120 min · Cierre.

Recorre las 5 ideas y deja claro el entregable. Si sobra tiempo, pide a
un equipo que demuestre la redundancia en directo.

La Sesión B es ahora un laboratorio completo por sí mismo: montar,
segmentar, enrutar de forma dinámica y demostrar que la red se
recupera sola.

</details>

---
