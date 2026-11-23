# from hungercore import clearTerminal
from calagoapi import Panel
from calagoapi.extensions import enable

# clearTerminal()
enable('minecraft')                      # adds panel.minecraft, sets process-wide defaults
panel = Panel(url='https://dash.hungernet.dev', api_key='c7sp_Gkf994sRJCWSp1xWzJbLvcUtdHwBfVkn2jYEMMxyBdX')
server = panel.minecraft.getServer('75e88326-0ace-4866-af62-845493ccdced', bridge_url='https://api.hungersmp.com', bridge_token_id='root', bridge_token_secret='6734c0db5b21699fbb20f6238e9525eaac09aa1d3f14b21f99c1eedcef1d8944')

# server.bridge.log('test', thread='THREAD', logger='Logger', level='LEVEL')

release = server.installBridge(minecraft_version='26.3', loader='fabric')
print(release)