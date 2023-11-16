import tkinter as tk
from tkinter import ttk
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class Values:
    name: str = "w233w"
    rank: int = 1
    gold: int = 0
    health: int = 100
    insight: int = 0
    sans: int = 100
    twist_rate: int = 0
    wisdom: int = 3
    strength: int = 3
    agility: int = 3
    items: defaultdict[int] = field(default_factory=lambda: defaultdict(int))


class UI:
    def __init__(self) -> None:
        self.values = Values()

        self.root = tk.Tk()
        self.root.title("mini")
        self.root.geometry("240x240")
        self.root.resizable(width=False, height=False)
        self.root.configure(background="#d3d3d3")

        # 菜单
        self.menubar = tk.Menu(self.root)
        self.menu_start = tk.Menu(self.menubar, tearoff=0)
        self.menu_start.add_command(label="Save Manually", command=None)
        self.menu_start.add_separator()
        self.menu_start.add_command(label="Exit", command=self.root.destroy)
        self.menubar.add_cascade(label="Game", menu=self.menu_start)
        self.root.config(menu=self.menubar)

        # 主体
        self.style = ttk.Style()
        self.style.layout("Tabless.TNotebook.Tab", [])  # turn off tabs
        self.tabview = ttk.Notebook(self.root, style="Tabless.TNotebook")
        self.tabview.pack(expand=True, fill=tk.BOTH)

        # 状态栏
        self.status = tk.StringVar()
        self.status.set(" ...")
        self.statusbar = tk.Label(
            self.root, textvariable=self.status, bd=1, relief=tk.SUNKEN, anchor=tk.W
        )
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        # 各个Tab
        self.main_frame = tk.Frame(self.tabview)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.tabview.add(self.main_frame, text="Main")

        self.map_frame = tk.Frame(self.tabview)
        self.map_frame.pack(fill=tk.BOTH, expand=True)
        self.tabview.add(self.map_frame, text="Map")

        self.ritual_frame = tk.Frame(self.tabview)
        self.ritual_frame.pack(fill=tk.BOTH, expand=True)
        self.tabview.add(self.ritual_frame, text="Ritual")

        self.items_frame = tk.Frame(self.tabview)
        self.items_frame.pack(fill=tk.BOTH, expand=True)
        self.tabview.add(self.items_frame, text="Items")

        self.shop_frame = tk.Frame(self.tabview)
        self.shop_frame.pack(fill=tk.BOTH, expand=True)
        self.tabview.add(self.shop_frame, text="Shop")

        self.skill_frame = tk.Frame(self.tabview)
        self.skill_frame.pack(fill=tk.BOTH, expand=True)
        self.tabview.add(self.skill_frame, text="Skill")

        self.challenge_frame = tk.Frame(self.tabview)
        self.challenge_frame.pack(fill=tk.BOTH, expand=True)
        self.tabview.add(self.challenge_frame, text="Challenge")

        self.archivement_frame = tk.Frame(self.tabview)
        self.archivement_frame.pack(fill=tk.BOTH, expand=True)
        self.tabview.add(self.archivement_frame, text="Archivement")

        self.setting_frame = tk.Frame(self.tabview)
        self.setting_frame.pack(fill=tk.BOTH, expand=True)
        self.tabview.add(self.setting_frame, text="Setting")

        # 绘制各个Tab
        self.main_page()
        self.map_page()
        self.ritual_page()
        self.items_page()
        self.shop_page()
        self.skill_page()
        self.challenge_page()
        self.archivement_page()
        self.setting_page()

    def main_page(self):
        # 上半部分
        self.Upper = tk.Frame(self.main_frame, padx=2)
        self.Upper.place(relheight=0.25, relwidth=1, relx=0, rely=0)

        # 名字
        self.name_tag = tk.Label(self.Upper, text="探员:", bd=1, relief="ridge")
        self.name_tag.place(relheight=0.5, relwidth=1 / 6, relx=0, rely=0)
        self.name = tk.StringVar()
        self.name_label = tk.Label(
            self.Upper, textvariable=self.name, bd=1, relief="ridge"
        )
        self.name_label.place(relheight=0.5, relwidth=1 / 3, relx=1 / 6, rely=0)

        # 等阶
        self.rank_tag = tk.Label(self.Upper, text="等阶:", bd=1, relief="ridge")
        self.rank_tag.place(relheight=0.5, relwidth=1 / 6, relx=0.5, rely=0)
        self.rank = tk.StringVar()
        self.rank_label = tk.Label(
            self.Upper, textvariable=self.rank, bd=1, relief="ridge"
        )
        self.rank_label.place(relheight=0.5, relwidth=1 / 3, relx=2 / 3, rely=0)

        # 灵视
        self.insight_tag = tk.Label(self.Upper, text="灵视:", bd=1, relief="ridge")
        self.insight_tag.place(relheight=0.5, relwidth=1 / 6, relx=0, rely=0.5)
        self.insight = tk.StringVar()
        self.insight_label = tk.Label(
            self.Upper, textvariable=self.insight, bd=1, relief="ridge"
        )
        self.insight_label.place(relheight=0.5, relwidth=1 / 6, relx=1 / 6, rely=0.5)

        # 理智
        self.sans_tag = tk.Label(self.Upper, text="理智:", bd=1, relief="ridge")
        self.sans_tag.place(relheight=0.5, relwidth=1 / 6, relx=1 / 3, rely=0.5)
        self.sans = tk.StringVar()
        self.sans_label = tk.Label(
            self.Upper, textvariable=self.sans, bd=1, relief="ridge"
        )
        self.sans_label.place(relheight=0.5, relwidth=1 / 6, relx=0.5, rely=0.5)

        # 扭曲
        self.twist_rate_tag = tk.Label(self.Upper, text="扭曲度:", bd=0.5, relief="ridge")
        self.twist_rate_tag.place(relheight=0.5, relwidth=1 / 6, relx=2 / 3, rely=0.5)
        self.twist_rate = tk.StringVar()
        self.twist_rate_label = tk.Label(
            self.Upper, textvariable=self.twist_rate, bd=1, relief="ridge"
        )
        self.twist_rate_label.place(relheight=0.5, relwidth=1 / 6, relx=5 / 6, rely=0.5)

        # 下半部分
        self.Lower = tk.Frame(self.main_frame)
        self.Lower.place(relheight=0.75, relwidth=1, relx=0, rely=0.25)

        # 地图
        self.map_buttom = tk.Button(self.Lower, text="Map", width=12)
        self.map_buttom.place(relx=0.25, rely=0.125, relheight=0.2, anchor=tk.CENTER)
        self.map_buttom.config(command=lambda: self.tabview.select(self.map_frame))

        # 仪式
        self.ritual_buttom = tk.Button(self.Lower, text="Ritual", width=12)
        self.ritual_buttom.place(relx=0.75, rely=0.125, relheight=0.2, anchor=tk.CENTER)
        self.ritual_buttom.config(
            command=lambda: self.tabview.select(self.ritual_frame)
        )

        # 物品
        self.items_buttom = tk.Button(self.Lower, text="Items", width=12)
        self.items_buttom.place(relx=0.25, rely=0.375, relheight=0.2, anchor=tk.CENTER)
        self.items_buttom.config(command=lambda: self.tabview.select(self.items_frame))

        # 商店
        self.shop_buttom = tk.Button(self.Lower, text="Shop", width=12)
        self.shop_buttom.place(relx=0.75, rely=0.375, relheight=0.2, anchor=tk.CENTER)
        self.shop_buttom.config(command=lambda: self.tabview.select(self.shop_frame))

        # 技能
        self.skill_buttom = tk.Button(self.Lower, text="Skill", width=12)
        self.skill_buttom.place(relx=0.25, rely=0.625, relheight=0.2, anchor=tk.CENTER)
        self.skill_buttom.config(command=lambda: self.tabview.select(self.skill_frame))

        # 挑战
        self.challenge_buttom = tk.Button(self.Lower, text="Challenge", width=12)
        self.challenge_buttom.place(
            relx=0.75, rely=0.625, relheight=0.2, anchor=tk.CENTER
        )
        self.challenge_buttom.config(
            command=lambda: self.tabview.select(self.challenge_frame)
        )

        # 成就
        self.archivement_buttom = tk.Button(self.Lower, text="Archivement", width=12)
        self.archivement_buttom.place(
            relx=0.25, rely=0.875, relheight=0.2, anchor=tk.CENTER
        )
        self.archivement_buttom.config(
            command=lambda: self.tabview.select(self.archivement_frame)
        )

        # 设置
        self.setting_buttom = tk.Button(self.Lower, text="Setting", width=12)
        self.setting_buttom.place(
            relx=0.75, rely=0.875, relheight=0.2, anchor=tk.CENTER
        )
        self.setting_buttom.config(
            command=lambda: self.tabview.select(self.setting_frame)
        )

        self.update_main()

    def update_main(self):
        self.name.set(self.values.name)
        self.rank.set(self.values.rank)
        self.insight.set(self.values.insight)
        self.sans.set(self.values.sans)
        self.twist_rate.set(str(self.values.twist_rate) + "%")
        self.root.after(100, self.update_main)

    # 选择地图后直接开始行动，触发事件会提示，30秒不理会则跳过
    def map_page(self):
        self.back_buttom = tk.Button(
            self.map_frame,
            text="Back",
            width=15,
            command=lambda: self.tabview.select(self.main_frame),
        )
        self.back_buttom.pack(side="bottom")

    def ritual_page(self):
        self.back_buttom = tk.Button(
            self.ritual_frame,
            text="Back",
            width=15,
            command=lambda: self.tabview.select(self.main_frame),
        )
        self.back_buttom.pack(side="bottom")

    def items_page(self):
        self.back_buttom = tk.Button(
            self.items_frame,
            text="Back",
            width=15,
            command=lambda: self.tabview.select(self.main_frame),
        )
        self.back_buttom.pack(side="bottom")

    def shop_page(self):
        self.currency_frame = tk.Frame(self.shop_frame, padx=2)
        self.currency_frame.place(relx=0, rely=0, relheight=1 / 8, relwidth=1)

        self.gold = tk.StringVar()
        self.gold.set(self.values.gold)
        self.gold_tag = tk.Label(self.currency_frame, text="金钱", bd=1, relief="ridge")
        self.gold_tag.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.gold_label = tk.Label(
            self.currency_frame, textvariable=self.gold, bd=1, relief="ridge"
        )
        self.gold_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.shopping_frame = tk.Frame(self.shop_frame, padx=2, pady=10)
        self.shopping_frame.place(relx=0, rely=1 / 8, relheight=7 / 8, relwidth=1)

        self.shopping_item1 = tk.Label(self.shopping_frame, text="1号商品")
        self.shopping_item1.place(relx=0, rely=0, relheight=1 / 7, relwidth=0.7)
        self.shopping_button1 = tk.Button(self.shopping_frame, text="shop_item1")
        self.shopping_button1.place(relx=0.7, rely=0, relheight=1 / 7, relwidth=0.3)

        self.shop_item_dict = {
            "test": 20,
            "test2": 10,
        }

        # 在按钮可用性层面解决购买金钱不够的情况
        def shopping_item(item: str):
            price = self.shop_item_dict.get(item, 0)
            match item:
                case "test":
                    self.values.gold -= price
                    self.values.sans += 3

        self.shopping_button1.config(command=lambda: shopping_item("test2"))

        self.back_buttom = tk.Button(
            self.shopping_frame,
            text="Back",
            width=15,
            command=lambda: self.tabview.select(self.main_frame),
        )
        self.back_buttom.pack(side="bottom")

        self.update_shop()

    def refresh_shop(self):
        self.values.gold += 1
        self.gold.set(self.values.gold)

    def update_shop(self):
        self.refresh_shop()
        self.root.after(100, self.update_shop)

    def skill_page(self):
        self.back_buttom = tk.Button(
            self.skill_frame,
            text="Back",
            width=15,
            command=lambda: self.tabview.select(self.main_frame),
        )
        self.back_buttom.pack(side="bottom")
        pass

    def challenge_page(self):
        self.back_buttom = tk.Button(
            self.challenge_frame,
            text="Back",
            width=15,
            command=lambda: self.tabview.select(self.main_frame),
        )
        self.back_buttom.pack(side="bottom")
        pass

    def archivement_page(self):
        self.back_buttom = tk.Button(
            self.archivement_frame,
            text="Back",
            width=15,
            command=lambda: self.tabview.select(self.main_frame),
        )
        self.back_buttom.pack(side="bottom")
        pass

    def setting_page(self):
        self.back_buttom = tk.Button(
            self.setting_frame,
            text="Back",
            width=15,
            command=lambda: self.tabview.select(self.main_frame),
        )
        self.back_buttom.pack(side="bottom")

        self.t1flag = True
        self.t1 = tk.Label(self.setting_frame, bg="red")
        self.t1.pack(fill="both", expand=1)
        self.t2 = tk.Label(self.setting_frame, bg="green", text="hover")
        self.t2.pack(fill="both", expand=1)
        self.t2.bind("<Enter>", self.foo)

    def foo(self, event):
        if self.t1flag:
            self.t1.config(bg="blue")
        else:
            self.t1.config(bg="cyan")
        self.t1flag = not self.t1flag

    def update_status(self, message):
        self.status.set(message)
        self.root.after(1500, self.reset_status)

    def reset_status(self, event):
        pass
        self.status.set(" ...")

    def run(self):
        self.root.mainloop()


UI().run()
