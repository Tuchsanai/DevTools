-- io.output("myFile.txt")
-- io.write("Hello World!")
-- io.close()

io.input("myFile.txt")

local file = io.read(5)

print(file)

local filex = io.read("*number")
print(filex)

local file1 = io.read("*line")
print(file1)

print(io.read("*all"))

io.close()

local file = io.open("myFilex.txt", "w")
file:write("My name is Arnab")
file:close()