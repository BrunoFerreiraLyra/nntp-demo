import socket
import threading

groups = {
    "comp.networking": [
        "From: professor@nntp.com\r\nSubject: Bem-vindo ao NNTP\r\n\r\nEste e um artigo de exemplo sobre redes de computadores.",
        "From: aluno@nntp.com\r\nSubject: Como funciona o NNTP?\r\n\r\nO NNTP usa comandos de texto simples para trocar mensagens."
    ],
    "alt.test": [
        "From: teste@nntp.com\r\nSubject: Teste NNTP ao vivo\r\n\r\nEste artigo foi postado durante a apresentacao!"
    ]
}

def handle_client(conn, addr):
    print("[+] Cliente conectado: " + str(addr))
    conn.sendall(b"200 Servidor NNTP Pronto - Bem-vindo!\r\n")
    current_group = None

    while True:
        try:
            data = conn.recv(1024).decode().strip()
            if not data:
                break
            print("[>] Comando recebido: " + data)
            cmd = data.upper().split()[0]

            if cmd == "HELP":
                conn.sendall(b"100 Comandos disponiveis:\r\nLIST - Lista grupos\r\nGROUP - Seleciona grupo\r\nARTICLE - Le artigo\r\nPOST - Posta artigo\r\nQUIT - Encerra\r\n.\r\n")

            elif cmd == "LIST":
                resp = "215 Lista de newsgroups disponiveis\r\n"
                for g in groups:
                    resp += g + " " + str(len(groups[g])) + " 1 y\r\n"
                resp += ".\r\n"
                conn.sendall(resp.encode())

            elif cmd == "GROUP":
                parts = data.split()
                if len(parts) > 1 and parts[1] in groups:
                    current_group = parts[1]
                    n = len(groups[current_group])
                    conn.sendall(("211 " + str(n) + " 1 " + str(n) + " " + current_group + " - Grupo selecionado!\r\n").encode())
                else:
                    conn.sendall(b"411 Grupo nao encontrado\r\n")

            elif cmd == "ARTICLE":
                parts = data.split()
                if current_group and len(groups[current_group]) > 0:
                    idx = int(parts[1]) - 1 if len(parts) > 1 else 0
                    if 0 <= idx < len(groups[current_group]):
                        art = groups[current_group][idx]
                        conn.sendall(("220 " + str(idx+1) + " Artigo encontrado\r\n" + art + "\r\n.\r\n").encode())
                    else:
                        conn.sendall(b"423 Artigo nao encontrado\r\n")
                else:
                    conn.sendall(b"420 Nenhum grupo selecionado\r\n")

            elif cmd == "POST":
                conn.sendall(b"340 Pode enviar o artigo. Termine com . em linha separada\r\n")
                article = ""
                while True:
                    line = conn.recv(1024).decode()
                    if line.strip() == ".":
                        break
                    article += line
                if current_group:
                    groups[current_group].append(article)
                    total = len(groups[current_group])
                    conn.sendall(("240 Artigo postado com sucesso! Total no grupo: " + str(total) + "\r\n").encode())
                else:
                    conn.sendall(b"440 Selecione um grupo antes de postar\r\n")

            elif cmd == "QUIT":
                conn.sendall(b"205 Ate logo! Conexao encerrada.\r\n")
                break

            else:
                conn.sendall(b"500 Comando nao reconhecido. Digite HELP para ajuda.\r\n")

        except Exception as e:
            print("[!] Erro: " + str(e))
            break

    conn.close()
    print("[-] Cliente desconectado: " + str(addr))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', 1119))
server.listen(5)
print("========================================")
print("Servidor NNTP rodando na porta 1119")
print("Aguardando conexoes...")
print("========================================")

while True:
    conn, addr = server.accept()
    t = threading.Thread(target=handle_client, args=(conn, addr))
    t.daemon = True
    t.start()
