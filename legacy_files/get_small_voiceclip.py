import soundfile as sf
import os

print("cwd:", os.getcwd())
print("exists:", os.path.exists("/home/rex/Documents/client_projects/bob_charish/small_audio/wavs_16k/111.wav"))

# load your 6 min file
data, sr = sf.read("/home/rex/Documents/client_projects/bob_charish/small_audio/wavs_16k/111.wav")  
# data.shape → (samples, channels) or (samples,) for mono

# take only the first 10 seconds
duration_sec = 10
snippet = data[: sr * duration_sec]

# write out
sf.write("/home/rex/Documents/client_projects/bob_charish/small_audio/wavs_16k/smallref_snip.wav", snippet, sr)
print("Wrote smallref_snip.wav (10 s)")
