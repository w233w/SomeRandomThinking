# Simple lib to genrate password, all password has exactly 22 bytes length.
import hashlib
import base64
import random
import argparse
import sys


# Based on seed input, first change it to md5 then change md5 to base64.
# finally remove two '==' at end of the base64 string.
# generated passward contain both upper/lower case english letter, number and special character.
def gen_hash(seed: [str, int]) -> str:
    string = str(seed)
    md5 = hashlib.md5(string.encode(encoding='utf-8')).digest()
    b64 = base64.b64encode(md5)
    return b64[:-2].decode()


# Based on seed input, first change it to int without negitive mark
# Randomly select n's character from alphabet and make them a string.
# generated passward contain both upper/lower case english letter, number and special character.
def gen_random(seed: [str, int]) -> str:
    real_seed = abs(hash(seed))
    nums = map(str, list(range(10)))
    lowercase = 'abcdefghijklmnopqrstuvwxyz'
    uppercase = lowercase.upper()
    special_char = '!@#$%^&*()[]+-<>'
    alphabet = list(nums) + list(lowercase) + list(uppercase) + list(special_char)
    random.seed(real_seed)
    return ''.join(random.choices(alphabet, k=22))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    gen_type = parser.add_mutually_exclusive_group()
    gen_type.add_argument("-H", help="Using md5 and base64 to generate password.")
    gen_type.add_argument("-R", help="Using RNG and alphabet to generate password.")
    args = parser.parse_args()
    if args.H is not None:
        print('Hash: ' + gen_hash(args.H))
    elif args.R is not None:
        print("Random: " + gen_random(args.R))
    else:
        seed = input("Enter your seed: ")
        method = 0
        while method not in [1, 2]:
            method = int(input("Enter 1 for Hash or 2 for Random: "))
        if method == 1:
            print('Hash: ' + gen_hash(seed))
        elif method == 2:
            print("Random: " + gen_random(seed))
        input("Press Enter to Exit...")

