function reset ()
   node.restart()
end

function dump (t)
   if t == nil then
      t = _G
   end
   for k,v in pairs(t) do
      print(k,v)
   end
end

function sysinfo ()
   local majorVer, minorVer, devVer, chipid, flashid, flashsize, flashmode, flashspeed = node.info()
   local heap = node.heap()
   local remaining, used, total=file.fsinfo()
   print("\nSystem info:\n"..
            "Node MCU "..majorVer.."."..minorVer.."."..devVer.."\n"..
            "Chip ID     : "..chipid.."\n"..
            "Flash ID    : "..flashid.."\n"..
            "Flash Size  : "..flashsize.."\n"..
            "Flash Mode  : "..flashmode.."\n"..
            "Flash Speed : "..flashspeed.."\n"..
            "Heap memory : "..heap.." Bytes\n\n"..
            "File system info:\n"..
            "Total : "..total.." Bytes\n"..
            "Used  : "..used.." Bytes\n"..
            "Remain: "..remaining.." Bytes\n")
end
