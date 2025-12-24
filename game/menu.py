import pygame
import sys
import random
import os
import subprocess
import time
import cv2


def play_intro_video(screen):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(script_dir,"abertura_spacewars.mp4")

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Erro ao abrir o vídeo da intro")
        return

    clock = pygame.time.Clock()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (screen.get_width(), screen.get_height()))
        frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))

        screen.blit(frame, (0, 0))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                cap.release()
                return  
        clock.tick(30)  

    cap.release()


pygame.init()
pygame.mixer.init() 

SCREEN_WIDTH = 1280      
SCREEN_HEIGHT = 720
FPS = 60

WHITE = (255, 255, 255)
DARK_BLUE = (20, 20, 50)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Wars")

class Button:
    def __init__(self, image, center_pos, callback):
        self.image = image
        self.rect = self.image.get_rect(center=center_pos)
        self.callback = callback

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
        
        script_dir = os.path.dirname(os.path.abspath(__file__))


        music_path = os.path.join(script_dir, "Sounds", "msc_starwars.mp3") 
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(1.0) 
            pygame.mixer.music.play(-1)        
        except Exception as e:
            print(f"Erro ao carregar música: {e}")

        #background
        bg_path = os.path.join(script_dir, "sprites", "backgrounds", "background.jpg")
        try:
            self.background = pygame.image.load(bg_path).convert()
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.has_bg_image = True
        except:
            self.has_bg_image = False
            self.stars = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)) for _ in range(100)]

        #butãos
        btn_path = os.path.join(script_dir, "sprites", "botoes", "buttons.png")
        try:
            btn_sheet = pygame.image.load(btn_path).convert_alpha()
            w, h = btn_sheet.get_width() // 2, btn_sheet.get_height()
            play_img = btn_sheet.subsurface((0, 0, w, h))
            exit_img = btn_sheet.subsurface((w, 0, w, h))
        except Exception as e:
            print(f"Erro ao carregar botões: {e}")
            play_img = pygame.Surface((150, 50)); play_img.fill((0, 255, 0))
            exit_img = pygame.Surface((150, 50)); exit_img.fill((255, 0, 0))

        mid_x = int(SCREEN_WIDTH * 0.69) 
        btn_y = 330 
        gap = 85 

        self.buttons = [
            Button(play_img, (mid_x - gap, btn_y), self.start_game),
            Button(exit_img, (mid_x + gap, btn_y), self.exit_game),
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
        pygame.mixer.music.stop()

        play_intro_video(self.screen) 

        pygame.event.clear()  
        self.launch_game = True
        self.running = False



    def exit_game(self):
        pygame.mixer.music.stop()
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
            
            self.draw_background()
            for btn in self.buttons:
                btn.draw(self.screen, mouse_pos)
            
            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    menu = Menu(screen)
    menu.run()
    
    if menu.launch_game:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        game_path = os.path.join(script_dir, "game_base.py")
        subprocess.Popen([sys.executable, game_path])