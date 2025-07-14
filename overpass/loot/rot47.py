def rot47(s):
    result = []
    for c in s:
        o = ord(c)
        if 33 <= o <= 126:
            result.append(chr(33 + ((o + 14) % 94)))
        else:
            result.append(c)
    return "".join(result)

input_file = "/usr/share/wordlists/rockyou.txt"
output_file = "rockyou-5k-rot47.txt"

with open(input_file, "r", encoding="latin-1") as infile, open(output_file, "w", encoding="latin-1") as outfile:
    for i, line in enumerate(infile):
        if i >= 5000:
            break
        password = line.rstrip("\n")
        outfile.write(rot47(password) + "\n")

print(f"ROT47 wordlist saved to {output_file}")

