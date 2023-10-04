import socket
import threading
import random

SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345

chatters = {}

def receive_messages(client_socket):
    global chatters

    while True:
        try:
            data, _ = client_socket.recvfrom(1024)
            message = data.decode('utf-8')

            # Nếu nhận được danh sách các chatters từ server hoặc từ một client khác
            if "\n" in message:
                chatters.clear()
                for line in message.split("\n"):
                    if line:
                        username, ip, port = line.split()
                        chatters[username] = (ip, int(port))
                # Hiển thị danh sách người dùng trên giao diện người dùng của client
                print("Danh sách người dùng:")
                for username in chatters:
                    print(username)
                    
            else:
                print(message)
                if message.startswith("LEAVE"):
                    print("Bạn đã rời khỏi nhóm.")
                    break

        except ConnectionResetError:
            print("Mất kết nối với máy chủ.")
            break

username = input("Nhập tên của bạn: ")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

join_request = f"JOIN {username}".encode('utf-8')
client_socket.sendto(join_request, (SERVER_IP, SERVER_PORT))

receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
receive_thread.start()

while True:
    recipient = input("Nhập tên người nhận: ")
    message = input("Nhập tin nhắn của bạn: ")
    
    # Nếu muốn rời khỏi cuộc trò chuyện
    if message == "LEAVE":
        leave_request = f"LEAVE {username}".encode('utf-8')
        client_socket.sendto(leave_request, (SERVER_IP, SERVER_PORT))
        break

    message_data = f"MESSAGE {username}: {message}".encode('utf-8')

    # Gửi tin nhắn tới người nhận đã chỉ định
    if recipient in chatters:
        client_socket.sendto(message_data, chatters[recipient])
    else:
        print(f"Không tìm thấy người dùng {recipient}")
    
    # Nếu muốn tham gia vào cuộc trò chuyện khi server bị tắt
    if message == "JOIN":
        
        # Chọn ngẫu nhiên một số client trong danh sách chatters và gửi yêu cầu JOIN cho họ
        num_peers = min(3, len(chatters))
        peers = random.sample(list(chatters.values()), num_peers)
        
        for peer in peers:
            client_socket.sendto(join_request, peer)
