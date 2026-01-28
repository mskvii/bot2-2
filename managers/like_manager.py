import json
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class LikeManager:
    """いいね機能の管理"""
    
    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir
        self.likes_dir = os.path.join(base_dir, "likes")
        os.makedirs(self.likes_dir, exist_ok=True)
    
    def get_next_like_id(self) -> int:
        """次のいいねIDを取得"""
        existing_likes = [f for f in os.listdir(self.likes_dir) if f.endswith('.json')]
        if not existing_likes:
            return 1
        
        max_id = 0
        for filename in existing_likes:
            try:
                like_id = int(filename.replace('.json', '').replace('like_', ''))
                max_id = max(max_id, like_id)
            except ValueError:
                continue
        
        return max_id + 1
    
    def save_like(self, post_id: int, user_id: str, display_name: str) -> int:
        """いいねを保存"""
        like_id = self.get_next_like_id()
        
        like_data = {
            "id": like_id,
            "post_id": post_id,
            "user_id": user_id,
            "display_name": display_name,
            "created_at": datetime.now().isoformat()
        }
        
        filename = os.path.join(self.likes_dir, f"like_{like_id}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(like_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"いいねを保存しました: like_id={like_id}, post_id={post_id}, user_id={user_id}")
        return like_id
    
    def get_likes(self, post_id: int) -> List[Dict[str, Any]]:
        """投稿のいいねを取得"""
        likes = []
        
        for filename in sorted(os.listdir(self.likes_dir)):
            if filename.startswith('like_') and filename.endswith('.json'):
                try:
                    with open(os.path.join(self.likes_dir, filename), 'r', encoding='utf-8') as f:
                        like = json.load(f)
                    
                    if like.get('post_id') == post_id:
                        likes.append(like)
                except (json.JSONDecodeError, FileNotFoundError):
                    continue
        
        return likes
    
    def get_like_by_user_and_post(self, post_id: int, user_id: str) -> Optional[Dict[str, Any]]:
        """ユーザーといいねされた投稿IDからいいねデータを取得"""
        for filename in os.listdir(self.likes_dir):
            if filename.startswith('like_') and filename.endswith('.json'):
                try:
                    with open(os.path.join(self.likes_dir, filename), 'r', encoding='utf-8') as f:
                        like_data = json.load(f)
                    
                    if (like_data.get('post_id') == post_id and 
                        like_data.get('user_id') == user_id):
                        return like_data
                except (json.JSONDecodeError, FileNotFoundError):
                    continue
        return None
    
    def delete_like(self, post_id: int, user_id: str) -> bool:
        """いいねを削除"""
        like_data = self.get_like_by_user_and_post(post_id, user_id)
        if not like_data:
            return False
        
        filename = os.path.join(self.likes_dir, f"like_{like_data['id']}.json")
        try:
            os.remove(filename)
            return True
        except FileNotFoundError:
            return False
    
    def update_like_message_id(self, like_id: int, message_id: str, channel_id: str, forwarded_message_id: str = None) -> None:
        """いいねファイルにメッセージIDを更新"""
        filename = os.path.join(self.likes_dir, f"like_{like_id}.json")
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                like_data = json.load(f)
            
            like_data['message_id'] = message_id
            like_data['channel_id'] = channel_id
            if forwarded_message_id:
                like_data['forwarded_message_id'] = forwarded_message_id
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(like_data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"いいねメッセージIDを更新しました: like_id={like_id}")
        except (json.JSONDecodeError, FileNotFoundError):
            logger.warning(f"いいねメッセージID更新失敗: like_id={like_id}")
