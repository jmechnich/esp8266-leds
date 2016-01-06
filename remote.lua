local P = {}
remote = P
P.__index = P

local pin_led = 8
P.buttons = {}
P.sleepdelay = 5

function P.blink(count,dt)
   if count == nil then count = 1 end
   if dt == nil then dt = 100 end

   for i=1,count do
      gpio.write(pin_led, gpio.HIGH)
      tmr.delay(dt*1000)
      gpio.write(pin_led, gpio.LOW)
      tmr.delay(dt*1000)
   end
end

function P.restartSleepTimer()
   tmr.stop(2)
   tmr.alarm(2,P.sleepdelay*1000,0,function ()
                print("Sleeping")
                P.blink(2)
                node.dsleep(0)
   end)
end

function P.init_led(pin)
   if pin ~= nil then pin_led = pin end
   gpio.mode(pin_led,gpio.OUTPUT)
   gpio.write(pin_led,gpio.LOW)
end

function P.init_buttons(buttons)
   if buttons ~= nil then P.buttons = buttons end
   for pin,func in pairs(P.buttons) do
      gpio.mode(pin,gpio.INPUT,gpio.PULLUP)
      local state = 0
      local function action (lvl)
         P.restartSleepTimer()
         if lvl == 0 then
            if state == 0 then
               tmr.delay(20)
               if gpio.read(pin) == gpio.LOW then
                  state = 1
                  tmr.alarm(1,1000,0, function()
                               if state == 1 and gpio.read(pin) == gpio.LOW then
                                  if func[2] ~= nil then
                                     func[2]()
                                  end
                                  state = 2
                               else
                                  state = 0
                               end
                  end)
               else
                  state = 0
               end
            end
         else
            if state == 1 and func[1] ~= nil then
               func[1]()
            end
            state = 0
            tmr.stop(1)
         end
      end
      gpio.trig(pin, "both", action)
   end
end

return remote
