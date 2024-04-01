from django.conf import settings
import hashlib
def md5(string):
    hand_object = hashlib.md5(settings.SECRET_KEY.encode("utf-8"))
    hand_object.update(string.encode("utf-8"))
    return hand_object.hexdigest()