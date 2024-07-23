from pptx_tools import utils
import  os
class BackgroundProcess():
    def __init__(self):
        self.pptdict=dict()
        self.background=dict()


    def ppt2img(self,ppt_src,ppt_index):
        pptfile = os.getcwd()+'/'+ppt_src
        pptfile=pptfile.replace('\\','/')
        print(pptfile)
        if(pptfile not in self.pptdict.keys()):
            png_folder = os.getcwd()+'\ppt'+'\ppt'+str(len(self.pptdict))
            #png_folder = png_folder.replace('\\', '/')
            print(png_folder)
            self.pptdict[pptfile]=png_folder
            utils.save_pptx_as_png(png_folder, pptfile, overwrite_folder=True)
        img_src=self.pptdict[pptfile]+'/幻灯片'+str(ppt_index)+'.PNG'
        img_src = img_src.replace('\\', '/')
        print(img_src)
        return img_src
        #pptfile = r'C:\Users\Lenovo\Desktop\实验室\文本生成语音\media_proccess\ppt\sora.pptx'
        #png_folder = r'C:\Users\Lenovo\Desktop\实验室\文本生成语音\media_proccess\ppt'

    def ppt2img_web(self,ppt_src,ppt_target):
        pptfile = ppt_src+ppt_target
        pptfile=pptfile.replace('\\','/')
        print(pptfile)
        if(pptfile not in self.pptdict.keys()):
            pptfolder=ppt_src+"\ppt"+str(len(self.pptdict))
            #png_folder = os.path.dirname(__file__) +'\webUI\static\\'+ppt_target+'\ppt'+str(len(self.pptdict))
            #png_folder2=ppt_target+'\ppt'+str(len(self.pptdict))
            #png_folder = png_folder.replace('\\', '/')
            print(ppt_src)
            self.pptdict[pptfile]=pptfolder
            utils.save_pptx_as_png(pptfolder, pptfile, overwrite_folder=True)
            folder_path = pptfolder  # 替换为你要访问的文件夹路径
            print('folder_path=', folder_path)
            images_data = []
            # 使用os.listdir获取文件夹中所有文件的列表
            for file in os.listdir(folder_path):
                print("file=", file)
                # 确保它是一个文件而不是文件夹
                if file.endswith(".jpg") or file.endswith(".PNG"):  # 只处理 JPG 和 PNG 图片
                    image_path = os.path.join(folder_path, file)
                    image_path = image_path.replace('\\', '/')
                    self.background[image_path]=image_path
        return self.pptdict[pptfile]
        #pptfile = r'C:\Users\Lenovo\Desktop\实验室\文本生成语音\media_proccess\ppt\sora.pptx'
        #png_folder = r'C:\Users\Lenovo\Desktop\实验室\文本生成语音\media_proccess\ppt'



if __name__ == '__main__':
    ps=BackgroundProcess()
    #ps.ppt2img("ppt/sora.pptx",1)
    #print(os.getcwd() + '\ppt' + '\ppt' + '1')
    #print(ps.ppt2img_web(os.path.dirname(__file__) +'/webUI/VMedia/public/ppt/ppt2img.pptx',os.path.dirname(__file__) +"\webUI\VMedia\public\ppt"))
    folder = ps.ppt2img_web(os.path.dirname(__file__) + "/webUI/VMedia/public/ppt/ppt2img.pptx",
                                          "vmedia\ppt")
    print(folder)