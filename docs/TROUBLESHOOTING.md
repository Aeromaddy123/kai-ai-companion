# KAI Troubleshooting Guide

## Common Issues

### Server Issues

#### Ollama not running
```
Error: Connection refused to http://localhost:11434
```

**Solution:**
```bash
# Start Ollama
ollama serve

# Check if running
curl http://localhost:11434/api/tags
```

#### Model not found
```
Error: model not found
```

**Solution:**
```bash
# Pull the required model
ollama pull qwen2.5:8b
ollama pull llava:1.6

# List available models
ollama list
```

#### Out of memory
```
Error: unexpected EOF
```

**Solution:**
- Use a smaller model (qwen2.5:4b instead of 8b)
- Close other applications
- Enable swap space:
```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Raspberry Pi Issues

#### Audio not working
```
Error: No default input device available
```

**Solution:**
```bash
# List audio devices
arecord -l
pactl list sources short

# Set default device
pactl set-default-source 1
```

#### Camera not detected
```
Error: Camera not found
```

**Solution:**
```bash
# Check camera
vcgencmd get_camera

# Enable camera in raspi-config
sudo raspi-config
# Navigate to Interface Options > Camera > Enable

# Or add to /boot/config.txt
echo "start_x=1" | sudo tee -a /boot/config.txt
echo "gpu_mem=256" | sudo tee -a /boot/config.txt

# Reboot
sudo reboot
```

#### Connection to server failed
```
Error: Connection refused to 192.168.1.100:8000
```

**Solution:**
1. Check server is running:
```bash
curl http://localhost:8000/health
```

2. Check firewall:
```bash
sudo ufw allow 8000
```

3. Verify network connectivity:
```bash
ping 192.168.1.100
```

### Voice Recognition Issues

#### Vosk model not found
```
Error: Model path does not exist: models/vosk-model-small-en-us-0.15
```

**Solution:**
```bash
# Download the model
mkdir -p models
cd models
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
rm vosk-model-small-en-us-0.15.zip
```

#### Poor transcription accuracy
**Tips:**
- Speak clearly and at normal pace
- Reduce background noise
- Position microphone close to speaker
- Use a directional microphone

### Vision Issues

#### LLaVA not responding
```
Error: vision model not available
```

**Solution:**
```bash
# Pull LLaVA model
ollama pull llava:1.6

# Test locally
ollama run llava:1.6 "Describe this image"
```

#### Low quality descriptions
**Tips:**
- Ensure good lighting
- Clean camera lens
- Position camera at eye level
- Avoid motion blur

### Memory Issues

#### ChromaDB errors
```
Error: ChromaDB collection not found
```

**Solution:**
```bash
# Clear and recreate database
rm -rf data/chroma
mkdir -p data/chroma
```

## Performance Optimization

### Server Performance
- Use quantization: `ollama pull qwen2.5:8b-instruct-q4_0`
- Enable GPU acceleration if available
- Use faster storage (SSD)

### RPI Performance
- Overclock in /boot/config.txt:
```
arm_freq=2000
gpu_freq=700
```
- Use Ethernet instead of WiFi for lower latency
- Close unnecessary processes

## Getting Help

If you encounter issues not covered here:
1. Check the GitHub Issues page
2. Enable debug logging in config.yaml
3. Check logs in logs/kai.log
