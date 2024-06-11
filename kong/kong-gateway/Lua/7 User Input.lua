local num1, num2 = 10, 5
local true_ans = num1 + num2
io.write("Input " .. num1 .. "+" .. num2 .. ": ")
local ans = io.read()

if tonumber(ans) == true_ans then
    print("You are correct!")
else
    print("\n Your answer is " .. ans .. " Incorrect")
end