import subprocess
import shlex


ffmpeg_options = f"-vn -i bugsnax.webm -ss 10 -to 15 -c copy output.webm -y"
args = ["ffmpeg"]
args.extend(shlex.split(ffmpeg_options))

subprocess.run(args)