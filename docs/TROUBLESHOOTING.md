# Troubleshooting

## Server won't start
```bash
ollama serve
```

## Models not found
```bash
ollama pull qwen2.5:8b
ollama pull llava:1.6
```

## Out of memory
Use smaller models (qwen2.5:4b) or close other apps.

## No audio on Raspberry Pi
```bash
# Check devices
arecord -l

# Set default
pactl set-default-source 1
```

## Camera not working
```bash
# Enable in raspi-config
sudo raspi-config
# Interface Options > Camera > Enable
sudo reboot
```

## Can't connect to server
1. Check server is running: `curl http://localhost:8000/health`
2. Check firewall allows port 8000
3. Make sure both devices are on same network

## Questions?
Open an issue on GitHub.
