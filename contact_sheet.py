import sys,os
from PIL import Image
d=sys.argv[1]; src='out/'+d; fs=sorted(f for f in os.listdir(src) if f.endswith('.png'))
w,h=360,480; cols=4; rows=(len(fs)+cols-1)//cols
sh=Image.new('RGB',(cols*w+(cols+1)*20,rows*h+(rows+1)*20),(200,200,200))
for i,f in enumerate(fs):
    im=Image.open(os.path.join(src,f)).convert('RGB'); assert im.size==(1080,1440),f
    sh.paste(im.resize((w,h),Image.LANCZOS),(20+(i%cols)*(w+20),20+(i//cols)*(h+20)))
sh.save('contact_%s.png'%d); print(sh.size)
