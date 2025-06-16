import mailbox
import os

phrases = [
    # -------------Purchases-----------------
    "You earned a dividend",
    "You have earned a dividend",
    "You have received a dividend",
    "You got a dividend!",
    # -------------Purchases-----------------
    "Your order has been filled",
    # -------------Deposits------------------
    "You made a deposit",
    "Your deposit is complete!",
]

def get_body(message):
    def remove_empty_lines(text):
        unwanted_chars = [
            # '\u0020',  # SPACE
            '\u00CD',  # LATIN CAPITAL LETTER I WITH ACUTE
            '\u008F',  # control character
            '\u034F'   # COMBINING GRAPHEME JOINER 
        ]

        cleaned_lines = []
        for line in text.splitlines():
            # Remove all unwanted characters
            for ch in unwanted_chars:
                line = line.replace(ch, '')
            if line.strip():  # keep only if there's any visible character left
                cleaned_lines.append(line)
        return "\n".join(cleaned_lines)

    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == 'text/plain' and 'attachment' not in content_disposition:
                charset = part.get_content_charset() or 'utf-8'
                body = part.get_payload(decode=True).decode(charset, errors='replace')
                return remove_empty_lines(body)
        return ""
    else:
        charset = message.get_content_charset() or 'utf-8'
        body = message.get_payload(decode=True).decode(charset, errors='replace')
        return remove_empty_lines(body)


def save_email(output_dir, i, from_, subject, date, body):
    filename = os.path.join(output_dir, f"{i}_email.txt")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"From: {from_}\n")
        f.write(f"Subject: {subject}\n")
        f.write(f"Date: {date}\n")
        f.write("\n")
        f.write(body)

    print(f"Saved email {i} to {filename}")


# Create output directory if not exists
input_file =  "Wealthsimple.mbox"
output_dir = "./emails"
ignore_dir = "./ignored_emails"
os.makedirs(output_dir, exist_ok=True)
os.makedirs(ignore_dir, exist_ok=True)

mbox = mailbox.mbox(input_file)

successful_count = 0
ignored_count = 0
for i, message in enumerate(mbox, start=1):
    body = get_body(message)
    from_ = message["From"] or "No From"
    subject = message["Subject"] or "No Subject"
    date = message["Date"] or "No Date"
    if subject in phrases:
        save_email(output_dir, i, from_, subject, date, body)
        successful_count += 1
    else:
        save_email(ignore_dir, i, from_, subject, date, body)
        ignored_count += 1

print("-" * 10)
print(f"\033[92mSuccessfully Parsed {successful_count} emails saved in {output_dir}\033[0m")
print(f"\033[91mIgnored {ignored_count} emails saved in {ignore_dir}\033[0m")
print("-" * 10)