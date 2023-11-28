import pygame
from network import Network
from game import BlockType
from game import Keys
from game import GameState
import traceback  # errors

screen_width = 500
screen_height = 500
window = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Bomber")
pygame.font.init()
font = pygame.font.Font(None, 36)


def draw_window(game_info, player_number):
    board = game_info[0]
    players = game_info[1]
    bombs = game_info[2]
    game_state = game_info[3]

    if game_state == GameState.WAITING:
        str = "Chờ người chơi"
    if game_state == GameState.STARTED:
        str = "Bắt đầu trò chơi"
    if game_state == GameState.ENDED:
        str = "Kết thúc trò chơi"
    window.fill((0, 0, 0))
    game_state_text = font.render(str, True, (255, 255, 255))
    window.blit(game_state_text, (80, 425))

    if game_state == GameState.ENDED:
        winner_color = (0, 0, 0)
        for player_id, player in players.items():
            if player.isDead is False:
                winner_color = player.color
        pygame.draw.rect(window, winner_color, (100, 460, 20, 20))
        winner_text = font.render("Thắng", True, (255, 255, 255))
        window.blit(winner_text, (130, 460))

    for block_rect, block_type in board:
        if block_type == BlockType.EMPTY:
            color = (255, 255, 255)  # trắng
        elif block_type == BlockType.WALL:
            color = (25, 25, 25)  # xám
        else:
            color = (75, 32, 0)

        pygame.draw.rect(window, color, block_rect)

    for player_id, player in players.items():
        if player.isDead is False:
            pygame.draw.rect(window, player.color, player.rect)

    for i in range(len(bombs)):
        pygame.draw.rect(window, (255, 165, 0), bombs[i][0])

    pygame.display.flip()


def get_keys_pressed():
    keys = {}  # từ điển (Keys.key, isClicked)
    pygame_keys = pygame.key.get_pressed()
    keys[Keys.LEFT] = False
    keys[Keys.RIGHT] = False
    keys[Keys.UP] = False
    keys[Keys.DOWN] = False
    keys[Keys.SPACE] = False

    if pygame_keys[pygame.K_LEFT]:
        keys[Keys.LEFT] = True
    if pygame_keys[pygame.K_RIGHT]:
        keys[Keys.RIGHT] = True
    if pygame_keys[pygame.K_UP]:
        keys[Keys.UP] = True
    if pygame_keys[pygame.K_DOWN]:
        keys[Keys.DOWN] = True
    if pygame_keys[pygame.K_SPACE]:
        keys[Keys.SPACE] = True
    return keys


def run_game():
    clock = pygame.time.Clock()  # để duy trì FPS
    network = Network()  # tạo đối tượng Network để giao tiếp với server
    player_number = network.connect()

    game_running = True
    while game_running:
        clock.tick(60)
        keys = get_keys_pressed()

        try:
            game_info = network.send(keys)
        except:
            game_running = False
            print("Lỗi: Giao tiếp client-server")
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
                pygame.quit()
                break

        try:
            draw_window(game_info, player_number)
        except:
            print("Lỗi khi vẽ màn hình, đã mất kết nối")


run_game()
