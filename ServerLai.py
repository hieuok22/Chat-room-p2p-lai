# Server
import socket
import threading

SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345

chatters = {}

def handle_client_request(data, client_address, server_socket):
    global chatters
    request = data.decode('utf-8')

    if request.startswith("JOIN"):
        username = request.split()[1]
        chatters[username] = client_address
        print(f'{username} đã tham gia vào cuộc trò chuyện.')   
        send_chatters_list_to_all_clients()

        # Gửi danh sách các chatters cho client mới
        message = ""
        for chatter in chatters:
            ip, port = chatters[chatter]
            message += f"{chatter} {ip} {port}\n"
        server_socket.sendto(message.encode('utf-8'), client_address)
        
        # Gửi thông báo cho tất cả các client
        message = f"JOIN {username}"
        for address in chatters.values():
            server_socket.sendto(message.encode('utf-8'), address)

    elif request.startswith("LEAVE"):
        username = request.split()[1]
        # Xóa người dùng khỏi danh sách chatters
        if username in chatters:
            del chatters[username]
        send_chatters_list_to_all_clients()

         # Gửi thông báo "LEAVE" cho tất cả các client
        message = f"LEAVE {username}"
        for address in chatters.values():
            server_socket.sendto(message.encode('utf-8'), address)


#hàm send tất cả list tham gia trong chat
def send_chatters_list_to_all_clients():
    global chatters
    # Gửi danh sách các chatters đến tất cả client
    message = "\n".join([f"{username} {ip} {port}" for username, (ip, port) in chatters.items()])
    for address in chatters.values():
        server_socket.sendto(message.encode('utf-8'), address)

# Hàm lắng nghe yêu cầu từ client
def receive_requests(server_socket):
    while True:
        data, client_address = server_socket.recvfrom(1024)
        client_thread = threading.Thread(target=handle_client_request, args=(data, client_address, server_socket))
        client_thread.start()

         # Gửi danh sách các chatters đến client mới
        send_chatters_list_to_all_clients()

# Tạo socket UDP cho máy chủ
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

print(f'Server đang lắng nghe trên {SERVER_IP}:{SERVER_PORT}')

# Bắt đầu lắng nghe yêu cầu từ client
receive_thread = threading.Thread(target=receive_requests, args=(server_socket,))
receive_thread.start()

# Lặp để tiếp tục lắng nghe yêu cầu từ client
while True:
    pass
