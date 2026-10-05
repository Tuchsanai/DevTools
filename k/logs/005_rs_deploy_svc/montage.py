import sys
from PIL import Image
out, files = sys.argv[1], sys.argv[2:]
W,H=900,600
im=Image.new('RGB',(W*2,H*((len(files)+1)//2)),'white')
for k,f in enumerate(files):
    t=Image.open(f).convert('RGB').resize((W,H))
    im.paste(t,((k%2)*W,(k//2)*H))
im.save(out)
