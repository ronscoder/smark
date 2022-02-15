from libs.configs import getConfigs, setConfigs


CONFIGS = {
    'NIFTYBANK_CE': ('BANKNIFTY2210637900CE', 'token'),
    'NIFTYBANK_PE': ('BANKNIFTY2210637500PE', 'token'),
}


setConfigs(CONFIGS)

confs = getConfigs()
for k in confs:
    print(k, confs[k])