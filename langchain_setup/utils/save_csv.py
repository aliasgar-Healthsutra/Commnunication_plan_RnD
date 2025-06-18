import re

def save_csv(csv_text:str):
    try:
        with open("raw_schedule.txt", "w", encoding="utf-8") as f:
            f.write(csv_text)
        with open("raw_schedule.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
        print(f"Read {len(lines)} lines from raw_schedule.txt")

        output = []
        current_date = ""
        current_topic = ""
        current_message = []

        for i, line in enumerate(lines):
            original_line = line  
            line = line.strip()
            if not line:
                continue
            # Updated regex to allow spaces after date and before pipe
            match = re.match(r'^\d{4}-\d{2}-\d{2}\s*\|\s*', line)
            print(f"Line {i+1}: '{original_line.rstrip()}' — Match? {bool(match)}")
            if match:
                if current_date:
                    msg = " ".join(current_message).strip()
                    output.append(f"{current_date} | {current_topic} | {msg}")
                parts = [p.strip() for p in line.split("|", 2)]
                if len(parts) == 3:
                    current_date = parts[0]
                    current_topic = parts[1]
                    current_message = [parts[2]]
                else:
                    print(f"Line {i+1} does not split into 3 parts: {line}")
            else:
                current_message.append(line.strip())


        # Add last entry
        if current_date and current_message:
            msg = " ".join(current_message).strip()
            output.append(f"{current_date} | {current_topic} | {msg}")

        print(f"Parsed {len(output)} entries")

        with open("cleaned_schedule.csv", "w", encoding="utf-8") as f:
            for row in output:
                f.write(row + "\n")

        print("✅ Cleaned CSV written to cleaned_schedule.csv")

    except FileNotFoundError:
        print("❌ raw_schedule.txt not found. Please make sure the file exists.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

