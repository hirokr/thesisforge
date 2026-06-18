# ThesisForge Submission Assets

Generated for the hackathon submission package.

- `cover.png` - 16:9 cover image for the submission/project thumbnail.
- `thesisforge-pitch.pdf` - 7-slide PDF presentation.
- `thesisforge-presentation.mp4` - 48-second silent video presentation, H.264, 1280x720.
- `thesisforge-presentation.gif` - animated GIF fallback of the video presentation.
- `deck.html` - source for the PDF deck.
- `video-render.html` and `render-video.mjs` - source and renderer for the video assets.

Regenerate the PDF:

```bash
google-chrome --headless --disable-gpu --no-sandbox --allow-file-access-from-files \
  --print-to-pdf=/home/hirokr/Documents/thesisforge/submission-assets/thesisforge-pitch.pdf \
  file:///home/hirokr/Documents/thesisforge/submission-assets/deck.html
```

Regenerate video frames and GIF:

```bash
node submission-assets/render-video.mjs
```

Regenerate the MP4 from generated frames:

```bash
FFMPEG=$(python3 - <<'PY'
import imageio_ffmpeg
print(imageio_ffmpeg.get_ffmpeg_exe())
PY
)
"$FFMPEG" -y -framerate 5 -i submission-assets/video-frames/frame-%04d.png \
  -vf "scale=1280:720,fps=24,format=yuv420p" \
  -c:v libx264 -profile:v high -level 4.0 -movflags +faststart \
  submission-assets/thesisforge-presentation.mp4
```
