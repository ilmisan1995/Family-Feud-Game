import tkinter as tk
from tkinter import ttk
import json

# =========================
# DATA
# =========================
data = {
    "rounds": [],
    "fast_money": []
}

answers = [["",0] for _ in range(8)]
fm_answers = {}

# =========================
# ROOT
# =========================
root = tk.Tk()
root.title("EDITOR PRO - FAMILY FEUD FINAL")
root.geometry("1400x800")
root.configure(bg="#0b1f66")

# =========================
# PANEL HELPER
# =========================
def panel(parent,title):
    f = tk.Frame(parent,bg="#0b1f66",bd=2,relief="ridge")
    tk.Label(f,text=title,fg="yellow",bg="#0b1f66",
             font=("Arial",12,"bold")).pack(anchor="w")
    return f

# =========================
# LEFT PANEL (ROUND)
# =========================
left = tk.Frame(root,bg="#0b1f66")
left.pack(side="left",fill="y",padx=10,pady=10)

f_round = panel(left,"MAIN GAME")
f_round.pack(fill="x")

round_type = tk.StringVar(value="single")
ttk.Combobox(f_round,textvariable=round_type,
             values=["single","double","triple","random"]).pack()

entry_q = tk.Entry(f_round,width=40)
entry_q.pack(pady=5)

# =========================
# TABLE JAWABAN
# =========================
tree = ttk.Treeview(left,columns=("No","Jawaban","Point"),
                    show="headings",height=8)

tree.heading("No",text="No")
tree.heading("Jawaban",text="Jawaban")
tree.heading("Point",text="Point")
tree.pack()

def refresh_table():
    tree.delete(*tree.get_children())
    for i,a in enumerate(answers):
        tree.insert("", "end", values=(i+1,a[0],a[1]))

refresh_table()

entry_ans = tk.Entry(left)
entry_pts = tk.Entry(left,width=5)
entry_ans.pack(side="left")
entry_pts.pack(side="left")

def add_answer():
    for i in range(8):
        if answers[i][0]=="":
            answers[i][0]=entry_ans.get().upper()
            try: answers[i][1]=int(entry_pts.get())
            except: answers[i][1]=0
            break
    refresh_table()
    preview()

def delete_answer():
    sel = tree.selection()
    if sel:
        idx = tree.index(sel[0])
        answers[idx]=["",0]
        refresh_table()
        preview()

tk.Button(left,text="Tambah",command=add_answer).pack()
tk.Button(left,text="Hapus",command=delete_answer).pack()

# =========================
# SAVE ROUND
# =========================
def save_round():
    r = {
        "type": round_type.get(),
        "question": entry_q.get(),
        "answers":[{"text":a[0],"points":a[1]} for a in answers if a[0]]
    }
    data["rounds"].append(r)
    update_json()

tk.Button(left,text="Simpan Round",bg="green",fg="white",
          command=save_round).pack(pady=5)

# =========================
# FAST MONEY PANEL
# =========================
right = tk.Frame(root,bg="#0b1f66")
right.pack(side="right",fill="y",padx=10)

f_fm = panel(right,"FAST MONEY")
f_fm.pack(fill="x")

fm_q = tk.Entry(f_fm,width=30)
fm_q.pack()

fm_ans = tk.Entry(f_fm)
fm_pts = tk.Entry(f_fm,width=5)
fm_ans.pack(side="left")
fm_pts.pack(side="left")

def add_fm():
    try:
        fm_answers[fm_ans.get().upper()] = int(fm_pts.get())
    except:
        pass
    fm_ans.delete(0,"end")
    fm_pts.delete(0,"end")

tk.Button(f_fm,text="Tambah Jawaban",command=add_fm).pack()

def save_fm():
    data["fast_money"].append({
        "question": fm_q.get(),
        "answers": fm_answers.copy()
    })
    fm_answers.clear()
    update_json()

tk.Button(f_fm,text="Simpan FM",bg="orange",command=save_fm).pack()

# =========================
# PREVIEW BOARD
# =========================
canvas = tk.Canvas(root,width=700,height=450,bg="#102a80")
canvas.pack(pady=20)

def preview():
    canvas.delete("all")

    canvas.create_oval(100,50,600,400,outline="yellow",width=10)

    canvas.create_text(350,100,text=entry_q.get(),
                       fill="white",font=("Arial",14))

    for i in range(8):
        x = 150 if i<4 else 380
        y = 150+(i%4)*60

        canvas.create_rectangle(x,y,x+200,y+50,fill="orange")

        if answers[i][0]:
            canvas.create_text(x+10,y+20,anchor="w",
                               text=answers[i][0],fill="black")
            canvas.create_text(x+170,y+20,
                               text=str(answers[i][1]),fill="red")
        else:
            canvas.create_text(x+100,y+20,text=str(i+1))

entry_q.bind("<KeyRelease>",lambda e:preview())

# =========================
# JSON VIEW
# =========================
txt = tk.Text(root,height=10)
txt.pack(fill="both")

def update_json():
    txt.delete("1.0","end")
    txt.insert("end",json.dumps(data,indent=2))

# =========================
# AUTO SAVE (LIVE SYNC)
# =========================
def autosave():
    with open("soal_live.json","w") as f:
        json.dump(data,f,indent=2)
    root.after(1000, autosave)

# =========================
# INIT
# =========================
preview()
autosave()
root.mainloop()
