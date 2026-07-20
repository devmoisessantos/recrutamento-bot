import discord
import json
import os
import datetime
from typing import Optional

from src.config import BACKUP_DIR, MAX_BACKUPS_PER_GUILD


class BackupManager:
    """Responsável por serializar o estado do servidor e gravar/ler backups em JSON."""

    def __init__(self):
        os.makedirs(BACKUP_DIR, exist_ok=True)

    def _guild_dir(self, guild_id: int) -> str:
        path = os.path.join(BACKUP_DIR, str(guild_id))
        os.makedirs(path, exist_ok=True)
        return path

    # ---------- Serialização ----------

    @staticmethod
    def _serialize_overwrites(overwrites) -> list:
        result = []
        for target, perm in overwrites.items():
            target_type = "role" if isinstance(target, discord.Role) else "member"
            allow, deny = perm.pair()
            result.append(
                {
                    "target_type": target_type,
                    "target_id": target.id,
                    "target_name": target.name,
                    "allow": allow.value,
                    "deny": deny.value,
                }
            )
        return result

    def _serialize_roles(self, guild: discord.Guild) -> list:
        roles = []
        for role in guild.roles:
            if role.is_default():
                continue
            roles.append(
                {
                    "id": role.id,
                    "name": role.name,
                    "color": role.color.value,
                    "hoist": role.hoist,
                    "mentionable": role.mentionable,
                    "permissions": role.permissions.value,
                    "position": role.position,
                }
            )
        return roles

    def _serialize_categories(self, guild: discord.Guild) -> list:
        categories = []
        for cat in guild.categories:
            categories.append(
                {
                    "id": cat.id,
                    "name": cat.name,
                    "position": cat.position,
                    "overwrites": self._serialize_overwrites(cat.overwrites),
                }
            )
        return categories

    def _serialize_channels(self, guild: discord.Guild) -> list:
        channels = []
        for ch in guild.channels:
            if isinstance(ch, discord.CategoryChannel):
                continue
            data = {
                "id": ch.id,
                "name": ch.name,
                "type": str(ch.type),
                "category_id": ch.category_id,
                "position": ch.position,
                "overwrites": self._serialize_overwrites(ch.overwrites),
            }
            if isinstance(ch, discord.TextChannel):
                data["topic"] = ch.topic
                data["nsfw"] = ch.nsfw
                data["slowmode_delay"] = ch.slowmode_delay
            elif isinstance(ch, discord.VoiceChannel):
                data["bitrate"] = ch.bitrate
                data["user_limit"] = ch.user_limit
            channels.append(data)
        return channels

    def _serialize_emojis(self, guild: discord.Guild) -> list:
        return [
            {"id": e.id, "name": e.name, "url": str(e.url), "animated": e.animated}
            for e in guild.emojis
        ]

    def _serialize_server_settings(self, guild: discord.Guild) -> dict:
        return {
            "name": guild.name,
            "icon_url": str(guild.icon.url) if guild.icon else None,
            "banner_url": str(guild.banner.url) if guild.banner else None,
            "afk_timeout": guild.afk_timeout,
            "afk_channel_id": guild.afk_channel.id if guild.afk_channel else None,
            "verification_level": str(guild.verification_level),
            "explicit_content_filter": str(guild.explicit_content_filter),
        }

    def _serialize_members(self, guild: discord.Guild) -> list:
        members = []
        for m in guild.members:
            if m.bot:
                continue
            members.append(
                {
                    "id": m.id,
                    "name": str(m),
                    "nickname": m.nick,
                    "role_ids": [r.id for r in m.roles if not r.is_default()],
                }
            )
        return members

    def create_backup(self, guild: discord.Guild, created_by: str) -> dict:
        return {
            "guild_id": guild.id,
            "guild_name": guild.name,
            "created_at": datetime.datetime.utcnow().isoformat(),
            "created_by": created_by,
            "roles": self._serialize_roles(guild),
            "categories": self._serialize_categories(guild),
            "channels": self._serialize_channels(guild),
            "emojis": self._serialize_emojis(guild),
            "server_settings": self._serialize_server_settings(guild),
            "members": self._serialize_members(guild),
        }

    # ---------- Persistência ----------

    def save_backup(self, backup: dict) -> str:
        guild_dir = self._guild_dir(backup["guild_id"])
        timestamp = backup["created_at"].replace(":", "-")
        filename = f"backup_{timestamp}.json"
        path = os.path.join(guild_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(backup, f, indent=2, ensure_ascii=False)
        self._prune_old_backups(backup["guild_id"])
        return path

    def _prune_old_backups(self, guild_id: int):
        guild_dir = self._guild_dir(guild_id)
        files = sorted(
            [f for f in os.listdir(guild_dir) if f.endswith(".json")], reverse=True
        )
        for old_file in files[MAX_BACKUPS_PER_GUILD:]:
            os.remove(os.path.join(guild_dir, old_file))

    def list_backups(self, guild_id: int) -> list:
        guild_dir = self._guild_dir(guild_id)
        return sorted(
            [f for f in os.listdir(guild_dir) if f.endswith(".json")], reverse=True
        )

    def load_backup(self, guild_id: int, filename: str) -> Optional[dict]:
        path = os.path.join(self._guild_dir(guild_id), filename)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def delete_backup(self, guild_id: int, filename: str) -> bool:
        path = os.path.join(self._guild_dir(guild_id), filename)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    def latest_backup_filename(self, guild_id: int) -> Optional[str]:
        files = self.list_backups(guild_id)
        return files[0] if files else None
