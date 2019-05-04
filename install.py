import json
import urllib3
import os
import re
from subprocess import call

urllib3.disable_warnings()
http = urllib3.PoolManager()

curse_url = "https://www.curseforge.com/minecraft/mc-mods/{0}/download/{1}/file"
forge_url = "https://files.minecraftforge.net/maven/net/minecraftforge/forge/{0}-{1}/forge-{0}-{1}-installer.jar"

data = json.loads(open("manifest.json").read())
pack_name = data["name"]
pack_version = data["version"]
out_name = "{}-{}".format(pack_name, pack_version)
mc_version = data["minecraft"]["version"]
overrides_dir = data["overrides"]

loaders = [loader_obj["id"] for loader_obj in data["minecraft"]["modLoaders"] if loader_obj["primary"]]
if len(loaders) != 1:
    raise ValueError("Can only handle one primary loader!")

forge_version = ""
if loaders[0].startswith("forge-"):
    forge_version = loaders[0][6:]
else:
    raise ValueError("Unknown modloader: " + loaders[0])

if not os.path.isdir(out_name):
    os.mkdir(out_name)

print("Downloading... ", end="")
res = http.request('GET', forge_url.format(mc_version, forge_version), preload_content=False)
filename = "forge-{}-{}-installer.jar".format(mc_version, forge_version)
with open("{}/{}".format(out_name, filename), "wb+") as f:
    f.write(res.data)
print(filename)

files = [curse_url.format(f["projectID"], f["fileID"]) for f in data["files"]]
if not os.path.isdir("{}/mods".format(out_name)):
    os.mkdir("{}/mods".format(out_name))

for fil in files:
    print("Downloading... ", end="")
    res = http.request('GET', fil, preload_content=False)
    filename = re.findall(r"(?<=/)[^/]+$", res.geturl())[0]
    with open("{}/mods/{}".format(out_name, filename), "wb+") as f:
        f.write(res.data)
    print(filename)

call(["cp", "-r", "{}/.".format(overrides_dir), "{}/".format(out_name)])