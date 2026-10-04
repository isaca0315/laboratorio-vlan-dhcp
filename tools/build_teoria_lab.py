"""Teoría del Laboratorio N.º 13 — VLSM, DHCP y enrutamiento · 60 min.

Genera Teoria-Lab-VLSM-DHCP.pptx con el mismo sistema de diseño que el resto de
las presentaciones del curso (ppt_kit: 16:9, navy 1F3864 + naranja E87C1E).

El orden sigue el hilo lógico del lab: primero se entiende la dirección IP y la
máscara, después se subnetea, y recién entonces tiene sentido el switch, el DHCP
y el enrutamiento.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from ppt_kit import *  # noqa

PART = "Lab 13 · VLSM, DHCP y enrutamiento"
MIN = "60 min"


def build(out):
    prs = new_deck()
    n = 0

    # ================================================================ 1 portada
    s = cover(prs, "UNIVERSIDAD TECNOLÓGICA DE PANAMÁ · FACULTAD DE INGENIERÍA DE SISTEMAS COMPUTACIONALES",
              "Teoría del Laboratorio N.º 13",
              "VLSM, DHCP y enrutamiento en Packet Tracer",
              ["IP, máscara y VLSM · por qué unas subredes son /28 y otras /30",
               "Switch, router, ARP y DHCP · el DORA paso a paso",
               "Tabla de enrutamiento · rutas estáticas · OSPF · redundancia"],
              "Teoría previa a las Sesiones A y B", "60 min de clase")
    notes(s, "⏱ 0-3 min · Apertura.\n\n"
             "Esta es la teoría que sostiene el Lab 13. No es teoría suelta: cada\n"
             "bloque corresponde a algo que van a escribir en la Sesión A o B.\n"
             "\n"
             "El hilo es: dirección IP → máscara → subredes (VLSM) → dispositivos →\n"
             "DHCP → tabla de enrutamiento → estáticas → OSPF.\n"
             "\n"
             "Pregunta de arranque para enganchar: ¿por qué en el laboratorio unas\n"
             "redes usan /28 y otras /30? La respuesta está en el bloque 2.")

    # ================================================================ 2 mapa
    n += 1
    s = content(prs, "Qué vamos a ver", "Cinco bloques que van del número al cable", PART, n + 1)
    table(s, [["#", "Bloque", "Pregunta que responde", "Min"],
              ["1", "Dirección IP y máscara", "¿Qué es un prefijo y por qué 2^h − 2?", "10"],
              ["2", "VLSM", "¿Por qué unas subredes son /28 y otras /30?", "12"],
              ["3", "Switch, router y cable", "¿Quién reenvía por MAC y quién por IP?", "10"],
              ["4", "DHCP", "¿Cómo consigue un PC su IP sin que nadie la escriba?", "10"],
              ["5", "Enrutamiento", "¿Cómo sabe el router por dónde enviar un paquete?", "14"],
              ["—", "Cierre", "Verificación, límites de PT y repaso", "4"]],
          0.45, 1.40, 12.4, col_w=[0.7, 3.3, 7.3, 1.1], size=12.5, row_h=0.40)
    callout(s, 0.45, 4.85, 12.4, 1.85, "La idea que sostiene todo el laboratorio", [
        "Una red no es «un switch con todos juntos»: es **segmentar** con las direcciones justas,",
        "**servir** esas direcciones automáticamente, y **conectar** los segmentos con rutas.",
        "Cada capa depende de la anterior: si la máscara está mal, DHCP entrega direcciones",
        "imposibles y el enrutamiento ni siquiera se intentará."], ORANGE, 12.5)
    notes(s, "⏱ 3-4 min · Mapa de la clase.\n\n"
             "Señala que el orden importa: no se puede entender DHCP sin la máscara,\n"
             "ni el enrutamiento sin el gateway.\n"
             "Deja claro que casi todo lo que vemos es teoría de la Sesión A; OSPF es\n"
             "lo único de la Sesión B.")

    # ================================================================ DIV 1
    s = divider(prs, "1", "Dirección IP y máscara", "El bloque de todo lo demás",
                ["Qué es una dirección IP y cómo se parte en red + host",
                 "Máscara de subred y prefijo CIDR",
                 "La fórmula 2^h − 2 y por qué se restan 2",
                 "Las direcciones especiales de una subred"], "10 min")
    notes(s, "⏱ 4-5 min · Transición.\n\n"
             "Pregunta para el grupo antes de avanzar: si una dirección tiene 4 octetos,\n"
             "¿cuántos identifican la red y cuántos el equipo? Que el número salga de la\n"
             "máscara, no del formato.")

    # ================================================================ 1.1 qué es una IP
    n += 1
    s = content(prs, "Qué es una dirección IP", "32 bits que identifican un equipo dentro de una red", PART, n + 1)
    code(s, 0.45, 1.40, 5.85, 2.25,
         ["192.168.2.1",
          "‾‾‾‾  ‾‾‾‾   ‾‾      ‾",
          " red    red    subred   equipo"], 13)
    text(s, 0.45, 3.80, 5.85, 1.0,
         "Cada octeto va de **0 a 255** (8 bits). Los 32 bits se reparten entre la\n"
         "**parte de red** (qué red es) y la **parte de host** (qué equipo es).",
         size=13.5)
    callout(s, 0.45, 4.90, 5.85, 1.75, "El reparto lo decide la máscara, no el número", [
        "Con 192.168.2.1 y máscara /24, los 3 primeros octetos son red.",
        "Con la misma IP y máscara /28, el 4.º octeto empieza a ser de red también.",
        "Por eso «cuántos equipos caben» no es una propiedad de la IP:",
        "es una propiedad de la IP **más** su máscara."], TEAL, 12)
    text(s, 6.75, 1.40, 6.15, 0.4, "Anatomía de una subred", size=16, color=NAVY, bold=True)
    table(s, [["Elemento", "En 192.168.2.0/28", "Para qué sirve"],
              ["Dirección de red", ".0", "Identifica la subred"],
              ["Primera útil", ".1", "Suele ser el gateway"],
              ["Última útil", ".14", "Último equipo asignable"],
              ["Broadcast", ".15", "Habla a todos a la vez"],
              ["Máscara", "255.255.255.240", "Separa red de host"]],
          6.75, 1.85, 6.15, col_w=[1.75, 2.05, 2.35], size=11.5, row_h=0.42)
    callout(s, 6.75, 4.90, 6.15, 1.75, "Las clases ya no se usan", [
        "La dirección «dice» su clase por el primer octeto (A, B, C).",
        "Hoy nadie usa clases: el tamaño de la red lo dice **el prefijo**.",
        "Por eso 192.168.2.0 puede dividirse en 6 subredes de tamaños distintos",
        "sin que nada contradiga el «diseño original»."], NAVY, 12)
    notes(s, "⏱ 5-7 min.\n\n"
             "Insiste en que la IP sola no dice nada: hace falta la máscara.\n"
             "Mismo número, distinta máscara, distinta red.\n"
             "\n"
             "Las clases (A/B/C) aparecen en los libros por historia. Si alguien pregunta\n"
             "por qué 192 es clase C: porque el diseño histórico reservaba el primer octeto\n"
             "para eso. Ya es irrelevante para el cálculo.")

    # ================================================================ 1.2 máscara y prefijo
    n += 1
    s = content(prs, "Máscara de subred y prefijo", "La misma idea, dos formas de escribirla", PART, n + 1)
    text(s, 0.45, 1.35, 12.4, 0.4, "La máscara es una cadena de bits: unos = red, ceros = host.", size=15)
    code(s, 0.45, 1.85, 12.4, 1.60,
         [("/28 = 255.255.255.240 = 11111111.11111111.11111111.1111 0000", ORANGE),
          ("      24 bits de red (fijos)                       4 bits de host", GRAY),
          ("/30 = 255.255.255.252 = 11111111.11111111.11111111.1111 11 00", TEAL),
          ("      24 bits de red (fijos)                          2 bits de host", GRAY)], 13.5)
    kpi(s, [("/28", "prefijo"), ("/24", "prefijo"), ("4", "bits de host"),
            ("14", "hosts útiles"), ("16", "direcciones")], 0.45, 3.55, 12.4, 1.05)
    table(s, [["Prefijo", "Máscara en decimal", "Bits de host", "Hosts útiles", "Tamaño del bloque"],
              ["/27", "255.255.255.224", "5", "30", "32"],
              ["/28", "255.255.255.240", "4", "14", "16"],
              ["/29", "255.255.255.248", "3", "6", "8"],
              ["/30", "255.255.255.252", "2", "2", "4"],
              ["/31", "255.255.255.254", "1", "2 (punto a punto)", "4"]],
          0.45, 4.72, 12.4, col_w=[1.5, 3.2, 2.2, 3.0, 2.5], size=12, row_h=0.32)
    text(s, 0.45, 6.75, 12.4, 0.3, "**Nunca** escribas /28 en un comando de Cisco: la máscara va en decimal.", size=12)
    notes(s, "⏱ 7-9 min.\n\n"
             "Regla: el prefijo es el número de unos. Contar los ceros del final da el\n"
             "tamaño del bloque (2^c).\n"
             "\n"
             "Errón típico: escribir /28 en 'ip address'. Cisco espera decimal y da error.\n"
             "El prefijo solo se usa con wildcard en OSPF/RIP.\n"
             "\n"
             "/31 es caso especial (RFC 3021, sin broadcast). En Packet Tracer no se usa.")

    # ================================================================ 1.3 fórmula
    n += 1
    s = content(prs, "La fórmula 2^h − 2", "Por qué un /28 no da 16 equipos sino 14", PART, n + 1)
    flow(s, [("h bits", "cuántos bits\ndedico a host"),
             ("2^h", "direcciones\ntotales del bloque"),
             ("− 2", "red y broadcast\nno se asignan"),
             ("2^h − 2", "hosts que\npuedo usar")],
         0.45, 1.45, 12.4, h=1.15)
    text(s, 0.45, 2.95, 6.1, 0.4, "Los dos que se pierden", size=15, color=NAVY, bold=True)
    bullets(s, [
        "La **dirección de red** identifica la subred. Si un equipo la toma, el",
        "tráfico hacia el resto de la LAN se rompe.",
        "La **dirección de broadcast** habla a todos los equipos a la vez. Es",
        "para difusión, no para un equipo concreto.",
    ], 0.45, 3.40, 6.1, 13, 6, h=1.35)
    callout(s, 0.45, 4.85, 6.1, 1.85, "Cuidado con el truco", [
        "Para elegir bits de host hay que contar los dos direcciones extra:",
        "**2^h ≥ equipos + 2**, no solo ≥ equipos.",
        "Con 10 equipos: 2^4 = 16 ≥ 12 ✓, y 2^3 = 8 < 12 ✗.",
        "Por eso h = 4 y el prefijo es /28."], ORANGE, 12)
    text(s, 6.75, 2.95, 6.15, 0.4, "Los tres pasos para elegir prefijo", size=15, color=NAVY, bold=True)
    table(s, [["Equipos", "Prueba", "h", "Prefijo", "¿Sirve?"],
              ["10", "2^3 − 2 = 6", "3", "/29", "No, insuficiente"],
              ["10", "2^4 − 2 = 14", "4", "/28", "Sí"],
              ["10", "2^5 − 2 = 30", "5", "/27", "Sí, pero desperdicia"],
              ["2", "2^1 − 2 = 0", "1", "/31", "No, insuficiente"],
              ["2", "2^2 − 2 = 2", "2", "/30", "Sí"]],
          6.75, 3.40, 6.15, col_w=[1.0, 1.65, 0.6, 1.05, 1.85], size=11.5, row_h=0.4)
    callout(s, 6.75, 5.88, 6.15, 1.15, "Regla del laboratorio", [
        "Se elige **el prefijo más corto que cumple**. Un /27 también serviría",
        "para 10 equipos, pero tiraría 16 direcciones por LAN."], GREEN, 12)
    notes(s, "⏱ 9-12 min · el corazón del cálculo.\n\n"
             "Si algo no queda claro, volver aquí.\n"
             "\n"
             "El error del 2^h ≥ equipos (sin +2) es el más común de todos: da /29 para\n"
             "10 equipos y luego un PC se queda sin dirección.\n"
             "\n"
             "En la tabla: /29 es insuficiente y /27 wasteful. /28 es el único que cumple\n"
             "exactamente. Esa es la definición de 'más eficiente'.")

    # ================================================================ DIV 2
    s = divider(prs, "2", "VLSM", "Por qué unas subredes son /28 y otras /30",
                ["Qué es VLSM y por qué no usar una sola máscara",
                 "El método en 6 pasos",
                 "Los dos requisitos del laboratorio",
                 "Las 6 subredes y los errores típicos"], "12 min")
    notes(s, "⏱ 12-13 min · Transición.\n\n"
             "Aquí se responde la pregunta del arranque. Anota en la pizarra la\n"
             "pregunta tal como la hizo el estudiante.")

    # ================================================================ 2.1 FLSM vs VLSM
    n += 1
    s = content(prs, "VLSM: una máscara por necesidad", "Por qué 6 redes de 192.168.2.0/24 no pueden compartir máscara", PART, n + 1)
    text(s, 0.45, 1.35, 12.4, 0.4,
         "Si dividiéramos el /24 con una sola máscara, cada subred tendría el mismo tamaño. Eso es **FLSM** y desperdicia.", size=14.5)
    table(s, [["", "FLSM · todo /26", "VLSM · lo que hacemos", "Diferencia"],
              ["LAN-A, LAN-B, LAN-C", "3 × 64 = 192 dir", "3 × 16 = 48 dir", "144 dir menos"],
              ["Enlaces entre routers", "3 × 64 = 192 dir", "3 × 4 = 12 dir", "180 dir menos"],
              ["Total usado", "384 de 256 ⚠", "60 de 256", "imposible vs posible"]],
          0.45, 1.95, 12.4, col_w=[3.3, 3.0, 3.1, 3.0], size=12.5, row_h=0.42)
    callout(s, 0.45, 3.68, 6.1, 1.5, "Con FLSM no cabe", [
        "6 subredes de 64 direcciones = 384, pero /24 solo tiene 256.",
        "El cálculo **falla antes de configurar nada**.",
        "VLSM es lo que hace posible el diseño."], RED, 12.5)
    callout(s, 6.75, 3.68, 6.15, 1.5, "Con VLSM sobra", [
        "60 direcciones usadas de 256 → **76 % libre**.",
        "Ese margen es el que permite crecer: añadir una subred /28 en .60",
        "sin rehacer el direccionamiento."], GREEN, 12.5)
    text(s, 0.45, 5.30, 12.4, 0.4, "El método en 6 pasos", size=15, color=NAVY, bold=True)
    flow(s, [("1 Ordena", "de mayor\na menor"),
             ("2 Bits", "2^h ≥ nece-\nsidad + 2"),
             ("3 Prefijo", "32 − h y su\nmáscara"),
             ("4 Alinea", "múltiplo del\ntamaño"),
             ("5 Asigna", "red, útiles,\nbroadcast"),
             ("6 Comprueba", "sin solapes\ny ≤ 256")],
         0.45, 5.75, 12.4, h=1.05, size=11.5)
    notes(s, "⏱ 13-16 min.\n\n"
             "El paso 4 es el que más cuesta: una /28 debe empezar en un múltiplo de 16,\n"
             "una /30 en un múltiplo de 4.\n"
             "\n"
             "Buen momento para mostrar que el error se detecta en papel: si al alinear\n"
             "no cuadra, el diseño está mal antes de tocar un cable.\n"
             "\n"
             "La tabla FLSM es un buen golpe visual: 384 > 256 es imposible de un vistazo.")

    # ================================================================ 2.2 los dos requisitos
    n += 1
    s = content(prs, "Los dos requisitos del laboratorio", "La respuesta a «¿por qué /28 y /30?»", PART, n + 1)
    table(s, [["Tipo de segmento", "Equipos que necesitan IP", "Cálculo", "Prefijo", "Útiles"],
              ["LAN-A, LAN-B, LAN-C", "10 de diseño (hoy: 1 GW + 3 PCs)", "2^4 − 2 = 14 ≥ 10", "/28", "14"],
              ["Enlaces entre routers", "2  (la interfaz de cada extremo)", "2^2 − 2 = 2 ≥ 2", "/30", "2"]],
          0.45, 1.32, 12.4, col_w=[3.2, 4.3, 2.6, 1.2, 1.1], size=12.5, row_h=0.45)
    text(s, 0.45, 2.72, 12.4, 0.4,
         "Son **dos cálculos porque hay dos requisitos**. No es «subnetear las LAN» y «subnetear los routers» por separado.", size=14)
    callout(s, 0.45, 3.15, 12.4, 1.70, "La prueba: un mismo router tiene las dos máscaras", [
        [("R1 Gi0/0 → 192.168.2.1/28", {"font": "Consolas", "size": 12, "color": NAVY, "bold": True}),
         ("   conecta con el switch: 10 equipos en la LAN", {"size": 12})],
        [("R1 Gi0/1 → 192.168.2.49/30", {"font": "Consolas", "size": 12, "color": ORANGE, "bold": True}),
         ("  conecta con R2: solo 2 equipos", {"size": 12})],
        [("R1 Gi0/2 → 192.168.2.58/30", {"font": "Consolas", "size": 12, "color": ORANGE, "bold": True}),
         ("  conecta con R3: solo 2 equipos", {"size": 12})]], ORANGE, 12)
    table(s, [["Si el destino...", "Por qué funciona", "Por qué no"],
              ["Un enlace es /28", "Funciona, pero sobran 12 IPs. Con 3 enlaces son 36 dir. tiradas", "Desperdicio innecesario"],
              ["Una LAN es /30", "2 IPs útiles, el gateway toma 1 y solo queda 1", "No alcanza para 3 PCs"]],
          0.45, 4.95, 12.4, col_w=[2.6, 6.4, 3.4], size=12.5, row_h=0.45)
    callout(s, 0.45, 6.25, 12.4, 0.80, "La asimetría que resume el método", [
        "Sobre-asignar funciona pero desperdicia. Sub-asignar rompe el laboratorio. "
        "Por eso siempre se calcula el mínimo que cumple."], NAVY, 12.5)
    notes(s, "⏱ 16-19 min · la pregunta del estudiante.\n\n"
             "Esta es la diapositiva que responde «¿por qué unas /30 y otras /28?».\n"
             "\n"
             "El argumento central: el criterio NO es si el otro extremo es switch o\n"
             "router. R1 tiene las dos máscaras en el mismo equipo. Lo que decide es\n"
             "cuántos dispositivos necesitan dirección en ese segmento.\n"
             "\n"
             "Si preguntan por qué no /31 para los enlaces: /31 existe (RFC 3021) pero\n"
             "PT y el IOS clásico no la aceptan en Ethernet.")

    # ================================================================ 2.3 tabla de subredes
    n += 1
    s = content(prs, "Las 6 subredes del laboratorio", "El resultado final del cálculo", PART, n + 1)
    table(s, [["#", "Subred", "Bloque", "¿Alineada?", "Red", "Hosts útiles", "Bcast", "Uso"],
              ["1", "192.168.2.0/28", "16", "0 = 0×16 ✓", ".0", ".1 – .14", ".15", "LAN-A"],
              ["2", "192.168.2.16/28", "16", "16 = 1×16 ✓", ".16", ".17 – .30", ".31", "LAN-B"],
              ["3", "192.168.2.32/28", "16", "32 = 2×16 ✓", ".32", ".33 – .46", ".47", "LAN-C"],
              ["4", "192.168.2.48/30", "4", "48 = 12×4 ✓", ".48", ".49 – .50", ".51", "R1 – R2"],
              ["5", "192.168.2.52/30", "4", "52 = 13×4 ✓", ".52", ".53 – .54", ".55", "R2 – R3"],
              ["6", "192.168.2.56/30", "4", "56 = 14×4 ✓", ".56", ".57 – .58", ".59", "R3 – R1"],
              ["—", ".60 – .255", "—", "—", "—", "—", "—", "196 libres"]],
          0.45, 1.40, 12.4, col_w=[0.55, 2.75, 0.9, 2.0, 0.9, 2.1, 0.95, 2.25], size=11.5, row_h=0.35)
    kpi(s, [("3×16", "LAN"), ("3×4", "enlaces"), ("60", "usadas"),
            ("196", "libres"), ("77%", "libre")], 0.45, 4.35, 12.4, 1.0)
    callout(s, 0.45, 5.45, 6.1, 1.4, "Cómo se verifica sin calculadora", [
        "Suma bloques: 3×16 + 3×4 = **60**.",
        "La siguiente posición libre es .60: es múltiplo de 16 y de 4 →",
        "cabe otra subred. Si no fuera múltiplo, el diseño estaría mal."], TEAL, 12)
    callout(s, 6.75, 5.45, 6.15, 1.4, "Reparto interno de cada LAN", [
        "En LAN-A: `.1` gateway, `.2`–`.5` reservadas, `.6`–`.14` para DHCP.",
        "Hoy solo 3 PCs usan ese rango; las otras 6 direcciones quedan libres.",
        "El crecimiento real está en `.60` en adelante: eso da el 77 % libre."], GREEN, 12)
    notes(s, "⏱ 19-22 min.\n\n"
             "Recorre la tabla fila por fila y haz que el grupo diga si está alineada.\n"
             "\n"
             "El detalle del reparto interno suele sorprender: el requisito decía 10\n"
             "equipos, pero el plan usa los 14 útiles. No sobran IPs en las LAN.\n"
             "\n"
             "Si piden ejercicio: ¿por qué .62/30 no vale? Porque 62 no es múltiplo de 4.\n"
             "Está en SUBNETEO.md como ejercicio 2.")

    # ================================================================ 2.4 errores
    n += 1
    s = content(prs, "Los 6 errores típicos de subneteo", "Reconocerlos por el síntoma es más rápido que recalcular", PART, n + 1)
    table(s, [["Error", "Por qué falla", "Síntoma que se ve en el lab"],
              ["Usar /29 para una LAN", "6 útiles < 10 equipos", "El 4.º PC queda en 169.254.x.x"],
              ["Empezar la 2.ª LAN en .15/28", ".15 es el broadcast de LAN-A", "Las subredes se solapan"],
              ["Poner un /30 en .46", "46 no es múltiplo de 4", "IOS lo rechaza: no alineada"],
              ["Usar .50/30 como red", ".50 es dirección de host", "Red con bits incoherentes"],
              ["No excluir el gateway del pool", "Un PC puede tomar .1", "La LAN se parte en dos y nadie pingea"],
              ["Escribir /28 en ip address", "Cisco espera decimal", "Error de sintaxis inmediato"]],
          0.45, 1.40, 12.4, col_w=[3.6, 4.0, 4.8], size=12, row_h=0.52)
    callout(s, 0.45, 5.00, 6.1, 1.6, "El más caro: no excluir el gateway", [
        "Si un PC obtiene .1, se convierte en un host más.",
        "El router tiene dos cosas en la misma IP.",
        "Resultado: mitad de la LAN sin poder hablar con la otra mitad.",
        "Se previene con `ip dhcp excluded-address`."], RED, 12)
    callout(s, 6.75, 5.00, 6.15, 1.6, "El más sutil: .15 como red", [
        "`.15` es el broadcast de `192.168.2.0/28`, no un host.",
        "La siguiente subred empieza en `.16`, siempre en el siguiente",
        "múltiplo del bloque. Never divide el espacio sin mirar la alineación."], ORANGE, 12)
    notes(s, "⏱ 22-25 min.\n\n"
             "No leer los 6: elegir 2 y preguntar el síntoma. El de 'no excluir el\n"
             "gateway' es el que más daño hace y el más difícil de diagnosticar.\n"
             "\n"
             "El de 169.254.x.x lo van a ver en la Sesión A si algo sale mal: es la\n"
             "señal de que no hubo respuesta DHCP.")

    # ================================================================ DIV 3
    s = divider(prs, "3", "Switch, router y cable", "Quién reenvía por MAC y quién por IP",
                ["El switch trabaja en la capa 2",
                 "El router trabaja en la capa 3",
                 "Por qué una malla de 3 routers y no un switch grande",
                 "Ethernet y cables de cobre · ARP y el gateway"], "10 min")
    notes(s, "⏱ 25-26 min · Transición.\n\n"
             "Hasta ahora solo números. Ahora: quién mueve esos paquetes.")

    # ================================================================ 3.1 switch vs router
    n += 1
    s = content(prs, "Switch y router: no son intercambiables", "Capa 2 contra capa 3", PART, n + 1)
    table(s, [["", "Switch 2960", "Router 2911"],
              ["Capa OSI", "2 · Enlace de datos", "3 · Red"],
              ["Decide mirando...", "la **dirección MAC**", "la **dirección IP**"],
              ["Su tabla es...", "tabla MAC (aprende por floods)", "tabla de enrutamiento"],
              ["Conecta...", "equipos de **la misma** red", "redes **distintas** entre sí"],
              ["Aísla el broadcast?", "No, lo reenvía", "Sí, cada interfaz es un dominio aparte"],
              ["En este lab", "SW1, SW2, SW3 (9 PCs)", "R1, R2, R3 (unen las 3 LAN)"]],
          0.45, 1.40, 12.4, col_w=[2.9, 4.6, 4.9], size=12.5, row_h=0.44)
    callout(s, 0.45, 4.85, 12.4, 1.05, "La frase que resume la diferencia", [
        "El switch mueve **tramas dentro** de una red. El router mueve **paquetes entre** redes.",
        "Por eso los 9 PCs de una LAN se hablan entre sí sin que ningún router participe"], TEAL, 12.5)
    callout(s, 0.45, 5.98, 12.4, 1.05, "Y el switch aprende solo", [
        "No se configura: empieza vacío, inunda y memoriza qué MAC está en cada puerto.",
        "Router en cambio sí necesita que le digan por dónde salir: eso es la tabla de enrutamiento."], NAVY, 12)
    notes(s, "⏱ 26-28 min.\n\n"
             "Analogía útil: el switch es el mayordomo que reparte cartas dentro del\n"
             "edificio; el router es el cartero que sabe salir a otra calle.\n"
             "\n"
             "El flooding del switch es lo que hace que 'no se configure'.")

    # ================================================================ 3.2 malla
    n += 1
    s = content(prs, "Por qué una malla de 3 routers", "Cada uno con enlaces a los otros dos", PART, n + 1)
    text(s, 0.45, 1.35, 12.4, 0.4,
         "Con 3 routers y enlaces en malla completa hay **dos caminos** entre cualquier par de sedes.", size=14.5)
    table(s, [["Enlace", "Subred", "Extremo A", "Extremo B", "Cable"],
              ["Enlace 1", "192.168.2.48/30", "R1 Gi0/1 = .49", "R2 Gi0/1 = .50", "Cobre recto"],
              ["Enlace 2", "192.168.2.52/30", "R2 Gi0/2 = .53", "R3 Gi0/1 = .54", "Cobre recto"],
              ["Enlace 3", "192.168.2.56/30", "R3 Gi0/2 = .57", "R1 Gi0/2 = .58", "Cobre recto"]],
          0.45, 1.90, 12.4, col_w=[1.7, 3.0, 2.6, 2.6, 2.5], size=12.5, row_h=0.44)
    callout(s, 0.45, 3.75, 6.1, 1.65, "Qué gana la malla", [
        "**Redundancia**: si cae un enlace, el tráfico reruta por el otro.",
        "Con dos rutas, el tráfico entre sedes tiene dos caminos posibles.",
        "En la Sesión B esto se demuestra apagando un cable."], GREEN, 12.5)
    callout(s, 6.75, 3.75, 6.15, 1.65, "Por qué no un solo router central", [
        "Un router solo reparte IPs de la subred de **su propia** interfaz.",
        "Para servir las otras LANs necesita `ip helper-address`.",
        "Packet Tracer **no implementa** ese comando, así que el diseño "
        "del lab usa 3 routers. Es una limitación de la herramienta, no del diseño."], ORANGE, 12)
    callout(s, 0.45, 5.60, 12.4, 1.35, "Y las tres LAN van a un switch, no directamente al router", [
        "Cada LAN tiene su switch: SW1 con R1, SW2 con R2, SW3 con R3.",
        "El router solo necesita **un** cable por LAN: el de su interfaz Gi0/0.",
        "Los 3 PCs se reparten los puertos Fa0/2, Fa0/3 y Fa0/4 de su switch."], TEAL, 12.5)
    notes(s, "⏱ 28-30 min.\n\n"
             "Insiste en el punto de ip helper-address: es un límite de Packet Tracer,\n"
             "no una buena práctica de diseño. Si alguien pregunta '¿se podría con un\n"
             "router central en un router real?', la respuesta es sí.\n"
             "\n"
             "La malla completa se explica aquí; la demostración de redundancia con\n"
             "OSPF es en la Sesión B.")

    # ================================================================ 3.3 cables
    n += 1
    s = content(prs, "Ethernet y cables de cobre", "Por qué 15 cables recto y ninguno serial", PART, n + 1)
    table(s, [["Qué se conecta", "Tipo de cable en PT", "Cuántos"],
              ["Router ↔ switch", "Copper Straight-Through", "3"],
              ["PC ↔ switch", "Copper Straight-Through", "9"],
              ["Router ↔ router", "Copper Straight-Through", "3"],
              ["Router ↔ router (variante)", "Serial DCE + `clock rate`", "3 · opcional"]],
          0.45, 1.40, 12.4, col_w=[4.4, 5.0, 3.0], size=12.5, row_h=0.44)
    callout(s, 0.45, 3.68, 6.1, 1.75, "Por qué recto y no crossover", [
        "Crossover se usaba entre dos dispositivos **iguales**.",
        "Como aquí todos los pares son distintos (router-switch, PC-switch),",
        "basta el recto.",
        "Además el 2911 tiene **auto-MDIX**: negocia solo y acepta ambos.",
        "En PT puedes elegir crossover y también funcionaría."], TEAL, 12)
    callout(s, 6.75, 3.68, 6.15, 1.75, "Por qué no Serial", [
        "El cable serial es de WAN: entre routers **no adyacentes**.",
        "Si lo usas, el lado DCE necesita `clock rate 64000` o el enlace no",
        "levanta: sin reloj no hay señal.",
        "Requiere instalar el módulo HWIC-2T con el router apagado.",
        "En este lab el gigabit basta y es más simple."], NAVY, 12)
    callout(s, 0.45, 5.52, 12.4, 1.50, "Lo primero que se ve mal: las luces", [
        "En Packet Tracer las Gi del 2911 nacen **apagadas administrativamente**.",
        "Con el cableado correcto pero sin configurar, los cables se ven **rojos**.",
        "Eso no significa cable mal conectado: significa que falta `no shutdown`.",
        "Pasa a verde solo después del `no shutdown` de la Sesión A."], RED, 12.5)
    notes(s, "⏱ 30-32 min.\n\n"
             "Muy probable que alguien reporte 'los cables salen rojos'. Adelantarse.\n"
             "\n"
             "El auto-MDIX del 2911 es la razón por la que el crossover es irrelevante\n"
             "aquí; en equipos viejos sin auto-MDIX sí importaba.\n"
             "\n"
             "clock rate: el lado DCE genera el reloj. Si no lo pones, la interfaz queda\n"
             "down/down aunque el cable esté perfecto.")

    # ================================================================ 3.4 ARP
    n += 1
    s = content(prs, "ARP: cómo el PC encuentra al gateway", "El paso que casi nadie explica y todos lo ejecutan", PART, n + 1)
    text(s, 0.45, 1.35, 12.4, 0.4, "Un PC decide **por IP**, pero en un cable Ethernet cada trama sale con una **MAC**. ARP traduce.", size=14.5)
    flow(s, [("PC quiere\nping 8.8.8.8", "compara\ndestino vs su /28"),
             ("¿Está en\nmi red?", "no: .1–.14 es\nmi segmento"),
             ("ARP:\n\"¿quién es .1?\"", "broadcast a\ntoda la LAN"),
             ("R1 responde\ncon su MAC", "ARP reply\nunicast"),
             ("PC encapsula\ny envía a R1", "allá enruta\nhacia Internet")],
         0.45, 1.85, 12.4, h=1.05, size=11)
    callout(s, 0.45, 3.20, 6.1, 1.75, "Por qué esto exige un gateway en la misma LAN", [
        "El PC **no** puede armar la trama si no conoce una MAC.",
        "Solo hay una MAC que puede usar: la del gateway.",
        "Si el gateway estuviera en otra red, el PC no podría salir nunca.",
        "Por eso la opción 3 del DHCP (default-router) es obligatoria."], ORANGE, 12)
    callout(s, 6.75, 3.20, 6.15, 1.75, "ARP es solo local", [
        "ARP nunca cruza un router. Se resuelve **por segmento**.",
        "Cada router hace su propio ARP hacia su siguiente salto.",
        "Por eso en cada /30 solo se ve tráfico entre los 2 extremos:",
        "nadie más existe en ese cable."], TEAL, 12)
    code(s, 0.45, 5.25, 12.4, 1.55,
         [("PC-A> arp -a          R1> show ip arp", ORANGE),
          ("  192.168.2.1   0000.0c29.5b11.22   ARPA   LAN-A R1-Gig0/0", GRAY),
          ("  192.168.2.5   0050.ea3d.9f01   ARPA   LAN-A PC-A", GRAY)], 12)
    notes(s, "⏱ 32-34 min.\n\n"
             "Esta diapositiva responde la duda más común del lab: 'mi PC ya tiene\n"
             "IP, ¿por qué necesita otra cosa?'.\n"
             "\n"
             "Buen experimento mental: si el ping a la IP del gateway funciona pero a\n"
             "otra red no, el problema no es la IP del PC: es la ruta.\n"
             "\n"
             "El 'porque está en mi red' es la comparación de los primeros 4 octetos\n"
             "más la máscara; si difieren, el destino no es local.")

    # ================================================================ DIV 4
    s = divider(prs, "4", "DHCP", "Cómo consigue un PC su IP sin que nadie la escriba",
                ["Por qué DHCP y no IP fija",
                 "El DORA paso a paso",
                 "El pool: red, opciones y exclusiones",
                 "Qué comando se ejecuta en cada lado"], "10 min")
    notes(s, "⏱ 34-35 min · Transición.\n\n"
             "Hasta ahora el PC tenía IP porque alguien la escribió. Ahora explica\n"
             "cómo la consigue solo. En el lab, los 9 PCs (3 por LAN) la reciben así.")

    # ================================================================ 4.1 por qué DHCP
    n += 1
    s = content(prs, "Por qué DHCP y no IP fija", "Tres problemas que la IP manual no resuelve", PART, n + 1)
    table(s, [["Problema con IP fija", "Qué pasa en la práctica", "Cómo lo resuelve DHCP"],
              ["Conflicto de direcciones", "Un PC nuevo toma .5 y nada funciona", "El servidor entrega direcciones libres"],
              ["Cambio de subred", "Hay que tocar 15 equipos a mano", "Se reconfigura el servidor"],
              ["Cambio de gateway o DNS", "Hay que editar cada equipo", "El PC renueva y se actualiza"],
              ["Equipos fuera de servicio", "La IP queda reservada y desperdiciada", "El pool la reutiliza"]],
          0.45, 1.40, 12.4, col_w=[3.2, 4.7, 4.5], size=12.5, row_h=0.46)
    callout(s, 0.45, 3.95, 12.4, 1.35, "Y qué gana el administrador", [
        "Un solo lugar donde ver y cambiar la configuración de la red: `show ip dhcp binding`.",
        "El router es el servidor DHCP **de su propia LAN** (servidor por defecto).",
        "Cada LAN tiene su propio pool porque cada una necesita entregar su gateway como opción 3."], GREEN, 12.5)
    callout(s, 0.45, 5.40, 12.4, 1.35, "El coste: el equipo necesita un piso de arranque", [
        "Sin leases el PC arranca en **APIPA**: 169.254.x.x, que **no** enrutable.",
        "Si ves 169.254 en un PC del lab, el DHCP no respondió. Es el primer síntoma a revisar.",
        "La lista de IPs esperadas en LAN-B es .17–.30; si un PC queda fuera de ese rango, el DHCP no está repartiendo esa IP."], RED, 12.5)
    notes(s, "⏱ 35-37 min.\n\n"
             "APIPA es el punto clave: es lo que van a ver si algo falla. Decirles que\n"
             "169.254 significa 'nadie me dio dirección'.\n"
             "\n"
             "El término correcto: el router actúa como servidor DHCP de su LAN. En el\n"
             "lab cada router sirve un pool distinto (R1 → LAN-A, R2 → LAN-B, R3 → LAN-C).")

    # ================================================================ 4.2 DORA
    n += 1
    s = content(prs, "El DORA, paso a paso", "Discover, Offer, Request, Acknowledge", PART, n + 1)
    table(s, [["Paso", "Quién envía", "A quién", "Mensaje", "Qué lleva"],
              ["1 · D", "PC (cliente)", "broadcast 255.255.255.255", "Discover", "\"¿Hay algún servidor DHCP?\" — su MAC"],
              ["2 · O", "servidor DHCP", "al PC", "Offer", "La IP que le ofrece + máscara, gw, DNS, lease"],
              ["3 · R", "PC (cliente)", "al servidor", "Request", "\"Quiero esa\" — pide específicamente esa IP"],
              ["4 · A", "servidor DHCP", "al PC", "Acknowledge", "Confirma y empieza el tiempo de concesión"]],
          0.45, 1.40, 12.4, col_w=[1.0, 2.2, 2.6, 2.1, 4.5], size=11.5, row_h=0.48)
    callout(s, 0.45, 3.80, 6.1, 1.70, "El Request parece redundante", [
        "Si hay varios servidores, el **servidor** gana por prioridad.",
        "En un cliente que ya tiene dirección, el Request",
        "pide **renovar** la misma, y el tiempo se reinicia.",
        "Por eso renovar es más rápido que obtenerla por primera vez."], TEAL, 12)
    callout(s, 6.75, 3.80, 6.15, 1.85, "Los puertos que lo hacen funcionar", [
        "Cliente UDP **68**, servidor UDP **67**.",
        "El Offer del servidor va a .68 porque en ese",
        "momento el cliente aún no tiene IP.",
        "El Discover va a 255.255.255.255: aún no hay IP,",
        "así que no puede usar un unicast."], NAVY, 12)
    callout(s, 0.45, 5.75, 12.4, 1.25, "Dónde ver cada paso en Packet Tracer", [
        "Abrir **Simulation** (Alt+Shift+S), poner un filtro por protocolo `bootpc`/`DHCP` y ver las 4 ventanas.",
        "El paso 1 y el 3 salen del PC; el 2 y el 4, del router. El nombre de la "
        "pestaña de cada mensaje lleva el paso: DORA."], ORANGE, 12.5)
    notes(s, "⏱ 37-39 min.\n\n"
             "El DORA es lo que hace 'mágico' al DHCP. Merece la pena escribir las\n"
             "iniciales en la pizarra antes de continuar.\n"
             "\n"
             "El Request no es redundante: es el que impide que dos servidores den la\n"
             "misma IP y el que sirve para renovar.\n"
             "\n"
             "Si piden ver el tráfico, esto es lo que hacen en la Sesión A con Simulation.")

    # ================================================================ 4.3 pool
    n += 1
    s = content(prs, "El pool y sus exclusiones", "Qué define el bloque `ip dhcp pool`", PART, n + 1)
    text(s, 0.45, 1.32, 12.4, 0.35, "Cada router define un pool para **su** LAN. El de LAN-B, en el router R2:", size=13.5)
    code(s, 0.45, 1.75, 6.0, 2.35,
         [("R2(config)# ip dhcp pool LAN_B", ORANGE),
          ("R2(dhcp-config)# network 192.168.2.16 255.255.255.240", GRAY),
          ("R2(dhcp-config)# default-router 192.168.2.17", GRAY),
          ("R2(dhcp-config)# dns-server 8.8.8.8", GRAY),
          ("R2(dhcp-config)# domain-name lab-utp.pa", GRAY),
          ("R2(dhcp-config)# exit", GRAY)], 10.5)
    code(s, 6.85, 1.75, 6.05, 2.35,
         [("R2(config)# ip dhcp excluded-address", ORANGE),
          ("          192.168.2.17 192.168.2.21", GRAY),
          ("R2(config)# interface gi0/0", GRAY),
          ("R2(config-if)# ip address 192.168.2.17 255.255.255.240", GRAY),
          ("R2(config-if)# no shutdown", GRAY),
          ("R2(config-if)# exit", GRAY)], 10.5)
    table(s, [["Línea", "Significado", "Paquete"],
              ["network ... máscara", "Qué subred se reparte", "—"],
              ["default-router", "La puerta de salida (opción 3)", "DHCP Discover"],
              ["dns-server", "A quién pregunta por nombres", "DHCP Discover"],
              ["domain-name", "El dominio que se registra", "DHCP Discover"],
              ["excluded-address", "Qué direcciones NO se entregan", "—"]],
          0.45, 4.30, 12.4, col_w=[3.4, 5.6, 3.4], size=12, row_h=0.30)
    callout(s, 0.45, 6.25, 12.4, 0.80, "El rango que se entrega en LAN-B", [
        "De `.22` a `.30`. Se excluye `.17` (gateway, opción 3) y `.18` a `.21` (reservadas). "
        "Por eso el `show ip dhcp binding` debe mostrar leases **.22 – .30**."], GREEN, 12.5)
    notes(s, "⏱ 39-42 min.\n\n"
             "El error clásico aquí es olvidar las exclusiones: el servidor entrega .17\n"
             "y el PC se queda con la IP del gateway.\n"
             "\n"
             "Otra confusión: la opción 3 (default-router) **no** es una IP de la LAN,\n"
             "es la dirección del propio router, y por eso se excluye del pool.\n"
             "\n"
             "Aquí se ve por qué las excluidas van de .17 a .21 y no solo .17: en el\n"
             "lab se reservan las 5 IPs para los PCs de configuración fija.")

    # ================================================================ DIV 5
    s = divider(prs, "5", "Enrutamiento", "Cómo sabe el router por dónde enviar un paquete",
                ["La tabla de enrutamiento y sus códigos",
                 "Rutas estáticas y siguiente salto",
                 "Por qué el ping necesita ruta de vuelta",
                 "OSPF, RIPv2 y la redundancia de la malla"], "14 min")
    notes(s, "⏱ 42-43 min · Transición.\n\n"
             "Último bloque y el más largo. Es donde se une todo: las subredes del\n"
             "bloque 2 se conectan entre sí con las rutas de este bloque.\n"
             "\n"
             "La pregunta que abre el bloque: si R1 no tiene ruta hacia 192.168.2.32,\n"
             "¿qué hace con un paquete que llega para esa red?")

    # ================================================================ 5.1 tabla
    n += 1
    s = content(prs, "La tabla de enrutamiento", "La lista que el router consulta en cada paquete", PART, n + 1)
    text(s, 0.45, 1.32, 12.4, 0.35, "Cada línea dice: **a qué red** llego, **por qué interfaz** salgo, **a qué dirección** entrego.", size=13.5)
    table(s, [["Código", "Significa", "Cómo llegó a la tabla", "Ejemplo en el lab"],
              ["C", "Conectada (directly connected)", "Se crea sola al configurar `ip address`", "192.168.2.0/28 en Gi0/0"],
              ["L", "Local", "Se crea sola, es la IP del propio router", "192.168.2.1/32"],
              ["S", "Estática", "Alguien la escribió a mano con `ip route`", "S 192.168.2.32/28 via .49"],
              ["O", "OSPF", "Aprendida de los vecinos por multicast", "O 192.168.2.32/28 via .58"],
              ["R", "RIP", "Aprendida de los vecinos por broadcast", "R 192.168.2.32/28 via .58"]],
          0.45, 1.72, 12.4, col_w=[1.0, 3.0, 4.6, 3.8], size=11.5, row_h=0.42)
    callout(s, 0.45, 4.28, 6.1, 1.65, "Cómo decide el router", [
        "1. Mira la **más específica** que coincide: /28 gana sobre /24.",
        "2. Si hay empate, elige la de **menor distancia administrativa**.",
        "3. Si sigue el empate, la de **menor costo**.",
        "4. El resto se descarta: la red se descarta."], ORANGE, 12)
    callout(s, 6.75, 4.28, 6.15, 1.65, "La distancia administrativa", [
        "El número que dice cuán creíble es cada fuente:",
        "Estática = **1** (la que el admin escribió, siempre gana).",
        "OSPF = **110**, RIP = **120**.",
        "Por eso, si dejaste la estática, **OSPF no se usará** aunque R2 ya sepa la ruta."], RED, 12)
    callout(s, 0.45, 6.02, 12.4, 0.95, "La diferencia entre C y L, que confunde siempre", [
        "`C` es la **subred** completa que la interfaz sirve (192.168.2.0/28).",
        "`L` es la **dirección propia** del router en esa interfaz (192.168.2.1/32), la que responde a los pings locales."], TEAL, 12.5)
    notes(s, "⏱ 43-45 min.\n\n"
             "La tabla de enrutamiento es el 'show ip route' que van a leer mil veces.\n"
             "Enseñarlo ahora, antes de las rutas, evita que sea un bloque de letras.\n"
             "\n"
             "El punto de la distancia administrativa es importante: explica por qué en\n"
             "la Sesión B, si la estática sigue puesta, la ruta que se ve en el ping\n"
             "puede no ser la de OSPF.\n"
             "\n"
             "C vs L: la analogía útil es que C es la dirección de la calle y L es tu\n"
             "número de casa en esa calle.")

    # ================================================================ 5.2 estáticas
    n += 1
    s = content(prs, "Rutas estáticas", "Tres partes, y la tercera es la que se olvida", PART, n + 1)
    code(s, 0.45, 1.35, 12.4, 1.15,
         [("R1(config)# ip route 192.168.2.32 255.255.255.240 192.168.2.49", ORANGE),
          ("                          red de destino        máscara        siguiente salto", GRAY)], 12)
    text(s, 0.45, 2.55, 12.4, 0.35, "Las tres partes de una ruta estática", size=15, color=NAVY, bold=True)
    table(s, [["Parte", "Qué es", "Qué pasa si te equivocas"],
              ["Red de destino", "La red que quieres alcanzar", "Alcanzas la red equivocada o nada"],
              ["Máscara", "Cuántos bits son red", "Con máscara incorrecta no hay coincidencia"],
              ["Siguiente salto", "La IP del **router vecino**", "Sin ruta hacia él: no se puede entregar"]],
          0.45, 2.95, 12.4, col_w=[2.7, 4.6, 5.1], size=12.5, row_h=0.42)
    callout(s, 0.45, 4.60, 12.4, 1.45, "El requisito invisible: el siguiente salto debe ser alcanzable", [
        "Un router **no** puede enviar a una dirección que no ve en su tabla.",
        "El siguiente salto tiene que estar en una red conectada (código C) del router.",
        "Ejemplo: en R1, `.49` es alcanzable porque está en 192.168.2.48/30, que es C.",
        "Por eso los enlaces del lab son /30 y no /28: así cada vecino es alcanzable."], ORANGE, 12.5)
    code(s, 0.45, 6.10, 12.4, 0.95,
         [("R1# show ip route static        R1# show ip route 192.168.2.32", GRAY)], 11.5)
    notes(s, "⏱ 45-48 min.\n\n"
             "El error número uno de la Sesión A: poner la IP de destino como siguiente\n"
             "salto, o poner una IP que no está conectada.\n"
             "\n"
             "Si el siguiente salto no está en una red conectada, el IOS acepta el\n"
             "comando pero la ruta no se puede usar (sale como 'no next hop').\n"
             "\n"
             "La analogía del siguiente salto: no es el destino final, es a quién le\n"
             "entrego el paquete para que llegue más cerca del destino.")

    # ================================================================ 5.3 ida y vuelta
    n += 1
    s = content(prs, "Ping: necesita ruta de ida y de vuelta", "El error más costoso del laboratorio", PART, n + 1)
    text(s, 0.45, 1.35, 12.4, 0.35, "Un paquete que llega y **no se devuelve** se pierde igual. El ping solo tiene éxito si ambos caminos existen.", size=14)
    table(s, [["Sentido", "R1 necesita", "R2 necesita", "Si falta"],
              ["PC-A (LAN-A) → PC-B (LAN-B)", "S → LAN-B via .49", "C → LAN-A (ya conectada)", "R1 no sabe salir"],
              ["PC-B (LAN-B) → PC-A (LAN-A)", "C → LAN-B (ya conectada)", "S → LAN-A via .50", "R2 no sabe volver"],
              ["Si solo hay una de las dos", "—", "—", "Se queda en **0 replies**"]],
          0.45, 1.80, 12.4, col_w=[3.9, 3.4, 3.4, 1.7], size=11.5, row_h=0.46)
    callout(s, 0.45, 3.65, 12.4, 1.85, "La trampa: la tabla parece correcta y aun así no hay respuesta", [
        "Cada router por separado **sí** tiene la ruta de salida hacia el otro.",
        "Falta la de vuelta: el paquete llega al destino, pero el destino no sabe",
        "regresar. El ping se ve como «timeout» aunque la ruta de ida exista.",
        "Por eso el `ping` de verificación se hace **desde el router**, con la IP de la",
        "interfaz de salida, no solo desde el PC."], RED, 12)
    callout(s, 0.45, 5.55, 12.4, 1.50, "El ping que sí prueba el camino completo", [
        "**ping desde el PC** de origen hacia el PC destino: prueba ida y vuelta.",
        "**ping desde el router** con su IP de salida: prueba solo la ruta de ese router.",
        "Si el ping desde el router funciona pero el del PC no, el problema está en el **PC** (IP o gateway mal).",
        "Si ninguno de los dos funciona, el problema está en las **rutas**."], GREEN, 12)
    notes(s, "⏱ 48-50 min.\n\n"
             "Este es el error más caro del lab porque la tabla parece correcta.\n"
             "\n"
             "Diagnóstico: si el ping al gateway propio funciona pero al otro lado no,\n"
             "es un problema de rutas, no de la IP del PC.\n"
             "\n"
             "El ping con IP de origen es el comando clave: 'ping 192.168.2.33' desde\n"
             "R1, no desde el PC.")

    # ================================================================ 5.4 OSPF
    n += 1
    s = content(prs, "OSPF: los routers se cuentan entre sí", "De estáticas a dinámico", PART, n + 1)
    table(s, [["Concepto", "Qué es", "En el lab"],
              ["Link-state", "Cada router anuncia qué redes tiene conectadas", "R1 anuncia sus 3 subredes"],
              ["Área (area)", "Grupo de routers que comparten LSDB. El área 0 es la **backbone**", "Los 3 routers en área 0"],
              ["Router ID", "Identificador único (un IP). Se elige con `router-id`", "R1=.1, R2=.17, R3=.33"],
              ["LSDB", "La base de datos con todas las redes conocidas", "`show ip ospf database`"],
              ["SPF", "Algoritmo (Dijkstra) que calcula el camino más corto", "Calcula la ruta de menor costo"],
              ["Hellos", "Paquetes cada 10 s para saber si el vecino sigue vivo", "`show ip ospf neighbor`"],
              ["Estado FULL", "Los dos vecinos se reconhecieron", "Debe verse FULL en los 3"],
              ["Passive", "La interfaz anuncia la red pero **no** manda hellos", "Gi0/0 de cada router es pasiva"]],
          0.45, 1.40, 12.4, col_w=[1.9, 6.4, 4.1], size=12, row_h=0.42)
    callout(s, 0.45, 5.20, 6.1, 1.80, "Por qué pasiva la interfaz de la LAN", [
        "Gi0/0 de cada router va al switch de su LAN, donde están los **3 PCs**.",
        "Si la interfaz mandara hellos, los PCs recibirían paquetes OSPF",
        "que no entienden y la red se inundaría.",
        "`passive-interface` anuncia la red pero silencia el hello: es lo correcto."], TEAL, 12)
    callout(s, 6.75, 5.20, 6.15, 1.80, "Qué se gana con OSPF en este lab", [
        "Los 3 routers **aprendan** las rutas de los otros, no hay que escribirlas.",
        "Si un enlace cae, se recalcula y el tráfico va por el otro.",
        "`show ip ospf neighbor` debe dar 3 vecinos FULL.",
        "En la Sesión B se quita una estática y se ve la ruta OSPF (`O`)."], GREEN, 12)
    notes(s, "⏱ 50-53 min.\n\n"
             "OSPF es el bloque más denso. No entrar en detalle de tipos de router ni\n"
             "estados exentos: basta con link-state + área 0 + SPF.\n"
             "\n"
             "El router-id es fijo en el lab (1, .17, .33) porque si no lo fijamos, IOS\n"
             "lo elige solo y puede cambiar entre reinicios.\n"
             "\n"
             "Passive-interface: el error típico es ponerlo en las interfaces de los\n"
             "enlaces entre routers, que entonces no se vecindan.")

    # ================================================================ 5.5 RIP
    n += 1
    s = content(prs, "RIPv2 y el resumen automático", "El protocolo más simple, y su trampa clásica", PART, n + 1)
    text(s, 0.45, 1.32, 12.4, 0.35, "RIP es distance-vector: cada router cuenta saltos hasta la red y comparte el contador.", size=13.5)
    code(s, 0.45, 1.75, 12.4, 1.45,
         [("R1(config)# router rip", ORANGE),
          ("R1(config-router)# version 2", GRAY),
          ("R1(config-router)# network 192.168.2.0", GRAY),
          ("R1(config-router)# no auto-summary", ORANGE)], 11.5)
    callout(s, 0.45, 3.30, 6.1, 1.85, "Por qué `no auto-summary` no es opcional aquí", [
        "Con VLSM en la red, el resumen automático **manda 192.168.2.0/24**",
        "en lugar de las subredes correctas.",
        "El vecino recibe una ruta que no corresponde y descarta la información real.",
        "Con `no auto-summary` se difunden las subredes con su máscara real.",
        "Es uno de los errores clásicos del protocolo RIP con VLSM."], RED, 12)
    callout(s, 6.75, 3.30, 6.15, 1.85, "Limitaciones de RIP", [
        "Máximo **15 saltos**: a partir de ahí la red es inalcanzable.",
        "Métrica por saltos, no por ancho de banda real.",
        "Converge lento (30 s por defecto) frente a OSPF.",
        "En el lab se usa para **comparar**, no para producción."], NAVY, 12)
    text(s, 0.45, 5.22, 12.4, 0.32, "OSPF frente a RIP en este mismo laboratorio", size=15, color=NAVY, bold=True)
    table(s, [["", "RIPv2", "OSPF"],
              ["Tipo", "distance-vector", "link-state"],
              ["Métrica", "saltos (≤ 15)", "costo por ancho de banda"],
              ["Convergencia", "lenta", "rápida"],
              ["VLSM", "con `no auto-summary`", "nativo"]],
          0.45, 5.58, 12.4, col_w=[2.6, 4.9, 4.9], size=11.5, row_h=0.27)
    notes(s, "⏱ 53-55 min.\n\n"
             "No hace falta dominar RIP: la idea es comparar y ver por qué OSPF es el\n"
             "que se usa en el lab.\n"
             "\n"
             "El error de auto-summary solo aparece cuando hay VLSM. Como el lab usa\n"
             "VLSM justamente, es el caso donde hay que verlo.")

    # ================================================================ 5.6 redundancia
    n += 1
    s = content(prs, "Redundancia: qué pasa cuando algo falla", "La malla se diseñó para esto", PART, n + 1)
    text(s, 0.45, 1.35, 12.4, 0.35, "Con la malla completa, cada par de LANs tiene **dos caminos**. Esto es lo que se demuestra al final.", size=14)
    table(s, [["Fallo", "Con rutas estáticas", "Con OSPF"],
              ["Caen Gi0/1 de R1 (enlace R1–R2)", "El tráfico muere hasta arreglarlo", "Se recalcula y va por R1–R3–R2"],
              ["Cae un switch (SW2)", "Esa LAN desaparece; las otras siguen", "Igual: solo cae esa LAN"],
              ["Se borra una estática", "Se pierde esa ruta al instante", "OSPF mantiene la ruta aprendida"],
              ["Vuelve el enlace", "Manual: rehacer la ruta", "Automático, recalcula"]],
          0.45, 1.80, 12.4, col_w=[4.4, 4.0, 4.0], size=12, row_h=0.46)
    callout(s, 0.45, 4.20, 12.4, 1.60, "La demostración de la Sesión B, en orden", [
        "1. `show ip ospf neighbor` → los 3 vecinos en **FULL**.",
        "2. Borrar la ruta estática a LAN-C en R1 → el ping **sigue** funcionando.",
        "3. `show ip route` → la ruta a LAN-C ahora aparece con código **O**, no S.",
        "4. Apagar un enlace → el tráfico sigue por el camino que queda."], ORANGE, 12.5)
    callout(s, 0.45, 5.90, 12.4, 1.05, "El mensaje que hay que llevarse", [
        "Las rutas estáticas no tienen «plan B»: si una falta, el tráfico se cae.",
        "Un protocolo dinámico es lo que hace que la topología de malla sirva de algo."], GREEN, 12.5)
    notes(s, "⏱ 55-57 min.\n\n"
             "Esta diapositiva es el puente directo con la Sesión B: los 4 pasos son\n"
             "literalmente lo que se hace al final del laboratorio.\n"
             "\n"
             "El paso 2 es el que convence: si el ping sigue funcionando sin la\n"
             "estática, es porque OSPF ya tenía esa ruta aprendida.\n"
             "\n"
             "Aviso: si el ping falla en el paso 2, es que OSPF no converge. Revisar\n"
             "network, router-id y que los 3 estén en área 0.")

    # ================================================================ 5.7 verificación
    n += 1
    s = content(prs, "Verificar es parte de la teoría", "Cada comando responde una pregunta concreta", PART, n + 1)
    table(s, [["Comando", "Pregunta que responde", "Qué debe verse"],
              ["show ip interface brief", "¿La interfaz está up?", "Gi0/0 up/up, Gi0/1 up/up"],
              ["show ip route", "¿Por dónde sale el tráfico?", "C para las 3 subredes + S (u O)"],
              ["show ip dhcp binding", "¿A quién se le entregó una IP?", "Leases .22 – .30 en LAN-B"],
              ["show ip dhcp server statistics", "¿Cuántos DORA hubo?", "DISCOVER, OFFER, REQUEST, ACK"],
              ["show ip arp", "¿Quién está en mi LAN?", "IP ↔ MAC de los vecinos"],
              ["show ip ospf neighbor", "¿Se conocen los routers?", "3 vecinos en estado FULL"],
              ["show ip route ospf", "¿Qué rutas aprendió OSPF?", "Rutas con código O"],
              ["show ip protocols", "¿Qué protocolos corren?", "OSPF en área 0, RIP si aplica"]],
          0.45, 1.40, 12.4, col_w=[4.7, 4.1, 3.6], size=11.5, row_h=0.44)
    callout(s, 0.45, 5.40, 12.4, 1.55, "La pregunta que hace el diagnóstico correcto", [
        "Antes de cambiar nada: **¿en qué capa está el problema?**",
        "Interfaz down → capa 1/2 (cable, `no shutdown`).",
        "Sin IP o 169.254 → capa 2 (DHCP no respondió, o falta `ip address`).",
        "Con IP pero sin ruta → capa 3 (falta `ip route`, o falta la ruta de vuelta)."], ORANGE, 12.5)
    notes(s, "⏱ 57-58 min.\n\n"
             "Esta tabla es el índice del COMANDOS.md. Decirla de memoria es mejor que\n"
             "recitarla.\n"
             "\n"
             "El enfoque de capas es lo que más rinde en el laboratorio: evita cambiar\n"
             "cosas al azar. Interface down no se arregla con una ruta.")

    # ================================================================ 5.8 límites PT
    n += 1
    s = content(prs, "Los límites de Packet Tracer 9.0.1", "Lo que la herramienta no hace", PART, n + 1)
    table(s, [["Lo que quieres", "Qué hace PT 9.0.1", "Solución en el lab"],
              ["`lease 7 8 23`", "**No existe** en el IOS de PT", "Se omite; el lease por defecto es 1 día"],
              ["Dos `dns-server`", "Solo acepta **uno**", "`dns-server 8.8.8.8`"],
              ["`ip helper-address`", "**No implementado**", "Cada router sirve **su** LAN (3 pools)"],
              ["Ripv2 con VLSM", "Requiere `no auto-summary` explícito", "Se incluye en la config"],
              ["Comando existencial", "El IOS de PT acepta `?` para=listar", "Úsalo si dudas"]],
          0.45, 1.40, 12.4, col_w=[3.5, 4.3, 4.6], size=11.5, row_h=0.44)
    callout(s, 0.45, 4.08, 12.4, 1.35, "Por qué `ip helper-address` cambia el diseño", [
        "Un router con esa orden puede servir DHCP para redes a las que no está conectado.",
        "Como PT no lo implementa, el laboratorio usa **3 servidores DHCP** en vez de uno.",
        "Es una limitación del simulador: en un router real, un solo servidor central bastaría."], ORANGE, 12.5)
    callout(s, 0.45, 5.52, 12.4, 1.40, "La regla de oro con Packet Tracer", [
        "Si un comando no existe, el propio simulador lo dice: el prompt `?` lista lo válido.",
        "No copies comandos de un libro sin verificarlos: las versiones del IOS cambian.",
        "La configuración del lab está en `config/R1.txt`, `R2.txt` y `R3.txt`, ya validadas."], TEAL, 12.5)
    notes(s, "⏱ 58-59 min.\n\n"
             "Esta diapositiva es el puente con la práctica: lo que se ve en la Sesión A\n"
             "tiene que coincidir con esta tabla, o el comando se va a rechazar.\n"
             "\n"
             "El uso de ? es el mejor hábito: si un comando falla, no es que esté mal\n"
             "escrito, es que no existe en esa versión.")

    # ================================================================ 5.9 checklist
    n += 1
    s = content(prs, "Checklist del laboratorio", "Todo lo teórico, en orden de ejecución", PART, n + 1)
    table(s, [["#", "Paso", "Bloque", "Qué debe pasar"],
              ["1", "Verificar VLSM antes de configurar", "2", "Las 6 subredes, alineadas y sin solapes"],
              ["2", "Cablear: 15 cables rectos", "3", "Cables rojos hasta hacer `no shutdown`"],
              ["3", "`no shutdown` en las 3 Gi", "3", "Las luces pasan a verde"],
              ["4", "`ip address` en cada interfaz", "1", "Aparecen las rutas C en `show ip route`"],
              ["5", "`ip dhcp pool` + excluded en cada router", "4", "3 pools, uno por LAN"],
              ["6", "`ipconfig /renew` en los PCs", "4", "Leases .22 – .30 en LAN-B"],
              ["7", "Ping al gateway y a la otra LAN", "5", "Ida y vuelta en ambos sentidos"],
              ["8", "Rutas estáticas hacia la tercera LAN", "5", "Los 3 se alcanzan entre sí"],
              ["9", "OSPF área 0 + router-id", "5", "3 vecinos FULL"],
              ["10", "Borrar una estática y reintentar", "5", "El ping sigue, ahora por OSPF"]],
          0.45, 1.40, 12.4, col_w=[0.6, 4.4, 1.1, 6.3], size=11.5, row_h=0.40)
    callout(s, 0.45, 5.90, 12.4, 1.05, "El orden importa más de lo que parece", [
        "No se puede hacer DHCP sin la interfaz configurada (paso 4 antes de 5).",
        "Y no se puede enrutar sin VLSM calculado (paso 1 antes de 8)."], NAVY, 12.5)
    notes(s, "⏱ 59-60 min · Cierre.\n\n"
             "Usar como índice del laboratorio. Cada fila corresponde a un bloque de la\n"
             "teoría que ya se dio.\n"
             "\n"
             "El paso 7 (ping) y el paso 10 (borrar la estática) son los que más\n"
             "diagnostican. Si algo falla, volver a la tabla de verificación.")

    # ================================================================ cierre
    n += 1
    s = content(prs, "Repaso: lo que hay que saber", "Cinco ideas y las cinco preguntas que dejan", PART, n + 1)
    callout(s, 0.45, 1.40, 12.4, 2.6, "Las 5 ideas", [
        [("1. ", {"color": ORANGE, "bold": True, "size": 13}),
         ("La máscara decide el reparto red/host; la IP sola no dice nada. /28 son 14 útiles, /30 son 2.", {"size": 13})],
        [("2. ", {"color": ORANGE, "bold": True, "size": 13}),
         ("VLSM da a cada subred la máscara que necesita: /28 para las LAN, /30 para los enlaces.", {"size": 13})],
        [("3. ", {"color": ORANGE, "bold": True, "size": 13}),
         ("El switch reenvía por MAC, el router por IP. ARP traduce IP→MAC solo dentro de la red.", {"size": 13})],
        [("4. ", {"color": ORANGE, "bold": True, "size": 13}),
         ("DHCP reparte por DORA, con gateway y DNS; se excluye el .1 del pool.", {"size": 13})],
        [("5. ", {"color": ORANGE, "bold": True, "size": 13}),
         ("El router elige ruta: la más específica y la de menor distancia. OSPF aprende y recalcula.", {"size": 13})]], NAVY, 13)
    text(s, 0.45, 4.30, 12.4, 0.35, "Las 5 preguntas para comprobar que se entendió", size=15, color=NAVY, bold=True)
    callout(s, 0.45, 4.75, 12.4, 2.0, "", [
        [("1. ", {"color": ORANGE, "bold": True, "size": 12.5}),
         ("¿Por qué un /28 da 14 hosts y no 16? ¿Qué dos direcciones se pierden?", {"size": 12.5})],
        [("2. ", {"color": ORANGE, "bold": True, "size": 12.5}),
         ("¿Por qué los enlaces entre routers son /30 y no /28 en este laboratorio?", {"size": 12.5})],
        [("3. ", {"color": ORANGE, "bold": True, "size": 12.5}),
         ("Un ping al gateway funciona pero a otra LAN no. ¿Qué capa revisarías primero?", {"size": 12.5})],
        [("4. ", {"color": ORANGE, "bold": True, "size": 12.5}),
         ("Un PC muestra 169.254.x.x. ¿Qué significa y dónde se mira?", {"size": 12.5})],
        [("5. ", {"color": ORANGE, "bold": True, "size": 12.5}),
         ("¿Qué cambia en la tabla de enrutamiento si borras una ruta estática que OSPF ya conoce?", {"size": 12.5})]], TEAL, 12.5)
    notes(s, "Cierre · Preguntas.\n\n"
             "Estas 5 preguntas cubren los 5 bloques. Si responden las 5, tienen la\n"
             "teoría suficiente para el laboratorio.\n"
             "\n"
             "La 3 y la 4 son las que más se confunden en la práctica: distinguen\n"
             "un problema de capa 2 de uno de capa 3.")

    prs.save(out)
    return out


if __name__ == "__main__":
    p = build(sys.argv[1] if len(sys.argv) > 1 else "Teoria-Lab-VLSM-DHCP.pptx")
    print("OK ->", p)
