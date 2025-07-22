import pygame
import random
import sys

pygame.init()

# Starting screen size for level 1
BASE_WIDTH, BASE_HEIGHT = 700, 500
MAX_LEVEL = 10

screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT))
pygame.display.set_caption("Shadow Tag - Kid Friendly with Levels")

clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK = (40, 40, 40)
LIGHT_BLUE = (135, 206, 250)
BRIGHT_YELLOW = (255, 255, 0)
BRIGHT_RED = (255, 50, 50)
BRIGHT_GREEN = (50, 255, 50)
BRIGHT_PURPLE = (180, 0, 255)
PINK = (255, 105, 180)
ORANGE = (255, 165, 0)
GRAY = (180, 180, 180)

# Fonts
title_font = pygame.font.SysFont("Comic Sans MS", 60, bold=True)
button_font = pygame.font.SysFont("Comic Sans MS", 36, bold=True)
message_font = pygame.font.SysFont("Comic Sans MS", 40, bold=True)

# Game variables
player_size = 35
orb_size = 25
light_radius = 60

# Game states
MENU = "menu"
PLAYING = "playing"
LEVEL_COMPLETE = "level_complete"
GAME_OVER = "game_over"
GAME_WON = "game_won"

# Modes
SINGLE = "single"
TWO_PLAYER = "two_player"

# Player speeds
player_speed = 6
light_speed_base = 4  # base speed for AI light
light_speed = 5  # speed for 2P light

# Initialize global state
game_state = MENU
mode = SINGLE
level = 1

# Map size (starts at base size, increases with level)
def get_map_size(level):
    scale = 1 + (level - 1) * 0.15  # 15% bigger each level
    w = int(BASE_WIDTH * scale)
    h = int(BASE_HEIGHT * scale)
    return w, h

# Get AI light speed based on level to balance difficulty
def get_ai_speed(level):
    # Increase speed slightly each level, max 8
    return min(light_speed_base + level * 0.4, 8)

# Positions
player_pos = [0, 0]
player2_pos = [0, 0]
orb_pos = [0, 0]

# AI light will chase the player
def ai_move(light_pos, target_pos, speed):
    dx = target_pos[0] - light_pos[0]
    dy = target_pos[1] - light_pos[1]
    dist = (dx**2 + dy**2)**0.5
    if dist == 0:
        return light_pos
    move_x = speed * dx / dist
    move_y = speed * dy / dist
    new_x = light_pos[0] + move_x
    new_y = light_pos[1] + move_y

    # Keep light inside bounds
    new_x = max(light_radius, min(screen.get_width() - light_radius, new_x))
    new_y = max(light_radius, min(screen.get_height() - light_radius, new_y))
    return [new_x, new_y]

# Check collision helper
def rect_collision(pos1, size1, pos2, size2):
    return (
        pos1[0] < pos2[0] + size2 and
        pos1[0] + size1 > pos2[0] and
        pos1[1] < pos2[1] + size2 and
        pos1[1] + size1 > pos2[1]
    )

# Button class for menu and other buttons
class Button:
    def __init__(self, rect, color, text, text_color=BLACK):
        self.rect = pygame.Rect(rect)
        self.color = color
        self.text = text
        self.text_color = text_color
        self.hovered = False

    def draw(self, surf):
        col = self.color
        if self.hovered:
            col = tuple(min(255, c + 40) for c in self.color)
        pygame.draw.rect(surf, col, self.rect, border_radius=10)
        text_surf = button_font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surf.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

# Buttons
btn_single = Button((BASE_WIDTH//2 - 150, 200, 300, 70), BRIGHT_YELLOW, "Single Player")
btn_two = Button((BASE_WIDTH//2 - 150, 300, 300, 70), BRIGHT_PURPLE, "Two Players")
btn_quit = Button((BASE_WIDTH//2 - 75, 400, 150, 50), ORANGE, "Quit", WHITE)

btn_next_level = Button((0, 0, 200, 60), BRIGHT_GREEN, "Next Level")
btn_restart = Button((0, 0, 200, 60), BRIGHT_YELLOW, "Restart Game")
btn_quit_end = Button((0, 0, 200, 60), ORANGE, "Quit", WHITE)

def reset_game_positions():
    global player_pos, player2_pos, orb_pos
    w, h = screen.get_size()
    player_pos = [w // 2, h // 2]
    player2_pos = [w // 4, h // 4]
    orb_pos = [random.randint(0, w - orb_size), random.randint(0, h - orb_size)]

def draw_light_spot(pos):
    pygame.draw.circle(screen, LIGHT_BLUE, (int(pos[0]), int(pos[1])), light_radius)
    glow_surface = pygame.Surface((light_radius*4, light_radius*4), pygame.SRCALPHA)
    pygame.draw.circle(glow_surface, (135,206,250,60), (light_radius*2, light_radius*2), light_radius*2)
    screen.blit(glow_surface, (int(pos[0]) - light_radius*2, int(pos[1]) - light_radius*2))

def main_menu():
    screen.fill(DARK)
    title_surf = title_font.render("Shadow Tag", True, BRIGHT_YELLOW)
    title_rect = title_surf.get_rect(center=(screen.get_width()//2, 100))
    screen.blit(title_surf, title_rect)

    mouse_pos = pygame.mouse.get_pos()
    for btn in [btn_single, btn_two, btn_quit]:
        btn.check_hover(mouse_pos)
        btn.draw(screen)

def playing():
    global game_state, orb_pos

    keys = pygame.key.get_pressed()

    # Move Player 1 (shadow)
    if keys[pygame.K_LEFT]:
        player_pos[0] -= player_speed
    if keys[pygame.K_RIGHT]:
        player_pos[0] += player_speed
    if keys[pygame.K_UP]:
        player_pos[1] -= player_speed
    if keys[pygame.K_DOWN]:
        player_pos[1] += player_speed

    # Clamp player inside window
    w, h = screen.get_size()
    player_pos[0] = max(0, min(w - player_size, player_pos[0]))
    player_pos[1] = max(0, min(h - player_size, player_pos[1]))

    if mode == TWO_PLAYER:
        # Player 2 controls light with WASD
        if keys[pygame.K_a]:
            player2_pos[0] -= light_speed
        if keys[pygame.K_d]:
            player2_pos[0] += light_speed
        if keys[pygame.K_w]:
            player2_pos[1] -= light_speed
        if keys[pygame.K_s]:
            player2_pos[1] += light_speed

        player2_pos[0] = max(light_radius, min(w - light_radius, player2_pos[0]))
        player2_pos[1] = max(light_radius, min(h - light_radius, player2_pos[1]))

    else:
        # AI light chases player, speed increases by level
        current_ai_speed = get_ai_speed(level)
        player2_pos[:] = ai_move(player2_pos, player_pos, speed=current_ai_speed)

    # Check collision - player caught by light
    dist_x = player_pos[0] + player_size/2 - player2_pos[0]
    dist_y = player_pos[1] + player_size/2 - player2_pos[1]
    dist = (dist_x**2 + dist_y**2)**0.5
    if dist < light_radius:
        return "lose"

    # Check if player caught orb (win)
    if rect_collision(player_pos, player_size, orb_pos, orb_size):
        return "win"

    # Draw background
    screen.fill(DARK)

    # Draw light spot
    draw_light_spot(player2_pos)

    # Draw orb only if in shadow (not inside light)
    dist_orb_light = ((orb_pos[0] + orb_size/2 - player2_pos[0])**2 + (orb_pos[1] + orb_size/2 - player2_pos[1])**2)**0.5
    if dist_orb_light > light_radius:
        pygame.draw.rect(screen, BRIGHT_GREEN, (*orb_pos, orb_size, orb_size), border_radius=6)

    # Draw player (shadow)
    pygame.draw.rect(screen, BLACK, (*player_pos, player_size, player_size), border_radius=8)

    # Draw light player (circle)
    pygame.draw.circle(screen, LIGHT_BLUE, (int(player2_pos[0]), int(player2_pos[1])), light_radius, width=6)

    # Level display
    level_surf = button_font.render(f"Level: {level}", True, WHITE)
    screen.blit(level_surf, (10, 10))

    # Instructions
    instructions = button_font.render(
        "Arrows: Move shadow | WASD: Move light (2P)", True, WHITE)
    screen.blit(instructions, (20, screen.get_height() - 40))

    return None

def level_complete_screen():
    screen.fill(DARK)
    msg = f"Level {level} Complete!"
    text_surf = message_font.render(msg, True, BRIGHT_GREEN)
    text_rect = text_surf.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 50))
    screen.blit(text_surf, text_rect)

    mouse_pos = pygame.mouse.get_pos()
    btn_next_level.rect.center = (screen.get_width()//2, screen.get_height()//2 + 50)
    btn_next_level.check_hover(mouse_pos)
    btn_next_level.draw(screen)

def game_over_screen():
    screen.fill(DARK)
    msg = "Caught by light! Game Over!"
    text_surf = message_font.render(msg, True, BRIGHT_RED)
    text_rect = text_surf.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 50))
    screen.blit(text_surf, text_rect)

    mouse_pos = pygame.mouse.get_pos()
    btn_restart.rect.center = (screen.get_width()//2, screen.get_height()//2 + 20)
    btn_restart.check_hover(mouse_pos)
    btn_restart.draw(screen)

    btn_quit_end.rect.center = (screen.get_width()//2, screen.get_height()//2 + 90)
    btn_quit_end.check_hover(mouse_pos)
    btn_quit_end.draw(screen)

def game_won_screen():
    screen.fill(DARK)
    msg = "Congratulations! You won all levels!"
    text_surf = message_font.render(msg, True, BRIGHT_YELLOW)
    text_rect = text_surf.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 50))
    screen.blit(text_surf, text_rect)

    mouse_pos = pygame.mouse.get_pos()
    btn_restart.rect.center = (screen.get_width()//2, screen.get_height()//2 + 20)
    btn_restart.check_hover(mouse_pos)
    btn_restart.draw(screen)

    btn_quit_end.rect.center = (screen.get_width()//2, screen.get_height()//2 + 90)
    btn_quit_end.check_hover(mouse_pos)
    btn_quit_end.draw(screen)

def resize_screen_for_level(lvl):
    new_w, new_h = get_map_size(lvl)
    pygame.display.set_mode((new_w, new_h))
    return pygame.display.get_surface()

# Initialize screen and positions for level 1
screen = pygame.display.set_mode(get_map_size(level))
reset_game_positions()

running = True
result = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if game_state == MENU:
                if btn_single.clicked(pos):
                    mode = SINGLE
                    level = 1
                    screen = pygame.display.set_mode(get_map_size(level))
                    reset_game_positions()
                    game_state = PLAYING
                elif btn_two.clicked(pos):
                    mode = TWO_PLAYER
                    level = 1
                    screen = pygame.display.set_mode(get_map_size(level))
                    reset_game_positions()
                    game_state = PLAYING
                elif btn_quit.clicked(pos):
                    running = False

            elif game_state == LEVEL_COMPLETE:
                if btn_next_level.clicked(pos):
                    level += 1
                    if level > MAX_LEVEL:
                        game_state = GAME_WON
                    else:
                        screen = pygame.display.set_mode(get_map_size(level))
                        reset_game_positions()
                        game_state = PLAYING

            elif game_state == GAME_OVER:
                if btn_restart.clicked(pos):
                    level = 1
                    screen = pygame.display.set_mode(get_map_size(level))
                    reset_game_positions()
                    game_state = MENU
                elif btn_quit_end.clicked(pos):
                    running = False

            elif game_state == GAME_WON:
                if btn_restart.clicked(pos):
                    level = 1
                    screen = pygame.display.set_mode(get_map_size(level))
                    reset_game_positions()
                    game_state = MENU
                elif btn_quit_end.clicked(pos):
                    running = False

        elif event.type == pygame.KEYDOWN:
            if game_state == GAME_OVER:
                if event.key == pygame.K_r:
                    level = 1
                    screen = pygame.display.set_mode(get_map_size(level))
                    reset_game_positions()
                    game_state = MENU
                elif event.key == pygame.K_q:
                    running = False
            elif game_state == GAME_WON:
                if event.key == pygame.K_r:
                    level = 1
                    screen = pygame.display.set_mode(get_map_size(level))
                    reset_game_positions()
                    game_state = MENU
                elif event.key == pygame.K_q:
                    running = False

    if game_state == MENU:
        main_menu()
    elif game_state == PLAYING:
        result = playing()
        if result == "win":
            game_state = LEVEL_COMPLETE
        elif result == "lose":
            game_state = GAME_OVER
    elif game_state == LEVEL_COMPLETE:
        level_complete_screen()
    elif game_state == GAME_OVER:
        game_over_screen()
    elif game_state == GAME_WON:
        game_won_screen()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()


