import socket
import ssl
import urllib.parse
import time
import sys

def menu():
    print("Menu:")
    print("1 - Search person in CPF database by name")
    print("2 - Search person in CPF database by exact name")
    print("3 - Search person in CPF database by CPF")
    print("4 - Search person in CNPJ database by name")
    print("5 - Search person in CNPJ database by both name and CPF")
    print("6 - Search person in CNPJ database with company details")
    print("7 - Test server connection (health check)")
    print("0 - Exit")
    choice = input("Enter your choice: ")
    return choice

def send_https_request(sock, path):
    request = f"GET {path} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
    sock.sendall(request.encode())

    # Aumentar o timeout para receber a resposta completa
    sock.settimeout(60.0)  # 60 segundos para respostas maiores

    # Receber a resposta
    print("Aguardando resposta do servidor...")
    response = b""
    start_time = time.time()

    # Inicialmente, vamos tentar obter pelo menos os headers
    while b"\r\n\r\n" not in response:
        try:
            chunk = sock.recv(8192)  # Aumentei o tamanho do buffer
            if not chunk:
                break
            response += chunk
            if time.time() - start_time > 60:  # Timeout de segurança
                print("Tempo limite excedido ao receber headers.")
                break
        except socket.timeout:
            print("Timeout ao aguardar headers.")
            break

    # Se não conseguimos os headers, retorna o que tiver
    if b"\r\n\r\n" not in response:
        print("Resposta incompleta recebida (sem headers completos).")
        return response.decode('utf-8', errors='ignore')

    # Dividir em headers e corpo
    headers_raw, body = response.split(b"\r\n\r\n", 1)
    headers = headers_raw.decode('utf-8', errors='ignore')
    # Verificar se há Content-Length

    content_length = None
    for line in headers.splitlines():
        if line.lower().startswith('content-length:'):
            content_length = int(line.split(':', 1)[1].strip())
            break

    # Se conhecemos o tamanho do corpo, continuamos recebendo até obtê-lo completo
    if content_length is not None:
        print(f"Esperando corpo da resposta ({content_length} bytes)...")
        while len(body) < content_length:
            try:
                chunk = sock.recv(8192)
                if not chunk:
                    print("Conexão fechada antes de receber o corpo completo.")
                    break
                body += chunk
                print(f"Recebido: {len(body)}/{content_length} bytes")
                if time.time() - start_time > 120:  # 2 minutos no máximo
                    print("Tempo limite excedido ao receber corpo.")
                    break
            except socket.timeout:
                print("Timeout ao aguardar corpo da resposta.")
                break
    else:
        # Se não temos Content-Length, continuamos recebendo até a conexão fechar
        print("Recebendo resposta de tamanho desconhecido...")
        while True:
            try:
                chunk = sock.recv(8192)
                if not chunk:
                    break
                body += chunk
                print(f"Recebido mais {len(chunk)} bytes...")
                if time.time() - start_time > 120:  # 2 minutos no máximo
                    print("Tempo limite excedido.")
                    break
            except socket.timeout:
                # Timeout pode significar que acabou
                break

    # Retornar o corpo da resposta
    try:
        total_time = time.time() - start_time
        print(f"Resposta completa recebida em {total_time:.2f} segundos ({len(body)} bytes).")
        return body.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Erro ao decodificar resposta: {e}")
        return f"Erro na decodificação: {len(body)} bytes recebidos"

def connect_to_server(host, port, path, timeout=30.0):
    # Create SSL context with proper configuration
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE  # Skip certificate verification (use in dev only)

    try:
        # Create a new socket for the request
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        wrapped_sock = context.wrap_socket(sock, server_hostname=host)

        print(f"Conectando a {host}:{port}...")
        wrapped_sock.connect((host, port))
        print("Conexão estabelecida. Enviando requisição...")

        result = send_https_request(wrapped_sock, path)
        return result
    except ConnectionRefusedError:
        print(f"Erro: Conexão recusada pelo servidor em {host}:{port}.")
        print("Verifique se o servidor está rodando e se a porta está correta.")
        return None
    except socket.timeout:
        print(f"Erro: Timeout ao conectar ao servidor em {host}:{port}")
        return None
    except Exception as e:
        print(f"Erro ao conectar ao servidor: {e}")
        return None
    finally:
        try:
            wrapped_sock.close()
        except:
            pass
        try:
            sock.close()
        except:
            pass

def main():
    # Default configuration
    DEFAULT_PORT = 5000  # Alterado para 5000 para corresponder ao servidor

    # Check command line arguments for host and port
    if len(sys.argv) > 1:
        HOST = sys.argv[1]
    else:
        # Try to get local IP, fallback to localhost
        try:
            HOST = socket.gethostbyname(socket.gethostname())
        except:
            HOST = "localhost"

    if len(sys.argv) > 2:
        try:
            PORT = int(sys.argv[2])
        except ValueError:
            print(f"Porta inválida, usando a padrão: {DEFAULT_PORT}")
            PORT = DEFAULT_PORT
    else:
        PORT = DEFAULT_PORT

    print(f"Cliente configurado para conectar em {HOST}:{PORT}")
    print("Você pode especificar o host e porta como argumentos: python client.py <host> <port>")

    # Set longer timeout for SSL handshake
    socket.setdefaulttimeout(30.0)

    while True:
        choice = menu()
        if choice == '1':
            name = input("Enter name: ")
            path = f"/get-person-by-name/{urllib.parse.quote(name)}"
            result = connect_to_server(HOST, PORT, path)
            if result:
                print("\n--- RESULTADO DA PESQUISA ---\n")
                print(result)

        elif choice == '2':
            name = input("Enter exact name: ")
            path = f"/get-person-by-exact-name/{urllib.parse.quote(name)}"
            result = connect_to_server(HOST, PORT, path)
            if result:
                print("\n--- RESULTADO DA PESQUISA ---\n")
                print(result)

        elif choice == '3':
            cpf = input("Enter CPF: ")
            path = f"/get-person-by-cpf/{cpf}"
            result = connect_to_server(HOST, PORT, path)
            if result:
                print("\n--- RESULTADO DA PESQUISA ---\n")
                print(result)

        elif choice == '4':
            name = input("Enter name: ")
            path = f"/get-person-cnpj-by-name/{urllib.parse.quote(name)}"
            result = connect_to_server(HOST, PORT, path)
            if result:
                print("\n--- RESULTADO DA PESQUISA ---\n")
                print(result)

        elif choice == '5':
            name = input("Enter exact name: ")
            cpf = input("Enter CPF: ")
            path = f"/get-person-cnpj-by-name-cpf/{urllib.parse.quote(name)}-{urllib.parse.quote(cpf)}"
            result = connect_to_server(HOST, PORT, path)
            if result:
                print("\n--- RESULTADO DA PESQUISA ---\n")
                print(result)

        elif choice == '6':
            name = input("Enter name: ")
            cpf = input("Enter CPF: ")
            path = f"/get-person-cnpj-by-name-cpf-radical/{urllib.parse.quote(name)}-{urllib.parse.quote(cpf)}"
            result = connect_to_server(HOST, PORT, path)
            if result:
                print("\n--- RESULTADO DA PESQUISA ---\n")
                print(result)

        elif choice == '7':
            print("Testando conexão com o servidor (health check)...")
            path = "/health"
            result = connect_to_server(HOST, PORT, path, timeout=5.0)
            if result:
                print("\n--- RESULTADO DO HEALTH CHECK ---\n")
                print(result)
                print("\nServidor está funcionando corretamente.")
            else:
                print("\nNão foi possível conectar ao servidor!")
                retry = input("Deseja tentar outra porta? (s/n): ")
                if retry.lower() == 's':
                    try:
                        new_port = int(input("Digite o número da porta: "))
                        PORT = new_port
                        print(f"Porta atualizada para: {PORT}")
                    except ValueError:
                        print("Valor de porta inválido, mantendo a porta atual.")

        elif choice == '0':
            print("Saindo do programa...")
            break

        else:
            print("Opção inválida, tente novamente.")

        print("\n" + "-"*50 + "\n")

if __name__ == "__main__":
    main()
