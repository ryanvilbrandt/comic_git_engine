import utils


def preprocess(comic_info):
    """
    Runs immediately after the main comic's comic_info.ini file is loaded. Can be used to do any miscellaneous setup
    you might want before the comic starts to build.

    :param comic_info: The main comic's comic_info.ini file parsed into a RawConfigParser object.
    :return: None
    """
    pass


def extra_page_info_processing(comic_folder, comic_info, page_path, page_info):
    """
    Use this hook to do further processing on info.ini files after they've been read in and processed by build_site.py

    :param comic_folder: If the main comic is being built, this will be blank. Otherwise, it's the name of the extra
    comic that's currently being built.
    :param comic_info: The current comic's comic_info.ini file parsed into a RawConfigParser object.
    :param page_path: The path of the current comic page being processed. E.g. your_content/comics/197/
    :param page_info: A dict representation of the info.ini file being processed.
    :return: A dict representation of the info.ini file being processed.
    """
    return page_info


def extra_comic_dict_processing(comic_folder, comic_info, comic_data_dict):
    """
    Use this hook to do further processing on individual comic_data_dicts after they've been generated by build_site.py

    :param comic_folder: If the main comic is being built, this will be blank. Otherwise, it's the name of the extra
    comic that's currently being built.
    :param comic_info: The current comic's comic_info.ini file parsed into a RawConfigParser object.
    :param comic_data_dict: A dictionary of the data for a given comic
    :return: A dictionary of the data for a given comic
    """
    return comic_data_dict


def extra_get_storylines_processing(comic_folder, comic_info, storylines_dict):
    """
    Use this hook to do further processing on the `storylines` variable, which is used primarily to build the
    Archive page. This is useful if you wanted to make your archive more complex, like breaking your comic
    up into Volumes and Chapters instead of just Storylines.

    :param comic_folder: If the main comic is being built, this will be blank. Otherwise, it's the name of the extra
    comic that's currently being built.
    :param comic_info: The current comic's comic_info.ini file parsed into a RawConfigParser object.
    :param storylines_dict: Dictionary of all storylines, each containing an ordered list of all comics in that
    storyline.
    :return: Dictionary of all storylines
    """
    return storylines_dict


def extra_global_values(comic_folder, comic_info, comic_data_dicts):
    """
    Returns a dictionary of values that will be added to the global values sent to all templates when they're built.

    :param comic_folder: If the main comic is being built, this will be blank. Otherwise, it's the name of the extra
    comic that's currently being built. Use this value if you want to return different global values depending on what
    comic is being built.
    :param comic_info: The current comic's comic_info.ini file parsed into a RawConfigParser object.
    :param comic_data_dicts: List of comic data dicts that were built during the previous processing steps.
    :return: dict of additional global template variables
    """
    return {}


def build_other_pages(comic_folder, comic_info, comic_data_dicts):
    """
    This function is called after all other HTML files are built. You can use this function to build whatever
    additional HTML files you may want, using the utils.write_to_template() function.

    :param comic_folder: If the main comic is being built, this will be blank. Otherwise, it's the name of the extra
    comic that's currently being built. Use this value if you want to return different global values depending on what
    comic is being built.
    :param comic_info: The current comic's comic_info.ini file parsed into a RawConfigParser object.
    :param comic_data_dicts: List of comic data dicts that were built during the previous processing steps. Each data
    dict also contains the global values passed in to all templates when they're built.
    :return: None
    """
    # You can use comic_data_dicts[-1] to pass the last comic_data_dict to the template so it can have access to all
    # the global template variables, as well as the information of the most recent comic page.

    # utils.write_to_template("infinite_scroll", "path/to/html/index.html", comic_data_dicts[-1])


def postprocess(comic_info):
    """
    Runs at the very end of the comic_git build process. Can be used to do any miscellaneous cleanup you might need.

    :param comic_info: The main comic's comic_info.ini file parsed into a RawConfigParser object.
    :return: None
    """
    pass
