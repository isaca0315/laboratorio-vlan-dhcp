# Teoría del Laboratorio N.º 13 — VLSM, DHCP y enrutamiento

> Contenido completo de [`Teoria-Lab-VLSM-DHCP.pptx`](Teoria-Lab-VLSM-DHCP.pptx)
> (31 diapositivas, 16:9). Este archivo es el volcado textual de la presentación:
> mismo contenido y mismo orden de lectura, sin depender de PowerPoint.
>
> Se regenera con:
> `python3 tools/dump_ppt_md.py Teoria-Lab-VLSM-DHCP.pptx`
>
> Cada diapositiva conserva sus **notas del orador** al final, en bloques
> plegables: en GitHub y en la mayoría de editores se despliegan con un clic.

## Índice

- **1.** Teoría del Laboratorio N.º 13
- **2.** Qué vamos a ver
- **3.** Dirección IP y máscara
- **4.** Qué es una dirección IP
- **5.** Máscara de subred y prefijo
- **6.** La fórmula 2^h − 2
- **7.** VLSM
- **8.** VLSM: una máscara por necesidad
- **9.** Los dos requisitos del laboratorio
- **10.** Las 6 subredes del laboratorio
- **11.** Los 6 errores típicos de subneteo
- **12.** Switch, router y cable
- **13.** Switch y router: no son intercambiables
- **14.** Por qué una malla de 3 routers
- **15.** Ethernet y cables de cobre
- **16.** ARP: cómo el PC encuentra al gateway
- **17.** DHCP
- **18.** Por qué DHCP y no IP fija
- **19.** El DORA, paso a paso
- **20.** El pool y sus exclusiones
- **21.** Enrutamiento
- **22.** La tabla de enrutamiento
- **23.** Rutas estáticas
- **24.** Ping: necesita ruta de ida y de vuelta
- **25.** OSPF: los routers se cuentan entre sí
- **26.** RIPv2 y el resumen automático
- **27.** Redundancia: qué pasa cuando algo falla
- **28.** Verificar es parte de la teoría
- **29.** Los límites de Packet Tracer 9.0.1
- **30.** Checklist del laboratorio
- **31.** Repaso: lo que hay que saber

---

## 1. Teoría del Laboratorio N.º 13

> UNIVERSIDAD TECNOLÓGICA DE PANAMÁ · FACULTAD DE INGENIERÍA DE SISTEMAS COMPUTACIONALES

VLSM, DHCP y enrutamiento en Packet Tracer

- IP, máscara y VLSM · por qué unas subredes son /28 y otras /30
- Switch, router, ARP y DHCP · el DORA paso a paso
- Tabla de enrutamiento · rutas estáticas · OSPF · redundancia

<details><summary>Notas del orador</summary>

⏱ 0-3 min · Apertura.

Esta es la teoría que sostiene el Lab 13. No es teoría suelta: cada
bloque corresponde a algo que van a escribir en la Sesión A o B.

El hilo es: dirección IP → máscara → subredes (VLSM) → dispositivos →
DHCP → tabla de enrutamiento → estáticas → OSPF.

Pregunta de arranque para enganchar: ¿por qué en el laboratorio unas
redes usan /28 y otras /30? La respuesta está en el bloque 2.

</details>

---

## 2. Qué vamos a ver

> Cinco bloques que van del número al cable

| # | Bloque | Pregunta que responde | Min |
|---|---|---|---|
| 1 | Dirección IP y máscara | ¿Qué es un prefijo y por qué 2^h − 2? | 10 |
| 2 | VLSM | ¿Por qué unas subredes son /28 y otras /30? | 12 |
| 3 | Switch, router y cable | ¿Quién reenvía por MAC y quién por IP? | 10 |
| 4 | DHCP | ¿Cómo consigue un PC su IP sin que nadie la escriba? | 10 |
| 5 | Enrutamiento | ¿Cómo sabe el router por dónde enviar un paquete? | 14 |
| — | Cierre | Verificación, límites de PT y repaso | 4 |

**La idea que sostiene todo el laboratorio**
- Una red no es «un switch con todos juntos»: es **segmentar** con las direcciones justas, **servir** esas direcciones automáticamente, y **conectar** los segmentos con rutas.
- Cada capa depende de la anterior: si la máscara está mal, DHCP entrega direcciones imposibles y el enrutamiento ni siquiera se intentará.

<details><summary>Notas del orador</summary>

⏱ 3-4 min · Mapa de la clase.

Señala que el orden importa: no se puede entender DHCP sin la máscara,
ni el enrutamiento sin el gateway.
Deja claro que casi todo lo que vemos es teoría de la Sesión A; OSPF es
lo único de la Sesión B.

</details>

---

## 3. Dirección IP y máscara

El bloque de todo lo demás

- Qué es una dirección IP y cómo se parte en red + host
- Máscara de subred y prefijo CIDR
- La fórmula 2^h − 2 y por qué se restan 2
- Las direcciones especiales de una subred

10 min

<details><summary>Notas del orador</summary>

⏱ 4-5 min · Transición.

Pregunta para el grupo antes de avanzar: si una dirección tiene 4 octetos,
¿cuántos identifican la red y cuántos el equipo? Que el número salga de la
máscara, no del formato.

</details>

---

## 4. Qué es una dirección IP

> 32 bits que identifican un equipo dentro de una red

**Anatomía de una subred**

```text
192.168.2.1
‾‾‾‾  ‾‾‾‾   ‾‾      ‾
red    red    subred   equipo
```

| Elemento | En 192.168.2.0/28 | Para qué sirve |
|---|---|---|
| Dirección de red | .0 | Identifica la subred |
| Primera útil | .1 | Suele ser el gateway |
| Última útil | .14 | Último equipo asignable |
| Broadcast | .15 | Habla a todos a la vez |
| Máscara | 255.255.255.240 | Separa red de host |

Cada octeto va de **0 a 255** (8 bits). Los 32 bits se reparten entre la
**parte de red** (qué red es) y la **parte de host** (qué equipo es).

**El reparto lo decide la máscara, no el número**
- Con 192.168.2.1 y máscara /24, los 3 primeros octetos son red.
- Con la misma IP y máscara /28, el 4.º octeto empieza a ser de red también.
- Por eso «cuántos equipos caben» no es una propiedad de la IP: es una propiedad de la IP **más** su máscara.

**Las clases ya no se usan**
- La dirección «dice» su clase por el primer octeto (A, B, C).
- Hoy nadie usa clases: el tamaño de la red lo dice **el prefijo**.
- Por eso 192.168.2.0 puede dividirse en 6 subredes de tamaños distintos sin que nada contradiga el «diseño original».

<details><summary>Notas del orador</summary>

⏱ 5-7 min.

Insiste en que la IP sola no dice nada: hace falta la máscara.
Mismo número, distinta máscara, distinta red.

Las clases (A/B/C) aparecen en los libros por historia. Si alguien pregunta
por qué 192 es clase C: porque el diseño histórico reservaba el primer octeto
para eso. Ya es irrelevante para el cálculo.

</details>

---

## 5. Máscara de subred y prefijo

> La misma idea, dos formas de escribirla

La máscara es una cadena de bits: unos = red, ceros = host.

```text
/28 = 255.255.255.240 = 11111111.11111111.11111111.1111 0000
24 bits de red (fijos)                       4 bits de host
/30 = 255.255.255.252 = 11111111.11111111.11111111.1111 11 00
24 bits de red (fijos)                          2 bits de host
```

**/28**
prefijo

**/24**
prefijo

bits de host

hosts útiles

direcciones

| Prefijo | Máscara en decimal | Bits de host | Hosts útiles | Tamaño del bloque |
|---|---|---|---|---|
| /27 | 255.255.255.224 | 5 | 30 | 32 |
| /28 | 255.255.255.240 | 4 | 14 | 16 |
| /29 | 255.255.255.248 | 3 | 6 | 8 |
| /30 | 255.255.255.252 | 2 | 2 | 4 |
| /31 | 255.255.255.254 | 1 | 2 (punto a punto) | 4 |

**Nunca** escribas /28 en un comando de Cisco: la máscara va en decimal.

<details><summary>Notas del orador</summary>

⏱ 7-9 min.

Regla: el prefijo es el número de unos. Contar los ceros del final da el
tamaño del bloque (2^c).

Errón típico: escribir /28 en 'ip address'. Cisco espera decimal y da error.
El prefijo solo se usa con wildcard en OSPF/RIP.

/31 es caso especial (RFC 3021, sin broadcast). En Packet Tracer no se usa.

</details>

---

## 6. La fórmula 2^h − 2

> Por qué un /28 no da 16 equipos sino 14

**h bits**
cuántos bits
dedico a host

**2^h**
direcciones
totales del bloque

**− 2**
red y broadcast
no se asignan

**2^h − 2**
hosts que
puedo usar

**Los dos que se pierden**
- La **dirección de red** identifica la subred. Si un equipo la toma, el tráfico hacia el resto de la LAN se rompe.
- La **dirección de broadcast** habla a todos los equipos a la vez. Es para difusión, no para un equipo concreto.

**Los tres pasos para elegir prefijo**
| Equipos | Prueba | h | Prefijo | ¿Sirve? |
|---|---|---|---|---|
| 10 | 2^3 − 2 = 6 | 3 | /29 | No, insuficiente |
| 10 | 2^4 − 2 = 14 | 4 | /28 | Sí |
| 10 | 2^5 − 2 = 30 | 5 | /27 | Sí, pero desperdicia |
| 2 | 2^1 − 2 = 0 | 1 | /31 | No, insuficiente |
| 2 | 2^2 − 2 = 2 | 2 | /30 | Sí |

**Cuidado con el truco**
- Para elegir bits de host hay que contar los dos direcciones extra:
- **2^h ≥ equipos + 2**, no solo ≥ equipos.
- Con 10 equipos: 2^4 = 16 ≥ 12 ✓, y 2^3 = 8 < 12 ✗.
- Por eso h = 4 y el prefijo es /28.

**Regla del laboratorio**
- Se elige **el prefijo más corto que cumple**. Un /27 también serviría para 10 equipos, pero tiraría 16 direcciones por LAN.

<details><summary>Notas del orador</summary>

⏱ 9-12 min · el corazón del cálculo.

Si algo no queda claro, volver aquí.

El error del 2^h ≥ equipos (sin +2) es el más común de todos: da /29 para
10 equipos y luego un PC se queda sin dirección.

En la tabla: /29 es insuficiente y /27 wasteful. /28 es el único que cumple
exactamente. Esa es la definición de 'más eficiente'.

</details>

---

## 7. VLSM

Por qué unas subredes son /28 y otras /30

- Qué es VLSM y por qué no usar una sola máscara
- El método en 6 pasos
- Los dos requisitos del laboratorio
- Las 6 subredes y los errores típicos

12 min

<details><summary>Notas del orador</summary>

⏱ 12-13 min · Transición.

Aquí se responde la pregunta del arranque. Anota en la pizarra la
pregunta tal como la hizo el estudiante.

</details>

---

## 8. VLSM: una máscara por necesidad

> Por qué 6 redes de 192.168.2.0/24 no pueden compartir máscara

Si dividiéramos el /24 con una sola máscara, cada subred tendría el mismo tamaño. Eso es **FLSM** y desperdicia.

|  | FLSM · todo /26 | VLSM · lo que hacemos | Diferencia |
|---|---|---|---|
| LAN-A, LAN-B, LAN-C | 3 × 64 = 192 dir | 3 × 16 = 48 dir | 144 dir menos |
| Enlaces entre routers | 3 × 64 = 192 dir | 3 × 4 = 12 dir | 180 dir menos |
| Total usado | 384 de 256 ⚠ | 60 de 256 | imposible vs posible |

**Con FLSM no cabe**
- 6 subredes de 64 direcciones = 384, pero /24 solo tiene 256.
- El cálculo **falla antes de configurar nada**.
- VLSM es lo que hace posible el diseño.

**Con VLSM sobra**
- 60 direcciones usadas de 256 → **76 % libre**.
- Ese margen es el que permite crecer: añadir una subred /28 en .60 sin rehacer el direccionamiento.

**El método en 6 pasos**

**1 Ordena**
de mayor
a menor

**2 Bits**
2^h ≥ nece-
sidad + 2

**3 Prefijo**
32 − h y su
máscara

**4 Alinea**
múltiplo del
tamaño

**5 Asigna**
red, útiles,
broadcast

**6 Comprueba**
sin solapes
y ≤ 256

<details><summary>Notas del orador</summary>

⏱ 13-16 min.

El paso 4 es el que más cuesta: una /28 debe empezar en un múltiplo de 16,
una /30 en un múltiplo de 4.

Buen momento para mostrar que el error se detecta en papel: si al alinear
no cuadra, el diseño está mal antes de tocar un cable.

La tabla FLSM es un buen golpe visual: 384 > 256 es imposible de un vistazo.

</details>

---

## 9. Los dos requisitos del laboratorio

> La respuesta a «¿por qué /28 y /30?»

| Tipo de segmento | Equipos que necesitan IP | Cálculo | Prefijo | Útiles |
|---|---|---|---|---|
| LAN-A, LAN-B, LAN-C | 10 de diseño (hoy: 1 GW + 3 PCs) | 2^4 − 2 = 14 ≥ 10 | /28 | 14 |
| Enlaces entre routers | 2  (la interfaz de cada extremo) | 2^2 − 2 = 2 ≥ 2 | /30 | 2 |

Son **dos cálculos porque hay dos requisitos**. No es «subnetear las LAN» y «subnetear los routers» por separado.

**La prueba: un mismo router tiene las dos máscaras**
**R1 Gi0/0 → 192.168.2.1/28**   conecta con el switch: 10 equipos en la LAN
**R1 Gi0/1 → 192.168.2.49/30**  conecta con R2: solo 2 equipos
**R1 Gi0/2 → 192.168.2.58/30**  conecta con R3: solo 2 equipos

| Si el destino... | Por qué funciona | Por qué no |
|---|---|---|
| Un enlace es /28 | Funciona, pero sobran 12 IPs. Con 3 enlaces son 36 dir. tiradas | Desperdicio innecesario |
| Una LAN es /30 | 2 IPs útiles, el gateway toma 1 y solo queda 1 | No alcanza para 3 PCs |

**La asimetría que resume el método**
- Sobre-asignar funciona pero desperdicia. Sub-asignar rompe el laboratorio. Por eso siempre se calcula el mínimo que cumple.

<details><summary>Notas del orador</summary>

⏱ 16-19 min · la pregunta del estudiante.

Esta es la diapositiva que responde «¿por qué unas /30 y otras /28?».

El argumento central: el criterio NO es si el otro extremo es switch o
router. R1 tiene las dos máscaras en el mismo equipo. Lo que decide es
cuántos dispositivos necesitan dirección en ese segmento.

Si preguntan por qué no /31 para los enlaces: /31 existe (RFC 3021) pero
PT y el IOS clásico no la aceptan en Ethernet.

</details>

---

## 10. Las 6 subredes del laboratorio

> El resultado final del cálculo

| # | Subred | Bloque | ¿Alineada? | Red | Hosts útiles | Bcast | Uso |
|---|---|---|---|---|---|---|---|
| 1 | 192.168.2.0/28 | 16 | 0 = 0×16 ✓ | .0 | .1 – .14 | .15 | LAN-A |
| 2 | 192.168.2.16/28 | 16 | 16 = 1×16 ✓ | .16 | .17 – .30 | .31 | LAN-B |
| 3 | 192.168.2.32/28 | 16 | 32 = 2×16 ✓ | .32 | .33 – .46 | .47 | LAN-C |
| 4 | 192.168.2.48/30 | 4 | 48 = 12×4 ✓ | .48 | .49 – .50 | .51 | R1 – R2 |
| 5 | 192.168.2.52/30 | 4 | 52 = 13×4 ✓ | .52 | .53 – .54 | .55 | R2 – R3 |
| 6 | 192.168.2.56/30 | 4 | 56 = 14×4 ✓ | .56 | .57 – .58 | .59 | R3 – R1 |
| — | .60 – .255 | — | — | — | — | — | 196 libres |

**3×16**
LAN

**3×4**
enlaces

usadas

libres

**77%**
libre

**Cómo se verifica sin calculadora**
- Suma bloques: 3×16 + 3×4 = **60**.
- La siguiente posición libre es .60: es múltiplo de 16 y de 4 → cabe otra subred. Si no fuera múltiplo, el diseño estaría mal.

**Reparto interno de cada LAN**
- En LAN-A: `.1` gateway, `.2`–`.5` reservadas, `.6`–`.14` para DHCP.
- Hoy solo 3 PCs usan ese rango; las otras 6 direcciones quedan libres.
- El crecimiento real está en `.60` en adelante: eso da el 77 % libre.

<details><summary>Notas del orador</summary>

⏱ 19-22 min.

Recorre la tabla fila por fila y haz que el grupo diga si está alineada.

El detalle del reparto interno suele sorprender: el requisito decía 10
equipos, pero el plan usa los 14 útiles. No sobran IPs en las LAN.

Si piden ejercicio: ¿por qué .62/30 no vale? Porque 62 no es múltiplo de 4.
Está en SUBNETEO.md como ejercicio 2.

</details>

---

## 11. Los 6 errores típicos de subneteo

> Reconocerlos por el síntoma es más rápido que recalcular

| Error | Por qué falla | Síntoma que se ve en el lab |
|---|---|---|
| Usar /29 para una LAN | 6 útiles < 10 equipos | El 4.º PC queda en 169.254.x.x |
| Empezar la 2.ª LAN en .15/28 | .15 es el broadcast de LAN-A | Las subredes se solapan |
| Poner un /30 en .46 | 46 no es múltiplo de 4 | IOS lo rechaza: no alineada |
| Usar .50/30 como red | .50 es dirección de host | Red con bits incoherentes |
| No excluir el gateway del pool | Un PC puede tomar .1 | La LAN se parte en dos y nadie pingea |
| Escribir /28 en ip address | Cisco espera decimal | Error de sintaxis inmediato |

**El más caro: no excluir el gateway**
- Si un PC obtiene .1, se convierte en un host más.
- El router tiene dos cosas en la misma IP.
- Resultado: mitad de la LAN sin poder hablar con la otra mitad.
- Se previene con `ip dhcp excluded-address`.

**El más sutil: .15 como red**
- `.15` es el broadcast de `192.168.2.0/28`, no un host.
- La siguiente subred empieza en `.16`, siempre en el siguiente múltiplo del bloque. Never divide el espacio sin mirar la alineación.

<details><summary>Notas del orador</summary>

⏱ 22-25 min.

No leer los 6: elegir 2 y preguntar el síntoma. El de 'no excluir el
gateway' es el que más daño hace y el más difícil de diagnosticar.

El de 169.254.x.x lo van a ver en la Sesión A si algo sale mal: es la
señal de que no hubo respuesta DHCP.

</details>

---

## 12. Switch, router y cable

Quién reenvía por MAC y quién por IP

- El switch trabaja en la capa 2
- El router trabaja en la capa 3
- Por qué una malla de 3 routers y no un switch grande
- Ethernet y cables de cobre · ARP y el gateway

10 min

<details><summary>Notas del orador</summary>

⏱ 25-26 min · Transición.

Hasta ahora solo números. Ahora: quién mueve esos paquetes.

</details>

---

## 13. Switch y router: no son intercambiables

> Capa 2 contra capa 3

|  | Switch 2960 | Router 2911 |
|---|---|---|
| Capa OSI | 2 · Enlace de datos | 3 · Red |
| Decide mirando... | la dirección MAC | la dirección IP |
| Su tabla es... | tabla MAC (aprende por floods) | tabla de enrutamiento |
| Conecta... | equipos de la misma red | redes distintas entre sí |
| Aísla el broadcast? | No, lo reenvía | Sí, cada interfaz es un dominio aparte |
| En este lab | SW1, SW2, SW3 (9 PCs) | R1, R2, R3 (unen las 3 LAN) |

**La frase que resume la diferencia**
- El switch mueve **tramas dentro** de una red. El router mueve **paquetes entre** redes.
- Por eso los 9 PCs de una LAN se hablan entre sí sin que ningún router participe

**Y el switch aprende solo**
- No se configura: empieza vacío, inunda y memoriza qué MAC está en cada puerto.
- Router en cambio sí necesita que le digan por dónde salir: eso es la tabla de enrutamiento.

<details><summary>Notas del orador</summary>

⏱ 26-28 min.

Analogía útil: el switch es el mayordomo que reparte cartas dentro del
edificio; el router es el cartero que sabe salir a otra calle.

El flooding del switch es lo que hace que 'no se configure'.

</details>

---

## 14. Por qué una malla de 3 routers

> Cada uno con enlaces a los otros dos

Con 3 routers y enlaces en malla completa hay **dos caminos** entre cualquier par de sedes.

| Enlace | Subred | Extremo A | Extremo B | Cable |
|---|---|---|---|---|
| Enlace 1 | 192.168.2.48/30 | R1 Gi0/1 = .49 | R2 Gi0/1 = .50 | Cobre recto |
| Enlace 2 | 192.168.2.52/30 | R2 Gi0/2 = .53 | R3 Gi0/1 = .54 | Cobre recto |
| Enlace 3 | 192.168.2.56/30 | R3 Gi0/2 = .57 | R1 Gi0/2 = .58 | Cobre recto |

**Qué gana la malla**
- **Redundancia**: si cae un enlace, el tráfico reruta por el otro.
- Con dos rutas, el tráfico entre sedes tiene dos caminos posibles.
- En la Sesión B esto se demuestra apagando un cable.

**Por qué no un solo router central**
- Un router solo reparte IPs de la subred de **su propia** interfaz.
- Para servir las otras LANs necesita `ip helper-address`.
- Packet Tracer **no implementa** ese comando, así que el diseño del lab usa 3 routers. Es una limitación de la herramienta, no del diseño.

**Y las tres LAN van a un switch, no directamente al router**
- Cada LAN tiene su switch: SW1 con R1, SW2 con R2, SW3 con R3.
- El router solo necesita **un** cable por LAN: el de su interfaz Gi0/0.
- Los 3 PCs se reparten los puertos Fa0/2, Fa0/3 y Fa0/4 de su switch.

<details><summary>Notas del orador</summary>

⏱ 28-30 min.

Insiste en el punto de ip helper-address: es un límite de Packet Tracer,
no una buena práctica de diseño. Si alguien pregunta '¿se podría con un
router central en un router real?', la respuesta es sí.

La malla completa se explica aquí; la demostración de redundancia con
OSPF es en la Sesión B.

</details>

---

## 15. Ethernet y cables de cobre

> Por qué 15 cables recto y ninguno serial

| Qué se conecta | Tipo de cable en PT | Cuántos |
|---|---|---|
| Router ↔ switch | Copper Straight-Through | 3 |
| PC ↔ switch | Copper Straight-Through | 9 |
| Router ↔ router | Copper Straight-Through | 3 |
| Router ↔ router (variante) | Serial DCE + `clock rate` | 3 · opcional |

**Por qué recto y no crossover**
- Crossover se usaba entre dos dispositivos **iguales**.
- Como aquí todos los pares son distintos (router-switch, PC-switch), basta el recto.
- Además el 2911 tiene **auto-MDIX**: negocia solo y acepta ambos.
- En PT puedes elegir crossover y también funcionaría.

**Por qué no Serial**
- El cable serial es de WAN: entre routers **no adyacentes**.
- Si lo usas, el lado DCE necesita `clock rate 64000` o el enlace no levanta: sin reloj no hay señal.
- Requiere instalar el módulo HWIC-2T con el router apagado.
- En este lab el gigabit basta y es más simple.

**Lo primero que se ve mal: las luces**
- En Packet Tracer las Gi del 2911 nacen **apagadas administrativamente**.
- Con el cableado correcto pero sin configurar, los cables se ven **rojos**.
- Eso no significa cable mal conectado: significa que falta `no shutdown`.
- Pasa a verde solo después del `no shutdown` de la Sesión A.

<details><summary>Notas del orador</summary>

⏱ 30-32 min.

Muy probable que alguien reporte 'los cables salen rojos'. Adelantarse.

El auto-MDIX del 2911 es la razón por la que el crossover es irrelevante
aquí; en equipos viejos sin auto-MDIX sí importaba.

clock rate: el lado DCE genera el reloj. Si no lo pones, la interfaz queda
down/down aunque el cable esté perfecto.

</details>

---

## 16. ARP: cómo el PC encuentra al gateway

> El paso que casi nadie explica y todos lo ejecutan

Un PC decide **por IP**, pero en un cable Ethernet cada trama sale con una **MAC**. ARP traduce.

**PC quiere
ping 8.8.8.8**
compara
destino vs su /28

**¿Está en
mi red?**
no: .1–.14 es
mi segmento

**ARP:
"¿quién es .1?"**
broadcast a
toda la LAN

**R1 responde
con su MAC**
ARP reply
unicast

**PC encapsula
y envía a R1**
allá enruta
hacia Internet

**Por qué esto exige un gateway en la misma LAN**
- El PC **no** puede armar la trama si no conoce una MAC.
- Solo hay una MAC que puede usar: la del gateway.
- Si el gateway estuviera en otra red, el PC no podría salir nunca.
- Por eso la opción 3 del DHCP (default-router) es obligatoria.

**ARP es solo local**
- ARP nunca cruza un router. Se resuelve **por segmento**.
- Cada router hace su propio ARP hacia su siguiente salto.
- Por eso en cada /30 solo se ve tráfico entre los 2 extremos: nadie más existe en ese cable.

```text
PC-A> arp -a          R1> show ip arp
192.168.2.1   0000.0c29.5b11.22   ARPA   LAN-A R1-Gig0/0
192.168.2.5   0050.ea3d.9f01   ARPA   LAN-A PC-A
```

<details><summary>Notas del orador</summary>

⏱ 32-34 min.

Esta diapositiva responde la duda más común del lab: 'mi PC ya tiene
IP, ¿por qué necesita otra cosa?'.

Buen experimento mental: si el ping a la IP del gateway funciona pero a
otra red no, el problema no es la IP del PC: es la ruta.

El 'porque está en mi red' es la comparación de los primeros 4 octetos
más la máscara; si difieren, el destino no es local.

</details>

---

## 17. DHCP

Cómo consigue un PC su IP sin que nadie la escriba

- Por qué DHCP y no IP fija
- El DORA paso a paso
- El pool: red, opciones y exclusiones
- Qué comando se ejecuta en cada lado

10 min

<details><summary>Notas del orador</summary>

⏱ 34-35 min · Transición.

Hasta ahora el PC tenía IP porque alguien la escribió. Ahora explica
cómo la consigue solo. En el lab, los 9 PCs (3 por LAN) la reciben así.

</details>

---

## 18. Por qué DHCP y no IP fija

> Tres problemas que la IP manual no resuelve

| Problema con IP fija | Qué pasa en la práctica | Cómo lo resuelve DHCP |
|---|---|---|
| Conflicto de direcciones | Un PC nuevo toma .5 y nada funciona | El servidor entrega direcciones libres |
| Cambio de subred | Hay que tocar 15 equipos a mano | Se reconfigura el servidor |
| Cambio de gateway o DNS | Hay que editar cada equipo | El PC renueva y se actualiza |
| Equipos fuera de servicio | La IP queda reservada y desperdiciada | El pool la reutiliza |

**Y qué gana el administrador**
- Un solo lugar donde ver y cambiar la configuración de la red: `show ip dhcp binding`.
- El router es el servidor DHCP **de su propia LAN** (servidor por defecto).
- Cada LAN tiene su propio pool porque cada una necesita entregar su gateway como opción 3.

**El coste: el equipo necesita un piso de arranque**
- Sin leases el PC arranca en **APIPA**: 169.254.x.x, que **no** enrutable.
- Si ves 169.254 en un PC del lab, el DHCP no respondió. Es el primer síntoma a revisar.
- La lista de IPs esperadas en LAN-B es .17–.30; si un PC queda fuera de ese rango, el DHCP no está repartiendo esa IP.

<details><summary>Notas del orador</summary>

⏱ 35-37 min.

APIPA es el punto clave: es lo que van a ver si algo falla. Decirles que
169.254 significa 'nadie me dio dirección'.

El término correcto: el router actúa como servidor DHCP de su LAN. En el
lab cada router sirve un pool distinto (R1 → LAN-A, R2 → LAN-B, R3 → LAN-C).

</details>

---

## 19. El DORA, paso a paso

> Discover, Offer, Request, Acknowledge

| Paso | Quién envía | A quién | Mensaje | Qué lleva |
|---|---|---|---|---|
| 1 · D | PC (cliente) | broadcast 255.255.255.255 | Discover | "¿Hay algún servidor DHCP?" — su MAC |
| 2 · O | servidor DHCP | al PC | Offer | La IP que le ofrece + máscara, gw, DNS, lease |
| 3 · R | PC (cliente) | al servidor | Request | "Quiero esa" — pide específicamente esa IP |
| 4 · A | servidor DHCP | al PC | Acknowledge | Confirma y empieza el tiempo de concesión |

**El Request parece redundante**
- Si hay varios servidores, el **servidor** gana por prioridad.
- En un cliente que ya tiene dirección, el Request pide **renovar** la misma, y el tiempo se reinicia.
- Por eso renovar es más rápido que obtenerla por primera vez.

**Los puertos que lo hacen funcionar**
- Cliente UDP **68**, servidor UDP **67**.
- El Offer del servidor va a .68 porque en ese momento el cliente aún no tiene IP.
- El Discover va a 255.255.255.255: aún no hay IP, así que no puede usar un unicast.

**Dónde ver cada paso en Packet Tracer**
- Abrir **Simulation** (Alt+Shift+S), poner un filtro por protocolo `bootpc`/`DHCP` y ver las 4 ventanas.
- El paso 1 y el 3 salen del PC; el 2 y el 4, del router. El nombre de la pestaña de cada mensaje lleva el paso: DORA.

<details><summary>Notas del orador</summary>

⏱ 37-39 min.

El DORA es lo que hace 'mágico' al DHCP. Merece la pena escribir las
iniciales en la pizarra antes de continuar.

El Request no es redundante: es el que impide que dos servidores den la
misma IP y el que sirve para renovar.

Si piden ver el tráfico, esto es lo que hacen en la Sesión A con Simulation.

</details>

---

## 20. El pool y sus exclusiones

> Qué define el bloque `ip dhcp pool`

Cada router define un pool para **su** LAN. El de LAN-B, en el router R2:

```text
R2(config)# ip dhcp pool LAN_B
R2(dhcp-config)# network 192.168.2.16 255.255.255.240
R2(dhcp-config)# default-router 192.168.2.17
R2(dhcp-config)# dns-server 8.8.8.8
R2(dhcp-config)# domain-name lab-utp.pa
R2(dhcp-config)# exit
```

```text
R2(config)# ip dhcp excluded-address
192.168.2.17 192.168.2.21
R2(config)# interface gi0/0
R2(config-if)# ip address 192.168.2.17 255.255.255.240
R2(config-if)# no shutdown
R2(config-if)# exit
```

| Línea | Significado | Paquete |
|---|---|---|
| network ... máscara | Qué subred se reparte | — |
| default-router | La puerta de salida (opción 3) | DHCP Discover |
| dns-server | A quién pregunta por nombres | DHCP Discover |
| domain-name | El dominio que se registra | DHCP Discover |
| excluded-address | Qué direcciones NO se entregan | — |

**El rango que se entrega en LAN-B**
- De `.22` a `.30`. Se excluye `.17` (gateway, opción 3) y `.18` a `.21` (reservadas). Por eso el `show ip dhcp binding` debe mostrar leases **.22 – .30**.

<details><summary>Notas del orador</summary>

⏱ 39-42 min.

El error clásico aquí es olvidar las exclusiones: el servidor entrega .17
y el PC se queda con la IP del gateway.

Otra confusión: la opción 3 (default-router) **no** es una IP de la LAN,
es la dirección del propio router, y por eso se excluye del pool.

Aquí se ve por qué las excluidas van de .17 a .21 y no solo .17: en el
lab se reservan las 5 IPs para los PCs de configuración fija.

</details>

---

## 21. Enrutamiento

Cómo sabe el router por dónde enviar un paquete

- La tabla de enrutamiento y sus códigos
- Rutas estáticas y siguiente salto
- Por qué el ping necesita ruta de vuelta
- OSPF, RIPv2 y la redundancia de la malla

14 min

<details><summary>Notas del orador</summary>

⏱ 42-43 min · Transición.

Último bloque y el más largo. Es donde se une todo: las subredes del
bloque 2 se conectan entre sí con las rutas de este bloque.

La pregunta que abre el bloque: si R1 no tiene ruta hacia 192.168.2.32,
¿qué hace con un paquete que llega para esa red?

</details>

---

## 22. La tabla de enrutamiento

> La lista que el router consulta en cada paquete

Cada línea dice: **a qué red** llego, **por qué interfaz** salgo, **a qué dirección** entrego.
| Código | Significa | Cómo llegó a la tabla | Ejemplo en el lab |
|---|---|---|---|
| C | Conectada (directly connected) | Se crea sola al configurar `ip address` | 192.168.2.0/28 en Gi0/0 |
| L | Local | Se crea sola, es la IP del propio router | 192.168.2.1/32 |
| S | Estática | Alguien la escribió a mano con `ip route` | S 192.168.2.32/28 via .49 |
| O | OSPF | Aprendida de los vecinos por multicast | O 192.168.2.32/28 via .58 |
| R | RIP | Aprendida de los vecinos por broadcast | R 192.168.2.32/28 via .58 |

**Cómo decide el router**
- 1. Mira la **más específica** que coincide: /28 gana sobre /24.
- 2. Si hay empate, elige la de **menor distancia administrativa**.
- 3. Si sigue el empate, la de **menor costo**.
- 4. El resto se descarta: la red se descarta.

**La distancia administrativa**
- El número que dice cuán creíble es cada fuente:
- Estática = **1** (la que el admin escribió, siempre gana).
- OSPF = **110**, RIP = **120**.
- Por eso, si dejaste la estática, **OSPF no se usará** aunque R2 ya sepa la ruta.

**La diferencia entre C y L, que confunde siempre**
- `C` es la **subred** completa que la interfaz sirve (192.168.2.0/28).
- `L` es la **dirección propia** del router en esa interfaz (192.168.2.1/32), la que responde a los pings locales.

<details><summary>Notas del orador</summary>

⏱ 43-45 min.

La tabla de enrutamiento es el 'show ip route' que van a leer mil veces.
Enseñarlo ahora, antes de las rutas, evita que sea un bloque de letras.

El punto de la distancia administrativa es importante: explica por qué en
la Sesión B, si la estática sigue puesta, la ruta que se ve en el ping
puede no ser la de OSPF.

C vs L: la analogía útil es que C es la dirección de la calle y L es tu
número de casa en esa calle.

</details>

---

## 23. Rutas estáticas

> Tres partes, y la tercera es la que se olvida

```text
R1(config)# ip route 192.168.2.32 255.255.255.240 192.168.2.49
red de destino        máscara        siguiente salto
```

**Las tres partes de una ruta estática**
| Parte | Qué es | Qué pasa si te equivocas |
|---|---|---|
| Red de destino | La red que quieres alcanzar | Alcanzas la red equivocada o nada |
| Máscara | Cuántos bits son red | Con máscara incorrecta no hay coincidencia |
| Siguiente salto | La IP del router vecino | Sin ruta hacia él: no se puede entregar |

**El requisito invisible: el siguiente salto debe ser alcanzable**
- Un router **no** puede enviar a una dirección que no ve en su tabla.
- El siguiente salto tiene que estar en una red conectada (código C) del router.
- Ejemplo: en R1, `.49` es alcanzable porque está en 192.168.2.48/30, que es C.
- Por eso los enlaces del lab son /30 y no /28: así cada vecino es alcanzable.

```text
R1# show ip route static        R1# show ip route 192.168.2.32
```

<details><summary>Notas del orador</summary>

⏱ 45-48 min.

El error número uno de la Sesión A: poner la IP de destino como siguiente
salto, o poner una IP que no está conectada.

Si el siguiente salto no está en una red conectada, el IOS acepta el
comando pero la ruta no se puede usar (sale como 'no next hop').

La analogía del siguiente salto: no es el destino final, es a quién le
entrego el paquete para que llegue más cerca del destino.

</details>

---

## 24. Ping: necesita ruta de ida y de vuelta

> El error más costoso del laboratorio

Un paquete que llega y **no se devuelve** se pierde igual. El ping solo tiene éxito si ambos caminos existen.
| Sentido | R1 necesita | R2 necesita | Si falta |
|---|---|---|---|
| PC-A (LAN-A) → PC-B (LAN-B) | S → LAN-B via .49 | C → LAN-A (ya conectada) | R1 no sabe salir |
| PC-B (LAN-B) → PC-A (LAN-A) | C → LAN-B (ya conectada) | S → LAN-A via .50 | R2 no sabe volver |
| Si solo hay una de las dos | — | — | Se queda en 0 replies |

**La trampa: la tabla parece correcta y aun así no hay respuesta**
- Cada router por separado **sí** tiene la ruta de salida hacia el otro.
- Falta la de vuelta: el paquete llega al destino, pero el destino no sabe regresar. El ping se ve como «timeout» aunque la ruta de ida exista.
- Por eso el `ping` de verificación se hace **desde el router**, con la IP de la interfaz de salida, no solo desde el PC.

**El ping que sí prueba el camino completo**
- **ping desde el PC** de origen hacia el PC destino: prueba ida y vuelta.
- **ping desde el router** con su IP de salida: prueba solo la ruta de ese router.
- Si el ping desde el router funciona pero el del PC no, el problema está en el **PC** (IP o gateway mal).
- Si ninguno de los dos funciona, el problema está en las **rutas**.

<details><summary>Notas del orador</summary>

⏱ 48-50 min.

Este es el error más caro del lab porque la tabla parece correcta.

Diagnóstico: si el ping al gateway propio funciona pero al otro lado no,
es un problema de rutas, no de la IP del PC.

El ping con IP de origen es el comando clave: 'ping 192.168.2.33' desde
R1, no desde el PC.

</details>

---

## 25. OSPF: los routers se cuentan entre sí

> De estáticas a dinámico

| Concepto | Qué es | En el lab |
|---|---|---|
| Link-state | Cada router anuncia qué redes tiene conectadas | R1 anuncia sus 3 subredes |
| Área (area) | Grupo de routers que comparten LSDB. El área 0 es la backbone | Los 3 routers en área 0 |
| Router ID | Identificador único (un IP). Se elige con `router-id` | R1=.1, R2=.17, R3=.33 |
| LSDB | La base de datos con todas las redes conocidas | `show ip ospf database` |
| SPF | Algoritmo (Dijkstra) que calcula el camino más corto | Calcula la ruta de menor costo |
| Hellos | Paquetes cada 10 s para saber si el vecino sigue vivo | `show ip ospf neighbor` |
| Estado FULL | Los dos vecinos se reconhecieron | Debe verse FULL en los 3 |
| Passive | La interfaz anuncia la red pero no manda hellos | Gi0/0 de cada router es pasiva |

**Por qué pasiva la interfaz de la LAN**
- Gi0/0 de cada router va al switch de su LAN, donde están los **3 PCs**.
- Si la interfaz mandara hellos, los PCs recibirían paquetes OSPF que no entienden y la red se inundaría.
- `passive-interface` anuncia la red pero silencia el hello: es lo correcto.

**Qué se gana con OSPF en este lab**
- Los 3 routers **aprendan** las rutas de los otros, no hay que escribirlas.
- Si un enlace cae, se recalcula y el tráfico va por el otro.
- `show ip ospf neighbor` debe dar 3 vecinos FULL.
- En la Sesión B se quita una estática y se ve la ruta OSPF (`O`).

<details><summary>Notas del orador</summary>

⏱ 50-53 min.

OSPF es el bloque más denso. No entrar en detalle de tipos de router ni
estados exentos: basta con link-state + área 0 + SPF.

El router-id es fijo en el lab (1, .17, .33) porque si no lo fijamos, IOS
lo elige solo y puede cambiar entre reinicios.

Passive-interface: el error típico es ponerlo en las interfaces de los
enlaces entre routers, que entonces no se vecindan.

</details>

---

## 26. RIPv2 y el resumen automático

> El protocolo más simple, y su trampa clásica

RIP es distance-vector: cada router cuenta saltos hasta la red y comparte el contador.

```text
R1(config)# router rip
R1(config-router)# version 2
R1(config-router)# network 192.168.2.0
R1(config-router)# no auto-summary
```

**Por qué `no auto-summary` no es opcional aquí**
- Con VLSM en la red, el resumen automático **manda 192.168.2.0/24** en lugar de las subredes correctas.
- El vecino recibe una ruta que no corresponde y descarta la información real.
- Con `no auto-summary` se difunden las subredes con su máscara real.
- Es uno de los errores clásicos del protocolo RIP con VLSM.

**Limitaciones de RIP**
- Máximo **15 saltos**: a partir de ahí la red es inalcanzable.
- Métrica por saltos, no por ancho de banda real.
- Converge lento (30 s por defecto) frente a OSPF.
- En el lab se usa para **comparar**, no para producción.

**OSPF frente a RIP en este mismo laboratorio**
|  | RIPv2 | OSPF |
|---|---|---|
| Tipo | distance-vector | link-state |
| Métrica | saltos (≤ 15) | costo por ancho de banda |
| Convergencia | lenta | rápida |
| VLSM | con `no auto-summary` | nativo |

<details><summary>Notas del orador</summary>

⏱ 53-55 min.

No hace falta dominar RIP: la idea es comparar y ver por qué OSPF es el
que se usa en el lab.

El error de auto-summary solo aparece cuando hay VLSM. Como el lab usa
VLSM justamente, es el caso donde hay que verlo.

</details>

---

## 27. Redundancia: qué pasa cuando algo falla

> La malla se diseñó para esto

Con la malla completa, cada par de LANs tiene **dos caminos**. Esto es lo que se demuestra al final.
| Fallo | Con rutas estáticas | Con OSPF |
|---|---|---|
| Caen Gi0/1 de R1 (enlace R1–R2) | El tráfico muere hasta arreglarlo | Se recalcula y va por R1–R3–R2 |
| Cae un switch (SW2) | Esa LAN desaparece; las otras siguen | Igual: solo cae esa LAN |
| Se borra una estática | Se pierde esa ruta al instante | OSPF mantiene la ruta aprendida |
| Vuelve el enlace | Manual: rehacer la ruta | Automático, recalcula |

**La demostración de la Sesión B, en orden**
- 1. `show ip ospf neighbor` → los 3 vecinos en **FULL**.
- 2. Borrar la ruta estática a LAN-C en R1 → el ping **sigue** funcionando.
- 3. `show ip route` → la ruta a LAN-C ahora aparece con código **O**, no S.
- 4. Apagar un enlace → el tráfico sigue por el camino que queda.

**El mensaje que hay que llevarse**
- Las rutas estáticas no tienen «plan B»: si una falta, el tráfico se cae.
- Un protocolo dinámico es lo que hace que la topología de malla sirva de algo.

<details><summary>Notas del orador</summary>

⏱ 55-57 min.

Esta diapositiva es el puente directo con la Sesión B: los 4 pasos son
literalmente lo que se hace al final del laboratorio.

El paso 2 es el que convence: si el ping sigue funcionando sin la
estática, es porque OSPF ya tenía esa ruta aprendida.

Aviso: si el ping falla en el paso 2, es que OSPF no converge. Revisar
network, router-id y que los 3 estén en área 0.

</details>

---

## 28. Verificar es parte de la teoría

> Cada comando responde una pregunta concreta

| Comando | Pregunta que responde | Qué debe verse |
|---|---|---|
| show ip interface brief | ¿La interfaz está up? | Gi0/0 up/up, Gi0/1 up/up |
| show ip route | ¿Por dónde sale el tráfico? | C para las 3 subredes + S (u O) |
| show ip dhcp binding | ¿A quién se le entregó una IP? | Leases .22 – .30 en LAN-B |
| show ip dhcp server statistics | ¿Cuántos DORA hubo? | DISCOVER, OFFER, REQUEST, ACK |
| show ip arp | ¿Quién está en mi LAN? | IP ↔ MAC de los vecinos |
| show ip ospf neighbor | ¿Se conocen los routers? | 3 vecinos en estado FULL |
| show ip route ospf | ¿Qué rutas aprendió OSPF? | Rutas con código O |
| show ip protocols | ¿Qué protocolos corren? | OSPF en área 0, RIP si aplica |

**La pregunta que hace el diagnóstico correcto**
- Antes de cambiar nada: **¿en qué capa está el problema?**
- Interfaz down → capa 1/2 (cable, `no shutdown`).
- Sin IP o 169.254 → capa 2 (DHCP no respondió, o falta `ip address`).
- Con IP pero sin ruta → capa 3 (falta `ip route`, o falta la ruta de vuelta).

<details><summary>Notas del orador</summary>

⏱ 57-58 min.

Esta tabla es el índice del COMANDOS.md. Decirla de memoria es mejor que
recitarla.

El enfoque de capas es lo que más rinde en el laboratorio: evita cambiar
cosas al azar. Interface down no se arregla con una ruta.

</details>

---

## 29. Los límites de Packet Tracer 9.0.1

> Lo que la herramienta no hace

| Lo que quieres | Qué hace PT 9.0.1 | Solución en el lab |
|---|---|---|
| `lease 7 8 23` | No existe en el IOS de PT | Se omite; el lease por defecto es 1 día |
| Dos `dns-server` | Solo acepta uno | `dns-server 8.8.8.8` |
| `ip helper-address` | No implementado | Cada router sirve su LAN (3 pools) |
| Ripv2 con VLSM | Requiere `no auto-summary` explícito | Se incluye en la config |
| Comando existencial | El IOS de PT acepta `?` para=listar | Úsalo si dudas |

**Por qué `ip helper-address` cambia el diseño**
- Un router con esa orden puede servir DHCP para redes a las que no está conectado.
- Como PT no lo implementa, el laboratorio usa **3 servidores DHCP** en vez de uno.
- Es una limitación del simulador: en un router real, un solo servidor central bastaría.

**La regla de oro con Packet Tracer**
- Si un comando no existe, el propio simulador lo dice: el prompt `?` lista lo válido.
- No copies comandos de un libro sin verificarlos: las versiones del IOS cambian.
- La configuración del lab está en `config/R1.txt`, `R2.txt` y `R3.txt`, ya validadas.

<details><summary>Notas del orador</summary>

⏱ 58-59 min.

Esta diapositiva es el puente con la práctica: lo que se ve en la Sesión A
tiene que coincidir con esta tabla, o el comando se va a rechazar.

El uso de ? es el mejor hábito: si un comando falla, no es que esté mal
escrito, es que no existe en esa versión.

</details>

---

## 30. Checklist del laboratorio

> Todo lo teórico, en orden de ejecución

| # | Paso | Bloque | Qué debe pasar |
|---|---|---|---|
| 1 | Verificar VLSM antes de configurar | 2 | Las 6 subredes, alineadas y sin solapes |
| 2 | Cablear: 15 cables rectos | 3 | Cables rojos hasta hacer `no shutdown` |
| 3 | `no shutdown` en las 3 Gi | 3 | Las luces pasan a verde |
| 4 | `ip address` en cada interfaz | 1 | Aparecen las rutas C en `show ip route` |
| 5 | `ip dhcp pool` + excluded en cada router | 4 | 3 pools, uno por LAN |
| 6 | `ipconfig /renew` en los PCs | 4 | Leases .22 – .30 en LAN-B |
| 7 | Ping al gateway y a la otra LAN | 5 | Ida y vuelta en ambos sentidos |
| 8 | Rutas estáticas hacia la tercera LAN | 5 | Los 3 se alcanzan entre sí |
| 9 | OSPF área 0 + router-id | 5 | 3 vecinos FULL |
| 10 | Borrar una estática y reintentar | 5 | El ping sigue, ahora por OSPF |

**El orden importa más de lo que parece**
- No se puede hacer DHCP sin la interfaz configurada (paso 4 antes de 5).
- Y no se puede enrutar sin VLSM calculado (paso 1 antes de 8).

<details><summary>Notas del orador</summary>

⏱ 59-60 min · Cierre.

Usar como índice del laboratorio. Cada fila corresponde a un bloque de la
teoría que ya se dio.

El paso 7 (ping) y el paso 10 (borrar la estática) son los que más
diagnostican. Si algo falla, volver a la tabla de verificación.

</details>

---

## 31. Repaso: lo que hay que saber

> Cinco ideas y las cinco preguntas que dejan

**Las 5 ideas**
1. La máscara decide el reparto red/host; la IP sola no dice nada. /28 son 14 útiles, /30 son 2.
2. VLSM da a cada subred la máscara que necesita: /28 para las LAN, /30 para los enlaces.
3. El switch reenvía por MAC, el router por IP. ARP traduce IP→MAC solo dentro de la red.
4. DHCP reparte por DORA, con gateway y DNS; se excluye el .1 del pool.
5. El router elige ruta: la más específica y la de menor distancia. OSPF aprende y recalcula.

**Las 5 preguntas para comprobar que se entendió**

1. ¿Por qué un /28 da 14 hosts y no 16? ¿Qué dos direcciones se pierden?
2. ¿Por qué los enlaces entre routers son /30 y no /28 en este laboratorio?
3. Un ping al gateway funciona pero a otra LAN no. ¿Qué capa revisarías primero?
4. Un PC muestra 169.254.x.x. ¿Qué significa y dónde se mira?
5. ¿Qué cambia en la tabla de enrutamiento si borras una ruta estática que OSPF ya conoce?

<details><summary>Notas del orador</summary>

Cierre · Preguntas.

Estas 5 preguntas cubren los 5 bloques. Si responden las 5, tienen la
teoría suficiente para el laboratorio.

La 3 y la 4 son las que más se confunden en la práctica: distinguen
un problema de capa 2 de uno de capa 3.

</details>
