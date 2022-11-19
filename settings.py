import simplified_pygame
DEFAULT_COLORS={
    'background':[230,230,230],
    'well':[255,255,255],
    '-':[50,50,50],
    '0':[204,48,48],
    'L':[0,200,0],
    'j':[0,0,200],
    's':[183,157,25],
    'r':[0,150,150],
    'T':[175,51,165]}
VAN_GOGH_COLORS={
    'background':[255,233,134],
    'well':[32,43,51],
    '-':[175,164,71],
    '0':[147,57,23],
    'L':[130,174,27],
    'j':[85,100,112],
    's':[140,104,14],
    'r':[179,170,123],
    'T':[175,187,181]}
MILLAIS_COLORS={
    'background':[100,130,80],
    'well':[59,29,12],
    '-':[159,169,30],
    '0':[146,27,8],
    'L':[16,119,49],
    'j':[47,57,123],
    's':[129,137,44],
    'r':[228,186,145],
    'T':[153,121,66]}
LEONARDO_COLORS={
    'background':[250,157,136],
    'well':[169,171,137],
    '-':[4,0,15],
    '0':[123,51,29],
    'L':[171,122,56],
    'j':[85,100,112],
    's':[140,104,14],
    'r':[216,174,88],
    'T':[63,10,45]}
MONDRIAN_COLORS={
    'background': [198,171,214],
    'well': [249, 249, 249],
    '-': [4, 0, 15],
    '0': [244, 15, 123],
    'L': [13, 190, 56],
    'j': [13, 127, 190],
    's': [224, 194, 22],
    'r': [155, 155, 160],
    'T': [190, 13, 123]}

KLIMT_COLORS={
    'background':[200,160,100],
    'well':[153,100,17],
    '-':[40,29,33],
    '0':[180,53,4],
    'L':[114,179,148],
    'j':[24,20,81],
    's':[215,120,106],
    'r':[239,215,192],
    'T':[111,77,147]}
SAVED_SETTINGS=simplified_pygame.DataFile(
    'settings',
    w=1200,
    h=800,
    wasd=False,
    arrows=True,
    controller=True,
    mouse=False,
    volume=0.5,
    color_scheme=DEFAULT_COLORS,
    shadow=False,
    bleed=True,
    letters=simplified_pygame.WASD_AS_ARROWS,
    randomness='fair random',
)
ACTIVE_SETTINGS = {'color_scheme': {}}
ACTIVE_SETTINGS['color_scheme'].update(SAVED_SETTINGS['color_scheme'])
ACTIVE_SETTINGS['bleed'] = SAVED_SETTINGS['bleed']
#ACTIVE_SETTINGS={
#'color_scheme':{
#   'background':[230,230,230],
#   'well':[255,255,255],
#   '-':[50,50,50],
#   '0':[204,48,48],
#   'L':[0,200,0],
#   'j':[0,0,200],
#   's':[183,157,25],
#   'r':[0,150,150],
#   'T':[175,51,165]},
#   'bleed':True}
