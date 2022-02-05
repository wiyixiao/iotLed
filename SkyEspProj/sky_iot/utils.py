import json

class UtilsTool:
    @staticmethod
    def read_json(filePath):
        with open(filePath,'rb') as fp:
            a = json.load(fp)
        return a

    @staticmethod
    def write_json(filepath,msg):
        with open(filepath,'w+') as fp:
            # fp.write(json.dumps(msg, indent=4))
            # json.dump(msg, fp)
            fp.write(json.dumps(msg))

    @staticmethod
    def rang_map(x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
