# Diagramas del laboratorio (Mermaid para draw.io)

Topología, direccionamiento y flujos del laboratorio **VLSM, DHCP y
enrutamiento** en 3 sedes, listos para insertar en **draw.io**.

## Cómo usarlos en draw.io

1. Abre draw.io (diagram.net) → **Arrange > Insert > Mermaid**
   (o el botón `+` de la barra → **Mermaid**).
2. Copia el bloque `mermaid` de este archivo y pégalo en el cuadro de texto.
3. En la lista inferior deja la opción **Diagram** (convierte a formas nativas de
   draw.io editables) o **Image** (SVG único).
4. Clic en **Insert**.

Para volver a editar el código: selecciona el grupo contenedor Mermaid y pulsa
**Enter** (o el icono del lápiz).

> Si tu versión de draw.io reporta un error de parseo al insertar, borra las
> líneas `classDef` y `class` de cada bloque: son **solo estilo** y el diagrama
> sigue siendo correcto sin ellas.

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
  FALLA["Si no hay respuesta<br/>queda en 169.254.x.x<br/>revisar Gi0/0 y el pool"]
  OK -.->|"sin respuesta DORA"| FALLA

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

## 5. Convergencia de OSPF (Fase B)

Los 3 routers en área 0 intercambian hellos, sincronizan la LSDB y ejecutan el
algoritmo SPF. Con un enlace caído, el camino se recalcula solo.

```mermaid
flowchart LR
  R1(["R1<br/>router ospf 10<br/>ID 192.168.2.34"])
  R2(["R2<br/>router ospf 10<br/>ID 192.168.2.50"])
  R3(["R3<br/>router ospf 10<br/>ID 192.168.2.66"])

  R1 <-->|"Hello cada 10 s<br/>Gi0/1 .49 ↔ .50"| R2
  R2 <-->|"Hello cada 10 s<br/>Gi0/2 .53 ↔ .54"| R3
  R3 <-->|"Hello cada 10 s<br/>Gi0/2 .57 ↔ .58"| R1

  DB[("LSDB común<br/>las 6 subredes de<br/>192.168.2.0/24")]
  R1 -->|"LSA"| DB
  R2 -->|"LSA"| DB
  R3 -->|"LSA"| DB

  DB --> SPF["Algoritmo SPF<br/>calcula la mejor ruta<br/>distancia administrativa 110"]
  SPF --> TABLA["show ip route<br/>marcas O en vez de S"]
  TABLA --> PC["PC-A1 ↔ PC-C1<br/>sigue=enlace"]
  TABLA --> CORTE["Si R2 Gi0/2 baja<br/>el tráfico pasa por R1 ↔ R3<br/>sin tocar nada"]

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

---

## Resumen del plan (para rotular a mano en el diagrama)

| Subred | Uso | Prefijo | Gateway | Rango DHCP | Broadcast |
|--------|-----|---------|---------|-----------|-----------|
| 192.168.2.0/28 | LAN-A (R1) | 255.255.255.240 | .1 | .6 – .14 | .15 |
| 192.168.2.16/28 | LAN-B (R2) | 255.255.255.240 | .17 | .22 – .30 | .31 |
| 192.168.2.32/28 | LAN-C (R3) | 255.255.255.240 | .33 | .38 – .46 | .47 |
| 192.168.2.48/30 | R1 ↔ R2 | 255.255.255.252 | — | — | .51 |
| 192.168.2.52/30 | R2 ↔ R3 | 255.255.255.252 | — | — | .55 |
| 192.168.2.56/30 | R3 ↔ R1 | 255.255.255.252 | — | — | .59 |