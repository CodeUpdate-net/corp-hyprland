assert(_VERSION == "Lua 5.5")
for _, mode in ipairs({"incremental", "generational"}) do
    collectgarbage(mode)
    local retained = {}
    for i = 1, 1000 do
        retained[i] = {value = i, label = tostring(i)}
        if i % 100 == 0 then collectgarbage("step") end
    end
    collectgarbage("collect")
    for i, item in ipairs(retained) do
        assert(item.value == i and item.label == tostring(i))
    end
end
collectgarbage("incremental")
