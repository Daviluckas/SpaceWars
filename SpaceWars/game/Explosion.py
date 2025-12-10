import pygame
import time
pygame.init()
Explosion_sound = pygame.mixer.Sound("SpaceWars/Sounds/Explosion-Song.wav")
class Explosao:
    def __init__(self, position):
        self.frames = [
            pygame.image.load(f"SpaceWars/spritesBase/exp/explosion{i}.png").convert_alpha() 
            for i in range(1, 6)
        ]
        self.index = 0
        self.pos = position
        self.timer = time.time()
        self.intervalo = 0.08

        self.sound = Explosion_sound
        self.sound.set_volume(1.0)

        channel = pygame.mixer.find_channel()
        if channel:
            channel.play(self.sound)

    def update(self):
        if time.time() - self.timer > self.intervalo:
            self.index += 1
            self.timer = time.time()

    def ended(self):
        return self.index >= len(self.frames)

    def draw(self, tela):
        if self.index < len(self.frames):
            imagem = pygame.transform.scale(self.frames[self.index], (94, 94))
            rect = imagem.get_rect(center=self.pos)
            tela.blit(imagem, rect)