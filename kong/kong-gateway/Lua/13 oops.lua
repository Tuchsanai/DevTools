local t = {
    name = "Jack",
    age = 18,
    friends = {"Fred"},
}

print(t.name)

local function Pet(name)
    name = name or "Luis"
    return {
        name = name,
        status = "Hungry",

        feed = function(self)
            print(self.name .. " is fed")
            self.status = "Full"
        end
    }
end

local cat = Pet("Kitty")
local dog = Pet()

print(cat.name)
print(cat.status)
cat:feed()
print(cat.status)

print(dog.name)
print(dog.status)

-- Inheritance

local function Dog(name, breed)
    local dog = Pet(name)
    dog.breed = breed
    dog.loyalty = 0
    dog.isLoyal = function(self)
        return self.loyalty >= 10
    end

    dog.feed = function(self)
        print(self.name .. " is fed")
        self.status = "Full"
        self.loyalty = self.loyalty + 5
    end

    dog.bark = function(self)
        print("Woof Woof")
    end

    return dog
end

local lassy = Dog("Lassy", "Poodle")
print()
print("----")
print(lassy.breed)
print(lassy.bark())

if lassy: isLoyal() then
    print("Will protect against intruders")
else
    print("Will not protect against intruders")
end

lassy:feed()
lassy:feed()


if lassy: isLoyal() then
    print("Will protect against intruders")
else
    print("Will not protect against intruders")
end


