from PIL import Image
src=Image.open("verbavia_premium.png").convert("RGB")

def extend_v(im,H):
    """pad to height H by repeating top/bottom edge rows (gradient is seamless there)"""
    w,h=im.size; out=Image.new("RGB",(w,H))
    top=(H-h)//2; bot=H-h-top
    if top: out.paste(im.crop((0,0,w,1)).resize((w,top),Image.NEAREST),(0,0))
    out.paste(im,(0,top))
    if bot: out.paste(im.crop((0,h-1,w,h)).resize((w,bot),Image.NEAREST),(0,top+h))
    return out

def extend_h(im,W):
    w,h=im.size; out=Image.new("RGB",(W,h))
    l=(W-w)//2; r=W-w-l
    if l: out.paste(im.crop((0,0,1,h)).resize((l,h),Image.NEAREST),(0,0))
    out.paste(im,(l,0))
    if r: out.paste(im.crop((w-1,0,w,h)).resize((r,h),Image.NEAREST),(l+w,0))
    return out

# story 1080x1920
extend_v(src,1920).save("verbavia_premium_story.png")
# square 1080x1080
sq=src.resize((864,1080),Image.LANCZOS)
extend_h(sq,1080).save("verbavia_premium_square.png")
print("variants saved")
