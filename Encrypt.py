import base64
import os
import tkinter as tk
from tkinter import messagebox

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# --- Cryptographic Config ---
ITERATIONS = 600_000  # OWASP recommended standard for PBKDF2-HMAC-SHA256
SALT_SIZE = 16        # 128-bit random salt per message


def derive_key(passphrase: str, salt: bytes) -> bytes:
    """Derives a 32-byte Fernet key from a passphrase and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode('utf-8')))


def encrypt_payload(plaintext: str, passphrase: str) -> str:
    """Encrypts text into a self-contained Base64 string containing salt + ciphertext."""
    salt = os.urandom(SALT_SIZE)
    key = derive_key(passphrase, salt)
    f = Fernet(key)
    encrypted_data = f.encrypt(plaintext.encode('utf-8'))
    
    # Pack salt + ciphertext together
    payload = salt + encrypted_data
    return base64.b64encode(payload).decode('utf-8')


def decrypt_payload(payload_b64: str, passphrase: str) -> str:
    """Unpacks and decrypts a Base64 string payload."""
    raw_payload = base64.b64decode(payload_b64.strip().encode('utf-8'))
    if len(raw_payload) <= SALT_SIZE:
        raise ValueError("Invalid payload length.")
    
    salt = raw_payload[:SALT_SIZE]
    encrypted_data = raw_payload[SALT_SIZE:]
    
    key = derive_key(passphrase, salt)
    f = Fernet(key)
    return f.decrypt(encrypted_data).decode('utf-8')


# --- Mobile & Desktop GUI ---
class VaultPadApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VaultPad Encryptor")
        self.geometry("450x680")
        self.configure(bg="#1e1e2e")

        FONT_LABEL = ("Helvetica", 11, "bold")
        FONT_BTN = ("Helvetica", 11, "bold")
        
        # Header
        tk.Label(
            self, text="🔒 VaultPad", font=("Helvetica", 18, "bold"),
            bg="#1e1e2e", fg="#cdd6f4", pady=10
        ).pack()

        # Passphrase Frame
        pass_frame = tk.Frame(self, bg="#1e1e2e")
        pass_frame.pack(fill="x", padx=15, pady=5)
        
        tk.Label(pass_frame, text="Master Password:", font=FONT_LABEL, bg="#1e1e2e", fg="#a6adc8").pack(anchor="w")
        
        self.pass_entry = tk.Entry(pass_frame, show="*", font=("Helvetica", 14), bg="#313244", fg="#cdd6f4", insertbackground="white")
        self.pass_entry.pack(fill="x", pady=2)
        
        self.show_pass_var = tk.BooleanVar()
        tk.Checkbutton(
            pass_frame, text="Show Password", variable=self.show_pass_var,
            command=self.toggle_password, bg="#1e1e2e", fg="#a6adc8", selectcolor="#313244", activebackground="#1e1e2e"
        ).pack(anchor="w")

        # Input Section
        input_frame = tk.Frame(self, bg="#1e1e2e")
        input_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        lbl_bar = tk.Frame(input_frame, bg="#1e1e2e")
        lbl_bar.pack(fill="x")
        tk.Label(lbl_bar, text="Input Text or Ciphertext:", font=FONT_LABEL, bg="#1e1e2e", fg="#a6adc8").pack(side="left")
        
        # Paste Button
        tk.Button(
            lbl_bar, text="📋 Paste", command=self.paste_input,
            bg="#45475a", fg="#cdd6f4", font=("Helvetica", 9, "bold"), relief="flat", padx=8
        ).pack(side="right")

        self.input_text = tk.Text(input_frame, height=6, font=("Courier", 11), bg="#313244", fg="#cdd6f4", insertbackground="white", wrap="word")
        self.input_text.pack(fill="both", expand=True, pady=4)

        # Action Buttons (Encrypt / Decrypt)
        btn_frame = tk.Frame(self, bg="#1e1e2e")
        btn_frame.pack(fill="x", padx=15, pady=8)

        tk.Button(
            btn_frame, text="🔒 ENCRYPT", command=self.do_encrypt,
            bg="#a6e3a1", fg="#11111b", font=FONT_BTN, relief="flat", pady=8, width=15
        ).pack(side="left", expand=True, fill="x", padx=(0, 5))

        tk.Button(
            btn_frame, text="🔓 DECRYPT", command=self.do_decrypt,
            bg="#89b4fa", fg="#11111b", font=FONT_BTN, relief="flat", pady=8, width=15
        ).pack(side="right", expand=True, fill="x", padx=(5, 0))

        # Output Section
        output_frame = tk.Frame(self, bg="#1e1e2e")
        output_frame.pack(fill="both", expand=True, padx=15, pady=5)

        out_bar = tk.Frame(output_frame, bg="#1e1e2e")
        out_bar.pack(fill="x")
        tk.Label(out_bar, text="Result:", font=FONT_LABEL, bg="#1e1e2e", fg="#a6adc8").pack(side="left")

        tk.Button(
            out_bar, text="✂️ Copy Output", command=self.copy_output,
            bg="#f9e2af", fg="#11111b", font=("Helvetica", 9, "bold"), relief="flat", padx=8
        ).pack(side="right")

        self.output_text = tk.Text(output_frame, height=6, font=("Courier", 11), bg="#181825", fg="#a6e3a1", insertbackground="white", wrap="word")
        self.output_text.pack(fill="both", expand=True, pady=4)

    def toggle_password(self):
        self.pass_entry.config(show="" if self.show_pass_var.get() else "*")

    def paste_input(self):
        try:
            pasted = self.clipboard_get()
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert(tk.END, pasted)
        except Exception:
            messagebox.showwarning("Clipboard Empty", "Nothing found in clipboard.")

    def copy_output(self):
        text = self.output_text.get("1.0", tk.END).strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.update()  # Required on mobile to update system clipboard
            messagebox.showinfo("Success", "Copied to clipboard!")
        else:
            messagebox.showwarning("Empty", "Nothing to copy.")

    def do_encrypt(self):
        pwd = self.pass_entry.get()
        data = self.input_text.get("1.0", tk.END).strip()
        
        if not pwd or not data:
            messagebox.showerror("Error", "Please provide both a password and text to encrypt.")
            return
        
        try:
            cipher_b64 = encrypt_payload(data, pwd)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, cipher_b64)
        except Exception as e:
            messagebox.showerror("Encryption Error", str(e))

    def do_decrypt(self):
        pwd = self.pass_entry.get()
        payload = self.input_text.get("1.0", tk.END).strip()
        
        if not pwd or not payload:
            messagebox.showerror("Error", "Please provide both a password and ciphertext to decrypt.")
            return
        
        try:
            plain_text = decrypt_payload(payload, pwd)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, plain_text)
        except InvalidToken:
            messagebox.showerror("Decryption Failed", "Incorrect password or corrupted data.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse payload: {e}")


if __name__ == "__main__":
    app = VaultPadApp()
    app.mainloop()