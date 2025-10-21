from tkinter import *
from tkinter import ttk

root = Tk()
root.geometry("500x500")
root.title("Cookie Clicker")

# Cookie NB display
Cookies = IntVar(value=0)

def updateCookieAmount(*args):
	CookieNBLabel.config(text=f"Your cookies: {Cookies.get()}")
	updateUpgradeButtons()

Cookies.trace_add("write", updateCookieAmount)

CookieNBLabel = Label(root, text=f"Your cookies: {Cookies.get()}", font=("Impact", 24))
CookieNBLabel.pack(fill=X, pady=10)

# Passive cookies display
PassiveCookieAmount = IntVar(value=0)

def updatePassiveCookieAmount(*args):
	PassiveCookieLabel.config(text=f"Passive cookies/second: {PassiveCookieAmount.get()}")

PassiveCookieAmount.trace_add("write", updatePassiveCookieAmount)

PassiveCookieLabel = Label(root, text=f"Passive cookies/second: {PassiveCookieAmount.get()}")
PassiveCookieLabel.pack(fill=X, pady=0)

def passiveCookieTick():
	passiveAmount = PassiveCookieAmount.get()
	if passiveAmount > 0:
		Cookies.set(Cookies.get() + passiveAmount)
	root.after(1000, passiveCookieTick)
passiveCookieTick()

# Get Cookie button
AddCookieAmount = IntVar(value=1)

## Cookies per click display
def updateAddCookieAmount(*args):
	AddCookieLabel.config(text=f"Cookies/click: {AddCookieAmount.get()}")

AddCookieAmount.trace_add("write", updateAddCookieAmount)

AddCookieLabel = Label(root, text=f"Cookies/click: {AddCookieAmount.get()}")
AddCookieLabel.pack(fill=X, pady=0)

def updateAddCookieButton(*args):
	c = AddCookieAmount.get()
	s = f"Get {c} cookie"
	if c > 1:
		s += "s"
	AddCookieButton.config(text=s)

AddCookieAmount.trace_add("write", updateAddCookieButton)

def addCookieButtonCmd():
	Cookies.set(Cookies.get() + AddCookieAmount.get())

AddCookieButton = Button(root, text=f"Get {AddCookieAmount.get()} cookie", command=addCookieButtonCmd)
AddCookieButton.pack(fill=X, pady=5)

# Upgrades Shop
style = ttk.Style()
style.theme_use("default")
style.configure(
	"Cookie.Horizontal.TProgressbar",
	throughcolor="#f2f2f2",
	background="#68ff54",
	thickness=4
)
class UpgradeWidget:
	def __init__(self, parent, upgrade_data, index):
		self.data = upgrade_data
		self.index = index

		self.frame = Frame(parent)
		self.frame.pack(fill=X, pady=4)

		self.button = Button(
			self.frame,
			text=f"{self.data['name']} ({self.data['cost']})",
			command=self.buy,
			state=DISABLED
		)
		self.button.pack(fill=X)

		self.description_label = Label(
			self.frame,
			text=self.data['description'],
			font=("Arial", 9),
			fg="gray"
		)
		self.description_label.pack(fill=X)

		self.progress = ttk.Progressbar(
			self.frame,
			length=100,
			mode="determinate",
			style="Cookie.Horizontal.TProgressbar"
		)
		self.progress.pack(fill=X, pady=2)

	def buy(self):
		if self.data['bought']:
			return
		cost = self.data['cost']
		if Cookies.get() >= cost:
			Cookies.set(Cookies.get() - cost)
			self.data['action']()
			self.data['bought'] = True
			refreshUpgradeList()
	
	def update(self):
		if self.data['bought']:
			self.button.config(
				state=DISABLED,
				text=f"{self.data['name']} (Bought)"
			)
			self.progress.forget()
			self.description_label.forget()
			return
		cost = self.data['cost']
		cookies = Cookies.get()
		can_afford = cookies >= cost
		self.button.config(state=NORMAL if can_afford else DISABLED)
		progress = min(100, int((cookies / cost) * 100))
		self.progress['value'] = progress

UpgradeFrameContainer = LabelFrame(root, text="Upgrades")
UpgradeFrameContainer.pack(fill=BOTH, expand=True, padx=10, pady=10)

UpgradeCanvas = Canvas(UpgradeFrameContainer)
UpgradeCanvas.pack(side=LEFT, fill=BOTH, expand=True)

UpgradeScrollBar = Scrollbar(UpgradeFrameContainer, orient=VERTICAL, command=UpgradeCanvas.yview)
UpgradeScrollBar.pack(side=RIGHT, fill=Y)

UpgradeCanvas.configure(yscrollcommand=UpgradeScrollBar.set)

UpgradeFrame = Frame(UpgradeCanvas)
UpgradeFrameWindow = UpgradeCanvas.create_window((0, 0), window=UpgradeFrame, anchor="nw")

def OnFrameConfigure(event):
	UpgradeCanvas.configure(scrollregion=UpgradeCanvas.bbox("all"))

UpgradeFrame.bind("<Configure>", OnFrameConfigure)

def OnMouseWheel(event):
	UpgradeCanvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

UpgradeCanvas.bind_all("<MouseWheel>", OnMouseWheel)

UpgradeCanvas.bind("<Configure>", lambda e: UpgradeCanvas.itemconfig(UpgradeFrameWindow, width=e.width - UpgradeScrollBar.winfo_width()))

Upgrades = [
	{
		"name": "Buy One, Get One Free!",
		"cost": 10,
		"description": "+1 cookie/click.",
		"action": lambda: AddCookieAmount.set(AddCookieAmount.get() + 1),
		"bought": False
	},
	{
		"name": "PCI (Passive Cookie Income)",
		"cost": 25,
		"description": "+1 cookie/second.",
		"action": lambda: PassiveCookieAmount.set(PassiveCookieAmount.get() + 1),
		"bought": False
	},
	{
		"name": "Unfair Trade",
		"cost": 50,
		"description": "+100 cookies.",
		"action": lambda: Cookies.set(Cookies.get() + 100),
		"bought": False
	},
	{
		"name": "Heavy Handed",
		"cost": 50,
		"description": "+1 cookie/click.",
		"action": lambda: AddCookieAmount.set(AddCookieAmount.get() + 1),
		"bought": False
	},
	{
		"name": "Rising Stocks",
		"cost": 100,
		"description": "+1 cookie/second.",
		"action": lambda: PassiveCookieAmount.set(PassiveCookieAmount.get() + 1),
		"bought": False
	},
	{
		"name": "Extra Finger",
		"cost": 150,
		"description": "+1 cookie/click.",
		"action": lambda: AddCookieAmount.set(AddCookieAmount.get() + 1),
		"bought": False
	},
	{
		"name": "Long Term Investment",
		"cost": 200,
		"description": "+2 cookies/second.",
		"action": lambda: PassiveCookieAmount.set(PassiveCookieAmount.get() + 2),
		"bought": False
	},
	{
		"name": "Extra Hand",
		"cost": 200,
		"description": "+3 cookies/click.",
		"action": lambda: AddCookieAmount.set(AddCookieAmount.get() + 3),
		"bought": False
	}
]

UpgradeWidgets = []
BoughtFrameVisible = BooleanVar(value=False)

def refreshUpgradeList():
	global AvailableFrame, BoughtUpgradeFrame, BoughtToggleButton

	for widget in UpgradeWidgets:
		widget.frame.destroy()
	UpgradeWidgets.clear()

	for child in UpgradeFrame.winfo_children():
		child.destroy()

	AvailableLabel = Label(UpgradeFrame, text="Available Upgrades", font=("Arial", 10, "bold"))
	AvailableLabel.pack(fill=X, pady=(5, 0))

	AvailableFrame = Frame(UpgradeFrame)
	AvailableFrame.pack(fill=X)

	BoughtFrame = Frame(UpgradeFrame)
	BoughtFrame.pack(fill=X, pady=(10, 0))

	BoughtCount = sum(1 for u in Upgrades if u['bought'])

	def ToggleBoughtSection():
		if BoughtFrameVisible.get():
			BoughtUpgradeFrame.pack_forget()
			BoughtToggleButton.config(text=f"Show Bought Upgrades ({BoughtCount})")
			BoughtFrameVisible.set(False)
		else:
			BoughtUpgradeFrame.pack(fill=X)
			BoughtToggleButton.config(text=f"Hide Bought Upgrades ({BoughtCount})")
			BoughtFrameVisible.set(True)
		
	BoughtToggleButton = Button(BoughtFrame, text=f"Show Bought Upgrades ({BoughtCount})", command=ToggleBoughtSection)
	BoughtToggleButton.pack(fill=X)

	if BoughtCount > 0:
		BoughtLabel = Label(BoughtFrame, text="Bought Upgrades", font=("Arial", 10, "bold"))
		BoughtLabel.pack(fill=X, pady=(5, 0))

	BoughtUpgradeFrame = Frame(BoughtFrame)

	sorted_upgrades = sorted(Upgrades, key=lambda u: u['cost'])

	for i, upgrade in enumerate(sorted_upgrades):
		target_frame = BoughtUpgradeFrame if upgrade['bought'] else AvailableFrame
		widget = UpgradeWidget(target_frame, upgrade, i)
		UpgradeWidgets.append(widget)

	if BoughtFrameVisible.get():
		BoughtUpgradeFrame.pack(fill=X)

	updateUpgradeButtons()

def updateUpgradeButtons():
	for widget in UpgradeWidgets:
		widget.update()

refreshUpgradeList()

root.mainloop()