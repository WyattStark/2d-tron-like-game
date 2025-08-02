import asyncio
import platform
import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 10
FPS = 10

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tron 2D Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 36)
small_font = pygame.font.SysFont('Arial', 24)

# Player class
class Player:
    def __init__(self, x, y, dx, dy, color, name):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.name = name
        self.trail = [(x, y)]

# Game state
class GameState:
    def __init__(self):
        self.state = "menu"
        self.player1 = Player(100, 300, GRID_SIZE, 0, BLUE, "Player 1")
        self.player2 = Player(700, 300, -GRID_SIZE, 0, RED, "Player 2")
        self.game_over = False
        self.player1_name = "Player 1"
        self.player2_name = "Player 2"
        self.active_input = None

game_state = GameState()

# Input box class
class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = WHITE
        self.text = text
        self.txt_surface = small_font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(self.text) < 10:  # Limit name length
                    self.text += event.unicode
            self.txt_surface = small_font.render(self.text, True, self.color)
        return self.active, self.text

# Button class
class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = GRAY
        self.text = text
        self.txt_surface = small_font.render(text, True, BLACK)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.txt_surface, (self.rect.x + (self.rect.w - self.txt_surface.get_width()) // 2,
                                      self.rect.y + (self.rect.h - self.txt_surface.get_height()) // 2))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Initialize menu elements
player1_input = InputBox(200, 300, 140, 32, "Player 1")
player2_input = InputBox(460, 300, 140, 32, "Player 2")
start_button = Button(350, 400, 100, 50, "Start Game")

def handle_menu_input():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        p1_active, game_state.player1_name = player1_input.handle_event(event)
        p2_active, game_state.player2_name = player2_input.handle_event(event)
        game_state.active_input = 'player1' if p1_active else 'player2' if p2_active else None
        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.is_clicked(event.pos):
                game_state.player1.name = game_state.player1_name
                game_state.player2.name = game_state.player2_name
                game_state.state = "game"
                reset_game()

def draw_menu():
    screen.fill(BLACK)
    title = font.render("Tron 2D Game", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
    player1_label = small_font.render("Player 1 Name:", True, WHITE)
    player2_label = small_font.render("Player 2 Name:", True, WHITE)
    screen.blit(player1_label, (200, 270))
    screen.blit(player2_label, (460, 270))
    player1_input.color = BLUE if player1_input.active else WHITE
    player2_input.color = RED if player2_input.active else WHITE
    pygame.draw.rect(screen, player1_input.color, player1_input.rect, 2)
    pygame.draw.rect(screen, player2_input.color, player2_input.rect, 2)
    screen.blit(player1_input.txt_surface, (player1_input.rect.x + 5, player1_input.rect.y + 5))
    screen.blit(player2_input.txt_surface, (player2_input.rect.x + 5, player2_input.rect.y + 5))
    start_button.draw(screen)

def handle_game_input():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            # Player 1 controls (WASD)
            if event.key == pygame.K_w and game_state.player1.dy != GRID_SIZE:
                game_state.player1.dx, game_state.player1.dy = 0, -GRID_SIZE
            if event.key == pygame.K_s and game_state.player1.dy != -GRID_SIZE:
                game_state.player1.dx, game_state.player1.dy = 0, GRID_SIZE
            if event.key == pygame.K_a and game_state.player1.dx != GRID_SIZE:
                game_state.player1.dx, game_state.player1.dy = -GRID_SIZE, 0
            if event.key == pygame.K_d and game_state.player1.dx != -GRID_SIZE:
                game_state.player1.dx, game_state.player1.dy = GRID_SIZE, 0
            # Player 2 controls (Arrows)
            if event.key == pygame.K_UP and game_state.player2.dy != GRID_SIZE:
                game_state.player2.dx, game_state.player2.dy = 0, -GRID_SIZE
            if event.key == pygame.K_DOWN and game_state.player2.dy != -GRID_SIZE:
                game_state.player2.dx, game_state.player2.dy = 0, GRID_SIZE
            if event.key == pygame.K_LEFT and game_state.player2.dx != GRID_SIZE:
                game_state.player2.dx, game_state.player2.dy = -GRID_SIZE, 0
            if event.key == pygame.K_RIGHT and game_state.player2.dx != -GRID_SIZE:
                game_state.player2.dx, game_state.player2.dy = GRID_SIZE, 0
            # Restart game
            if event.key == pygame.K_r and game_state.game_over:
                reset_game()
                game_state.state = "menu"

def check_collision(player):
    # Wall collision
    if player.x < 0 or player.x >= WIDTH or player.y < 0 or player.y >= HEIGHT:
        return True
    # Trail collision
    for segment in game_state.player1.trail[:-1] + game_state.player2.trail[:-1]:
        if (player.x, player.y) == segment:
            return True
    return False

def draw_player(player):
    pygame.draw.rect(screen, player.color, (player.x, player.y, GRID_SIZE, GRID_SIZE))
    for x, y in player.trail:
        pygame.draw.rect(screen, player.color, (x, y, GRID_SIZE, GRID_SIZE))

def reset_game():
    game_state.player1 = Player(100, 300, GRID_SIZE, 0, BLUE, game_state.player1_name)
    game_state.player2 = Player(700, 300, -GRID_SIZE, 0, RED, game_state.player2_name)
    game_state.game_over = False

async def main():
    def setup():
        pass  # Pygame initialized above

    def update_loop():
        if game_state.state == "menu":
            handle_menu_input()
            draw_menu()
        elif game_state.state == "game":
            handle_game_input()
            if not game_state.game_over:
                # Update positions
                game_state.player1.x += game_state.player1.dx
                game_state.player1.y += game_state.player1.dy
                game_state.player2.x += game_state.player2.dx
                game_state.player2.y += game_state.player2.dy

                # Add to trails
                game_state.player1.trail.append((game_state.player1.x, game_state.player1.y))
                game_state.player2.trail.append((game_state.player2.x, game_state.player2.y))

                # Check collisions
                if check_collision(game_state.player1) or check_collision(game_state.player2):
                    game_state.game_over = True

            # Draw
            screen.fill(BLACK)
            draw_player(game_state.player1)
            draw_player(game_state.player2)

            if game_state.game_over:
                text = font.render(f"Game Over! Press R to Restart", True, WHITE)
                text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
                screen.blit(text, text_rect)

        pygame.display.flip()

    setup()
    while True:
        update_loop()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
