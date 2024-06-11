local str = [[
    Hello World
    My name is Raj
]]

print(str)
print(type(str))
print(#str)


local x = 22
x = tostring(22)
print(x)
print(type(x))

print("Hello\nWorld\t!!!!\vI'm \"Raj\\Arnab\"")

local strx = "Hello World"
print(string.sub(strx, 7, 99))
print(string.sub(strx, 7))
print(string.byte("a"))
print(string.byte(strx, 1, 99))
print(string.rep(strx, 10, ","))
print(string.format("pi: %.2f \nMy age: %i", math.pi, 18))


print(string.find(strx, "orl"))
print(string.match(strx, "orl"))
print(string.gsub(strx, "o", "!"))
