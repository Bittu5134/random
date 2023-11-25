import pygame
import random
from pygame.locals import *


pygame.init()
screen = pygame.display.set_mode((900, 600))
gameOn = True
all_sprites = pygame.sprite.Group()
font = pygame.font.Font(None, 32)
clock = pygame.time.Clock()
sprite_count = {
	"stone": 0,
	"paper": 0,
	"scissors": 0
}


class player(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()

		self.image = pygame.Surface((30, 30))
		self.color = {
			"stone": "red",
			"paper": "blue",
			"scissors": "yellow"
		}
		self.set_type(random.choice(["stone", "paper", "scissors"]))

		self.rect = self.image.get_rect()
		self.rect.center = (random.randint(10, 890), random.randint(10, 590))

		self.stationary = True
		self.speed = random.randint(2, 3)
		self.vel_x = 1
		self.vel_y = 1
		self.vel_update = 0
		self.change_criteria = [
			("stone", "paper"),
			("paper", "scissors"),
			("scissors", "stone"),
		]
		self.movements = [0,1,-1]

	def set_type(self, type):
		self.type = type
		self.image = pygame.image.load(f"./Rock_Paper_Scissors_war/{self.type}.png")
		self.image = pygame.transform.scale(self.image, (30, 30))

	def update(self):
		for sprite in pygame.sprite.spritecollide(self, all_sprites, False):
			if (self.type, sprite.type) in self.change_criteria:
				self.set_type(sprite.type)

		self.vel_update -= 1
		self.rect.x += self.vel_x * self.speed
		self.rect.y += self.vel_y * self.speed

		if self.vel_update < 1:

			self.vel_update = random.randint(30, 120)
			self.stationary = True

			while self.stationary:
				self.vel_x = random.choice(self.movements)
				self.vel_y = random.choice(self.movements)
				self.stationary = self.vel_x == self.vel_y == 0

		if self.rect.left < 0 or self.rect.right > 900:
			self.vel_x *= -1
		if self.rect.top < 0 or self.rect.bottom > 600:
			self.vel_y *= -1


all_sprites.add(player() for _ in range(60))


while gameOn:
	clock.tick(60)

	for event in pygame.event.get():
		if event.type == QUIT:
			gameOn = False
		if event.type == KEYDOWN:
			if event.key == K_k:
				all_sprites.add(player())

	all_sprites.update()

	sprite_count = {"stone": 0, "paper": 0, "scissors": 0}
	for sprite in all_sprites: 
		sprite_count[sprite.type] += 1
	if sprite_count["stone"] == sprite_count["paper"] == 0: print("scissors won")
	elif sprite_count["stone"] == sprite_count["scissors"] == 0: print("paper won")
	elif sprite_count["paper"] == sprite_count["scissors"] == 0: print("stone won")

	screen.fill("grey")
	all_sprites.draw(screen)
	screen.blit(font.render(f"FPS: {int(clock.get_fps())}", True, "gold"), (5, 5))
	pygame.display.update()