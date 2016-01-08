function reset ()
   return node.restart()
end

function dump (t)
   for k,v in pairs(t) do
      print(k,v)
   end
end

function gdump()
   return dump (_G)
end

function ls ()
   local sum = 0
   for n,s in pairs(file.list()) do
      sum = sum + s
      print(n,s)
   end
   print ("Total:",sum.." Bytes")
end

function sysinfo ()
   local majorVer, minorVer, devVer, chipid, flashid, flashsize, flashmode, flashspeed = node.info()
   local heap = node.heap()
   local luamem = collectgarbage("count")
   local remaining, used, total=file.fsinfo()
   print("\nSystem info:\n"..
            "Node MCU "..majorVer.."."..minorVer.."."..devVer.."\n"..
            "Chip ID     : "..chipid.."\n"..
            "Flash ID    : "..flashid.."\n"..
            "Flash Size  : "..flashsize.."\n"..
            "Flash Mode  : "..flashmode.."\n"..
            "Flash Speed : "..flashspeed.."\n\n"..
            "Mem free (heap) : "..heap.." Bytes\n"..
            "Mem used by lua : "..math.ceil(luamem*1000).." Bytes\n\n"..
            "File system info:\n"..
            "Total : "..total.." Bytes\n"..
            "Used  : "..used.." Bytes\n"..
            "Remain: "..remaining.." Bytes\n")
end
