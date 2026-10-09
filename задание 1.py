import random
import string

length = int(input('Введи длину пароля: '))

chars = string.ascii_letters + string.digits

password = ''.join(random.choices(chars, k=length))

print('Твой пароль:', password)