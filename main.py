import sys, random, time, json
import pygame

# Multi-window (Pygame 2)
from pygame._sdl2 import Window, Renderer

pygame.init()
pygame.font.init()

# =========================
# WINDOWS
# =========================
DISPLAY_SIZE = (1100, 650)
HOST_SIZE = (420, 650)

display_win = Window("DISPLAY (Audience)", size=DISPLAY_SIZE)
display_ren = Renderer(display_win)

host_win = Window("HOST PANEL", size=HOST_SIZE, position=(DISPLAY_SIZE[0]+20, 60))
host_ren = Renderer(host_win)

display_surf = pygame.Surface(DISPLAY_SIZE)
host_surf = pygame.Surface(HOST_SIZE)

# =========================
# FONT
# =========================
font = pygame.font.SysFont("consolas", 22)
big = pygame.font.SysFont("consolas", 52, bold=True)

# =========================
# AUDIO (optional)
# =========================
def load_sfx(path):
    try: return pygame.mixer.Sound(path)
    except: return None

try:
    pygame.mixer.init()
    try:
        pygame.mixer.music.load("crowd_loop.wav")
        pygame.mixer.music.set_volume(0.25)
        pygame.mixer.music.play(-1)
    except: pass
except: pass

SFX = {
    "ding": load_sfx("ding.wav"),
    "strike": load_sfx("strike.wav"),
    "buzzer": load_sfx("buzzer.wav"),
    "tick": load_sfx("tick.wav"),
    "win": load_sfx("win.wav")
}
def sfx(name):
    if SFX.get(name): SFX[name].play()

# =========================
# LOAD DATABASE (fallback kalau tidak ada file)
# =========================
try:
    with open("soal.json") as f:
        QUESTIONS = json.load(f)
except:
    QUESTIONS = [
        {"question":"Benda di rumah",
         "answers":[{"text":"TV","points":18},{"text":"KURSI","points":12},{"text":"MEJA","points":10}]},
        {"question":"Alat komunikasi",
         "answers":[{"text":"HP","points":30},{"text":"EMAIL","points":15},{"text":"TELEPON","points":20}]}
    ]

def pick_question():
    q = random.choice(QUESTIONS)
    return q["question"], [(a["text"], a["points"]) for a in q["answers"]]

# =========================
# GAME STATE
# =========================
phase = "INTRO"
substate = "BUZZER"

question, answers = pick_question()

def make_state(ans):
    return [{
        "text": t, "points": p,
        "revealed": False,
        "anim": False,
        "scale": 1.0,
        "phase": 0
    } for (t,p) in ans]

ans_state = make_state(answers)

scoreA = scoreB = 0
dispA = dispB = 0
current = None
strikes = 0
round_num = 1
target_score = 300

def mult(r):
    if r<=2: return 1
    if r==3: return 2
    if r<=5: return 3
    return random.choice([1,2,3])

multiplier = mult(round_num)

# =========================
# FAST MONEY
# =========================
FM_Q = [
 ("Benda kantor",{"KOMPUTER":30,"MEJA":25}),
 ("Transportasi",{"MOBIL":30,"MOTOR":25}),
 ("Elektronik",{"TV":30,"HP":25}),
 ("Bisa dibuka",{"PINTU":30,"BUKU":25}),
 ("Benda dapur",{"PIRING":30,"SENDOK":25})
]

fm_player = 1
fm_q = 0
fm_input = ""
fm_a1=[]; fm_a2=[]
fm_s1=[]; fm_s2=[]
fm_timer = 20
fm_start = time.time()

winner = None

# =========================
# LED TEXT
# =========================
def led_text(surf, txt, x,y, col=(255,220,0), scale=3):
    f = pygame.font.SysFont("consolas", 16, bold=True)
    t = f.render(txt, True, (255,255,255))
    t = pygame.transform.scale(t, (t.get_width()*scale, t.get_height()*scale))
    for iy in range(0,t.get_height(),scale):
        for ix in range(0,t.get_width(),scale):
            if t.get_at((ix,iy))[0]>0:
                pygame.draw.circle(surf,col,(x+ix,y+iy),2)

# =========================
# ANIMATION
# =========================
def flip(i):
    if not ans_state[i]["revealed"]:
        ans_state[i]["anim"]=True
        ans_state[i]["phase"]=0

def update_anim():
    for a in ans_state:
        if a["anim"]:
            if a["phase"]==0:
                a["scale"]-=0.08
                if a["scale"]<=0:
                    a["scale"]=0
                    a["phase"]=1
                    a["revealed"]=True
                    sfx("ding")
            else:
                a["scale"]+=0.08
                if a["scale"]>=1:
                    a["scale"]=1
                    a["anim"]=False

def update_score():
    global dispA, dispB
    if dispA<scoreA: dispA+=2; sfx("tick")
    if dispB<scoreB: dispB+=2; sfx("tick")

# =========================
# MAIN LOGIC
# =========================
def reveal(i):
    global scoreA, scoreB, phase, winner
    if i<len(ans_state) and not ans_state[i]["revealed"]:
        flip(i)
        pts = ans_state[i]["points"]*multiplier
        if current=="A": scoreA+=pts
        elif current=="B": scoreB+=pts

        if scoreA>=target_score:
            phase="FAST"; winner="A"
        if scoreB>=target_score:
            phase="FAST"; winner="B"

def next_round():
    global question,answers,ans_state,strikes,current,round_num,multiplier
    round_num+=1
    multiplier=mult(round_num)
    question,answers=pick_question()
    ans_state=make_state(answers)
    strikes=0
    current=None

def buzzer(t):
    global current
    if current is None:
        current=t
        sfx("buzzer")

def strike():
    global strikes
    strikes+=1
    sfx("strike")

# =========================
# DRAW DISPLAY
# =========================
def draw_main():
    display_surf.fill((10,30,120))
    led_text(display_surf,f"ROUND {round_num} x{multiplier}",420,20)
    led_text(display_surf,question.upper(),200,80)

    for i,a in enumerate(ans_state):
        x=120 if i<4 else 560
        y=150+(i%4)*90
        w=int(360*a["scale"])
        r=pygame.Rect(x+180-w//2,y,w,70)
        pygame.draw.rect(display_surf,(10,10,10),r)

        if a["revealed"] and a["scale"]>0.2:
            led_text(display_surf,a["text"],r.x+10,y+10)
            led_text(display_surf,str(a["points"]*multiplier),r.x+r.width-60,y+10)
        else:
            led_text(display_surf,str(i+1),r.centerx-10,y+10)

    led_text(display_surf,f"A {dispA}",40,580)
    led_text(display_surf,f"B {dispB}",900,580)

def draw_fast():
    display_surf.fill((0,0,0))
    total=sum(fm_s1)+sum(fm_s2)
    led_text(display_surf,str(total),520,20)

    for i in range(5):
        y=120+i*80
        if i<len(fm_a1):
            led_text(display_surf,fm_a1[i],60,y)
            led_text(display_surf,str(fm_s1[i]),320,y)
        if i<len(fm_a2):
            led_text(display_surf,fm_a2[i],700,y)
            led_text(display_surf,str(fm_s2[i]),960,y)

    led_text(display_surf,fm_input,420,560,(255,255,255))

    t=max(0,int(fm_timer-(time.time()-fm_start)))
    led_text(display_surf,f"TIME {t}",520,520,(255,80,80))

def draw_end():
    display_surf.fill((0,0,0))
    total=sum(fm_s1)+sum(fm_s2)
    txt="WIN!" if total>=200 else "LOSE"
    led_text(display_surf,txt,480,300)

# =========================
# HOST UI
# =========================
class Btn:
    def __init__(self,x,y,w,h,txt,act):
        self.r=pygame.Rect(x,y,w,h)
        self.t=txt
        self.a=act
    def draw(self):
        pygame.draw.rect(host_surf,(255,200,0),self.r)
        host_surf.blit(font.render(self.t,1,(0,0,0)),(self.r.x+10,self.r.y+10))
    def click(self,pos):
        if self.r.collidepoint(pos): self.a()

buttons=[
    Btn(20,20,160,40,"A",lambda:buzzer("A")),
    Btn(200,20,160,40,"B",lambda:buzzer("B")),
    Btn(20,80,160,40,"STRIKE",strike),
    Btn(200,80,160,40,"NEXT",next_round)
]
for i in range(8):
    buttons.append(Btn(20+(i%2)*180,150+(i//2)*50,160,40,f"{i+1}",lambda i=i:reveal(i)))

def draw_host():
    host_surf.fill((30,30,30))
    for b in buttons: b.draw()

# =========================
# LOOP
# =========================
clock=pygame.time.Clock()
start=time.time()

running=True
while running:

    for e in pygame.event.get():
        if e.type==pygame.QUIT: running=False

        if e.type==pygame.MOUSEBUTTONDOWN:
            for b in buttons:
                b.click(pygame.mouse.get_pos())

        if e.type==pygame.KEYDOWN:
            if e.key==pygame.K_ESCAPE: running=False

            if phase=="FAST":
                if e.key==pygame.K_RETURN:
                    if fm_q<5:
                        q,data=FM_Q[fm_q]
                        ans=fm_input.upper()
                        pts=data.get(ans,0)

                        if fm_player==2 and ans in fm_a1:
                            pts=0

                        if fm_player==1:
                            fm_a1.append(ans); fm_s1.append(pts)
                        else:
                            fm_a2.append(ans); fm_s2.append(pts)

                        fm_input=""; fm_q+=1

                elif e.key==pygame.K_BACKSPACE:
                    fm_input=fm_input[:-1]
                else:
                    fm_input+=e.unicode

    # UPDATE
    if phase=="INTRO":
        display_surf.fill((0,0,0))
        led_text(display_surf,"FAMILY FEUD",350,250)
        if time.time()-start>3:
            phase="MAIN"

    elif phase=="MAIN":
        update_anim()
        update_score()
        draw_main()

    elif phase=="FAST":
        draw_fast()
        if time.time()-fm_start>fm_timer:
            if fm_player==1:
                fm_player=2
                fm_q=0
                fm_timer=25
                fm_start=time.time()
            else:
                phase="END"
                sfx("win")

    elif phase=="END":
        draw_end()

    draw_host()

    display_ren.clear()
    display_ren.blit(display_surf,(0,0))
    display_ren.present()

    host_ren.clear()
    host_ren.blit(host_surf,(0,0))
    host_ren.present()

    clock.tick(60)

pygame.quit()
sys.exit()
