import discord
from core.backup_manager import BackupManager


class DiffEngine:
    """Compara um backup salvo contra o estado atual do servidor, sem alterar nada."""

    def __init__(self):
        self.bm = BackupManager()

    def compare(self, guild: discord.Guild, backup: dict) -> dict:
        current = self.bm.create_backup(guild, created_by="diff-temporario")

        return {
            "cargos": self._diff_list(
                backup["roles"],
                current["roles"],
                key="id",
                compare_fields=["name", "color", "permissions", "hoist", "mentionable", "position"],
            ),
            "categorias": self._diff_list(
                backup["categories"], current["categories"], key="id",
                compare_fields=["name", "position"],
            ),
            "canais": self._diff_list(
                backup["channels"], current["channels"], key="id",
                compare_fields=["name", "type", "category_id", "position", "topic", "nsfw", "slowmode_delay"],
            ),
            "emojis": self._diff_list(
                backup["emojis"], current["emojis"], key="id", compare_fields=["name"],
            ),
        }

    @staticmethod
    def _diff_list(old_list, new_list, key, compare_fields):
        old_map = {item[key]: item for item in old_list}
        new_map = {item[key]: item for item in new_list}

        # Existia no backup mas não existe mais agora -> seria recriado num restore
        faltando_no_atual = [old_map[k] for k in old_map if k not in new_map]
        # Existe agora mas não existia no backup
        novo_no_atual = [new_map[k] for k in new_map if k not in old_map]

        modificado = []
        for k in old_map:
            if k in new_map:
                old_item, new_item = old_map[k], new_map[k]
                diffs = {}
                for field_ in compare_fields:
                    if old_item.get(field_) != new_item.get(field_):
                        diffs[field_] = {"backup": old_item.get(field_), "atual": new_item.get(field_)}
                if diffs:
                    modificado.append({"id": k, "name": old_item.get("name", "?"), "diffs": diffs})

        return {
            "faltando_no_atual": faltando_no_atual,
            "novo_no_atual": novo_no_atual,
            "modificado": modificado,
        }

    @staticmethod
    def summarize(diff: dict) -> str:
        lines = []
        for categoria, resultado in diff.items():
            faltando = len(resultado["faltando_no_atual"])
            novo = len(resultado["novo_no_atual"])
            modificado = len(resultado["modificado"])
            if faltando or novo or modificado:
                lines.append(
                    f"**{categoria.capitalize()}**: {faltando} ausentes, {novo} novos, {modificado} modificados"
                )
        if not lines:
            return "✅ Nenhuma diferença encontrada. O servidor está idêntico ao backup."
        return "\n".join(lines)
