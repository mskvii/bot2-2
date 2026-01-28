import json
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class MessageRefManager:
    """メッセージ参照機能の管理"""
    
    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir
        self.message_refs_dir = os.path.join(base_dir, "message_refs")
        os.makedirs(self.message_refs_dir, exist_ok=True)
    
    def save_message_ref(self, post_id: int, message_id: str, channel_id: str, user_id: str) -> None:
        """メッセージ参照を保存"""
        message_ref_data = {
            "post_id": post_id,
            "message_id": message_id,
            "channel_id": channel_id,
            "user_id": user_id,
            "created_at": datetime.now().isoformat()
        }
        
        message_ref_file = os.path.join(self.message_refs_dir, f'message_ref_{post_id}.json')
        
        with open(message_ref_file, 'w', encoding='utf-8') as f:
            json.dump(message_ref_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"メッセージ参照を保存しました: 投稿ID={post_id}")
    
    def get_message_ref(self, post_id: int) -> Optional[Dict[str, Any]]:
        """メッセージ参照を取得"""
        message_ref_file = os.path.join(self.message_refs_dir, f'message_ref_{post_id}.json')
        
        if not os.path.exists(message_ref_file):
            return None
        
        try:
            with open(message_ref_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    def delete_message_ref(self, post_id: int) -> bool:
        """メッセージ参照を削除"""
        message_ref_file = os.path.join(self.message_refs_dir, f'message_ref_{post_id}.json')
        
        try:
            os.remove(message_ref_file)
            return True
        except FileNotFoundError:
            return False
