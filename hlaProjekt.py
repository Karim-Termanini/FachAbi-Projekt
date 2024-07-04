### Imports:
# Sounds:
#   - import os:                                        - Für die Ausführung von Betriebssystembefehlen zur
#                                                                                               Sound-Wiedergabe.
#   - import platform:                                  - Zur Überprüfung des Betriebssystems für die Sound-Wiedergabe.


# GUI-Komponenten:
#   - from tkinter import:                              - Grundlegende GUI-Elemente.
#   - from customtkinter import:                        - Erweiterte GUI-Elemente und Design.

# Netzwerk-Validierung und -Information:
#   - from icmplib import ping, NameLookupError:        - Für Netzwerk-Ping-Operationen und Fehlerbehandlung.
#   - import re:                                        - Für reguläre Ausdrücke zur IP-Validierung.

# Allgemein:
#   - from website_info_module import:                  - Importiert benutzerdefinierte Funktionen zur Abfrage von
#                                                                                           Website-Informationen.

### Funktionen:
# Sounds:
#   - play_sound(sound_key):                            - Spielt anhand eines Schlüsselwortes einen Sound ab.

# Netzwerk-Validierung:
#   - is_valid_ip(ip):                                  - Überprüft die Gültigkeit einer IP-Adresse.
#   - is_valid_url(url):                                - Überprüft die Gültigkeit einer URL.

# Information und Aktualisierung:
#   - update_info():                                                    - Validiert Eingaben und aktualisiert die
#                                                                                   Anzeige von Netzwerkinformationen.
#   - show_detailed_info(), show_geo_info(), show_dns_info():           - Funktionen zum Anzeigen spezifischer
#                                                                                   Informationen in Popup-Fenstern.

# GUI-Interaktion und Zustandsmanagement:
#   - toggle_port_input():                                              - Wechselt zwischen manueller Porteingabe und
#                                                                                           Protokollauswahl.
#   - update_port_from_tab_selection():                                 - Aktualisiert den Port basierend auf der
#                                                                                               Auswahl im TabView.
#   - periodic_port_update():                                           - Aktualisiert periodisch den Port, wenn die
#                                                                               Eingabemethode auf "Liste" gesetzt ist.
#   - show_error(message), display_popup_window(title, content):        - Zeigen Fehlermeldungen oder Informationen in
#                                                                                                     Popup-Fenstern an.
#   - show_confirmation_dialog(), on_close():                           - Bestätigungsdialog beim Schließen der
#                                                                                                       Anwendung.

### Globale Variablen:
# Sounds:
#   - sound_files:                                                      - Dictionary mit Sound-Datei Zuweisungen zu
#                                                                                                   Schlüsselwörtern.

### GUI-Elemente und Layout:
#   - Verwendung von CTk* Klassen für Fenster, Frames, Labels,
#   Eingabefelder, Buttons und TabViews zur Gestaltung der Benutzeroberfläche.
########################################################################################################################

from website_info_module import *
import re
from tkinter import *
from customtkinter import *
from icmplib import ping, NameLookupError
import os
import platform
import threading
from tkinter import messagebox
import time
from datetime import datetime, timedelta

# Use datetime.datetime.today() for datetime operations
current_time = datetime.today()

sound_files = {
    "open": "open.wav",
    "close": "close.wav",
    "click": "click.wav",
    "error": "error.wav"
}


def play_sound(sound_key):
    sound_path = sound_files.get(sound_key)
    if not sound_path:
        print(f"Sound key '{sound_key}' not found.")
        return

    if platform.system() == "Windows":
        try:
            import winsound
            winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception as e:
            print(f"Failed to play sound on Windows: {e}")
    else:
        try:
            if platform.system() == "Darwin":  # macOS
                os.system(f"afplay {sound_path}")
            elif platform.system() == "Linux":
                os.system(f"aplay {sound_path}")
            else:
                print("Sound playback not supported on this operating system.")
        except Exception as e:
            print(f"Failed to play sound: {e}")


play_sound("open")

self = CTk()
self.title("HLA")
self.geometry("1700x900")
set_appearance_mode("dark")
set_default_color_theme("blue")
section1 = CTkFrame(master=self)
section1.grid(row=0, column=0)

section2 = CTkFrame(self)
section2.grid(row=0, column=2)

section3 = CTkFrame(master=self, height=700)
section3.grid(row=2, column=0, columnspan=3, sticky="ew")

section4 = CTkFrame(section3, height=0, width=0)
section4.grid(row=0, column=1)

info_var = StringVar(value="")
full_url = ""
tabView_port = StringVar(value="")


def is_valid_ip(ip):
    pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    return re.match(pattern, ip) is not None


def is_valid_url(url):
    return "." in url


port_var = StringVar()
ip_var = StringVar()


def update_info():
    global full_url
    input_value = UrlInput.get().strip()
    port = tabView_port.get() if port_input_state.get() == "list" else portInput.get()
    if not input_value or not port:
        info_var.set("\n\n\tPlease enter the required information.")
        play_sound("error")
        return

    if is_valid_ip(input_value) or is_valid_url(input_value):
        full_url = input_value
        try:
            host = ping(full_url, count=1, privileged=False)
            ip = host.address
            ip_var.set(ip)
            port_var.set(port)
            info_var.set(f"\n  Target:\n\tURL:\t {full_url}\n\tIP:\t {ip}\n\tPORT:\t {port}")
        except NameLookupError as e:
            info_var.set(f"\n\n\tError resolving domain or IP: {full_url}\n\t\t{e}")
            play_sound("error")
        except Exception as e:
            info_var.set(f"\n\n\tError: {e}")
            play_sound("error")
    else:
        info_var.set(f"\n\n\tInvalid input: {input_value}")
        play_sound("error")


def toggle_port_input():
    state = port_input_state.get()
    if state == "manual":
        portInput.configure(state=NORMAL)
        toolsTabView.configure(state=DISABLED)
    else:
        portInput.configure(state=DISABLED)
        toolsTabView.configure(state=NORMAL)
        update_port_from_tab_selection()


def update_port_from_tab_selection():
    current_tab = toolsTabView.get()
    if current_tab == "HTTP":
        tabView_port.set("80")
    elif current_tab == "NNTP":
        tabView_port.set("119")
    elif current_tab == "FTP":
        tabView_port.set("20")
    elif current_tab == "SMTP":
        tabView_port.set("25")
    elif current_tab == "POP3":
        tabView_port.set("110")
    elif current_tab == "IMAP4":
        tabView_port.set("143")
    elif current_tab == "Telnet":
        tabView_port.set("23")
    elif current_tab == "Gopher":
        tabView_port.set("70")
    elif current_tab == "TCP":
        tabView_port.set("1")
    else:
        tabView_port.set("")


def show_detailed_info():
    if not full_url:
        play_sound("error")
        show_error("No URL or IP provided.")
        return
    detailed_info = website_info_lookup(full_url)
    play_sound("click")
    display_popup_window("Detailed Information", detailed_info)


def show_geo_info():
    if not full_url:
        play_sound("error")
        show_error("No URL or IP provided.")
        return
    geo_info = print_geo_results(full_url)
    play_sound("click")
    display_popup_window("Geolocation Information", geo_info)


def show_dns_info():
    if not full_url:
        play_sound("error")
        show_error("No URL or IP provided.")
        return
    dns_info = detailed_dns_lookup(full_url)
    play_sound("click")
    display_popup_window("DNS Information", dns_info)


def show_error(message):
    popup_window = CTkToplevel(self)
    popup_window.title("Fehler")
    popup_window.geometry("500x200")
    popup_window.transient()
    popup_window.grab_set()
    popup_window.focus_force()
    error_label = CTkLabel(popup_window, text=message, fg_color="red")
    error_label.pack(padx=40, pady=40)


def display_popup_window(title, content):
    popup_window = CTkToplevel(self)
    popup_window.title(title)
    popup_window.geometry("900x500")
    popup_window.transient()
    popup_window.grab_set()
    popup_window.focus_force()
    textbox = CTkTextbox(popup_window, width=1900, height=1080, text_color="green", fg_color=("#242E29", "#242E29"),
                         corner_radius=0)
    textbox.pack(padx=10, pady=10)
    textbox.delete(1.0, END)
    textbox.insert(1.0, content)


############################## Section 1 ################################

gap1 = CTkLabel(section1, text="", width=100, height=50)
gap1.grid(row=0, column=1, padx=20, pady=(20, 0))

pInfo = CTkLabel(section1, text="Provide Information", text_color="lightgray")
pInfo.grid(row=1, column=2, padx=(0, 300), pady=(0, 20))

##############################

urlLabel = CTkLabel(section1, text="URL or IP", width=150, height=35, text_color="white")
urlLabel.grid(row=2, column=1, padx=(100, 0))
UrlInput = CTkEntry(section1, placeholder_text="Enter website or IP (e.g., example.com or 192.168.1.1)",
                    width=500, height=45, border_width=2, border_color="grey",
                    text_color="gray", corner_radius=0)
UrlInput.grid(row=2, column=2, pady=(20, 0), padx=(50, 0))

##############################

portLabel = CTkLabel(section1, text="PORT", width=150, height=35, text_color="white")
portLabel.grid(row=3, column=1, padx=(100, 0))

##############################

port_input_state = StringVar(value="manual")
manualPortRadio = Radiobutton(section1, text="Manual", variable=port_input_state, value="manual",
                              command=toggle_port_input, fg="#0D47A1", width=8)
manualPortRadio.grid(row=4, column=1, sticky='w', padx=(20, 0), pady=(40, 0))

##############################

listPortRadio = Radiobutton(section1, text="Select Protocol", variable=port_input_state, value="list",
                            command=toggle_port_input, fg="#0D47A1", width=12)
listPortRadio.grid(row=5, column=1, sticky='w', padx=(20, 0), pady=(0, 20))

##############################

portInput = CTkEntry(section1, width=300, placeholder_text="873",
                     textvariable=tabView_port, height=45, border_width=2,
                     border_color="grey", text_color="gray", corner_radius=0)
portInput.grid(row=3, column=2, pady=(20, 0), padx=(0, 150))

toolsTabView = CTkTabview(section1, width=400, height=0, bg_color="green", fg_color="black")
toolsTabView.grid(row=5, column=2, pady=(10, 30))
toolsTabView.add("HTTP")  # Web Pages
toolsTabView.add("NNTP")  # Usenet news
toolsTabView.add("FTP")  # File transfers
toolsTabView.add("SMTP")  # Sending Email
toolsTabView.add("POP3")  # Fetching Email
toolsTabView.add("IMAP4")  # Fetching Email
toolsTabView.add("Telnet")  # Command lines
toolsTabView.add("Gopher")  # Document transfers
toolsTabView.add("TCP")

toggle_port_input()
update_port_from_tab_selection()

##############################

getButton = CTkButton(section1, text="Get Info", text_color="white",
                      height=50, command=update_info)
getButton.grid(row=6, column=3, padx=(0, 40), pady=10)


##############################

def periodic_port_update():
    if port_input_state.get() == "list":
        update_port_from_tab_selection()
    self.after(500, periodic_port_update)


periodic_port_update()

############################## Section 2 ################################
zusammenfassenInformationen = CTkLabel(section2, textvariable=info_var, width=710, height=465,
                                       text_color="white", fg_color=("grey", "grey"),
                                       corner_radius=0, anchor="nw", justify=LEFT)
zusammenfassenInformationen.grid(row=0, column=2)

view_more_button = CTkButton(section4, text="View more", command=show_detailed_info)
view_more_button.grid(row=0, column=0, padx=(10, 10))

geo_button = CTkButton(section4, text="Show Geo Info", command=show_geo_info)
geo_button.grid(row=0, column=1, pady=0, padx=10)

dns_button = CTkButton(section4, text="Show DNS Info", command=show_dns_info)
dns_button.grid(row=0, column=2, pady=10, padx=(10, 10))


############################## Details Frame ################################
def show_confirmation_dialog():
    confirmation_dialog = CTkToplevel(self)
    confirmation_dialog.title("Confirm Exit")
    dialog_width = 300
    dialog_height = 150
    confirmation_dialog.geometry(f"{dialog_width}x{dialog_height}")
    confirmation_dialog.grab_set()
    confirmation_dialog.focus_force()

    label = CTkLabel(confirmation_dialog, text="Do you want to close the application?", wraplength=250)
    label.pack(pady=10)

    def on_yes():
        play_sound("close")
        self.destroy()

    def on_no():
        confirmation_dialog.destroy()

    yes_button = CTkButton(confirmation_dialog, text="Yes", command=on_yes)
    yes_button.pack(side=LEFT, padx=15, pady=10)

    no_button = CTkButton(confirmation_dialog, text="No", command=on_no)
    no_button.pack(side=RIGHT, padx=15, pady=10)

    screen_width = self.winfo_screenwidth()
    screen_height = self.winfo_screenheight()
    x_coordinate = int((screen_width / 2) - (dialog_width / 2))
    y_coordinate = int((screen_height / 2) - (dialog_height / 2))
    confirmation_dialog.geometry("+{}+{}".format(x_coordinate, y_coordinate))


##########################################################################################################
section_tools = CTkFrame(master=section3, width=1000, height=350)
section_tools.grid(row=1, column=0, padx=10, pady=20,
                   sticky='ew ns')  # Chatgpt, ich könnte nicht wißen, wie ich den Width kriege

action_show = CTkFrame(master=section3, width=670, height=350)
action_show.grid(row=1, column=1, pady=20)

gap_label = CTkLabel(section_tools, text="")
gap_label.grid(row=0, column=0, padx=10, pady=10)

toolsTabView = CTkTabview(section_tools, width=200, height=0, bg_color="red", fg_color="black")
toolsTabView.grid(row=1, column=1, pady=(0, 10), padx=(100, 10))
toolsTabView.add("tool1")
toolsTabView.add("tool2")
toolsTabView.add("tool3")
toolsTabView.add("tool4")

toolsTabView._segmented_button.configure(font=('DejaVu Sans Mono', 14))

ip_label = CTkLabel(section_tools, text="IP: ", text_color='white')
ip_label.grid(row=2, column=0, padx=10, pady=10)
ip_out = CTkLabel(section_tools, textvariable=ip_var, text_color='white')
ip_out.grid(row=2, column=1, padx=10, pady=10)

port_label = CTkLabel(section_tools, text="Port: ", text_color='white')
port_label.grid(row=3, column=0, padx=10, pady=10)
port_out = CTkLabel(section_tools, textvariable=port_var, text_color='white')
port_out.grid(row=3, column=1, padx=10, pady=10)

duration_label = CTkEntry(section_tools, width=200, placeholder_text="Duration", height=45, border_width=2,
                          border_color="grey", text_color="gray",
                          corner_radius=0)  # hier muss ich noch ein textvariable= variabel input name
duration_label.grid(row=2, column=2, padx=(70, 10), pady=10)

delay_label = CTkEntry(section_tools, width=200, placeholder_text="Delay", height=45, border_width=2,
                       border_color="grey", text_color="gray",
                       corner_radius=0)  # hier muss ich noch ein textvariable= variabel input name
delay_label.grid(row=3, column=2, padx=(70, 10), pady=10)

check_button = CTkButton(section_tools, text="CHECK", height=50)
check_button.grid(row=2, column=3, padx=(50, 10), pady=10)

action_button = CTkButton(section_tools, text="Action", height=50)
action_button.grid(row=3, column=3, padx=(50, 10), pady=10)


############################################# CHATGPT ####################################################
def ping_ip_continuously(ip, delay=1):
    """
    Function to continuously ping an IP address with a specified delay between pings.
    """
    while True:
        try:
            host = ping(ip, count=1, privileged=False)
            result = f"Pinged {ip}, response time: {host.avg_rtt} ms\n"
            # Update the ping_results widget with the new result
            ping_results.insert(END, result)
            time.sleep(delay)
        except NameLookupError as e:
            result = f"Error resolving domain or IP: {ip}\n\t{e}\n"
            ping_results.insert(END, result)
            break  # Stop pinging if there's an error
        except Exception as e:
            result = f"Error: {e}\n"
            ping_results.insert(END, result)
            break  # Stop pinging if there's an error


def start_pinging():
    """
    Starts the pinging process in a separate thread.
    """
    ip = ip_var.get()  # Assuming ip_var is your StringVar holding the IP address
    if ip:
        # Start the pinging process in a new thread
        ping_thread = threading.Thread(target=ping_ip_continuously, args=(ip,))
        ping_thread.daemon = True  # Ensures the thread will exit when the main program exits
        ping_thread.start()
    else:
        messagebox.showerror("Error", "Please enter a valid IP address.")


def on_close():
    """
    Handles the GUI close event.
    """
    # Show a confirmation dialog before closing
    if messagebox.askokcancel("Confirm Exit", "Do you want to close the application?"):
        # Close the main window without terminating the application
        self.withdraw()
        # Optionally, you can save any necessary state or data here
        # before the application fully closes


# Replace the original self.protocol("WM_DELETE_WINDOW", on_close) with the following:
self.protocol("WM_DELETE_WINDOW", on_close)

ping_results = CTkTextbox(action_show, width=420, height=300, text_color="green", fg_color=("#242E29", "#242E29"),
                          corner_radius=0)
ping_results.pack(padx=10, pady=10)

############################################# CHATGPT ####################################################

ping_button = CTkButton(section_tools, text="PING", height=50, command=start_pinging)
ping_button.grid(row=1, column=3, padx=(50, 10), pady=10)
section_tools.grid_propagate(0)  # Chatgpt, ich könnte nicht wißen, wie ich den Width kriege


#########################################################################################################
def on_close():
    show_confirmation_dialog()


self.protocol("WM_DELETE_WINDOW", on_close)

self.mainloop()
