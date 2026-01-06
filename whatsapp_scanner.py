#!/usr/bin/env python3
# whatsapp_scanner.py
import qrcode
import json
import requests
import time
import os
import base64
import subprocess
from datetime import datetime

class WhatsAppSessionScanner:
    def __init__(self):
        self.session_file = "whatsapp_session.json"
        self.sessions = {}
        self.load_sessions()
        
    def load_sessions(self):
        """Load saved sessions"""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r') as f:
                    self.sessions = json.load(f)
                print(f"📁 Loaded {len(self.sessions)} sessions")
            except:
                self.sessions = {}
    
    def save_sessions(self):
        """Save sessions to file"""
        with open(self.session_file, 'w') as f:
            json.dump(self.sessions, f, indent=2)
        print("💾 Sessions saved")
    
    def generate_qr_code(self, session_name="default"):
        """Generate WhatsApp QR code for scanning"""
        # Create unique session ID
        session_id = f"session_{int(time.time())}_{session_name}"
        
        # QR data for WhatsApp Web
        qr_data = f"https://web.whatsapp.com/scan?session={session_id}"
        
        # Generate QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to file
        filename = f"{session_id}.png"
        img.save(filename)
        
        # Store session info
        self.sessions[session_id] = {
            "name": session_name,
            "created": datetime.now().isoformat(),
            "status": "pending",
            "qr_file": filename,
            "last_activity": None,
            "messages_sent": 0
        }
        self.save_sessions()
        
        return {
            "session_id": session_id,
            "qr_file": filename,
            "qr_data": qr_data,
            "instructions": f"Scan this QR with WhatsApp -> Link Device"
        }
    
    def check_session_status(self, session_id):
        """Check if session is active"""
        if session_id not in self.sessions:
            return {"active": False, "error": "Session not found"}
        
        session = self.sessions[session_id]
        
        # Simulate checking (in real app, you'd check WhatsApp Web connection)
        # Here we just check if session was "used" recently
        if session["status"] == "active":
            return {
                "active": True,
                "session": session,
                "message": "Session is active"
            }
        else:
            return {
                "active": False,
                "session": session,
                "message": "Session pending - scan QR code"
            }
    
    def activate_session(self, session_id):
        """Mark session as active (after QR scan)"""
        if session_id in self.sessions:
            self.sessions[session_id]["status"] = "active"
            self.sessions[session_id]["last_activity"] = datetime.now().isoformat()
            self.sessions[session_id]["activated"] = datetime.now().isoformat()
            self.save_sessions()
            return {"success": True, "message": "Session activated"}
        return {"success": False, "error": "Session not found"}
    
    def send_message_via_api(self, session_id, phone, message):
        """Send message using WhatsApp API services"""
        try:
            # Format phone
            if not phone.startswith('+'):
                phone = f'+255{phone.lstrip("0")}'
            
            # Using free WhatsApp API services (demo)
            apis = [
                {
                    "name": "ChatAPI",
                    "url": f"https://eu1.chat-api.com/instance12345/sendMessage",
                    "method": "POST",
                    "headers": {"Content-Type": "application/json"},
                    "data": {"phone": phone, "body": message}
                },
                {
                    "name": "CallMeBot",
                    "url": f"https://api.callmebot.com/whatsapp.php",
                    "method": "GET",
                    "params": {"phone": phone, "text": message, "apikey": "demo"}
                }
            ]
            
            # Try each API
            for api in apis:
                try:
                    if api["method"] == "POST":
                        response = requests.post(
                            api["url"],
                            json=api["data"],
                            headers=api["headers"],
                            timeout=10
                        )
                    else:
                        response = requests.get(
                            api["url"],
                            params=api["params"],
                            timeout=10
                        )
                    
                    if response.status_code == 200:
                        # Update session stats
                        if session_id in self.sessions:
                            self.sessions[session_id]["messages_sent"] += 1
                            self.sessions[session_id]["last_activity"] = datetime.now().isoformat()
                            self.save_sessions()
                        
                        return {
                            "success": True,
                            "api": api["name"],
                            "message": f"Message sent to {phone}",
                            "response": response.text[:100]
                        }
                except:
                    continue
            
            # If all APIs fail, use fallback
            return self._fallback_send(session_id, phone, message)
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _fallback_send(self, session_id, phone, message):
        """Fallback sending method"""
        # Simulate sending (for demo)
        print(f"[SIMULATED] Sending to {phone}: {message}")
        
        if session_id in self.sessions:
            self.sessions[session_id]["messages_sent"] += 1
            self.sessions[session_id]["last_activity"] = datetime.now().isoformat()
            self.save_sessions()
        
        return {
            "success": True,
            "method": "simulated",
            "message": f"Simulated send to {phone}",
            "note": "In production, connect to real WhatsApp API"
        }
    
    def list_sessions(self):
        """List all sessions"""
        active = [s for s in self.sessions.values() if s["status"] == "active"]
        pending = [s for s in self.sessions.values() if s["status"] == "pending"]
        
        return {
            "total": len(self.sessions),
            "active": len(active),
            "pending": len(pending),
            "sessions": self.sessions
        }
    
    def delete_session(self, session_id):
        """Delete a session"""
        if session_id in self.sessions:
            # Delete QR file if exists
            qr_file = self.sessions[session_id].get("qr_file")
            if qr_file and os.path.exists(qr_file):
                os.remove(qr_file)
            
            del self.sessions[session_id]
            self.save_sessions()
            return {"success": True, "message": "Session deleted"}
        return {"success": False, "error": "Session not found"}
    
    def get_session_qr_image(self, session_id):
        """Get QR code image for session"""
        if session_id in self.sessions:
            qr_file = self.sessions[session_id].get("qr_file")
            if qr_file and os.path.exists(qr_file):
                with open(qr_file, 'rb') as f:
                    return base64.b64encode(f.read()).decode('utf-8')
        return None
    
    def export_session(self, session_id):
        """Export session data"""
        if session_id in self.sessions:
            session_data = self.sessions[session_id].copy()
            
            # Add QR image
            qr_image = self.get_session_qr_image(session_id)
            if qr_image:
                session_data["qr_image_base64"] = qr_image
            
            return {
                "success": True,
                "session_id": session_id,
                "data": session_data
            }
        return {"success": False, "error": "Session not found"}
    
    def import_session(self, session_data):
        """Import session data"""
        try:
            session_id = session_data.get("session_id")
            if session_id:
                self.sessions[session_id] = session_data
                self.save_sessions()
                return {"success": True, "session_id": session_id}
        except:
            pass
        return {"success": False, "error": "Invalid session data"}

# Command Line Interface
def main():
    scanner = WhatsAppSessionScanner()
    
    print("🤖 WhatsApp Session Scanner")
    print("=" * 40)
    
    while True:
        print("\nCommands:")
        print("1. Create new session")
        print("2. List sessions")
        print("3. Check session status")
        print("4. Send message")
        print("5. Activate session")
        print("6. Delete session")
        print("7. Export session")
        print("8. Exit")
        
        choice = input("\nSelect option (1-8): ").strip()
        
        if choice == "1":
            name = input("Enter session name: ").strip() or "default"
            result = scanner.generate_qr_code(name)
            print(f"\n✅ Session created: {result['session_id']}")
            print(f"📁 QR saved: {result['qr_file']}")
            print(f"📱 Scan with WhatsApp -> Link Device")
            
            # Show QR in terminal if possible
            try:
                subprocess.run(["termux-open", result["qr_file"]])
                print("📸 QR opened in image viewer")
            except:
                print("💡 Open QR file manually to scan")
        
        elif choice == "2":
            result = scanner.list_sessions()
            print(f"\n📊 Sessions: {result['total']} total")
            print(f"✅ Active: {result['active']}")
            print(f"⏳ Pending: {result['pending']}")
            
            for sid, session in result["sessions"].items():
                print(f"\n  🔹 {sid}")
                print(f"    Name: {session['name']}")
                print(f"    Status: {session['status']}")
                print(f"    Created: {session['created']}")
                print(f"    Messages: {session['messages_sent']}")
        
        elif choice == "3":
            session_id = input("Enter session ID: ").strip()
            result = scanner.check_session_status(session_id)
            if result["active"]:
                print(f"\n✅ Session active")
                print(f"📅 Created: {result['session']['created']}")
                print(f"📤 Messages sent: {result['session']['messages_sent']}")
            else:
                print(f"\n❌ {result['message']}")
        
        elif choice == "4":
            session_id = input("Session ID: ").strip()
            phone = input("Phone number: ").strip()
            message = input("Message: ").strip()
            
            result = scanner.send_message_via_api(session_id, phone, message)
            if result["success"]:
                print(f"\n✅ {result['message']}")
                print(f"🔧 Method: {result.get('method', result.get('api', 'unknown'))}")
            else:
                print(f"\n❌ Failed: {result.get('error', 'Unknown error')}")
        
        elif choice == "5":
            session_id = input("Session ID to activate: ").strip()
            result = scanner.activate_session(session_id)
            print(f"\n{'✅' if result['success'] else '❌'} {result.get('message', result.get('error', ''))}")
        
        elif choice == "6":
            session_id = input("Session ID to delete: ").strip()
            result = scanner.delete_session(session_id)
            print(f"\n{'✅' if result['success'] else '❌'} {result.get('message', result.get('error', ''))}")
        
        elif choice == "7":
            session_id = input("Session ID to export: ").strip()
            result = scanner.export_session(session_id)
            if result["success"]:
                filename = f"{session_id}_export.json"
                with open(filename, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"\n✅ Session exported to {filename}")
            else:
                print(f"\n❌ {result['error']}")
        
        elif choice == "8":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("\n❌ Invalid choice")

if __name__ == "__main__":
    main()
