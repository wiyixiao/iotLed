from sky_iot.utils import UtilsTool

def _init():
    global _global_dict
    _global_dict = {}

def set_value(name, value):
    _global_dict[name] = value

def get_value(name, defValue=None):
    try:
        return _global_dict[name]
    except KeyError:
        return defValue

_init()

def read_config():
    set_value("config", UtilsTool.read_json("./config.json")) # 保存成功 重新读取
    gl_config = get_value("config")

    gl_config['deviceConfig']['apname'] = gl_config['deviceid']
    gl_config['deviceConfig']['clientid'] = gl_config['deviceid']
    gl_config['uploadMsg']['id'] = gl_config['deviceid']

    set_value("config", gl_config)

    clientid = gl_config['deviceConfig']['clientid']
    set_value("topics",{
        "control":'device/%s/control/'%(clientid),
        "setting":'device/%s/setting/'%(clientid)
    })

    pass

def save_config(cfg):
    print(cfg)
    UtilsTool.write_json("./config.json", cfg)
    read_config()

read_config()