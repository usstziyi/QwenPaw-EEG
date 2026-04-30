import os
import mne



def set_datasets_path():
    # 目录配置
    data_dir = os.path.abspath("./mne-eeg-learning/datasets")
    os.makedirs(data_dir, exist_ok=True)
    # 每次运行强制更新 config
    mne.set_config("MNE_DATA", data_dir)
    mne.set_config("MNE_DATASETS_SAMPLE_PATH", data_dir)
    print("-" * 80)
    print("config file =", mne.get_config_path())
    print("=" * 80)
    # 打印config 内容,友好格式
    config = mne.get_config()
    for key, value in config.items():
        print(f"* {key:25s}: {value}")
    print("-" * 80)