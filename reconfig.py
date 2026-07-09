"""
Generador de scripts de reconfiguracion rapida ante subredes.

Reproduce, de forma automatizada, el mismo procedimiento que se ejecuto
manualmente durante la simulacion de examen.

ESTADO BASE (usado por el modo NO MEMORY, y como punto de partida inicial
del modo MEMORY si aun no existe historial). Corresponde al estado de la
topologia en el momento antes de realizar el último testing:

    LAN1 (R1 FastEthernet1/0): 192.168.20.0/24   gateway 192.168.20.1
    LAN2 (R1 FastEthernet2/0): 192.168.11.128/26 gateway 192.168.11.129
        Srv-DHCP: 192.168.11.130/26
        Srv-DNS : 192.168.11.131/26
"""

import ipaddress
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
STATE_FILE = SCRIPT_DIR / "estado_memoria.json"

BASELINE = {
    "lan1": {
        "network": "192.168.20.0",
        "prefix": 24,
        "gateway": "192.168.20.1",
    },
    "lan2": {
        "network": "192.168.11.128",
        "prefix": 26,
        "gateway": "192.168.11.129",
        "srv_dhcp_ip": "192.168.11.130",
        "srv_dns_ip": "192.168.11.131",
    },
}


# ---------------------------------------------------------------------------
# Utilidades de direccionamiento
# ---------------------------------------------------------------------------

def full_info(d, is_lan2=False):
    """Completa un dict de subred (network/prefix/...) con mascara y wildcard."""
    net = ipaddress.ip_network(f"{d['network']}/{d['prefix']}", strict=False)
    info = dict(d)
    info["netmask"] = str(net.netmask)
    info["wildcard"] = str(net.hostmask)
    return info


def lan_info_from_network(net, is_lan2=False):
    """Construye la info de una LAN nueva a partir de un ipaddress.IPv4Network.
    Convencion (igual que en los Escenarios A y B ejecutados manualmente):
      network + 1 -> gateway (interfaz de R1)
      network + 2 -> Srv-DHCP (solo LAN2)
      network + 3 -> Srv-DNS  (solo LAN2)
    """
    info = {
        "network": str(net.network_address),
        "prefix": net.prefixlen,
        "netmask": str(net.netmask),
        "wildcard": str(net.hostmask),
        "gateway": str(net.network_address + 1),
    }
    if is_lan2:
        info["srv_dhcp_ip"] = str(net.network_address + 2)
        info["srv_dns_ip"] = str(net.network_address + 3)
    return info


def ask_subnet(prompt):
    while True:
        raw = input(prompt).strip()
        try:
            net = ipaddress.ip_network(raw, strict=False)
        except ValueError as e:
            print(f"  Formato invalido ({e}). Usa el formato V.W.X.Y/Z, ej. 172.16.50.0/28")
            continue
        if str(net.network_address) != raw.split("/")[0]:
            print(f"  Nota: se interpreto como direccion de red {net.network_address}/{net.prefixlen} "
                  f"(se ajustaron bits de host sobrantes).")
        return net


def ask_choice(prompt, choices):
    while True:
        v = input(prompt).strip().upper()
        if v in choices:
            return v
        print(f"  Opcion invalida. Elige entre: {', '.join(sorted(choices))}")


# ---------------------------------------------------------------------------
# Persistencia de estado (modo Memory)
# ---------------------------------------------------------------------------

def load_state(mode):
    if mode == "B" and STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    # Copia profunda del baseline
    return json.loads(json.dumps(BASELINE))


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Generadores de contenido por entidad (replican exactamente los comandos
# usados en vivo durante el Paso 9)
# ---------------------------------------------------------------------------

def gen_r1_file(old1, new1, old2, new2, change_lan1, change_lan2, modo_txt):
    L = []
    L.append("! ============================================================")
    L.append("! Reconfiguracion de R1 ante subred(es) sorpresa")
    L.append(f"! Modo de estado: {modo_txt}")
    L.append("! ============================================================")
    L.append("enable")
    L.append("configure terminal")

    f1_cmds = []
    if change_lan1:
        f1_cmds += [
            "no ip address",
            f"ip address {new1['gateway']} {new1['netmask']}",
            "description SUBRED_SORPRESA_LAN1_APLICADA",
        ]
    if change_lan2:
        f1_cmds += [
            f"no ip helper-address {old2['srv_dhcp_ip']}",
            f"ip helper-address {new2['srv_dhcp_ip']}",
        ]
    if f1_cmds:
        L.append("!")
        L.append("! --- FastEthernet1/0 (hacia LAN1 / Switch1) ---")
        L.append("interface FastEthernet1/0")
        L.extend(f" {c}" for c in f1_cmds)

    if change_lan2:
        L.append("!")
        L.append("! --- FastEthernet2/0 (hacia LAN2 / Switch2) ---")
        L.append("interface FastEthernet2/0")
        L.append(" no ip address")
        L.append(f" ip address {new2['gateway']} {new2['netmask']}")
        L.append(" description SUBRED_SORPRESA_LAN2_APLICADA")

    L.append("!")
    L.append("router ospf 1")
    if change_lan1:
        L.append(f" no network {old1['network']} {old1['wildcard']} area 0")
        L.append(f" network {new1['network']} {new1['wildcard']} area 0")
    if change_lan2:
        L.append(f" no network {old2['network']} {old2['wildcard']} area 0")
        L.append(f" network {new2['network']} {new2['wildcard']} area 0")

    L.append("end")
    L.append("write memory")
    L.append("")
    L.append("! --- Verificacion sugerida ---")
    L.append("! show ip interface brief")
    L.append("! show ip ospf neighbor")
    L.append("! show ip route ospf")
    return "\n".join(L) + "\n"


def gen_srvdhcp_file(old1, new1, old2, new2, change_lan1, change_lan2, modo_txt):
    L = []
    L.append("! ============================================================")
    L.append("! Reconfiguracion de Srv-DHCP ante subred(es) sorpresa")
    L.append(f"! Modo de estado: {modo_txt}")
    L.append("! ============================================================")
    L.append("enable")
    L.append("configure terminal")

    if change_lan2:
        L.append("!")
        L.append("! --- Reubicacion de Srv-DHCP (vive fisicamente en LAN2) ---")
        L.append("interface FastEthernet0/0")
        L.append(" no ip address")
        L.append(f" ip address {new2['srv_dhcp_ip']} {new2['netmask']}")
        L.append("!")
        L.append(f"no ip route 0.0.0.0 0.0.0.0 {old2['gateway']}")
        L.append(f"ip route 0.0.0.0 0.0.0.0 {new2['gateway']}")

    if change_lan1:
        L.append("!")
        L.append("! --- Pool DHCP de LAN1 ---")
        L.append("no ip dhcp pool LAN1_POOL")
        L.append(f"no ip dhcp excluded-address {old1['gateway']}")
        L.append(f"ip dhcp excluded-address {new1['gateway']}")
        L.append("ip dhcp pool LAN1_POOL")
        L.append(f" network {new1['network']} {new1['netmask']}")
        L.append(f" default-router {new1['gateway']}")
        L.append(f" dns-server {new2['srv_dns_ip']}")

    if change_lan2:
        L.append("!")
        L.append("! --- Pool DHCP de LAN2 ---")
        L.append("no ip dhcp pool LAN2_POOL")
        L.append(f"no ip dhcp excluded-address {old2['gateway']} {old2['srv_dns_ip']}")
        L.append(f"ip dhcp excluded-address {new2['gateway']} {new2['srv_dns_ip']}")
        L.append("ip dhcp pool LAN2_POOL")
        L.append(f" network {new2['network']} {new2['netmask']}")
        L.append(f" default-router {new2['gateway']}")
        L.append(f" dns-server {new2['srv_dns_ip']}")

    L.append("end")
    L.append("write memory")
    L.append("")
    L.append("! --- Verificacion sugerida ---")
    L.append("! show ip dhcp binding")
    L.append("! show ip dhcp pool")
    L.append("")
    L.append("! NOTA:")
    L.append("! en los hosts VPCS afectados, tras renovar con 'ip dhcp' es")
    L.append("! necesario re-teclear manualmente 'ip dns <ip-de-Srv-DNS>', ya que VPCS")
    L.append("! no siempre adopta automaticamente el DNS entregado por el pool.")
    return "\n".join(L) + "\n"


def gen_srvdns_file(old2, new2, modo_txt):
    L = []
    L.append("! ============================================================")
    L.append("! Reconfiguracion de Srv-DNS ante subred sorpresa en LAN2")
    L.append(f"! Modo de estado: {modo_txt}")
    L.append("! ============================================================")
    L.append("enable")
    L.append("configure terminal")
    L.append("interface FastEthernet0/0")
    L.append(" no ip address")
    L.append(f" ip address {new2['srv_dns_ip']} {new2['netmask']}")
    L.append("!")
    L.append(f"no ip route 0.0.0.0 0.0.0.0 {old2['gateway']}")
    L.append(f"ip route 0.0.0.0 0.0.0.0 {new2['gateway']}")
    L.append("!")
    L.append("! --- Actualizacion de registros DNS (entidades con IP fija) ---")
    L.append(f"no ip host srv-dns.ets.local {old2['srv_dns_ip']}")
    L.append(f"ip host srv-dns.ets.local {new2['srv_dns_ip']}")
    L.append(f"no ip host srv-dhcp.ets.local {old2['srv_dhcp_ip']}")
    L.append(f"ip host srv-dhcp.ets.local {new2['srv_dhcp_ip']}")
    L.append(f"no ip host r1.ets.local {old2['gateway']}")
    L.append(f"ip host r1.ets.local {new2['gateway']}")
    L.append("end")
    L.append("write memory")
    L.append("")
    L.append("! --- Verificacion sugerida ---")
    L.append("! ping www.cisco.com")
    L.append("")
    L.append("! ============================================================")
    L.append("! PENDIENTE MANUAL:")
    L.append("! Los registros de PC1/PC2 usan IP dinamica y no se pueden prever")
    L.append("! de antemano. Procedimiento:")
    L.append("!   1) En Srv-DHCP: show ip dhcp binding o show ip en ambas VPC")
    L.append("!   2) En Srv-DNS, por cada host afectado:")
    L.append("!        no ip host pc1.ets.local <ip-vieja>")
    L.append("!        ip host pc1.ets.local <ip-nueva>")
    L.append("!        no ip host pc2.ets.local <ip-vieja>")
    L.append("!        ip host pc2.ets.local <ip-nueva>")
    L.append("! ============================================================")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------

def run(mode, case, new1_net=None, new2_net=None, base_dir=None):
    """Logica central, separada de input() para poder probarla sin consola."""
    state = load_state(mode)
    old1 = full_info(state["lan1"])
    old2 = full_info(state["lan2"], is_lan2=True)

    change_lan1 = case in ("1", "3")
    change_lan2 = case in ("2", "3")

    new1 = lan_info_from_network(new1_net) if change_lan1 else old1
    new2 = lan_info_from_network(new2_net, is_lan2=True) if change_lan2 else old2

    if change_lan2 and new2_net.prefixlen > 29:
        print("  ADVERTENCIA: la subred de LAN2 tiene muy pocas direcciones utiles "
              "para alojar gateway + Srv-DHCP + Srv-DNS + hosts. Verifica que alcance.")

    modo_txt = "NO MEMORY (estado base al cierre de pruebas)" if mode == "A" \
        else "MEMORY (estado base = ultimo cambio aplicado)"

    labels = []
    if change_lan1:
        labels.append(f"{new1['network']}-{new1['prefix']}")
    if change_lan2:
        labels.append(f"{new2['network']}-{new2['prefix']}")
    folder_name = "Cambios " + "_".join(labels)
    folder = (base_dir or Path.cwd()) / folder_name
    folder.mkdir(parents=True, exist_ok=True)

    created = []
    step = 1

    r1_content = gen_r1_file(old1, new1, old2, new2, change_lan1, change_lan2, modo_txt)
    p = folder / f"{step}_R1.txt"
    p.write_text(r1_content)
    created.append(p)
    step += 1

    dhcp_content = gen_srvdhcp_file(old1, new1, old2, new2, change_lan1, change_lan2, modo_txt)
    p = folder / f"{step}_Srv-DHCP.txt"
    p.write_text(dhcp_content)
    created.append(p)
    step += 1

    if change_lan2:
        dns_content = gen_srvdns_file(old2, new2, modo_txt)
        p = folder / f"{step}_Srv-DNS.txt"
        p.write_text(dns_content)
        created.append(p)
        step += 1

    if mode == "B":
        new_state = {
            "lan1": {"network": new1["network"], "prefix": new1["prefix"], "gateway": new1["gateway"]},
            "lan2": {
                "network": new2["network"], "prefix": new2["prefix"], "gateway": new2["gateway"],
                "srv_dhcp_ip": new2["srv_dhcp_ip"], "srv_dns_ip": new2["srv_dns_ip"],
            },
        }
        save_state(new_state)

    return folder, created


def main():
    print("=" * 70)
    print(" Generador de reconfiguracion rapida")
    print("=" * 70)
    print()
    print("Modo de estado de partida:")
    print("  (A) No memory  - siempre parte del estado antes del último testing")
    print("  (B) Memory     - parte del ultimo cambio aplicado (historial)")
    mode = ask_choice("Elige modo (A/B): ", {"A", "B"})

    print()
    print("Caso a generar:")
    print("  (1) Cambia LAN1")
    print("  (2) Cambia LAN2")
    print("  (3) Cambian LAN1 y LAN2")
    case = ask_choice("Elige opcion (1/2/3): ", {"1", "2", "3"})

    new1_net = new2_net = None
    print()
    if case in ("1", "3"):
        new1_net = ask_subnet("Nueva subred SORPRESA para LAN1 (V.W.X.Y/Z): ")
    if case in ("2", "3"):
        new2_net = ask_subnet("Nueva subred SORPRESA para LAN2 (V.W.X.Y/Z): ")

    folder, created = run(mode, case, new1_net, new2_net)

    print()
    print(f"Listo. Carpeta generada: {folder}")
    for f in created:
        print(f"  - {f.name}")
    print()
    print("Aplicar los archivos en GNS3 EN EL ORDEN NUMERADO")
    print("No olvidar el bloque PENDIENTE MANUAL dentro de Srv-DNS si se genero.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelado por el usuario.")
        sys.exit(1)
