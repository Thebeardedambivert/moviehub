import random

code = ''.join(random.choice('0123456789') for _ in range(10))
total = [int(code[i]) * 3 if i % 2 == 0 else int(code[i]) for i in range(10)]
print(total)