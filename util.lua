function reset () node.restart() end
function dump (t)
   if t == nil then
      t = _G
   end
   for k,v in pairs(t) do
      print(k,v)
   end
end
