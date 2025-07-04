<!DOCTYPE html>
<html lang="en">
<head>
    {# Style sheet for margins and advanced layout #}
    <link rel="stylesheet" type="text/css" href="{{ base_dir }}/css/advanced_stylesheet.css">
    {# Style sheet for colors and fonts #}
    <link rel="stylesheet" type="text/css" href="{{ base_dir }}/your_content/themes/{{ theme }}/css/stylesheet.css">
    <title>{{ _title }} - {{ comic_title }}</title>
</head>
<body>
<div id="container">
    {# Banner Image #}
    <div id="banner"><img id="banner-img" src="{{ banner_image }}"></div>
    {# Links Bar #}
    <div id="links-bar">
    {%- for link in links %}
        <a class="link-bar-link" href="{{ link.url }}">{{ link.name }}</a>
    {%- endfor %}
    </div>

    {# Comic Page #}
    <div id="comic-page">
        <a href="{{ comic_base_dir }}/comic/{{ next_id }}/#comic-page">
            {%- for comic_path in comic_paths %}
            <img class="comic-image" src="{{ base_dir }}/{{ comic_paths[0] }}" title="{{ escaped_alt_text }}"/>
            {%- endfor %}
        </a>
    </div>

    {# Navigation links. Supports disabling the links when you're at the first or last page. #}
    <div id="navigation-bar">
    {% if first_id == current_id %}
        <a class="navigation-button-disabled">First</a>
        <a class="navigation-button-disabled">Previous</a>
    {% else %}
        <a class="navigation-button" href="{{ comic_base_dir }}/comic/{{ first_id }}/#comic-page">First</a>
        <a class="navigation-button" href="{{ comic_base_dir }}/comic/{{ previous_id }}/#comic-page">Previous</a>
    {% endif %}
    {% if last_id == current_id %}
        <a class="navigation-button-disabled">Next</a>
        <a class="navigation-button-disabled">Last</a>
    {% else %}
        <a class="navigation-button" href="{{ comic_base_dir }}/comic/{{ next_id }}/#comic-page">Next</a>
        <a class="navigation-button" href="{{ comic_base_dir }}/comic/{{ last_id }}/#comic-page">Last</a>
    {% endif %}
    </div>

    {# The comic "blurb" at the bottom with title, post date, tags, etc #}
    <div id="blurb">
        <h1 id="post-title">{{ _title }}</h1>
        <h3 id="post-date">Posted on: {{ _post_date }}</h3>

        {# The storyline this page is in, with a link to the first page in that storyline #}
        {%- if _storyline %}
            <div id="storyline">
                Storyline: <a href="{{ comic_base_dir }}/comic/{{ _storyline_id }}/#comic-page">{{ _storyline }}</a>
            </div>
        {%- endif %}

        {# List of characters in this comic, with a link to a web page that lists all comics with that character #}
        {%- if _characters %}
            <div id="characters">
            Characters:
            {%- for character in _characters %}
                {# "if not loop.last" puts commas after every link except at the very end #}
                <a href="{{ comic_base_dir }}/tagged/{{ character }}/">{{ character }}</a>{% if not loop.last %}, {% endif %}
            {%- endfor %}
            </div>
        {%- endif %}

        {# List of other tags on this comic, with a link to a web page that lists all comics with that tag #}
        {%- if _tags %}
            <div id="tags">
            Tags:
            {%- for tag in _tags %}
                {# "if not loop.last" puts commas after every link except at the very end #}
                <a class="tag-link" href="{{ comic_base_dir }}/tagged/{{ tag }}/">{{ tag }}</a>{% if not loop.last %}, {% endif %}
            {%- endfor %}
            </div>
        {%- endif %}

        <hr id="post-body-break">
        {# The post that goes with this comic #}
        <div id="post-body">
{{ post_html }}
        </div>
    </div>

    <div id="powered-by">
        Powered by <a id="powered-by-link" href="https://github.com/ryanvilbrandt/comic_git_dev">comic_git</a> v{{ version }}
    </div>
</div>
</body>
</html>
