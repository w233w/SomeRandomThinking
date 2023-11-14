from tkinter import *
import random
import traceback


class GUI:
    def __init__(self) -> None:
        self.root = Tk()
        self.root.title("mini")
        self.root.geometry("240x240")
        self.root.resizable(width=False, height=False)

        # Core parameter
        self.lawn = 0
        self.lawn_svar = StringVar(value=self.lawn)
        self.delta_lawn = 0

        self.barricade = 10
        self.barricade_svar = StringVar(value=self.barricade)
        self.delta_barricade = 0

        self.garage = 0
        self.garage_svar = StringVar(value=self.garage)
        self.delta_garage = 0

        self.zombies = 1
        self.zombies_svar = StringVar(value=self.zombies)
        self.new_zombies = 0
        self.kill_zombies = 0

        # Helper parameter
        self.zombies_come = True

        # info parameter
        self.info = StringVar(value="信息栏\n")

        # menu
        self.menubar = Menu(self.root)
        self.menu_start = Menu(self.menubar, tearoff=0)
        self.menu_start.add_command(label="Restart", command=self.reset)
        self.menu_start.add_separator()
        self.menu_start.add_command(label="Exit", command=self.root.destroy)
        self.menubar.add_cascade(label="Game", menu=self.menu_start)
        self.root.config(menu=self.menubar)

        # row1
        self.Z_frame = Frame(self.root)
        self.Z_frame.pack(fill=BOTH, expand=True)
        self.Z_label = Label(self.Z_frame, text="Zombies:", anchor=CENTER)
        self.Z_label.place(
            relx=0.25, rely=0.5, relheight=1, relwidth=0.5, anchor=CENTER
        )
        self.Zv_label = Label(
            self.Z_frame, textvariable=self.zombies_svar, anchor=CENTER
        )
        self.Zv_label.place(
            relx=0.75, rely=0.5, relheight=1, relwidth=0.5, anchor=CENTER
        )

        self.LHP_frame = Frame(self.root)
        self.LHP_frame.pack(fill=BOTH, expand=True)
        self.L_label = Label(self.LHP_frame, text="荣耀", anchor=CENTER)
        self.L_label.place(
            relx=1 / 12, rely=0.5, relheight=1, relwidth=1 / 6, anchor=CENTER
        )
        self.Lv_label = Label(
            self.LHP_frame, textvariable=self.lawn_svar, anchor=CENTER
        )
        self.Lv_label.place(
            relx=3 / 12, rely=0.5, relheight=1, relwidth=1 / 6, anchor=CENTER
        )
        self.H_label = Label(self.LHP_frame, text="生命")
        self.H_label.place(
            relx=5 / 12, rely=0.5, relheight=1, relwidth=1 / 6, anchor=CENTER
        )
        self.Hv_label = Label(
            self.LHP_frame, textvariable=self.barricade_svar, anchor=CENTER
        )
        self.Hv_label.place(
            relx=7 / 12, rely=0.5, relheight=1, relwidth=1 / 6, anchor=CENTER
        )
        self.P_label = Label(self.LHP_frame, text="进度")
        self.P_label.place(
            relx=9 / 12, rely=0.5, relheight=1, relwidth=1 / 6, anchor=CENTER
        )
        self.Pv_label = Label(
            self.LHP_frame, textvariable=self.garage_svar, anchor=CENTER
        )
        self.Pv_label.place(
            relx=11 / 12, rely=0.5, relheight=1, relwidth=1 / 6, anchor=CENTER
        )

        self.SFB_info_frame = Frame(self.root)
        self.SFB_info_frame.pack(fill=BOTH, expand=True)
        self.SFB_info_label = Label(
            self.SFB_info_frame, text="4个D6行动点, 攻击>2生效\n修理>3生效,逃离>4生效"
        )
        self.SFB_info_label.pack(fill=BOTH, expand=True)

        self.SFB_frame = Frame(self.root)
        self.SFB_frame.pack(fill=BOTH, expand=True)
        self.S_label = Label(self.SFB_frame, text="攻击")
        self.S_label.place(
            relx=1 / 12, rely=0.5, relheight=1, relwidth=1 / 6, anchor=CENTER
        )
        self.S_entry = Entry(self.SFB_frame)
        self.S_entry.place(
            relx=3 / 12, rely=0.5, relheight=0.6, relwidth=1 / 7, anchor=CENTER
        )
        self.F_label = Label(self.SFB_frame, text="修理")
        self.F_label.place(
            relx=5 / 12, rely=0.5, relheight=1, relwidth=1 / 6, anchor=CENTER
        )
        self.F_entry = Entry(self.SFB_frame)
        self.F_entry.place(
            relx=7 / 12, rely=0.5, relheight=0.6, relwidth=1 / 7, anchor=CENTER
        )
        self.B_label = Label(self.SFB_frame, text="逃离")
        self.B_label.place(
            relx=9 / 12, rely=0.5, relheight=1, relwidth=1 / 6, anchor=CENTER
        )
        self.B_entry = Entry(self.SFB_frame)
        self.B_entry.place(
            relx=11 / 12, rely=0.5, relheight=0.6, relwidth=1 / 7, anchor=CENTER
        )

        self.A_frame = Frame(self.root)
        self.A_frame.pack(fill=BOTH, expand=True)
        self.A_button = Button(self.A_frame, text="Action", width=12, command=self.turn)
        self.A_button.place(relx=0.5, rely=0.5, relheight=0.9, anchor=CENTER)

        self.I_frame = Frame(self.root)
        self.I_frame.pack(fill=X, expand=True)
        self.I_label = Label(self.I_frame, textvariable=self.info, anchor=CENTER)
        self.I_label.pack(fill=X, expand=True)

    def reset(self):
        self.lawn = 0
        self.barricade = 10
        self.garage = 10
        self.zombies = 0
        self.info.set("信息栏\n\n")
        self.refresh_label()

    def refresh_label(self):
        self.lawn_svar.set(self.lawn)
        self.barricade_svar.set(self.barricade)
        self.garage_svar.set(self.garage)
        self.zombies_svar.set(self.zombies)

    def fix_barricade(self, v: int):
        if self.barricade + v <= 10:
            self.barricade += v
            self.delta_barricade += v
        else:
            self.delta_barricade += 10 - self.barricade
            self.barricade = 10

    def progress(self):
        self.garage += 10
        self.delta_garage += 10

    def use_lawn(self):
        self.lawn -= 10
        self.delta_lawn += 10

    def event_on_action(self):
        s = int(self.S_entry.get())
        f = int(self.F_entry.get())
        b = int(self.B_entry.get())

        if s + f + b != 4:
            raise ValueError("Sum must be 4!")

        for _ in range(s):
            # roll a dice, if hit [3,4,5,6] then pass, else fail.
            # pass check will kill 1 zombie.
            # for every zombie killed, player gain 1 lawn.
            if random.choice(range(1, 7)) in range(3, 7):
                if self.zombies >= 1:
                    self.lawn += 1
                    self.delta_lawn += 1
                    self.zombies -= 1
                    self.kill_zombies += 1
        for _ in range(f):
            if random.choice(range(1, 7)) in range(3, 7):
                self.fix_barricade(1)
        for _ in range(b):
            if random.choice(range(1, 7)) in range(5, 7):
                self.progress()

    def event_zombies_attack(self):
        self.barricade -= self.zombies
        self.delta_barricade -= self.zombies

    def event_make_reward_decision(self):
        if self.lawn >= 10:
            reward = Toplevel(self.root)
            reward.geometry("200x200")

            Label(reward, text="选择以下一种效果").pack(fill=BOTH, expand=True)
            Button(
                reward,
                text="敌人归零",
                command=lambda: [
                    setattr(self, "zombies", 0),
                    reward.destroy(),
                    reward.update(),
                    self.use_lawn(),
                    self.refresh_label(),
                ],
            ).pack(fill=BOTH, expand=True)
            Button(
                reward,
                text="进度加十",
                command=lambda: [
                    self.progress(),
                    reward.destroy(),
                    reward.update(),
                    self.use_lawn(),
                    self.refresh_label(),
                ],
            ).pack(fill=BOTH, expand=True)
            Button(
                reward,
                text="敌人增加归零",
                command=lambda: [
                    setattr(self, "zombies_come", False),
                    reward.destroy(),
                    reward.update(),
                    self.use_lawn(),
                    self.refresh_label(),
                ],
            ).pack(fill=BOTH, expand=True)
            Button(
                reward,
                text="回复三血",
                command=lambda: [
                    self.fix_barricade(3),
                    reward.destroy(),
                    reward.update(),
                    self.use_lawn(),
                    self.refresh_label(),
                ],
            ).pack(fill=BOTH, expand=True)
        else:
            return

    def event_zombie_income(self):
        if self.zombies_come is False:
            self.zombies_come = True
            return
        elif 0 <= self.garage < 40:
            self.zombies += 1
            self.new_zombies += 1
        elif 40 <= self.garage < 60:
            self.zombies += 2
            self.new_zombies += 2
        elif 60 <= self.garage < 90:
            self.zombies += 3
            self.new_zombies += 3
        elif 90 <= self.garage:
            self.zombies += 4
            self.new_zombies += 4

    def event_show_turn_result(self):
        s = f"敌人击杀{self.kill_zombies},"
        s += f"敌人新增{self.new_zombies},"
        s += f"荣誉增加{self.delta_lawn}\n"
        s += f"生命变化{self.delta_barricade},"
        s += f"进度提升{self.delta_garage}%。"
        if self.garage >= 100 and self.barricade > 0:
            s = "WIN\n"
        elif self.barricade <= 0:
            s = "LOSE\n"
        self.kill_zombies = 0
        self.new_zombies = 0
        self.delta_lawn = 0
        self.delta_barricade = 0
        self.delta_garage = 0
        self.info.set(s)
        self.refresh_label()

    def turn(self):
        if self.garage >= 100 and self.barricade > 0:
            return
        elif self.barricade <= 0:
            return
        try:
            self.event_on_action()
        except:
            traceback.print_exc()
            self.info.set("总和必须是4\n")
            return
        self.event_zombies_attack()
        self.event_make_reward_decision()
        self.event_zombie_income()
        self.event_show_turn_result()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    GUI().run()
