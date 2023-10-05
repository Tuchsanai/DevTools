import argparse

parser = argparse.ArgumentParser()
parser.add_argument("name", help="the name to greet")
parser.add_argument("--age", help="the age of the person being greeted", type=int)
args = parser.parse_args()

greeting = "Hello, " + args.name + "!"
if args.age:
    greeting += " You are " + str(args.age) + " years old."

print(greeting)
