print(os.date())
print(os.time())

local past = (os.time({
    year = 2000,
    month = 10,
    day = 1,
    hour = 13,
    min = 20,
    sec = 10
})/ 3600)

print(os.time()-past)

-- os.execute("ipconfig")

local start = os.clock()

for i = 1, 100000000 do
    local x = 10
end

print(os.clock() - start)

os.exit()