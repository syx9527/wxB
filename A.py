import json

ru = r"""D:\Program Files (x86)\Tencent\QQ\Bin\QQ.EXE
D:\Program Files (x86)\Tencent\QQ\Bin\QQExternal.exe
D:\Program Files (x86)\Tencent\QQ\Bin\TXPlatform.exe
C:\Program Files (x86)\Common Files\Tencent\QQProtect\Bin\QQProtect.exe
C:\Program Files (x86)\Common Files\Tencent\QQProtect\Bin\QQProtectUpd.exe
C:\Users\SYX\AppData\Roaming\Tencent\QQ\commonf_inst\ACCPUpdate.exe
D:\Program Files (x86)\Tencent\QQ\Bin\QQUrlMgr.exe
D:\Program Files (x86)\Tencent\QQ\Bin\QQCallyo.exe
D:\Program Files (x86)\Tencent\QQ\Bin\QQScLauncher.exe
D:\Program Files (x86)\Tencent\QQ\Bin\Timwp.dll
D:\Program Files (x86)\Tencent\QQ\Bin\QQApp.exe
D:\Program Files (x86)\Tencent\QQ\ShellExt\QQShellExt.dll
D:\Program Files (x86)\Tencent\QQ\ShellExt\QQShellExt64.dll
C:\Users\SYX\AppData\Roaming\Tencent\QQ\commonf_inst\QQLinkChanger.exe
D:\Program Files (x86)\Tencent\QQ\Bin\txupd.exe
C:\Users\SYX\AppData\Roaming\Tencent\QQ\commonf_inst\firewalltool.exe
C:\Program Files (x86)\Common Files\Tencent\Npchrome\npactivex.dll
D:\Program Files (x86)\Tencent\QQ\Bin\SetupEx\QQSetupEx.exe
D:\Program Files (x86)\Tencent\QQ\Bin\CPHelper.dll"""
b = ru.split('\n')
data = {
    "ver": "5.0",
    "tag": "hipsuser",

    "data": [

    ],

}
for i in range(len(b)):
    res = {
              "id": i,
              "power": 1,
              "name": f"{i}",
              "procname": b[i],
              "treatment": 3,
              "policies": [
                  {
                      "montype": 1,
                      "action_type": 15,
                      "res_path": "C:\\*"
                  },
              ],
          },
    data['data'].append(res)
# print(str(data))
print(json.dumps(data))