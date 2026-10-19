from urllib.parse import unquote, unquote_plus

def extract_s3_key(key: str) -> dict:
    key_info = {}
    y = key.split("/")
    key_info["source"] = y[2]
    key_info["year"] = int(unquote(y[3]).split("=")[1])
    key_info["month"] = int(unquote(y[4]).split("=")[1])
    key_info["file_name"] = y[5]
    key_info["decoded_key"] = unquote_plus(key)
    return key_info

