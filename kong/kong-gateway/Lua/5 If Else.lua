if true then
    print("Statement was true")
end

--[[
    >
    <
    >=
    <=
    ~=
    ==
]]

local age = 7

if age > 17 or age < 60 then
    print("You many Enter the club")
end

if age > 20 then
    print("You are old")
elseif age > 10 then
    print("You are Teen")
elseif age > 5 then
    print("boo boo kid")
else
    print("you are young")
end


local old = false
if age > 30 then
    old = true
end

local old = age > 30 and true or true

print(old)