/**
 * To convert day of week number (1-7) to string (Monday to Sunday)
 * */
const day_of_week_lookup = {
    1: 'Mon.',
    2: 'Tues.',
    3: 'Wed.',
    4: 'Thurs.',
    5: 'Fri.',
    6: 'Sat.',
    7: 'Sun.'
}

/**
 * Update search parameters by toggling key in ?sorting=key
 */
function sort_by(key) {
    // Parse query string
    let urlSearchParams = new URLSearchParams(window.location.search);
    let sorting = Object.fromEntries(urlSearchParams.entries())['sorting'];

    if (sorting === key) {
        urlSearchParams.set("sorting", "-" + key);
    } else {
        // sorting is undefined or -key
        urlSearchParams.set("sorting", key);
    }

    // Update search parameters, causing page to reload
    window.location.search = urlSearchParams.toString();
}

/**
 * Returns a li tag which displays a << sign and contains a link to the previous page.
 * The tag is disabled when there is no previous page.
 */
function get_previous_li() {
    const previous_li = document.createElement('li');
    previous_li.classList.add('page-item');
    if (current_page === 1) {
        previous_li.classList.add('disabled');
    }

    const anchor_tag = document.createElement('a');
    anchor_tag.classList.add('page-link');
    href.searchParams.set('page', `${current_page-1}`);
    anchor_tag.setAttribute('href', `${href.toString()}`);
    anchor_tag.setAttribute('aria-label', 'Previous');

    const span_tag = document.createElement('span');
    span_tag.setAttribute('aria-hidden', 'true');
    span_tag.innerText = '«';

    anchor_tag.appendChild(span_tag);
    previous_li.appendChild(anchor_tag);
    return previous_li;
}

/**
 * Returns a li tag which displays a >> sign and contains a link to the next page.
 * The tag is disabled when there is no next page.
 */
function get_next_li() {
    const next_li = document.createElement('li');
    next_li.classList.add('page-item');
    if (current_page === total_nb_pages) {
        next_li.classList.add('disabled');
    }

    const anchor_tag = document.createElement('a');
    anchor_tag.classList.add('page-link');
    href.searchParams.set('page', `${current_page+1}`);
    anchor_tag.setAttribute('href', `${href.toString()}`);
    anchor_tag.setAttribute('aria-label', 'Next');

    const span_tag = document.createElement('span');
    span_tag.setAttribute('aria-hidden', 'true');
    span_tag.innerText = '»';

    anchor_tag.appendChild(span_tag);
    next_li.appendChild(anchor_tag);
    return next_li;
}

/**
 * Returns a li tag which displays a page number and contains a link to the corresponding page.
 * The tag is highlighted if it is linking to the current page.
 * @param: {number} page_nb
 */
function get_page_li(page_nb) {
    const page_li = document.createElement('li');
    page_li.classList.add('page-item');
    if (current_page === page_nb) {
        page_li.classList.add('active');
    }
    page_li.setAttribute('aria-current', 'page');

    const anchor_tag = document.createElement('a');
    anchor_tag.classList.add('page-link');
    href.searchParams.set('page', `${page_nb}`);
    anchor_tag.setAttribute('href', `${href.toString()}`);
    anchor_tag.innerText = page_nb

    page_li.appendChild(anchor_tag);
    return page_li;
}

/**
 * Returns a li tag which displays an ellipsis.
 */
function get_ellipsis_li() {
    const ellipsis_li = document.createElement('li');
    ellipsis_li.classList.add('page-item');

    const anchor_tag = document.createElement('a');
    anchor_tag.classList.add('page-link');
    anchor_tag.innerText = '⋯';

    ellipsis_li.appendChild(anchor_tag);
    return ellipsis_li;
}

/**
 * Generates the entire pagination section.
 */
function pagination() {
    pagination_ul.appendChild(get_previous_li());
    if (total_nb_pages < 7) {
        // << Link to all pages >>
        for (let page = 1; page <= total_nb_pages; page++) {
            pagination_ul.appendChild(get_page_li(page));
        }
    } else if (current_page >= 1 && current_page <= 3) {
        // << Link to all pages from 1 to current_page+1 ... end >>
        for (let page = 1; page <= current_page + 1; page++) {
            pagination_ul.appendChild(get_page_li(page));
        }
        pagination_ul.appendChild(get_ellipsis_li());
        pagination_ul.appendChild(get_page_li(total_nb_pages));
    } else if (current_page >= 4 && current_page <= total_nb_pages - 3) {
        // << 1 ... current_page-1 current_page current_page+1 ... end >>
        pagination_ul.appendChild(get_page_li(1));
        pagination_ul.appendChild(get_ellipsis_li());
        pagination_ul.appendChild(get_page_li(current_page - 1));
        pagination_ul.appendChild(get_page_li(current_page));
        pagination_ul.appendChild(get_page_li(current_page + 1));
        pagination_ul.appendChild(get_ellipsis_li());
        pagination_ul.appendChild(get_page_li(total_nb_pages));
    } else {
        // << 1 ... Link to all pages from current_page-1 to the last page >>
        pagination_ul.appendChild(get_page_li(1));
        pagination_ul.appendChild(get_ellipsis_li());
        for (let page = current_page - 1; page <= total_nb_pages; page++) {
            pagination_ul.appendChild(get_page_li(page));
        }
    }
    pagination_ul.appendChild(get_next_li());
}


/**
 * Send post request to URL without query string, informing backend to refresh cache for current page.
 * */
function refresh() {
    let xhr = new XMLHttpRequest();
    xhr.open("POST", `${location.protocol}//${location.host}${location.pathname}`, true);
    xhr.setRequestHeader("X-CSRFToken", `${csrf_token}`);
    xhr.send("refresh");
}
