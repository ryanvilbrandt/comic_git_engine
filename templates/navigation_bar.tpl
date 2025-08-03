{# `if` blocks let you check the value of a variable and then generate different HTML depending on that variable.
   The if block below will generate non-functioning links for `First` and `Previous` if the current page is the
   first page in the comic, and functioning links otherwise. #}
<div class="navigation-bar">
{% if use_images_in_navigation_bar %}
    {% if first_id == current_id %}
        <a class="navigation-button-disabled" id="first-button"><img alt="First" src="{{ base_dir }}/your_content/images/navigation_icons/Icon_First_Disabled.png"></a>
        <a class="navigation-button-disabled" id="previous-button"><img alt="Previous" src="{{ base_dir }}/your_content/images/navigation_icons/Icon_Previous_Disabled.png"></a>
    {% else %}
        <a class="navigation-button" id="first-button" href="{{ comic_base_dir }}/comic/{{ first_id }}/#comic-page"><img alt="First" src="{{ base_dir }}/your_content/images/navigation_icons/Icon_First.png"></a>
        <a class="navigation-button" id="previous-button" href="{{ comic_base_dir }}/comic/{{ previous_id }}/#comic-page"><img alt="Previous" src="{{ base_dir }}/your_content/images/navigation_icons/Icon_Previous.png"></a>
    {% endif %}
    {# The block below is the same as the one above, except it checks if you're on the last page. #}
    {% if last_id == current_id %}
        <a class="navigation-button-disabled" id="next-button"><img alt="Next" src="{{ base_dir }}/your_content/images/navigation_icons/Icon_Next_Disabled.png"></a>
        <a class="navigation-button-disabled" id="latest-button"><img alt="Latest" src="{{ base_dir }}/your_content/images/navigation_icons/Icon_Latest_Disabled.png"></a>
    {% else %}
        <a class="navigation-button" id="next-button" href="{{ comic_base_dir }}/comic/{{ next_id }}/#comic-page"><img alt="Next" src="{{ base_dir }}/your_content/images/navigation_icons/Icon_Next.png"></a>
        <a class="navigation-button" id="last-button" href="{{ comic_base_dir }}/comic/{{ last_id }}/#comic-page"><img alt="Latest" src="{{ base_dir }}/your_content/images/navigation_icons/Icon_Latest.png"></a>
    {% endif %}
{% else %}
    {% if first_id == current_id %}
        <a class="navigation-button-disabled" id="first-button">‹‹ First</a>
        <a class="navigation-button-disabled" id="previous-button">‹ Previous</a>
    {% else %}
        <a class="navigation-button" id="first-button" href="{{ comic_base_dir }}/comic/{{ first_id }}/#comic-page">‹‹ First</a>
        <a class="navigation-button" id="previous-button" href="{{ comic_base_dir }}/comic/{{ previous_id }}/#comic-page">‹ Previous</a>
    {% endif %}
    {# The block below is the same as the one above, except it checks if you're on the last page. #}
    {% if last_id == current_id %}
        <a class="navigation-button-disabled" id="next-button">Next ›</a>
        <a class="navigation-button-disabled" id="last-button">Latest ››</a>
    {% else %}
        <a class="navigation-button" id="next-button" href="{{ comic_base_dir }}/comic/{{ next_id }}/#comic-page">Next ›</a>
        <a class="navigation-button" id="last-button" href="{{ comic_base_dir }}/comic/{{ last_id }}/#comic-page">Latest ››</a>
    {% endif %}
{% endif %}
</div>
