import discord
import asyncio

RATE_LIMIT_DELAY = 1.0  # segundos entre chamadas de API para evitar rate limit do Discord


class RestoreManager:
    """Aplica (ou simula, em modo dry_run) a restauração de partes específicas de um backup."""

    def __init__(self):
        self.report: list = []

    def _log(self, msg: str):
        self.report.append(msg)

    async def restore_roles(self, guild: discord.Guild, backup: dict, dry_run: bool = False) -> list:
        self.report = []
        existing_roles = {r.id: r for r in guild.roles}
        backup_roles = sorted(backup["roles"], key=lambda r: r["position"])

        for role_data in backup_roles:
            role = existing_roles.get(role_data["id"])
            perms = discord.Permissions(role_data["permissions"])
            color = discord.Color(role_data["color"])

            if role is None:
                self._log(f"➕ Criar cargo '{role_data['name']}'")
                if not dry_run:
                    await guild.create_role(
                        name=role_data["name"],
                        permissions=perms,
                        color=color,
                        hoist=role_data["hoist"],
                        mentionable=role_data["mentionable"],
                        reason="Restauração de backup",
                    )
                    await asyncio.sleep(RATE_LIMIT_DELAY)
            else:
                changed = (
                    role.name != role_data["name"]
                    or role.permissions.value != role_data["permissions"]
                    or role.color.value != role_data["color"]
                    or role.hoist != role_data["hoist"]
                    or role.mentionable != role_data["mentionable"]
                )
                if changed:
                    self._log(f"✏️ Atualizar cargo '{role.name}'")
                    if not dry_run:
                        await role.edit(
                            name=role_data["name"],
                            permissions=perms,
                            color=color,
                            hoist=role_data["hoist"],
                            mentionable=role_data["mentionable"],
                            reason="Restauração de backup",
                        )
                        await asyncio.sleep(RATE_LIMIT_DELAY)

        if not self.report:
            self._log("Nenhuma alteração necessária nos cargos.")
        return self.report

    async def restore_categories(self, guild: discord.Guild, backup: dict, dry_run: bool = False) -> list:
        self.report = []
        existing = {c.id: c for c in guild.categories}

        for cat_data in sorted(backup["categories"], key=lambda c: c["position"]):
            cat = existing.get(cat_data["id"])
            if cat is None:
                self._log(f"➕ Criar categoria '{cat_data['name']}'")
                if not dry_run:
                    await guild.create_category(name=cat_data["name"], reason="Restauração de backup")
                    await asyncio.sleep(RATE_LIMIT_DELAY)
            elif cat.name != cat_data["name"]:
                self._log(f"✏️ Renomear categoria '{cat.name}' → '{cat_data['name']}'")
                if not dry_run:
                    await cat.edit(name=cat_data["name"], reason="Restauração de backup")
                    await asyncio.sleep(RATE_LIMIT_DELAY)

        if not self.report:
            self._log("Nenhuma alteração necessária nas categorias.")
        return self.report

    async def restore_channels(self, guild: discord.Guild, backup: dict, dry_run: bool = False) -> list:
        self.report = []
        existing = {c.id: c for c in guild.channels if not isinstance(c, discord.CategoryChannel)}
        category_map = {c.id: c for c in guild.categories}

        for ch_data in sorted(backup["channels"], key=lambda c: c["position"]):
            ch = existing.get(ch_data["id"])
            category = category_map.get(ch_data["category_id"])

            if ch is None:
                self._log(f"➕ Criar canal '{ch_data['name']}' ({ch_data['type']})")
                if not dry_run:
                    if ch_data["type"] == "voice":
                        await guild.create_voice_channel(
                            name=ch_data["name"], category=category, reason="Restauração de backup"
                        )
                    else:
                        await guild.create_text_channel(
                            name=ch_data["name"],
                            category=category,
                            topic=ch_data.get("topic"),
                            nsfw=ch_data.get("nsfw", False),
                            reason="Restauração de backup",
                        )
                    await asyncio.sleep(RATE_LIMIT_DELAY)
            else:
                changed = ch.name != ch_data["name"]
                if isinstance(ch, discord.TextChannel):
                    changed = (
                        changed
                        or ch.topic != ch_data.get("topic")
                        or ch.nsfw != ch_data.get("nsfw", False)
                    )
                if changed:
                    self._log(f"✏️ Atualizar canal '{ch.name}'")
                    if not dry_run:
                        kwargs = {"name": ch_data["name"], "reason": "Restauração de backup"}
                        if isinstance(ch, discord.TextChannel):
                            kwargs["topic"] = ch_data.get("topic")
                            kwargs["nsfw"] = ch_data.get("nsfw", False)
                        await ch.edit(**kwargs)
                        await asyncio.sleep(RATE_LIMIT_DELAY)

        if not self.report:
            self._log("Nenhuma alteração necessária nos canais.")
        return self.report

    async def restore_member_roles(self, guild: discord.Guild, backup: dict, dry_run: bool = False) -> list:
        self.report = []
        role_map = {r.id: r for r in guild.roles}

        for member_data in backup["members"]:
            member = guild.get_member(member_data["id"])
            if member is None:
                continue  # Membro saiu do servidor; Discord não permite re-adicionar via bot.

            target_role_ids = set(member_data["role_ids"])
            current_role_ids = {r.id for r in member.roles if not r.is_default()}

            to_add = [role_map[rid] for rid in target_role_ids - current_role_ids if rid in role_map]
            to_remove = [role_map[rid] for rid in current_role_ids - target_role_ids if rid in role_map]

            if to_add or to_remove:
                self._log(f"👤 {member_data['name']}: +{len(to_add)} cargo(s), -{len(to_remove)} cargo(s)")
                if not dry_run:
                    if to_add:
                        await member.add_roles(*to_add, reason="Restauração de backup")
                    if to_remove:
                        await member.remove_roles(*to_remove, reason="Restauração de backup")
                    await asyncio.sleep(RATE_LIMIT_DELAY)

            if member_data.get("nickname") != member.nick:
                self._log(f"👤 {member_data['name']}: apelido '{member.nick}' → '{member_data['nickname']}'")
                if not dry_run:
                    try:
                        await member.edit(nick=member_data.get("nickname"), reason="Restauração de backup")
                    except discord.Forbidden:
                        self._log(f"⚠️ Sem permissão para renomear {member_data['name']}")
                    await asyncio.sleep(RATE_LIMIT_DELAY)

        if not self.report:
            self._log("Nenhuma alteração necessária nos membros.")
        return self.report

    async def restore_all(self, guild: discord.Guild, backup: dict, dry_run: bool = False) -> dict:
        return {
            "roles": await self.restore_roles(guild, backup, dry_run),
            "categories": await self.restore_categories(guild, backup, dry_run),
            "channels": await self.restore_channels(guild, backup, dry_run),
        }
