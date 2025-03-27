import dns.resolver
import socket

# Funcție pentru a rezolva domeniul într-o adresă IP
def resolve_domain(domain, dns_server):
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [dns_server]  # Setăm serverul DNS utilizat
        
        # Căutăm adresa IP a domeniului
        answers = resolver.resolve(domain, 'A')  # 'A' pentru adrese IPv4
        print(f'Domeniul {domain} are următoarele IP-uri:')
        for rdata in answers:
            print(rdata.to_text())
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN) as e:
        print(f'Eroare: Nu s-a găsit niciun răspuns pentru domeniul {domain}. Detalii: {e}')
    except Exception as e:
        print(f'Eroare generală: {e}')

# Funcție pentru a rezolva IP-ul într-un domeniu
def resolve_ip(ip, dns_server):
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [dns_server]  # Setăm serverul DNS utilizat
        
        # Verificăm dacă IP-ul este valid
        socket.inet_aton(ip)  # Verificăm dacă este o adresă IP validă
        
        # Căutăm domeniile asociate IP-ului
        reversed_ip = '.'.join(reversed(ip.split('.'))) + '.in-addr.arpa'
        answers = resolver.resolve(reversed_ip, 'PTR')  # 'PTR' pentru reverse lookup
        print(f'IP-ul {ip} este asociat cu domeniile:')
        for rdata in answers:
            print(rdata.to_text())
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN) as e:
        print(f'Eroare: Nu s-au găsit domenii pentru IP-ul {ip}. Detalii: {e}')
    except socket.error:
        print(f'Eroare: Adresa IP {ip} nu este validă.')
    except Exception as e:
        print(f'Eroare generală: {e}')

# Funcție pentru a verifica validitatea unui IP
def is_valid_ip(ip):
    try:
        socket.inet_aton(ip)  # Verificăm dacă IP-ul este valid
        return True
    except socket.error:
        return False

# Funcția principală
def main():
    dns_server = '1.1.1.1'  
    print(f'Folosind serverul DNS: {dns_server}')
    
    while True:
        command = input("Introduceți comanda: ").strip()
        
        if command.startswith("resolve"):
            parts = command.split()
            if len(parts) == 2:
                if is_valid_ip(parts[1]):  # Dacă este IP valid
                    resolve_ip(parts[1], dns_server)
                else:  # Dacă nu este IP, presupunem că este un domeniu
                    resolve_domain(parts[1], dns_server)
            else:
                print("Comandă invalidă! Folosiți: resolve <domain> sau resolve <ip>")
        
        elif command.startswith("use dns"):
            parts = command.split()
            if len(parts) == 3:
                try:
                    # Verificăm dacă adresa IP a serverului DNS este validă
                    if is_valid_ip(parts[2]):
                        dns_server = parts[2]
                        print(f'Server DNS schimbat la: {dns_server}')
                    else:
                        print("Eroare: Adresa IP a serverului DNS este invalidă.")
                except socket.error:
                    print("Eroare: Adresa IP a serverului DNS este invalidă.")
            else:
                print("Comandă invalidă! Folosiți: use dns <ip>")
        
        elif command.lower() == "exit":
            print("Ieșire din aplicație.")
            break

if __name__ == "__main__":
    main()