msg = input("Quel message veux-tu encrypter ? ")
try:
	decal = int(input("Avec quel décalage ? "))
except:
	decal = 1
result = ""

for c in msg:
	i = ord(c)
	if 33 <= i <= 126:
		i = 33 + ((i - 33 + decal) % 94)
	result += chr(i)

print(result)