import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from rsa_manager import RSAKeyManager
from envelope import Envelope
from utils import Utils
from cryptography.hazmat.primitives.asymmetric import padding
import os

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Envelope Digital com Criptografia RSA + AES")
        self.root.geometry("800x500")
        self.root.resizable(False, False)

        self.files_created = []  # lista para armazenar arquivos criados
        self.storage_dir = os.path.join(os.getcwd(), "teste")  # pasta onde os arquivos serão salvos

        # Criar a pasta 'teste' se não existir
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.root, text="Envelope Digital", font=("Helvetica", 16)).pack(pady=10)

        self.option_menu = tk.LabelFrame(self.root, text="⚙️ Opções", padx=10, pady=10)
        self.option_menu.pack(padx=10, pady=10, fill="both", expand=True)

        # Botões
        self.create_rsa_btn = tk.Button(self.option_menu, text="🔑 Gerar Chaves RSA", width=25, command=self.generate_rsa_keys)
        self.create_rsa_btn.grid(row=0, column=0, pady=5)

        self.create_envelope_btn = tk.Button(self.option_menu, text="📦 Criar Envelope Digital", width=25, command=self.create_envelope)
        self.create_envelope_btn.grid(row=1, column=0, pady=5)

        self.open_envelope_btn = tk.Button(self.option_menu, text="📬  Abrir Envelope Digital", width=25, command=self.open_envelope)
        self.open_envelope_btn.grid(row=2, column=0, pady=5)

        self.decrypt_key_btn = tk.Button(self.option_menu, text="🔓 Descriptografar Chave AES", width=25, command=self.decrypt_aes_key)
        self.decrypt_key_btn.grid(row=3, column=0, pady=5)

        self.view_btn = tk.Button(self.option_menu, text="👁️ Visualizar Arquivos Criados", width=25, command=self.view_created_files)
        self.view_btn.grid(row=4, column=0, pady=5)

        # Entradas e opções
        tk.Label(self.option_menu, text="Tamanho RSA:").grid(row=0, column=1, padx=10)
        self.key_size_var = tk.StringVar(value="2048")
        self.key_size_menu = ttk.Combobox(self.option_menu, textvariable=self.key_size_var, values=["1024", "2048"], width=10)
        self.key_size_menu.grid(row=0, column=2)

        tk.Label(self.option_menu, text="AES Size:").grid(row=1, column=1, padx=10)
        self.aes_size_var = tk.StringVar(value="128")
        self.aes_size_menu = ttk.Combobox(self.option_menu, textvariable=self.aes_size_var, values=["128", "192", "256"], width=10)
        self.aes_size_menu.grid(row=1, column=2)

        tk.Label(self.option_menu, text="Modo AES:").grid(row=2, column=1, padx=10)
        self.mode_var = tk.StringVar(value="ecb")
        self.mode_menu = ttk.Combobox(self.option_menu, textvariable=self.mode_var, values=["ecb", "cbc"], width=10)
        self.mode_menu.grid(row=2, column=2)

        tk.Label(self.option_menu, text="Formato:").grid(row=3, column=1, padx=10)
        self.format_var = tk.StringVar(value="base64")
        self.format_menu = ttk.Combobox(self.option_menu, textvariable=self.format_var, values=["base64", "hexadecimal"], width=10)
        self.format_menu.grid(row=3, column=2)

        # Área de entrada da mensagem
        tk.Label(self.root, text="Mensagem para Criptografar:").pack()
        self.msg_entry = ScrolledText(self.root, width=80, height=5)
        self.msg_entry.pack(padx=10, pady=5)

    def generate_rsa_keys(self):
        pub_file = filedialog.asksaveasfilename(defaultextension=".pem", filetypes=[("PEM files", "*.pem")], title="Salvar Chave Pública", initialdir=self.storage_dir)
        priv_file = filedialog.asksaveasfilename(defaultextension=".pem", filetypes=[("PEM files", "*.pem")], title="Salvar Chave Privada", initialdir=self.storage_dir)
        if pub_file and priv_file:
            size = int(self.key_size_var.get())
            RSAKeyManager.generate_keys(size, pub_file, priv_file)
            self.files_created.extend([pub_file, priv_file])
            messagebox.showinfo("Sucesso", "Chaves RSA geradas com sucesso!")

    def create_envelope(self):
        msg = self.msg_entry.get("1.0", tk.END).strip()
        if not msg:
            messagebox.showwarning("Aviso", "Digite uma mensagem para criptografar.")
            return

        pub_key_file = filedialog.askopenfilename(filetypes=[("PEM files", "*.pem")], title="Escolher Chave Pública", initialdir=self.storage_dir)
        if not pub_key_file:
            return

        aes_size = int(self.aes_size_var.get())
        aes_mode = self.mode_var.get().lower()
        fmt = self.format_var.get().lower()

        key_file = filedialog.asksaveasfilename(defaultextension=".txt", title="Salvar Chave Criptografada", initialdir=self.storage_dir)
        msg_file = filedialog.asksaveasfilename(defaultextension=".txt", title="Salvar Mensagem Criptografada", initialdir=self.storage_dir)
        iv_file = None
        if aes_mode == "cbc":
            iv_file = filedialog.asksaveasfilename(defaultextension=".txt", title="Salvar IV", initialdir=self.storage_dir)

        Envelope.create(msg, pub_key_file, aes_size, aes_mode, fmt, key_file, msg_file, iv_file)
        self.files_created.extend([key_file, msg_file])
        if iv_file:
            self.files_created.append(iv_file)

        messagebox.showinfo("Sucesso", "Envelope criado com sucesso!")

    def open_envelope(self):
        msg_file = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")], title="Escolher Mensagem Criptografada", initialdir=self.storage_dir)
        key_file = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")], title="Escolher Chave Criptografada", initialdir=self.storage_dir)
        priv_key_file = filedialog.askopenfilename(filetypes=[("PEM files", "*.pem")], title="Escolher Chave Privada", initialdir=self.storage_dir)

        aes_mode = self.mode_var.get().lower()
        fmt = self.format_var.get().lower()
        iv_file = None
        if aes_mode == "cbc":
            iv_file = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")], title="Escolher IV", initialdir=self.storage_dir)

        out_file = filedialog.asksaveasfilename(defaultextension=".txt", title="Salvar Mensagem Decifrada", initialdir=self.storage_dir)
        Envelope.open(msg_file, key_file, priv_key_file, aes_mode, fmt, out_file, iv_file)
        self.files_created.append(out_file)

        messagebox.showinfo("Sucesso", f"Envelope aberto com sucesso! Mensagem salva.")

    def decrypt_aes_key(self):
        key_file = filedialog.askopenfilename(title="Escolher Chave AES Criptografada", initialdir=self.storage_dir)
        priv_key_file = filedialog.askopenfilename(title="Escolher Chave Privada", initialdir=self.storage_dir)
        fmt = self.format_var.get().lower()

        encrypted_key = Utils.decode(open(key_file).read(), fmt)
        private_key = RSAKeyManager.load_private_key(priv_key_file)
        aes_key = private_key.decrypt(encrypted_key, padding.PKCS1v15())

        # Salvar a chave AES em um arquivo dentro da pasta 'teste'
        aes_key_file = os.path.join(self.storage_dir, "aes_key_decifrada.txt")
        with open(aes_key_file, "w") as f:
            f.write(aes_key.hex())

        self.files_created.append(aes_key_file)  # Adiciona o arquivo da chave AES à lista de arquivos criados

        messagebox.showinfo("Sucesso", f"Chave AES descriptografada e salva como 'aes_key_decifrada.txt'.")

    def view_created_files(self):
        files = [f for f in os.listdir(self.storage_dir) if f.endswith(".txt") or f.endswith(".pem")]

        if not files:
            messagebox.showinfo("Nenhum Arquivo", "Nenhum arquivo .txt ou .pem encontrado na pasta de armazenamento.")
            return

        win = tk.Toplevel(self.root)
        win.title("📂 Arquivos Criados")
        win.geometry("600x500")

        # Cria o canvas e a barra de rolagem
        canvas = tk.Canvas(win)
        scroll_y = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll_y.set)
        
        # Cria o frame que irá conter os arquivos
        files_frame = tk.Frame(canvas)

        # Coloca o frame dentro do canvas
        canvas.create_window((0, 0), window=files_frame, anchor="nw")
        canvas.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        # Adiciona os arquivos e seus conteúdos no frame
        for file in files:
            file_path = os.path.join(self.storage_dir, file)

            try:
                with open(file_path, "r") as f:
                    content = f.read()
            except Exception as e:
                content = f"[Erro ao ler o arquivo]: {e}"

            tk.Label(files_frame, text=f"📄 Arquivo: {file}", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))

            text_box = ScrolledText(files_frame, width=70, height=6)
            text_box.insert(tk.END, content)
            text_box.configure(state="disabled")
            text_box.pack(padx=10, pady=5)

        # Atualiza a área de rolagem
        files_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

# Iniciar o app
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
