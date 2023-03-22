import hashlib
import base64


# A super simple passward generator
# generated passward contain both upper/lower case english letter, number and special character.
s = '??????'
md5 = hashlib.md5(s.encode(encoding='utf-8')).digest()
b64 = base64.b64encode(hashlib.md5(s.encode(encoding='utf-8')).digest())
print(b64[:-2].decode())
