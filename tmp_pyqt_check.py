from PyQt6.QtCore import Qt
print('has_AA_EnableHighDpiScaling', hasattr(Qt, 'AA_EnableHighDpiScaling'))
print('has_AA_UseHighDpiPixmaps', hasattr(Qt, 'AA_UseHighDpiPixmaps'))
print('AA attrs:', [x for x in dir(Qt) if x.startswith('AA_')])
