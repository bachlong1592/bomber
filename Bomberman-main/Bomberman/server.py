import socket
from _thread import *
import threading
import pickle
from game import Game
from game import GameState

server = "192.168.1.17"
port = 5547
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Tạo một socket TCP/IP
server_socket.bind((server, port)) # Bind socket đến một địa chỉ và cổng cụ thể
server_socket.listen(4)
print("Server đã khởi động, đang chờ client kết nối")

connected_clients = []
games = {}  # từ điển trống - {game_id, game}
games_id_counter = 0

games_lock = threading.Lock()  # đối tượng khóa bảo vệ từ điển games


# cho mỗi client, một luồng mới được khởi động
def threaded_handle_client(client_socket, player_number, game_id):
    global games_id_counter
    # gửi phản hồi đầu tiên cho client - số thứ tự của player
    client_socket.send(pickle.dumps(player_number))
    with games_lock:
        games[game_id].add_player(player_number)

    # vòng lặp giao tiếp server - client
    while True:
        try:
            # nhận các phím đã được nhấn từ client
            keys = pickle.loads(client_socket.recv(2048*2))
            with games_lock:
                games[game_id].react_to_keys(keys, player_number)
                games[game_id].activate_bombs()
                games[game_id].check_if_ended()

                if game_id in games:  # kiểm tra xem trò chơi vẫn có tồn tại không
                    game = games[game_id]
                    # gửi lại thông tin trò chơi để vẽ trạng thái trò chơi
                    client_socket.sendall(pickle.dumps(game.get_game_info()))
                else:
                    print("Trò chơi không tồn tại")
                    break
        except:
            print("Vấn đề giao tiếp")
            break

    print("Client đã ngắt kết nối")
    try:
        with games_lock:
            del games[game_id]  # xóa trò chơi
            print("Đóng trò chơi, id: ", game_id)
    except:
        pass  # người chơi khác đã xóa trò chơi trước đó
    games_id_counter -= 1
    client_socket.close()


while True:
    # accept() trả về một socket mới và địa chỉ của client đã kết nối
    client_socket, client_address = server_socket.accept()
    print("Client mới, địa chỉ: ", client_address)

    game_id = games_id_counter // 4  # với mỗi 4 client, game_id không thay đổi
    games_id_counter += 1

    if games_id_counter % 4 == 1:
        with games_lock:
            games[game_id] = Game(game_id)  # thêm mục mới vào từ điển
            print("Trò chơi mới được tạo, id: ", game_id)
    if games_id_counter % 4 == 0:
        with games_lock:
            games[game_id].game_state = GameState.STARTED
            print("4 người chơi đã tham gia, trò chơi bắt đầu, id: ", game_id)
            print(games[game_id].game_state)


    player_number = games_id_counter % 4
    # bắt đầu luồng mới cho mỗi client
    start_new_thread(threaded_handle_client, (client_socket, player_number, game_id))
