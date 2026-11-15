from lib.iflapp_reader import IflappReader

reader = input("dir?")
reader = IflappReader(reader)
print(reader.summary())
reader.export_assets(f"./salida")