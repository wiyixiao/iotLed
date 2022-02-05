from sky_iot.utils import UtilsTool

def test():
    str = 'aaa'
    str1 = 'aaabbb'
    if str1.startswith(str):
        print("ok")
    pass

test()

print(UtilsTool.rang_map(100, 0, 180, 0.5, 2.5))

def for_test():
    step = 1;
    last_angle = 270
    target = 100
    m_target = target
    if target < last_angle:
        step = -1

    m_target += step

    for angle in range(last_angle, m_target, step):
        print(angle)

for_test()
