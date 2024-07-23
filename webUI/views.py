import base64
import re

from flask import Flask, redirect, url_for, request, render_template, jsonify, send_file, send_from_directory
import json
import os
from flask_cors import CORS
from Vmedia import Vmedia, my_VM

#import Vmedia
# 传入__name__初始化一个Flask实例
#app = Flask(__name__)
app = Flask(__name__, static_folder='static')
# 使用 Flask-CORS 扩展添加 CORS 支持
cors = CORS(app, resources={r"/*": {"origins": "*"}})



# app.route装饰器映射URL和执行的函数。这个设置将根URL映射到了hello_world函数上
@app.route('/')
def home():
    return render_template('index.html')
#@app.route('/generate')
#def generate():
#    return render_template('index.html')
def natural_sort_key(s):
    # 使用正则表达式匹配数字，并返回元组，使得排序时先比较数字部分，再比较非数字部分
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def is_image_file_by_extension(filename):
    # 定义一些常见的图片扩展名
    image_extensions = {'.png', '.jpg', '.jpeg'}
    # 获取文件的扩展名
    extension = os.path.splitext(filename)[1].lower()
    # 检查扩展名是否在定义的集合中
    return extension in image_extensions
@app.route('/<path:filename>')
def serve_extra_file(filename):
    directory = os.path.join(app.root_path, 'static')  # 指定文件夹路径
    print(directory)
    return send_from_directory(directory, filename)
@app.route('/ppt2img', methods=['POST', 'GET'])
def ppt2img():
    data = request.headers
    print(data)
    #data = request.form.get('ppt')
    file = request.files['ppt']
    if(file.filename.endswith("pptx")==False):
        print( '不是PPTX文件' )
        return 0
    #f = open(os.path.dirname(__file__) + "/test.pptx", mode='w', encoding='utf-8')
    #f.write(data)
    userid=len(os.listdir(app.root_path + "\static\\users"))
    userpath=app.root_path + "\static\\users\\user"+str(userid)+"\\background"
    userpptpath = userpath+"\ppt2img.pptx"
    if os.path.exists(userpath):
        #os.makedirs(userpptpath)
        print(f"文件夹 '{userpath}' 存在")
    else:
        os.makedirs(userpath)

    print(userpptpath)
    file.save(userpptpath)

    folder =my_VM.ps.ppt2img_web(userpath,"\ppt2img.pptx")
    folder=folder.replace(app.root_path+'\static\\','')
    print('folder=',folder)
    folder_path = app.root_path+'\static\\'+folder  # 替换为你要访问的文件夹路径
    print('folder_path=', folder_path)
    images_data = []

    files = os.listdir(folder_path)
    print(files)
    # 使用自定义的排序键进行排序
    sorted_files = sorted(files, key=natural_sort_key)
    # 使用os.listdir获取文件夹中所有文件的列表
    for file in sorted_files:
        print("file=", file)
        #file
        # 确保它是一个文件而不是文件夹
        if is_image_file_by_extension(file):  # 只处理 JPG 和 PNG 图片
            image_path = os.path.join(folder, file)
            image_path = image_path.replace('\\', '/')
            images_data.append({
                'filename': file,
                'data': image_path
            })
    print(images_data)
    return jsonify(images_data),200,{"Content-Type":"application/json"}

@app.route('/addbackground', methods=['POST', 'GET'])
def addbackground():
    data = request.headers
    print(data)
    #data = request.form.get('ppt')
    file = request.files['background']
    print("文件是：",file)
    userbackgroundpath=""
    if(file.filename.endswith("png")==False and file.filename.endswith("jpg")==False and file.filename.endswith("jpeg")==False):
        print( '不是图片文件' )
        return 0
    userid =0
    userpath = app.root_path + "\static\\users\\user" + str(userid) + "\\background"
    if os.path.exists(userpath):
        #os.makedirs(userpptpath)
        print(f"文件夹 '{userpath}' 存在")
    else:
        os.makedirs(userpath)
    if (file.filename.endswith("png") == True ):
        userbackgroundpath=userpath+"\\background"+str(userid)+".png"
    elif(file.filename.endswith("jpg") == True ):
        userbackgroundpath = userpath+ "\\background" + str(userid) + ".jpg"
    else:
        userbackgroundpath = userpath+ "\\background" + str(userid) + ".jpeg"

    print(userbackgroundpath)
    file.save(userbackgroundpath)

    folder=userbackgroundpath.replace(app.root_path+'\static\\','')
    image_path = folder.replace('\\', '/')
    print('image_path=',image_path)
    images_data = []
    images_data.append({
        'filename': "background",
        'data': image_path
    })

    print(images_data)
    return jsonify(images_data),200,{"Content-Type":"application/json"}

@app.route('/addvoice', methods=['POST', 'GET'])
def addvoice():
    data = request.headers
    print(data)
    #data = request.form.get('ppt')
    file = request.files['voice']
    print("文件是：",file)
    uservoicepath=""
    if(file.filename.endswith("wav")==False and file.filename.endswith("mp3")==False and file.filename.endswith("aac")==False):
        print( '不是支持的音频文件' )
        return 0
    userid =0
    userpath = app.root_path + "\static\\users\\user" + str(userid) + "\\voice"
    if os.path.exists(userpath):
        #os.makedirs(userpptpath)
        print(f"文件夹 '{userpath}' 存在")
    else:
        os.makedirs(userpath)
    if (file.filename.endswith("wav") == True ):
        uservoicepath=userpath+"\\voice"+str(userid)+".wav"
    elif(file.filename.endswith("mp3") == True ):
        uservoicepath = userpath+ "\\voice" + str(userid) + ".mp3"
    else:
        uservoicepath = userpath+ "\\voice" + str(userid) + ".mp3"

    print(uservoicepath)
    file.save(uservoicepath)

    folder=uservoicepath.replace(app.root_path+'\static\\','')
    voice_path = folder.replace('\\', '/')
    print('voice_path=',voice_path)
    voice_data = []
    voice_data.append({
        'filename': "voice",
        'data': voice_path
    })

    print(voice_data)
    return jsonify(voice_data),200,{"Content-Type":"application/json"}

@app.route('/generate', methods=['POST', 'GET'])
def generate():
    try:
        data = request.json
        scenes=data["data"]["scenes"]
        data=data["data"]
        print(data)
        if(data['voice_method']=='3'):
            data['voice']=os.path.join(app.static_folder, data['voice'])
        for i in range(len(scenes)):
            scenes[i]['background']=os.path.join(app.static_folder, scenes[i]['background'])
        print(data)
        vvedio=my_VM.work_live2d(data)
        print(44444444)
        print(vvedio)
        video_path = os.path.join(app.static_folder, 'test_result.mp4')
        print(video_path)
        # 使用 send_file 发送文件
        # as_attachment=True 会使浏览器提示下载文件，而不是尝试播放它
        # 如果你想让浏览器直接播放视频，可以省略 as_attachment 参数或者设置为 False
        return send_file(vvedio, as_attachment=False, mimetype='video/mp4')
        # 在这里处理你的数据
        #return jsonify({'message': 'Data processed successfully.'})
    except json.JSONDecodeError:

        return jsonify({'error': 'Invalid JSON data.'}), 400
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400
if __name__ == '__main__':
    app.run(debug=False)
