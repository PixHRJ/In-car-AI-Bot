import json

# 退出应用函数
def exit_app():
    print("结束循环，再见！")
    # 可以在这里执行其他退出应用的操作，比如关闭音频播放器等
    exit()
# 全局变量，用于控制音乐播放状态
music_playing = False
def switch_output_mode(output_mode):
    if output_mode == "audio":
        output_mode = "text"
    else:
        output_mode = "audio"
    print("输出模式切换为:", output_mode)
    return output_mode

# 播放音量设置函数
def set_volume(volume):
    new_volume_str = input("请输入音量(0-1)：")
    try:
        new_volume = float(new_volume_str)
        if 0.0 <= new_volume <= 1.0:
            volume = new_volume
            print("音量设置为:", volume)
        else:
            print("音量必须介于0和1之间！")
    except ValueError:
        print("请输入有效的数字！")
    return volume

# 读取配置文件函数
def read_config():
    with open('config.json', encoding='utf-8') as f:
        config = json.load(f)
    return config

# 重新加载配置文件函数
def reload_config():
    global output_mode, volume, input_mode
    config = read_config()
    output_mode = config["output_mode"]
    volume = config["volume"]
    input_mode = config["input_mode"]
    print("重新加载配置文件成功。")
