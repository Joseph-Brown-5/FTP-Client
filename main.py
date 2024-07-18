# Author: Joseph Brown
# Date: 6/25/2024

import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from ftplib import FTP, error_perm
import os
import tempfile


class FTPClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FTP Client")

        # Initialize FTP object
        self.ftp = None

        # Initialize local directory path
        self.local_directory_path = tk.StringVar()
        self.local_directory_path.set(os.getcwd())  # Initialize with current working directory

        # Login Frame
        self.login_frame = tk.Frame(root, padx=10, pady=10)
        self.login_frame.grid(row=0, column=0, sticky=tk.W)

        self.host_label = tk.Label(self.login_frame, text="Host:")
        self.host_label.grid(row=0, column=0, sticky=tk.E)
        self.host_entry = tk.Entry(self.login_frame, width=30)
        self.host_entry.grid(row=0, column=1)

        self.user_label = tk.Label(self.login_frame, text="Username:")
        self.user_label.grid(row=1, column=0, sticky=tk.E)
        self.user_entry = tk.Entry(self.login_frame, width=30)
        self.user_entry.grid(row=1, column=1)

        self.pass_label = tk.Label(self.login_frame, text="Password:")
        self.pass_label.grid(row=2, column=0, sticky=tk.E)
        self.pass_entry = tk.Entry(self.login_frame, show="*", width=30)
        self.pass_entry.grid(row=2, column=1)

        self.connect_button = tk.Button(self.login_frame, text="Connect", command=self.connect_ftp)
        self.connect_button.grid(row=3, column=1, sticky=tk.E)

        self.status_label = tk.Label(root, text="")
        self.status_label.grid(row=1, column=0, sticky=tk.W)

    def connect_ftp(self):
        host = self.host_entry.get()
        user = self.user_entry.get()
        password = self.pass_entry.get()

        try:
            self.ftp = FTP(host)
            self.ftp.login(user=user, passwd=password)
            messagebox.showinfo("Success", "Connected to FTP server successfully!")

            # Disable login elements after successful connection
            self.host_entry.config(state='disabled')
            self.user_entry.config(state='disabled')
            self.pass_entry.config(state='disabled')
            self.connect_button.config(state='disabled')

            # Open file operations window
            self.open_file_operations_window()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {str(e)}")

    def open_file_operations_window(self):
        # Creates a window for file op
        file_operations_window = tk.Toplevel(self.root)
        file_operations_window.title("File Operations")
        file_operations_window.config(bg='#dddddd')

        # Lists the local dr
        local_directory_frame = tk.Frame(file_operations_window, padx=10, pady=10)
        local_directory_frame.pack(anchor=tk.W, padx=10, pady=10)

        local_directory_label = tk.Label(local_directory_frame, text="Local Directory:")
        local_directory_label.grid(row=0, column=0, sticky=tk.W)

        local_directory_entry = tk.Entry(local_directory_frame, textvariable=self.local_directory_path, width=50)
        local_directory_entry.grid(row=0, column=1, sticky=tk.W)

        browse_button = tk.Button(local_directory_frame, text="Browse", command=self.browse_local_directory)
        browse_button.grid(row=0, column=2, sticky=tk.W)

        # Frame for FTP server files
        left_frame = tk.Frame(file_operations_window)
        left_frame.pack(side=tk.LEFT, padx=10, pady=10, anchor=tk.N)

        # Label for FTP server files
        ftp_file_list_label = tk.Label(left_frame, text="Files on FTP Server:")
        ftp_file_list_label.pack(pady=10)

        # Listbox to display FTP server files
        self.ftp_files_listbox = tk.Listbox(left_frame, width=50, height=10)
        self.ftp_files_listbox.pack(padx=10, pady=10)

        # Double click to open file
        self.ftp_files_listbox.bind('<Double-Button-1>', self.open_selected_ftp_file)

        # Frame for server op
        ftp_button_frame = tk.Frame(left_frame)
        ftp_button_frame.pack(pady=10)

        try:
            # Check if FTP connection
            if self.ftp is None:
                messagebox.showerror("Error", "FTP connection not established.")
                return

            # Get list of files from FTP server
            self.refresh_ftp_files_list()

        except error_perm as e:
            messagebox.showerror("Permission Error", f"Permission denied: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to list files from FTP server: {str(e)}")

        # Frame for local upload
        right_frame = tk.Frame(file_operations_window)
        right_frame.pack(side=tk.LEFT, padx=10, pady=10, anchor=tk.N)

        # Label for local directory files
        local_file_list_label = tk.Label(right_frame, text="Files in Local Upload Directory:")
        local_file_list_label.pack(pady=10)

        # Listbox to display local files
        self.local_files_listbox = tk.Listbox(right_frame, width=50, height=10)
        self.local_files_listbox.pack(padx=10, pady=10)

        # Double click to open files
        self.local_files_listbox.bind('<Double-Button-1>', self.open_selected_local_file)

        # Frame for local uploads
        local_button_frame = tk.Frame(right_frame)
        local_button_frame.pack(pady=10)

        try:
            local_directory = self.local_directory_path.get()
            if not os.path.isdir(local_directory):
                messagebox.showerror("Error", "Invalid local directory.")
                return

            # Get list of files from Local Upload Directory
            local_files = os.listdir(local_directory)

            # Insert files into the Local Upload Directory listbox
            for file in local_files:
                self.local_files_listbox.insert(tk.END, file)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to list files from Local Upload Directory: {str(e)}")

        # Local dr upload button
        upload_files_button = tk.Button(local_button_frame, text="Upload Files", command=self.upload_files)
        upload_files_button.pack(side=tk.LEFT, padx=10)

        # FTP server download button
        download_files_button = tk.Button(ftp_button_frame, text="Download Files", command=self.download_files)
        download_files_button.pack(side=tk.LEFT, padx=10)

        # FTP server rename button
        rename_file_button = tk.Button(ftp_button_frame, text="Rename File", command=self.rename_ftp_file)
        rename_file_button.pack(side=tk.LEFT, padx=10)

        # FTP server delete button
        delete_file_button = tk.Button(ftp_button_frame, text="Delete File", command=self.delete_ftp_file)
        delete_file_button.pack(side=tk.LEFT, padx=10)

        # Local dr rename button
        rename_local_button = tk.Button(local_button_frame, text="Rename Local File", command=self.rename_local_file)
        rename_local_button.pack(side=tk.LEFT, padx=10)

        # Local dr delete button
        delete_local_button = tk.Button(local_button_frame, text="Delete Local File", command=self.delete_local_file)
        delete_local_button.pack(side=tk.LEFT, padx=10)

        # constantly refreshes gui looking for updates
        self.refresh_ftp_files_list()

    # opens the file on the FTP server
    def open_selected_ftp_file(self, event):
        try:
            # Check FTP connection
            if self.ftp is None:
                messagebox.showerror("Error", "FTP connection not established.")
                return

            # Get file from server
            index = self.ftp_files_listbox.curselection()
            if index:
                file_name = self.ftp_files_listbox.get(index)
                temp_file = tempfile.NamedTemporaryFile(delete=False)

                # Download server file as temp file
                with open(temp_file.name, 'wb') as f:
                    self.ftp.retrbinary(f"RETR {file_name}", f.write)

                # Open file
                os.startfile(temp_file.name)  # For Windows

        except error_perm as e:
            messagebox.showerror("Permission Error", f"Permission denied: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {str(e)}")

    # open local file
    def open_selected_local_file(self, event):
        try:
            # Get local file
            index = self.local_files_listbox.curselection()
            if index:
                file_name = self.local_files_listbox.get(index)
                local_directory = self.local_directory_path.get()
                file_path = os.path.join(local_directory, file_name)

                # Open the file
                os.startfile(file_path)  # For Windows

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {str(e)}")

    # upload files from local
    def upload_files(self):
        try:
            # Check FTP connection
            if self.ftp is None:
                messagebox.showerror("Error", "FTP connection not established.")
                return

            local_directory = self.local_directory_path.get()
            if not os.path.isdir(local_directory):
                messagebox.showerror("Error", "Invalid local directory.")
                return

            # upload files
            files_to_upload = os.listdir(local_directory)

            for file_name in files_to_upload:
                local_file_path = os.path.join(local_directory, file_name)

                if file_name.lower().endswith('.txt') or file_name.lower().endswith('.csv'):
                    # Use ASCII mode for text files
                    self.ftp.sendcmd('TYPE A')
                    with open(local_file_path, 'rb') as f:
                        self.ftp.storlines(f"STOR {file_name}", f)
                else:
                    # Use binary mode for other files
                    self.ftp.sendcmd('TYPE I')
                    with open(local_file_path, 'rb') as f:
                        self.ftp.storbinary(f"STOR {file_name}", f)

                print(f"Uploaded {file_name} successfully")

            messagebox.showinfo("Upload Complete", "Files uploaded successfully!")

            # Refresh FTP files list
            self.refresh_ftp_files_list()

        except error_perm as e:
            messagebox.showerror("Permission Error", f"Permission denied: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload files: {str(e)}")

    # download files
    def download_files(self):
        try:
            # Check FTP connection
            if self.ftp is None:
                messagebox.showerror("Error", "FTP connection not established.")
                return

            # Get the file from server
            index = self.ftp_files_listbox.curselection()
            if index:
                file_name = self.ftp_files_listbox.get(index)
                local_directory = self.local_directory_path.get()
                local_file_path = os.path.join(local_directory, file_name)

                # Download file
                with open(local_file_path, 'wb') as f:
                    self.ftp.retrbinary(f"RETR {file_name}", f.write)

                messagebox.showinfo("Download Complete", f"Downloaded {file_name} successfully to {local_file_path}")

        except error_perm as e:
            messagebox.showerror("Permission Error", f"Permission denied: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download file: {str(e)}")

    # rename server file
    def rename_ftp_file(self):
        try:
            # Check FTP connection
            if self.ftp is None:
                messagebox.showerror("Error", "FTP connection not established.")
                return

            index = self.ftp_files_listbox.curselection()
            if index:
                current_name = self.ftp_files_listbox.get(index)
                new_name = simpledialog.askstring("Rename File", f"Enter new name for '{current_name}':")
                if new_name:
                    self.ftp.rename(current_name, new_name)
                    self.refresh_ftp_files_list()  # Refresh file list in the GUI
                    messagebox.showinfo("Success", f"File '{current_name}' renamed to '{new_name}' successfully!")

        except error_perm as e:
            messagebox.showerror("Permission Error", f"Permission denied: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to rename file: {str(e)}")

    # delete server file
    def delete_ftp_file(self):
        # Check if file is selected
        if not self.ftp_files_listbox.curselection():
            messagebox.showerror("Error", "No file selected.")
            return

        try:
            # Get the file name
            index = self.ftp_files_listbox.curselection()[0]
            file_name = self.ftp_files_listbox.get(index)

            # Try and delete the server file
            self.ftp.delete(file_name)
            self.refresh_ftp_files_list()  # Refresh file list in the GUI
            messagebox.showinfo("Success", f"File '{file_name}' deleted successfully!")

        except error_perm as e:
            messagebox.showerror("Permission Error", f"Permission denied: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete file: {str(e)}")

    # rename file local
    def rename_local_file(self):
        try:
            # Check if a file is selected
            if not self.local_files_listbox.curselection():
                messagebox.showerror("Error", "No file selected.")
                return

            # Get file name
            index = self.local_files_listbox.curselection()[0]
            current_name = self.local_files_listbox.get(index)
            new_name = simpledialog.askstring("Rename File", f"Enter new name for '{current_name}':")

            # change the name
            if new_name:
                local_directory = self.local_directory_path.get()
                current_file_path = os.path.join(local_directory, current_name)
                new_file_path = os.path.join(local_directory, new_name)
                os.rename(current_file_path, new_file_path)
                self.refresh_local_files_list()  # Refresh file list in the GUI
                messagebox.showinfo("Success", f"File '{current_name}' renamed to '{new_name}' successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to rename file: {str(e)}")

    # delete file local
    def delete_local_file(self):
        try:
            # Check if a file is selected
            if not self.local_files_listbox.curselection():
                messagebox.showerror("Error", "No file selected.")
                return

            # Get file name
            index = self.local_files_listbox.curselection()[0]
            file_name = self.local_files_listbox.get(index)
            local_directory = self.local_directory_path.get()
            file_path = os.path.join(local_directory, file_name)

            # Delete file
            os.remove(file_path)
            self.refresh_local_files_list()  # Refresh file list in the GUI
            messagebox.showinfo("Success", f"File '{file_name}' deleted successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete file: {str(e)}")

    # loads the local directory
    def browse_local_directory(self):
        local_directory = filedialog.askdirectory(title="Select Local Directory")
        if local_directory:
            self.local_directory_path.set(local_directory)
            # Refresh directory
            self.refresh_local_files_list()

    # Loads the server files
    def refresh_ftp_files_list(self):
        # Clears the box first
        self.ftp_files_listbox.delete(0, tk.END)

        # Loads new contents
        try:
            if self.ftp:
                files = self.ftp.nlst('/')
                for file in files:
                    self.ftp_files_listbox.insert(tk.END, file)
        except error_perm as e:
            messagebox.showerror("Permission Error", f"Permission denied: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to list files from FTP server: {str(e)}")

    # Loads the local files
    def refresh_local_files_list(self):
        # Clear the box first
        self.local_files_listbox.delete(0, tk.END)

        # Loads new contents
        try:
            local_directory = self.local_directory_path.get()
            if os.path.isdir(local_directory):
                local_files = os.listdir(local_directory)
                for file in local_files:
                    self.local_files_listbox.insert(tk.END, file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to list files from Local Upload Directory: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    ftp_client = FTPClientGUI(root)
    root.mainloop()
