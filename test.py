import re

s = '''
In May 2019, a new and astonishingly small version of the classic Sellier Kelly bag was unveiled at a private Hermès press preview, measuring just 5cm in size. While it may resemble a charm more than a functional bag, it is indeed a fully operational bag, complete with the iconic gold Kelly closure, which has been expertly miniaturized, right down to the stamping and fully lined interior. However, the absence of interior pockets and the silk wrapped handle and strap distinguish it from its larger counterparts. As with the full-sized Kellys, these micro mini bags are highly sought after and elusive at Hermès. This particular example, in Rose Sakura Tadelakt leather, is a store-fresh and exceptional collector's item that stands out from the rest.

Size: 5cm
Color: Rose Sakura
Collection: 2020, Y
Hardware: Palladium
Material: Tadelakt Leather
Condition: Store Fresh
'''

size_re = re.compile(r'Size: (.+)')
color_re = re.compile(r'Color: (.+)')
hardware_re = re.compile(r'Hardware: (.+)')
material_re = re.compile(r'Material: (.+)')

size = size_re.search(s).group(1)
color = color_re.search(s).group(1)
hardware = hardware_re.search(s).group(1)
material = material_re.search(s).group(1)

print(size, color, hardware, material)
