import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import base64

class SaveFileEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pokeclicker save Editor")
        self.root.configure(bg="#add8e6")

        self.json_data = None
        self.file_path = None

        self.load_button = tk.Button(root, text="Load Save File", command=self.load_base64_json)
        self.load_button.pack(pady=10)

        self.save_button = tk.Button(root, text="Save Save File", command=self.save_base64_json)
        self.save_button.pack(pady=10)

        self.tree = ttk.Treeview(root, columns=("value",), show="tree headings")
        self.tree.heading("#1", text="Value")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_double_click)

    def load_base64_json(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not file_path:
            return
        
        try:
            with open(file_path, "r") as file:
                encoded_content = file.read().strip()
                decoded_bytes = base64.b64decode(encoded_content)
                decoded_text = self.decode_bytes(decoded_bytes)
                self.json_data = json.loads(decoded_text)
                self.file_path = file_path
                self.tree.delete(*self.tree.get_children())
                self.populate_tree("", self.json_data)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while loading: {str(e)}")

    def decode_bytes(self, bytes_data):
        try:
            return bytes_data.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return bytes_data.decode("latin-1")  # Try decoding with latin-1 (ISO-8859-1)
            except UnicodeDecodeError:
                return str(bytes_data)  # If all else fails, return as string representation

    def save_base64_json(self):
        if self.json_data is None:
            messagebox.showwarning("Warning", "No JSON data loaded.")
            return
        
        try:
            encoded_content = base64.b64encode(json.dumps(self.json_data).encode("utf-8")).decode("utf-8")
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            if not file_path:
                return
            
            with open(file_path, "w") as file:
                file.write(encoded_content)
            
            messagebox.showinfo("Success", "Base64 JSON file saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving: {str(e)}")

    def populate_tree(self, parent, data):
        if isinstance(data, dict):
            for key, value in data.items():
                node = self.tree.insert(parent, "end", text=key, values=(str(value),))
                if isinstance(value, (dict, list)):
                    self.populate_tree(node, value)
        elif isinstance(data, list):
            for index, value in enumerate(data):
                node = self.tree.insert(parent, "end", text=f"[{index}]", values=(str(value),))
                if isinstance(value, (dict, list)):
                    self.populate_tree(node, value)
        else:
            self.tree.insert(parent, "end", values=(str(data),))

    def on_double_click(self, event):
        item = self.tree.selection()[0]
        column = self.tree.identify_column(event.x)
        if column == "#1":  # Only allow editing the value column
            value = self.tree.item(item, "values")[0]
            self.edit_value(item, value)

    def edit_value(self, item, value):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Value")
        
        entry = tk.Entry(edit_window)
        entry.pack(fill="x", expand=True)
        entry.insert(0, value)
        
        def save_edit():
            new_value = entry.get()
            self.tree.set(item, column="#1", value=new_value)
            self.update_json_from_tree()
            edit_window.destroy()
        
        save_button = tk.Button(edit_window, text="Save", command=save_edit)
        save_button.pack(pady=10)
        
        entry.focus_set()  # Set focus to entry for immediate editing
    
    def update_json_from_tree(self):
        def recurse_tree(item):
            children = self.tree.get_children(item)
            if not children:
                value = self.tree.item(item, "values")[0]
                if value.isdigit():
                    return int(value)
                try:
                    return float(value)
                except ValueError:
                    if value.lower() == "true":
                        return True
                    elif value.lower() == "false":
                        return False
                    return value
            elif self.tree.item(item, "text").startswith("["):
                return [recurse_tree(child) for child in children]
            else:
                return {self.tree.item(child, "text"): recurse_tree(child) for child in children}

        self.json_data = recurse_tree("")

if __name__ == "__main__":
    root = tk.Tk()
    app = SaveFileEditorApp(root)
    root.mainloop()
