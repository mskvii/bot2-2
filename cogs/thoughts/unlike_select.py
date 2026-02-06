"""
unlike UIコンポーネント
"""

import discord
from discord import app_commands, ui, Interaction
from discord.ext import commands
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class UnlikeSelectView(ui.View):
    """いいね選択用ビュー（unlike）"""
    
    def __init__(self, items: List[Dict[str, Any]], cog):
        super().__init__(timeout=None)
        self.items = items
        self.cog = cog
        
        # いいね選択メニューを作成
        options = []
        for item in items[:25]:  # Discordの制限で25件まで
            post_content = item.get('post_content', '内容不明')[:50] + "..." if len(item.get('post_content', '')) > 50 else item.get('post_content', '内容不明')
            options.append(
                discord.SelectOption(
                    label=f"いいね ID: {item['id']} (投稿ID: {item['post_id']})",
                    description=f"{post_content} - {item.get('created_at', '')[:10]}",
                    value=f"like_{item['id']}"
                )
            )
        
        self.select_menu = ui.Select(
            placeholder="削除するいいねを選択...",
            options=options,
            min_values=1,
            max_values=1
        )
        self.select_menu.callback = self.select_callback
        self.add_item(self.select_menu)
    
    async def select_callback(self, interaction: Interaction):
        """選択されたいいねを削除"""
        try:
            selected_value = self.select_menu.values[0]
            
            if selected_value.startswith("like_"):
                like_id = int(selected_value.split("_")[1])
                like_data = next((item for item in self.items if item['id'] == like_id), None)
                
                if like_data:
                    # いいね削除処理を実行
                    await self.cog.process_unlike(interaction, like_data)
                else:
                    await interaction.response.send_message("いいねデータが見つかりません。", ephemeral=True)
            else:
                await interaction.response.send_message("無効な選択です。", ephemeral=True)
                
        except Exception as e:
            logger.error(f"いいね選択エラー: {e}")
            await interaction.response.send_message("エラーが発生しました。もう一度お試しください。", ephemeral=True)
