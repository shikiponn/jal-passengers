import logging
import yaml

logger = logging.getLogger(__name__)

def load_yml(fpath: str):

    with open(fpath) as file:
        data= yaml.safe_load(file)
    return data


def load_config(fpath:str):
    dict_config = load_yml(fpath)
    logger.info(f"Read yml of {dict_config}")
    # 必要な処理があれば
    return dict_config