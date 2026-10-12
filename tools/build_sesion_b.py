"""Guía de la Sesión B — Laboratorio independiente: sede central, sucursales, VLANs y OSPF · 150 min.

Genera Sesion-B.pptx con el mismo sistema de diseño que Teoria-Lab-VLSM-DHCP
(ppt_kit: 16:9, navy 1F3864 + naranja E87C1E, Calibri + Consolas).

La Sesión B ya NO continúa la Sesión A: es un laboratorio autónomo que parte de
equipos de fábrica y construye una red corporativa completa con topología
hub-and-spoke (sede central R1 + sucursales R2 y R3), VLAN 10/20 con
router-on-a-stick, DHCP por VLAN y OSPF área 0 como único protocolo (sin fase de
rutas estáticas). RIPv2 queda como alternativa de comparación.

Se regenera con:  python3 tools/build_sesion_b.py Sesion-B.pptx
El layout se verifica con:  python3 tools/check_layout.py Sesion-B.pptx
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from ppt_kit import *  # noqa

PART = "Sesión B · Red corporativa con OSPF (lab independiente)"
MIN = "150 min"


def build(out):
    prs = new_deck()
    n = 0

    # ================================================================ 1 portada
    s = cover(prs, "UNIVERSIDAD TECNOLÓGICA DE PANAMÁ · FACULTAD DE INGENIERÍA DE SISTEMAS COMPUTACIONALES",
              "Sesión B — Red corporativa con OSPF",
              "Sede central + 2 sucursales · VLANs · DHCP por VLAN · laboratorio independiente",
              ["Hub-and-spoke: la sede central R1 y las sucursales R2 y R3",
               "VLAN 10 (usuarios) y VLAN 20 (invitados) con router-on-a-stick",
               "OSPF área 0 directo, costes primario/respaldo y prueba de redundancia"],
              "Práctica · laboratorio independiente (no requiere la Sesión A)", "150 min de laboratorio")
    notes(s, "⏱ 0-3 min · Apertura.\n\n"
             "Esta sesión NO depende de la Sesión A: se parte de equipos de fábrica y\n"
             "se construye una red completa nueva. Escenario: una sede central (R1) y\n"
             "dos sucursales (R2 y R3), cada sitio partido en VLAN 10 (usuarios) y\n"
             "VLAN 20 (invitados), con DHCP por VLAN y OSPF área 0 como único\n"
             "protocolo (no hay rutas estáticas).\n"
             "\n"
             "Idea de arranque: en una red real las sedes no se conectan escribiendo\n"
             "rutas a mano; descubren los caminos solas. Hoy demostramos que la red\n"
             "sobrevive a la caída de un enlace sin que nadie toque nada.")

    # ================================================================ 2 mapa
    n += 1
    s = content(prs, "Qué vamos a ver", "Seis partes: del escenario al diagnóstico de una red independiente", PART, n + 1)
    table(s, [["#", "Parte", "Qué haces", "Min"],
              ["1", "Escenario y topología", "Roles central/sucursales, 15 cables, reset de fábrica", "10"],
              ["2", "Direccionamiento", "El plan VLSM de referencia (tabla dada)", "5"],
              ["3", "VLAN y DHCP", "VLAN 10/20 en switches, subinterfaces y pool por VLAN", "30"],
              ["4", "OSPF área 0", "Enrutamiento dinámico directo, costes y redundancia", "40"],
              ["5", "RIPv2 (alternativa)", "Comparar con OSPF en la misma topología", "10"],
              ["6", "Verificación y diagnóstico", "Checklist final y los 8 errores típicos", "30"],
              ["—", "Preguntas", "Reflexión y entregable de la sesión", "25"]],
          0.45, 1.40, 12.4, col_w=[0.7, 3.5, 7.4, 0.8], size=12.5, row_h=0.40)
    callout(s, 0.45, 4.80, 12.4, 1.85, "La regla de la sesión", [
        "**Nada se hereda, todo se construye aquí.** Si algo falla, se diagnostica por capas desde el cable.",
        "Cada parte depende de la anterior: sin el trunk y la subinterfaz no hay VLAN 20; sin la subinterfaz no hay pool; sin OSPF no hay redundancia.",
        "Al terminar debes poder demostrar que **la red sobrevive a la caída de un uplink**."], ORANGE, 12.5)
    notes(s, "⏱ 3-4 min · Mapa de la sesión.\n\n"
             "Enmarca el orden: primero se monta y se segmenta con VLANs, después se\n"
             "vuelve dinámico el enrutamiento con OSPF, y al final se aprende a\n"
             "diagnosticar.\n"
             "\n"
             "A diferencia de la Sesión A, aquí no hay fase estática: OSPF se\n"
             "configura directamente y el contraste con las estáticas es solo teoría.")

    # ================================================================ DIV 1
    s = divider(prs, "1", "Escenario y topología", "Una sede central y dos sucursales, montado desde cero",
                ["R1 sede central · R2 sucursal 1 · R3 sucursal 2, con uplinks a la central",
                 "Un enlace de respaldo entre sucursales para la redundancia",
                 "Cablear los 15 cables y empezar con equipos de fábrica",
                 "Nada que ver con la parte A: no se hereda configuración"], "10 min")
    notes(s, "⏱ 4-5 min · Transición.\n\n"
             "Primera parte corta. La clave: la topología cambia. Ya no hay tres sedes\n"
             "equivalentes en malla: ahora hay una central y dos sucursales, y el\n"
             "enlace entre sucursales existe solo como respaldo.\n"
             "\n"
             "Esto es lo que hace que OSPF tenga sentido: hay más de un camino y la\n"
             "red debe elegir y re-elegir.")

    # ================================================================ 1.1 escenario
    n += 1
    s = content(prs, "La red: una central y dos sucursales", "Cada sitio tiene usuarios (VLAN 10) e invitados (VLAN 20)", PART, n + 1)
    table(s, [["Router", "Rol", "VLAN 10 · GW", "VLAN 20 · GW"],
              ["R1", "Sede central", ".1/28", ".65/28"],
              ["R2", "Sucursal 1", ".17/28", ".81/28"],
              ["R3", "Sucursal 2", ".33/28", ".97/28"]],
          0.45, 1.30, 6.1, col_w=[1.0, 2.0, 1.55, 1.55], size=12, row_h=0.44)
    table(s, [["Enlace", "Subred", "Extremos"],
              ["Uplink SUC-1", "192.168.2.48/30", "R1 .49 ↔ R2 .50"],
              ["Respaldo R2–R3", "192.168.2.52/30", "R2 .53 ↔ R3 .54"],
              ["Uplink SUC-2", "192.168.2.56/30", "R3 .57 ↔ R1 .58"]],
          6.75, 1.30, 6.15, col_w=[1.7, 1.9, 2.55], size=11.5, row_h=0.40)
    callout(s, 0.45, 3.60, 6.1, 2.10, "Hub-and-spoke", [
        "Las sucursales hablan con el mundo **a través de R1**.",
        "Es el camino normal (bajo costo).",
        "Más realista que tres sedes iguales: hay una central."], BLUE, 12)
    callout(s, 6.75, 3.60, 6.15, 2.10, "El enlace R2–R3 es el respaldo", [
        "Su costo se sube (Parte 4) para que no compita con los uplinks.",
        "Solo se usa si cae un uplink de una sucursal.",
        "Es ahí donde se demuestra la redundancia OSPF."], ORANGE, 12)
    callout(s, 0.45, 5.85, 12.4, 1.10, "Cada PC de la tabla anterior sigue igual: PC-A/B/C con 2 en VLAN 10 y 1 en VLAN 20.",
            [], NAVY, 12.5)
    notes(s, "⏱ 5-8 min.\n\n"
             "Recorre la tabla de routers: cada sitio conserva su subred /28 de\n"
             "usuarios y suma otra /28 para invitados.\n"
             "\n"
             "El cambio conceptual: R2 y R3 suben a R1 (hub-and-spoke), y el enlace\n"
             "R2-R3 queda como camino de emergencia. Ahí está la gracia de OSPF:\n"
             "sin él, ese enlace de respaldo sería cable de adorno.")

    # ================================================================ 1.2 cableado
    n += 1
    s = content(prs, "Montar la topología desde cero", "15 cables y equipos de fábrica: esto es un lab independiente", PART, n + 1)
    table(s, [["Tramo", "Cables", "Qué conecta"],
              ["Gateway → switch", "3", "R1 Gi0/0 → SW1 Fa0/1, y análogo en R2, R3"],
              ["PC → switch", "9", "3 PCs por sitio (Fa0/2, Fa0/3, Fa0/4)"],
              ["Router → router", "3", ".48/30, .52/30 y .56/30 (directo, sin switch)"]],
          0.45, 1.32, 12.4, col_w=[2.6, 1.0, 8.8], size=12, row_h=0.42)
    callout(s, 0.45, 3.30, 6.1, 1.80, "Empezar de fábrica", [
        "Routers: `erase startup-config` + `reload` (responde yes).",
        "Switches 2960 y PCs: sin configuración por defecto.",
        "Las interfaces Gi nacen apagadas (rojas): es normal."], RED, 12)
    callout(s, 6.75, 3.30, 6.15, 1.80, "Comprobar el cableado", [
        "Cada router tiene sus 3 cables (Gi0/0, Gi0/1, Gi0/2).",
        "Cada switch tiene 4: Fa0/1 (router) y Fa0/2-4 (PCs).",
        "Los cables se ponen en verde recién en la Parte 3."], TEAL, 12)
    callout(s, 0.45, 5.30, 12.4, 1.60, "Los cables entre routers no pasan por ningún switch", [
        "Son enlaces de capa 2 punto a punto con su propia subred /30.",
        "Los tres juntos son el corazón de la topología: dos caminos desde cada sucursal hacia la central."], NAVY, 12.5)
    notes(s, "⏱ 8-12 min.\n\n"
             "Insistir en el reset: es lo que hace que el laboratorio sea\n"
             "independiente. Si no borran la config de un router usado antes, se\n"
             "arrastran IPs y rutas viejas.\n"
             "\n"
             "Los 15 cables son los mismos números de siempre, pero la narrativa\n"
             "cambió: dos de los tres enlaces entre routers son uplinks a la central\n"
             "y el tercero es un respaldo.")

    # ================================================================ DIV 2
    s = divider(prs, "2", "Direccionamiento", "El plan VLSM de referencia (ya calculado)",
                ["La tabla de 9 subredes está dada: se copia, no se recalcula",
                 "VLAN 10 y VLAN 20 por sitio: dos /28 por router",
                 "Tres /30 para los enlaces: .48, .52 y .56",
                 "Cualquier IP que escribas debe caer en su rango"], "5 min")
    notes(s, "⏱ 12-13 min · Transición.\n\n"
             "El cálculo completo está en SUBNETEO.md. Aquí solo se entrega la tabla\n"
             "para trabajar rápido y sin equivocarse.\n"
             "\n"
             "Única novedad frente a otros labs: las VLAN 20 usan las subredes .64,\n"
             ".80 y .96, que encajan justo después de los tres enlaces /30.")

    # ================================================================ 2.1 vlsm
    n += 1
    s = content(prs, "Plan VLSM de referencia", "9 subredes sobre 192.168.2.0/24 · se toma tal cual", PART, n + 1)
    table(s, [["Subred", "Red", "Rango útil", "Uso"],
              ["192.168.2.0/28", ".0", ".1 – .14", "Central · VLAN 10 · GW .1"],
              ["192.168.2.16/28", ".16", ".17 – .30", "SUC-1 · VLAN 10 · GW .17"],
              ["192.168.2.32/28", ".32", ".33 – .46", "SUC-2 · VLAN 10 · GW .33"],
              ["192.168.2.48/30", ".48", ".49 – .50", "Uplink SUC-1 (R1–R2)"],
              ["192.168.2.52/30", ".52", ".53 – .54", "Respaldo (R2–R3)"],
              ["192.168.2.56/30", ".56", ".57 – .58", "Uplink SUC-2 (R3–R1)"],
              ["192.168.2.64/28", ".64", ".65 – .78", "Central · VLAN 20 · GW .65"],
              ["192.168.2.80/28", ".80", ".81 – .94", "SUC-1 · VLAN 20 · GW .81"],
              ["192.168.2.96/28", ".96", ".97 – .110", "SUC-2 · VLAN 20 · GW .97"]],
          0.45, 1.32, 12.4, col_w=[2.2, 1.0, 1.7, 7.5], size=11.5, row_h=0.35)
    callout(s, 0.45, 5.15, 12.4, 1.65, "Verificación rápida de cualquier IP", [
        "Un /28 empieza en múltiplo de 16 (0, 16, 32, 64, 80, 96) y un /30 en múltiplo de 4 (48, 52, 56).",
        "Los enlaces /30 ocupan de .48 a .59; las VLAN 20 saltan a .64 en adelante.",
        "De .112 a .255 queda reservado para crecer."], GREEN, 12.5)
    notes(s, "⏱ 13-18 min.\n\n"
             "Recorrer la tabla por bloques: los seis /28 (tres de usuarios, tres de\n"
             "invitados) y los tres /30 de enlaces.\n"
             "\n"
             "Subrayar la regla de los múltiplos: es la que permite darse cuenta si\n"
             "una IP está mal antes de configurarla.\n"
             "\n"
             "Dejar claro que el cálculo está documentado en SUBNETEO.md para quien\n"
             "quiera entenderlo.")

    # ================================================================ DIV 3
    s = divider(prs, "3", "VLAN y DHCP", "Segmentar cada sede y servir dos VLANs con un solo cable",
                ["Switches: crear VLAN 10 y 20, puertos access y un trunk",
                 "La trampa del native: si no se fija, el gateway queda en la VLAN 1",
                 "Router-on-a-stick: subinterfaz .20 con encapsulation dot1Q",
                 "Un pool DHCP por VLAN y la verificación con pings"], "30 min")
    notes(s, "⏱ 18-19 min · Transición.\n\n"
             "Hasta aquí solo topología e IPs. Ahora cada sede deja de ser una LAN\n"
             "plana y se parte en dos dominios de broadcast.\n"
             "\n"
             "Todo lo de esta parte es nuevo para esta sesión (no viene de la A):\n"
             "VLANs, trunk, subinterfaces y el segundo pool.")

    # ================================================================ 3.1 switches
    n += 1
    s = content(prs, "Switches: VLAN 10 y 20", "Primero se crea la VLAN, después se asigna el puerto", PART, n + 1)
    code(s, 0.45, 1.32, 7.4, 3.30,
         [("SW1(config)# vlan 10", ORANGE),
          ("SW1(config-vlan)# name USUARIOS-CENTRAL", GRAY),
          ("SW1(config-vlan)# vlan 20", ORANGE),
          ("SW1(config-vlan)# name INVITADOS-CENTRAL", GRAY),
          ("SW1(config)# interface Fa0/2        ! PC-A1", GRAY),
          ("SW1(config-if)# switchport mode access", GRAY),
          ("SW1(config-if)# switchport access vlan 10", GRAY),
          ("SW1(config-if)# interface Fa0/4     ! PC-A3 (invitados)", GRAY),
          ("SW1(config-if)# switchport access vlan 20", GRAY),
          ("SW1(config-if)# interface Fa0/1     ! hacia R1", ORANGE),
          ("SW1(config-if)# switchport mode trunk", GRAY),
          ("SW1(config-if)# switchport trunk native vlan 10", ORANGE),
          ("SW1(config-if)# switchport trunk allowed vlan 10,20", GRAY)], 10)
    callout(s, 8.05, 1.32, 4.85, 1.50, "Access vs trunk", [
        "**access**: un puerto, un VLAN (un PC).",
        "**trunk**: lleva las 2 VLAN etiquetadas (hacia el router)."], TEAL, 11.5)
    callout(s, 8.05, 2.98, 4.85, 1.64, "Dos dominios de broadcast", [
        "PC-A1 y PC-A2 se ven entre sí (VLAN 10).",
        "PC-A3 ya no los ve (VLAN 20): ese aislamiento es el objetivo.",
        "Fa0/2 y Fa0/3 en VLAN 10 · Fa0/4 en VLAN 20."], ORANGE, 11.5)
    callout(s, 0.45, 4.80, 12.4, 2.05, "La trampa del native VLAN", [
        "Por defecto, la **native** de un trunk es la **VLAN 1** y viaja **sin etiqueta**.",
        "La IP de `Gi0/0` del router llega sin etiqueta: con el native por defecto cae en la VLAN 1, en una subred que no existe.",
        "Se fija `switchport trunk native vlan 10`: así la VLAN 10 viaja sin etiqueta y coincide con el gateway.",
        "Comprobación: `show interfaces trunk` debe ver `Native vlan 10` y `allowed 10,20`."], RED, 12)
    text(s, 0.45, 6.90, 12.4, 0.3, "En SW2 y SW3 es idéntico, con nombres SUC1/SUC2.", size=12)
    notes(s, "⏱ 19-25 min.\n\n"
             "La mitad del tiempo de VLANs va en la trampa del native: es el fallo\n"
             "que más confunde. Si el ping al gateway de la VLAN 10 falla justo\n"
             "después de crear el trunk, es aquí.\n"
             "\n"
             "Analogía útil: la native es el 'carril sin etiqueta' del trunk. Si los\n"
             "extremos no acuerdan cuál es, el tráfico acaba en el carril equivocado.\n"
             "\n"
             "Recordar: VLAN 10 sin etiqueta (gateway en Gi0/0), VLAN 20 etiquetada\n"
             "(gateway en Gi0/0.20).")

    # ================================================================ 3.2 subinterfaces
    n += 1
    s = content(prs, "Router-on-a-stick: dos gateways en un cable", "La física para la VLAN 10, la subinterfaz para la 20", PART, n + 1)
    code(s, 0.45, 1.35, 7.4, 2.70,
         [("R1(config)# interface GigabitEthernet0/0", ORANGE),
          ("R1(config-if)# ip address 192.168.2.1 255.255.255.240", GRAY),
          ("R1(config-if)# no shutdown", GRAY),
          ("R1(config-if)# interface GigabitEthernet0/0.20", ORANGE),
          ("R1(config-subif)# encapsulation dot1Q 20", GRAY),
          ("R1(config-subif)# ip address 192.168.2.65 255.255.255.240", GRAY),
          ("R1(config-subif)# no shutdown", GRAY)], 10.5)
    table(s, [["Interfaz", "VLAN", "IP / máscara", "Etiqueta"],
              ["Gi0/0", "10", "192.168.2.1/28", "sin etiqueta"],
              ["Gi0/0.20", "20", "192.168.2.65/28", "802.1Q 20"]],
          8.05, 1.35, 4.85, col_w=[1.1, 0.7, 1.85, 1.2], size=10.5, row_h=0.42)
    callout(s, 8.05, 3.05, 4.85, 1.20, "Una interfaz, dos mundos", [
        "La física enciende todas las subinterfaces.",
        "Cada subinterfaz es el gateway de una VLAN."], TEAL, 11)
    callout(s, 0.45, 4.25, 12.4, 1.35, "El router enruta entre las dos VLAN de su sitio", [
        "Un `ping` de PC-A3 a PC-A1 sale por `Gi0/0.20` (VLAN 20) y vuelve por `Gi0/0` (VLAN 10).",
        "Enrutamiento de capa 3 sobre un solo cable físico: eso es **router-on-a-stick**."], ORANGE, 12.5)
    callout(s, 0.45, 5.75, 12.4, 1.20, "No olvides los uplinks", [
        "Cada router configura además sus dos enlaces /30 (Parte 2): R1 Gi0/1=.49 y Gi0/2=.58; R2 .50/.53; R3 .54/.57."], NAVY, 12.5)
    notes(s, "⏱ 25-30 min.\n\n"
             "El concepto clave: una interfaz física soporta subinterfaces lógicas,\n"
             "cada una con su VLAN y su IP.\n"
             "\n"
             "El `encapsulation dot1Q 20` es lo que hace que la subinterfaz entienda\n"
             "el tráfico etiquetado de la VLAN 20.\n"
             "\n"
             "En R2 y R3 es idéntico: siempre `Gi0/0.20`, con sus IPs (.81 y .97).")

    # ================================================================ 3.3 dhcp
    n += 1
    s = content(prs, "DHCP por VLAN", "Cada VLAN es una subred: necesita su propio pool", PART, n + 1)
    code(s, 0.45, 1.35, 7.4, 2.80,
         [("R1(config)# ip dhcp excluded-address 192.168.2.65 192.168.2.69", ORANGE),
          ("R1(config)# ip dhcp pool VLAN20-CENTRAL", ORANGE),
          ("R1(dhcp-config)# network 192.168.2.64 255.255.255.240", GRAY),
          ("R1(dhcp-config)# default-router 192.168.2.65", GRAY),
          ("R1(dhcp-config)# dns-server 8.8.8.8", GRAY),
          ("R1(dhcp-config)# domain-name lab-utp.pa", GRAY), ], 10.5)
    table(s, [["Sitio", "Gateway", "Pool VLAN 20", "Rango DHCP"],
              ["Central", ".65", "VLAN20-CENTRAL", ".70 – .78"],
              ["SUC-1", ".81", "VLAN20-SUC1", ".86 – .94"],
              ["SUC-2", ".97", "VLAN20-SUC2", ".102 – .110"]],
          8.05, 1.35, 4.85, col_w=[0.9, 1.1, 1.55, 1.3], size=10, row_h=0.44)
    callout(s, 8.05, 3.20, 4.85, 1.55, "Mismo patrón que la VLAN 10", [
        "Se excluye el gateway de la VLAN 20 y 4 IPs fijas.",
        "Cada router termina con **2 pools**."], TEAL, 11)
    callout(s, 0.45, 4.30, 12.4, 1.35, "Dos pools por router, no uno", [
        "VLAN 10 usa `LAN-CENTRAL` (red .0/28, gateway .1); la VLAN 20 usa `VLAN20-CENTRAL` (red .64/28, gateway .65).",
        "`show ip dhcp pool` debe listar dos pools; `show ip dhcp binding` reparte leases entre ambos."], ORANGE, 12.5)
    callout(s, 0.45, 5.75, 12.4, 1.25, "Recordatorio de Packet Tracer 9.0.1", [
        "`lease` no existe en el 2911 (el alquiler por defecto es 1 día) y `dns-server` acepta una sola IP.",
        "En los 9 PCs: `ipconfig /renew` y comprobar IP del rango + máscara /28 + gateway de SU VLAN."], NAVY, 12.5)
    notes(s, "⏱ 30-35 min.\n\n"
             "El punto que sorprende: el mismo router atiende dos subredes porque\n"
             "ahora tiene dos IP (la física y la subinterfaz).\n"
             "\n"
             "Verificación tipo: `show ip dhcp pool`, `show ip dhcp binding` y\n"
             "`ipconfig /all` de un PC de cada VLAN. Los tres campos críticos: IP en\n"
             "rango, máscara /28, gateway correcto.")

    # ================================================================ 3.4 verificación VLAN
    n += 1
    s = content(prs, "Verificar: los pings que lo demuestran", "Aquí se ve el enrutamiento entre VLANs en acción", PART, n + 1)
    code(s, 0.45, 1.35, 7.4, 2.30,
         [("SW1# show vlan brief", ORANGE),
          ("SW1# show interfaces trunk   ! native 10, allowed 10,20", GRAY),
          ("R1#  show ip interface brief ! Gi0/0 y Gi0/0.20 con IP", ORANGE),
          ("R1#  show ip dhcp binding    ! leases de los 2 pools", GRAY)], 11)
    table(s, [["Prueba", "Resultado"],
              ["PC-A3 ping .1 (gateway VLAN 20)", "OK"],
              ["PC-A3 ping .6 (VLAN 10)", "Falla (a propósito)"],
              ["PC-A1 ping .70 (VLAN 20)", "OK · R1 enruta"]],
          8.05, 1.35, 4.85, col_w=[3.05, 1.8], size=10.5, row_h=0.52)
    callout(s, 0.45, 3.90, 6.1, 1.60, "¿Por qué el segundo falla?", [
        "PC-A3 (VLAN 20) y PC-A1 (VLAN 10) están en subredes distintas.",
        "Sin el router no se alcanzan: es el aislamiento deseado."], RED, 12)
    callout(s, 6.75, 3.90, 6.15, 1.60, "¿Por qué el tercero funciona?", [
        "PC-A1 sale por su gateway (.1) y R1 reenvía por Gi0/0.20 hacia .70.",
        "Router-on-a-stick: capa 3 sobre un solo cable."], GREEN, 12)
    callout(s, 0.45, 5.65, 12.4, 1.30, "Primer vistazo a la tabla", [
        "Estos pings solo funcionan dentro de cada sede. Para cruzar entre sedes falta OSPF (Parte 4).",
        "Guiño: `show ip route` hoy solo muestra conectadas; en la Parte 4 aparecen las `O`."], NAVY, 12.5)
    notes(s, "⏱ 35-40 min.\n\n"
             "Tres pings que cuentan la historia de la segmentación por sedes.\n"
             "\n"
             "Ojo con la asimetría: PC-A3 → PC-A1 falla (el PC no tiene ruta a otra\n"
             "VLAN), pero PC-A1 → PC-A3 funciona porque el router sí enruta. Que el\n"
             "grupo explique eso.\n"
             "\n"
             "Si el ping al gateway de la VLAN 20 falla, revisar `encapsulation` y el\n"
             "`native vlan` del trunk.")

    # ================================================================ DIV 4
    s = divider(prs, "4", "OSPF área 0", "Enrutamiento dinámico directo: ni una sola ruta estática",
                ["Por qué OSPF y no mantener estáticas en la topología",
                 "Anatomía del comando: proceso, network, área y passive",
                 "Costes: uplink primario frente a respaldo (ip ospf cost 100)",
                 "Vecinos FULL, rutas O [110/2] y la prueba de redundancia"], "40 min")
    notes(s, "⏱ 40-41 min · Transición.\n\n"
             "Aquí empieza lo dinámico. A diferencia de la Sesión A, no hay fase\n"
             "estática previa: OSPF se configura directo y la red aprende sola.\n"
             "\n"
             "Pregunta de apertura: si R1 no tuviera ruta a la LAN de SUC-1, ¿qué\n"
             "haría con un paquete para esa red? Lo descartaría. OSPF evita tener\n"
             "que escribírsela.")

    # ================================================================ 4.1 por qué OSPF
    n += 1
    s = content(prs, "Por qué OSPF y no estáticas", "Cuatro ventajas que se notan en esta topología", PART, n + 1)
    table(s, [["Ventaja", "Explicación"],
              ["Automático", "No hay que escribir rutas cuando se añade un sitio"],
              ["Detección de caídas", "Los hellos detectan un enlace caído en segundos"],
              ["Mejor ruta", "Elige por costo (métrica), no por lo que se escribió"],
              ["Redundancia real", "Con el enlace R2–R3 de respaldo, recalcula solo"]],
          0.45, 1.35, 12.4, col_w=[3.4, 9.0], size=12.5, row_h=0.46)
    callout(s, 0.45, 3.65, 6.1, 1.65, "Qué pasaría con una estática", [
        "La ruta estática apuntaría al uplink de cada sucursal.",
        "Si cae ese uplink, el estático no se entera y el paquete se descarta.",
        "La red se parte en dos hasta que alguien la corrija."], RED, 12)
    callout(s, 6.75, 3.65, 6.15, 1.65, "Qué pasa con OSPF", [
        "Si cae el uplink de SUC-1, OSPF usa el respaldo R2→R3→R1.",
        "En minutos (o segundos) la red vuelve a estar completa.",
        "Ese es el contrato de este laboratorio."], GREEN, 12)
    callout(s, 0.45, 5.45, 12.4, 1.45, "¿Y las estáticas en la Sesión A?", [
        "La Sesión A las usa como base pedagógica. Esta sesión es independiente: OSPF desde el inicio.",
        "La distancia administrativa (estática 1, OSPF 110) se comenta en la teoría, aquí no hay conflicto porque no hay estáticas."], NAVY, 12.5)
    notes(s, "⏱ 41-45 min.\n\n"
             "Contraste directo: sin OSPF el enlace R2-R3 es inútil; con OSPF es\n"
             "seguro de vida de la red.\n"
             "\n"
             "Subrayar que aquí no hay que 'quitar estáticas': nunca se pusieron.\n"
             "La ventaja es aprender OSPF sobre una red limpia, sin tener que\n"
             "deshacer la Fase A de otro lab.")

    # ================================================================ 4.2 anatomía
    n += 1
    s = content(prs, "Anatomía del comando OSPF", "Tres piezas: proceso, red y área (más passive)", PART, n + 1)
    code(s, 0.45, 1.35, 7.4, 2.60,
         [("R1(config)# router ospf 10", ORANGE),
          ("R1(config-router)# router-id 192.168.2.1", GRAY),
          ("R1(config-router)# network 192.168.2.0 0.0.0.255 area 0", GRAY),
          ("R1(config-router)# passive-interface GigabitEthernet0/0", GRAY),
          ("R1(config-router)# passive-interface GigabitEthernet0/0.20", GRAY)], 11)
    callout(s, 8.05, 1.35, 4.85, 1.25, "El 10 no es el área", [
        "`router ospf 10` es un número local del proceso.",
        "El área debe ser **0** en los tres."], ORANGE, 11.5)
    callout(s, 8.05, 2.75, 4.85, 1.25, "Wildcard = máscara invertida", [
        "`0.0.0.255` es la inversa de /24.",
        "Una línea cubre las 9 subredes."], TEAL, 11.5)
    callout(s, 0.45, 4.15, 6.1, 1.60, "Qué anuncia `network`", [
        "Toda interfaz dentro de 192.168.2.x entra en OSPF.",
        "Incluye las subinterfaces: la VLAN 20 se anuncia sola.",
        "No hay que tocar OSPF al añadir VLANs."], GREEN, 12)
    callout(s, 6.75, 4.15, 6.15, 1.60, "`passive-interface` en las LAN", [
        "En Gi0/0 y Gi0/0.20 no hay vecinos OSPF: solo PCs.",
        "La red se anuncia, pero no se envían hellos.",
        "**Nunca** passive en gi0/1 ni gi0/2 (los enlaces)."], NAVY, 12)
    callout(s, 0.45, 5.95, 12.4, 1.00, "Router-id fijo: R1=.1, R2=.17, R3=.33. Without él cada router elige la IP más alta y el lab no coincide.",
            [], TEAL, 12.5)
    notes(s, "⏱ 45-52 min.\n\n"
             "Desglosar el comando en sus piezas. El `router-id` se fija para que los\n"
             "resultados coincidan con el material.\n"
             "\n"
             "El wildcard es la confusión clásica: es la máscara invertida, no la\n"
             "máscara. /24 → 0.0.0.255.\n"
             "\n"
             "Passive en las dos LAN de cada router: la red se anuncia igual, pero no\n"
             "se gastan hellos con PCs.")

    # ================================================================ 4.3 costes
    n += 1
    s = content(prs, "Costes: uplink primario y respaldo", "`ip ospf cost 100` en el enlace R2–R3 hace que solo sea de emergencia", PART, n + 1)
    code(s, 0.45, 1.35, 7.4, 2.35,
         [("R2(config)# interface GigabitEthernet0/2", ORANGE),
          ("R2(config-if)# ip ospf cost 100    ! hacia R3 (respaldo)", GRAY),
          ("R3(config)# interface GigabitEthernet0/1", ORANGE),
          ("R3(config-if)# ip ospf cost 100    ! hacia R2 (respaldo)", GRAY)], 11)
    table(s, [["Desde R2…", "Camino", "Costo"],
              ["a la central", "R2→R1 (uplink)", "1 + 1 = 2"],
              ["a la central", "R2→R3→R1 (respaldo)", "100+1+1 = 102"],
              ["a SUC-2", "R2→R1→R3 (por central)", "1+1+1 = 3"],
              ["a SUC-2", "R2→R3 (respaldo)", "100+1 = 101"]],
          8.05, 1.35, 4.85, col_w=[1.5, 2.15, 1.2], size=10, row_h=0.36)
    callout(s, 0.45, 3.90, 6.1, 1.75, "Con Gigabit todo cuesta 1", [
        "OSPF usa costo = referencia / ancho de banda.",
        "Sin ajuste, R2 vería **dos caminos de igual costo** a la central (ECMP).",
        "El costo 100 fuerza primario → respaldo como único orden."], ORANGE, 12)
    callout(s, 6.75, 3.90, 6.15, 1.75, "El efecto hub-and-spoke", [
        "Entre sucursales se prefiere **pasar por la central** (3 < 101).",
        "El enlace R2–R3 queda en modo dormido hasta que un uplink falle.",
        "Si `ip ospf cost` no lo acepta tu PT: `bandwidth 1000` (100000/1000 = 100)."], BLUE, 12)
    callout(s, 0.45, 5.85, 12.4, 1.10, "Los uplinks se dejan con costo 1: comparan entre ellos para elegir el mejor camino hacia la central.",
            [], NAVY, 12.5)
    notes(s, "⏱ 52-60 min.\n\n"
             "Este es el detalle que distingue al laboratorio: sin el costo 100, OSPF\n"
             "haría balanceo ECMP por los dos caminos, y la prueba de redundancia\n"
             "sería menos clara.\n"
             "\n"
             "La tabla de costos se lee en columna: el costo acumulado decide la\n"
             "ruta. El tráfico entre sucursales sale por la central.\n"
             "\n"
             "El comando fallback (`bandwidth 1000`) logra el mismo número.")

    # ================================================================ 4.4 verificación vecinos/tabla
    n += 1
    s = content(prs, "Vecinos FULL y rutas O", "Los dos `show` que prueban que OSPF funciona", PART, n + 1)
    code(s, 0.45, 1.32, 7.4, 2.20,
         [("R1# show ip ospf neighbor", ORANGE),
          ("Neighbor ID     Pri   State   Dead Time   Address      Interface", GRAY),
          ("192.168.2.17      0   FULL/-  00:00:37  192.168.2.50  Gi0/1  SUC-1", GRAY),
          ("192.168.2.33      0   FULL/-  00:00:35  192.168.2.57  Gi0/2  SUC-2", GRAY)], 10)
    callout(s, 8.05, 1.32, 4.85, 1.25, "FULL, no 2-WAY", [
        "FULL = vecindad establecida.",
        "2-WAY / EXSTART = área o red mal."], TEAL, 11.5)
    callout(s, 8.05, 2.75, 4.85, 0.85, "El Pri 0 no es error", [
        "Confirma `Gi0/0` pasiva: sin hellos."], ORANGE, 11)
    code(s, 0.45, 3.70, 7.4, 2.75,
         [("R1# show ip route", ORANGE),
          ("C  192.168.2.0/28   Gi0/0        L 192.168.2.1/32", GRAY),
          ("C  192.168.2.64/28  Gi0/0.20     L 192.168.2.65/32", GRAY),
          ("C  192.168.2.48/30  Gi0/1        L 192.168.2.49/32", GRAY),
          ("C  192.168.2.56/30  Gi0/2        L 192.168.2.58/32", GRAY),
          ("O  192.168.2.16/28 [110/2] via 192.168.2.50", ORANGE),
          ("O  192.168.2.80/28 [110/2] via 192.168.2.50", ORANGE),
          ("O  192.168.2.32/28 [110/2] via 192.168.2.57", ORANGE),
          ("O  192.168.2.96/28 [110/2] via 192.168.2.57", ORANGE)], 9.5)
    callout(s, 8.05, 3.70, 4.85, 1.40, "Lectura de [110/2]", [
        "**110** = distancia administrativa de OSPF.",
        "**2** = costo: 1 del enlace + 1 de la LAN del destino."], NAVY, 11)
    callout(s, 8.05, 5.25, 4.85, 1.20, "Cada router ve 2 vecinos", [
        "R2 y R3 también deben mostrar FULL con los otros dos.",
        "`show ip route 192.168.2.0` en R2 → via R1 (o via R3 si el uplink cae)."], GREEN, 11)
    notes(s, "⏱ 60-68 min.\n\n"
             "Dos capturas obligatorias: vecinos FULL y tabla con rutas O. Son la\n"
             "prueba de que OSPF está enrutando.\n"
             "\n"
             "El [110/2]: 110 es la distancia administrativa y 2 la métrica. Es la\n"
             "duda más frecuente al leer `show ip route`.\n"
             "\n"
             "Probar también `show ip protocols` en R1 para ver el proceso, el\n"
             "router-id y las interfaces pasivas.")

    # ================================================================ 4.5 redundancia
    n += 1
    s = content(prs, "La prueba de redundancia", "Apagar un uplink y ver la red sobrevivir por el respaldo", PART, n + 1)
    flow(s, [("1. shutdown", "R1 Gi0/1\n(uplink SUC-1)"),
             ("2. espera ~40 s", "OSPF detecta\nla caída"),
             ("3. R2 recalcula", "ruta a central\nvia R3 (.54)"),
             ("4. ruta nueva", "[110/102] via\n192.168.2.54"),
             ("5. ping OK", "PC-B1 → .6\npor el respaldo")],
         0.45, 1.40, 12.4, h=1.20, size=11.5)
    callout(s, 0.45, 2.90, 12.4, 1.70, "Qué demuestra", [
        "Con el uplink de la sucursal 1 caído, el tráfico SUC-1 → Central sale por **R2 → R3 → R1** (enlace de respaldo).",
        "El `ping` desde PC-B1 sigue respondiendo y el `tracert` muestra el camino nuevo: `.17 → .54 (R3) → .1 (R1)`.",
        "OSPF recalculó solo: nadie tocó una ruta a mano."], GREEN, 12)
    callout(s, 0.45, 4.75, 6.1, 1.75, "Con rutas estáticas no pasa", [
        "El estático seguiría apuntando al uplink caído.",
        "Sin ruta alternativa, el tráfico se corta hasta que alguien la corrija.",
        "Por eso OSPF: resilencia sin intervención."], RED, 12)
    callout(s, 6.75, 4.75, 6.15, 1.75, "Restaurar el enlace", [
        "`interface Gi0/1` → `no shutdown` en R1.",
        "Esperar la convergencia: la ruta vuelve a `[110/2] via .50`.",
        "Verificar con `show ip route 192.168.2.0` en R2."], TEAL, 12)
    text(s, 0.45, 6.60, 12.4, 0.35, "Usa `tracert` antes y después del shutdown: el camino se ve cambiar.", size=12)
    notes(s, "⏱ 68-75 min.\n\n"
             "Es la prueba estrella y cierra la Parte 4. Hazla en directo si se puede\n"
             "proyectar.\n"
             "\n"
             "Pasos: apagar R1 Gi0/1, esperar los ~40 s de convergencia, comprobar el\n"
             "ping desde PC-B1 y leer `show ip route 192.168.2.0` en R2 (debe decir\n"
             "via .54 con costo 102).\n"
             "\n"
             "No olvides restaurar con `no shutdown` o el resto de la sesión quedará\n"
             "con medio enlace caído.")

    # ================================================================ DIV 5
    s = divider(prs, "5", "RIPv2 (alternativa)", "El otro dinámico, para comparar",
                ["Configurar RIPv2 y por qué `no auto-summary` es obligatorio",
                 "Verificar rutas `R` en la tabla",
                 "Comparar OSPF y RIPv2 en esta misma topología",
                 "Volver a OSPF al terminar la comparación"], "10 min")
    notes(s, "⏱ 75-76 min · Transición.\n\n"
             "Parte opcional: se hace si el profesor la pide o para comparar. RIP no\n"
             "sustituye a OSPF en producción, pero enseña el concepto de vector de\n"
             "distancia.")

    # ================================================================ 5.1 rip
    n += 1
    s = content(prs, "RIPv2: la alternativa", "Más simple de escribir, más frágil con VLSM", PART, n + 1)
    code(s, 0.45, 1.35, 7.4, 2.35,
         [("R1(config)# no router ospf 10", ORANGE),
          ("R1(config)# router rip", ORANGE),
          ("R1(config-router)# version 2", GRAY),
          ("R1(config-router)# no auto-summary", ORANGE),
          ("R1(config-router)# network 192.168.2.0", GRAY)], 11)
    table(s, [["Comando", "Por qué"],
              ["version 2", "RIPv2 envía la máscara (VLSM lo exige)"],
              ["no auto-summary", "Sin esto resume mal las subredes"],
              ["network 192.168.2.0", "Activa RIP en esa red, sin máscara ni área"]],
          8.05, 1.35, 4.85, col_w=[1.85, 3.0], size=10.5, row_h=0.62)
    callout(s, 0.45, 3.90, 12.4, 1.55, "`no auto-summary` no es opcional aquí", [
        "Con VLSM, el resumen automático manda `192.168.2.0/24` en vez de las subredes reales.",
        "El vecino recibe una ruta que no corresponde y descarta la información correcta.",
        "Con `no auto-summary` se difunden las subredes con su máscara real."], RED, 12)
    callout(s, 0.45, 5.60, 12.4, 1.35, "Es solo enrutamiento", [
        "`network 192.168.2.0` le dice a RIP qué interfaces anunciar: el DHCP por VLAN no cambia.",
        "RIPv2 puede tardar 1-3 min en aparecer en Packet Tracer: es normal."], TEAL, 12.5)
    notes(s, "⏱ 76-82 min.\n\n"
             "El `no auto-summary` es el corazón de esta parte: es el error clásico\n"
             "de RIP con VLSM.\n"
             "\n"
             "Recordar apagar OSPF primero (`no router ospf 10`): si corren juntos,\n"
             "compiten y OSPF gana por distancia administrativa.\n"
             "\n"
             "La paciencia es obligatoria: RIP en PT tarda en converger.")

    # ================================================================ 5.2 comparativa
    n += 1
    s = content(prs, "OSPF frente a RIPv2", "Mismo laboratorio, dos maneras de aprender rutas", PART, n + 1)
    table(s, [["Característica", "OSPF (área 0)", "RIPv2"],
              ["Tipo", "estado de enlace", "vector de distancia"],
              ["Distancia administrativa", "110", "120"],
              ["Convergencia", "rápida (segundos, SPF)", "lenta (temporizadores)"],
              ["Métrica", "costo por ancho de banda", "saltos (máx. 15)"],
              ["VLSM", "nativo", "requiere `no auto-summary`"],
              ["Configuración", "más comandos", "más simple"]],
          0.45, 1.35, 12.4, col_w=[3.4, 4.5, 4.5], size=12, row_h=0.46)
    callout(s, 0.45, 5.15, 12.4, 1.75, "Con cuál te quedas", [
        "En este laboratorio, **OSPF**: converge rápido y aprende VLSM sin trucos.",
        "RIPv2 sirve para **comparar** y para ver por qué el resumen automático rompe con subredes.",
        "Mientras corren juntos gana OSPF (110 < 120). Para volver a OSPF: `no router rip` y repetir la Parte 4."], GREEN, 12.5)
    notes(s, "⏱ 82-86 min.\n\n"
             "No hace falta dominar RIP: la idea es comparar y justificar por qué\n"
             "OSPF es el protocolo de producción.\n"
             "\n"
             "La distancia administrativa distinta (110 vs 120) explica por qué se\n"
             "apaga uno cuando se prueba el otro.")

    # ================================================================ DIV 6
    s = divider(prs, "6", "Verificación y diagnóstico", "El checklist final y los 8 errores que te vas a encontrar",
                ["Checklist de 10 comprobaciones con su resultado esperado",
                 "Los 8 errores típicos: síntoma, causa y solución",
                 "El método por capas y el comando de rescate",
                 "Preguntas de reflexión y entregable"], "30 min")
    notes(s, "⏱ 86-87 min · Transición.\n\n"
             "Última parte: comprobar y saber arreglar. El checklist es el mismo que\n"
             "se entrega; los 8 errores cubren el 90 % de lo que sale mal.")

    # ================================================================ 6.1 checklist
    n += 1
    s = content(prs, "Checklist final de la Sesión B", "Cada comando responde una pregunta", PART, n + 1)
    table(s, [["#", "Comando", "Dónde", "Resultado esperado"],
              ["1", "show ip interface brief", "R1, R2, R3", "Gi0/0 y Gi0/0.20 up/up con IP"],
              ["2", "show vlan brief", "SW1, SW2, SW3", "VLAN 10 y 20; Fa0/4 en la 20"],
              ["3", "show interfaces trunk", "SW1, SW2, SW3", "Fa0/1 troncal, native 10, allowed 10,20"],
              ["4", "show ip dhcp pool", "R1, R2, R3", "2 pools por router"],
              ["5", "show ip dhcp binding", "R1, R2, R3", "2 leases VLAN 10 + 1 de VLAN 20"],
              ["6", "ipconfig /all", "1 PC de cada VLAN", "IP del pool + máscara /28 + gateway correcto"],
              ["7", "show ip route", "R1, R2, R3", "rutas O (o R) y sin S"],
              ["8", "show ip ospf neighbor", "R1, R2, R3", "2 vecinos en FULL"],
              ["9", "show ip route 192.168.2.0", "R2", "via R1 normal; via R3 con uplink caído"],
              ["10", "shutdown R1 Gi0/1", "R1", "ping PC-B1 sigue OK (redundancia)"]],
          0.45, 1.32, 12.4, col_w=[0.6, 3.6, 2.4, 5.8], size=11, row_h=0.37)
    callout(s, 0.45, 5.65, 12.4, 1.25, "El orden importa", [
        "No puede haber lease de la VLAN 20 (paso 5) sin la subinterfaz y el pool (Parte 3).",
        "Y no puede haber vecinos FULL (paso 8) si un enlace está caído o mal configurado."], NAVY, 12.5)
    notes(s, "⏱ 87-92 min.\n\n"
             "Usa el checklist como índice del entregable: cada fila es una captura\n"
             "de pantalla.\n"
             "\n"
             "Los pasos 5 y 9 son los que más se olvidan. El 10 cierra la demostración\n"
             "de redundancia de la Parte 4.")

    # ================================================================ 6.2 errores
    n += 1
    s = content(prs, "Los 8 errores típicos", "Reconocerlos por el síntoma es más rápido que depurar", PART, n + 1)
    table(s, [["Síntoma", "Causa probable", "Solución"],
              ["Interfaz administratively down", "Falta `no shutdown`", "`interface Gi0/x` → `no shutdown`"],
              ["PC en 169.254.x.x (APIPA)", "DHCP sin responder o pool malo", "Revisar `show ip dhcp pool` y el cable"],
              ["IP pero no ping al gateway", "IP fuera del rango o máscara mala", "`ipconfig /renew`, revisar `network`"],
              ["PC tomó la IP del gateway", "Gateway no excluido", "`excluded-address`, `clear ip dhcp binding`"],
              ["Gateway OK, otra VLAN falla", "OSPF no anuncia, o subinterfaz mal", "`show ip route`; `encapsulation dot1Q` y `network`"],
              ["OSPF sin vecinos", "Área distinta, red mal o enlace caído", "Revisar `area 0`, `show ip ospf interface brief`"],
              ["No aparece una subred vecina", "passive en un enlace, o falta la subinterfaz", "Quitar passive de Gi0/1 y Gi0/2"],
              ["RIPv2 no anuncia subredes", "Falta `no auto-summary`", "`no auto-summary` en `router rip`"]],
          0.45, 1.32, 12.4, col_w=[3.7, 4.4, 4.3], size=10.5, row_h=0.44)
    callout(s, 0.45, 5.42, 12.4, 1.50, "El patrón que hay detrás", [
        "La mitad de estos errores **no son de enrutamiento**: son de capa 1 o 2 (cable, `no shutdown`, DHCP).",
        "Antes de tocar OSPF, mirar `show ip interface brief` y `show ip dhcp binding`.",
        "Rescate de emergencia: `erase startup-config` + `reload` deja el equipo de fábrica (se vuelve a la Parte 1)."], ORANGE, 12)
    notes(s, "⏱ 92-102 min.\n\n"
             "No hace falta leerlos todos: elegir 2 o 3 y preguntar el síntoma. La\n"
             "tabla completa está en SESION-B.md, Parte 11.\n"
             "\n"
             "El más costoso en este lab es 'gateway OK pero otra VLAN falla': se\n"
             "pierde tiempo en OSPF cuando el problema es la subinterfaz o un\n"
             "`network` mal declarado.\n"
             "\n"
             "El rescate `erase + reload` es la última carta: documentar config antes\n"
             "o tenerla en config/R*.txt.")

    # ================================================================ 6.3 preguntas
    n += 1
    s = content(prs, "Preguntas de la Sesión B", "Para cerrar el entregable", PART, n + 1)
    callout(s, 0.45, 1.35, 12.4, 5.45, "Responde con lo que viste en la CLI", [
        [("1. ", {"color": ORANGE, "bold": True, "size": 12.5}),
         ("En `[110/2]`, ¿qué significan los dos números? ¿Cómo se calcula el 2 en el camino de R1 a la VLAN 20 de una sucursal?", {"size": 12.5})],
        [("2. ", {"color": ORANGE, "bold": True, "size": 12.5}),
         ("¿Por qué el tráfico entre sucursales pasa por la central y no por el enlace R2–R3? ¿Qué comando lo provoca?", {"size": 12.5})],
        [("3. ", {"color": ORANGE, "bold": True, "size": 12.5}),
         ("Con el uplink de la SUC-1 caído, ¿qué camino toma un paquete de PC-B1 a un PC de la central? Escribe el `tracert` esperado.", {"size": 12.5})],
        [("4. ", {"color": ORANGE, "bold": True, "size": 12.5}),
         ("¿Qué pasa si quitas `passive-interface Gi0/0`? ¿Y si lo pusieras en Gi0/1?", {"size": 12.5})],
        [("5. ", {"color": ORANGE, "bold": True, "size": 12.5}),
         ("¿Qué diferencia hay entre `show ip route` y `show ip protocols`?", {"size": 12.5})],
        [("6. ", {"color": ORANGE, "bold": True, "size": 12.5}),
         ("Compara la convergencia de OSPF y RIPv2. ¿Cuál usarías en una red de 50 routers y por qué?", {"size": 12.5})],
        [("7. ", {"color": ORANGE, "bold": True, "size": 12.5}),
         ("Un PC de la VLAN 10 obtuvo una IP de la VLAN 20. ¿Qué comando corregiste y con qué `show` lo detectas?", {"size": 12.5})]], TEAL, 12.5)
    notes(s, "⏱ 102-112 min.\n\n"
             "Las siete preguntas son el entregable escrito. La 2 y la 3 conectan\n"
             "directo con los costes y la prueba de redundancia; la 7 con el\n"
             "troubleshooting de DHCP.\n"
             "\n"
             "Déjalas como tarea si el tiempo no alcanza: están al final de\n"
             "SESION-B.md con más contexto.")

    # ================================================================ cierre
    n += 1
    s = content(prs, "Repaso: lo que hay que saber", "Cinco ideas y el entregable de la Sesión B", PART, n + 1)
    callout(s, 0.45, 1.32, 6.1, 4.40, "Las 5 ideas de la Sesión B", [
        [("1. ", {"color": ORANGE, "bold": True, "size": 12.5}),
         ("La red es hub-and-spoke: R1 central y R2/R3 suben por uplinks; R2–R3 es el respaldo.", {"size": 12.5})],
        [("2. ", {"color": ORANGE, "bold": True, "size": 12.5}),
         ("El trunk viaja sin etiqueta en la native VLAN: si no se fija en 10, el gateway queda en la VLAN 1.", {"size": 12.5})],
        [("3. ", {"color": ORANGE, "bold": True, "size": 12.5}),
         ("Router-on-a-stick: una interfaz física, dos gateways con `encapsulation dot1Q` y un pool por VLAN.", {"size": 12.5})],
        [("4. ", {"color": ORANGE, "bold": True, "size": 12.5}),
         ("OSPF aprende las 9 subredes solo: no hay estáticas y no hace falta quitarlas porque nunca se pusieron.", {"size": 12.5})],
        [("5. ", {"color": ORANGE, "bold": True, "size": 12.5}),
         ("Con los costes (uplink 1, respaldo 100), si cae un uplink OSPF recalcula y el tráfico sigue por el respaldo.", {"size": 12.5})]], NAVY, 12.5)
    callout(s, 6.75, 1.32, 6.15, 4.40, "Entregable de la Sesión B", [
        [("▸ ", {"color": ORANGE, "bold": True, "size": 11.5}),
         ("`show vlan brief` y `show interfaces trunk` de un switch.", {"size": 11.5})],
        [("▸ ", {"color": ORANGE, "bold": True, "size": 11.5}),
         ("`show ip interface brief` de los 3 routers.", {"size": 11.5})],
        [("▸ ", {"color": ORANGE, "bold": True, "size": 11.5}),
         ("`show ip dhcp pool` y `show ip dhcp binding` de R1.", {"size": 11.5})],
        [("▸ ", {"color": ORANGE, "bold": True, "size": 11.5}),
         ("`show ip route` de R1 y R2 con rutas `O` y **sin** `S`.", {"size": 11.5})],
        [("▸ ", {"color": ORANGE, "bold": True, "size": 11.5}),
         ("`show ip ospf neighbor` de los 3 routers en FULL.", {"size": 11.5})],
        [("▸ ", {"color": ORANGE, "bold": True, "size": 11.5}),
         ("Evidencia de redundancia: ping OK desde PC-B1 con `R1 Gi0/1` en `shutdown` + `tracert`.", {"size": 11.5})],
        [("▸ ", {"color": ORANGE, "bold": True, "size": 11.5}),
         ("`ipconfig /all` de un PC de cada VLAN y respuestas a las 7 preguntas.", {"size": 11.5})]], GREEN, 11.5)
    notes(s, "⏱ 112-120 min · Cierre.\n\n"
             "Recorre las 5 ideas y deja claro el entregable. Si sobra tiempo, pide a\n"
             "un equipo que demuestre la redundancia en directo.\n"
             "\n"
             "La Sesión B es ahora un laboratorio completo por sí mismo: montar,\n"
             "segmentar, enrutar de forma dinámica y demostrar que la red se\n"
             "recupera sola.")

    prs.save(out)
    return out


if __name__ == "__main__":
    p = build(sys.argv[1] if len(sys.argv) > 1 else "Sesion-B.pptx")
    print("OK ->", p)