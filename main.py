import pygame, sys, random, time

pygame.init()

# =========================
# SCREEN
# =========================
W, H = 1100, 650
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Family Feud Final")

clock = pygame.time.Clock()

# =========================
# FONT
# =========================
font = pygame.font.SysFont("arial", 24, bold=True)
big = pygame.font.SysFont("consolas", 60, bold=True)

# =========================
# MAIN GAME DATA
# =========================
question = "Benda di rumah"
answers = [
    {"text":"TV","points":18},
    {"text":"KURSI","points":15},
    {"text":"MEJA","points":14},
    {"text":"LEMARI","points":12},
    {"text":"SOFA","points":10},
    {"text":"KARPET","points":8},
    {"text":"LAMPU","points":7},
    {"text":"AC","points":6},
]

state = [{"revealed":False,"scale":1,"anim":False,"phase":0} for _ in answers]

score_main = 0
target_score = 100

# =========================
# FAST MONEY DATA
# =========================
fm_questions = [
 ("Benda liburan",{"BAJU":30,"HP":25}),
 ("Transportasi",{"MOBIL":30,"MOTOR":25}),
 ("Makanan",{"NASI":30,"ROTI":25}),
 ("Elektronik",{"TV":30,"HP":25}),
 ("Dapur",{"SENDOK":30,"PIRING":25}),
]

fm_player = 1
fm_q = 0
fm_input = ""
fm_ans1=[]; fm_ans2=[]
fm_score1=[]; fm_score2=[]
fm_timer = 20
fm_start = time.time()

# =========================
# STATE
# =========================
phase = "MAIN"

# =========================
# LED TEXT
# =========================
def led(text,x,y):
    f = pygame.font.SysFont("consolas",18,bold=True)
    t = f.render(text,True,(255,255,255))
    t = pygame.transform.scale(t,(t.get_width()*3,t.get_height()*3))
    for iy in range(0,t.get_height(),3):
        for ix in range(0,t.get_width(),3):
            if t.get_at((ix,iy))[0]>0:
                pygame.draw.circle(screen,(255,220,0),(x+ix,y+iy),2)

# =========================
# DRAW ARC
# =========================
def draw_arc(color):
    pygame.draw.circle(screen,(255,200,0),(550,320),320,30)
    pygame.draw.circle(screen,color,(550,320),300)

# =========================
# MAIN GAME DRAW
# =========================
def draw_main():
    screen.fill((10,30,120))
    draw_arc((10,30,120))

    led(str(score_main),500,60)

    qtxt = font.render(question,True,(255,255,255))
    screen.blit(qtxt,(400,130))

    for i in range(8):
        x = 150 if i<4 else 600
        y = 200+(i%4)*80
        a = answers[i]
        s = state[i]

        rect = pygame.Rect(x,y,360,60)
        pygame.draw.rect(screen,(255,200,0),rect)
        pygame.draw.rect(screen,(0,0,0),rect,3)

        if s["revealed"]:
            inner = pygame.Rect(x+5,y+5,350,50)
            pygame.draw.rect(screen,(0,0,0),inner)

            screen.blit(font.render(a["text"],1,(255,255,255)),(x+10,y+15))
            screen.blit(font.render(str(a["points"]),1,(255,0,0)),(x+300,y+15))
        else:
            screen.blit(font.render(str(i+1),1,(0,0,0)),(x+170,y+15))

# =========================
# FAST MONEY DRAW
# =========================
def draw_fast():
    screen.fill((150,0,0))
    draw_arc((150,0,0))

    total = sum(fm_score1)+sum(fm_score2)
    led(str(total),500,60)

    screen.blit(font.render("PLAYER 1",1,(255,255,255)),(150,120))
    screen.blit(font.render("PLAYER 2",1,(255,255,255)),(750,120))

    for i in range(5):
        y = 180+i*70

        # kiri
        if i<len(fm_ans1):
            screen.blit(font.render(fm_ans1[i],1,(255,255,255)),(120,y))
            screen.blit(font.render(str(fm_score1[i]),1,(255,220,0)),(300,y))

        # kanan
        if i<len(fm_ans2):
            screen.blit(font.render(fm_ans2[i],1,(255,255,255)),(700,y))
            screen.blit(font.render(str(fm_score2[i]),1,(255,220,0)),(900,y))

    # input
    screen.blit(font.render(fm_input,1,(255,255,0)),(400,550))

    # timer
    t = int(fm_timer-(time.time()-fm_start))
    led(str(max(0,t)),540,130)

# =========================
# LOOP
# =========================
running=True

while running:
    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            running=False

        if e.type==pygame.KEYDOWN:

            # MAIN GAME
            if phase=="MAIN":
                if pygame.K_1<=e.key<=pygame.K_8:
                    i=e.key-pygame.K_1
                    if not state[i]["revealed"]:
                        state[i]["revealed"]=True
                        score_main+=answers[i]["points"]

                        if score_main>=target_score:
                            phase="FAST"

            # FAST MONEY
            elif phase=="FAST":
                if e.key==pygame.K_RETURN:
                    if fm_q<5:
                        q,data=fm_questions[fm_q]
                        pts=data.get(fm_input.upper(),0)

                        if fm_player==1:
                            fm_ans1.append(fm_input.upper())
                            fm_score1.append(pts)
                        else:
                            fm_ans2.append(fm_input.upper())
                            fm_score2.append(pts)

                        fm_input=""
                        fm_q+=1

                elif e.key==pygame.K_BACKSPACE:
                    fm_input=fm_input[:-1]
                else:
                    fm_input+=e.unicode

    # TIMER SWITCH
    if phase=="FAST":
        t = fm_timer-(time.time()-fm_start)
        if t<=0:
            if fm_player==1:
                fm_player=2
                fm_q=0
                fm_timer=25
                fm_start=time.time()
            else:
                phase="END"

    # DRAW
    if phase=="MAIN":
        draw_main()
    elif phase=="FAST":
        draw_fast()
    else:
        screen.fill((0,0,0))
        total = sum(fm_score1)+sum(fm_score2)
        msg = "WIN!" if total>=200 else "LOSE"
        screen.blit(big.render(msg,1,(255,200,0)),(450,300))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
