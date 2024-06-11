local routine_1 = coroutine.create(
    function()
        for i = 1, 10, 1 do
            print("(Routine 1): " .. i)

            if i == 5 then
                coroutine.yeild()
            end
        end
    end
)

local routine_func = function()
    for i = 11, 20 do
        print("(Routine 2): " .. i)
    end
end

local routine_2 = coroutine.create(routine_func)

coroutine.resume(routine_1)
coroutine.resume(routine_2)

if coroutine.status(routine_1) == "suspended" then
    coroutine.resume(routine_1)
end

print(coroutine.status(routine_1))
coroutine.resume(routine_1)
print(coroutine.status(routine_2))
