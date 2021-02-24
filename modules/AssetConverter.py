import os
from os.path import basename, splitext, exists
os.environ["NO_BPY"] = "1"
from PIL import Image
from SourceIO.source1.vtf.VTFWrapper import VTFLib
from .Vector2 import Vector2
from tempfile import gettempdir
from .Static import uniqueName
from subprocess import call
from PyCoD import Model

tempDir = gettempdir() + "/corvid"

def convertImage(src, dest, format="rgba"):
    if not exists(src):
        return False
    format = format.upper()
    image = VTFLib.VTFLib()
    image.image_load(src)
    width = image.width()
    height = image.height()
    rgba = Image.frombuffer("RGBA", (width, height), image.convert_to_rgba8888().contents)
    # image.image_format().name => compression format as a string. might come in handy if I decide to convert the color maps to dds in the future.
    if format == "RGBA":
        rgba.save(dest)
    elif format == "RGB":
        rgba.convert("RGB").save(dest)
    elif len(format) == 1:
        rgba.getchannel(format).save(dest)

def convertImages(images, src, dest, ext="tga"):
    images["colorMaps"] = list(dict.fromkeys(images["colorMaps"]))
    images["colorMapsAlpha"] = list(dict.fromkeys(images["colorMapsAlpha"]))
    images["normalMaps"] = list(dict.fromkeys(images["normalMaps"]))
    images["envMaps"] = list(dict.fromkeys(images["envMaps"]))
    images["envMapsAlpha"] = list(dict.fromkeys(images["envMapsAlpha"]))
    images["revealMaps"] = list(dict.fromkeys(images["revealMaps"]))
    for file in images["colorMapsAlpha"]:
        convertImage(f"{tempDir}/{src}/{file}.vtf", f"{tempDir}/converted/{dest}/{uniqueName(file)}.{ext}", "rgba")
    for file in images["normalMaps"]:
        convertImage(f"{tempDir}/{src}/{file}.vtf", f"{tempDir}/converted/{dest}/{uniqueName(file)}.{ext}", "rgb")
    for file in images["envMaps"]:
        convertImage(f"{tempDir}/{src}/{file}.vtf", f"{tempDir}/converted/{dest}/{uniqueName(file)}.{ext}", "rgb")
    for file in images["envMapsAlpha"]:
        convertImage(f"{tempDir}/{src}/{file}.vtf", f"{tempDir}/converted/{dest}/{uniqueName(file)}_.{ext}", "a")
    for file in images["revealMaps"]:
        convertImage(f"{tempDir}/{src}/{file}.vtf", f"{tempDir}/converted/{dest}/{uniqueName(file)}.{ext}", "g")
    for file in images["colorMaps"]:
        convertImage(f"{tempDir}/{src}/{file}.vtf", f"{tempDir}/converted/{dest}/{uniqueName(file)}.{ext}", "rgb")

def getTexSize(src):
    image = VTFLib.VTFLib()
    image.image_load(src)
    return Vector2(image.width(), image.height())

def convertModels(models, BO3=False):
    codModel = Model()
    mdlDir = f"{tempDir}/mdl"
    convertDir = f"{tempDir}/converted/model_export/corvid"
    for model in models:
        model = splitext(basename(model))[0]
        call(["bin/mdl2xmodel.exe", f"{mdlDir}/{model}", convertDir])
        if BO3:
            codModel.LoadFile_Raw(f"{convertDir}/{model}.xmodel_export")
            codModel.WriteFile_Bin(f"{convertDir}/{model}.xmodel_bin")
            os.remove(f"{convertDir}/{model}.xmodel_export")
