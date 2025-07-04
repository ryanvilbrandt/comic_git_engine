import argparse
import html
import os
import re
import shutil
import sys
import traceback
from collections import OrderedDict, defaultdict
from configparser import RawConfigParser
from copy import deepcopy
from datetime import datetime
from glob import glob
from importlib import import_module
from json import dumps
from time import strptime, strftime, perf_counter_ns
from typing import Dict, List, Tuple, Any, Optional

from PIL import Image
from markdown2 import Markdown
from pytz import timezone

import utils
from build_rss_feed import build_rss_feed
from utils import read_info

VERSION = "0.4.3"

BASE_DIRECTORY = ""
MARKDOWN = Markdown(extras=["strike", "break-on-newline", "markdown-in-html"])
PROCESSING_TIMES: List[Tuple[str, float]] = []


def web_path(rel_path: str):
    if rel_path.startswith("/"):
        return BASE_DIRECTORY + rel_path
    return rel_path


def delete_output_file_space(comic_info: RawConfigParser = None):
    shutil.rmtree("comic", ignore_errors=True)
    if os.path.isfile("feed.xml"):
        os.remove("feed.xml")
    if comic_info is None:
        comic_info = read_info("your_content/comic_info.ini")
    for page in get_pages_list(comic_info):
        if page["template_name"] == "index":
            if os.path.exists("index.html"):
                os.remove("index.html")
        elif page["template_name"] == "404":
            if os.path.exists("404.html"):
                os.remove("404.html")
        else:
            if os.path.exists(page["template_name"]):
                shutil.rmtree(page["template_name"])
    for comic in get_extra_comics_list(comic_info):
        if os.path.exists(comic):
            shutil.rmtree(comic)


def setup_output_file_space(comic_info: RawConfigParser):
    # Clean workspace, i.e. delete old files
    delete_output_file_space(comic_info)


def get_links_list(comic_info: RawConfigParser):
    link_list = []
    for option in comic_info.options("Links Bar"):
        link_list.append({"name": option, "url": web_path(comic_info.get("Links Bar", option))})
    return link_list


def get_pages_list(comic_info: RawConfigParser, section_name="Pages"):
    if comic_info.has_section("Pages"):
        return [{"template_name": option, "title": comic_info.get(section_name, option)}
                for option in comic_info.options(section_name)]
    return []


def get_extra_comics_list(comic_info: RawConfigParser) -> List[str]:
    return utils.str_to_list(comic_info.get("Comic Settings", "Extra comics", fallback=""))


def run_hook(theme: str, func: str, args: List[Any]) -> Any:
    """
    Determines if the hooks.py file has been added to the given theme, and if that file contains the given function.
    If so, it will call that function with the given args.
    :param theme: Name of the theme to check in for the hooks.py file
    :param func: Function name to call
    :param args: Args list to pass to the function
    :return: The return value of the function called, if one was found. Otherwise, None.
    """
    if os.path.exists(f"your_content/themes/{theme}/scripts/hooks.py"):
        current_path = os.path.abspath(".")
        if current_path not in sys.path:
            sys.path.append(current_path)
            print(f"Path updated: {sys.path}")
        hooks = import_module(f"your_content.themes.{theme}.scripts.hooks")
        if hasattr(hooks, func):
            method = getattr(hooks, func)
            return method(*args)
    return None


def build_and_publish_comic_pages(
        comic_url: str,
        comic_folder: str,
        comic_info: RawConfigParser,
        delete_scheduled_posts: bool,
        publish_all_comics: bool,
        extra_comics_dict: Optional[dict] = None,
) -> tuple[list[dict], dict]:
    page_info_list, scheduled_post_count = get_page_info_list(
        comic_folder, comic_info, delete_scheduled_posts, publish_all_comics
    )
    print([p["page_name"] for p in page_info_list])
    checkpoint(f"Get info for all pages in '{comic_folder}'")

    # Save page_info_list.json file for use by other pages
    save_page_info_json_file(comic_folder, page_info_list, scheduled_post_count)
    checkpoint(f"Save page_info_list.json file in '{comic_folder}'")

    # Build full comic data dicts, to build templates with
    comic_data_dicts = build_comic_data_dicts(comic_folder, comic_info, page_info_list)
    checkpoint(f"Build full comic data dicts for '{comic_folder}'")

    # Create low-res and thumbnail versions of all the comic pages
    process_comic_images(comic_info, comic_data_dicts)
    checkpoint(f"Process comic images in '{comic_folder}'")

    # Load home page text
    if os.path.isfile(f"your_content/{comic_folder}home page.txt"):
        with open(f"your_content/{comic_folder}home page.txt", "rb") as f:
            home_page_text = MARKDOWN.convert(f.read().decode("utf-8"))
    else:
        home_page_text = ""

    # Write page info to comic HTML pages

    # e.g. /base_dir/extra_comic
    comic_base_dir = f"{BASE_DIRECTORY}/{comic_folder}".rstrip("/")
    # e.g. /base_dir/your_content/extra_comic
    content_base_dir = f"{BASE_DIRECTORY}/your_content/{comic_folder}".rstrip("/")
    global_values = {
        "version": VERSION,
        "comic_title": comic_info.get("Comic Info", "Comic name"),
        "comic_author": comic_info.get("Comic Info", "Author"),
        "comic_description": comic_info.get("Comic Info", "Description"),
        "banner_image": web_path(
            comic_info.get("Comic Settings", "Banner image", fallback="/your_content/images/banner.png")
        ),
        "theme": comic_info.get("Comic Settings", "Theme", fallback="default"),
        "comic_url": comic_url,
        "comic_folder": comic_folder,
        "base_dir": BASE_DIRECTORY,
        "comic_base_dir": comic_base_dir,
        "content_base_dir": content_base_dir,
        "links": get_links_list(comic_info),
        "use_images_in_navigation_bar": comic_info.getboolean("Comic Settings", "Use images in navigation bar"),
        "use_thumbnails": comic_info.getboolean("Archive", "Use thumbnails"),
        "storylines": get_storylines(comic_info, comic_data_dicts),
        "home_page_text": home_page_text,
        "google_analytics_id": comic_info.get("Google Analytics", "Tracking ID", fallback=""),
        "scheduled_post_count": scheduled_post_count,
        "extra_comics": extra_comics_dict if extra_comics_dict is not None else {},
    }
    # Update the global values with any custom values returned by the hook.py file's extra_global_value's function
    extra_global_variables = run_hook(
        global_values["theme"],
        "extra_global_values",
        [comic_folder, comic_info, comic_data_dicts]
    )
    if extra_global_variables:
        global_values.update(extra_global_variables)
    checkpoint(f"Run hook for extra global values in '{comic_folder}'")
    write_html_files(comic_folder, comic_info, comic_data_dicts, global_values)
    checkpoint(f"Write HTML files for '{comic_folder}'")
    return comic_data_dicts, global_values


def get_page_info_list(comic_folder: str, comic_info: RawConfigParser, delete_scheduled_posts: bool,
                       publish_all_comics: bool) -> Tuple[List[Dict], int]:
    date_format = comic_info.get("Comic Settings", "Date format")
    tz_info = timezone(comic_info.get("Comic Settings", "Timezone"))
    local_time = datetime.now(tz=tz_info)
    print(f"Local time is {local_time}")
    page_info_list = []
    scheduled_post_count = 0
    theme = comic_info.get("Comic Settings", "Theme", fallback="default")
    for page_path in glob(f"your_content/{comic_folder}comics/*/"):
        filepath = f"{page_path}info.ini"
        if not os.path.exists(f"{page_path}info.ini"):
            print(f"{page_path} is missing its info.ini file. Skipping")
            continue
        page_info = read_info(filepath, to_dict=True)
        post_date = tz_info.localize(datetime.strptime(page_info["Post date"], date_format))
        if post_date > local_time and not publish_all_comics:
            scheduled_post_count += 1
            # Post date is in the future, so delete the folder with the resources
            if delete_scheduled_posts:
                print(f"Deleting {page_path}")
                shutil.rmtree(page_path)
        else:
            filenames = page_info.get("Filenames") or page_info.get("Filename", "")
            if filenames:
                page_info["image_file_names"] = utils.str_to_list(filenames)
            else:
                # If Filenames weren't defined in the info.ini, then search through all images in the given comic
                # folder and add any you find to the list of image files.
                # Skip any image files whose names start with an underscore.
                image_files = []
                for filename in os.listdir(page_path):
                    if filename.startswith("_"):
                        continue
                    if re.search(r"\.(jpg|jpeg|png|tif|tiff|gif|bmp|webp|webv|svg|eps)$", filename):
                        image_files.append(filename)
                page_info["image_file_names"] = sorted(image_files)
            page_info["page_name"] = os.path.basename(os.path.normpath(page_path))
            page_info["Storyline"] = page_info.get("Storyline", "")
            page_info["Characters"] = utils.str_to_list(page_info.get("Characters", ""))
            page_info["Tags"] = utils.str_to_list(page_info.get("Tags", ""))
            # Remove all keys in page_info that start with !, so creators don't have to worry about these
            # showing up in page_info_list.json
            for key in page_info.copy():
                if key.startswith("!"):
                    del page_info[key]
            # Get list of transcript languages for the given page
            transcripts = get_transcripts(comic_folder, comic_info, page_info["page_name"])
            page_info["transcript_languages"] = list(transcripts.keys())
            hook_result = run_hook(theme, "extra_page_info_processing",
                                   [comic_folder, comic_info, page_path, page_info])
            if hook_result:
                page_info = hook_result
            print(page_info)
            page_info_list.append(page_info)

    page_info_list = sorted(
        page_info_list,
        key=lambda x: (strptime(x["Post date"], date_format), x["page_name"])
    )
    return page_info_list, scheduled_post_count


def save_page_info_json_file(comic_folder: str, page_info_list: List, scheduled_post_count: int):
    d = {
        "page_info_list": page_info_list,
        "scheduled_post_count": scheduled_post_count
    }
    os.makedirs(f"{comic_folder}comic", exist_ok=True)
    with open(f"{comic_folder}comic/page_info_list.json", "w") as f:
        f.write(dumps(d))


def get_ids(comic_list: List[Dict], index):
    return {
        "first_id": comic_list[0]["page_name"],
        "previous_id": comic_list[max(0, index - 1)]["page_name"],
        "current_id": comic_list[index]["page_name"],
        "next_id": comic_list[min(len(comic_list) - 1, index + 1)]["page_name"],
        "last_id": comic_list[-1]["page_name"]
    }


def get_transcripts(comic_folder: str, comic_info: RawConfigParser, page_name: str) -> OrderedDict:
    if not comic_info.getboolean("Transcripts", "Enable transcripts"):
        return OrderedDict()
    transcripts = OrderedDict()
    if comic_info.getboolean("Transcripts", "Load transcripts from comic folder", fallback=True):
        transcripts.update(load_transcripts_from_folder(f"your_content/{comic_folder}comics", page_name))
    transcripts_dir = comic_info.get("Transcripts", "Transcripts folder", fallback="")
    if transcripts_dir:
        transcripts.update(load_transcripts_from_folder(transcripts_dir, page_name))
    default_language = comic_info.get("Transcripts", "Default language", fallback="English")
    if default_language in transcripts:
        transcripts.move_to_end(default_language, last=False)
    return transcripts


def load_transcripts_from_folder(transcripts_dir: str, page_name: str):
    """
    Loads both *.txt and *.md files from the transcripts folder, as defined in the config file. If two files exist
    with the same name (e.g. English.txt and English.md), then the *.md file will take precedence.
    :param transcripts_dir:
    :param page_name:
    :return:
    """
    extensions = ["*.txt", "*.md"]
    transcripts = {}
    for ext in extensions:
        for transcript_path in sorted(glob(os.path.join(transcripts_dir, page_name, ext))):
            # Ignore the post.txt in the comic folders
            if transcript_path.endswith("post.txt"):
                continue
            language = os.path.splitext(os.path.basename(transcript_path))[0]
            with open(transcript_path, "rb") as f:
                text = f.read()
                try:
                    text = text.decode("utf-8")
                except UnicodeDecodeError:
                    text = text.decode("latin-1")
                transcripts[language] = MARKDOWN.convert(text)
    return transcripts


def format_user_variable(k: str) -> str:
    """
    Option names passed in by the user from their info.ini files can have any string values like "Post date" or
    "This page is full of spiders!!1". The option names are then passed on to Jinja2 templates as variable names.
    Unfortunately, Jinja2 variable names are much more limited in what characters they can contain than
    option names, i.e., no spaces or hyphens.

    To work around this, we will replace all non-alphanumeric (and non-underscore) characters with an underscore.
    Multiples of those characters in a row will be converted to a single underscore. We will also convert all
    variables to lowercase to make their format more consistent with regular variable naming. We will then strip
    leading and trailing underscores from the name.

    Lastly, we will prepend the variable with an underscore to represent it as a converted user variable.
    This will prevent user variables from accidentally overwriting system variables, like "page_num" or "comic_url".

    Example: Post date => _post_date
    :param k:
    :return:
    """
    k = re.sub(r"[^a-z0-9_]+", "_", k.lower()).strip("_")
    if k not in ["page_name"]:
        k = "_" + k
    return k


def create_comic_data(comic_folder: str, comic_info: RawConfigParser, page_info: dict,
                      first_id: str, previous_id: str, current_id: str, next_id: str, last_id: str):
    t = strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{t}] Building page {page_info['page_name']}...")
    page_dir = f"your_content/{comic_folder}comics/{page_info['page_name']}/"
    archive_post_date = strftime(
        comic_info.get("Archive", "Date format"),
        strptime(
            page_info["Post date"],
            comic_info.get("Comic Settings", "Date format")
        )
    )
    post_html = []
    post_text_paths = [
        f"your_content/{comic_folder}before post text.txt",
        f"your_content/{comic_folder}before post text.html",
        page_dir + "post.txt",
        f"your_content/{comic_folder}after post text.txt",
        f"your_content/{comic_folder}after post text.html",
    ]
    for post_text_path in post_text_paths:
        if os.path.exists(post_text_path):
            with open(post_text_path, "rb") as f:
                post_html.append(f.read().decode("utf-8"))
    post_html = MARKDOWN.convert("\n\n".join(post_html))
    d = {
        "comic_paths": [os.path.join(page_dir, f) for f in page_info["image_file_names"]],
        "thumbnail_path": os.path.join(page_dir, "_thumbnail.jpg"),
        "escaped_alt_text": html.escape(page_info["Alt text"]),
        "first_id": first_id,
        "previous_id": previous_id,
        "current_id": current_id,
        "next_id": next_id,
        "last_id": last_id,
        "archive_post_date": archive_post_date,
        "post_html": post_html,
        "transcripts": get_transcripts(comic_folder, comic_info, page_info["page_name"]),
    }
    # Copy in existing page info options to the data dict, but format them so they're proper Jinja2 variable names
    d.update({format_user_variable(k): v for k, v in page_info.items()})
    # Add an _on_comic_click option from global comic_info.ini if it doesn't exist in the per-comic info.ini
    if "_on_comic_click" not in d:
        d["_on_comic_click"] = comic_info.get("Comic Settings", "On comic click", fallback="Next comic")
    d["_on_comic_click"] = d["_on_comic_click"].lower()
    theme = comic_info.get("Comic Settings", "Theme", fallback="default")
    hook_result = run_hook(theme, "extra_comic_dict_processing", [comic_folder, comic_info, d])
    if hook_result:
        d = hook_result
    return d


def build_comic_data_dicts(comic_folder: str, comic_info: RawConfigParser, page_info_list: List[Dict]) -> List[Dict]:
    return [
        create_comic_data(comic_folder, comic_info, page_info, **get_ids(page_info_list, i))
        for i, page_info in enumerate(page_info_list)
    ]


def resize(im, size):
    image_width, image_height = im.size
    if "," in size:
        # Convert a string of the form "100, 36" into a 2-tuple of ints (100, 36)
        w, h = size.strip().split(",")
        w, h = w.strip(), h.strip()
    elif size.endswith("%"):
        # Convert a percentage (50%) into a new size (50, 18)
        size = float(size.strip().strip("%"))
        size = size / 100
        w, h = image_width * size, image_height * size
    elif size.endswith("h"):
        # Scale to set height and adjust width to keep the same aspect ratio
        h = int(size[:-1].strip())
        w = image_width / image_height * h
    elif size.endswith("w"):
        # Scale to set width and adjust height to keep the same aspect ratio
        w = int(size[:-1].strip())
        h = image_height / image_width * w
    else:
        raise ValueError("Unknown resize value: {!r}".format(size))
    return im.resize((int(w), int(h)))


def save_image(im, path):
    try:
        # If saving as JPEG, force-convert to RGB first
        if path.lower().endswith("jpg") or path.lower().endswith("jpeg"):
            if im.mode != 'RGB':
                im = im.convert('RGB')
        im.save(path)
    except OSError as e:
        if str(e) == "cannot write mode RGBA as JPEG":
            # Get rid of transparency
            bg = Image.new("RGB", im.size, "WHITE")
            bg.paste(im, (0, 0), im)
            bg.save(path)
        else:
            raise


def create_comic_thumbnail(comic_info, comic_page_path):
    section = "Image Reprocessing"
    comic_page_dir = os.path.dirname(comic_page_path)
    comic_page_name, comic_page_ext = os.path.splitext(os.path.basename(comic_page_path))
    with open(comic_page_path, "rb") as f:
        im = Image.open(f)
        thumbnail_path = os.path.join(comic_page_dir, "_thumbnail.jpg")
        if comic_info.getboolean(section, "Overwrite existing images") or not os.path.isfile(thumbnail_path):
            print(f"Creating thumbnail for {comic_page_name}")
            thumb_im = resize(im, comic_info.get(section, "Thumbnail size"))
            save_image(thumb_im, thumbnail_path)


def process_comic_images(comic_info: RawConfigParser, comic_data_dicts: List[Dict]):
    section = "Image Reprocessing"
    if comic_info.getboolean(section, "Create thumbnails"):
        for comic_data in comic_data_dicts:
            # We don't support multiple thumbnails per page, so pick the first image in the list
            create_comic_thumbnail(comic_info, comic_data["comic_paths"][0])


def get_storylines(comic_info: RawConfigParser, comic_data_dicts: List[Dict]) -> OrderedDict:
    # Start with an OrderedDict, so we can easily drop the pages we encounter in the proper buckets, while keeping
    # their proper order
    storylines_dict = OrderedDict()
    show_uncategorized = comic_info.getboolean("Archive", "Show Uncategorized comics", fallback=True)
    for comic_data in comic_data_dicts:
        storyline = comic_data["_storyline"]
        if not storyline:
            if not show_uncategorized:
                continue
            storyline = "Uncategorized"
        if storyline not in storylines_dict.keys():
            storylines_dict[storyline] = []
        storylines_dict[storyline].append(comic_data.copy())
    if "Uncategorized" in storylines_dict:
        storylines_dict.move_to_end("Uncategorized")
    hooked_storylines_dict = run_hook(
        comic_info.get("Comic Settings", "Theme", fallback="default"),
        "extra_get_storylines_processing",
        [comic_info, comic_data_dicts, storylines_dict]
    )
    return hooked_storylines_dict if hooked_storylines_dict is not None else storylines_dict


def write_html_files(comic_folder: str, comic_info: RawConfigParser, comic_data_dicts: List[Dict], global_values: Dict):
    # Load Jinja environment
    template_folders = ["comic_git_engine/templates"]
    theme = comic_info.get("Comic Settings", "Theme", fallback="default")
    if theme:
        template_folders.insert(0, f"your_content/themes/{theme}/templates")
        if comic_folder:
            template_folders.insert(0, f"your_content/themes/{theme}/templates/{comic_folder}")
    print(f"Template folders: {template_folders}")
    utils.build_jinja_environment(comic_info, template_folders)
    utils.build_markdown_parser(comic_info)
    # Write individual comic pages
    print("Writing {} comic pages...".format(len(comic_data_dicts)))
    for comic_data_dict in comic_data_dicts:
        html_path = f"{comic_folder}comic/{comic_data_dict['page_name']}/index.html"
        comic_data_dict.update(global_values)
        utils.write_to_template("comic", html_path, comic_data_dict)
    write_other_pages(comic_folder, comic_info, comic_data_dicts, global_values)
    run_hook(global_values["theme"], "build_other_pages", [comic_folder, comic_info, comic_data_dicts])


def write_other_pages(comic_folder: str, comic_info: RawConfigParser, comic_data_dicts: List[Dict],
                      global_values: Dict):
    base_data_dict = {}
    if not comic_data_dicts:
        print("You're publishing a website with no comic pages. Are you sure you want that??", file=sys.stderr)
        # Set a default page title, in case of a situation like wanting to
        # TODO Replace with a default comic_data_dict
        base_data_dict.update({"_title": "Index"})
    else:
        base_data_dict.update(comic_data_dicts[-1])
    base_data_dict.update(global_values)
    pages_list = get_pages_list(comic_info)
    for page in pages_list:
        # Special handling for tag pages
        if page["template_name"] == "tagged":
            write_tagged_pages(comic_data_dicts, base_data_dict)
            continue
        # If we're building the index or 404 pages, they should go in the root directory
        if page["template_name"].lower() in ("index", "404"):
            html_path = f"{page['template_name']}.html"
        else:
            html_path = os.path.join(page['template_name'], "index.html")
        # If we're processing an extra comic, prepend the extra comic path
        if comic_folder:
            html_path = os.path.join(comic_folder, html_path)
        # Don't build latest page if there are no comics published
        if page["template_name"] == "latest" and not comic_data_dicts:
            continue
        data_dict = base_data_dict.copy()
        if page["title"]:
            data_dict["_title"] = page["title"]
        utils.write_to_template(page["template_name"], html_path, data_dict)


def write_tagged_pages(comic_data_dicts: List[Dict], global_values: Dict):
    if not comic_data_dicts:
        return
    tags = defaultdict(list)
    for page in comic_data_dicts:
        for character in page.get("_characters", []):
            tags[character].append(page)
        for tag in page.get("_tags", []):
            tags[tag].append(page)
    for tag, pages in tags.items():
        data_dict = global_values.copy()
        data_dict.update({
            "_title": f"Posts tagged with {tag}",
            "tag": tag,
            "tagged_pages": pages
        })
        # Tag names can get weird, and it doesn't matter too much if their files don't get created.
        # Catch any exceptions and print the error, but let things continue if needed.
        filename = f"tagged/{tag}/index.html"
        try:
            utils.write_to_template("tagged", filename, data_dict)
        except Exception:
            print(f"Failed to create '{filename}' from 'tagged' template", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)


def get_extra_comic_info(folder_name: str, comic_info: RawConfigParser):
    comic_info = deepcopy(comic_info)
    # Always delete existing Pages section; by default, extra comic provides no additional pages
    del comic_info["Pages"]
    # Delete "Links Bar" from original if the extra comic's info has that section defined
    extra_comic_info = RawConfigParser()
    extra_comic_info.read(f"your_content/{folder_name}/comic_info.ini")
    if extra_comic_info.has_section("Links Bar"):
        del comic_info["Links Bar"]
    # Read the extra comic info in again, to merge with the original comic info
    comic_info.read(f"your_content/{folder_name}/comic_info.ini")
    return comic_info


def checkpoint(s: str):
    global PROCESSING_TIMES
    PROCESSING_TIMES.append((s, perf_counter_ns()))


def print_processing_times():
    print(PROCESSING_TIMES)
    last_processed_time = None
    print("")
    for name, t in PROCESSING_TIMES:
        if last_processed_time is not None:
            print("{}: {:.2f} ms".format(name, (t - last_processed_time) / 1_000_000))
        last_processed_time = t
    print("{}: {:.2f} ms".format("Total time", (PROCESSING_TIMES[-1][1] - PROCESSING_TIMES[0][1]) / 1_000_000))


def main(args: argparse.Namespace):
    global BASE_DIRECTORY
    checkpoint("Start")

    # Get site-wide settings for this comic
    utils.find_project_root()
    comic_info = read_info("your_content/comic_info.ini")
    comic_url, BASE_DIRECTORY = utils.get_comic_url(comic_info)
    theme = comic_info.get("Comic Settings", "Theme", fallback="default")

    checkpoint("Get comic settings")

    run_hook(theme, "preprocess", [comic_info])

    checkpoint("Preprocessing hook")

    # Setup output file space
    setup_output_file_space(comic_info)
    checkpoint("Setup output file space")

    # Build any extra comics that may be needed
    extra_comic_values = {}
    for extra_comic in get_extra_comics_list(comic_info):
        print(extra_comic)
        extra_comic_info = get_extra_comic_info(extra_comic, comic_info)
        os.makedirs(extra_comic, exist_ok=True)
        comic_data_dicts, _ = build_and_publish_comic_pages(
            comic_url, extra_comic.strip("/") + "/", extra_comic_info, args.delete_scheduled_posts,
            args.publish_all_comics
        )
        extra_comic_values[extra_comic] = comic_data_dicts[-1] if comic_data_dicts else {}

    # Build and publish pages for main comic
    print("Main comic")
    comic_data_dicts, global_values = build_and_publish_comic_pages(
        comic_url, "", comic_info, args.delete_scheduled_posts, args.publish_all_comics, extra_comic_values
    )

    # Build RSS feed
    build_rss_feed(comic_info, comic_data_dicts)
    checkpoint("Build RSS feed")

    run_hook(theme, "postprocess", [comic_info, comic_data_dicts, global_values])

    checkpoint("Postprocessing hook")

    print_processing_times()


def parse_args():
    parser = argparse.ArgumentParser(description='Manual build of comic_git')
    parser.add_argument(
        "-d",
        "--delete-scheduled-posts",
        action="store_true",
        help="Deletes scheduled post content when the script is run. USE AT YOUR OWN RISK! You can discard your "
             "changes in GitHub Desktop if you accidentally delete important files."
    )
    parser.add_argument(
        "-p",
        "--publish-all-comics",
        action="store_true",
        help="Will publish all comics, even ones with a publish date set in the future."
    )
    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())
