<h1 align="center">Preparación y Ejecución del Examen a Título de Suficiencia (ETS) de Administración de Servicios en Red: Diseño, Configuración y Validación de una Topología en GNS3</h1>
<h3 align="center">Preparación del ETS de Administración de Servicios en Red</h3>

<p align="center">
  <strong>Autor:</strong> Eliot Uriel Elena Arriaga<br>
  <strong>Institución:</strong> Escuela Superior de Cómputo (ESCOM) -- IPN
</p>

---

<blockquote>
<h3>Resumen (Abstract)</h3>
<p>Este reporte documenta el proceso completo de preparación para el Examen Teórico-Sustitutivo (ETS) de la Unidad de Aprendizaje de Administración de Servicios en Red, semestre 2026-2. Se construyó, en el simulador GNS3, una topología de práctica que replica la especificada en el documento oficial de requisitos, compuesta por un router ISP, un router de borde (Edge), un router de distribución (R1), dos routers dedicados a servicios (DNS y DHCP), dos hosts cliente y un host externo, todos sobre routers Cisco 7200 con la imagen IOS <code>c7200-a3jk9s-mz.124-25g</code>. Se implementaron y validaron enrutamiento estático restringido en el router ISP, enrutamiento dinámico OSPF entre Edge y R1, traducción de direcciones (NAT) en cadena para permitir salida real a Internet a través del nodo NAT de GNS3, y los servicios de DHCP (con relay entre subredes) y DNS (con resolución interna, externa y reenvío/forwarding hacia servidores públicos). Adicionalmente, se diseñó y validó un procedimiento de reconfiguración rápida ante la asignación de subredes "sorpresa" el día del examen, mediante la simulación de dos escenarios de cambio de subred. Se documentan las incidencias técnicas encontradas durante el proceso, su diagnóstico y solución, así como las decisiones de diseño tomadas y su justificación.</p>
<p><strong>Palabras clave:</strong> GNS3, Cisco IOS, OSPF, NAT, DHCP, DNS, Administración de Servicios en Red</p>
</blockquote>

---

## 1. Introducción y objetivo

El presente documento tiene como propósito registrar de manera ordenada el trabajo de preparación realizado para el Examen a Título de Suficiencia (ETS) de la Unidad de Aprendizaje de Administración de Servicios en Red, correspondiente al semestre 2026-2. De acuerdo con el documento oficial de requisitos entregado por la academia, el examen consiste en la construcción de una topología en GNS3 que cumpla con un conjunto de características técnicas específicas, más un cuestionario teórico complementario, con una ponderación de 90% y 10% respectivamente sobre la calificación final.

El objetivo de este reporte es documentar, paso a paso, el proceso de diseño, construcción, configuración y validación de dicha topología de práctica, incluyendo las decisiones técnicas tomadas ante ambigüedades del documento original, las incidencias encontradas durante la configuración y su respectivo diagnóstico y solución, así como la simulación de un escenario de examen real mediante la asignación de subredes no conocidas de antemano.

## 2. Requisitos del examen

A partir del análisis del documento oficial de requisitos, se identificaron las siguientes condiciones fijas:

- El examen se realiza de forma presencial realizando pruebas sobre la topología solicitada y respondiendo un cuestionario teórico.
- Se solicita trabajar con los routers con los que el alumno se sienta cómodo, por lo que se va a usar la imagen IOS `c7200-a3jk9s-mz.124-25g`.
- Deben implementarse los servicios de NAT, DNS y DHCP, pudiendo usarse los propios routers como servidores de dichos servicios.
- Debe estar funcionando el NAT que ofrece GNS3 (salida a Internet real).
- El router `ISP` solo permite la implementación de **dos** enrutamientos estáticos: uno hacia la subred `209.165.200.240/29` y la ruta por defecto.
- Entre `Edge` y `R1` debe existir enrutamiento dinámico (protocolo libre).
- Las subredes internas (detrás de `R1`) no vienen fijas en su totalidad y se indicarán el día del examen.
- El cuestionario abarca, entre otros temas, listas de control de acceso (2.2), SNMP (3.1.1) y calidad de servicio/DiffServ (3.2).

La **Tabla 1** resume el direccionamiento IP fijo especificado en el documento oficial.

<p align="center"><strong>Tabla 1.</strong> Direccionamiento IP fijo especificado en el documento oficial del ETS.</p>

<table align="center">
  <thead>
    <tr>
      <th>Dispositivo</th>
      <th>Interfaz</th>
      <th>Dirección IP</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>ISP</td><td>F1/1</td><td>200.10.10.1/30</td></tr>
    <tr><td>ISP</td><td>F0/0</td><td>200.20.20.1/24</td></tr>
    <tr><td colspan="3"></td></tr>
    <tr><td>Edge</td><td>F1/1</td><td>200.10.10.2/30</td></tr>
    <tr><td>Edge</td><td>F0/0</td><td>10.1.1.1/30</td></tr>
    <tr><td colspan="3"></td></tr>
    <tr><td>R1</td><td>F0/0</td><td>10.1.1.2/30</td></tr>
    <tr><td>R1</td><td>F2/0</td><td>192.168.11.129/26</td></tr>
  </tbody>
</table>

## 3. Metodología de trabajo

El proyecto se organizó en pasos secuenciales. Para cada paso se definieron las instrucciones de configuración, se ejecutaron, se verificó su correcta aplicación y se realizó una fase de pruebas específica que validara no solo que la configuración se aplicó, sino que cumple funcionalmente lo solicitado por el documento del examen. Ante cualquier error o resultado inesperado, se realizó un proceso de diagnóstico iterativo hasta resolverlo antes de continuar al siguiente paso. Al finalizar todos los pasos de construcción, se realizaron pruebas globales de integración y una simulación de examen mediante la asignación de subredes no conocidas previamente, como ocurrirá el día real del examen.

## 4. Topología construida

La **Figura 1** muestra la topología final construida en GNS3 para efectos de práctica, la cual reproduce fielmente la topología ilustrativa del documento oficial, con la adición de dos routers dedicados a los servicios de DNS y DHCP.

<p align="center">
  <img src="/0.-%20Reporte/figures/Full_Topology.png" alt="Topología completa construida en GNS3 para la práctica del ETS." width="90%"><br>
  <em>Figura 1: Topología completa construida en GNS3 para la práctica del ETS.</em>
</p>

<p align="center"><strong>Tabla 2.</strong> Nodos de la topología de práctica y su rol.</p>

<table align="center">
  <thead>
    <tr>
      <th>Nodo</th>
      <th>Tipo</th>
      <th>Rol</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>ISP</td><td>Router c7200</td><td>Borde externo, salida a Internet real</td></tr>
    <tr><td>Edge</td><td>Router c7200</td><td>Borde interno, NAT overload</td></tr>
    <tr><td>R1</td><td>Router c7200</td><td>Distribución, OSPF, DHCP relay</td></tr>
    <tr><td>Srv-DHCP</td><td>Router c7200</td><td>Servidor DHCP dedicado</td></tr>
    <tr><td>Srv-DNS</td><td>Router c7200</td><td>Servidor DNS dedicado</td></tr>
    <tr><td>Switch1, Switch2</td><td>Ethernet Switch</td><td>Conmutación de LAN1 y LAN2</td></tr>
    <tr><td>PC1, PC2</td><td>VPCS</td><td>Hosts cliente de prueba</td></tr>
    <tr><td>HostExterno</td><td>VPCS</td><td>Host externo simulado</td></tr>
    <tr><td>NAT (nube)</td><td>NAT node GNS3</td><td>Salida a Internet real</td></tr>
  </tbody>
</table>

Durante la construcción se identificó que la interfaz `F1/1` especificada en el documento oficial para el enlace ISP--Edge no estaba disponible en la configuración de adaptadores, por lo que dicho enlace se implementó sobre la interfaz `F1/0` en ambos extremos, conservando exactamente las direcciones IP indicadas en la **Tabla 1**. Se interpreta esta discrepancia como un posible error tipográfico del documento, dado que lo relevante para la evaluación es el direccionamiento IP, no el número literal de interfaz.

De manera análoga, se detectó que la dirección `200.20.20.1/24` asignada en la tabla del documento a la interfaz `F0/0` de ISP corresponde, por la lógica de la topología (el host externo con IP `200.20.20.20/24` se conecta físicamente a `F2/0`), a la interfaz `F2/0`; la interfaz `F0/0` se reservó para la conexión hacia el nodo NAT de GNS3, obteniendo dirección de forma dinámica.

La **Tabla 3** resume el direccionamiento definitivo aplicado en la práctica.

<p align="center"><strong>Tabla 3.</strong> Direccionamiento definitivo aplicado en la topología de práctica.</p>

<table align="center">
  <thead>
    <tr>
      <th>Enlace físico</th>
      <th>IP/Máscara</th>
      <th>Origen</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>ISP F0/0 -- NAT (nube)</td><td>Dinámica (DHCP del cloud)</td><td>Salida a Internet real</td></tr>
    <tr><td>ISP F2/0 -- HostExterno</td><td>200.20.20.1/24</td><td>Fija por tabla (aclarada)</td></tr>
    <tr><td>ISP F1/0 -- Edge F1/0</td><td>200.10.10.1/30 -- 200.10.10.2/30</td><td>Fija por tabla (interfaz aclarada)</td></tr>
    <tr><td>Edge F0/0 -- R1 F0/0</td><td>10.1.1.1/30 -- 10.1.1.2/30</td><td>Fija por tabla</td></tr>
    <tr><td>R1 F1/0 -- Switch1 (LAN1)</td><td>Variable (subred sorpresa)</td><td>Se dicta el día del examen</td></tr>
    <tr><td>R1 F2/0 -- Switch2 (LAN2)</td><td>192.168.11.129/26</td><td>Fija por tabla</td></tr>
    <tr><td>Switch2 -- Srv-DNS</td><td>192.168.11.131/26</td><td>Estática, elegida en el segmento</td></tr>
    <tr><td>Switch2 -- Srv-DHCP</td><td>192.168.11.130/26</td><td>Estática, marcada en el diagrama</td></tr>
  </tbody>
</table>

## 5. Configuración por fase

### 5.1. Enrutamiento estático en ISP

En cumplimiento estricto de la restricción del documento, en el router ISP se configuraron únicamente las dos rutas estáticas permitidas:

<pre><code><strong>ip route 209.165.200.240 255.255.255.248 FastEthernet1/0
ip route 0.0.0.0 0.0.0.0 FastEthernet0/0</strong> (Asignada por el NAT de GNS3)
</code></pre>
<p align="center"><em>Código 1: Rutas estáticas configuradas en ISP.</em></p>

Para validar la primera ruta sin depender de dispositivos externos al laboratorio, se configuró en el propio ISP una interfaz de *loopback* como host de prueba (`209.165.200.241/32`), y en Edge una ruta estática puntual hacia dicha subred a través de ISP. Se documenta que este loopback y la ruta en Edge son artefactos exclusivos de prueba del alumno, no un requisito literal del documento.

<p align="center">
  <img src="/0.-%20Reporte/figures/ISP_SHOW_IP_ROUTE.png" alt="Verificación de las dos rutas estáticas permitidas en ISP." width="80%"><br>
  <em>Figura 2: Verificación de las dos rutas estáticas permitidas en ISP.</em>
</p>

### 5.2. Enrutamiento dinámico OSPF entre Edge y R1

Se implementó OSPF de área única (área 0) exclusivamente en el enlace de tránsito entre Edge y R1, sin que el router ISP participe del proceso en ningún momento.

<pre><code><strong>! Edge
router ospf 1
 network 10.1.1.0 0.0.0.3 area 0
 default-information originate always

! R1
router ospf 1
 network 10.1.1.0 0.0.0.3 area 0
 network 192.168.11.128 0.0.0.63 area 0
 network &lt;LAN1_sorpresa&gt; area 0</strong>
</code></pre>
<p align="center"><em>Código 2: Configuración OSPF en Edge y R1.</em></p>

Se optó por que Edge origine una ruta por defecto hacia OSPF mediante `default-information originate always`, en lugar de redistribuir puntualmente rutas específicas. De esta manera, cualquier destino externo a la red interna —incluyendo cualquier prueba adicional o el tráfico real hacia Internet— queda resuelto automáticamente para R1 y todo lo que cuelga de él, sin necesidad de modificar la configuración de OSPF ante cambios futuros.

<p align="center">
  <img src="/0.-%20Reporte/figures/show_ip_ospf_neighbor.png" alt="Adyacencia OSPF establecida (estado FULL) entre Edge y R1." width="85%"><br>
  <em>Figura 3: Adyacencia OSPF establecida (estado FULL) entre Edge y R1.</em>
</p>

### 5.3. Traducción de direcciones (NAT)

Se implementó NAT overload en el router Edge para traducir el tráfico proveniente de las redes internas hacia la interfaz pública de Edge:

<pre><code><strong>interface FastEthernet0/0
 ip nat inside
interface FastEthernet1/0
 ip nat outside
ip access-list standard NAT_INTERNAS
 permit 10.0.0.0 0.255.255.255
 permit 172.16.0.0 0.15.255.255
 permit 192.168.0.0 0.0.255.255
ip nat inside source list NAT_INTERNAS interface FastEthernet1/0 overload
ip route 0.0.0.0 0.0.0.0 200.10.10.1</strong>
</code></pre>
<p align="center"><em>Código 3: Configuración de NAT overload en Edge.</em></p>

La lista de acceso utilizada para seleccionar el tráfico a traducir se diseñó deliberadamente para cubrir los tres bloques de direccionamiento privado completos definidos en el RFC 1918 (`10.0.0.0/8`, `172.16.0.0/12` y `192.168.0.0/16`), en vez de únicamente las subredes puntuales en uso durante la práctica. Esta decisión de diseño permite que, sin importar qué subred "sorpresa" se asigne el día del examen, el NAT continúe funcionando sin necesidad de modificarlo, siempre que dicha subred se encuentre dentro de un rango de direccionamiento privado estándar.

Durante las pruebas se identificó que el router ISP, al obtener su interfaz externa vía DHCP del nodo NAT de GNS3, únicamente traduce tráfico cuyo origen pertenece a la subred que el propio nodo NAT le asignó (`192.168.122.0/24` en el laboratorio de práctica); el tráfico de tránsito con origen en la IP pública interna de Edge no era reconocido por dicho nodo. Para resolver esta limitación sin infringir la restricción de "dos enrutamientos estáticos" de ISP —dado que no se trata de una modificación al enrutamiento sino a un subsistema independiente (NAT/PAT)— se implementó un segundo nivel de traducción (NAT en cadena) en el propio ISP:

<pre><code><strong>interface FastEthernet1/0
 ip nat inside
interface FastEthernet0/0
 ip nat outside
ip access-list standard NAT_TRANSITO
 permit any
ip nat inside source list NAT_TRANSITO interface FastEthernet0/0 overload</strong>
</code></pre>
<p align="center"><em>Código 4: NAT en cadena configurado en ISP.</em></p>

<table align="center">
  <tr>
    <td align="center">
      <img src="/0.-%20Reporte/figures/nat_translations_edge.png" alt="Traducciones NAT activas en Edge (NAT overload interno)." width="90%"><br>
      <em>Figura 4: Traducciones NAT activas en Edge.</em>
    </td>
    <td align="center">
      <img src="/0.-%20Reporte/figures/nat_translations_isp.png" alt="Traducciones NAT en cadena activas en ISP (doble PAT hacia Internet real)." width="90%"><br>
      <em>Figura 5: Traducciones NAT en cadena activas en ISP.</em>
    </td>
  </tr>
</table>

<p><strong>Discusión: la ruta default aprendida por DHCP.</strong><br>
Se identificó que Cisco IOS clasifica internamente como estática (código <code>S*</code>) la ruta por defecto instalada automáticamente por el cliente DHCP en la interfaz externa de ISP, aun cuando dicha ruta nunca se escribe como línea <code>ip route</code> en el <code>running-config</code>. Esto tiene una implicación relevante para la evaluación: si el examen se califica revisando <code>show ip route</code>, el requisito de "dos rutas estáticas" se cumple; si se califica revisando literalmente el <code>running-config</code>, únicamente aparecerá una línea escrita por el alumno. Existe la alternativa de fijar esta ruta manualmente (<code>ip route 0.0.0.0 0.0.0.0 &lt;gateway&gt;</code>) para eliminar cualquier ambigüedad; en esta práctica se optó deliberadamente por dejarla implícita, documentando aquí el análisis y la alternativa disponible.</p>

### 5.4. DHCP

Se configuró el router `Srv-DHCP` con dos ámbitos (*pools*), uno por cada LAN interna, y se habilitó reenvío (*relay*) en `R1` mediante `ip helper-address` para la LAN que no comparte segmento físico con el servidor:

<pre><code><strong>! Srv-DHCP
ip dhcp excluded-address &lt;gateways y direcciones fijas&gt;
ip dhcp pool LAN1_POOL
 network &lt;subred_LAN1&gt;
 default-router &lt;gateway_LAN1&gt;
 dns-server 192.168.11.131
ip dhcp pool LAN2_POOL
 network 192.168.11.128 255.255.255.192
 default-router 192.168.11.129
 dns-server 192.168.11.131

! R1, interfaz hacia la LAN sin servidor local
ip helper-address 192.168.11.130</strong>
</code></pre>
<p align="center"><em>Código 5: Configuración del servicio DHCP.</em></p>

Durante las pruebas iniciales se detectó que los clientes de la LAN sin servidor local no lograban obtener dirección, mientras que los de la LAN local al servidor sí. El diagnóstico aisló el problema en que `Srv-DHCP` (y por el mismo motivo, `Srv-DNS`) únicamente contaban con la dirección de su propia interfaz, sin ruta de regreso hacia el resto de la red, por lo que no podían enviar sus respuestas de vuelta a los segmentos remotos. La solución consistió en agregar una ruta por defecto en ambos servidores apuntando a `R1`.

<p align="center">
  <img src="/0.-%20Reporte/figures/show_ip_dhcp_binding.png" alt="Concesiones DHCP activas en Srv-DHCP para ambas LAN." width="80%"><br>
  <em>Figura 6: Concesiones DHCP activas en Srv-DHCP para ambas LAN.</em>
</p>

### 5.5. DNS

Se habilitó el motor de DNS de IOS en `Srv-DNS`, con registros locales para los dispositivos internos y externos relevantes, y reenvío (*forwarding*) hacia servidores DNS públicos para resolver nombres de Internet:

<pre><code><strong>ip dns server
ip domain name ets.local
ip host srv-dns.ets.local 192.168.11.131
ip host srv-dhcp.ets.local 192.168.11.130
ip host r1.ets.local 192.168.11.129
ip host hostexterno.ets.local 200.20.20.20
ip host isp-loopback.ets.local 209.165.200.241
ip name-server 8.8.8.8
ip name-server 1.1.1.1</strong>
</code></pre>
<p align="center"><em>Código 6: Configuración del servicio DNS.</em></p>

<p><strong>Discusión: sincronización de registros DNS con IPs dinámicas.</strong><br>
Dado que <code>PC1</code> y <code>PC2</code> obtienen dirección por DHCP, existe el riesgo de que sus registros DNS queden obsoletos tras una renovación de concesión. Se evaluaron dos alternativas:</p>

<ol type="A">
  <li>reservar una dirección fija por MAC en el propio DHCP, eliminando el problema de raíz sin mantenimiento posterior; y</li>
  <li>un proceso manual de dos comandos (<code>no ip host</code> seguido de <code>ip host</code>) para actualizar el registro tras cada cambio.</li>
</ol>

<p>Se optó por la alternativa (B), dado que, al esperarse subredes "sorpresa" distintas el día del examen, de cualquier forma será necesario reconfigurar manualmente los ámbitos de DHCP y el <code>ip helper-address</code> de R1, por lo que la ventaja de "cero mantenimiento" de la alternativa (A) se pierde en ese escenario. La alternativa (A) se documenta como solución técnicamente válida, no implementada.</p>

<p align="center">
  <img src="/0.-%20Reporte/figures/dns_resolution_pc1.png" alt="Resolución de nombres interna, externa y vía forwarder desde PC1." width="80%"><br>
  <em>Figura 7: Resolución de nombres interna, externa y vía forwarder desde PC1.</em>
</p>

## 6. Pruebas globales de integración

Tras completar la configuración de todos los servicios, se ejecutó una batería de pruebas de cumplimiento y conectividad de extremo a extremo, resumida en la **Tabla 4**.

<p align="center"><strong>Tabla 4.</strong> Resumen de pruebas globales de integración.</p>

<table align="center">
  <thead>
    <tr>
      <th>Prueba</th>
      <th>Resultado</th>
      <th>Observación</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>ISP: 2 rutas estáticas únicamente</td><td>Cumplido</td><td>Sin procesos dinámicos activos</td></tr>
    <tr><td>OSPF Edge--R1</td><td>FULL</td><td>Adyacencia estable</td></tr>
    <tr><td>PC1 ↔ PC2</td><td>Exitoso</td><td>Inter-LAN vía R1</td></tr>
    <tr><td>PC1/PC2 → 8.8.8.8</td><td>Exitoso</td><td>NAT extremo a extremo</td></tr>
    <tr><td>R1 → loopback de prueba ISP</td><td>Exitoso</td><td>Ruta estática validada</td></tr>
    <tr><td>HostExterno → PC1</td><td>Fallido (esperado)</td><td>Aislamiento propio del NAT/PAT</td></tr>
    <tr><td>DHCP (ambas LAN)</td><td>Exitoso</td><td>Incluye relay</td></tr>
    <tr><td>DNS (interno/externo/forwarder)</td><td>Exitoso</td><td></td></tr>
  </tbody>
</table>

Es importante señalar que el fallo de conectividad de `HostExterno` hacia `PC1` no constituye un error, sino el comportamiento esperado de una red protegida por NAT/PAT: los hosts internos pueden iniciar conexiones hacia el exterior, pero ningún host externo puede iniciar una conexión hacia adentro sin una regla explícita de NAT estático o redirección de puertos, la cual no fue solicitada por el documento del examen. Este resultado se interpreta como una validación positiva del aislamiento de seguridad de la topología.

<pre><code>ISP#show run | include ip route

Edge#show ip ospf neighbor

R1#show ip ospf neighbor

PC1&gt; ping pc2.ets.local
pc2.ets.local resolved to 192.168.11.132
PC1&gt; ping srv-dns.ets.local
srv-dns.ets.local resolved to 192.168.11.131
PC1&gt; ping hostexterno.ets.local
hostexterno.ets.local resolved to 200.20.20.20

PC2&gt; ping 8.8.8.8

HostExterno a PC1 FALLIDO (Por NAT, es Esperable)
HostExterno&gt; ping 192.168.20.4
192.168.20.4 icmp_seq=1 timeout

R1#ping 209.165.200.241

Srv-DHCP#show ip dhcp binding

PC1&gt; ping srv-dns.ets.local
srv-dns.ets.local resolved to 192.168.11.131
PC1&gt; ping hostexterno.ets.local
hostexterno.ets.local resolved to 200.20.20.20

PC2&gt; ping srv-dns.ets.local
srv-dns.ets.local resolved to 192.168.11.131
PC2&gt; ping hostexterno.ets.local
hostexterno.ets.local resolved to 200.20.20.20
</code></pre>
<p align="center"><em>Código 7: Comandos ejecutados para la matriz de pruebas de conectividad global.</em></p>

## 7. Simulación de examen: subredes sorpresa

Dado que el documento oficial indica que las subredes internas se asignarán el día del examen, se diseñó y validó un procedimiento de reconfiguración rápida, probado mediante dos escenarios simulados.

### 7.1. Escenario A: cambio de subred en LAN1

Se simuló la asignación de la subred `172.16.50.0/28` para la LAN de `PC1`. Los únicos elementos que requirieron modificación fueron la dirección IP de `R1` en la interfaz correspondiente, la sentencia `network` de OSPF, y el ámbito de DHCP asociado. No fue necesario modificar el NAT de `Edge`, validando la decisión de diseño de cubrir los tres bloques RFC 1918 completos desde el inicio.

### 7.2. Escenario B: cambio de subred en LAN2 (reubicación de servidores)

Se simuló la asignación de la subred `10.30.30.0/27` para la LAN donde residen `Srv-DHCP` y `Srv-DNS`, escenario más exigente al requerir la reubicación de ambos servidores. Se actualizaron: la dirección de `R1` en la interfaz correspondiente y su sentencia `network` de OSPF; el `ip helper-address` de R1 hacia la nueva dirección de `Srv-DHCP`; las direcciones IP y rutas por defecto de ambos servidores; el ámbito de DHCP; y los registros `ip host` en `Srv-DNS`. Nuevamente, el NAT de Edge no requirió ningún cambio.

<p align="center">
  <img src="/0.-%20Reporte/figures/Escenario_B.png" alt="Evidencia de la reconfiguración exitosa del Escenario B." width="80%"><br>
  <em>Figura 8: Evidencia de la reconfiguración exitosa del Escenario B.</em>
</p>

Ambos escenarios se ejecutaron exitosamente sin afectar el resto de la topología, confirmando la robustez del diseño frente al componente de incertidumbre propio del examen real.

<p><strong>Lección aprendida.</strong><br>
Durante la simulación se observó que los hosts VPCS no adoptan automáticamente el servidor DNS entregado por el ámbito de DHCP tras una renovación de dirección en una nueva subred, siendo necesario reconfigurar manualmente el DNS del cliente (<code>ip dns &lt;dirección&gt;</code>) después de cada cambio de subred. Se recomienda incluir este paso explícitamente en el procedimiento a seguir el día del examen.</p>

## 8. Temas complementarios del cuestionario

De acuerdo con el documento oficial, los temas de listas de control de acceso (2.2), protocolo de administración de red SNMP (3.1.1) y calidad de servicio/servicios diferenciados (3.2) corresponden al cuestionario teórico y no constituyen un requisito explícito de la topología práctica. Por esta razón, no fueron implementados en la topología de este proyecto, y su repaso se realizó de manera independiente como preparación para el cuestionario.

## 9. Conclusiones

El proceso documentado en este reporte permitió construir, configurar y validar de manera sistemática una topología de red que cumple con la totalidad de los requisitos técnicos especificados en el documento oficial del ETS de Administración de Servicios en Red. A lo largo del proceso se identificaron y resolvieron diversas incidencias técnicas —discrepancias entre el documento y la topología real, problemas de resolución de rutas sobre medios Ethernet, limitaciones del nodo NAT de GNS3, y ausencia de rutas de retorno en los servidores de servicio— cuyo diagnóstico metódico permitió llegar a soluciones robustas y, en varios casos, más resilientes que una implementación literal del documento (como la cobertura completa de bloques RFC 1918 en el NAT o el uso de una ruta por defecto originada dinámicamente en OSPF). La simulación de dos escenarios de subred "sorpresa" confirmó que la topología y el procedimiento de reconfiguración diseñados son capaces de adaptarse rápidamente a la incertidumbre propia de las condiciones del examen real.

---

<hr>

<h3 align="center">Agradecimientos</h3>
<p align="center">Trabajo de preparación individual para el ETS de la Unidad de Aprendizaje de Administración de Servicios en Red, semestre 2026-2.</p>

<h3 align="center">Divulgación de Intereses</h3>
<p align="center">Los autores no tienen conflictos de interés que declarar en relación con el contenido de este reporte.</p>
