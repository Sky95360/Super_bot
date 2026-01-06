#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║               SKY AI ASSISTANT SETUP                     ║"
echo "║          WhatsApp Bot + AI Assistant                     ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running in Termux
if [[ -d "/data/data/com.termux/files/usr" ]]; then
    echo -e "${GREEN}✓ Detected Termux Environment${NC}"
    IS_TERMUX=true
else
    echo -e "${YELLOW}⚠ Running on regular Linux/Mac${NC}"
    IS_TERMUX=false
fi

# Update system packages
echo -e "\n${CYAN}[1/7] Updating system packages...${NC}"
if [ "$IS_TERMUX" = true ]; then
    pkg update -y && pkg upgrade -y
    echo -e "${GREEN}✓ Termux updated successfully${NC}"
else
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt upgrade -y
    elif command -v yum &> /dev/null; then
        sudo yum update -y
    elif command -v brew &> /dev/null; then
        brew update && brew upgrade
    fi
    echo -e "${GREEN}✓ System updated${NC}"
fi

# Install Python and Git
echo -e "\n${CYAN}[2/7] Installing Python and Git...${NC}"
if [ "$IS_TERMUX" = true ]; then
    pkg install python -y
    pkg install git -y
    pkg install wget -y
    pkg install curl -y
    echo -e "${GREEN}✓ Python & Git installed${NC}"
else
    if command -v apt &> /dev/null; then
        sudo apt install python3 python3-pip git wget curl -y
    elif command -v yum &> /dev/null; then
        sudo yum install python3 python3-pip git wget curl -y
    elif command -v brew &> /dev/null; then
        brew install python git wget curl
    fi
    echo -e "${GREEN}✓ Python & Git installed${NC}"
fi

# Upgrade pip
echo -e "\n${CYAN}[3/7] Setting up Python environment...${NC}"
pip install --upgrade pip setuptools wheel
echo -e "${GREEN}✓ Pip upgraded to latest version${NC}"

# Install Python requirements
echo -e "\n${CYAN}[4/7] Installing Python packages...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓ All Python packages installed${NC}"
else
    echo -e "${YELLOW}⚠ requirements.txt not found, installing basic packages${NC}"
    pip install flask flask-cors gunicorn requests python-dotenv
    echo -e "${GREEN}✓ Basic packages installed${NC}"
fi

# Termux specific setup
if [ "$IS_TERMUX" = true ]; then
    echo -e "\n${CYAN}[5/7] Setting up Termux specific features...${NC}"
    
    # Install Termux:API for WhatsApp
    echo "Installing Termux:API..."
    pkg install termux-api -y
    
    # Grant permissions
    echo "Granting permissions..."
    termux-sms-permission 2>/dev/null || echo "SMS permission already granted"
    termux-contact-permission 2>/dev/null || echo "Contact permission already granted"
    
    # Install additional tools
    pkg install ffmpeg -y
    pkg install sqlite3 -y
    
    echo -e "${GREEN}✓ Termux setup completed${NC}"
fi

# Download NLTK data for AI features
echo -e "\n${CYAN}[6/7] Setting up AI/NLP components...${NC}"
python3 -c "
try:
    import nltk
    print('Downloading NLTK data...')
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    print('NLTK setup complete!')
except ImportError:
    print('NLTK not installed, skipping...')
except Exception as e:
    print(f'NLTK error: {e}')
"

# Make scripts executable
echo -e "\n${CYAN}[7/7] Setting up scripts...${NC}"
chmod +x build.sh setup.sh 2>/dev/null || true
chmod +x *.py 2>/dev/null || true
echo -e "${GREEN}✓ Scripts made executable${NC}"

# Display completion message
echo -e "\n${GREEN}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                  SETUP COMPLETED!                        ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${CYAN}📦 Installed Packages:${NC}"
echo "• Flask Web Framework"
echo "• WhatsApp Integration (Termux:API)"
echo "• AI/NLP Capabilities"
echo "• Production Server (Gunicorn)"
echo "• Database Support (SQLite3)"

echo -e "\n${CYAN}🚀 To start the application:${NC}"
echo "1. Run: ${GREEN}python app.py${NC}"
echo "2. Open browser: ${GREEN}http://localhost:5000${NC}"
echo "3. WhatsApp: Send commands to ${GREEN}+255748529340${NC}"

echo -e "\n${CYAN}🔧 Additional Commands:${NC}"
echo "• Test API: ${GREEN}curl http://localhost:5000/api/status${NC}"
echo "• Check logs: ${GREEN}tail -f app.log${NC}"
echo "• Run in background: ${GREEN}nohup python app.py &${NC}"

if [ "$IS_TERMUX" = true ]; then
    echo -e "\n${CYAN}📱 Termux Tips:${NC}"
    echo "• Keep screen on: ${GREEN}termux-wake-lock${NC}"
    echo "• Allow storage: ${GREEN}termux-setup-storage${NC}"
    echo "• Run in background: ${GREEN}tmux${NC}"
    echo "• Test WhatsApp: ${GREEN}termux-sms-send -n '+255748529340' 'Test'${NC}"
fi

echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📞 Your Number: +255748529340${NC}"
echo -e "${YELLOW}📧 Your Email: Sky649957@gmail.com${NC}"
echo -e "${YELLOW}🤖 Bot Name: Sky_b.o.y${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "\n${GREEN}🎉 Setup completed successfully!${NC}"
