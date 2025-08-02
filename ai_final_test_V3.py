import asyncio
import platform
import pygame
import sys
import random
import math

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
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
GRID_COLOR = (50, 50, 50)

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
        self.state = "menu"  # "menu", "ai_difficulty", "game"
        self.player1 = Player(100, 300, GRID_SIZE, 0, BLUE, "Player 1")
        self.player2 = Player(700, 300, -GRID_SIZE, 0, RED, "Player 2")
        self.player3 = None  # Used in Dual AI Mode for AI 2
        self.game_over = False
        self.player1_name = "Player 1"
        self.player2_name = "Player 2"
        self.active_input = None
        self.game_mode = None  # "two_player", "ai", "dual_ai"
        self.ai_difficulty = None  # "easy", "medium", "hard", "extreme"
        self.console_active = False
        self.god_mode = False
        self.ai_target_player = True

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
                if len(self.text) < 20:
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
two_player_button = Button(200, 400, 100, 50, "Two Player")
ai_mode_button = Button(350, 400, 100, 50, "AI Mode")
dual_ai_button = Button(500, 400, 150, 50, "Dual AI Mode")  # Increased width to 150
easy_button = Button(200, 300, 100, 50, "Easy")
medium_button = Button(350, 300, 100, 50, "Medium")
hard_button = Button(500, 300, 100, 50, "Hard")
extreme_button = Button(650, 300, 100, 50, "Extreme")
back_button = Button(350, 400, 100, 50, "Back")
console_input = InputBox(50, HEIGHT - 40, WIDTH - 100, 32, "")

def handle_menu_input():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if game_state.state == "menu":
            p1_active, game_state.player1_name = player1_input.handle_event(event)
            p2_active, game_state.player2_name = player2_input.handle_event(event)
            game_state.active_input = 'player1' if p1_active else 'player2' if p2_active else None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if two_player_button.is_clicked(event.pos):
                    game_state.game_mode = "two_player"
                    game_state.player1.name = game_state.player1_name
                    game_state.player2.name = game_state.player2_name
                    game_state.player3 = None
                    game_state.state = "game"
                    reset_game()
                elif ai_mode_button.is_clicked(event.pos):
                    game_state.state = "ai_difficulty"
                    game_state.game_mode = "ai"
                elif dual_ai_button.is_clicked(event.pos):
                    game_state.state = "ai_difficulty"
                    game_state.game_mode = "dual_ai"
        elif game_state.state == "ai_difficulty":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if easy_button.is_clicked(event.pos):
                    game_state.ai_difficulty = "easy"
                    game_state.player1.name = game_state.player1_name
                    game_state.player2.name = "AI 1"
                    game_state.player3 = Player(400, 100, 0, GRID_SIZE, GREEN, "AI 2") if game_state.game_mode == "dual_ai" else None
                    game_state.state = "game"
                    reset_game()
                elif medium_button.is_clicked(event.pos):
                    game_state.ai_difficulty = "medium"
                    game_state.player1.name = game_state.player1_name
                    game_state.player2.name = "AI 1"
                    game_state.player3 = Player(400, 100, 0, GRID_SIZE, GREEN, "AI 2") if game_state.game_mode == "dual_ai" else None
                    game_state.state = "game"
                    reset_game()
                elif hard_button.is_clicked(event.pos):
                    game_state.ai_difficulty = "hard"
                    game_state.player1.name = game_state.player1_name
                    game_state.player2.name = "AI 1"
                    game_state.player3 = Player(400, 100, 0, GRID_SIZE, GREEN, "AI 2") if game_state.game_mode == "dual_ai" else None
                    game_state.state = "game"
                    reset_game()
                elif extreme_button.is_clicked(event.pos):
                    game_state.ai_difficulty = "extreme"
                    game_state.player1.name = game_state.player1_name
                    game_state.player2.name = "AI 1"
                    game_state.player3 = Player(400, 100, 0, GRID_SIZE, GREEN, "AI 2") if game_state.game_mode == "dual_ai" else None
                    game_state.state = "game"
                    reset_game()
                elif back_button.is_clicked(event.pos):
                    game_state.state = "menu"

def draw_menu():
    screen.fill(BLACK)
    if game_state.state == "menu":
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
        two_player_button.draw(screen)
        ai_mode_button.draw(screen)
        dual_ai_button.draw(screen)
    elif game_state.state == "ai_difficulty":
        title = font.render("Select AI Difficulty", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        easy_button.draw(screen)
        medium_button.draw(screen)
        hard_button.draw(screen)
        extreme_button.draw(screen)
        back_button.draw(screen)

def ai_move(player, is_ai1):
    directions = [
        (GRID_SIZE, 0), (-GRID_SIZE, 0), (0, -GRID_SIZE), (0, GRID_SIZE)
    ]
    opposite = (-player.dx, -player.dy)
    directions = [d for d in directions if d != opposite]
    
    if game_state.ai_difficulty == "easy":
        max_steps = 20 if is_ai1 else 10
        trap_player = game_state.ai_target_player and not is_ai1
    elif game_state.ai_difficulty == "medium":
        max_steps = 30 if is_ai1 else 15
        trap_player = game_state.ai_target_player and not is_ai1
    elif game_state.ai_difficulty == "hard":
        max_steps = 40 if is_ai1 else 20
        trap_player = game_state.ai_target_player
    else:  # extreme
        max_steps = 60 if is_ai1 else 30
        trap_player = game_state.ai_target_player

    safe_directions = []
    scores = []
    all_trails = game_state.player1.trail[:-1] + game_state.player2.trail[:-1]
    if game_state.player3:
        all_trails += game_state.player3.trail[:-1]

    for dx, dy in directions:
        new_x, new_y = player.x + dx, player.y + dy
        if not (new_x < 0 or new_x >= WIDTH or new_y < 0 or new_y >= HEIGHT):
            collision = False
            for segment in all_trails:
                if (new_x, new_y) == segment:
                    collision = True
                    break
            if not collision:
                safe_directions.append((dx, dy))
                steps = 0
                x, y = new_x, new_y
                while 0 <= x < WIDTH and 0 <= y < HEIGHT and steps < max_steps:
                    if (x, y) in all_trails:
                        break
                    steps += 1
                    x += dx
                    y += dy
                score = steps
                if trap_player:
                    targets = [game_state.player1]
                    if game_state.player3 and player != game_state.player3:
                        targets.append(game_state.player3)
                    elif game_state.player2 and player != game_state.player2:
                        targets.append(game_state.player2)
                    min_dist = float('inf')
                    for target in targets:
                        dist = math.hypot(target.x - new_x, target.y - new_y)
                        min_dist = min(min_dist, dist)
                    score += max(0, 50 - min_dist) * (0.1 if is_ai1 else 0.3)
                scores.append(score)
    
    if safe_directions:
        if scores:
            best_idx = scores.index(max(scores))
            player.dx, player.dy = safe_directions[best_idx]
        else:
            player.dx, player.dy = random.choice(safe_directions)
    else:
        pass

def handle_game_input():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKQUOTE:
                game_state.console_active = not game_state.console_active
                console_input.active = game_state.console_active
                if not game_state.console_active:
                    console_input.text = ""
                    console_input.txt_surface = small_font.render("", True, WHITE)
            if game_state.console_active:
                console_active, command = console_input.handle_event(event)
                if event.key == pygame.K_RETURN and command:
                    if command.lower() == "god":
                        game_state.god_mode = not game_state.god_mode
                    elif command.lower() == "ainotarget":
                        game_state.ai_target_player = not game_state.ai_target_player
                    console_input.text = ""
                    console_input.txt_surface = small_font.render("", True, WHITE)
            else:
                if event.key == pygame.K_w and game_state.player1.dy != GRID_SIZE:
                    game_state.player1.dx, game_state.player1.dy = 0, -GRID_SIZE
                if event.key == pygame.K_s and game_state.player1.dy != -GRID_SIZE:
                    game_state.player1.dx, game_state.player1.dy = 0, GRID_SIZE
                if event.key == pygame.K_a and game_state.player1.dx != GRID_SIZE:
                    game_state.player1.dx, game_state.player1.dy = -GRID_SIZE, 0
                if event.key == pygame.K_d and game_state.player1.dx != -GRID_SIZE:
                    game_state.player1.dx, game_state.player1.dy = GRID_SIZE, 0
                if game_state.game_mode == "two_player":
                    if event.key == pygame.K_UP and game_state.player2.dy != GRID_SIZE:
                        game_state.player2.dx, game_state.player2.dy = 0, -GRID_SIZE
                    if event.key == pygame.K_DOWN and game_state.player2.dy != -GRID_SIZE:
                        game_state.player2.dx, game_state.player2.dy = 0, GRID_SIZE
                    if event.key == pygame.K_LEFT and game_state.player2.dx != GRID_SIZE:
                        game_state.player2.dx, game_state.player2.dy = -GRID_SIZE, 0
                    if event.key == pygame.K_RIGHT and game_state.player2.dx != -GRID_SIZE:
                        game_state.player2.dx, game_state.player2.dy = GRID_SIZE, 0
                if event.key == pygame.K_r and game_state.game_over:
                    reset_game()
                    game_state.state = "menu"

def check_collision(player):
    if player == game_state.player1 and game_state.god_mode:
        return False
    if player.x < 0 or player.x >= WIDTH or player.y < 0 or player.y >= HEIGHT:
        return True
    all_trails = game_state.player1.trail[:-1] + game_state.player2.trail[:-1]
    if game_state.player3:
        all_trails += game_state.player3.trail[:-1]
    for segment in all_trails:
        if (player.x, player.y) == segment:
            return True
    return False

def draw_player(player):
    pygame.draw.rect(screen, player.color, (player.x, player.y, GRID_SIZE, GRID_SIZE))
    for x, y in player.trail:
        pygame.draw.rect(screen, player.color, (x, y, GRID_SIZE, GRID_SIZE))

def draw_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))

def draw_console():
    if game_state.console_active:
        pygame.draw.rect(screen, BLACK, (50, HEIGHT - 40, WIDTH - 100, 32))
        pygame.draw.rect(screen, WHITE, console_input.rect, 2)
        screen.blit(console_input.txt_surface, (console_input.rect.x + 5, console_input.rect.y + 5))

def reset_game():
    game_state.player1 = Player(100, 300, GRID_SIZE, 0, BLUE, game_state.player1_name)
    game_state.player2 = Player(700, 300, -GRID_SIZE, 0, RED, game_state.player2_name if game_state.game_mode == "two_player" else "AI 1")
    if game_state.game_mode == "dual_ai":
        game_state.player3 = Player(400, 100, 0, GRID_SIZE, GREEN, "AI 2")
    else:
        game_state.player3 = None
    game_state.game_over = False
    game_state.god_mode = False
    game_state.ai_target_player = True

async def main():
    def setup():
        pass  # Pygame initialized above

    def update_loop():
        if game_state.state in ["menu", "ai_difficulty"]:
            handle_menu_input()
            draw_menu()
        elif game_state.state == "game":
            handle_game_input()
            if game_state.game_mode in ["ai", "dual_ai"] and not game_state.game_over:
                ai_move(game_state.player2, is_ai1=True)
                if game_state.player3:
                    ai_move(game_state.player3, is_ai1=False)
            if not game_state.game_over:
                game_state.player1.x += game_state.player1.dx
                game_state.player1.y += game_state.player1.dy
                game_state.player2.x += game_state.player2.dx
                game_state.player2.y += game_state.player2.dy
                game_state.player1.trail.append((game_state.player1.x, game_state.player1.y))
                game_state.player2.trail.append((game_state.player2.x, game_state.player2.y))
                if game_state.player3:
                    game_state.player3.x += game_state.player3.dx
                    game_state.player3.y += game_state.player3.dy
                    game_state.player3.trail.append((game_state.player3.x, game_state.player3.y))
                if (check_collision(game_state.player1) or 
                    check_collision(game_state.player2) or 
                    (game_state.player3 and check_collision(game_state.player3))):
                    game_state.game_over = True
            screen.fill(BLACK)
            draw_grid()
            draw_player(game_state.player1)
            draw_player(game_state.player2)
            if game_state.player3:
                draw_player(game_state.player3)
            if game_state.game_over:
                winners = []
                if not check_collision(game_state.player1):
                    winners.append(game_state.player1.name)
                if not check_collision(game_state.player2):
                    winners.append(game_state.player2.name)
                if game_state.player3 and not check_collision(game_state.player3):
                    winners.append(game_state.player3.name)
                winner_text = "No one" if not winners else " and ".join(winners)
                text = font.render(f"Game Over! {winner_text} wins! Press R to Restart", True, WHITE)
                text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
                screen.blit(text, text_rect)
            draw_console()
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
