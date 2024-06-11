local arr = { 10, true, 20, 23, "xyz"}
local x, y, z = 10, 15, 20


print(arr)
print(arr[0])
print(arr[1])
print(arr[5])
print(#arr)

local arr = { 10, 3, 20}
table.sort(arr)
print(arr[1])

table.insert(arr, 2, 45)
print(arr[2])

table.remove(arr, 2)
print(arr[2])

print(table.concat(arr, "-"))

print(arr[1])

local arr = {
    {1, 2, 3},
    {6, 8, 0},
    {9, 99 , 989}
}

print(arr[1])
print(arr[2][1])

print(" ")

for i = 1, #arr do
    for j = 1, #arr[i] do
        print(arr[i][j])
    end
end