# Cuts the uploaded logo image into transparent pieces: logo.png, tulips_tr.png, tulips_bl.png
import numpy as np
from PIL import Image
src = np.asarray(Image.open('brand/logo_full.jpg').convert('RGB')).astype(float)
r, g, b = src[..., 0], src[..., 1], src[..., 2]
dark_green = (g > r + 15) & (r < 90) & (g < 150)
gold = (r > 120) & (r - b > 70) & (r >= g) & (g - b > 30)
logo_px = dark_green | gold

def feather(img, top=0, bottom=0):
    a = np.asarray(img).astype(float); h = a.shape[0]
    if top: a[:top, :, 3] *= np.linspace(0, 1, top)[:, None]
    if bottom: a[h-bottom:, :, 3] *= np.linspace(1, 0, bottom)[:, None]
    return Image.fromarray(a.astype(np.uint8), 'RGBA')

def unmultiply(rgb):
    a = np.clip((255 - rgb.min(axis=2) - 10) / 245 * 1.15, 0, 1)
    c = np.where(a[..., None] > 0, (rgb - (1 - a[..., None]) * 255) / np.maximum(a[..., None], 1e-3), 0)
    return Image.fromarray(np.dstack([np.clip(c, 0, 255), a * 255]).astype(np.uint8), 'RGBA')

# logo: crop and erase tulip pixels around the edges
L = src[330:880, 20:1240].copy(); lp = logo_px[330:880, 20:1240]
H, W = lp.shape
yy, xx = np.mgrid[0:H, 0:W]
tulip_zone = ((xx > 620) & (yy < 140)) | ((xx < 230) & (yy > 490)) | ((xx > 1030) & (yy < 170)) | ((xx > 970) & (yy < 96))
L[(xx > 970) & (yy < 96)] = 255
keep = dark_green[330:880, 20:1240] | (lp & (xx > 815) & (xx < 1010))
L[tulip_zone & ~keep] = 255
unmultiply(L).save('brand/logo.png')

# tulips: top-right and bottom-left clusters, soft edge where the logo was
T = src[0:416, 400:1254].copy(); T[330:, :60] = 255
feather(unmultiply(T), bottom=30).save('brand/tulips_tr.png')
feather(unmultiply(src[874:1254, 0:860].copy()), top=30).save('brand/tulips_bl.png')
