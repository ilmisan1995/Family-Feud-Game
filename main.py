import pygame, json, time, os, sys

pygame.init()

# =========================
# SCREEN
# =========================
W, H = 1280, 720
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Family Feud FINAL")

clock = pygame.time.Clock()

# =========================
# LOAD ASSETS
# =========================
def load(name):
    return pygame.image.load(f"assets/{name}").convert_alpha()

board = load("main board.png")
blank = load("blank.png")
strike_img = load("strike.png")
numbers = [load(f"{i}.png") for i in range(1,9)]

font = pygame.font.SysFont("arial", 30, True)
big  = pygame.font.SysFont("arial", 60, True)

# =========================
# LOAD JSON (LIVE)
# =========================
data = {}
def load_json():
    global data
    if os.path.exists("soal_live.json"):
        with open("soal_live.json") as f:
            data = json.load(f)

# =========================
# MAIN GAME STATE
# =========================
round_index = 0
revealed = [False]*8
score = 0
strikes = 0
target_score = 100

# =========================
# FAST MONEY STATE
# =========================
fm_player = 1
fm_q = 0
fm_input = ""
fm_score_total = 0
fm_start = time.time()
fm_time = 20

# =========================
# DRAW MAIN GAME
# =========================
def draw_main():
    screen.blit(board,(0,0))

    if not data.get("rounds"): return

    r = data["rounds"][round_index]

    # QUESTION
    qtxt = font.render(r["question"],1,(255,255,255))
    screen.blit(qtxt,(500,120))

    # ANSWERS
    for i,a in enumerate(r["answers"]):
        x = 300 if i<4 else 750
        y = 200+(i%4)*80

        if revealed[i]:
            txt = font.render(a["text"],1,(255,255,255))
            pts = font.render(str(a["points"]),1,(255,0,0))
            screen.blit(txt,(x,y))
            screen.blit(pts,(x+200,y))
        else:
            screen.blit(blank,(x,y))
            screen.blit(numbers[i],(x+70,y))

    # SCORE
    s = big.render(str(score),1,(255,220,0))
    screen.blit(s,(550,50))

    # STRIKE
    for i in range(strikes):
        screen.blit(strike_img,(50+i*60,600))

# =========================
# DRAW FAST MONEY
# =========================
def draw_fast():
    screen.fill((150,0,0))

    if not data.get("fast_money"): return

    if fm_q < 5:
        q = data["fast_money"][fm_q]["question"]
        screen.blit(font.render(q,1,(255,255,255)),(400,100))

    screen.blit(font.render(fm_input,1,(255,255,0)),(400,500))

    # TIMER
    t = int(fm_time-(time.time()-fm_start))
    screen.blit(big.render(str(max(0,t)),1,(255,220,0)),(600,50))

    # TOTAL
    screen.blit(big.render(str(fm_score_total),1,(255,255,255)),(550,300))

# =========================
# GAME LOOP
# =========================
phase = "MAIN"
load_json()

running=True
while running:

    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            running=False

        if e.type==pygame.KEYDOWN:

            # =================
            # MAIN GAME
            # =================
            if phase=="MAIN":

                if pygame.K_1 <= e.key <= pygame.K_8:
                    i = e.key - pygame.K_1
                    if not revealed[i] and i < len(data["rounds"][0]["answers"]):
                        revealed[i] = True
                        score += data["rounds"][0]["answers"][i]["points"]

                        if score >= target_score:
                            phase = "FAST"
                            fm_start = time.time()

                if e.key == pygame.K_x:
                    if strikes < 3:
                        strikes += 1

            # =================
            # FAST MONEY
            # =================
            elif phase=="FAST":

                if e.key == pygame.K_RETURN:
                    if fm_q < 5:
                        qdata = data["fast_money"][fm_q]["answers"]
                        pts = qdata.get(fm_input.upper(),0)
                        fm_score_total += pts

                        fm_input=""
                        fm_q +=1

                elif e.key == pygame.K_BACKSPACE:
                    fm_input = fm_input[:-1]
                else:
                    fm_input += e.unicode

    # TIMER FAST MONEY
    if phase=="FAST":
        if time.time() - fm_start > fm_time:
            phase = "END"

    # DRAW
    if phase=="MAIN":
        draw_main()
    elif phase=="FAST":
        draw_fast()
    else:
        screen.fill((0,0,0))
        msg = "WIN!" if fm_score_total >= 200 else "LOSE"
        screen.blit(big.render(msg,1,(255,200,0)),(500,300))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
