import json
import urllib.request
from PIL import Image
import logging

log = logging.getLogger('bot.' + __name__)


class Mojang:

    def __init__(self):
        pass

    def mojang_status_loop(self):
        # todo: probably should finish this
        pass

    @staticmethod
    def mojang_status():
        with urllib.request.urlopen("https://status.mojang.com/check") as url:
            data = json.loads(url.read().decode())
            yellow = []
            red = []
            for service in data:
                for s, t in service.items():
                    if t == "yellow":
                        yellow.append(s)
                    elif t == "red":
                        red.append(s)
        return [red, yellow]

    @staticmethod
    def mojang_user_to_uuid(username):
        with urllib.request.urlopen("https://api.mojang.com/users/profiles/minecraft/%s" % username) as url:
            data = json.loads(url.read().decode())
        return data['id']

    def mojang_get_user_avatar(self, username):
        uuid = self.mojang_user_to_uuid(username)
        # payload = base64.decode(self._get_avatar_payload(uuid), )

    @staticmethod
    def _get_avatar_payload(uuid: int):
        with urllib.request.urlopen("https://sessionserver.mojang.com/session/minecraft/profile/%s" % uuid) as url:
            data = json.loads(url.read().decode())
        return data['properties'][0]['textures']

    @staticmethod
    def get_face_from_skin(skin: Image) -> Image:
        """Return the portion of a Minecraft skin that represents the face."""
        face_zone = (8, 8, 16, 16)
        return skin.crop(face_zone)
