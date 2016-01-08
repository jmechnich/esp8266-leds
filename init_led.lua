require('led')
led.show()

local offset = 0

local function cycle_off (t)
   return tmr.alarm(4,t,0, function ()
                       led.show_off(offset)
                       offset = (offset+1)%led.nled
                       return cycle_off(t)
   end)
end

local function cycle (t)
   return tmr.alarm(4,t,0, function ()
                       led.setRainbow(offset)
                       led.show()
                       offset = (offset+1)%led.nled
                       return cycle(t)
   end)
end

function rbow_start_off(t)
   if t == nil then t = 10 end
   led.setRainbow()
   return cycle_off(t)
end

function rbow_start(t)
   if t == nil then t = 10 end
   return cycle(t)
end

function rbow_stop()
   tmr.stop(4)
   led.off()
   offset = 0
   return tmr.alarm(4,1000,0, collectgarbage)
end
