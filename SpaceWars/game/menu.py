import pygame
import sys
import random

# Inicialização
pygame.init()

# Constantes de Tela
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BLUE = (20, 20, 50)
BUTTON_BG = (240, 240, 240)
BUTTON_TEXT_COLOR = (20, 20, 60)
HIGHLIGHT = (100, 149, 237)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Wars")

class Button:
    def __init__(self, text, center_pos, font, callback, width=160, height=50):
        self.text = text
        self.callback = callback
        self.font = font
        self.width = width
        self.height = height
        self.pos = center_pos
        
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.pos
        
        # Renderiza o texto
        self.text_surf = self.font.render(self.text, True, BUTTON_TEXT_COLOR)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def draw(self, surface, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(surface, HIGHLIGHT, self.rect)
            pygame.draw.rect(surface, WHITE, self.rect, 3)
        else:
            pygame.draw.rect(surface, BUTTON_BG, self.rect)
            pygame.draw.rect(surface, (100, 100, 100), self.rect, 3)
        
        surface.blit(self.text_surf, self.text_rect)

    def check_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.callback()

class Menu:
    def __init__(self, tela):
        self.screen = tela
        self.running = True
        
        
        try:
            
            self.btn_font = pygame.font.Font("SpaceWars/game/fonte.ttf", 25) 
        except pygame.error:
            print("Aviso: Arquivo 'fonte.ttf' não encontrado. Usando fonte padrão.")
            self.btn_font = pygame.font.SysFont('consolas', 28, bold=True)

       
        try:
            self.background = pygame.image.load("SpaceWars/game/background.jpg").convert()
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.has_bg_image = True
        except pygame.error:
            self.has_bg_image = False
            self.stars = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)) for _ in range(100)]

        # --- POSICIONAMENTO DOS BOTÕES ---
        mid_x = int(SCREEN_WIDTH * 0.72)  
        btn_y = 320
        gap = 89

        self.buttons = [
            Button("PLAY", (mid_x - gap, btn_y), self.btn_font, self.start_game),
            Button("EXIT", (mid_x + gap, btn_y), self.btn_font, self.exit_game),
        ]

    def draw_background(self):
        if self.has_bg_image:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(DARK_BLUE)
            for star in self.stars:
                pygame.draw.circle(self.screen, WHITE, star, 2)
            pygame.draw.circle(self.screen, (100, 100, 200), (150, 450), 100) 
            pygame.draw.ellipse(self.screen, (150, 150, 250), (40, 400, 220, 100), 5)

    def start_game(self):
        print("Iniciando Space Wars...")
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