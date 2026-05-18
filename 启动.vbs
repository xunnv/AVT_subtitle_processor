Set WshShell = CreateObject("WScript.Shell")
currentDir = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))
batPath = currentDir & "run.bat"
WshShell.Run """" & batPath & """", 0, False
Set WshShell = Nothing