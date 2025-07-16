#!/usr/bin/env python3
"""
Oracle Intelligence System - Historical Data Import
Imports and processes historical Zoom meetings from various sources
"""

import os
import sys
import json
import argparse
import requests
import zipfile
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ZoomMeetingImporter:
    """Import and process historical Zoom meetings"""
    
    def __init__(self, api_base_url: str = "http://localhost:8001/api"):
        self.api_base_url = api_base_url
        self.session = requests.Session()
        self.imported_count = 0
        self.processed_count = 0
        self.error_count = 0
        
        # Impact Launchpad team member mapping
        self.team_mapping = {
            "daniel.matalon@impactlaunchpad.com": "daniel",
            "daniel@impactlaunchpad.com": "daniel",
            "troy.mork@impactlaunchpad.com": "troy", 
            "troy@impactlaunchpad.com": "troy",
            "kristie.thompson@impactlaunchpad.com": "kristie",
            "kristie@impactlaunchpad.com": "kristie",
            "debbie.resnick@impactlaunchpad.com": "debbie",
            "debbie@impactlaunchpad.com": "debbie",
            "joe.dalton@impactlaunchpad.com": "joe",
            "joe@impactlaunchpad.com": "joe",
            "ronnie.elcheikh@impactlaunchpad.com": "ronnie",
            "ronnie@impactlaunchpad.com": "ronnie",
            "isabel.pierola@impactlaunchpad.com": "isabel",
            "isabel@impactlaunchpad.com": "isabel",
            "marc.diamond@impactlaunchpad.com": "marc",
            "marc@impactlaunchpad.com": "marc",
            "jimi.cohen@impactlaunchpad.com": "jimi",
            "jimi@impactlaunchpad.com": "jimi"
        }
    
    def test_api_connection(self) -> bool:
        """Test connection to Oracle Intelligence API"""
        try:
            response = self.session.get(f"{self.api_base_url}/health")
            if response.status_code == 200:
                logger.info("✅ Oracle Intelligence API connection successful")
                return True
            else:
                logger.error(f"❌ API connection failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ API connection error: {e}")
            return False
    
    def map_participants(self, participants: List[str]) -> List[str]:
        """Map email addresses to team member IDs"""
        mapped = []
        for participant in participants:
            # Try direct mapping first
            if participant.lower() in self.team_mapping:
                mapped.append(self.team_mapping[participant.lower()])
            # Try name-based mapping
            elif any(name in participant.lower() for name in ["daniel", "troy", "kristie", "debbie", "joe", "ronnie", "isabel", "marc", "jimi"]):
                for email, user_id in self.team_mapping.items():
                    if user_id in participant.lower():
                        mapped.append(user_id)
                        break
            else:
                # Keep original if no mapping found
                mapped.append(participant)
        
        return list(set(mapped))  # Remove duplicates
    
    def import_zoom_cloud_meetings(self, zoom_api_key: str, zoom_api_secret: str, 
                                 date_range: str = "all") -> List[Dict]:
        """Import meetings from Zoom Cloud"""
        logger.info("🌥️ Starting Zoom Cloud import...")
        
        # This would integrate with Zoom API
        # For now, return sample structure
        meetings = []
        
        # TODO: Implement actual Zoom API integration
        logger.warning("⚠️ Zoom Cloud API integration not yet implemented")
        logger.info("📋 Please export meetings manually from Zoom and use local import")
        
        return meetings
    
    def import_local_zoom_files(self, directory: str) -> List[Dict]:
        """Import Zoom meetings from local files"""
        logger.info(f"📁 Importing local Zoom files from: {directory}")
        
        meetings = []
        directory_path = Path(directory)
        
        if not directory_path.exists():
            logger.error(f"❌ Directory not found: {directory}")
            return meetings
        
        # Look for common Zoom file patterns
        patterns = [
            "*.mp4",  # Video recordings
            "*.m4a",  # Audio recordings
            "*.txt",  # Chat transcripts
            "*.vtt",  # Subtitle files
            "*.csv",  # Participant reports
            "*.json", # Meeting metadata
        ]
        
        for pattern in patterns:
            files = list(directory_path.rglob(pattern))
            logger.info(f"Found {len(files)} {pattern} files")
            
            for file_path in files:
                try:
                    meeting_data = self.process_zoom_file(file_path)
                    if meeting_data:
                        meetings.append(meeting_data)
                        self.processed_count += 1
                except Exception as e:
                    logger.error(f"❌ Error processing {file_path}: {e}")
                    self.error_count += 1
        
        logger.info(f"✅ Processed {len(meetings)} meetings from local files")
        return meetings
    
    def process_zoom_file(self, file_path: Path) -> Optional[Dict]:
        """Process individual Zoom file"""
        file_name = file_path.name
        file_ext = file_path.suffix.lower()
        
        # Extract meeting info from filename
        # Common Zoom filename patterns:
        # "GMT20240101-120000_Recording_1920x1080.mp4"
        # "Meeting_Title_2024-01-01_12-00-00.mp4"
        
        meeting_data = {
            "file_path": str(file_path),
            "file_name": file_name,
            "file_type": file_ext,
            "file_size": file_path.stat().st_size,
            "created_date": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
            "modified_date": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }
        
        # Extract date from filename
        meeting_date = self.extract_date_from_filename(file_name)
        if meeting_date:
            meeting_data["meeting_date"] = meeting_date
        
        # Process different file types
        if file_ext == ".txt":
            # Chat transcript
            meeting_data.update(self.process_chat_transcript(file_path))
        elif file_ext == ".vtt":
            # Subtitle/transcript file
            meeting_data.update(self.process_vtt_transcript(file_path))
        elif file_ext == ".csv":
            # Participant report
            meeting_data.update(self.process_participant_report(file_path))
        elif file_ext == ".json":
            # Meeting metadata
            meeting_data.update(self.process_meeting_metadata(file_path))
        elif file_ext in [".mp4", ".m4a"]:
            # Audio/video recording
            meeting_data.update(self.process_recording_file(file_path))
        
        return meeting_data
    
    def extract_date_from_filename(self, filename: str) -> Optional[str]:
        """Extract date from Zoom filename patterns"""
        import re
        
        # Pattern 1: GMT20240101-120000
        pattern1 = r"GMT(\d{8})-(\d{6})"
        match1 = re.search(pattern1, filename)
        if match1:
            date_str = match1.group(1)
            time_str = match1.group(2)
            try:
                dt = datetime.strptime(f"{date_str}{time_str}", "%Y%m%d%H%M%S")
                return dt.isoformat()
            except:
                pass
        
        # Pattern 2: 2024-01-01_12-00-00
        pattern2 = r"(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2})"
        match2 = re.search(pattern2, filename)
        if match2:
            date_str = match2.group(1)
            time_str = match2.group(2).replace("-", ":")
            try:
                dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
                return dt.isoformat()
            except:
                pass
        
        return None
    
    def process_chat_transcript(self, file_path: Path) -> Dict:
        """Process Zoom chat transcript"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse chat messages
            messages = []
            participants = set()
            
            for line in content.split('\n'):
                if line.strip():
                    # Common format: "12:34:56 From John Doe : Message text"
                    if ' From ' in line and ' : ' in line:
                        parts = line.split(' From ', 1)
                        if len(parts) == 2:
                            timestamp = parts[0].strip()
                            rest = parts[1].split(' : ', 1)
                            if len(rest) == 2:
                                sender = rest[0].strip()
                                message = rest[1].strip()
                                
                                participants.add(sender)
                                messages.append({
                                    "timestamp": timestamp,
                                    "sender": sender,
                                    "message": message
                                })
            
            return {
                "chat_messages": messages,
                "chat_participants": list(participants),
                "chat_message_count": len(messages)
            }
        except Exception as e:
            logger.error(f"Error processing chat transcript {file_path}: {e}")
            return {}
    
    def process_vtt_transcript(self, file_path: Path) -> Dict:
        """Process VTT subtitle/transcript file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse VTT format
            transcript_text = ""
            speakers = set()
            
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '-->' in line:  # Timestamp line
                    # Next line should be the transcript
                    if i + 1 < len(lines):
                        text_line = lines[i + 1].strip()
                        if text_line:
                            transcript_text += text_line + " "
                            
                            # Extract speaker if format includes it
                            if ':' in text_line:
                                speaker = text_line.split(':')[0].strip()
                                speakers.add(speaker)
            
            return {
                "transcript": transcript_text.strip(),
                "transcript_speakers": list(speakers),
                "transcript_length": len(transcript_text.strip())
            }
        except Exception as e:
            logger.error(f"Error processing VTT transcript {file_path}: {e}")
            return {}
    
    def process_participant_report(self, file_path: Path) -> Dict:
        """Process CSV participant report"""
        try:
            df = pd.read_csv(file_path)
            
            participants = []
            if 'Name (Original Name)' in df.columns:
                participants = df['Name (Original Name)'].tolist()
            elif 'Name' in df.columns:
                participants = df['Name'].tolist()
            
            # Map to team member IDs
            mapped_participants = self.map_participants(participants)
            
            return {
                "participants": mapped_participants,
                "participant_count": len(participants),
                "participant_details": df.to_dict('records') if len(df) < 100 else []
            }
        except Exception as e:
            logger.error(f"Error processing participant report {file_path}: {e}")
            return {}
    
    def process_meeting_metadata(self, file_path: Path) -> Dict:
        """Process JSON meeting metadata"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            return {
                "metadata": metadata,
                "meeting_title": metadata.get("topic", ""),
                "meeting_id": metadata.get("id", ""),
                "start_time": metadata.get("start_time", ""),
                "duration": metadata.get("duration", 0)
            }
        except Exception as e:
            logger.error(f"Error processing meeting metadata {file_path}: {e}")
            return {}
    
    def process_recording_file(self, file_path: Path) -> Dict:
        """Process audio/video recording file"""
        return {
            "recording_path": str(file_path),
            "recording_type": "video" if file_path.suffix == ".mp4" else "audio",
            "recording_size_mb": round(file_path.stat().st_size / (1024 * 1024), 2)
        }
    
    def create_meeting_record(self, meeting_data: Dict) -> Dict:
        """Create standardized meeting record for Oracle Intelligence"""
        
        # Generate meeting ID
        meeting_id = meeting_data.get("meeting_id")
        if not meeting_id:
            # Generate from filename and date
            base_name = Path(meeting_data.get("file_name", "unknown")).stem
            date_str = meeting_data.get("meeting_date", datetime.now().isoformat())[:10]
            meeting_id = f"imported_{base_name}_{date_str}".replace(" ", "_").replace("-", "_")
        
        # Extract meeting title
        title = meeting_data.get("meeting_title") or meeting_data.get("file_name", "Imported Meeting")
        
        # Get participants
        participants = meeting_data.get("participants", [])
        if not participants:
            participants = meeting_data.get("chat_participants", [])
        if not participants:
            participants = meeting_data.get("transcript_speakers", [])
        
        # Map participants to team IDs
        participants = self.map_participants(participants)
        
        # Create transcript
        transcript = meeting_data.get("transcript", "")
        if not transcript and "chat_messages" in meeting_data:
            # Create transcript from chat
            chat_text = []
            for msg in meeting_data["chat_messages"]:
                chat_text.append(f"{msg['sender']}: {msg['message']}")
            transcript = "\n".join(chat_text)
        
        # Estimate duration
        duration_minutes = meeting_data.get("duration", 60)
        if isinstance(duration_minutes, str):
            try:
                duration_minutes = int(duration_minutes)
            except:
                duration_minutes = 60
        
        return {
            "meeting_id": meeting_id,
            "title": title,
            "date": meeting_data.get("meeting_date", datetime.now().isoformat())[:10],
            "participants": participants,
            "transcript": transcript,
            "duration_minutes": duration_minutes,
            "meeting_type": "imported",
            "source_data": meeting_data
        }
    
    def upload_meeting_to_oracle(self, meeting_record: Dict) -> bool:
        """Upload meeting record to Oracle Intelligence API"""
        try:
            response = self.session.post(
                f"{self.api_base_url}/meetings",
                json=meeting_record
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"✅ Uploaded meeting: {meeting_record['meeting_id']}")
                self.imported_count += 1
                return True
            else:
                logger.error(f"❌ Failed to upload meeting {meeting_record['meeting_id']}: {response.status_code}")
                logger.error(f"Response: {response.text}")
                self.error_count += 1
                return False
                
        except Exception as e:
            logger.error(f"❌ Error uploading meeting {meeting_record['meeting_id']}: {e}")
            self.error_count += 1
            return False
    
    def import_and_process(self, source: str, **kwargs) -> Dict[str, int]:
        """Main import and processing function"""
        logger.info("🚀 Starting Oracle Intelligence historical data import...")
        
        # Test API connection
        if not self.test_api_connection():
            return {"error": "API connection failed"}
        
        meetings = []
        
        if source == "cloud":
            zoom_api_key = kwargs.get("zoom_api_key")
            zoom_api_secret = kwargs.get("zoom_api_secret")
            date_range = kwargs.get("date_range", "all")
            meetings = self.import_zoom_cloud_meetings(zoom_api_key, zoom_api_secret, date_range)
            
        elif source == "local":
            directory = kwargs.get("directory")
            if not directory:
                logger.error("❌ Directory path required for local import")
                return {"error": "Directory path required"}
            meetings = self.import_local_zoom_files(directory)
            
        else:
            logger.error(f"❌ Unknown source: {source}")
            return {"error": f"Unknown source: {source}"}
        
        # Process and upload meetings
        logger.info(f"📊 Processing {len(meetings)} meetings...")
        
        for meeting_data in meetings:
            try:
                meeting_record = self.create_meeting_record(meeting_data)
                self.upload_meeting_to_oracle(meeting_record)
            except Exception as e:
                logger.error(f"❌ Error processing meeting: {e}")
                self.error_count += 1
        
        # Return summary
        summary = {
            "processed": self.processed_count,
            "imported": self.imported_count,
            "errors": self.error_count,
            "total_files": len(meetings)
        }
        
        logger.info("📈 Import Summary:")
        logger.info(f"  • Files processed: {summary['processed']}")
        logger.info(f"  • Meetings imported: {summary['imported']}")
        logger.info(f"  • Errors: {summary['errors']}")
        
        return summary

def main():
    parser = argparse.ArgumentParser(description="Import historical Zoom meetings to Oracle Intelligence")
    parser.add_argument("--source", choices=["cloud", "local"], required=True,
                       help="Import source: cloud (Zoom API) or local (file directory)")
    parser.add_argument("--directory", help="Directory path for local import")
    parser.add_argument("--zoom-api-key", help="Zoom API key for cloud import")
    parser.add_argument("--zoom-api-secret", help="Zoom API secret for cloud import")
    parser.add_argument("--date-range", default="all", help="Date range for cloud import")
    parser.add_argument("--api-url", default="http://localhost:8001/api", 
                       help="Oracle Intelligence API URL")
    
    args = parser.parse_args()
    
    # Create importer
    importer = ZoomMeetingImporter(api_base_url=args.api_url)
    
    # Prepare kwargs
    kwargs = {}
    if args.directory:
        kwargs["directory"] = args.directory
    if args.zoom_api_key:
        kwargs["zoom_api_key"] = args.zoom_api_key
    if args.zoom_api_secret:
        kwargs["zoom_api_secret"] = args.zoom_api_secret
    if args.date_range:
        kwargs["date_range"] = args.date_range
    
    # Run import
    result = importer.import_and_process(args.source, **kwargs)
    
    if "error" in result:
        logger.error(f"❌ Import failed: {result['error']}")
        sys.exit(1)
    else:
        logger.info("🎉 Import completed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()

