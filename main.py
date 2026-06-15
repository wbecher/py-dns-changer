import os
import sys
import ctypes
import subprocess
import psutil
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem

# Path para configurações
CONFIG_FILE = "dns_config.json"

DEFAULT_PROFILES = {
    "Google": {"primary": "8.8.8.8", "secondary": "8.8.4.4"},
    "Cloudflare": {"primary": "1.1.1.1", "secondary": "1.0.0.1"}
}

dns_profiles = {}
selected_interface = ""
active_dns_profile = ""
icon_instance = None
root_window = None

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def load_dns_profiles():
    global dns_profiles
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                dns_profiles = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
            dns_profiles = DEFAULT_PROFILES.copy()
    else:
        dns_profiles = DEFAULT_PROFILES.copy()
        save_dns_profiles()

def save_dns_profiles():
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(dns_profiles, f, indent=4)
    except Exception as e:
        print(f"Erro ao salvar configurações: {e}")

def get_active_interfaces():
    interfaces = []
    stats = psutil.net_if_stats()
    addrs = psutil.net_if_addrs()
    for name, stat in stats.items():
        if stat.isup and name in addrs:
            if "loopback" not in name.lower() and "localhost" not in name.lower():
                interfaces.append(name)
    return interfaces

def set_dns(profile_name):
    global selected_interface, dns_profiles, active_dns_profile
    if not selected_interface:
        print("Nenhuma interface selecionada.")
        return

    if profile_name == "dhcp":
        cmd_dhcp = f'netsh interface ipv4 set dns name="{selected_interface}" dhcp'
        subprocess.run(cmd_dhcp, shell=True, capture_output=True)
        print(f"DNS restaurado para DHCP na interface: {selected_interface}")
        if icon_instance:
            icon_instance.notify(f"Restaurado para DHCP", title="DNS Alterado")
        active_dns_profile = "dhcp"
    elif profile_name in dns_profiles:
        prof = dns_profiles[profile_name]
        cmd_primary = f'netsh interface ipv4 set dns name="{selected_interface}" static {prof["primary"]} primary'
        cmd_secondary = f'netsh interface ipv4 add dns name="{selected_interface}" {prof["secondary"]} index=2'
        
        subprocess.run(cmd_primary, shell=True, capture_output=True)
        if prof.get("secondary"):
            subprocess.run(cmd_secondary, shell=True, capture_output=True)
            
        print(f"DNS alterado para {profile_name} na interface: {selected_interface}")
        if icon_instance:
            icon_instance.notify(f"DNS alterado para {profile_name}", title="DNS Alterado")
        active_dns_profile = profile_name

def select_interface_action(interface_name):
    global selected_interface
    selected_interface = interface_name
    print(f"Interface selecionada alterada para: {selected_interface}")

def make_interface_action(iface):
    def action(icon, item):
        select_interface_action(iface)
    return action

def make_interface_checked(iface):
    def is_checked(item):
        return selected_interface == iface
    return is_checked

def make_dns_action(profile_name):
    def action(icon, item):
        set_dns(profile_name)
    return action

def make_dns_checked(profile_name):
    def is_checked(item):
        return active_dns_profile == profile_name
    return is_checked

def get_menu_items():
    global selected_interface
    interfaces = get_active_interfaces()
    
    if not selected_interface and interfaces:
        selected_interface = interfaces[0]

    interface_menu_items = []
    for iface in interfaces:
        interface_menu_items.append(
            MenuItem(iface, make_interface_action(iface), checked=make_interface_checked(iface), radio=True)
        )
    
    dns_menu_items = []
    for profile_name in dns_profiles.keys():
        dns_menu_items.append(
            MenuItem(profile_name, make_dns_action(profile_name), checked=make_dns_checked(profile_name), radio=True)
        )
    
    dns_menu_items.append(Menu.SEPARATOR)
    dns_menu_items.append(
        MenuItem('Automático (DHCP)', make_dns_action("dhcp"), checked=make_dns_checked("dhcp"), radio=True)
    )

    menu_items = [
        MenuItem(lambda item: f'Interface Atual: {selected_interface}', lambda: None, enabled=False),
        MenuItem('Selecionar Interface', Menu(lambda: interface_menu_items)),
        MenuItem('Selecionar DNS', Menu(lambda: dns_menu_items)),
        Menu.SEPARATOR,
        MenuItem('Gerenciar DNS...', lambda icon, item: open_dns_manager_safe()),
        MenuItem('Status da Rede...', lambda icon, item: open_status_window_safe()),
        Menu.SEPARATOR,
        MenuItem('Sair', on_exit)
    ]
    
    return menu_items

def create_image():
    image = Image.new('RGB', (64, 64), color=(31, 41, 55))
    dc = ImageDraw.Draw(image)
    dc.ellipse([(16, 16), (48, 48)], fill=(59, 130, 246))
    return image

def on_exit(icon, item):
    icon.stop()
    if root_window:
        root_window.after(0, root_window.destroy)

# -- GUI Code (Tkinter) --

def open_dns_manager_safe():
    if root_window:
        root_window.after(0, open_dns_manager)

def open_status_window_safe():
    if root_window:
        root_window.after(0, open_status_window)

def center_window(win, width, height):
    win.update_idletasks()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry(f'{width}x{height}+{x}+{y}')

def open_dns_manager():
    win = tk.Toplevel(root_window)
    win.title("Gerenciar DNS")
    center_window(win, 450, 350)
    win.grab_set()

    list_frame = tk.Frame(win)
    list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    tree = ttk.Treeview(list_frame, columns=("Nome", "Primário", "Secundário"), show="headings", selectmode="browse")
    tree.heading("Nome", text="Nome")
    tree.heading("Primário", text="Primário")
    tree.heading("Secundário", text="Secundário")
    tree.column("Nome", width=120)
    tree.column("Primário", width=120)
    tree.column("Secundário", width=120)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh_tree():
        for i in tree.get_children():
            tree.delete(i)
        for name, data in dns_profiles.items():
            tree.insert("", "end", values=(name, data.get("primary", ""), data.get("secondary", "")))

    refresh_tree()

    inputs_frame = tk.Frame(win)
    inputs_frame.pack(fill=tk.X, padx=10, pady=5)

    tk.Label(inputs_frame, text="Nome:").grid(row=0, column=0, sticky=tk.W)
    entry_name = tk.Entry(inputs_frame, width=15)
    entry_name.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(inputs_frame, text="Pri:").grid(row=0, column=2, sticky=tk.W)
    entry_primary = tk.Entry(inputs_frame, width=15)
    entry_primary.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(inputs_frame, text="Sec:").grid(row=1, column=2, sticky=tk.W)
    entry_secondary = tk.Entry(inputs_frame, width=15)
    entry_secondary.grid(row=1, column=3, padx=5, pady=5)

    def add_profile():
        name = entry_name.get().strip()
        pri = entry_primary.get().strip()
        sec = entry_secondary.get().strip()
        if not name or not pri:
            messagebox.showwarning("Erro", "Nome e DNS Primário são obrigatórios.", parent=win)
            return
        dns_profiles[name] = {"primary": pri, "secondary": sec}
        save_dns_profiles()
        refresh_tree()
        entry_name.delete(0, tk.END)
        entry_primary.delete(0, tk.END)
        entry_secondary.delete(0, tk.END)
        if icon_instance:
            icon_instance.update_menu()

    def remove_profile():
        selected = tree.selection()
        if not selected:
            return
        item = tree.item(selected[0])
        name = item['values'][0]
        if messagebox.askyesno("Confirmar", f"Tem certeza que deseja remover '{name}'?", parent=win):
            if name in dns_profiles:
                del dns_profiles[name]
                save_dns_profiles()
                refresh_tree()
                if icon_instance:
                    icon_instance.update_menu()

    btn_frame = tk.Frame(win)
    btn_frame.pack(fill=tk.X, padx=10, pady=10)
    
    tk.Button(btn_frame, text="Adicionar / Editar", command=add_profile).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Remover Selecionado", command=remove_profile).pack(side=tk.LEFT, padx=5)

def open_status_window():
    win = tk.Toplevel(root_window)
    win.title("Status da Rede")
    center_window(win, 600, 400)
    
    txt = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Consolas", 10))
    txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    txt.insert(tk.END, "Carregando configurações de rede...\n")
    txt.configure(state='disabled')
    
    def load_status():
        try:
            output_bytes = subprocess.check_output('ipconfig /all', shell=True)
            output = output_bytes.decode('cp850', errors='replace')
        except Exception as e:
            output = f"Erro ao executar ipconfig: {e}"
        
        # Atualiza GUI na thread principal
        if root_window:
            root_window.after(0, lambda: _update_status_text(txt, output))

    def _update_status_text(widget, text_content):
        widget.configure(state='normal')
        widget.delete(1.0, tk.END)
        widget.insert(tk.END, text_content)
        widget.configure(state='disabled')

    threading.Thread(target=load_status, daemon=True).start()

# -- End GUI Code --

def run_tray():
    global icon_instance
    dynamic_menu = Menu(lambda: get_menu_items())
    icon_instance = Icon("DNS Switcher", create_image(), title="Alternador de DNS", menu=dynamic_menu)
    icon_instance.run()

def main():
    global root_window
    
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        return

    load_dns_profiles()

    root_window = tk.Tk()
    root_window.withdraw() # Esconde a janela principal
    
    tray_thread = threading.Thread(target=run_tray, daemon=True)
    tray_thread.start()
    
    # Inicia loop do Tkinter (bloqueante, rodando na Main Thread)
    root_window.mainloop()

if __name__ == "__main__":
    main()