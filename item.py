import pygame

class Item:
    def __init__(self, x, y, type):
        self.type = type
        self.image = pygame.Surface((20, 20))
        if type == "battery":
            self.image.fill((0, 255, 0))
        elif type == "key":
            self.image.fill((255, 255, 0))
        elif type == "note":
            self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect(center=(x, y))


'''import pygame, sys, math, random

# --- Inicialização ---
pygame.init()
screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("Terror STEM - Nível Play Store")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Orbitron",28)
small_font = pygame.font.SysFont("Orbitron",20)

# --- Funções utilitárias ---
def draw_gradient_rect(surface, rect, color1, color2):
    x,y,w,h = rect
    for i in range(h):
        ratio = i/h
        r = int(color1[0]*(1-ratio)+color2[0]*ratio)
        g = int(color1[1]*(1-ratio)+color2[1]*ratio)
        b = int(color1[2]*(1-ratio)+color2[2]*ratio)
        pygame.draw.line(surface,(r,g,b),(x,y+i),(x+w-1,y+i))

def draw_text_outline(surface,text,font,color,outline_color,pos):
    x,y = pos
    for dx in [-2,-1,0,1,2]:
        for dy in [-2,-1,0,1,2]:
            if dx!=0 or dy!=0:
                surface.blit(font.render(text, True, outline_color), (x+dx,y+dy))
    surface.blit(font.render(text, True, color), pos)

# --- Classes ---
class Player:
    def __init__(self,x,y):
        self.rect = pygame.Rect(x,y,30,30)
        self.speed = 5
        self.light_energy = 100
        self.keys = 0
        self.walk_anim = 0
        self.shield = 0
        self.sprint_timer = 0
        self.vision_timer = 0

    def move(self,keys,walls):
        dx=dy=0; moving=False
        spd = self.speed
        if self.sprint_timer>0: spd *= 1.8
        if keys[pygame.K_w]: dy -= spd; moving=True
        if keys[pygame.K_s]: dy += spd; moving=True
        if keys[pygame.K_a]: dx -= spd; moving=True
        if keys[pygame.K_d]: dx += spd; moving=True
        self.rect.x += dx
        for wall in walls:
            if self.rect.colliderect(wall.rect): self.rect.x -= dx
        self.rect.y += dy
        for wall in walls:
            if self.rect.colliderect(wall.rect): self.rect.y -= dy
        if moving: self.walk_anim += 0.2
        else: self.walk_anim = 0

    def use_light(self):
        if self.light_energy>0: self.light_energy -= 0.2

    def draw(self,surface):
        offset = math.sin(self.walk_anim)*5
        temp_surf = pygame.Surface((self.rect.width,self.rect.height))
        color1 = (255,255,255)
        color2 = (180,180+offset,180)
        draw_gradient_rect(temp_surf,(0,0,self.rect.width,self.rect.height),color1,color2)
        surface.blit(temp_surf,(self.rect.x,self.rect.y))

class Enemy:
    def __init__(self,x,y,speed=2):
        self.rect = pygame.Rect(x,y,30,30)
        self.speed = speed
        self.alert_distance = 200
        self.flash_timer = 0
        self.dir = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
    def update(self,player,walls):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.hypot(dx,dy)
        if distance < self.alert_distance:
            if distance!=0:
                self.rect.x += int(dx/distance*self.speed)
                self.rect.y += int(dy/distance*self.speed)
            self.flash_timer=5
        else:
            self.rect.x += self.dir[0]*self.speed
            self.rect.y += self.dir[1]*self.speed
            for wall in walls:
                if self.rect.colliderect(wall.rect):
                    self.dir = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
            self.flash_timer=max(self.flash_timer-0.1,0)
    def draw(self,surface):
        color=(255,0,0) if self.flash_timer<=0 else (255,255,255)
        temp_surf=pygame.Surface((self.rect.width,self.rect.height))
        draw_gradient_rect(temp_surf,(0,0,self.rect.width,self.rect.height),color,(100,0,0))
        surface.blit(temp_surf,(self.rect.x,self.rect.y))

class Item:
    def __init__(self,x,y,type):
        self.type = type
        self.rect = pygame.Rect(x,y,20,20)
        self.color = (0,255,0) if type=="battery" else (255,255,0) if type=="key" else (0,0,255)
    def draw(self,surface):
        temp_surf = pygame.Surface((self.rect.width,self.rect.height))
        draw_gradient_rect(temp_surf,(0,0,self.rect.width,self.rect.height),self.color,(50,50,50))
        surface.blit(temp_surf,(self.rect.x,self.rect.y))

class Wall:
    def __init__(self,x,y,w,h):
        self.rect = pygame.Rect(x,y,w,h)
        self.color1=(30,30,30)
        self.color2=(70,70,70)
    def draw(self,surface):
        draw_gradient_rect(surface,(self.rect.x,self.rect.y,self.rect.width,self.rect.height),self.color1,self.color2)

class Door:
    def __init__(self,x,y,w,h,key_required=1):
        self.rect=pygame.Rect(x,y,w,h)
        self.locked=True
        self.flash_timer=0
        self.color1=(150,75,0)
        self.color2=(100,50,0)
        self.key_required = key_required  # chaves necessárias para abrir
    def draw(self,surface):
        temp_surf=pygame.Surface((self.rect.width,self.rect.height))
        if self.flash_timer>0:
            draw_gradient_rect(temp_surf,(0,0,self.rect.width,self.rect.height),(255,255,255),(255,255,255))
        else:
            draw_gradient_rect(temp_surf,(0,0,self.rect.width,self.rect.height),self.color1,self.color2)
        surface.blit(temp_surf,(self.rect.x,self.rect.y))
        self.flash_timer=max(self.flash_timer-0.1,0)

# --- Tela de escolha de dificuldade futurista ---
def choose_difficulty():
    choosing = True
    selected = "medio"
    buttons = [
        {"text":"Fácil","pos":(250,250),"color1":(0,200,255),"color2":(0,100,200),"key":pygame.K_1,"value":"facil"},
        {"text":"Médio","pos":(250,320),"color1":(0,255,100),"color2":(0,150,50),"key":pygame.K_2,"value":"medio"},
        {"text":"Difícil","pos":(250,390),"color1":(255,50,50),"color2":(150,0,0),"key":pygame.K_3,"value":"dificil"}
    ]
    while choosing:
        screen.fill((10,10,10)) 
        draw_text_outline(screen,"ESCOLHA A DIFICULDADE",font,(0,255,200),(0,0,0),(120,150))
        mx,my = pygame.mouse.get_pos()
        click = False
        for event in pygame.event.get():
            if event.type==pygame.QUIT: sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN: click=True
            if event.type==pygame.KEYDOWN:
                for b in buttons:
                    if event.key==b["key"]: selected=b["value"]; choosing=False
        for b in buttons:
            rect = pygame.Rect(b["pos"][0],b["pos"][1],300,50)
            if rect.collidepoint((mx,my)):
                draw_gradient_rect(screen,(rect.x,rect.y,rect.width,rect.height),b["color2"],b["color1"])
                if click: selected=b["value"]; choosing=False
            else:
                draw_gradient_rect(screen,(rect.x,rect.y,rect.width,rect.height),b["color1"],b["color2"])
            draw_text_outline(screen,b["text"],small_font,(255,255,255),(0,0,0),(rect.x+100,rect.y+10))
        for i in range(0,800,80):
            pygame.draw.line(screen,(0,255,255),(i,(pygame.time.get_ticks()/10)%600),(i,((pygame.time.get_ticks()/10)%600)+20),2)
        pygame.display.flip()
        clock.tick(60)
    return selected

# --- Tela de morte com botão continuar ---
def death_screen():
    waiting = True
    while waiting:
        screen.fill((0,0,0))
        draw_text_outline(screen,"VOCÊ MORREU!", font, (255,0,0), (0,0,0), (250,200))
        mx,my = pygame.mouse.get_pos()
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN: click=True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c: waiting=False
        rect = pygame.Rect(300,300,200,50)
        if rect.collidepoint((mx,my)):
            draw_gradient_rect(screen,(rect.x,rect.y,rect.width,rect.height),(0,200,255),(0,100,200))
            if click: waiting=False
        else:
            draw_gradient_rect(screen,(rect.x,rect.y,rect.width,rect.height),(0,100,200),(0,50,100))
        draw_text_outline(screen,"CONTINUAR", small_font,(255,255,255),(0,0,0),(rect.x+50,rect.y+10))
        pygame.display.flip()
        clock.tick(60)

# --- Configuração de dificuldade e poderes ---
difficulty = choose_difficulty()
difficulty_settings = {
    "facil": {"enemy_count":2, "enemy_speed":2, "item_count":4, "wall_factor":1},
    "medio": {"enemy_count":4, "enemy_speed":3, "item_count":3, "wall_factor":1.5},
    "dificil": {"enemy_count":6, "enemy_speed":4, "item_count":2, "wall_factor":2}
}
diff = difficulty_settings[difficulty]

powers = ["sprint","shield","vision"]

# --- Fases ---
fases = []
for lvl in range(1,11):
    walls=[]
    doors=[]
    items=[]
    enemies=[]
    walls += [Wall(0,0,800,20), Wall(0,580,800,20), Wall(0,0,20,600), Wall(780,0,20,600)]
    for _ in range(int((5+lvl)*diff["wall_factor"])):
        x=random.randint(50,700); y=random.randint(50,500)
        if random.random()>0.5: w=random.randint(50,150); h=20
        else: w=20; h=random.randint(50,150)
        walls.append(Wall(x,y,w,h))
    key_required = 2 if lvl%3==0 else 1  # algumas portas exigem 2 chaves
    doors.append(Door(760,540,20,40,key_required=key_required))
    for _ in range(diff["item_count"]):
        items.append(Item(random.randint(50,750),random.randint(50,550),random.choice(["battery","key","note"])))
    for _ in range(diff["enemy_count"]):
        enemies.append(Enemy(random.randint(50,750),random.randint(50,550),speed=diff["enemy_speed"]))
    fases.append({"walls":walls,"doors":doors,"items":items,"enemies":enemies})

# --- Inicialização jogador ---
level = 0
player = Player(50,550)
walls = fases[level]["walls"]
doors = fases[level]["doors"]
items = fases[level]["items"]
enemies = fases[level]["enemies"]
running = True

def proximo_level():
    global level, player, walls, doors, items, enemies
    level += 1
    if level>=len(fases):
        print("Parabéns! Você completou todas as fases!")
        pygame.time.delay(3000)
        pygame.quit(); sys.exit()
    player.rect.topleft=(50,550)
    walls = fases[level]["walls"]
    doors = fases[level]["doors"]
    items = fases[level]["items"]
    enemies = fases[level]["enemies"]

# --- Loop principal ---
while running:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type==pygame.QUIT: running=False

    player.move(keys,walls)
    player.use_light()

    # Inimigos
    for enemy in enemies:
        enemy.update(player,walls)
        dx = player.rect.centerx - enemy.rect.centerx
        dy = player.rect.centery - enemy.rect.centery
        distance = math.hypot(dx,dy)
        if distance < 50:
            screen.fill((255,0,0))
            pygame.display.flip()
            pygame.time.delay(50)
        if player.rect.colliderect(enemy.rect):
            if player.shield>0:
                player.shield=0
            else:
                death_screen()
                player.rect.topleft = (50,550)
                player.keys=0
                walls = fases[level]["walls"]
                doors = fases[level]["doors"]
                items = fases[level]["items"]
                enemies = fases[level]["enemies"]

    # Itens
    for item in items[:]:
        if player.rect.colliderect(item.rect):
            if item.type=="battery": player.light_energy=min(player.light_energy+50,100)
            elif item.type=="key": player.keys+=1
            items.remove(item)

    # Portas
    for door in doors:
        if player.rect.colliderect(door.rect):
            if door.locked:
                if player.keys >= door.key_required:
                    door.locked=False
                    player.keys -= door.key_required
                    proximo_level()
                else:
                    door.flash_timer=5

    # --- Desenhar ---
    screen.fill((0,0,0))
    fog = pygame.Surface((800,600),pygame.SRCALPHA)
    for i in range(0,600,5):
        alpha = int(50+50*math.sin(pygame.time.get_ticks()/1000+i))
        pygame.draw.line(fog,(50,50,50,alpha),(0,i),(800,i))
    screen.blit(fog,(0,0))

    light_surface=pygame.Surface((800,600),pygame.SRCALPHA)
    for r in range(int(player.light_energy*2),0,-1):
        alpha=max(0,min(180,int(180*(r/(player.light_energy*2)))))
        pygame.draw.circle(light_surface,(255,255,255,alpha),player.rect.center,r)
    screen.blit(light_surface,(0,0),special_flags=pygame.BLEND_RGBA_MULT)

    for wall in walls: wall.draw(screen)
    for door in doors: door.draw(screen)
    for item in items: item.draw(screen)
    for enemy in enemies: enemy.draw(screen)
    player.draw(screen)

    pygame.draw.rect(screen,(255,200,0),(10,10,int(player.light_energy*2),20))
    draw_text_outline(screen,f"Chaves: {player.keys}  Fase: {level+1}  Dificuldade: {difficulty.capitalize()}",font,(255,255,255),(0,0,0),(10,40))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
'''

import pygame, sys, math, random

# --- Inicialização ---
pygame.init()
screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("Terror STEM - Nível Play Store")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Orbitron",28)
small_font = pygame.font.SysFont("Orbitron",20)

# --- Funções utilitárias ---
def draw_gradient_rect(surface, rect, color1, color2):
    x,y,w,h = rect
    for i in range(h):
        ratio = i/h
        r = int(color1[0]*(1-ratio)+color2[0]*ratio)
        g = int(color1[1]*(1-ratio)+color2[1]*ratio)
        b = int(color1[2]*(1-ratio)+color2[2]*ratio)
        pygame.draw.line(surface,(r,g,b),(x,y+i),(x+w-1,y+i))

def draw_text_outline(surface,text,font,color,outline_color,pos):
    x,y = pos
    for dx in [-2,-1,0,1,2]:
        for dy in [-2,-1,0,1,2]:
            if dx!=0 or dy!=0:
                surface.blit(font.render(text, True, outline_color), (x+dx,y+dy))
    surface.blit(font.render(text, True, color), pos)

# --- Classes ---
class Player:
    def __init__(self,x,y):
        self.rect = pygame.Rect(x,y,30,30)
        self.speed = 5
        self.light_energy = 100
        self.keys = 0
        self.walk_anim = 0
        self.shield = 0
        self.sprint_timer = 0
        self.vision_timer = 0

    def move(self,keys,walls):
        dx=dy=0; moving=False
        spd = self.speed
        if self.sprint_timer>0: spd *= 1.8
        if keys[pygame.K_w]: dy -= spd; moving=True
        if keys[pygame.K_s]: dy += spd; moving=True
        if keys[pygame.K_a]: dx -= spd; moving=True
        if keys[pygame.K_d]: dx += spd; moving=True
        self.rect.x += dx
        for wall in walls:
            if self.rect.colliderect(wall.rect): self.rect.x -= dx
        self.rect.y += dy
        for wall in walls:
            if self.rect.colliderect(wall.rect): self.rect.y -= dy
        if moving: self.walk_anim += 0.2
        else: self.walk_anim = 0

    def use_light(self):
        if self.light_energy>0: self.light_energy -= 0.2

    def draw(self,surface):
        offset = math.sin(self.walk_anim)*5
        temp_surf = pygame.Surface((self.rect.width,self.rect.height))
        color1 = (255,255,255)
        color2 = (180,180+offset,180)
        draw_gradient_rect(temp_surf,(0,0,self.rect.width,self.rect.height),color1,color2)
        surface.blit(temp_surf,(self.rect.x,self.rect.y))

class Enemy:
    def __init__(self,x,y,speed=2):
        self.rect = pygame.Rect(x,y,30,30)
        self.speed = speed
        self.alert_distance = 200
        self.flash_timer = 0
        self.dir = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
    def update(self,player,walls):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.hypot(dx,dy)
        if distance < self.alert_distance:
            if distance!=0:
                self.rect.x += int(dx/distance*self.speed)
                self.rect.y += int(dy/distance*self.speed)
            self.flash_timer=5
        else:
            self.rect.x += self.dir[0]*self.speed
            self.rect.y += self.dir[1]*self.speed
            for wall in walls:
                if self.rect.colliderect(wall.rect):
                    self.dir = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
            self.flash_timer=max(self.flash_timer-0.1,0)
    def draw(self,surface):
        color=(255,0,0) if self.flash_timer<=0 else (255,255,255)
        temp_surf=pygame.Surface((self.rect.width,self.rect.height))
        draw_gradient_rect(temp_surf,(0,0,self.rect.width,self.rect.height),color,(100,0,0))
        surface.blit(temp_surf,(self.rect.x,self.rect.y))

class Item:
    def __init__(self,x,y,type):
        self.type = type
        self.rect = pygame.Rect(x,y,20,20)
        self.color = (0,255,0) if type=="battery" else (255,255,0) if type=="key" else (0,0,255)
    def draw(self,surface):
        temp_surf = pygame.Surface((self.rect.width,self.rect.height))
        draw_gradient_rect(temp_surf,(0,0,self.rect.width,self.rect.height),self.color,(50,50,50))
        surface.blit(temp_surf,(self.rect.x,self.rect.y))

class Wall:
    def __init__(self,x,y,w,h):
        self.rect = pygame.Rect(x,y,w,h)
        self.color1=(30,30,30)
        self.color2=(70,70,70)
    def draw(self,surface):
        draw_gradient_rect(surface,(self.rect.x,self.rect.y,self.rect.width,self.rect.height),self.color1,self.color2)

class Door:
    def __init__(self,x,y,w,h,key_required=1):
        self.rect=pygame.Rect(x,y,w,h)
        self.locked=True
        self.flash_timer=0
        self.color1=(150,75,0)
        self.color2=(100,50,0)
        self.key_required = key_required  # chaves necessárias para abrir
    def draw(self,surface):
        temp_surf=pygame.Surface((self.rect.width,self.rect.height))
        if self.flash_timer>0:
            draw_gradient_rect(temp_surf,(0,0,self.rect.width,self.rect.height),(255,255,255),(255,255,255))
        else:
            draw_gradient_rect(temp_surf,(0,0,self.rect.width,self.rect.height),self.color1,self.color2)
        surface.blit(temp_surf,(self.rect.x,self.rect.y))
        self.flash_timer=max(self.flash_timer-0.1,0)

# --- Tela de escolha de dificuldade futurista ---
def choose_difficulty():
    choosing = True
    selected = "medio"
    buttons = [
        {"text":"Fácil","pos":(250,250),"color1":(0,200,255),"color2":(0,100,200),"key":pygame.K_1,"value":"facil"},
        {"text":"Médio","pos":(250,320),"color1":(0,255,100),"color2":(0,150,50),"key":pygame.K_2,"value":"medio"},
        {"text":"Difícil","pos":(250,390),"color1":(255,50,50),"color2":(150,0,0),"key":pygame.K_3,"value":"dificil"}
    ]
    while choosing:
        screen.fill((10,10,10)) 
        draw_text_outline(screen,"ESCOLHA A DIFICULDADE",font,(0,255,200),(0,0,0),(120,150))
        mx,my = pygame.mouse.get_pos()
        click = False
        for event in pygame.event.get():
            if event.type==pygame.QUIT: sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN: click=True
            if event.type==pygame.KEYDOWN:
                for b in buttons:
                    if event.key==b["key"]: selected=b["value"]; choosing=False
        for b in buttons:
            rect = pygame.Rect(b["pos"][0],b["pos"][1],300,50)
            if rect.collidepoint((mx,my)):
                draw_gradient_rect(screen,(rect.x,rect.y,rect.width,rect.height),b["color2"],b["color1"])
                if click: selected=b["value"]; choosing=False
            else:
                draw_gradient_rect(screen,(rect.x,rect.y,rect.width,rect.height),b["color1"],b["color2"])
            draw_text_outline(screen,b["text"],small_font,(255,255,255),(0,0,0),(rect.x+100,rect.y+10))
        for i in range(0,800,80):
            pygame.draw.line(screen,(0,255,255),(i,(pygame.time.get_ticks()/10)%600),(i,((pygame.time.get_ticks()/10)%600)+20),2)
        pygame.display.flip()
        clock.tick(60)
    return selected

# --- Tela de morte com botão continuar ---
def death_screen():
    waiting = True
    while waiting:
        screen.fill((0,0,0))
        draw_text_outline(screen,"VOCÊ MORREU!", font, (255,0,0), (0,0,0), (250,200))
        mx,my = pygame.mouse.get_pos()
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN: click=True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c: waiting=False
        rect = pygame.Rect(300,300,200,50)
        if rect.collidepoint((mx,my)):
            draw_gradient_rect(screen,(rect.x,rect.y,rect.width,rect.height),(0,200,255),(0,100,200))
            if click: waiting=False
        else:
            draw_gradient_rect(screen,(rect.x,rect.y,rect.width,rect.height),(0,100,200),(0,50,100))
        draw_text_outline(screen,"CONTINUAR", small_font,(255,255,255),(0,0,0),(rect.x+50,rect.y+10))
        pygame.display.flip()
        clock.tick(60)

# --- Configuração de dificuldade e poderes ---
difficulty = choose_difficulty()
difficulty_settings = {
    "facil": {"enemy_count":2, "enemy_speed":2, "item_count":4, "wall_factor":1},
    "medio": {"enemy_count":4, "enemy_speed":3, "item_count":3, "wall_factor":1.5},
    "dificil": {"enemy_count":6, "enemy_speed":4, "item_count":2, "wall_factor":2}
}
diff = difficulty_settings[difficulty]

powers = ["sprint","shield","vision"]

# --- Configuração fases ---
fases = {}
musica_fase = ["../assents/sounds/phase1.mp3", 
               "../assents/sounds/phase2.mp3", 
               "../assents/sounds/phase3.mp3"]

for i in range(1, 11):
    fases[i] = {
        "walls": [],
        "doors": [],
        "items": [],
        "enemies": [],
        "music": musica_fase[((i-1)//3) % len(musica_fase)]  # repete quando acabar
    }

# --- Fases ---
fases = []
for lvl in range(1,11):
    walls=[]
    doors=[]
    items=[]
    enemies=[]
    walls += [Wall(0,0,800,20), Wall(0,580,800,20), Wall(0,0,20,600), Wall(780,0,20,600)]
    for _ in range(int((5+lvl)*diff["wall_factor"])):
        x=random.randint(50,700); y=random.randint(50,500)
        if random.random()>0.5: w=random.randint(50,150); h=20
        else: w=20; h=random.randint(50,150)
        walls.append(Wall(x,y,w,h))
    key_required = 2 if lvl%3==0 else 1  # algumas portas exigem 2 chaves
    doors.append(Door(760,540,20,40,key_required=key_required))
    for _ in range(diff["item_count"]):
        items.append(Item(random.randint(50,750),random.randint(50,550),random.choice(["battery","key","note"])))
    for _ in range(diff["enemy_count"]):
        enemies.append(Enemy(random.randint(50,750),random.randint(50,550),speed=diff["enemy_speed"]))
    fases.append({"walls":walls,"doors":doors,"items":items,"enemies":enemies})

# --- Inicialização jogador ---
level = 0
player = Player(50,550)
walls = fases[level]["walls"]
doors = fases[level]["doors"]
items = fases[level]["items"]
enemies = fases[level]["enemies"]
running = True

def proximo_level():
    global level, player, walls, doors, items, enemies
    level += 1
    if level>=len(fases):
        print("Parabéns! Você completou todas as fases!")
        pygame.time.delay(3000)
        pygame.quit(); sys.exit()
    player.rect.topleft=(50,550)
    walls = fases[level]["walls"]
    doors = fases[level]["doors"]
    items = fases[level]["items"]
    enemies = fases[level]["enemies"]

# --- Loop principal ---
while running:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type==pygame.QUIT: running=False

    player.move(keys,walls)
    player.use_light()

    # Inimigos
    for enemy in enemies:
        enemy.update(player,walls)
        dx = player.rect.centerx - enemy.rect.centerx
        dy = player.rect.centery - enemy.rect.centery
        distance = math.hypot(dx,dy)
        if distance < 50:
            screen.fill((255,0,0))
            pygame.display.flip()
            pygame.time.delay(50)
        if player.rect.colliderect(enemy.rect):
            if player.shield>0:
                player.shield=0
            else:
                death_screen()
                player.rect.topleft = (50,550)
                player.keys=0
                walls = fases[level]["walls"]
                doors = fases[level]["doors"]
                items = fases[level]["items"]
                enemies = fases[level]["enemies"]

    # Itens
    for item in items[:]:
        if player.rect.colliderect(item.rect):
            if item.type=="battery": player.light_energy=min(player.light_energy+50,100)
            elif item.type=="key": player.keys+=1
            items.remove(item)

    # Portas
    for door in doors:
        if player.rect.colliderect(door.rect):
            if door.locked:
                if player.keys >= door.key_required:
                    door.locked=False
                    player.keys -= door.key_required
                    proximo_level()
                else:
                    door.flash_timer=5

    # --- Desenhar ---
    screen.fill((0,0,0))
    fog = pygame.Surface((800,600),pygame.SRCALPHA)
    for i in range(0,600,5):
        alpha = int(50+50*math.sin(pygame.time.get_ticks()/1000+i))
        pygame.draw.line(fog,(50,50,50,alpha),(0,i),(800,i))
    screen.blit(fog,(0,0))

    light_surface=pygame.Surface((800,600),pygame.SRCALPHA)
    for r in range(int(player.light_energy*2),0,-1):
        alpha=max(0,min(180,int(180*(r/(player.light_energy*2)))))
        pygame.draw.circle(light_surface,(255,255,255,alpha),player.rect.center,r)
    screen.blit(light_surface,(0,0),special_flags=pygame.BLEND_RGBA_MULT)

    for wall in walls: wall.draw(screen)
    for door in doors: door.draw(screen)
    for item in items: item.draw(screen)
    for enemy in enemies: enemy.draw(screen)
    player.draw(screen)

    pygame.draw.rect(screen,(255,200,0),(10,10,int(player.light_energy*2),20))
    draw_text_outline(screen,f"Chaves: {player.keys}  Fase: {level+1}  Dificuldade: {difficulty.capitalize()}",font,(255,255,255),(0,0,0),(10,40))

    pygame.display.flip()
    clock.tick(60)
#quero adicionar uma musica de fundo
player = pygame.mixer.Sound("../assents/sounds/door.mp3")

pygame.quit()
sys.exit()