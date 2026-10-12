# Diagramas del laboratorio (Mermaid para draw.io)

Topología, direccionamiento y flujos del laboratorio **VLSM, DHCP y
enrutamiento** en 3 sedes, listos para insertar en **draw.io**.

## Cómo usarlos en draw.io

Todos los bloques son **Mermaid estándar**, compatibles con el importador de
draw.io. El tipo de diagrama se detecta por la **primera palabra** del bloque
(`flowchart` o `sequenceDiagram`), así que copia siempre el bloque completo, con
su primera línea incluida.

Pasos para insertar uno:

1. Abre draw.io (app.diagrams.net o la app de escritorio).
2. **Arrange > Insert > Mermaid** (o el botón `+` de la barra de herramientas →
   **Mermaid**).
3. Copia el bloque del diagrama que quieras y pégalo en el cuadro de texto. En el
   desplegable inferior elige:
   - **Diagram** — lo convierte en formas nativas de draw.io: puedes recolorear,
     mover y seguir dibujando el lab encima (recomendado para el entregable).
   - **Image (SVG)** — inserta un solo objeto que conserva el código Mermaid;
     para re-editarlo, doble clic sobre la imagen.
4. Clic en **Insert**.

Los 11 diagramas son independientes: se pueden insertar todos en el mismo lienzo
y ordenarlos como láminas separadas. El **diagrama 7** (topología con VLANs) es
el indicado como base del entregable de la Sesión B.

| # | Diagrama | Tipo | Uso |
|---|----------|------|-----|
| 1 | Topología física completa | flowchart | Sesión A — interfaces y cables |
| 2 | Enlaces punto a punto y VLSM | flowchart | Sesión A — /30 y rutas estáticas |
| 3 | DHCP DORA | flowchart | Sesión A — negociación DHCP |
| 4 | Recorrido del paquete entre sedes | sequenceDiagram | Sesión A — ping PC-A1 → PC-C1 |
| 5 | Convergencia de OSPF | flowchart | Sesión B — vecindades de área 0 |
| 6 | Costes: primario vs respaldo | flowchart | Sesión B — `[110/2]` frente a `[110/102]` |
| 7 | Topología hub-and-spoke con VLANs | flowchart | Sesión B — base del entregable |
| 8 | La trampa del native VLAN | flowchart | Sesión B — gateway de la VLAN 10 |
| 9 | Router-on-a-stick | flowchart | Sesión B — subinterfaz `.20` |
| 10 | DHCP por VLAN | sequenceDiagram | Sesión B — pools VLAN 10 y 20 |
| 11 | Redundancia paso a paso | sequenceDiagram | Sesión B — prueba del respaldo |

> **Si draw.io reporta un error de parseo** (importadores antiguos): borra las
> líneas `classDef` y `class` del bloque —son **solo estilo**— y reintenta. Si aún
> falla, quita la línea `autonumber` en los `sequenceDiagram` y cambia las dobles
> flechas `<-->` por `---`.

---

## 1. Topología física completa (estilo Packet Tracer)

Los 3 routers en malla, cada uno con su switch y sus 3 PCs. Muestra qué interfaz
conecta con qué y la subred de cada enlace.

```mermaid
flowchart TB
  subgraph SA["SEDE A · LAN-A · 192.168.2.0/28"]
    A1["PC-A1<br/>192.168.2.6"]
    A2["PC-A2<br/>192.168.2.7"]
    A3["PC-A3<br/>192.168.2.8"]
    SWA["SW1 · 2960"]
    A1 --> SWA
    A2 --> SWA
    A3 --> SWA
  end

  subgraph SB["SEDE B · LAN-B · 192.168.2.16/28"]
    B1["PC-B1<br/>192.168.2.22"]
    B2["PC-B2<br/>192.168.2.23"]
    B3["PC-B3<br/>192.168.2.24"]
    SWB["SW2 · 2960"]
    B1 --> SWB
    B2 --> SWB
    B3 --> SWB
  end

  subgraph SC["SEDE C · LAN-C · 192.168.2.32/28"]
    C1["PC-C1<br/>192.168.2.38"]
    C2["PC-C2<br/>192.168.2.39"]
    C3["PC-C3<br/>192.168.2.40"]
    SWC["SW3 · 2960"]
    C1 --> SWC
    C2 --> SWC
    C3 --> SWC
  end

  R1(["R1 · Cisco 2911<br/>Gi0/0 = 192.168.2.1/28"])
  R2(["R2 · Cisco 2911<br/>Gi0/0 = 192.168.2.17/28"])
  R3(["R3 · Cisco 2911<br/>Gi0/0 = 192.168.2.33/28"])

  SWA -->|"Fa0/1 ↔ Gi0/0"| R1
  SWB -->|"Fa0/1 ↔ Gi0/0"| R2
  SWC -->|"Fa0/1 ↔ Gi0/0"| R3

  R1 <-->|"Gi0/1 192.168.2.49 ↔ Gi0/1 192.168.2.50<br/>192.168.2.48/30"| R2
  R2 <-->|"Gi0/2 192.168.2.53 ↔ Gi0/1 192.168.2.54<br/>192.168.2.52/30"| R3
  R3 <-->|"Gi0/2 192.168.2.57 ↔ Gi0/2 192.168.2.58<br/>192.168.2.56/30"| R1

  classDef router fill:#dbeafe,stroke:#1d4ed8,stroke-width:2px,color:#0b2559
  classDef switch fill:#dcfce7,stroke:#15803d,stroke-width:2px,color:#052e16
  classDef pc fill:#fef9c3,stroke:#a16207,stroke-width:1px,color:#422006
  class R1,R2,R3 router
  class SWA,SWB,SWC switch
  class A1,A2,A3,B1,B2,B3,C1,C2,C3 pc
```

## 2. Malla de enlaces punto a punto y subredes VLSM

Solo la capa 3 entre routers: cada `/30` con sus dos extremos y el siguiente salto
de cada ruta estática.

```mermaid
flowchart LR
  R1(["R1<br/>LAN-A .0/28"])
  R2(["R2<br/>LAN-B .16/28"])
  R3(["R3<br/>LAN-C .32/28"])

  R1 <-->|"Enlace 1<br/>192.168.2.48/30<br/>R1 Gi0/1 = .49<br/>R2 Gi0/1 = .50"| R2
  R2 <-->|"Enlace 2<br/>192.168.2.52/30<br/>R2 Gi0/2 = .53<br/>R3 Gi0/1 = .54"| R3
  R3 <-->|"Enlace 3<br/>192.168.2.56/30<br/>R3 Gi0/2 = .57<br/>R1 Gi0/2 = .58"| R1

  N1["Rutas de R1<br/>LAN-B .16/28 vía .50<br/>LAN-C .32/28 vía .57"]
  N2["Rutas de R2<br/>LAN-A .0/28 vía .49<br/>LAN-C .32/28 vía .54"]
  N3["Rutas de R3<br/>LAN-A .0/28 vía .58<br/>LAN-B .16/28 vía .53"]

  R1 --- N1
  R2 --- N2
  R3 --- N3

  LIBRE["192.168.2.60 – 192.168.2.255<br/>196 direcciones libres"]
  N1 --- LIBRE

  classDef router fill:#dbeafe,stroke:#1d4ed8,stroke-width:2px,color:#0b2559
  classDef nota fill:#f1f5f9,stroke:#475569,stroke-dasharray:4 3,color:#0f172a
  classDef libre fill:#f1f5f9,stroke:#94a3b8,stroke-dasharray:4 3,color:#334155
  class R1,R2,R3 router
  class N1,N2,N3 nota
  class LIBRE libre
```

## 3. DHCP DORA — cómo un PC obtiene su IP

Flujo completo de la negociación entre un PC de LAN-A y el servidor DHCP que es
el propio router R1.

```mermaid
flowchart LR
  PC["PC-A1<br/>sin dirección IP<br/>0.0.0.0"]
  R1(["R1 Gi0/0<br/>192.168.2.1/28<br/>servidor DHCP"])

  PC -->|"1 DISCOVER<br/>UDP 68 → 67<br/>destino 255.255.255.255"| R1
  R1 -->|"2 OFFER<br/>propone 192.168.2.6<br/>máscara 255.255.255.240"| PC
  PC -->|"3 REQUEST<br/>pide 192.168.2.6"| R1
  R1 -->|"4 ACK<br/>confirma .6<br/>gw .1 · DNS 8.8.8.8"| PC

  EXC["Excluidas del pool<br/>.1 gateway<br/>.2 – .5 IP fijas admin"]
  R1 --- EXC

  PC -->|"ipconfig /renew"| OK["IP 192.168.2.6/28<br/>GW 192.168.2.1<br/>DNS 8.8.8.8"]
  FALLA["Sin respuesta de R1<br/>queda en 169.254.x.x<br/>revisar Gi0/0 y el pool"]
  PC -.->|"ipconfig /renew sin OFFER"| FALLA

  classDef router fill:#dbeafe,stroke:#1d4ed8,stroke-width:2px,color:#0b2559
  classDef pc fill:#fef9c3,stroke:#a16207,color:#422006
  classDef ok fill:#dcfce7,stroke:#15803d,color:#052e16
  classDef fail fill:#fee2e2,stroke:#b91c1c,color:#450a0a
  classDef nota fill:#f1f5f9,stroke:#475569,stroke-dasharray:4 3,color:#0f172a
  class R1 router
  class PC pc
  class OK ok
  class FALLA fail
  class EXC nota
```

## 4. Recorrido de un paquete entre sedes

Traza de un `ping` de PC-A1 a PC-C1, que es el camino de 2 saltos directo de la
malla.

```mermaid
sequenceDiagram
  autonumber
  participant P as PC-A1<br/>192.168.2.6
  participant A as R1<br/>Gi0/0 192.168.2.1
  participant B as R3<br/>Gi0/2 192.168.2.57
  participant C as PC-C1<br/>192.168.2.38

  P->>A: echo request · destino 192.168.2.38
  Note over A: consulta su tabla y ve la ruta<br/>192.168.2.32/28 vía 192.168.2.57
  A->>B: reenvía · siguiente salto 192.168.2.57
  B->>C: entrega el ICMP en LAN-C
  C-->>B: echo reply
  B-->>A: reenvía la respuesta
  A-->>P: PING OK desde 192.168.2.38
```

## 5. Convergencia de OSPF (Sesión B)

Los 3 routers en área 0 intercambian hellos, sincronizan la LSDB y ejecutan el
algoritmo SPF. Con roles hub-and-spoke (R1 central, R2/R3 sucursales) y el
enlace R2↔R3 como respaldo de costo alto, un uplink caído se recorre solo.

```mermaid
flowchart LR
  R1(["R1 SEDE CENTRAL<br/>router ospf 10<br/>ID 192.168.2.1"])
  R2(["R2 SUCURSAL 1<br/>router ospf 10<br/>ID 192.168.2.17"])
  R3(["R3 SUCURSAL 2<br/>router ospf 10<br/>ID 192.168.2.33"])

  R1 <-->|"UPLINK SUC-1<br/>Gi0/1 .49 ↔ .50<br/>costo 1"| R2
  R2 <-->|"RESPALDO<br/>Gi0/2 .53 ↔ .54<br/>ip ospf cost 100"| R3
  R3 <-->|"UPLINK SUC-2<br/>Gi0/2 .57 ↔ .58<br/>costo 1"| R1

  DB[("LSDB común<br/>las 9 subredes de<br/>192.168.2.0/24")]
  R1 -->|"LSA"| DB
  R2 -->|"LSA"| DB
  R3 -->|"LSA"| DB

  DB --> SPF["Algoritmo SPF<br/>calcula la mejor ruta<br/>distancia administrativa 110"]
  SPF --> TABLA["show ip route<br/>marcas O · no hay S"]
  TABLA --> PC["PC-B1 ↔ PC-A1<br/>cruce entre sedes OK"]
  TABLA --> CORTE["Si R1 Gi0/1 baja<br/>SUC-1 sale por R2→R3→R1<br/>sin tocar nada"]

  classDef router fill:#dbeafe,stroke:#1d4ed8,stroke-width:2px,color:#0b2559
  classDef db fill:#ede9fe,stroke:#6d28d9,color:#2e1065
  classDef paso fill:#f1f5f9,stroke:#475569,color:#0f172a
  classDef ok fill:#dcfce7,stroke:#15803d,color:#052e16
  classDef warn fill:#fef3c7,stroke:#b45309,color:#451a03
  class R1,R2,R3 router
  class DB db
  class SPF,TABLA paso
  class PC ok
  class CORTE warn
```

## 6. Sesión B — costes OSPF: primario frente a respaldo

El tráfico de una sucursal a la central usa su uplink directo (costo bajo); el
enlace entre sucursales queda dormido (`ip ospf cost 100`) hasta que cae un
uplink. Comparación de costos vistos desde R2.

```mermaid
flowchart LR
  R2(["R2 · SUCURSAL 1<br/>Gi0/2 = .53/30 · costo 100"])

  R2 -->|"camino normal<br/>costo 1+1 = 2"| R1(["R1 · CENTRAL<br/>Gi0/1 = .49"])
  R2 -.->|"respaldo<br/>costo 100+1+1 = 102"| R3(["R3 · SUCURSAL 2<br/>Gi0/1 = .54"])

  R1 <-->|"costo 1"| R3
  R3 -->|"si el uplink SUC-1 cae:<br/>R2→R3→R1"| R1

  NORMAL["Estado normal<br/>SUC-1 → Central por R1 · [110/2]"]
  CORTE["R1 Gi0/1 en shutdown<br/>SUC-1 → Central por R3<br/>[110/102] via .54"]

  R1 --- NORMAL
  R3 -.- CORTE

  classDef router fill:#dbeafe,stroke:#1d4ed8,stroke-width:2px,color:#0b2559
  classDef ok fill:#dcfce7,stroke:#15803d,color:#052e16
  classDef warn fill:#fef3c7,stroke:#b45309,color:#451a03
  class R1,R2,R3 router
  class NORMAL ok
  class CORTE warn
```

## 7. Sesión B — topología hub-and-spoke con VLAN 10 y 20

La estructura física es la misma de siempre (15 cables), pero los roles cambian:
R1 es la **sede central**, R2 y R3 son sucursales con su uplink, y el enlace
R2↔R3 queda como respaldo de costo alto. Cada sitio se parte en VLAN 10
(usuarios) y VLAN 20 (invitados).

```mermaid
flowchart TB
  subgraph CEN["SEDE CENTRAL · R1"]
    A1["PC-A1 · VLAN 10 · .6"]
    A2["PC-A2 · VLAN 10 · .7"]
    A3["PC-A3 · VLAN 20 · .70"]
    SW1["SW1 · 2960"]
    A1 --> SW1
    A2 --> SW1
    A3 --> SW1
  end

  subgraph S1["SUCURSAL 1 · R2"]
    B1["PC-B1 · VLAN 10 · .22"]
    B2["PC-B2 · VLAN 10 · .23"]
    B3["PC-B3 · VLAN 20 · .86"]
    SW2["SW2 · 2960"]
    B1 --> SW2
    B2 --> SW2
    B3 --> SW2
  end

  subgraph S2["SUCURSAL 2 · R3"]
    C1["PC-C1 · VLAN 10 · .38"]
    C2["PC-C2 · VLAN 10 · .39"]
    C3["PC-C3 · VLAN 20 · .102"]
    SW3["SW3 · 2960"]
    C1 --> SW3
    C2 --> SW3
    C3 --> SW3
  end

  R1(["R1 · SEDE CENTRAL<br/>Gi0/0 = .1/28 (VLAN 10)<br/>Gi0/0.20 = .65/28 (VLAN 20)"])
  R2(["R2 · SUCURSAL 1<br/>Gi0/0 = .17/28 (VLAN 10)<br/>Gi0/0.20 = .81/28 (VLAN 20)"])
  R3(["R3 · SUCURSAL 2<br/>Gi0/0 = .33/28 (VLAN 10)<br/>Gi0/0.20 = .97/28 (VLAN 20)"])

  SW1 -->|"trunk Fa0/1<br/>native 10 · allowed 10,20"| R1
  SW2 -->|"trunk Fa0/1<br/>native 10 · allowed 10,20"| R2
  SW3 -->|"trunk Fa0/1<br/>native 10 · allowed 10,20"| R3

  R1 <-->|"UPLINK SUC-1<br/>192.168.2.48/30<br/>R1 Gi0/1 = .49 ↔ R2 Gi0/1 = .50"| R2
  R2 <-->|"RESPALDO<br/>192.168.2.52/30<br/>R2 Gi0/2 = .53 ↔ R3 Gi0/1 = .54<br/>costo 100"| R3
  R3 <-->|"UPLINK SUC-2<br/>192.168.2.56/30<br/>R3 Gi0/2 = .57 ↔ R1 Gi0/2 = .58"| R1

  classDef router fill:#dbeafe,stroke:#1d4ed8,stroke-width:2px,color:#0b2559
  classDef switch fill:#dcfce7,stroke:#15803d,stroke-width:2px,color:#052e16
  classDef pc fill:#fef9c3,stroke:#a16207,color:#422006
  class R1,R2,R3 router
  class SW1,SW2,SW3 switch
  class A1,A2,A3,B1,B2,B3,C1,C2,C3 pc
```

## 8. Sesión B — la trampa del native VLAN

La VLAN 10 viaja por el trunk **sin etiqueta** (es la nativa). Si no se fija,
la nativa por defecto es la VLAN 1 y el gateway de `Gi0/0` cae en una subred que
no existe: los PCs de la VLAN 10 no ven su ruteador.

```mermaid
flowchart TB
  R1(["R1 Gi0/0<br/>IP 192.168.2.1/28<br/>tramas de la VLAN 10 SIN etiqueta"])
  SW["SW1 · Fa0/1<br/>switchport mode trunk"]

  R1 --> SW

  SW -->|"native por defecto = VLAN 1"| MAL["✗ Tramas sin etiqueta → VLAN 1<br/>subred inexistente en el plan<br/>PCs de VLAN 10 NO ven su gateway"]
  SW -->|"switchport trunk native vlan 10"| BIEN["✓ Tramas sin etiqueta → VLAN 10<br/>coincide con Gi0/0 (.1/28)<br/>PCs de VLAN 10 ven su gateway"]

  classDef router fill:#dbeafe,stroke:#1d4ed8,stroke-width:2px,color:#0b2559
  classDef mal fill:#fee2e2,stroke:#b91c1c,color:#450a0a
  classDef ok fill:#dcfce7,stroke:#15803d,color:#052e16
  class R1 router
  class MAL mal
  class BIEN ok
```

## 9. Sesión B — router-on-a-stick

Un solo cable entre cada router y su switch transporta las dos VLAN: la física
`Gi0/0` es el gateway de la VLAN 10 y la subinterfaz `Gi0/0.20` el de la 20.

```mermaid
flowchart LR
  subgraph R1BOX["R1 · SEDE CENTRAL"]
    G0["Gi0/0 física<br/>192.168.2.1/28<br/>gateway VLAN 10 · sin etiqueta"]
    G20["Gi0/0.20 subinterfaz<br/>encapsulation dot1Q 20<br/>192.168.2.65/28<br/>gateway VLAN 20"]
  end
  SW["SW1 · Fa0/1 trunk<br/>native vlan 10 · allowed 10,20"]
  P10["PC-A1 · .6 · PC-A2 · .7<br/>VLAN 10"]
  P20["PC-A3 · .70<br/>VLAN 20"]

  P10 --> SW
  P20 --> SW
  SW -->|"VLAN 10 sin etiqueta"| G0
  SW -->|"VLAN 20 etiqueta 802.1Q"| G20

  classDef router fill:#dbeafe,stroke:#1d4ed8,color:#0b2559
  classDef sub fill:#ede9fe,stroke:#6d28d9,color:#2e1065
  class G0 router
  class G20 sub
```

## 10. Sesión B — DHCP por VLAN

El mismo router sirve dos subredes porque tiene dos IP: el pool de la VLAN 10 y
el de la VLAN 20. Ejemplo con la sede central.

```mermaid
sequenceDiagram
  autonumber
  participant P10 as PC-A1<br/>VLAN 10
  participant P20 as PC-A3<br/>VLAN 20
  participant R1 as R1 · CENTRAL<br/>Gi0/0 .1/28 + Gi0/0.20 .65/28

  P10->>R1: DISCOVER · broadcast 255.255.255.255
  R1-->>P10: OFFER 192.168.2.6/28 · GW .1
  P10->>R1: REQUEST 192.168.2.6
  R1-->>P10: ACK ✓

  P20->>R1: DISCOVER
  R1-->>P20: OFFER 192.168.2.70/28 · GW .65
  P20->>R1: REQUEST 192.168.2.70
  R1-->>P20: ACK ✓

  Note over R1: pool LAN-CENTRAL → .6-.14<br/>pool VLAN20-CENTRAL → .70-.78
```

## 11. Sesión B — la prueba de redundancia paso a paso

Con el uplink de la sucursal 1 caído, el tráfico de PC-B1 a la central sale por
el respaldo (R2→R3→R1). OSPF recalculó solo.

```mermaid
sequenceDiagram
  autonumber
  participant B as PC-B1 · SUC-1<br/>192.168.2.22
  participant R2 as R2 · SUC-1
  participant R3 as R3 · SUC-2
  participant R1 as R1 · CENTRAL
  participant A as PC-A1 · Central<br/>192.168.2.6

  Note over R2: ruta a la central [110/2] via .49 (uplink)
  B->>R2: ping 192.168.2.6
  R2->>R1: vía 192.168.2.49 (costo 1)
  R1-->>A: entrega en VLAN 10
  A-->>B: echo reply ✓

  Note over R1: shutdown Gi0/1 ✂ cae el uplink de SUC-1
  Note over R2: OSPF recalcula → [110/102] via .54
  B->>R2: ping 192.168.2.6 (sigue)
  R2->>R3: vía 192.168.2.53 → .54 (respaldo, costo 100)
  R3->>R1: vía 192.168.2.57 → .58 (uplink SUC-2)
  R1-->>A: entrega en VLAN 10
  A-->>B: echo reply ✓
```

---

## Resumen del plan (para rotular a mano en el diagrama)

| Subred | Uso | Prefijo | Gateway | Rango DHCP | Broadcast |
|--------|-----|---------|---------|-----------|-----------|
| 192.168.2.0/28 | Central · VLAN 10 (usuarios) | 255.255.255.240 | .1 | .6 – .14 | .15 |
| 192.168.2.16/28 | SUC-1 · VLAN 10 | 255.255.255.240 | .17 | .22 – .30 | .31 |
| 192.168.2.32/28 | SUC-2 · VLAN 10 | 255.255.255.240 | .33 | .38 – .46 | .47 |
| 192.168.2.48/30 | Uplink SUC-1 · R1 ↔ R2 | 255.255.255.252 | — | — | .51 |
| 192.168.2.52/30 | Respaldo · R2 ↔ R3 | 255.255.255.252 | — | — | .55 |
| 192.168.2.56/30 | Uplink SUC-2 · R3 ↔ R1 | 255.255.255.252 | — | — | .59 |
| 192.168.2.64/28 | Central · VLAN 20 (invitados) | 255.255.255.240 | .65 | .70 – .78 | .79 |
| 192.168.2.80/28 | SUC-1 · VLAN 20 | 255.255.255.240 | .81 | .86 – .94 | .95 |
| 192.168.2.96/28 | SUC-2 · VLAN 20 | 255.255.255.240 | .97 | .102 – .110 | .111 |

> Los diagramas 1-4 reflejan la **Sesión A** (malla equivalente, 3 LAN, fases
> estática/OSPF). Los diagramas **5-11** son de la **Sesión B** (laboratorio
> independiente): el 5-6 muestran la convergencia y los costes OSPF, y el 7-11 el
> resto de la sesión — topología hub-and-spoke con VLANs, la trampa del native,
> router-on-a-stick, DHCP por VLAN y la prueba de redundancia. La estructura
> física y las IPs son las mismas; cambian los roles y el uso de cada enlace.