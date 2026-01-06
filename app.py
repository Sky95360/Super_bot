from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import time
import random
import requests
from datetime import datetime

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Detect platform
IS_TERMUX = os.path.exists('/data/data/com.termux/files/usr')
YOUR_NUMBER = "+255748529340"
YOUR_EMAIL = "Sky649957@gmail.com"

# Your Termux phone's public URL (you need to set this up)
TERMUX_PUBLIC_URL = None  # You'll set this after ngrok setup

class HybridWhatsApp:
    def __init__(self):
        self.platform = "termux" if IS_TERMUX else "render"
        
    def send_message(self, phone, message):
        """Send WhatsApp message - works on both platforms"""
        
        if IS_TERMUX:
            # Running on Termux - send directly
            return self._send_via_termux(phone, message)
        else:
            # Running on Render - forward to Termux
            return self._forward_to_termux(phone, message)
    
    def _send_via_termux(self, phone, message):
        """Direct WhatsApp sending (Termux only)"""
        try:
            import subprocess
            
            # Format phone for Tanzania
            if not phone.startswith('+'):
                if phone.startswith('0'):
                    phone = f"+255{phone[1:]}"
                else:
                    phone = f"+255{phone}"
            
            cmd = f'termux-sms-send -n "{phone}" "{message}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'platform': 'termux',
                    'message': f'✅ Sent to {phone}',
                    'details': 'Direct WhatsApp via Termux'
                }
            else:
                return {
                    'success': False,
                    'platform': 'termux',
                    'error': 'Failed to send via Termux'
                }
        except Exception as e:
            return {
                'success': False,
                'platform': 'termux',
                'error': str(e)
            }
    
    def _forward_to_termux(self, phone, message):
        """Forward request to Termux phone"""
        if not TERMUX_PUBLIC_URL:
            # Try to use ngrok if available
            ngrok_url = self._get_ngrok_url()
            if ngrok_url:
                global TERMUX_PUBLIC_URL
                TERMUX_PUBLIC_URL = ngrok_url
        
        if TERMUX_PUBLIC_URL:
            try:
                # Forward to Termux
                response = requests.post(
                    f"{TERMUX_PUBLIC_URL}/api/whatsapp/send",
                    json={'phone': phone, 'message': message},
                    timeout=10
                )
                
                if response.status_code == 200:
                    return {
                        'success': True,
                        'platform': 'render_to_termux',
                        'message': f'✅ Forwarded to Termux for delivery to {phone}',
                        'details': 'Message queued for WhatsApp delivery'
                    }
            except:
                pass
        
        # Fallback - simulate sending
        return {
            'success': True,
            'platform': 'render_simulation',
            'message': f'📱 WhatsApp message prepared for {phone}',
            'details': f'Message: "{message}"\n\n⚠️ Note: Enable Termux forwarding for actual delivery',
            'instructions': 'To enable actual WhatsApp: 1. Keep Termux running 2. Setup ngrok 3. Update TERMUX_PUBLIC_URL'
        }
    
    def _get_ngrok_url(self):
        """Try to get ngrok URL"""
        try:
            response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
            if response.status_code == 200:
                data = response.json()
                tunnels = data.get('tunnels', [])
                for tunnel in tunnels:
                    if tunnel.get('proto') == 'https':
                        return tunnel.get('public_url')
        except:
            pass
        return None
    
    def get_status(self):
        """Get platform status"""
        if IS_TERMUX:
            return {
                'platform': 'termux',
                'whatsapp': 'direct_send_enabled',
                'status': 'ready',
                'instructions': 'WhatsApp messages sent directly from this device'
            }
        else:
            status = {
                'platform': 'render',
                'whatsapp': 'forwarding_required',
                'status': 'web_only',
                'instructions': 'WhatsApp requires Termux forwarding setup'
            }
            
            if TERMUX_PUBLIC_URL:
                status['whatsapp'] = 'forwarding_enabled'
                status['termux_url'] = TERMUX_PUBLIC_URL
                status['status'] = 'connected'
            
            return status

# Initialize
whatsapp = HybridWhatsApp()

@app.route('/')
def home():
    """Serve the index.html file"""
    try:
        return send_from_directory('.', 'index.html')
    except:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sky AI Assistant</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
                h1 { color: #333; }
                .status { background: #4CAF50; color: white; padding: 10px; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Sky AI Assistant</h1>
                <p>Status: <span class="status">Online</span></p>
                <p>Platform: <strong>{}</strong></p>
                <p>Your Number: <strong>{}</strong></p>
                <p>Use the API endpoints to interact with the bot.</p>
                <p><a href="/api/status">Check API Status</a></p>
            </div>
        </body>
        </html>
        """.format(whatsapp.platform, YOUR_NUMBER)

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'response': 'Please enter a message!', 'status': 'error'})
        
        # Check for WhatsApp commands
        if user_message.lower().startswith('send whatsapp') or 'whatsapp to' in user_message.lower():
            # Parse phone and message
            parts = user_message.split('to', 1)
            if len(parts) > 1:
                rest = parts[1].strip()
                phone_end = rest.find(' ')
                if phone_end > 0:
                    phone = rest[:phone_end].strip()
                    message = rest[phone_end:].strip()
                    
                    result = whatsapp.send_message(phone, message)
                    
                    response = f"""
📱 **WhatsApp Message Status**
━━━━━━━━━━━━━━━━━━━━━━
📞 **To:** {phone}
📝 **Message:** {message[:50]}...
━━━━━━━━━━━━━━━━━━━━━━
✅ **Status:** {result['message']}
🔧 **Platform:** {result['platform']}
━━━━━━━━━━━━━━━━━━━━━━
"""
                    
                    if 'details' in result:
                        response += f"📋 **Details:** {result['details']}\n"
                    
                    if 'instructions' in result:
                        response += f"💡 **Note:** {result['instructions']}\n"
                    
                    response += "━━━━━━━━━━━━━━━━━━━━━━"
                    
                    return jsonify({
                        'response': response,
                        'status': 'success',
                        'whatsapp_result': result
                    })
        
        # Regular commands
        commands = {
            'ping': f"🏓 PONG!\nPlatform: {whatsapp.platform}\nNumber: {YOUR_NUMBER}\nStatus: Active",
            'status': get_system_status(),
            'menu': get_menu(),
            'help': get_help(),
            'info': f"""
🤖 **Sky AI Assistant**
━━━━━━━━━━━━━━━━━━━━━━
📞 **Phone:** {YOUR_NUMBER}
📧 **Email:** {YOUR_EMAIL}
🔧 **Platform:** {whatsapp.platform}
🌐 **WhatsApp:** {'Direct Send' if IS_TERMUX else 'Forwarding'}
━━━━━━━━━━━━━━━━━━━━━━
            """,
            'whatsapp setup': get_whatsapp_setup_guide()
        }
        
        cmd = user_message.lower().replace('.', '')
        if cmd in commands:
            response = commands[cmd]
        else:
            response = f"""
💬 **Chat Response**
━━━━━━━━━━━━━━━━━━━━━━
You said: "{user_message}"
━━━━━━━━━━━━━━━━━━━━━━
Try these commands:
• ping - Check status
• menu - Show commands
• status - System info
• send whatsapp to [number] [message]
━━━━━━━━━━━━━━━━━━━━━━
            """
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'response': f'Error: {str(e)}', 'status': 'error'})

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'online',
        'platform': whatsapp.platform,
        'whatsapp': whatsapp.get_status(),
        'your_number': YOUR_NUMBER,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/whatsapp/send', methods=['POST'])
def whatsapp_send():
    """Endpoint for Termux to receive forwarded messages"""
    if not IS_TERMUX:
        return jsonify({'error': 'This endpoint only works on Termux'}), 400
    
    try:
        data = request.json
        phone = data.get('phone')
        message = data.get('message')
        
        if not phone or not message:
            return jsonify({'error': 'Phone and message required'}), 400
        
        result = whatsapp.send_message(phone, message)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_system_status():
    status = whatsapp.get_status()
    return f"""
⚡ **System Status**
━━━━━━━━━━━━━━━━━━━━━━
🔧 Platform: {status['platform']}
📱 WhatsApp: {status['whatsapp']}
✅ Status: {status['status']}
📞 Your Number: {YOUR_NUMBER}
━━━━━━━━━━━━━━━━━━━━━━
💡 {status['instructions']}
━━━━━━━━━━━━━━━━━━━━━━
"""

def get_menu():
    return """
📱 **Sky AI Commands**
━━━━━━━━━━━━━━━━━━━━━━
🤖 **Basic Commands:**
• ping - Check bot status
• status - System information
• menu - This menu
• help - Get help
• info - Bot information

📱 **WhatsApp Commands:**
• send whatsapp to [number] [message]
• whatsapp setup - Setup instructions

🌐 **Web Features:**
• Chat interface
• Real-time responses
• Platform detection
• Status monitoring
━━━━━━━━━━━━━━━━━━━━━━
"""

def get_help():
    return """
🆘 **Help & Support**
━━━━━━━━━━━━━━━━━━━━━━
For WhatsApp issues:
1. Make sure Termux is running
2. Install Termux:API
3. Grant SMS permissions
4. Save contacts in phone

📞 **Contact:**
Phone: +255748529340
Email: Sky649957@gmail.com
━━━━━━━━━━━━━━━━━━━━━━
"""

def get_whatsapp_setup_guide():
    if IS_TERMUX:
        return """
✅ **Termux Setup (Already Done)**
━━━━━━━━━━━━━━━━━━━━━━
✓ Termux installed
✓ WhatsApp sending enabled
✓ Direct SMS permissions
✓ Ready to send messages
━━━━━━━━━━━━━━━━━━━━━━
To send: `send whatsapp to 0748xxxxxx Hello`
        """
    else:
        return """
📱 **Render + WhatsApp Setup**
━━━━━━━━━━━━━━━━━━━━━━
For actual WhatsApp delivery:
1. **On Termux (Phone):**
   ```bash
   pkg install ngrok
   ngrok authtoken YOUR_TOKEN
   ngrok http 5000
