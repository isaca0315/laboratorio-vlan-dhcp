# Sesión B — Enrutamiento dinámico (OSPF / RIPv2) y diagnóstico

Laboratorio N.º 13 · Unidad III · **Cisco Packet Tracer**

Objetivo: sustituir las rutas estáticas de la Fase A por enrutamiento dinámico
(**OSPF área 0**, con **RIPv2** como alternativa), comprobar la convergencia y
demostrar la **redundancia** de enlaces que aportan los protocolos dinámicos.

## Parte 1 — Estado de partida

Antes de tocar nada, confirma que la Fase A quedó bien:

```text
show ip route static   ! las 2 rutas estáticas que dejaste en la Sesión A
show ip route          ! tabla completa: connected, local y static
ping 192.168.2.38      ! desde PC-A1: confirma que hay conectividad entre sedes
```

Si el ping entre sedes falla, **no sigas**: primero corrige la Fase A (ver
sesión B, Parte 6).

> Referencia de comandos: [`COMANDOS.md`](COMANDOS.md) (§6 OSPF, §7 RIPv2).

## Parte 2 — VLAN y enrutamiento entre VLANs

Hasta ahora cada sede era **una sola LAN**: un switch, un dominio de broadcast y
una subred. Con VLAN cada sede se parte en **dos dominios de broadcast** con
subred propia, y el router pasa a ser el que enruta entre VLANs usando **un solo
cable** (router-on-a-stick).

| Sede | VLAN | Nombre | Subred | Gateway | Pool DHCP | PCs |
|------|------|--------|--------|---------|-----------|-----|
| A | 10 | `USUARIOS-A` | 192.168.2.0/28 | .1 | .6-.14 | PC-A1, PC-A2 |
| A | 20 | `INVITADOS-A` | 192.168.2.64/28 | .65 | .70-.78 | PC-A3 |
| B | 10 | `USUARIOS-B` | 192.168.2.16/28 | .17 | .22-.30 | PC-B1, PC-B2 |
| B | 20 | `INVITADOS-B` | 192.168.2.80/28 | .81 | .86-.94 | PC-B3 |
| C | 10 | `USUARIOS-C` | 192.168.2.32/28 | .33 | .38-.46 | PC-C1, PC-C2 |
| C | 20 | `INVITADOS-C` | 192.168.2.96/28 | .97 | .102-.110 | PC-C3 |

Las tres subredes nuevas son `.64/28`, `.80/28` y `.96/28`. Los bloques /28
empiezan en **múltiplos de 16**, así que `.60/28` no existe como red, y de
`.48` a `.59` ya lo ocupan los tres enlaces /30 de la Sesión A.

> La VLAN 10 deja intacta la Fase A: mismo switch, misma IP de gateway y mismo
> pool. Lo único que se añade es la VLAN 20 y el cable del router pasa a ser
> trunk. No hay que rehacer el VLSM de la Sesión A.

### Paso 2.1 — Qué cambia respecto a la Sesión A

Un PC por sede cambia de VLAN: el tercero de cada sede.

| PC | Antes (VLAN 10) | Ahora (VLAN 20) | Puerto del switch |
|----|-----------------|-----------------|-------------------|
| PC-A3 | IP del pool .6-.14 | IP del pool .70-.78 | SW1 Fa0/4, access VLAN 20 |
| PC-B3 | IP del pool .22-.30 | IP del pool .86-.94 | SW2 Fa0/4, access VLAN 20 |
| PC-C3 | IP del pool .38-.46 | IP del pool .102-.110 | SW3 Fa0/4, access VLAN 20 |

Los **cables no cambian**: siguen siendo los mismos 15. Lo que cambia es a qué
VLAN pertenece cada puerto del switch.

### Paso 2.2 — Crear los VLAN en el switch

En `SW1` (haz lo equivalente en `SW2` y `SW3`, con los valores del Paso 2.6):

```text
enable                     ! modo privilegiado
configure terminal          ! modo de configuración global
vlan 10                    ! crea el VLAN 10
 name USUARIOS-A           ! le pone nombre; es etiqueta, no afecta al tráfico
vlan 20                    ! crea el VLAN 20
 name INVITADOS-A          ! nombre de la VLAN nueva de esta sede
end                        ! vuelve al modo privilegiado
copy running-config startup-config ! guarda la config
```

Un VLAN no existe hasta que se crea con `vlan <id>`: los puertos no pueden
asignarse a un VLAN que todavía no está en la base de datos del switch.

### Paso 2.3 — Poner los puertos en acceso y el del router en trunk

```text
configure terminal          ! modo de configuración global
interface FastEthernet0/2   ! PC-A1
 switchport mode access      ! puerto de un solo VLAN: el de un PC
 switchport access vlan 10   ! ese PC queda en la VLAN 10
interface FastEthernet0/3   ! PC-A2
 switchport mode access
 switchport access vlan 10   ! mismo VLAN que PC-A1: se ven entre sí
interface FastEthernet0/4   ! PC-A3, el que cambia de VLAN
 switchport mode access
 switchport access vlan 20   ! ahora en la VLAN 20: deja de ver a PC-A1 y PC-A2
interface FastEthernet0/1   ! el cable que va al router R1 Gi0/0
 switchport mode trunk       ! este puerto transporta las 2 VLANs etiquetadas
 switchport trunk native vlan 10  ! la VLAN 10 viaja SIN etiqueta (ver nota)
 switchport trunk allowed vlan 10,20  ! soloDeja pasar estas 2 VLANs
end                          ! vuelve al modo privilegiado
copy running-config startup-config ! guarda la config
```

> **La trampa del `native`.** Por defecto un trunk usa la VLAN 1 como nativa, y
> lo que llega sin etiqueta va a parar ahí. El router ya tiene `192.168.2.1/28`
> en Gi0/0 **sin configurar**, o sea sin etiqueta: con el `native` por defecto
> esa IP quedaría en la VLAN 1, en una subred que no existe en el plan, y los
> PCs de la VLAN 10 no la verían. Por eso el `native` se fija en 10.

Los PCs de una misma VLAN se ven entre sí porque comparten dominio de broadcast;
los de VLAN distintas **no**, aunque estén en el mismo switch y el mismo cable
al router. Eso es el punto del ejercicio.

### Paso 2.4 — Las subinterfaces en el router (router-on-a-stick)

El trunk trae las dos VLANs por el mismo cable, así que la IP de cada VLAN va en
una subinterfaz distinta. En `R1`:

```text
configure terminal          ! modo de configuración global
interface GigabitEthernet0/0   ! la física: se queda con la IP de la VLAN 10
 ip address 192.168.2.1 255.255.255.240  ! gateway de VLAN 10, sin etiqueta
 no shutdown                ! la física debe quedar encendida
interface GigabitEthernet0/0.20  ! subinterfaz lógica para la VLAN 20
 encapsulation dot1Q 20     ! add: etiquetas este tráfico con 802.1Q VLAN 20
 ip address 192.168.2.65 255.255.255.240  ! gateway de la VLAN 20 de la sede A
 no shutdown                ! enciende también la subinterfaz
end                          ! vuelve al modo privilegiado
copy running-config startup-config ! guarda la config
```

Con esto R1 enruta entre las dos VLAN de su sede: un `ping` de PC-A3 a PC-A1
sale por la subinterfaz y vuelve por la física, sin tocar el cableado.

### Paso 2.5 — DHCP para la VLAN 20

Cada VLAN es una subred distinta, así que necesita **su propio pool**. El de la
VLAN 20 en R1:

```text
configure terminal          ! modo de configuración global
ip dhcp excluded-address 192.168.2.65 192.168.2.69
!   .65-.69 fuera del pool: es el gateway de la VLAN 20, no un PC
ip dhcp pool VLAN20-A       ! crea el pool de la VLAN 20 de la sede A
 network 192.168.2.64 255.255.255.240  ! subred /28 que reparte este pool
 default-router 192.168.2.65  ! gateway que reciben los PCs de la VLAN 20
 dns-server 8.8.8.8          ! servidor DNS que reciben los PCs
 domain-name lab-utp.pa     ! sufijo DNS: el host será PC-A3.lab-utp.pa
exit                         ! sale del modo pool -> vuelve a config global
end                          ! vuelve al modo privilegiado
copy running-config startup-config ! guarda la config
```

### Paso 2.6 — Repetir en SW2, SW3, R2 y R3

Estos son todos los valores que cambian; el resto de los comandos es idéntico.

| Elemento | SW2 / R2 (sede B) | SW3 / R3 (sede C) |
|----------|-------------------|-------------------|
| VLAN 10 | `USUARIOS-B`, red .16/28 | `USUARIOS-C`, red .32/28 |
| VLAN 20 | `INVITADOS-B`, red .80/28 | `INVITADOS-C`, red .96/28 |
| Gateway VLAN 20 | `192.168.2.81/28` | `192.168.2.97/28` |
| Subinterfaz | `Gi0/0.20`, `encapsulation dot1Q 20` | `Gi0/0.20`, `encapsulation dot1Q 20` |
| Exclusión DHCP | `192.168.2.81 192.168.2.85` | `192.168.2.97 192.168.2.101` |
| Pool DHCP | `ip dhcp pool VLAN20-B`, red .80/28 | `ip dhcp pool VLAN20-C`, red .96/28 |
| Default-router | `192.168.2.81` | `192.168.2.97` |
| Puerto access VLAN 20 | SW2 Fa0/4 (PC-B3) | SW3 Fa0/4 (PC-C3) |
| Native del trunk | SW2 Fa0/1 `vlan 10` | SW3 Fa0/1 `vlan 10` |

En los tres routers la subinterfaz es `Gi0/0.20` porque la LAN de cada router es
siempre su `Gi0/0` (ver Sesión A, Parte 3).

> OSPF y RIP no necesitan cambios: `network 192.168.2.0 0.0.0.255` ya cubre
> cualquier interfaz dentro de 192.168.2.x, y las subinterfaces lo están. Las
> subredes `.64/28`, `.80/28` y `.96/28` se anuncian solas.

### Paso 2.7 — Verificar

En el switch:

```text
show vlan brief          ! VLAN 10 y 20 creadas, y qué puertos son de cada una
show interfaces trunk    ! qué VLANs pasan por el Fa0/1 y cuál es la nativa
```

En el router:

```text
show ip interface brief  ! Gi0/0 con .1/28 y Gi0/0.20 con .65/28: dos gateways
show ip dhcp binding     ! 2 IPs del pool de la VLAN 10 y 1 del pool de la VLAN 20
show ip dhcp pool VLAN20-A  ! el pool nuevo: red .64/28, gateway .65, sin leases
```

En los PCs, tras un `ipconfig /renew` en PC-A3, debe salir una IP del rango
.70-.78 con gateway .65 y máscara /28.

Prueba el punto clave del ejercicio:

```text
PC-A3> ping 192.168.2.1      ! a su propio gateway (VLAN 20)  -> OK
PC-A3> ping 192.168.2.6      ! a PC-A1, en OTRA VLAN           -> falla
PC-A1> ping 192.168.2.70     ! a PC-A3, en OTRA VLAN           -> OK (R1 enruta)
```

Los dos primeros pings son de un PC a su gateway y a un PC de otra VLAN: el
segundo falla a propósito. El tercero es el que demuestra que el router está
enrutando entre VLANs con un solo cable físico.

## Parte 3 — Fase B: OSPF área 0

### Paso 3.1 — Por qué OSPF y no estáticas

| Ventaja | Explicación |
|---------|-------------|
| Automático | No hay que escribir rutas al añadir un sitio nuevo |
| Detección de caídas | Los hellos detectan el enlace caído en segundos |
| Mejor ruta | Elige por costo (métrica) y no por "lo que escribí" |
| Escalable | Con 30 routers seguirías usando 1 comando por router, no 29 rutas |

### Paso 3.2 — Qué significa el comando

```text
router ospf 10                      ← proceso OSPF con ID local 10
 network 192.168.2.0 0.0.0.255      ← wildmask: todo 192.168.2.x participates
 area 0                              ← área backbone (todos deben coincidir)
 passive-interface GigabitEthernet0/0 ← no enviar hellos por la LAN de PCs
```

> El **wildmask** es la inversa de la máscara: `/24` → máscara
> `255.255.255.255` → wildmask `0.0.0.255`. Se puede abreviar:
> `network 192.168.2.0 area 0` (Packet Tracer lo acepta y expande solo).

### Paso 3.3 — Configurar los 3 routers

```text
! ---------- R1 ----------
configure terminal             ! modo de configuracion global
router ospf 10                 ! arranca el proceso OSPF con ID local 10
 router-id 192.168.2.1        ! ID único del router; debe coincidir en los 3
 network 192.168.2.0 0.0.0.255 area 0  ! anuncia 192.168.2.x en el área 0
 passive-interface GigabitEthernet0/0  ! en la LAN de PCs no se envían hellos
end                            ! vuelve al modo privilegiado

! ---------- R2 ----------
configure terminal             ! mismo proceso OSPF, con el ID de R2
router ospf 10
 router-id 192.168.2.17       ! ID único; es la LAN-B, no la IP de un enlace
 network 192.168.2.0 0.0.0.255 area 0
 passive-interface GigabitEthernet0/0
end

! ---------- R3 ----------
configure terminal             ! mismo proceso OSPF, con el ID de R3
router ospf 10
 router-id 192.168.2.33       ! ID único; por eso se elige la IP de la LAN
 network 192.168.2.0 0.0.0.255 area 0
 passive-interface GigabitEthernet0/0
end
```

`passive-interface` es buena práctica: en la LAN no hay ningún router vecino, así
que enviar hellos allí solo consume ancho de banda.

> **`router-id` importa.** Si no lo configuras, cada router elige uno solo: la IP
> más alta de una interfaz activa (R1 = .58, R2 = .53, R3 = .57). Fijándolo a la
> IP de su gateway (.1 / .17 / .33) el lab se vuelve **determinista** y lo que
> veas en `show ip ospf neighbor` coincide con este material.

### Paso 3.4 — Quitar las rutas estáticas

Se **deben eliminar**, si no OSPF no podrá instalar sus rutas (la estática, más
específica en distancia administrativa, siempre gana):

```text
! ---------- R1 ----------
configure terminal             ! modo de configuracion global
no ip route 192.168.2.16 255.255.255.240 192.168.2.50  ! borra la ruta a LAN-B
no ip route 192.168.2.32 255.255.255.240 192.168.2.57  ! borra la ruta a LAN-C
end                            ! vuelve al modo privilegiado

! ---------- R2 ----------
configure terminal             ! el `no` delante de la ruta es lo que la elimina
no ip route 192.168.2.0 255.255.255.240 192.168.2.49   ! borra la ruta a LAN-A
no ip route 192.168.2.32 255.255.255.240 192.168.2.54  ! borra la ruta a LAN-C
end

! ---------- R3 ----------
configure terminal             ! si dejas las 6 rutas, OSPF no puede tomar el control
no ip route 192.168.2.0 255.255.255.240 192.168.2.58   ! borra la ruta a LAN-A
no ip route 192.168.2.16 255.255.255.240 192.168.2.53  ! borra la ruta a LAN-B
end
```

Comprobación de que ya no quedan estáticas (no debe mostrar nada):

```text
show ip route static   ! debe salir vacío: ya no hay rutas S
```

### Paso 3.5 — Verificar la vecindad OSPF

```text
show ip ospf neighbor   ! lista los vecinos FULL: 2 por router (R2 y R3)
```

```text
R1#show ip ospf neighbor

Neighbor ID     Pri   State       Dead Time   Address      Interface
192.168.2.33      0   FULL/  -    00:00:37    192.168.2.57  GigabitEthernet0/2
192.168.2.17      0   FULL/  -    00:00:35    192.168.2.50  GigabitEthernet0/1
```

Ambos vecinos en **FULL** = vecindad establecida (estado `2-WAY` o `EXSTART`
significa que algo va mal). El `Pri 0` confirma que Gi0/0 es pasiva.

Otros comandos de diagnóstico OSPF:

```text
show ip ospf interface brief      ← interfaces participantes en OSPF
show ip protocols                  ← qué protocolos de enrutamiento hay activos
show ip ospf                       ← ID de router, áreas, SPF
```

### Paso 3.6 — Verificar la tabla de enrutamiento

```text
show ip route   ! las 2 rutas remotas ya no son S (static) sino O (OSPF)
```

```text
R1#show ip route
Codes: C - connected, S - static, O - OSPF, L - local

      192.168.2.0/24 is variably subnetted, 5 subnets, 3 masks
C        192.168.2.0/28 is directly connected, GigabitEthernet0/0
L        192.168.2.1/32 is directly connected, GigabitEthernet0/0
C        192.168.2.48/30 is directly connected, GigabitEthernet0/1
L        192.168.2.49/32 is directly connected, GigabitEthernet0/1
C        192.168.2.56/30 is directly connected, GigabitEthernet0/2
L        192.168.2.57/32 is directly connected, GigabitEthernet0/2
O        192.168.2.16/28 [110/2] via 192.168.2.50, 00:38:24, GigabitEthernet0/1
O        192.168.2.32/28 [110/2] via 192.168.2.57, 00:38:24, GigabitEthernet0/2
```

Lectura de `[110/2]`:

- **110** = distancia administrativa de OSPF (comparada con 1 de estática y 0 de
  conectada). Menor = más confiable. Por eso quitar las `S` era obligatorio.
- **2** = métrica (costo). OSPF calcula el costo desde el ancho de banda de la
  interfaz (100 Mbps en Gig → costo 1 por salto).

### Paso 3.7 — Probar conectividad

```text
show ip route 192.168.2.32        ← debe indicar OSPF en la línea install
ping 192.168.2.22
ping 192.168.2.38
```

Y desde los PCs, los mismos 9 pings de la Fase A deben seguir respondiendo.

### Paso 3.8 — Demostrar la redundancia (prueba clave)

1. En R2: `configure terminal` → `interface GigabitEthernet0/2` → `shutdown`.
2. Espera ~40 s y en R1 ejecuta `show ip ospf neighbor` (R2 debe salir como
   `DOWN` o desaparecer de esa interfaz) y `show ip route`.
3. Vuelve a hacer ping desde **PC-A1** a `192.168.2.38` (LAN-C).

Resultado esperado: **los pings siguen funcionando**, ahora por el camino
R1 → R3 directo, porque OSPF recalculó la mejor ruta. Repite la prueba con
`tracert` para ver que el camino cambió.

Después restaura el enlace:

```text
interface GigabitEthernet0/2   ! el enlace R1-R3, el único de R1 hacia R3
 no shutdown                  ! simula la caída: al apagarlo, OSPF recalcula
```

> Con rutas **estáticas** (Fase A) esta prueba también funcionaría en esta malla
> pequeña, porque las rutas apuntan a la subred del vecino y no a su interfaz
> concreta. En una cadena o en un escenario real, la diferencia es decisiva: el
> estático no sabe que el enlace murió hasta que alguien lo actualiza a mano.

## Parte 4 — Alternativa: RIPv2

Úsala solo si el profesor lo pide o si quieres **comparar** ambos protocolos en la
misma topología.

### Paso 4.1 — Configurar

```text
! ---------- R1 ----------
configure terminal             ! modo de configuracion global
no router ospf 10              ! apaga OSPF: esta es la alternativa a OSPF
router rip                     ! entra al modo de configuración de RIP
 version 2                    ! RIPv2: envía la máscara completa (VLSM lo exige)
 no auto-summary              ! sin resumen: con /28 y /30 mezclados, resume mal
 network 192.168.2.0          ! activa RIP en las interfaces de esa subred
end                            ! vuelve al modo privilegiado

! ---------- R2 ----------
configure terminal             ! misma secuencia que en R1
no router ospf 10
router rip
 version 2
 no auto-summary
 network 192.168.2.0
end

! ---------- R3 ----------
configure terminal             ! misma secuencia que en R1 y R2
no router ospf 10
router rip
 version 2
 no auto-summary
 network 192.168.2.0
end
```

Significado:

| Comando | Por qué |
|---------|---------|
| `version 2` | RIPv2 es **con clase-free**: envía la máscara completa. RIPv1 es legacy y rompe con VLSM. |
| `no auto-summary` | Con VLSM es **obligatorio**: si no, summariza en los bordes y las subredes /28 y /30 dejan de anunciarse. |
| `network 192.168.2.0` | Activa RIP en cualquier interfaz dentro de ese rango (incluye las LAN). |

> La red /24 en el statement `network` **no** significa que los PCs reciban
> /24: RIP solo se ocupa del **enrutamiento**; el DHCP de la Parte 4 de la
> Sesión A sigue entregando /28.

### Paso 4.2 — Verificar

```text
show ip route   ! ahora las rutas remotas son R (RIP), no O ni S
```

```text
R1#show ip route
      192.168.2.0/24 is variably subnetted, 5 subnets, 3 masks
C        192.168.2.0/28 is directly connected, GigabitEthernet0/0
R        192.168.2.16/28 [120/1] via 192.168.2.50, 00:00:12
R        192.168.2.32/28 [120/1] via 192.168.2.57, 00:00:12
```

```text
show ip protocols       ! confirma que RIP es el único protocolo activo
show ip rip database      ! las rutas RIP aprendidas y por qué interfaz
```

### Paso 4.3 — OSPF vs RIPv2 en esta topología

| Característica | OSPF (área 0) | RIPv2 |
|----------------|---------------|-------|
| Tipo | Estado de enlace | Vector de distancia |
| Distancia administrativa | 110 | 120 |
| Convergencia | Rápida (segundos, SPF) | Lenta (temporizadores de basura: minutos) |
| Métrica | Costo por ancho de banda | Saltos (máx. 15) |
| Escala a redes grandes | Sí | No |
| Configuración | Más comandos | Más simple |
| VLSM | Nativo | Requiere `no auto-summary` |

En Packet Tracer, RIPv2 puede tardar **1-3 minutos** en muncul en la tabla: es
normal, no es una falla.

Para volver a OSPF: `no router rip` y volver a la Parte 3.

## Parte 5 — Verificación final (checklist)

| # | Comando | Dónde | Resultado esperado |
|---|---------|-------|--------------------|
| 1 | `show ip interface brief` | R1, R2, R3 | 3 interfaces `up/up` con IP |
| 2 | `show ip dhcp pool` | R1, R2, R3 | `Network` con la máscara /28 correcta |
| 3 | `show ip dhcp binding` | R1, R2, R3 | 3 leases: 2 del pool VLAN 10 y 1 del de VLAN 20 |
| 4 | `ipconfig /all` | 1 PC de cada LAN | IP del pool + máscara /28 + gateway correcto |
| 5 | `ping 192.168.2.1` | PC propio | OK (gateway) |
| 6 | `ping` a otra LAN | PC | OK (enrutamiento) |
| 7 | `show ip route` | R1, R2, R3 | Rutas `O` (o `R`) y **sin** `S` |
| 8 | `show ip ospf neighbor` | R1, R2, R3 | 2 vecinos en `FULL` |
| 9 | `show ip route static` | R1, R2, R3 | Vacío |
| 10 | Prenda de un enlace | R2 | Ping entre sedes sigue OK (redundancia) |
| 11 | `show vlan brief` | SW1, SW2, SW3 | VLAN 10 y 20, con Fa0/4 en la 20 |
| 12 | `show interfaces trunk` | SW1, SW2, SW3 | Fa0/1 trunca, native VLAN 10, allowed 10,20 |
| 13 | `show ip interface brief` | R1, R2, R3 | `Gi0/0` y `Gi0/0.20` con IP /28 cada una |
| 14 | `show ip dhcp pool` | R1, R2, R3 | 2 pools por router: el de la VLAN 10 y el de la 20 |
| 15 | `ipconfig /all` | PC-A3, PC-B3, PC-C3 | IP del pool de la VLAN 20 y gateway de esa VLAN |

## Parte 6 — Troubleshooting: los 8 errores típicos

| Síntoma | Causa probable | Solución |
|---------|----------------|----------|
| Interface aparece `administratively down` | Falta `no shutdown` | `interface Gi0/0` → `no shutdown` |
| PC obtiene `169.254.x.x` (APIPA) | El router no responde el DHCP: falta la IP en Gi0/0, o el pool tiene otra red/máscara, o el cable del PC está mal | `show ip interface brief`, `show ip dhcp pool`, revisar cable |
| PC obtiene IP pero no hace ping al gateway | IP del PC fuera del rango o máscara incorrecta | `ipconfig /release` + `ipconfig /renew`, revisar `network` del pool |
| Un PC se quedó con la IP del gateway | El gateway no estaba excluido | `ip dhcp excluded-address ...`, `clear ip dhcp binding <ip>` |
| Ping al gateway OK, a otra LAN falla | Falta la ruta estática, o no se quitó al activar OSPF | `show ip route static`, `show ip route` (¿aparece `S` u `O`?) |
| `show ip ospf neighbor` no muestra nada | Áreas distintas, red mal declarada en `network`, o cable de hellos caído | Revisar `area 0` en los 3, `show ip ospf interface brief` |
| OSPF instalado pero sigue saliendo `S` | La estática tiene menor distancia administrativa | `no ip route ...` en los 3 routers |
| RIPv2 no anuncia las subredes | Falta `no auto-summary` | `no auto-summary` dentro de `router rip` |

### Comando de rescate de emergencia

Si un router quedó mal configurado y no sabes qué corregir:

```text
enable                ! modo privilegiado: sin esto el router no deja borrar nada
erase startup-config  ! borra la config de arranque; deja el router como de fábrica
reload                ! reinicia y aplica el borrado; responde yes cuando pregunte
```

Vuelve a la Parte 3 de la Sesión A y reingresa la configuración.

## Preguntas de la Sesión B

1. ¿Por qué una ruta estática (distancia 1) gana siempre a una ruta OSPF
   (distancia 110)? ¿Qué hubiera pasado si las hubieras dejado juntas?
2. Explica el significado de `passive-interface GigabitEthernet0/0` y qué
   pasaría con `show ip ospf neighbor` si lo quitaras.
3. En `[110/2]`, ¿qué significan los dos números? ¿Cómo se calcula el 2?
4. Compara el tiempo de convergencia de OSPF y RIPv2. ¿Cuál usarías en una red
   de 50 routers y por qué?
5. ¿Qué diferencia hay entre `show ip route` y `show ip protocols`? ¿Qué info
   adicional da cada uno?
6. Con el enlace R2–R3 caído, ¿qué camino toma un paquete de LAN-B a LAN-C?
   ¿Y con rutas estáticas mal escritas?

## Entregable de la Sesión B

1. `show ip ospf neighbor` de los 3 routers en `FULL`.
2. `show ip route` de los 3 routers con rutas `O` (o `R`) y **sin** `S`.
3. `show ip route static` vacío en los 3.
4. `show ip protocols` de R1.
5. Evidencia de la prueba de redundancia: `ping` OK con el enlace R2 Gi0/2 en
   `shutdown` + `tracert` mostrando el camino alternativo.
6. Alternativa RIPv2: `show ip route` con rutas `R` (opcional, según lo pedido).
7. Respuestas a las 6 preguntas.