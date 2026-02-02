import json
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ReplyManager:
    """リプライ機能の管理"""
    
    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir
        self.replies_dir = os.path.join(base_dir, "replies")
        os.makedirs(self.replies_dir, exist_ok=True)
    
    def get_next_reply_id(self) -> int:
        """次のリプライIDを取得"""
        existing_replies = [f for f in os.listdir(self.replies_dir) if f.endswith('.json')]
        if not existing_replies:
            return 1
        
        max_id = 0
        for filename in existing_replies:
            try:
                reply_id = int(filename.replace('.json', '').replace('reply_', ''))
                max_id = max(max_id, reply_id)
            except ValueError:
                continue
        
        return max_id + 1
    
    def save_reply(self, post_id: int, user_id: str, content: str, display_name: str) -> int:
        """リプライを保存"""
        reply_id = self.get_next_reply_id()
        
        reply_data = {
            "id": reply_id,
            "post_id": post_id,
            "user_id": user_id,
            "content": content,
            "display_name": display_name,
            "created_at": datetime.now().isoformat()
        }
        
        filename = os.path.join(self.replies_dir, f"reply_{reply_id}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(reply_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"リプライを保存しました: reply_id={reply_id}, post_id={post_id}, user_id={user_id}")
        return reply_id
    
    def get_replies(self, post_id: int) -> List[Dict[str, Any]]:
        """投稿のリプライを取得"""
        replies = []
        
        for filename in sorted(os.listdir(self.replies_dir)):
            if filename.startswith('reply_') and filename.endswith('.json'):
                try:
                    with open(os.path.join(self.replies_dir, filename), 'r', encoding='utf-8') as f:
                        reply = json.load(f)
                    
                    if reply.get('post_id') == post_id:
                        replies.append(reply)
                except (json.JSONDecodeError, FileNotFoundError):
                    continue
        
        return replies
    
    def get_replies_by_post_id(self, post_id: int) -> List[Dict[str, Any]]:
        """投稿IDから全リプライを取得"""
        return self.get_replies(post_id)
    
    def get_reply_by_id_and_user(self, reply_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """リプライIDとユーザーIDからリプライデータを取得"""
        for filename in os.listdir(self.replies_dir):
            if filename.startswith('reply_') and filename.endswith('.json'):
                try:
                    with open(os.path.join(self.replies_dir, filename), 'r', encoding='utf-8') as f:
                        reply_data = json.load(f)
                    
                    if (str(reply_data.get('id')) == str(reply_id) and 
                        reply_data.get('user_id') == user_id):
                        return reply_data
                except (json.JSONDecodeError, FileNotFoundError):
                    continue
        return None
    
    def delete_reply(self, reply_id: str, user_id: str) -> bool:
        """リプライを削除"""
        reply_data = self.get_reply_by_id_and_user(reply_id, user_id)
        if not reply_data:
            return False
        
        filename = os.path.join(self.replies_dir, f"reply_{reply_id}.json")
        try:
            os.remove(filename)
            return True
        except FileNotFoundError:
            return False
    
    def update_reply(self, post_id: int, reply_id: int, content: str) -> bool:
        """リプライを更新"""
        filename = os.path.join(self.replies_dir, f"reply_{reply_id}.json")
        
        if not os.path.exists(filename):
            return False
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reply_data = json.load(f)
            
            if reply_data.get('post_id') != post_id:
                return False
            
            reply_data['content'] = content
            reply_data['updated_at'] = datetime.now().isoformat()
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(reply_data, f, ensure_ascii=False, indent=2)
            
            return True
        except (json.JSONDecodeError, FileNotFoundError):
            return False
    
    def update_reply_message_id(self, reply_id: int, message_id: str, channel_id: str, forwarded_message_id: str = None) -> None:
        """リプライファイルにメッセージIDを更新"""
        filename = os.path.join(self.replies_dir, f"reply_{reply_id}.json")
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reply_data = json.load(f)
            
            reply_data['message_id'] = message_id
            reply_data['channel_id'] = channel_id
            if forwarded_message_id:
                reply_data['forwarded_message_id'] = forwarded_message_id
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(reply_data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"リプライメッセージIDを更新しました: reply_id={reply_id}")
        except (json.JSONDecodeError, FileNotFoundError):
            logger.warning(f"リプライメッセージID更新失敗: reply_id={reply_id}")
    
    def get_reply_message_ref(self, reply_id: int) -> Optional[Dict[str, Any]]:
        """リプライのmessage_refを取得"""
        filename = os.path.join(self.replies_dir, f"reply_{reply_id}.json")
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reply_data = json.load(f)
            
            return {
                'message_id': reply_data.get('message_id'),
                'channel_id': reply_data.get('channel_id'),
                'forwarded_message_id': reply_data.get('forwarded_message_id')
            }
        except (json.JSONDecodeError, FileNotFoundError):
            return None
