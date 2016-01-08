local P = {}
P.mt = {}

ledbuffer = P

function P.new (o)
   setmetatable( o, P.mt)
   return o
end

P.mt.__index = function (o, key)
   return {0,0,0}
end

return ledbuffer
