local P={}
led = P

P.pin = 2
P.nled = 5
require('ledbuffer')
P.buffer = ledbuffer.new{}

function P.clear()
   for i,pix in pairs(P.buffer) do
      P.buffer[i] = nil
   end
end

function P.dump ()
   for i,pix in pairs(P.buffer) do
      print(i,unpack(pix))
   end
end

local function getrange(i,max)
   if i < max then
      return string.char(unpack(P.buffer[i]))..getrange(i+1,max)
   end
   return string.char(unpack(P.buffer[max]))
end

function P.show_off(offset)
   if offset == nil then offset = 0 end
   if offset > 0 then return ws2812.writergb( P.pin, getrange(P.nled-offset+1,P.nled)..getrange(1,P.nled-offset)) end
   if offset < 0 then return ws2812.writergb( P.pin, getrange(-offset+1,P.nled)..getrange(1,-offset)) end
   return ws2812.writergb( P.pin, getrange(1,P.nled))
end

function P.show()
   local buf = ""
   for i=1,P.nled do
      buf = buf..string.char(unpack(P.buffer[i]))
   end
   return ws2812.writergb( P.pin, buf)
end

function P.setUniColor(r,g,b)
   if r == nil then r = 0 end
   if g == nil then g = 0 end
   if b == nil then b = 0 end
   for i=1,P.nled do
      P.buffer[i] = {r,g,b}
   end
end

function P.setRainbow(offset)
   require('colorsys')
   if offset == nil then offset = 0 end
   for i=1,P.nled do
      local frac = (i-1+offset)%P.nled
      local r,g,b = hsvToRgb(frac/P.nled, 1, 0.1)
      P.buffer[i] = { r,g,b }
   end
end

function P.off()
   P.clear()
   P.show()
end

return led
