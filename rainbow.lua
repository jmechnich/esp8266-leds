local P = {}
rainbow = P

P.nled = 5
P.pin  = 2

local function norm(v)
   if v == nil then
      return 1
   end
   while v < 1 do
      v = v + P.nled
   end
   while v > P.nled do
      v = v - P.nled
   end
   return v
end

require('colorsys')
function P.show(offset)
   local buf = ""
   for i=1,P.nled do
      local frac = i
      if offset ~= nil then
         frac = norm(frac+offset)
      end
      local r,g,b = hsvToRgb((frac-1)/P.nled, 1, 0.1)
      buf = buf..string.char(r)..string.char(g)..string.char(b)
   end
   ws2812.writergb( P.pin, buf)
end

local i = 0
function P.cycle()
   tmr.alarm(4,10,0, function ()
                P.show(i)
                i = (i+1)%P.nled
                P.cycle()
   end)
end

function P.stop()
   tmr.stop(4)
   ws2812.writergb( P.pin, string.char(0):rep(P.nled*3))
   i=0
   tmr.alarm(4,1000,0, collectgarbage)
end

return rainbow
