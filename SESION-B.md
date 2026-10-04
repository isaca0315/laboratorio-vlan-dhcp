# Sesión B — Enrutamiento dinámico (OSPF / RIPv2) y diagnóstico

Laboratorio N.º 13 · Unidad III · **Cisco Packet Tracer**

Objetivo: sustituir las rutas estáticas de la Fase A por enrutamiento dinámico
(**OSPF área 0**, con **RIPv2** como alternativa), comprobar la convergencia y
demostrar la **redundancia** de enlaces que aportan los protocolos dinámicos.

## Parte 1 — Estado de partida

Antes de tocar nada, confirma que la Fase A quedó bien:

```text
show ip route static
show ip route
ping 192.168.2.38        ← desde PC-A1: debe responder
```

Si el ping entre sedes falla, **no sigas**: primero corrige la Fase A (ver
sesión B, Parte 5).

## Parte 2 — Fase B: OSPF área 0

### Paso 2.1 — Por qué OSPF y no estáticas

| Ventaja | Explicación |
|---------|-------------|
| Automático | No hay que escribir rutas al añadir un sitio nuevo |
| Detección de caídas | Los hellos detectan el enlace caído en segundos |
| Mejor ruta | Elige por costo (métrica) y no por "lo que escribí" |
| Escalable | Con 30 routers seguirías usando 1 comando por router, no 29 rutas |

### Paso 2.2 — Qué significa el comando

```text
router ospf 10                      ← proceso OSPF con ID local 10
 network 192.168.2.0 0.0.0.255      ← wildmask: todo 192.168.2.x participates
 area 0                              ← área backbone (todos deben coincidir)
 passive-interface GigabitEthernet0/0 ← no enviar hellos por la LAN de PCs
```

> El **wildmask** es la inversa de la máscara: `/24` → máscara
> `255.255.255.255` → wildmask `0.0.0.255`. Se puede abreviar:
> `network 192.168.2.0 area 0` (Packet Tracer lo acepta y expande solo).

### Paso 2.3 — Configurar los 3 routers

```text
! ---------- R1 ----------
configure terminal
router ospf 10
 router-id 192.168.2.1
 network 192.168.2.0 0.0.0.255 area 0
 passive-interface GigabitEthernet0/0
end

! ---------- R2 ----------
configure terminal
router ospf 10
 router-id 192.168.2.17
 network 192.168.2.0 0.0.0.255 area 0
 passive-interface GigabitEthernet0/0
end

! ---------- R3 ----------
configure terminal
router ospf 10
 router-id 192.168.2.33
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

### Paso 2.4 — Quitar las rutas estáticas

Se **deben eliminar**, si no OSPF no podrá instalar sus rutas (la estática, más
específica en distancia administrativa, siempre gana):

```text
! ---------- R1 ----------
configure terminal
no ip route 192.168.2.16 255.255.255.240 192.168.2.50
no ip route 192.168.2.32 255.255.255.240 192.168.2.57
end

! ---------- R2 ----------
configure terminal
no ip route 192.168.2.0 255.255.255.240 192.168.2.49
no ip route 192.168.2.32 255.255.255.240 192.168.2.54
end

! ---------- R3 ----------
configure terminal
no ip route 192.168.2.0 255.255.255.240 192.168.2.58
no ip route 192.168.2.16 255.255.255.240 192.168.2.53
end
```

Comprobación de que ya no quedan estáticas (no debe mostrar nada):

```text
show ip route static
```

### Paso 2.5 — Verificar la vecindad OSPF

```text
show ip ospf neighbor
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

### Paso 2.6 — Verificar la tabla de enrutamiento

```text
show ip route
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

### Paso 2.7 — Probar conectividad

```text
show ip route 192.168.2.32        ← debe indicar OSPF en la línea install
ping 192.168.2.22
ping 192.168.2.38
```

Y desde los PCs, los mismos 9 pings de la Fase A deben seguir respondiendo.

### Paso 2.8 — Demostrar la redundancia (prueba clave)

1. En R2: `configure terminal` → `interface GigabitEthernet0/2` → `shutdown`.
2. Espera ~40 s y en R1 ejecuta `show ip ospf neighbor` (R2 debe salir como
   `DOWN` o desaparecer de esa interfaz) y `show ip route`.
3. Vuelve a hacer ping desde **PC-A1** a `192.168.2.38` (LAN-C).

Resultado esperado: **los pings siguen funcionando**, ahora por el camino
R1 → R3 directo, porque OSPF recalculó la mejor ruta. Repite la prueba con
`tracert` para ver que el camino cambió.

Después restaura el enlace:

```text
interface GigabitEthernet0/2
 no shutdown
```

> Con rutas **estáticas** (Fase A) esta prueba también funcionaría en esta malla
> pequeña, porque las rutas apuntan a la subred del vecino y no a su interfaz
> concreta. En una cadena o en un escenario real, la diferencia es decisiva: el
> estático no sabe que el enlace murió hasta que alguien lo actualiza a mano.

## Parte 3 — Alternativa: RIPv2

Úsala solo si el profesor lo pide o si quieres **comparar** ambos protocolos en la
misma topología.

### Paso 3.1 — Configurar

```text
! ---------- R1 ----------
configure terminal
no router ospf 10
router rip
 version 2
 no auto-summary
 network 192.168.2.0
end

! ---------- R2 ----------
configure terminal
no router ospf 10
router rip
 version 2
 no auto-summary
 network 192.168.2.0
end

! ---------- R3 ----------
configure terminal
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

### Paso 3.2 — Verificar

```text
show ip route
```

```text
R1#show ip route
      192.168.2.0/24 is variably subnetted, 5 subnets, 3 masks
C        192.168.2.0/28 is directly connected, GigabitEthernet0/0
R        192.168.2.16/28 [120/1] via 192.168.2.50, 00:00:12
R        192.168.2.32/28 [120/1] via 192.168.2.57, 00:00:12
```

```text
show ip protocols
show ip rip database
```

### Paso 3.3 — OSPF vs RIPv2 en esta topología

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

Para volver a OSPF: `no router rip` y volver a la Parte 2.

## Parte 4 — Verificación final (checklist)

| # | Comando | Dónde | Resultado esperado |
|---|---------|-------|--------------------|
| 1 | `show ip interface brief` | R1, R2, R3 | 3 interfaces `up/up` con IP |
| 2 | `show ip dhcp pool` | R1, R2, R3 | `Network` con la máscara /28 correcta |
| 3 | `show ip dhcp binding` | R1, R2, R3 | 3 leases en el rango asignable |
| 4 | `ipconfig /all` | 1 PC de cada LAN | IP del pool + máscara /28 + gateway correcto |
| 5 | `ping 192.168.2.1` | PC propio | OK (gateway) |
| 6 | `ping` a otra LAN | PC | OK (enrutamiento) |
| 7 | `show ip route` | R1, R2, R3 | Rutas `O` (o `R`) y **sin** `S` |
| 8 | `show ip ospf neighbor` | R1, R2, R3 | 2 vecinos en `FULL` |
| 9 | `show ip route static` | R1, R2, R3 | Vacío |
| 10 | Prenda de un enlace | R2 | Ping entre sedes sigue OK (redundancia) |

## Parte 5 — Troubleshooting: los 8 errores típicos

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
enable
erase startup-config
reload          → responde "yes" cuando pregunte
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