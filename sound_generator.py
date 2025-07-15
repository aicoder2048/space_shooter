"""
音效生成器模块
用于程序化生成游戏武器音效
"""

import numpy as np
import pygame
import os
import math

class SoundGenerator:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        pygame.mixer.init(frequency=sample_rate, size=-16, channels=2, buffer=512)
    
    def generate_tone(self, frequency, duration, amplitude=0.5):
        """生成基础音调"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave = amplitude * np.sin(2 * np.pi * frequency * t)
        return wave
    
    def apply_envelope(self, wave, attack=0.01, decay=0.1, sustain=0.7, release=0.2):
        """应用ADSR包络"""
        total_samples = len(wave)
        attack_samples = int(attack * self.sample_rate)
        decay_samples = int(decay * self.sample_rate)
        release_samples = int(release * self.sample_rate)
        sustain_samples = total_samples - attack_samples - decay_samples - release_samples
        
        envelope = np.ones(total_samples)
        
        # Attack
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Decay
        if decay_samples > 0:
            envelope[attack_samples:attack_samples + decay_samples] = \
                np.linspace(1, sustain, decay_samples)
        
        # Sustain
        if sustain_samples > 0:
            envelope[attack_samples + decay_samples:attack_samples + decay_samples + sustain_samples] = sustain
        
        # Release
        if release_samples > 0:
            envelope[-release_samples:] = np.linspace(sustain, 0, release_samples)
        
        return wave * envelope
    
    def add_noise(self, wave, noise_level=0.1):
        """添加噪音"""
        noise = np.random.normal(0, noise_level, len(wave))
        return wave + noise
    
    def apply_simple_filter(self, wave, cutoff_freq, filter_type='lowpass'):
        """应用简单滤波器（无需scipy）"""
        # 简单的移动平均滤波器
        if filter_type == 'lowpass':
            # 低通滤波 - 平滑高频噪音
            window_size = max(1, int(self.sample_rate / cutoff_freq))
            kernel = np.ones(window_size) / window_size
            return np.convolve(wave, kernel, mode='same')
        else:
            # 其他滤波器类型暂时返回原波形
            return wave
    
    def frequency_sweep(self, start_freq, end_freq, duration, amplitude=0.5):
        """生成频率扫描"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        freq = np.linspace(start_freq, end_freq, len(t))
        wave = amplitude * np.sin(2 * np.pi * np.cumsum(freq) * duration / len(t))
        return wave
    
    def generate_beam_sound(self):
        """生成光束武器音效
        特点：高频、连续、科幻感
        """
        print("生成光束武器音效...")
        
        # 基础载波 - 高频音调
        carrier = self.generate_tone(1200, 0.8, 0.4)
        
        # 调制波 - 创造"光束"的颤动效果
        modulator = self.generate_tone(80, 0.8, 0.3)
        modulated = carrier * (1 + modulator)
        
        # 频率扫描 - 从高到低，模拟能量释放
        sweep = self.frequency_sweep(1800, 900, 0.8, 0.2)
        
        # 合成波形
        beam_wave = modulated + sweep
        
        # 添加高频噪音，增加"电子感"
        beam_wave = self.add_noise(beam_wave, 0.05)
        
        # 应用低通滤波，去除刺耳的高频
        beam_wave = self.apply_simple_filter(beam_wave, 3000, 'lowpass')
        
        # 应用包络 - 快速攻击，长持续，慢释放
        beam_wave = self.apply_envelope(beam_wave, attack=0.02, decay=0.1, sustain=0.8, release=0.3)
        
        # 标准化音量
        beam_wave = np.clip(beam_wave, -1, 1)
        
        return beam_wave
    
    def generate_missile_sound(self):
        """生成导弹武器音效
        特点：低频启动、高频尾音、爆炸感
        """
        print("生成导弹武器音效...")
        
        # 第一阶段：发射音 - 低频轰鸣
        launch_wave = self.generate_tone(120, 0.3, 0.6)
        launch_wave = self.add_noise(launch_wave, 0.2)  # 更多噪音
        
        # 第二阶段：飞行音 - 频率上升
        flight_wave = self.frequency_sweep(200, 800, 0.4, 0.4)
        
        # 第三阶段：撞击音 - 高频爆炸
        impact_base = self.generate_tone(1500, 0.2, 0.5)
        impact_noise = np.random.normal(0, 0.3, int(0.2 * self.sample_rate))
        impact_wave = impact_base + impact_noise
        
        # 合成完整导弹音效
        missile_wave = np.concatenate([launch_wave, flight_wave, impact_wave])
        
        # 应用简单低通滤波
        missile_wave = self.apply_simple_filter(missile_wave, 2000, 'lowpass')
        
        # 应用包络 - 多段包络模拟发射过程
        total_samples = len(missile_wave)
        envelope = np.ones(total_samples)
        
        # 发射段：快速攻击
        launch_samples = int(0.3 * self.sample_rate)
        envelope[:launch_samples] = np.linspace(0, 1, launch_samples)
        
        # 飞行段：保持音量
        flight_samples = int(0.4 * self.sample_rate)
        # 保持原有音量
        
        # 撞击段：快速衰减
        impact_samples = total_samples - launch_samples - flight_samples
        if impact_samples > 0:
            envelope[-impact_samples:] = np.linspace(1, 0, impact_samples)
        
        missile_wave = missile_wave * envelope
        
        # 标准化音量
        missile_wave = np.clip(missile_wave, -1, 1)
        
        return missile_wave
    
    def save_sound(self, wave, filename):
        """保存音效到文件"""
        # 转换为16位整数
        wave_int = (wave * 32767).astype(np.int16)
        
        # 创建立体声（复制到两个声道）
        stereo_wave = np.column_stack([wave_int, wave_int])
        
        # 创建pygame Sound对象
        sound = pygame.sndarray.make_sound(stereo_wave)
        
        # 保存为wav文件
        resources_dir = os.path.join(os.path.dirname(__file__), 'resources', 'sounds')
        os.makedirs(resources_dir, exist_ok=True)
        file_path = os.path.join(resources_dir, filename)
        
        # 使用pygame保存
        pygame.mixer.Sound.play(sound)  # 播放一次以确保格式正确
        pygame.time.wait(10)  # 短暂等待
        
        # 手动保存为wav格式
        import wave
        with wave.open(file_path, 'w') as wav_file:
            wav_file.setnchannels(2)  # 立体声
            wav_file.setsampwidth(2)  # 16位
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(stereo_wave.tobytes())
        
        print(f"音效已保存到: {file_path}")
        return sound

def generate_weapon_sounds():
    """生成所有缺失的武器音效"""
    try:
        print("开始生成武器音效...")
        
        generator = SoundGenerator()
        
        # 生成光束音效
        beam_wave = generator.generate_beam_sound()
        generator.save_sound(beam_wave, 'beam.wav')
        
        # 生成导弹音效（独特版本）
        missile_wave = generator.generate_missile_sound()
        generator.save_sound(missile_wave, 'missile_unique.wav')
        
        print("✅ 武器音效生成完成！")
        
    except ImportError as e:
        print(f"❌ 缺少依赖库: {e}")
        print("请安装: pip install numpy")
        return False
    except Exception as e:
        print(f"❌ 生成音效时出错: {e}")
        return False
    
    return True

if __name__ == "__main__":
    generate_weapon_sounds()