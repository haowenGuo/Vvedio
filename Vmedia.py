import json
import math
import os
import random
import time
import torch
import cv2
import numpy as np
from bs4 import BeautifulSoup
from moviepy.video.VideoClip import VideoClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import AudioFileClip, concatenate_audioclips

from TTS.api import TTS
# 自定义标签的 HTML 文档
from moviepy.editor import ImageClip, concatenate_videoclips

from BackgroundProcess import BackgroundProcess
import subprocess


class Parseerror(RuntimeError):
    def __init__(self, arg):
        self.args = arg
class Vmedia():
    def __init__(self):
        self.media_path =''
        self.media_type = 'mp4'
        self.animation_src=''
        self.voice_src=''
        self.clip={'background':'',"speed":'',"anim":'','text':'','duration':0}
        self.data = list()
        self.ps = BackgroundProcess()

        self.tts=self.initTTS()
        # 启动EXE文件

    # 使用 BeautifulSoup 解析文档
    def work(self,doc):
        self.parser(doc)
        aduio=self.TTS(self.data,self.voice_src)
        print(self.data)
        result = self.add_voice(aduio)
        myanim=self.animation_concate(self.data)
        print('fps= ',myanim.fps)
        background=self.img2media(self.data)
        background.write_videofile("background_video.mp4", fps=myanim.fps)  # fps代表帧率，根据需要设置
        myanim.write_videofile("foreground_video.mp4", codec='libx264')
        self.background_conbine()
        result=self.add_voice(aduio)
        result.write_videofile(self.media_path, codec='libx264', audio_codec='aac')
        json_data = json.dumps(self.data)

    def work_live2d(self,data):
        scenes=data['scenes']
        self.parser2(scenes)
        print(data)

        #aduio=self.TTS(self.data,self.voice_src)
        userid=0
        module_dir = os.path.dirname(__file__)
        path0=os.path.join(module_dir, "webUI/static/users/user"+str(userid))
        path1 = os.path.join(module_dir, "Fast_Live2d\Samples\OpenGL\Demo\proj.win.cmake\\build\proj_msvc2022_x64_mt\\bin\Demo\Debug\Resources\data" )
        folder_path=os.path.join(module_dir, path1)
        rm = random.randint(1, 10000000)
        taskid = str(rm)
        audio_target_path=os.path.join(folder_path, 'task'+taskid+'.wav')

        data['audio_path']=audio_target_path
        data['taskid'] = taskid
        print("1111111111",data)
        aduio = self.TTS2(scenes,data,folder_path,audio_target_path)
        print(scenes)

        vedio_path=self.getVedio(data,taskid)
        target_path=path0+"/result"+taskid+".mp4"
        vedio_path = self.add_voice2(aduio,vedio_path,target_path)
        print(vedio_path)
        return vedio_path
        #json_data = json.dumps(self.data)


    def parser(self,doc):
        soup = BeautifulSoup(doc, 'html.parser')
        # 查找自定义标签
        #解析MEDIA系统
        media = soup.find('media')
        if 'path' in media.attrs:
            self.media_path = media['path']
            if'type' in media.attrs:
                self.media_type=media['type']
        else :
            raise Parseerror("Parse Media error")
        #解析动画系统
        animation = soup.find('animation')
        if 'src' in animation.attrs:
            self.animation_src = animation['src']
        else :
            raise Parseerror("Parse Animation error")

        # 解析声音系统
        voice = soup.find('voice')
        if 'src' in voice.attrs:
            self.voice_src = voice['src']
        else:
            raise Parseerror("Parse voice error")

        scenes = soup.find_all(['scenario'])
        for scene in scenes:
            background_src=''
            if 'background' in scene.attrs:
                background_src = scene['background']
                if(background_src[-4:]=="pptx"):
                    if 'slide' in scene.attrs:
                        background_src = self.ps.ppt2img(background_src,scene['slide'])
                    else:
                        raise Parseerror("Parse background_src error,for not slide index in pptx")
            else:
                raise Parseerror("Parse background_src error")
            anims=scene.find_all(['anim'])
            #print(anims)
            for anim in anims:
                #print(anim.text)
                anim_type=''
                if 'type' in anim.attrs:
                    anim_type = anim['type']
                else:
                    raise Parseerror("Parse anim_type error")
                clip = {'background': background_src, "speed": '', 'voice':self.voice_src,"anim": anim_type, 'text': anim.text,'duration':0}
                self.data.append(clip)
    def parser2(self,scenes):
        for scene in scenes:
            texts = scene['text'].strip().split('。')
            scene.pop('text')
            clips=[]
            for text in texts:
                if(text!=''):
                    text=text+'。'
                    clip = {'text': text, "expression": "", "motion": "", "duration": 0}
                    clips.append(clip)
            if(len(clips)==0):
                clip = {'text': '。', "expression": "", "motion": "", "duration": 0}
                clips.append(clip)
            scene["clips"]=clips

    def TTS(self, data, clone_voice):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        # Init TTS with the target model name
        # 使用xttx-v2模型进行语音合成
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        # print(tts.languages)
        # Run TTS
        # text:要合成语音的文本
        # speaker_wav：需要克隆的声音源
        # language：使用的语言类型
        # file_path：语音合成结果输出路径
        chunk_size = 80
        segment_audio_clips = []
        p= 0
        t = 0
        for clip in data:
            text0=clip['text'].split('。')
            print("克隆的文本为：",text0)
            p= t
            for text in text0:
                for i in range(0, len(text), chunk_size):
                    tts.tts_to_file(text=str(text)[i:i + chunk_size], speaker_wav=clone_voice, language="zh-cn",
                                    file_path=f"audio/speak{t}.wav")
                    t += 1
            audio_folder_path = "audio"
            audio_files = []
            for i in range(p, t):
                audio_files.append(f'audio/speak{i}.wav')
            audio_clips = []
            for audio_file in audio_files:
                audio_clip = AudioFileClip(audio_file)
                audio_clips.append(audio_clip)
            segment_audio_clip = concatenate_audioclips(audio_clips)
            clip['duration'] = segment_audio_clip.duration
            segment_audio_clips.append(segment_audio_clip)
        final_audio_clip = concatenate_audioclips(segment_audio_clips)
        print("音频总数=",t)
        final_audio_clip.write_audiofile("scenes_sounds.wav")
        return final_audio_clip

    def initTTS(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        # Init TTS with the target model name
        # 使用xttx-v2模型进行语音合成
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        return tts
    def TTS2(self,scenes,data,folder_path,target_path):

        # print(tts.languages)
        # Run TTS
        # text:要合成语音的文本
        # speaker_wav：需要克隆的声音源
        # language：使用的语言类型
        # file_path：语音合成结果输出路径

        voice_method=data['voice_method']
        t = 0
        last_end=0
        audio_files = []
        audio_clips = []
        for scene in scenes:
            module_dir = os.path.dirname(__file__)
            #voice="TTS/samples_zh-cn-sample.wav"
            if(voice_method=='0' or voice_method=='2'):
                data['voice']=os.path.join(module_dir,"TTS/samples_zh-cn-sample.wav")
            elif(voice_method=='1'):
                data['voice'] = os.path.join(module_dir,"TTS/广告男声.mp3")
            voice = data['voice']
            for clip in scene["clips"]:
                print("克隆的文本为：",clip['text'])
                text=clip['text']
                audio_path = folder_path + f"/speak{t}.wav"
                self.tts.tts_to_file(text=text, speaker_wav=voice, language="zh-cn",
                                        file_path=audio_path)
                t += 1
                #region 修剪音频以到达更好效果
                ''''''
                audio_clip = AudioFileClip(audio_path)
                crop_duration = audio_clip.duration % 0.04
                end_time = audio_clip.duration +0.04-crop_duration
                #end_time = audio_clip.duration
                # 裁剪音频
                #cropped_audio = audio_clip.subclip(0, end_time)
                # 如果提供了输出文件路径，则保存裁剪后的音频
                #cropped_audio.write_audiofile(clip['audio_path'])
                clip['duration']=end_time
                audio_clip.set_start(last_end)
                # 修剪音频，以得到更好的效果
                last_end=end_time
                #audio_files.append(audio_path)
                audio_clips.append(audio_clip)
        '''
        for audio_file in audio_files:
            audio_clip = AudioFileClip(audio_file)
            audio_clips.append(audio_clip)
        '''
        final_audio_clip = concatenate_audioclips(audio_clips)
        print("音频总数=",t)
        final_audio_clip.write_audiofile(target_path)
        return final_audio_clip

    '''
    scene = {'id': '0', "background": "/sora.jpg", "name": 'panda', "character": "/panda1.png",
             "clips": [{'text': 'text', "audio_path": "", "expression": "", "motion": "", "duration": 0}],
             "voice": '', "method": '', "width": 200, "height": 200, "x": 0, "y": 0}
    '''

    def getVedio(self,data,taskid):
        module_dir = os.path.dirname(__file__)
        userid = 0
        live2dpath = os.path.join(module_dir, "Fast_Live2d/Samples/OpenGL/Demo/proj.win.cmake/build/proj_msvc2022_x64_mt/bin/Demo/Debug/Resources/data")
        #live2dpath = os.path.join(module_dir,"Live2d/Samples/Resources/data")

        taskpath = live2dpath + "/task" + taskid + ".json"
        resultpath = os.path.join(module_dir, "webUI/static/users" + "/task" + taskid + ".mp4")
        #resultpath = os.path.join(module_dir, "Live2d/Samples/OpenGL/Demo/proj.win.cmake/build/proj_msvc2022_x64_mt/bin/Demo/Debug/output.mp4")
        with open(taskpath, 'w', encoding='utf-8') as file:
            # 将数据转换为JSON格式的字符串
            json_data = json.dumps(data, ensure_ascii=False, indent=4)
            # 写入文件xzxz
            file.write(json_data)
        print("成功写入")
        module_dir = os.path.dirname(__file__)
        path = os.path.join(module_dir,
                            "Fast_Live2d\Samples\OpenGL\Demo\proj.win.cmake\\build\proj_msvc2022_x64_mt\\bin\Demo\Debug\Demo.exe")
        # 或者，如果你需要获取输出，可以这样做：
        # 设置命令行参数
        cmd_args = [path,taskpath,resultpath]
        # 设置工作目录（如果需要）
        working_dir = os.path.join(module_dir,
                                   "Fast_Live2d\Samples\OpenGL\Demo\proj.win.cmake\\build\proj_msvc2022_x64_mt\\bin\Demo\Debug")
        # 调用EXE程序pyinstaller --onefile views.py
        process = subprocess.Popen(cmd_args, cwd=working_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # 读取标准输出和标准错误（如果需要）
        stdout, stderr = process.communicate()
        # 检查退出码
        if process.returncode != 0:
            print(f"EXE程序返回了错误代码 {process.returncode}")
            print(f"标准错误输出: {stderr.decode()}")
        else:
            print(f"EXE程序成功执行，输出: {stdout.decode()}")
        #process.wait()
        while True:
        # 检查文件是否存在
            if not os.path.exists(taskpath):
                break
            else:
            # 等待一段时间再次检查
                # 等待一段时间再次检查
                time.sleep(0.5)  # 每秒检查一次
        return resultpath


    def img2media(self,data):
        # 创建一个图片剪辑列表
        clips = [ImageClip(clip['background'], duration=clip['duration']) for clip in data]

        # 合并图片剪辑为视频
        final_clip = concatenate_videoclips(clips)
        return final_clip

    def animation_concate(self, data):

        animation = {'说话': self.animation_src+'/说话.mp4', '摇头': self.animation_src+'/摇头.mp4', '闭眼': self.animation_src+'/闭眼.mp4',
                     '点头': self.animation_src+'/点头.mp4', '惊呆': self.animation_src+'/惊呆.mp4'}
        # 视频文件列表
        video_files = ['animation/说话-4.mp4', 'animation/说话-4.mp4', 'animation/点头.mp4', 'animation/闭眼.mp4',
                       'animation/摇头.mp4', 'animation/说话-4.mp4', 'animation/说话-4.mp4']
        clips = []
        for clip in data:
            print(clip)
            segment = VideoFileClip(animation[(clip['anim'])])
            sem=VideoFileClip(animation[(clip['anim'])])
            for i in range(0, math.ceil(clip['duration'] / sem.duration)):
                segment = concatenate_videoclips([segment, sem])
            # 读取视频文件并转换为 VideoFileClip 对象
            clips.append(segment)
            print('clip.duration:',clip['duration'])
            print('animation.duration:',segment.duration)
            print(clips)

        # 使用 concatenate_videoclips 函数将视频片段连接在一起
        # 这里我们假设所有的视频片段都有相同的分辨率
        final_clip = concatenate_videoclips(clips)

        #final_clip.write_videofile("background_video.mp4", codec='libx264')
        return final_clip
        # 写入最终的视频文件

    def background_conbine(self):
        background_video = cv2.VideoCapture("background_video.mp4")
        foreground_video = cv2.VideoCapture("foreground_video.mp4")
        background_fps = background_video.get(cv2.CAP_PROP_FPS)
        background_size = (
        int(background_video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(background_video.get(cv2.CAP_PROP_FRAME_HEIGHT)))

        # 初始化视频写入器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        output_video = cv2.VideoWriter('background_conbine.mp4', fourcc, background_fps,
                                       background_size)
        #output_video2 = cv2.VideoWriter('background_conbine2.mp4', fourcc, background_fps,
         #                              background_size)
        while True:
            # 读取背景视频的帧
            ret_background, background_frame = background_video.read()
            if not ret_background:
                break

            # 读取前景视频的帧
            ret_foreground, foreground_frame = foreground_video.read()
            if not ret_foreground:
                break

            # 检查前景视频帧是否为空
            if foreground_frame is None:
                continue

            # 缩放前景视频帧
            # 这里我们将其缩小到原来的一半，你可以根据需要调整这些值
            scaled_foreground_frame = cv2.resize(foreground_frame,
                                                 (foreground_frame.shape[1] , foreground_frame.shape[0] ))
            x_offset = int(background_size[0]*0.2)
            y_offset = int(background_size[1]*0)
            copied_background_frame = np.copy(background_frame)
            h=min((background_size[1]-y_offset),scaled_foreground_frame.shape[0])
            w=min((background_size[0]-x_offset),scaled_foreground_frame.shape[1])
            #print("scaled_foreground_frame.shape",scaled_foreground_frame.shape)
            #print("background_size",background_size)
            #print("h", h)
            #print("w",w)
            # 将调整大小的前景视频帧插入到背景视频帧中
            background_frame[y_offset:y_offset +h,
            x_offset:x_offset + w] = scaled_foreground_frame[0:h,
            0:w]

            mask = cv2.inRange(background_frame, (0, 0, 0), (20, 20, 20))
            # mask_inv = cv2.bitwise_not(mask)
            # print(mask)
            bg_masked = cv2.bitwise_and(copied_background_frame, copied_background_frame, mask=mask)
            fused_frame = cv2.add(background_frame, bg_masked)
            # 将背景视频帧与缩放且居中的前景视频帧相加
            # 注意：OpenCV读取的图像是BGR格式，不是RGB，但相加操作是逐通道的，所以结果是一样的
            # fused_frame = cv2.add(background_frame, scaled_foreground_frame)
            # 显示或保存融合后的视频帧
            output_video.write(fused_frame)
            #output_video2.write(background_frame)
            # 如果你想实时查看效果，可以取消下面这行的注释
            # cv2.imshow('Fused Video', fused_frame)
            # 如果按下'q'键，则退出循环
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
        # 释放资源
        background_video.release()
        foreground_video.release()
        output_video.release()
        # 如果打开了窗口显示，也需要关闭窗口
        # cv2.destroyAllWindows()
    def add_voice(self,audio,vedio_path):
        # 加载视频文件
        video_clip = VideoFileClip(vedio_path)

        # 加载音频文件
        audio_clip = audio

        # 如果音频文件比视频长，截取与视频相同的长度
        if audio_clip.duration > video_clip.duration:
            audio_clip = audio_clip.subclip(0, video_clip.duration)

        # 如果音频文件比视频短，则重复音频以匹配视频长度
        # elif audio_clip.duration < video_clip.duration:
        #    audio_clip = audio_clip.fx(vfx.loop, duration=video_clip.duration)

        # 创建一个组合的视频片段，将视频和音频组合在一起
        final_clip = video_clip.set_audio(audio_clip)

        final_clip.write_videofile(vedio_path, codec='libx264',audio_codec='aac')
        return vedio_path
        # 写入最终的视频文件（包含音频）

    def add_voice2(self, audio, vedio_path,target_path):
        # 加载视频文件
        video_clip = VideoFileClip(vedio_path)

        # 加载音频文件
        audio_clip = audio

        # 如果音频文件比视频长，截取与视频相同的长度
        if audio_clip.duration > video_clip.duration:
            audio_clip = audio_clip.subclip(0, video_clip.duration)

        # 如果音频文件比视频短，则重复音频以匹配视频长度
        # elif audio_clip.duration < video_clip.duration:
        #    audio_clip = audio_clip.fx(vfx.loop, duration=video_clip.duration)

        # 创建一个组合的视频片段，将视频和音频组合在一起
        final_clip = video_clip.set_audio(audio_clip)
        print(final_clip.fps)
        final_clip.set_fps(25)
        final_clip.write_videofile(target_path, fps=25,codec='libx264', audio_codec='aac')
        return target_path
        # 写入最终的视频文件（包含音频）

    scenes = [{'id': '0', "background": "/sora.jpg", "name": 'panda', "character": "/panda1.png",
             "clips": [{'text': 'Sora能够创造出包含多个角色、特定动作类型以及与主题和背景相符的详细场景。这款模型不仅能理解用户的指令，还能洞察这些元素在现实世界中的表现。 Sora对语言有着深刻的理解，能够精准地捕捉到用户的需求，并创造出充满生命力、情感丰富的角色。此外，Sora还能在同一视频中创造出多个画面，同时保持角色和视觉风格的一致性。', "audio_path": "", "expression": "", "motion": "", "duration": 0}],
             "voice": '', "method": '', "width": 200, "height": 200, "x": 0, "y": 0}]

my_VM = Vmedia()
if __name__ == '__main__':
    module_dir = os.path.dirname(__file__)
    print(module_dir)

    #my_VM.work_live2d(scenes)


