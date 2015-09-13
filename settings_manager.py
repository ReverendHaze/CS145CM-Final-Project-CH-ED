def load_settings():
    with open("settings.conf") as f:
        config = {}
        for line in f:
            if line[-1:] == '\n':
                line = line[:-1].split(' ')
                key = line[0]
                val = line[-1]
                try:
                    config[key] = float(val)
                except:
                    config[key] = val
            else:
                break
    print(config)
    return config

