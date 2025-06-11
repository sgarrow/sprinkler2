import re
import socket
import threading
import sys
from functools import partial

from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.utils import platform
from kivy.clock import Clock
from kivy.app import App

import cfg
#############################################################################

class ClientApp(App):
    def build(self):
        self.root_layout = BoxLayout()  # Temporary root
        self.show_connection_popup()
        return self.root_layout

    def show_connection_popup(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        siz = (600,700) if platform == 'android' else (250,225)
        popup = Popup(title='Choose Connection Type', size_hint=(None, None), size=siz)

        def choose_and_start(connect_type, *args):
            popup.dismiss()
            self.start_client(connect_type)

        height = dp(60) if platform == 'android' else 40
        layout.add_widget(Button(
            text='Connect via LAN', size_hint_y=None, height=height,
            on_press=partial(choose_and_start, 'l')
        ))
        layout.add_widget(Button(
            text='Connect via Internet', size_hint_y=None, height=height,
            on_press=partial(choose_and_start, 'i')
        ))
        layout.add_widget(Button(
            text='Connect via Localhost', size_hint_y=None, height=height,
            on_press=partial(choose_and_start, 's')
        ))

        popup.content = layout
        popup.open()

    def start_client(self, connect_type):
        layout = ClientLayout(connect_type)
        self.root_layout.clear_widgets()
        self.root_layout.add_widget(layout)
#############################################################################

class ClientLayout(BoxLayout):
    def __init__(self, connect_type, **kwargs):
        # This method creates the GUI then connects to server.
        super().__init__(orientation='vertical', **kwargs)

        self.connectType = connect_type
        self.start_connection()
        self.build_ui() #####

    def build_ui(self):
        # Create 2 TextInput widgets.  Both hidden by default.
        height = dp(60) if platform == 'android' else 40

        self.input     = TextInput( hint_text = 'Enter cmd',   multiline = False,
                                    size_hint_y = None, height = height )
        self.set_input = TextInput( hint_text = 'Enter value', multiline = False,
                                    size_hint_y = None, height = height )

        self.input.opacity,  self.set_input.opacity  = 0, 0
        self.input.disabled, self.set_input.disabled = True, True

        # Create 1 send Button widget.
        self.send_button = Button( text = 'Send' )
        self.send_button.bind( on_press=partial( self.send_command, '' ))

        # Create 1 Output scrollview widget (read-only).
        self.output = TextInput(readonly=True, size_hint_y=None)
        self.output.bind(minimum_height=self.output.setter('height'))
        output_scroll = ScrollView(size_hint=(1, 1))
        output_scroll.add_widget(self.output)

        # Create 1 TabbedPanel widget.
        self.tabbed_panel = TabbedPanel(do_default_tab=False)

        # Create 4 tabs with contents.
        # Create GET tab and its content.
        self.get_tab_content = GridLayout(cols=3, spacing=5, size_hint_y=None)
        self.get_tab_content.bind(minimum_height=self.get_tab_content.setter('height'))
        get_scroll = ScrollView(size_hint=(1, 1))
        get_scroll.add_widget(self.get_tab_content)
        self.get_tab = TabbedPanelItem(text='Get')
        self.get_tab.add_widget(get_scroll)

        # Create SET tab and its content.
        self.set_tab_content = GridLayout(cols=3, spacing=5, size_hint_y=None)
        self.set_tab_content.bind(minimum_height=self.set_tab_content.setter('height'))
        set_scroll = ScrollView(size_hint=(1, 1))
        set_scroll.add_widget(self.set_tab_content)
        self.set_tab = TabbedPanelItem(text='Set')
        self.set_tab.add_widget(set_scroll)

        # Create OTHER tab and its content.
        self.oth_tab_content = GridLayout(cols=3, spacing=5, size_hint_y=None)
        self.oth_tab_content.bind(minimum_height=self.oth_tab_content.setter('height'))
        oth_scroll = ScrollView(size_hint=(1, 1))
        oth_scroll.add_widget(self.oth_tab_content)
        self.oth_tab = TabbedPanelItem(text='Other')
        self.oth_tab.add_widget(oth_scroll)

        # Create DEBUG tab and its content.
        self.debug_tab_content = GridLayout(cols=3, spacing=5, size_hint_y=None)
        self.debug_tab_content.add_widget(Label(text='Type command above and hit Send')) # orig
        self.debug_tab_content.add_widget( self.send_button )
        self.debug_tab_content.bind(minimum_height=self.debug_tab_content.setter('height'))
        debug_scroll = ScrollView(size_hint=(1, 1))
        debug_scroll.add_widget(self.debug_tab_content)
        self.debug_tab = TabbedPanelItem(text='Debug') # orig
        self.debug_tab.add_widget(debug_scroll)

        # Add the 4 tabs to the panel.
        self.tabbed_panel.add_widget( self.get_tab )
        self.tabbed_panel.add_widget( self.set_tab )
        self.tabbed_panel.add_widget( self.oth_tab )
        self.tabbed_panel.add_widget( self.debug_tab )

        # Now that tabbed panel is fully constructed.
        self.tabbed_panel.bind( current_tab = self.on_tab_switch )

        # Add 4 widgets to final layout structure.
        self.add_widget( self.input )
        self.add_widget( self.set_input )
        self.add_widget( self.tabbed_panel )
        self.add_widget( output_scroll )
    ###################

    def _on_connection_chosen(self, choice, popup, *args):
        self.connectType = choice
        popup.dismiss()
        self.start_connection()
    ###################

    def start_connection(self):
        # Make/ Get Config and Connection Info (IP, PORT, ... from text file
        # ckl.cfg).  Note that server also has access to the cfgDict.
        #arguments  = sys.argv
        #scriptName = arguments[0]
        #userArgs   = arguments[1:]
        #uut        = userArgs[0] 
        #cfgDict    = cfg.getCfgDict(uut)
        cfgDict    = cfg.getCfgDict('spr')

        if cfgDict is None:
            print('  Client could not connect to server.')
            print('  Missing or (malformed) cfg file or missing cmd line arg')
            print('  usage1: python client.py uut (uut = spr or clk).')
            print('  usage2: python    gui.py uut (uut = spr or clk).')
            sys.exit()

        # Populate a connection dictionary based on cfgDict contents.
        connectDict = {
            's': 'localhost',
            'l': cfgDict['myLan'],
            'i': cfgDict['myIP']
        }

        ip   = connectDict[self.connectType]
        port = int(cfgDict['myPort'])
        pwd  = cfgDict['myPwd']

        self.conn = ClientConnection(ip, port, pwd, self.update_output)
    ###################

    def update_output(self, text):
        # This method wraps UI updates from a background thread using Clock
        # because Kivy requires all UI updates to happen on the main thread.
        Clock.schedule_once(lambda dt: self._update_output_ui_safe(text))
    ###################

    def _update_output_ui_safe(self, text):
        # This method does the heavy lifting in displaying responses.
        # If the response is to the "m" command then this method also
        # populates buttons.  Furthermore is the response to to either the
        # "close" or "ks" command then this method disables the GUI.
        self.output.text += f'\n{text}'

        if 'COMMANDS' in text:
            menu_lines = text.splitlines()
            for line in menu_lines:
                match = re.match(r'\s*(\w+)\s*-\s*(.+)', line)
                if match:
                    cmd, desc = match.groups()
                    self.add_command_button(cmd, desc)

        if 'Server killed' in text or 'Disconnected' in text:
            self.input.disabled = True
            self.send_button.disabled = True
            for tab_content in [self.get_tab_content, self.set_tab_content, self.oth_tab_content]:
                for child in tab_content.children:
                    child.disabled = True
    ###############

    def add_command_button(self, cmd, label):
        # This method does the heavy lifting in adding buttons when a
        # response to the 'm' command is recieved.
        height = dp(60) if platform == 'android' else 40
        btn = Button(text=label, size_hint_y=None, height=height)
        btn.bind(on_press=partial(self.send_command, cmd))

        if 'Get' in label:
            self.get_tab_content.add_widget(btn)
        elif 'Set' in label:
            self.set_tab_content.add_widget(btn)
        else:
            self.oth_tab_content.add_widget(btn)
    ###################

    def on_tab_switch(self, instance, tab):
        # This method takes care of hiding one or both of the input
        # widgets depending upon which tab is active.
        if tab.text == 'Debug':
            self.input.opacity = 1
            self.input.disabled = False
            self.set_input.opacity = 0
            self.set_input.disabled = True
        elif tab.text in ['Set', 'Other']:
            self.input.opacity = 0
            self.input.disabled = True
            self.set_input.opacity = 1
            self.set_input.disabled = False
        else:  # 'Get' or unknown
            self.input.opacity = 0
            self.input.disabled = True
            self.set_input.opacity = 0
            self.set_input.disabled = True
    ###################

    def send_command(self, inText, instance):
        # This method constructs the command string to be sent to the server.
        # The srting is built from inText parm (button cmd) + any text from
        # an input widget (if not a Get).
        cmd = ''
        if instance.text == 'Send':
            if self.tabbed_panel.current_tab.text == 'Debug':
                cmd = self.input.text.strip()
            else:
                cmd = self.set_input.text.strip()
        else:
            # Button-based command
            cmd = inText.strip()
            if self.tabbed_panel.current_tab.text in ['Set', 'Other']:
                param = self.set_input.text.strip()
                if param:
                    cmd += f' {param}'
        if not cmd:
            return
        self.conn.send_command(cmd)
        self.input.text = ''
        self.set_input.text = ''
#############################################################################
class ClientConnection:
    def __init__(self, ip, port, pwd, on_receive_callback):
        self.ip = ip
        self.port = port
        self.pwd = pwd
        self.socket = None
        self.connected = False
        self.on_receive = on_receive_callback

        # Run connection in background
        threading.Thread(target=self.connect, daemon=True).start()
    ###################

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.ip, self.port))
            self.socket.send(self.pwd.encode())
            self.connected = True

            response = self.socket.recv(1024).decode()
            self.on_receive(response)
            self.send_command('m') # For auto-populating tabbed panel buttons.
        except Exception as e:
            self.on_receive(f'Connection error: {e}')
            self.connected = False
    ###################

    def send_command(self, cmd):
        if not self.connected:
            self.on_receive('Not connected.')
            return

        try:
            self.socket.send(cmd.encode())
            self.socket.settimeout(1.0)
            response = ''
            while True:
                try:
                    chunk = self.socket.recv(1024).decode()
                    if not chunk:
                        break
                    response += chunk
                    if 'RE: ks' in response:
                        self.socket.close()
                        self.connected = False
                        self.on_receive('Server killed. Disconnected.')
                        break
                except socket.timeout:
                    break

            self.on_receive(response)

            if cmd.lower() == 'close':
                self.socket.close()
                self.connected = False
                self.on_receive('Disconnected.')
        except Exception as e:
            self.on_receive(f'Send error: {e}')
            self.connected = False
#############################################################################

if __name__ == '__main__':
    ClientApp().run()
#############################################################################
