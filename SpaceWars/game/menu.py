import pygame
import sys
import random
import subprocess
import os

pygame.init()

#alura/largura
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60

#cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BLUE = (20, 20, 50)
BUTTON_TEXT_COLOR = (20, 20, 60)
HIGHLIGHT = (100, 149, 237)

#configuração tela
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Wars")


class Button:
    def __init__(self, image, center_pos, callback):
        self.image = image
        self.callback = callback
        self.rect = self.image.get_rect(center=center_pos)

    def draw(self, surface, mouse_pos):
        surface.blit(self.image, self.rect)

    def check_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.callback()


class Menu:
    def __init__(self, tela):
        self.screen = tela
        self.running = True
        self.launch_game = False

        # Fonte (mantida)
        try:
            self.btn_font = pygame.font.Font("spacewars/game/fonte.ttf", 25)
        except pygame.error:
            self.btn_font = pygame.font.SysFont('consolas', 28, bold=True)

        # Fundo
        try:
            self.background = pygame.image.load("images/backgrounds/background_menu.jpg").convert()
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.has_bg_image = True
        except pygame.error:
            self.has_bg_image = False
            self.stars = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)) for _ in range(100)]

        #
        # ---------- 🔥 CARREGA E SEPARA OS BOTÕES DA IMAGEM ----------
        #
        buttons_img = pygame.image.load("images/backgrounds/buttons.png").convert_alpha()
        full_width = buttons_img.get_width()
        full_height = buttons_img.get_height()
        half_width = full_width // 2

        # recorte de cada botão
        btn_play_img = buttons_img.subsurface((0, 0, half_width, full_height))
        btn_exit_img = buttons_img.subsurface((half_width, 0, half_width, full_height))

        # posição dos botões
        mid_x = int(SCREEN_WIDTH * 0.72)
        btn_y = 320
        gap = 90

        # cria botões com imagem
        self.buttons = [
            Button(btn_play_img, (mid_x - gap, btn_y), self.start_game),
            Button(btn_exit_img, (mid_x + gap, btn_y), self.exit_game),
        ]

    def draw_background(self):
        if self.has_bg_image:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(DARK_BLUE)
            for star in self.stars:
                pygame.draw.circle(self.screen, WHITE, star, 2)

    def start_game(self):
        print("Iniciando Space Wars...")
        self.launch_game = True
        self.running = False

    def exit_game(self):
        pygame.quit()
        sys.exit()

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for btn in self.buttons:
                        btn.check_click(mouse_pos)

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.exit_game()

            self.draw_background()

            for btn in self.buttons:
                btn.draw(self.screen, mouse_pos)

            pygame.display.flip()
            clock.tick(FPS)


if __name__ == "__main__":
    menu = Menu(screen)
    menu.run()

    if getattr(menu, "launch_game", False):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            subprocess.Popen([sys.executable, os.path.join(script_dir, "game_base.py")], cwd=script_dir)
        except Exception as e:
            print("Falha ao iniciar o jogo:", e)
