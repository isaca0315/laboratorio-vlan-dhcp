# Referencia de comandos del laboratorio

Qué hace **cada comando** que aparece en `config/R1.txt`, `config/R2.txt` y
`config/R3.txt`, más los de verificación. Todos están verificados contra la
referencia de comandos que instala Packet Tracer 9.0.1 para el 2911
(`2900_universal_security_15.1.html`).

---

## 1. Los modos de la CLI

IOS tiene niveles de privilegio. El prompt te dice en cuál estás:

| Prompt | Modo | Qué puedes hacer |
|--------|------|------------------|
| `R1>` | usuario | Solo mirar, no cambia nada |
| `R1#` | privilegiado (`enable`) | Ver todo, guardar, entrar a configuración |
| `R1(config)#` | configuración global | Cambiar todo el router |
| `R1(config-if)#` | configuración de interfaz | Cambiar una interfaz |
| `R1(config-dhcp-pool)#` | configuración de pool DHCP | Definir qué IPs se entregan |

| Comando | Qué hace |
|---------|----------|
| `enable` | Pasa de usuario a privilegiado. Si hay `enable secret`, pide contraseña |
| `configure terminal` (o `conf t`) | Entra a configuración global |
| `end` | Sale un nivel: de interfaz vuelve a config global, de ahí a privilegiado |
| `exit` | Sale del modo actual |
| `?` | **El comando más útil**: lista las opciones válidas en el modo actual |

> La diferencia entre `end` y `exit` importa en el pool DHCP: `end` te saca del
> pool, `exit` también. Usa `end` cuando dudes.

---

## 2. Identificación del equipo

| Comando | Qué hace | En este lab |
|---------|----------|-------------|
| `hostname R1-SEDE-A` | Renombra el router. Aparece en el prompt y en la configuración | Identifica cada sede |
| `no ip domain-lookup` | Deja de pedir DNS cuando escribes mal un comando | Evita el retraso de 30 s al teclear mal |
| `banner motd @ texto @` | Mensaje de bienvenida al entrar por consola | Identifica el equipo al conectar. El `@` final evita el espacio sobrante |
| `enable secret cisco` | Contraseña cifrada para el modo privilegiado | Después de esto, `enable` pide contraseña |
| `service password-encryption` | Cifra las contraseñas que aparecen en texto plano | Complementa al `secret` (cifrado débil, es ornamental) |
| `line console 0` / `password cisco` / `logging synchronous` | Configura la línea de consola: contraseña y salida de mensajes sin cortar lo que escribes | Acceso por consola |
| `line vty 0 4` / `login` / `transport input ssh` / `password cisco` | Configura las 5 líneas de acceso remoto: exige login, solo por SSH, con contraseña | Acceso remoto seguro |

> `password` (texto plano) y `enable secret` (cifrado) no son lo mismo: el
> primero se ve en `show running-config` aunque el servicio de cifrado lo
> esconda. Paraprivileged mode se usa siempre `enable secret`.

---

## 3. Interfaces

| Comando | Qué hace | En este lab |
|---------|----------|-------------|
| `interface GigabitEthernet0/0` | Entra a la configuración de esa interfaz | Separar LAN de enlaces |
| `description LAN-A - Gateway 192.168.2.1/28` | Etiqueta la interfaz | Para saber qué cable va dónde al leer la config |
| `ip address 192.168.2.1 255.255.255.240` | Asigna IP y máscara a la interfaz | **Aquí va el `/28` de la LAN** |
| `no shutdown` | Activa la interfaz | **Imprescindible**: en PT las Gi nacen apagadas |

> **Máscara siempre en decimal.** `255.255.255.240` es el `/28`; escribir `/28`
> da error de sintaxis. La forma `/28` solo se usa en OSPF/RIP con *wildcard*.

> `Gi0/0` es la LAN en los tres routers, por diseño. Eso permite que
> `passive-interface GigabitEthernet0/0` se escriba igual en R1, R2 y R3.

---

## 4. Servidor DHCP

**Primero se excluyen** (modo configuración global):

| Comando | Qué hace | En este lab |
|---------|----------|-------------|
| `ip dhcp excluded-address 192.168.2.1 192.168.2.5` | Rango que **nunca** se entrega | Gateway (`.1`) + 4 fijas admin (`.2`–`.5`) |

**Luego el pool** (`ip dhcp pool` es global; el resto va dentro):

| Comando | Qué hace | En este lab |
|---------|----------|-------------|
| `ip dhcp pool LAN-A` | Crea el pool y entra a su modo | Uno por LAN |
| `network 192.168.2.0 255.255.255.240` | Define la subred del pool | La **red** y la **máscara**, no el gateway |
| `default-router 192.168.2.1` | Gateway que recibe el PC (opción 3) | La IP de la interfaz LAN del router |
| `dns-server 8.8.8.8` | DNS que recibe el PC (opción 6) | Google. **En PT solo se acepta uno** |
| `domain-name lab-utp.pa` | Dominio que recibe el PC (opción 15) | Nombre del laboratorio |

> **Por qué cada router sirve su propia LAN:** un router solo reparte direcciones
> de la subred de su propia interfaz. Para servir una LAN remota hace falta
> `ip helper-address`, que el 2911 de Packet Tracer **no tiene**. Por eso el
> diseño usa 3 routers en vez de 1 central con 3 LANs.

---

## 5. Rutas estáticas (Fase A)

| Comando | Qué hace |
|---------|----------|
| `ip route 192.168.2.16 255.255.255.240 192.168.2.50` | Ruta manual: "para llegar a `192.168.2.16/28`, entrega al `.50`" |
| `no ip route 192.168.2.16 255.255.255.240 192.168.2.50` | Borra esa ruta (para dar paso a OSPF) |
| `show ip route static` | Solo las estáticas |

**Las tres partes son obligatorias:** red destino, máscara, siguiente salto. El
siguiente salto **debe ser alcanzable por una interfaz conectada**; si no, la ruta
queda inútil. Ejemplo: R1 usa `.50` porque esa IP es la de R2 en la red
`192.168.2.48/30` que R1 tiene conectada en `Gi0/1`.

---

## 6. OSPF (Fase B)

| Comando | Qué hace |
|---------|----------|
| `router ospf 10` | Crea el proceso OSPF. El **10 es un número local**, no el área |
| `router-id 192.168.2.1` | Identidad del router dentro de OSPF. Debe ser **única** entre los vecinos |
| `network 192.168.2.0 0.0.0.255 area 0` | Declara qué interfaces participan: prefijo + **wildcard** + área |
| `passive-interface GigabitEthernet0/0` | No enviar hellos por esa interfaz |
| `no router ospf 10` | Elimina el proceso OSPF completo |

**El wildcard es la máscara invertida:**

| Máscara | Wildcard | Prefijo |
|---------|----------|---------|
| 255.255.255.0 | 0.0.0.255 | /24 |
| 255.255.255.240 | 0.0.0.15 | /28 |
| 255.255.255.252 | 0.0.0.3 | /30 |

`network 192.168.2.0 0.0.0.255 area 0` resume **las 6 subredes** del lab en una
sola línea, porque todas caen dentro de `192.168.2.0/24`.

**`router-id` fijo:** si no lo configuras, cada router elige la IP más alta de
una interfaz activa (R1 = `.58`, R2 = `.53`, R3 = `.57`). Fijarlo a `.1`/`.17`/`.33`
hace el lab **determinista** y lo que ves en `show ip ospf neighbor` coincide con
el material.

**`passive-interface`:** en las LAN no hay ningún router vecino, así que los hellos
ahí solo consumen ancho de banda. En los tres enlaces entre routers sí se mandan,
por eso se advertise vecindad.

---

## 7. RIPv2 (alternativa)

| Comando | Qué hace |
|---------|----------|
| `router rip` | Entra al modo de configuración de RIP |
| `version 2` | RIP v2 (envía máscara, a diferencia de la v1) |
| `no auto-summary` | **Crítico en VLSM**: sin esto, RIP v2 resumirá las subredes y sumariza mal |
| `network 192.168.2.0` | Interfaces dentro del rango participan. Aquí **no** lleva máscara ni área |
| `passive-interface GigabitEthernet0/0` | Igual que en OSPF |
| `timers basic 5 15 30` | hellos cada 5 s, inválido a los 15 s, flush a los 30 s (no obligatorio) |

> `no auto-summary` es el error clásico: RIP v2 con autosummary ignora los límites
> de subred y manda la red completa, y las rutas dejan de coincidir con el VLSM.

---

## 8. Verificación

| Comando | Qué muestra | Lo esperado en este lab |
|---------|-------------|------------------------|
| `show ip interface brief` | IP, estado y protocolo de cada interfaz | Las 3 en `up/up` con su IP |
| `show ip dhcp binding` | IPs entregadas a clientes | 3 leases en `.6–.14` (o `.22–.30`, `.38–.46`) |
| `show ip dhcp pool` | Cómo quedó configurado cada pool | Red, gateway y rango del pool |
| `show ip dhcp server statistics` | Estadísticas del servidor DHCP | Paquetes recibidos/enviados |
| `show ip dhcp conflict` | Detecta IPs duplicadas | Vacío |
| `show ip route` | Tabla de enrutamiento completa | `C` conectadas, `S` estáticas (Fase A) u `O` OSPF (Fase B) |
| `show ip route static` | Solo estáticas | Vacío tras activar OSPF |
| `show ip route summary` | Rutas resumidas por prefijo | Un resumen de cada subred |
| `show ip route 192.168.2.32` | ¿Qué ruta se usa para un destino? | La entrada que coincide |
| `show ip arp` | Caché ARP (IP ↔ MAC) | learned de cada PC |
| `show ip protocols` | Qué protocolos de enrutamiento están activos | OSPF y/o RIP |
| `show ip ospf` | Estado general del proceso OSPF | Process ID, router ID |
| `show ip ospf neighbor` | Vecinos y su estado | 2 vecinos en `FULL` |
| `show ip ospf interface brief` | Interfaces dentro de OSPF | Las 3, Gi0/0 como passive |
| `show ip rip database` | Base de datos de RIP | Las redes aprendidas |
| `show running-config` | Configuración activa completa | Para revisar y corregir |
| `show version` | Versión de IOS y modelo | 2911 |
| `copy running-config startup-config` | Guarda la config en NVRAM | Tras cada cambio importante |

### Comandos de prueba

| Comando | Qué hace |
|---------|----------|
| `ping 192.168.2.38` | 5 paquetes de prueba |
| `ping 192.168.2.22 source 192.168.2.1` | Ping **con IP de origen** forzada: prueba la ruta de retorno |
| `traceroute 192.168.2.38` | Muestra el camino salto a salto |

> `ping` con `source` es el comando más útil del lab: si el ping normal falla
> pero con `source` funciona, el problema es la **ruta de vuelta**, no la de ida.

---

## 9. Diagnóstico

| Comando | Para qué |
|---------|----------|
| `clear ip arp` | Vaciar la caché ARP cuando una IP cambia de dueño |
| `debug ip dhcp` | Ver el DORA en vivo mientras el PC pide dirección |
| `copy running-config startup-config` | Guardar antes de experimenting, para poder volver |

---

## 10. Lo que Packet Tracer NO soporta

| Comando | En IOS real | En PT 9.0.1 |
|---------|-------------|--------------|
| `lease 1` | ✅ Sí (duración del alquiler) | ❌ No existe → `% Invalid input detected` |
| `dns-server 8.8.8.8 1.1.1.1` | ✅ Sí (dos DNS) | ❌ Solo un IP |
| `ip helper-address` | ✅ Sí (servir LAN remota) | ❌ No está implementado |

Los tres están comentados o evitados en los CLI. Para ver qué acepta tu router:

```
R1(config-dhcp-pool)#?
```

---

## 11. Comandos del PC

En `Desktop → Command Prompt` de cada PC:

| Comando | Qué hace |
|---------|----------|
| `ipconfig /all` | Muestra IP, máscara, gateway y DNS completos |
| `ipconfig /release` | Devuelve la IP (equipo queda sin dirección) |
| `ipconfig /renew` | **Pide una IP al servidor DHCP** (dispara el DORA) |
| `ping 192.168.2.1` | Prueba el gateway primero |
| `tracert 192.168.2.38` | Camino hasta otra LAN |
| `arp -a` | Vecinos aprendidos por ARP |

> Un PC en `169.254.x.x` significa que **no hubo respuesta DHCP**. El siguiente
> paso es `ipconfig /renew` y, si sigue igual, revisar `show ip dhcp binding` en
> el router: si está vacío, el problema es de cableado o de pool.

---

## Ver también

- [`README.md`](README.md) — índice del laboratorio.
- [`SESION-A.md`](SESION-A.md) — topología, DHCP y rutas estáticas.
- [`SESION-B.md`](SESION-B.md) — OSPF, RIPv2 y diagnóstico.
- [`SUBNETEO.md`](SUBNETEO.md) — el cálculo de las máscaras.
- [`config/`](config/) — los tres CLI completos y listos para pegar.
