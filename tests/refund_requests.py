import os
import win32com.client

# Output directory
SAVE_DIR = r"C:\temp\refund_attachments"
os.makedirs(SAVE_DIR, exist_ok=True)

# Connect to Outlook
outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")


def print_folders(folder, indent=0):
    try:
        print("  " * indent + f"- {folder.Name}")
        for i in range(1, folder.Folders.Count + 1):
            subfolder = folder.Folders.Item(i)
            print_folders(subfolder, indent + 1)
    except Exception as e:
        print("  " * indent + f"[ERROR accessing folder: {e}]")


print("\n=== TOP LEVEL MAILBOXES (STORES) ===")

for i in range(1, outlook.Folders.Count + 1):
    try:
        root = outlook.Folders.Item(i)
        print(f"\n=== STORE {i}: {root.Name} ===")
        print_folders(root)
    except Exception as e:
        print(f"\n[ERROR accessing store {i}: {e}]")

# Access Inbox
# Navigate to your subfolder (adjust name exactly)

mailbox = outlook.Folders["max.rijnberg@lbh-group.com"]
folder = mailbox.Folders["Compliance LBH"].Folders["Refund requests"]

# Iterate emails
messages = folder.Items.Restrict("[HasAttachment] = True")

# Optional: sort newest first
messages.Sort("[ReceivedTime]", True)

saved_files = []

for message in messages:
    try:
        attachments = message.Attachments

        for i in range(1, attachments.Count + 1):
            attachment = attachments.Item(i)
            filename = attachment.FileName.lower()

            if filename.endswith(".pdf") or filename.endswith(".docx"):
                save_path = os.path.join(SAVE_DIR, attachment.FileName)

                # Handle duplicate file names
                base, ext = os.path.splitext(save_path)
                counter = 1
                while os.path.exists(save_path):
                    save_path = f"{base}_{counter}{ext}"
                    counter += 1

                attachment.SaveAsFile(save_path)
                saved_files.append(save_path)

    except Exception as e:
        print(f"Error processing message: {e}")

print(f"Saved {len(saved_files)} files.")
