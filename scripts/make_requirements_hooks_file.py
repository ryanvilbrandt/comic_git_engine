import os
from typing import Set

from build_site import get_extra_comics_list, get_extra_comic_info
from utils import find_project_root, str_to_list, read_info


def get_requirements(theme: str) -> Set[str]:
    requirements_path = f"your_content/themes/{theme}/scripts/requirements.txt"
    if os.path.exists(requirements_path):
        with open(requirements_path) as f:
            return set(str_to_list(f.read().replace("\r", ""), delimiter="\n"))
    return set()


def main():
    find_project_root()
    comic_info = read_info("your_content/comic_info.ini")
    theme = comic_info.get("Comic Settings", "Theme", fallback="default")
    requirements = get_requirements(theme)
    print(requirements)
    # Build any extra comics that may be needed
    for extra_comic in get_extra_comics_list(comic_info):
        print(extra_comic)
        extra_comic_info = get_extra_comic_info(extra_comic, comic_info)
        theme = extra_comic_info.get("Comic Settings", "Theme", fallback="default")
        if theme:
            requirements.update(get_requirements(theme))
            print(requirements)
    with open("comic_git_engine/scripts/requirements_hooks.txt", "w") as f:
        f.write("\n".join(requirements))


if __name__ == "__main__":
    main()
