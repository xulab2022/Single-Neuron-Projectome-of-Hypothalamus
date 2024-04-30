
import pandas as pd
import numpy as np
import nrrd,cv2,glob,os
import matplotlib.pyplot as plt
import math,random
from PIL import Image
from tqdm import tqdm


class two_D_plot_AXon():
    # ba = BrainArea()

    def __init__(self):
        self.dfarea = pd.read_excel(r"D:\projectome\brain_areas.xlsx",index_col =0)
        self.templatefile,header = nrrd.read(r"D:\projectome\average_template_10_8bit.nrrd")
        print("area and brain infor load")
    def load_brain_area(self,area = "",nrrdpath = "",enlarge =2,bisite = True,bisite_threshold = 20):
        if nrrdpath != "":
            self.nrrdfile,header = nrrd.read(nrrdpath)
            print("%s file load"%area)
            IndexCube = np.where(self.nrrdfile==1)
            self.mean_DV = (IndexCube[1].max()+IndexCube[1].min())/2
            ML_left_min = IndexCube[2].min()
            ML_left_max = IndexCube[2][np.where(IndexCube[2] <=570)].max()
            ML_right_min = IndexCube[2][np.where(IndexCube[2] >=570)].min()
            ML_right_max = IndexCube[2].max()
            center = ML_right_min - ML_left_max
            print(center)
            if (center > bisite_threshold)|(bisite == False):
                self.mean_ML = (ML_left_max+ML_left_min)/2
                para_tmp = max((ML_left_max-ML_left_min),(IndexCube[1].max()-IndexCube[1].min()))
            else:
                self.mean_ML = (ML_right_max+ML_left_min)/2
                para_tmp = max((ML_right_max-ML_left_min),(IndexCube[1].max()-IndexCube[1].min()))

            # if para_tmp>400:
            #     self.para = para_tmp*0.6
            # else:
            self.para = para_tmp/2*enlarge
        else:
            areaID = self.dfarea.loc[self.dfarea.region == area].index.values[0]
            self.nrrdfile,header = nrrd.read(r"D:\projectome\allen-structure\structure_%d.nrrd"%areaID)
            print("%s file load"%area)
            IndexCube = np.where(self.nrrdfile==1)
            self.mean_DV = (IndexCube[1].max()+IndexCube[1].min())/2
            ML_left_min = IndexCube[2].min()
            ML_left_max = IndexCube[2][np.where(IndexCube[2] <=570)].max()
            ML_right_min = IndexCube[2][np.where(IndexCube[2] >=570)].min()
            ML_right_max = IndexCube[2].max()
            center = ML_right_min - ML_left_max
            print(center)
            if (center > bisite_threshold)|(bisite == False):
                self.mean_ML = (ML_left_max+ML_left_min)/2
                para_tmp = max((ML_left_max-ML_left_min),(IndexCube[1].max()-IndexCube[1].min()))
            else:
                self.mean_ML = (ML_right_max+ML_left_min)/2
                para_tmp = max((ML_right_max-ML_left_min),(IndexCube[1].max()-IndexCube[1].min()))
            # if para_tmp>400:
            #     self.para = para_tmp*0.6
            # else:
            self.para = para_tmp/2*enlarge



    def plot_neurons_slice(self,swcpath = "",print_slice =False,slice_cor = 0,swclist = [],normal= 20,savepath = "",linewith = 0.8,filename = "",color_list = [],scale_bar = True,bar_length = 500,bar_site = 0.9):
        color = ["magenta","yellow","cyan","m","g","b","gray"]
        IndexCube = np.where(self.nrrdfile>0)
        slice = math.ceil((IndexCube[0].min()+IndexCube[0].max())/2)+slice_cor
        if print_slice == True:
            print("the image is %d"%slice)
        if slice >1320:
            slice =1320
        image = self.templatefile[slice,:,:]
        # print(slice)
        contour = self.nrrdfile[slice,:,:]
        edges = cv2.Canny(contour,0,1)
        Index2 = np.where(edges==255)
        NumCube = len(Index2[1])
        for i in range(NumCube):
            image[Index2[0][i],Index2[1][i]] = 255
        ratio = 10

        if scale_bar == True:
            site_x_start = int(self.mean_ML+self.para*bar_site-bar_length/ratio)
            site_x_end = int(self.mean_ML+self.para*bar_site)
            site_y = int(self.mean_DV+self.para*bar_site)
            image[int(site_y-self.para/normal):site_y,site_x_start:site_x_end] = 180
            # image[site_y:int(site_y+self.para/320),site_x_start:site_x_end] = 255

        fig = plt.figure(figsize=(12,8),dpi=300)
        ax = fig.add_subplot(1,1,1)
        ax.imshow(image,cmap = 'gray')
        # for i,swc in enumerate(tqdm(swclist)):
        for i,swc in enumerate(swclist):
            # print(swc)
            dfneuron = pd.read_csv(os.path.join(swcpath,swc+".swc"),sep = " ",header=None)
            dfneuron.columns = ["ID","type","AP","DV","ML","R","father"]
            dfinarea = dfneuron.loc[(dfneuron.AP>= IndexCube[0].min()*10)&(dfneuron.AP<=IndexCube[0].max()*10),:]
            dfinarea.index = range(0,len(dfinarea)) 
            nodes = [0]
            for h in range(1,len(dfinarea)):
                if ((dfinarea.loc[h,"ID"]-dfinarea.loc[h-1,"ID"]) >1)|((dfinarea.loc[h,"ID"]-dfinarea.loc[h,"father"]) !=1):
                    nodes.append(h)
            if color_list == True:
                c = color[i]
            elif color_list == False:
                c = [random.random(),random.random(),random.random()]
            else:
                c = color_list[i]
                # print(c)
                # c = [random.random(),random.random(),random.random()]
            for j in range(len(nodes)):
                if j != len(nodes)-1:
                    x_p = (dfinarea.iloc[nodes[j]:nodes[j+1],:].ML.values)/10
                    y_p = (dfinarea.iloc[nodes[j]:nodes[j+1],:].DV.values)/10
                    ax.plot(x_p,y_p,linewidth=linewith,c=c,alpha=0.7)  
                else:
                    x_p = (dfinarea.iloc[nodes[j]:,:].ML.values)/10
                    y_p = (dfinarea.iloc[nodes[j]:,:].DV.values)/10
                    ax.plot(x_p,y_p,linewidth=linewith,c=c,alpha=0.7)

        # mean_DV = (IndexCube[1].max()+IndexCube[1].min())/2
        # # mean_ML = (570+IndexCube[2].min())/2
        # mean_ML1 = (570+IndexCube[2].min())/2
        # mean_ML2 = (IndexCube[2].max()+IndexCube[2].min())/2
        # if mean_ML2>300:
        #     mean_ML = mean_ML1
        #     para = max((570-IndexCube[2].min()),(IndexCube[1].max()-IndexCube[1].min()))*enlarge/2
        # else:
        #     mean_ML = mean_ML2
        #     para = max((IndexCube[2].max()-IndexCube[2].min()),(IndexCube[1].max()-IndexCube[1].min()))*enlarge/3
        # x_start = int(self.mean_ML-self.para)
        # x_end = int(self.mean_ML+self.para)
        # y_start= int(self.mean_DV+self.para)
        # y_end = int(self.mean_DV-self.para)
        # # ax.set_ylim(y_start,y_end)
        # # ax.set_xlim(x_start,x_end)
        ax.set_ylim(int(self.mean_DV+self.para),int(self.mean_DV-self.para))
        ax.set_xlim(int(self.mean_ML-self.para),int(self.mean_ML+self.para))
        plt.axis('off')
        plt.savefig(os.path.join(savepath,filename+".jpg"))
        plt.close()


    def plot_neurons_region(self,swcpath = "",swclist = [],enlarge= 2,normal =20,savepath = "",filename = "",color_list = ["r","g","b","c","m","y"],scale_bar = True,bar_length = 500,bar_site = 0.9):

        def get_wendu_type(x):
            loc = self.nrrdfile[int(x.AP/10),int(x.DV/10),int(x.ML/10)]
            return loc

        IndexCube = np.where(self.nrrdfile==1)
        slice = math.ceil((IndexCube[0].min()+IndexCube[0].max())/2)

        mean_DV = (IndexCube[1].max()+IndexCube[1].min())/2
        # mean_ML = (570+IndexCube[2].min())/2
        mean_ML1 = (570+IndexCube[2].min())/2
        mean_ML2 = (IndexCube[2].max()+IndexCube[2].min())/2
        if mean_ML2>570:
            mean_ML = mean_ML1
            para = max((570-IndexCube[2].min()),(IndexCube[1].max()-IndexCube[1].min()))*enlarge/2
        else:
            mean_ML = mean_ML2
            para = max((IndexCube[2].max()-IndexCube[2].min()),(IndexCube[1].max()-IndexCube[1].min()))*enlarge/3
        # para = max((570-IndexCube[2].min()),(IndexCube[1].max()-IndexCube[1].min()))*enlarge
        image = self.templatefile[int(mean_DV-para):int(mean_DV+para),int(mean_ML-para):int(mean_ML+para)]
        contour = self.nrrdfile[int(mean_DV-para):int(mean_DV+para),int(mean_ML-para):int(mean_ML+para)]
        edges = cv2.Canny(contour,0,1)
        Index2 = np.where(edges==255)
        NumCube = len(Index2[1])
        for i in range(NumCube):
            image[Index2[0][i],Index2[1][i]] = 255
        
        ratio = 10

        if scale_bar == True:
            site_x_start = int(self.mean_ML+self.para*bar_site-bar_length/ratio)
            site_x_end = int(self.mean_ML+self.para*bar_site)
            site_y = int(self.mean_DV+self.para*bar_site)
            image[int(site_y-self.para/normal):site_y,site_x_start:site_x_end] = 180
            # image[site_y:int(site_y+self.para/320),site_x_start:site_x_end] = 255



        fig = plt.figure(figsize=(8,8),dpi=300)
        ax = fig.add_subplot(1,1,1)
        # image = templatefile[:,:]
        ax.imshow(image,cmap = 'gray')
        for i,swc in enumerate(swclist):
            dfneuron = pd.read_csv(os.path.join(swcpath,swc+".swc"),sep = " ",header=None)
            dfneuron.columns = ["ID","type","AP","DV","ML","R","father"]
            dfneuron.loc[:, "In_area"] = dfneuron.apply(get_wendu_type, axis=1)
            dfinarea = dfneuron.loc[dfneuron.In_area == 1]
            dfinarea.index = range(0,len(dfinarea)) 
            nodes = [0]
            xlsname = swc.split("\\")[-1].split(".")[0]
            # dfinarea.to_excel(os.path.join(savepath,xlsname+".xlsx"))
            for h in range(1,len(dfinarea)):
                if ((dfinarea.loc[h,"ID"]-dfinarea.loc[h-1,"ID"]) >1)|((dfinarea.loc[h,"ID"]-dfinarea.loc[h,"father"]) !=1):
                    nodes.append(h)
            x_nor = mean_ML-para
            y_nor = mean_DV-para
            for j in range(len(nodes)):
                if j != len(nodes)-1:
                    ax.plot(dfinarea.iloc[nodes[j]:nodes[j+1],:].ML.values/10-x_nor,dfinarea.iloc[nodes[j]:nodes[j+1],:].DV.values/10-y_nor,linewidth=0.4,c=color_list[i])
                else:
                    ax.plot(dfinarea.iloc[nodes[j]:,:].ML.values/10-x_nor,dfinarea.iloc[nodes[j]:,:].DV.values/10-y_nor,linewidth=0.4,c=color_list[i])

        plt.axis('off')
        # plt.gca().xaxis.set_major_locator(plt.NullLocator())
        # plt.gca().yaxis.set_major_locator(plt.NullLocator())
        plt.savefig(os.path.join(savepath,filename+".jpg"))
        plt.close()

    def plot_neurons_slice_brain(self,space = 500,figsize = (8,8),color_list = [],whole_brain = False,swcpath = "",swclist = [],savepath = "",linewith = 0.6,filename = "",crop = True,normal=20,scale_bar = True,bar_length = 500,bar_site = 0.9):
        
        if whole_brain == True:
            IndexCube = np.where(self.nrrdfile==0)
        else:
            IndexCube = np.where(self.nrrdfile>=1)

        slice_length = IndexCube[0].max()-IndexCube[0].min()
        spacenew = space/10
        slice_number = math.ceil(slice_length/spacenew)
        # print(slice_number)

        for sli in range(slice_number):
            start = IndexCube[0].min()
            slice = int(start+(sli+0.5)*spacenew)
            image = self.templatefile[slice,:,:]
            contour = self.nrrdfile[slice,:,:]
            edges = cv2.Canny(contour,0,1)
            Index2 = np.where(edges==255)
            NumCube = len(Index2[1])
            for i in range(NumCube):
                image[Index2[0][i],Index2[1][i]] = 255
            ratio = 10
            if scale_bar == True:
                site_x_start = int(self.mean_ML+self.para*bar_site-bar_length/ratio)
                site_x_end = int(self.mean_ML+self.para*bar_site)
                site_y = int(self.mean_DV+self.para*bar_site)
                image[int(site_y-self.para/normal):site_y,site_x_start:site_x_end] = 180
                # image[site_y:int(site_y+self.para/320),site_x_start:site_x_end] = 255        
            fig = plt.figure(figsize=figsize,dpi=300)
            ax = fig.add_subplot(1,1,1)
            # image = templatefile[:,:]
            ax.imshow(image,cmap = 'gray')
            # print("see")
            for i,swc in enumerate(swclist):
                # print(swc)
                dfneuron = pd.read_csv(os.path.join(swcpath,swc+".swc"),sep = " ",header=None)
                dfneuron.columns = ["ID","type","AP","DV","ML","R","father"]
                
                dfinarea = dfneuron.loc[(dfneuron.AP>=(start*10+sli*space))&(dfneuron.AP<=(start*10+(sli+1)*space)),:]
                dfinarea.index = range(0,len(dfinarea)) 
                nodes = [0]
                for h in range(1,len(dfinarea)):
                    if ((dfinarea.loc[h,"ID"]-dfinarea.loc[h-1,"ID"]) >1)|((dfinarea.loc[h,"ID"]-dfinarea.loc[h,"father"]) !=1):
                        nodes.append(h)
                # c = [random.random(),random.random(),random.random()]
                for j in range(len(nodes)):
                    if j != len(nodes)-1:
                        x_p = (dfinarea.iloc[nodes[j]:nodes[j+1],:].ML.values)/10
                        y_p = (dfinarea.iloc[nodes[j]:nodes[j+1],:].DV.values)/10
                        if type(swclist) == dict:
                            ax.plot(x_p,y_p,linewidth=linewith,c=swclist[swc])
                        else:
                            ax.plot(x_p,y_p,linewidth=linewith,c=color_list[i])  
                    else:
                        x_p = (dfinarea.iloc[nodes[j]:,:].ML.values)/10
                        y_p = (dfinarea.iloc[nodes[j]:,:].DV.values)/10
                        if type(swclist) == dict:
                            ax.plot(x_p,y_p,linewidth=linewith,c=swclist[swc])
                        else:
                            ax.plot(x_p,y_p,linewidth=linewith,c=color_list[i])  
            if crop == True:
                # mean_DV = (IndexCube[1].max()+IndexCube[1].min())/2
                # # mean_ML = (570+IndexCube[2].min())/2
                # mean_ML1 = (570+IndexCube[2].min())/2
                # mean_ML2 = (IndexCube[2].max()+IndexCube[2].min())/2
                # if mean_ML2>570:
                #     mean_ML = mean_ML1
                #     para = max((570-IndexCube[2].min()),(IndexCube[1].max()-IndexCube[1].min()))*enlarge/2
                # else:
                #     mean_ML = mean_ML2
                #     para = max((IndexCube[2].max()-IndexCube[2].min()),(IndexCube[1].max()-IndexCube[1].min()))*enlarge/2
                # ax.set_ylim(int(self.mean_DV-self.para),int(self.mean_DV+self.para))
                # ax.set_xlim(int(self.mean_ML+self.para),int(self.mean_ML-self.para))
                ax.set_ylim(int(self.mean_DV+self.para),int(self.mean_DV-self.para))
                ax.set_xlim(int(self.mean_ML+self.para),int(self.mean_ML-self.para))
        
            plt.axis('off')
            # plt.gca().xaxis.set_major_locator(plt.NullLocator())
            # plt.gca().yaxis.set_major_locator(plt.NullLocator())
            plt.savefig(os.path.join(savepath,filename+"_%s.jpg"%sli))
            plt.close()

    def plot_neurons_slice_whole_brain(self,space = 500,ranges = [0,1],soma_color="white",figsize = (8,8),color_list = [],swcpath = "",swclist = [],savepath = "",linewith = 0.6,filename = "",crop = True,normal=20,scale_bar = True,bar_length = 500,bar_site = 0.9):
        spacenew = space/10
        wholerange = self.templatefile.shape[0]
        # print(wholerange)
        # print(spacenew)
        for sli in tqdm(range(int(ranges[0]*wholerange),int(ranges[1]*wholerange),int(spacenew))):
            slice = int(sli+0.5*spacenew)
            image = self.templatefile[slice,:,:]
            contour = self.nrrdfile[slice,:,:]
            edges = cv2.Canny(contour,0,1)
            Index2 = np.where(edges==255)
            NumCube = len(Index2[1])
            for i in range(NumCube):
                image[Index2[0][i],Index2[1][i]] = 255
            ratio = 10

            if scale_bar == True:
                site_x_start = int(self.mean_ML+self.para*bar_site-bar_length/ratio)
                site_x_end = int(self.mean_ML+self.para*bar_site)
                site_y = int(self.mean_DV+self.para*bar_site)
                image[int(site_y-self.para/normal):site_y,site_x_start:site_x_end] = 180
                # image[site_y:int(site_y+self.para/320),site_x_start:site_x_end] = 255        
            fig = plt.figure(figsize=figsize,dpi=300)
            ax = fig.add_subplot(1,1,1)
            # image = templatefile[:,:]
            ax.imshow(image,cmap = 'gray')
            # print("see")
            for i,swc in enumerate(swclist):
                # print(swc)
                dfneuron = pd.read_csv(os.path.join(swcpath,swc+".swc"),sep = " ",header=None)
                dfneuron.columns = ["ID","type","AP","DV","ML","R","father"]
                
                dfinarea = dfneuron.loc[(dfneuron.AP>=(sli*10))&(dfneuron.AP<=(sli*10+space*1.2)),:]
                dfinarea.index = range(0,len(dfinarea)) 
                nodes = [0]
                for h in range(1,len(dfinarea)):
                    if ((dfinarea.loc[h,"ID"]-dfinarea.loc[h-1,"ID"]) >1)|((dfinarea.loc[h,"ID"]-dfinarea.loc[h,"father"]) !=1):
                        nodes.append(h)
                # c = [random.random(),random.random(),random.random()]
                for j in range(len(nodes)):
                    if j != len(nodes)-1:
                        x_p = (dfinarea.iloc[nodes[j]:nodes[j+1],:].ML.values)/10
                        y_p = (dfinarea.iloc[nodes[j]:nodes[j+1],:].DV.values)/10
                        if type(swclist) == dict:
                            ax.plot(x_p,y_p,linewidth=linewith,c=swclist[swc])
                        else:
                            ax.plot(x_p,y_p,linewidth=linewith,c=color_list[i])  
                    else:
                        x_p = (dfinarea.iloc[nodes[j]:,:].ML.values)/10
                        y_p = (dfinarea.iloc[nodes[j]:,:].DV.values)/10
                        if type(swclist) == dict:
                            ax.plot(x_p,y_p,linewidth=linewith,c=swclist[swc])
                        else:
                            ax.plot(x_p,y_p,linewidth=linewith,c=color_list[i]) 

                soma_AP = dfneuron.loc[dfneuron.type ==1].AP.values[0]
                if (soma_AP>=(sli*10))&(soma_AP<(sli*10+space*1)):
                    x_s = dfneuron.loc[dfneuron.type ==1].ML.values[0]/10
                    y_s = dfneuron.loc[dfneuron.type ==1].DV.values[0]/10
                    ax.scatter(x_s,y_s,s=4,c=soma_color,zorder=55)


                
            if crop == True:
                ax.set_ylim(int(self.mean_DV+self.para),int(self.mean_DV-self.para))
                ax.set_xlim(int(self.mean_ML+self.para),int(self.mean_ML-self.para))
        
            plt.axis('off')
            plt.savefig(os.path.join(savepath,filename+"_%s.jpg"%sli))
            plt.close()



    def crop_neurons(self,filelist = "",savedir = "",para = (250,250,1900,1900),mirrow = True):
        for file in filelist:
            filetmp = Image.open(file).crop(para)
            filename = file.split("\\")[-1]
            if mirrow == True:
                filetmp = filetmp.transpose(Image.FLIP_LEFT_RIGHT)
            filetmp.save(os.path.join(savedir,filename))
            filetmp.close()


    def load_brain_area_sagittal(self,area = "",nrrdpath = "",enlarge =2,bisite = True,bisite_threshold = 20):
        if nrrdpath != "":
            self.nrrdfile,header = nrrd.read(nrrdpath)
            # print("%s file load"%area)
            IndexCube = np.where(self.nrrdfile[:,:,571]>=1)
            self.DV_min = IndexCube[1].min()
            self.DV_max = IndexCube[1].max()
            self.mean_DV = (self.DV_max+self.DV_min)/2

            self.AP_min = IndexCube[0].min()
            self.AP_max = IndexCube[0].max()
            self.mean_AP = (self.AP_max+self.AP_min)/2
            para_tmp = max((self.AP_max-self.AP_min),(self.DV_max-self.DV_min))
            if para_tmp>400:
                self.para = para_tmp*0.6
            else:
                self.para = para_tmp/2*enlarge
            
        else:
            areaID = self.dfarea.loc[self.dfarea.region == area].index.values[0]
            self.nrrdfile,header = nrrd.read(r"D:\projectome\allen-structure\structure_%d.nrrd"%areaID)
            print("%s file load"%area)
            IndexCube = np.where(self.nrrdfile[:,:,571]==1)
            self.DV_min = IndexCube[1].min()
            self.DV_max = IndexCube[1].max()
            self.mean_DV = (self.DV_max+self.DV_min)/2

            self.AP_min = IndexCube[0].min()
            self.AP_max = IndexCube[0].max()
            self.mean_AP = (self.AP_max+self.AP_min)/2
            para_tmp = max((self.AP_max-self.AP_min),(self.DV_max-self.DV_min))
            if para_tmp>400:
                self.para = para_tmp*0.6
            else:
                self.para = para_tmp/2*enlarge



    def plot_neurons_slice_sagittal(self,swcpath = "",slice_cor = 0,swclist = [],Crop = True,normal= 20,savepath = "",linewith = 0.6,filename = "",color_list = ["r","g","b","c","m","y"],scale_bar = True,bar_length = 500,bar_site = 0.9):
        color = ["magenta","yellow","cyan","m","g","b","gray"]
        IndexCube = np.where(self.nrrdfile[:,:,0:571]>0)
        slice = math.ceil((IndexCube[2].min()+IndexCube[2].max())/2)+slice_cor
        # print(slice)
        image = self.templatefile[:,:,slice]
        contour = self.nrrdfile[:,:,slice]
        edges = cv2.Canny(contour,0,1)
        Index2 = np.where(edges==255)
        NumCube = len(Index2[1])
        
        for i in range(NumCube):
            image[Index2[0][i],Index2[1][i]] = 255
        ratio = 10

        if scale_bar == True:
            # print(normal)
            
            site_x_start = int(self.mean_AP+self.para*bar_site-bar_length/ratio)
            site_x_end = int(self.mean_AP+self.para*bar_site)
            site_y = int(self.mean_DV+self.para*bar_site)
            image[site_x_start:site_x_end,int(site_y-self.para/normal):site_y] = 180
            # print(int(site_y-self.para/normal))
            # image[site_y:int(site_y+self.para/320),site_x_start:site_x_end] = 255

        fig = plt.figure(figsize=(12,8),dpi=300)
        ax = fig.add_subplot(1,1,1)
        ax.imshow(image,cmap = 'gray')
        for i,swc in enumerate(tqdm(swclist)):
            # print(swc)
            dfneuron = pd.read_csv(os.path.join(swcpath,swc+".swc"),sep = " ",header=None)
            dfneuron.columns = ["ID","type","AP","DV","ML","R","father"]
            dfinarea = dfneuron.loc[(dfneuron.ML>= IndexCube[2].min()*10)&(dfneuron.ML<=IndexCube[2].max()*10),:]
            dfinarea.index = range(0,len(dfinarea)) 
            nodes = [0]
            for h in range(1,len(dfinarea)):
                if ((dfinarea.loc[h,"ID"]-dfinarea.loc[h-1,"ID"]) >1)|((dfinarea.loc[h,"ID"]-dfinarea.loc[h,"father"]) !=1):
                    nodes.append(h)
            if color_list == True:
                c = color[i]
            else:
                c = [random.random(),random.random(),random.random()]
            for j in range(len(nodes)):
                if j != len(nodes)-1:
                    x_p = (dfinarea.iloc[nodes[j]:nodes[j+1],:].AP.values)/10
                    y_p = (dfinarea.iloc[nodes[j]:nodes[j+1],:].DV.values)/10
                    ax.plot(y_p,x_p,linewidth=linewith,c=c,alpha=0.7)  
                else:
                    x_p = (dfinarea.iloc[nodes[j]:,:].AP.values)/10
                    y_p = (dfinarea.iloc[nodes[j]:,:].DV.values)/10
                    ax.plot(y_p,x_p,linewidth=linewith,c=c,alpha=0.7)
        if Crop == True:
            ax.set_xlim(int(self.mean_DV+self.para),int(self.mean_DV-self.para))
            ax.set_ylim(int(self.mean_AP-self.para),int(self.mean_AP+self.para))
        plt.axis('off')
        plt.savefig(os.path.join(savepath,"cluster_"+filename+".jpg"))
        plt.close()

    def plot_neurons_slice_neuron(self,space = 500,figsize = (11.4,8),swcfile = "",savepath = "",linewith = 1,soma_color = "hotpink",axon_color="orange",filename = "",somasize=30,crop = True,normal=20,scale_bar = True,bar_length = 500,bar_site = 0.9):
        dfneuron = pd.read_csv(swcfile,sep = " ",header=None)
        dfneuron.columns = ["ID","type","AP","DV","ML","R","father"]
        # IndexCube = np.where(self.nrrdfile>=1)
        slice_length = dfneuron.AP.max()/10-dfneuron.AP.min()/10
        spacenew = space/10
        slice_number = math.ceil(slice_length/spacenew)
        soma_AP = dfneuron.loc[dfneuron.type ==1].AP.values[0]
        # print(slice_number)

        for sli in range(slice_number):
            start = dfneuron.AP.min()/10
            slice = int(start+(sli+0.5)*spacenew)

            if slice <1320:

                image = self.templatefile[slice,:,:]
                contour = self.nrrdfile[slice,:,:]
                edges = cv2.Canny(contour,0,1)
                Index2 = np.where(edges==255)
                NumCube = len(Index2[1])
                if NumCube>0:
                    for i in range(NumCube):
                        image[Index2[0][i],Index2[1][i]] = 255
                    ratio = 10

                # if scale_bar == True:
                #     site_x_start = int(self.mean_ML+self.para*bar_site-bar_length/ratio)
                #     site_x_end = int(self.mean_ML+self.para*bar_site)
                #     site_y = int(self.mean_DV+self.para*bar_site)
                #     image[int(site_y-self.para/normal):site_y,site_x_start:site_x_end] = 180
            
                fig = plt.figure(figsize=figsize,dpi=300)
                ax = fig.add_subplot(1,1,1)
                # image = templatefile[:,:]
                ax.imshow(image,cmap = 'gray')
                # print("see")
                

                    
                dfinarea = dfneuron.loc[(dfneuron.AP>=(start*10+sli*space))&(dfneuron.AP<=(start*10+(sli+1)*space)),:]
                dfinarea.index = range(0,len(dfinarea)) 
                nodes = [0]
                for h in range(1,len(dfinarea)):
                    if ((dfinarea.loc[h,"ID"]-dfinarea.loc[h-1,"ID"]) >1)|((dfinarea.loc[h,"ID"]-dfinarea.loc[h,"father"]) !=1):
                        nodes.append(h)
                # c = [random.random(),random.random(),random.random()]
                for j in range(len(nodes)):
                    if j != len(nodes)-1:
                        x_p = (dfinarea.iloc[nodes[j]:nodes[j+1],:].ML.values)/10
                        y_p = (dfinarea.iloc[nodes[j]:nodes[j+1],:].DV.values)/10
                        ax.plot(x_p,y_p,linewidth=linewith,c=axon_color,zorder=1)  
                    else:
                        x_p = (dfinarea.iloc[nodes[j]:,:].ML.values)/10
                        y_p = (dfinarea.iloc[nodes[j]:,:].DV.values)/10
                        ax.plot(x_p,y_p,linewidth=linewith,c=axon_color,zorder=1)

                if (soma_AP>=(start*10+sli*space))&(soma_AP<(start*10+(sli+1)*space)):
                    x_s = dfneuron.loc[dfneuron.type ==1].ML.values[0]/10
                    y_s = dfneuron.loc[dfneuron.type ==1].DV.values[0]/10
                    ax.scatter(x_s,y_s,s=somasize,c=soma_color,zorder=2)
                    
                # if crop == True:
                #     ax.set_ylim(int(self.mean_DV+self.para),int(self.mean_DV-self.para))
                #     ax.set_xlim(int(self.mean_ML+self.para),int(self.mean_ML-self.para))
                allabel = int((start*10+sli*space)/100)
                plt.axis('off')
                plt.savefig(os.path.join(savepath,filename+"_%s.jpg"%allabel))
                plt.close()

    # def plot_neurons_slice_brain(self,space = 500,figsize = (11.4,8),swcfile = "",savepath = "",linewith = 0.6,soma_color = "blue",axon_color="red",filename = "",crop = True,normal=20,scale_bar = True,bar_length = 500,bar_site = 0.9):
    def plot_neurons_slice_neuron_siggtial(self,figsize = (8,13.2),swcfile = "",savepath = "",linewith = 0.6,soma_color = "blue",axon_color="red",somasize = 30,filename = "",crop = True,normal=20,scale_bar = True,bar_length = 500,bar_site = 0.9):
        dfneuron = pd.read_csv(swcfile,sep = " ",header=None)
        dfneuron.columns = ["ID","type","AP","DV","ML","R","father"]
        # IndexCube = np.where(nrrdfile>=1)
        # # IndexCube = np.where(self.nrrdfile>=1)
        # slice_length = dfneuron.AP.max()-dfneuron.AP.min()
        # spacenew = space/10
        # slice_number = math.ceil(slice_length/spacenew)
        # soma_AP = dfneuron.loc[dfneuron.type ==1].AP.values[0]
        # print(slice_number)
        image = self.templatefile[:,:,570]

        fig = plt.figure(figsize=figsize,dpi=300)
        ax = fig.add_subplot(1,1,1)
                # image = templatefile[:,:]
        ax.imshow(image,cmap = 'gray')


        x_s = dfneuron.loc[dfneuron.type ==1].DV.values[0]/10
        y_s = dfneuron.loc[dfneuron.type ==1].AP.values[0]/10
        ax.scatter(x_s,y_s,s=somasize,c=soma_color)
        

        dfinarea = dfneuron

        nodes = [0]
        for h in range(1,len(dfinarea)):
            if ((dfinarea.loc[h,"ID"]-dfinarea.loc[h-1,"ID"]) >1)|((dfinarea.loc[h,"ID"]-dfinarea.loc[h,"father"]) !=1):
                nodes.append(h)
        # c = [random.random(),random.random(),random.random()]
        for j in range(len(nodes)):
            if j != len(nodes)-1:
                x_p = (dfinarea.iloc[nodes[j]:nodes[j+1],:].DV.values)/10
                y_p = (dfinarea.iloc[nodes[j]:nodes[j+1],:].AP.values)/10
                ax.plot(x_p,y_p,linewidth=linewith,c=axon_color)  
            else:
                x_p = (dfinarea.iloc[nodes[j]:,:].DV.values)/10
                y_p = (dfinarea.iloc[nodes[j]:,:].AP.values)/10
                ax.plot(x_p,y_p,linewidth=linewith,c=axon_color)



        plt.axis('off')

        # plt.gca().xaxis.set_major_locator(plt.NullLocator())
        # plt.gca().yaxis.set_major_locator(plt.NullLocator())
        plt.savefig(os.path.join(savepath,filename+".jpg"))
        plt.close()


    



