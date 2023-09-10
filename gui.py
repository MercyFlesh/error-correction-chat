import threading
import config
from backend import Backend
from hamming import Hamming
from rs import RS
from ldpc import LDPC
from conv_code import Convolutional
from cipher_factory import CipherFactory
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

class GUI:
    def __init__(self):
        self.backend = Backend()
        self.__init_interface()

        self.receiving_thread = threading.Thread(target=self.backend.run_receiving, args=(self,))
        self.receiving_thread.start()

        self._load_history()

    def __init_interface(self):
        self.root = ctk.CTk()
        
        self.root.geometry("800x600")
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure((1, 2, 3, 4, 5, 6, 7, 8, 9), weight=1)
        self.root.grid_columnconfigure((0), weight=0)
        self.root.grid_columnconfigure((1, 2, 3), weight=1)
        
        self.root.title('UDP Hamming chat')

        my_ip_address_label = ctk.CTkLabel(
            self.root, text=f'Мой хост:'
            ).grid(row=0, column=0, columnspan=1, padx=(20, 5), pady=(20, 5), sticky="se")
        
        my_ip_address = ctk.CTkLabel(self.root, text=self.backend.host
            ).grid(row=0, column=1, columnspan=1, padx=(10, 20), pady=(20, 5), sticky="sw")
        
        ip_address_label = ctk.CTkLabel(
            self.root, text='Хост получателя:'
            ).grid(row=1, column=0, columnspan=1, padx=(20, 5), pady=(5, 10), sticky="e")
        
        self.ip_address = ctk.CTkEntry(self.root, placeholder_text="192.168.0.1")
        self.ip_address.grid(row=1, column=1, columnspan=1, padx=(5, 10), pady=(5, 10), sticky="wew")
        self.ip_address.bind('<KeyRelease>', self._enter_host2)

        self.txt = ctk.CTkTextbox(self.root, state="disabled")
        self.txt.grid(row=2, column=1, columnspan=2, rowspan=4, padx=(5, 0), pady=(20, 10), sticky="nsew")

        ctk.CTkLabel(self.root, text="Сообщение:").grid(row=6, column=0, columnspan=1, padx=(20, 5), pady=(10, 5), sticky="e")
        self.text_message = ctk.CTkEntry(self.root, placeholder_text="aboba")
        self.text_message.grid(row=6, column=1, columnspan=1, padx=(5, 10), pady=(10, 5), sticky="wew")
        
        mistake_label = ctk.CTkLabel(self.root, text='Ошибка:', width=10).grid(row=7, column=0, columnspan=1, padx=(20, 5), pady=(5, 5), sticky="e")
        self.mistake = ctk.CTkEntry(self.root)
        self.mistake.grid(row=7, column=1, columnspan=1, padx=(5, 10), pady=(5, 5), sticky="wew")
        self.mistake.insert(0, '0')

        hamming_message_label = ctk.CTkLabel(self.root, text='Код:', width=15).grid(row=8, column=0, columnspan=1, padx=(20, 5), pady=(5, 5), sticky="e")
        self.encode_message = ctk.CTkTextbox(self.root, height=1, state="disabled")
        self.encode_message.grid(row=8, column=1, columnspan=1, rowspan=1, padx=(5, 10), pady=(5, 5), sticky="nsew")
        
        self.text_message.bind('<KeyRelease>', self._encode)
        self.mistake.bind('<KeyRelease>', self._encode)

        self.selected_algorithm = ctk.StringVar(self.root)
        self.selected_algorithm.set(config.ALGORITHMS[0])

        self.algorithm_mode_menu = ctk.CTkOptionMenu(self.root, variable=self.selected_algorithm, values=config.ALGORITHMS, command=self._change_algorithm_mode)
        self.algorithm_mode_menu.grid(row=6, column=2, columnspan=1, rowspan=1, padx=(5, 10), pady=(5, 5), sticky="wew")

        self.send = ctk.CTkButton(self.root, text="Отправить", command=lambda: self._send())
        self.send.grid(row=7, column=2, columnspan=1, rowspan=1, padx=(5, 10), pady=(5, 5), sticky="wew")
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _enter_host2(self, event):
        self.backend.host2 = self.ip_address.get()

    def insert_message(self, message):
        message = f'''[{message['time'][:-7]}] {message["sender"]}:\n
    Сообщение: {message['text']}
    {message['algorithm']}: {message['code_message']}
 {'-' * 128}\n'''
        
        self.txt.configure(state="normal")
        self.txt.insert(ctk.END, message)
        self.txt.yview_moveto(1)
        self.txt.configure(state="disabled")

    def _send(self):
        text_message = self.text_message.get()
        if not text_message:
            return
        encode_message = self.encode_message.get(1.0, 'end-1c')
        ret = self.backend.send(text_message, encode_message, self.selected_algorithm.get())
        if ret == 1:
            CTkMessagebox(title="Error", message='Введите хост!', icon=None)
            return
        elif ret == 2:
            CTkMessagebox(title="Error", message='Неверный хост!', icon=None)
            return
        
        self._clear_message_data()
        self.insert_message(self.backend.history_dict['messages'][-1])

    def _clear_message_data(self):
        self.text_message.delete("0", ctk.END)
        self.encode_message.configure(state="normal")
        self.encode_message.delete(0.0, 'end')
        self.encode_message.configure(state="disabled")
        self.mistake.delete("0", ctk.END)
        self.mistake.insert(0, '0')

    def _load_history(self):
        for message in self.backend.history_dict['messages']:
            self.insert_message(message)

    def _on_closing(self):
        self.root.destroy()

    def _encode(self, event):
        text = self.text_message.get().strip()
        mistake = self.mistake.get().strip()
        selected_alg = self.selected_algorithm.get()
        if not text:
            self.encode_message.configure(state="normal")
            self.encode_message.delete(0.0, 'end')
            self.encode_message.configure(state="disabled")
            return
        
        mistake = '0' if mistake == '' else mistake

        encode_message = ""
        if selected_alg == config.ALGORITHMS[0]:
            encode_message = CipherFactory.encode(Hamming, text, mistake)
        elif selected_alg == config.ALGORITHMS[1]:
            encode_message = CipherFactory.encode(LDPC, text, mistake)
        elif selected_alg == config.ALGORITHMS[2]:
            encode_message = CipherFactory.encode(RS, text, mistake)
        elif selected_alg == config.ALGORITHMS[3]:
            encode_message = CipherFactory.encode(Convolutional, text, mistake)

        self.encode_message.configure(state="normal")
        self.encode_message.delete(0.0, 'end')
        self.encode_message.insert(ctk.END, encode_message)
        self.encode_message.configure(state="disabled")

    def _min_divider(self, n):
        for i in range(3, n + 1):
            if n % i == 0:
                return i

    def _change_algorithm_mode(self, new_algorithm_mode: str):
        self._encode(None)


if __name__ == '__main__':
    gui = GUI()
    gui.root.mainloop()
